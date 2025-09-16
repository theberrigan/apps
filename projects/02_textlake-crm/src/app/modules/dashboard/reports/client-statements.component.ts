import {Component, HostBinding, OnDestroy, ViewChild, ViewEncapsulation} from '@angular/core';
import {Subscription, zip} from 'rxjs';
import {DeviceService, ViewportBreakpoint} from '../../../services/device.service';
import {FormBuilder, FormGroup} from '@angular/forms';
import {Pagination, PaginationLoadEvent} from '../../../widgets/pagination/pagination.component';
import {ClientStatement, ClientStatementItem, StatementsService} from '../../../services/statements.service';
import {CanDeactivate, Router} from '@angular/router';
import {TitleService} from '../../../services/title.service';
import {UserData, UserService} from '../../../services/user.service';
import {isSameObjectsLayout, updateObject} from '../../../lib/utils';
import {mapValues, merge} from 'lodash';
import {PopupService} from '../../../services/popup.service';
import {UiService} from '../../../services/ui.service';
import {ProjectsService} from '../../../services/projects.service';
import {DatetimeService} from '../../../services/datetime.service';
import {ToastService} from '../../../services/toast.service';
import {SidebarComponent} from '../../shared/sidebar/sidebar.component';

type ListState = 'init' | 'loading' | 'loading-more' | 'error' | 'empty' | 'list';

@Component({
    selector: 'clients-statements',
    templateUrl: './client-statements.component.html',
    styleUrls: [ './client-statements.component.scss' ],
    encapsulation: ViewEncapsulation.None,
    host: {
        'class': 'clients-statements',
    }
})
export class ClientStatementsComponent implements OnDestroy, CanDeactivate<boolean | Promise<boolean>> {
    public subs : Subscription[] = [];

    public viewportBreakpoint : ViewportBreakpoint;

    public state : any;

    public isSaving : boolean = false;

    public updateDebounceTimer : any = null;

    public stateChangeDebounceTimer : any = null;

    public listState : ListState;

    public filtersForm : FormGroup;

    public pagination : Pagination;

    public statementsRequest : Subscription = null;

    public statementsPages : { page : number, items : ClientStatement[] }[] = [];

    public selectDateFormat : string;

    public displayDatetimeFormat : string;

    public projectStatusOptions : any[];

    public invoiceOptions : any[] = [
        {
            value: null,
            display: ''
        },
        {
            value: true,
            display: 'billing.client_statements.filters.invoice_yes'
        },
        {
            value: false,
            display: 'billing.client_statements.filters.invoice_no'
        }
    ];

    public readonly sizeOptions : number[] = [ 10, 25, 50, 75, 100 ];

    public defaultState : any = {
        pagination: {
            page: 0,
            size: this.sizeOptions[1],
        },
        sidebar: {
            isActive: true,
            filters: {
                name: '',
                status: '',
                from: null,
                to: null,
                closedFrom: null,
                closedTo: null,
                key: '',
                hasInvoice: null
            },
            collapse: {
                options: false,
                filters: false
            }
        }
    };

    public statementItemsToSave : ClientStatementItem[] = [];

    public activeDetailsStatement : ClientStatement;

    @ViewChild('sidebar')
    public sidebar : SidebarComponent;

    constructor (
        private formBuilder : FormBuilder,
        private router : Router,
        private titleService : TitleService,
        private userService : UserService,
        private deviceService : DeviceService,
        private uiService : UiService,
        private popupService : PopupService,
        private datetimeService : DatetimeService,
        private projectsService : ProjectsService,
        private toastService : ToastService,
        private statementsService : StatementsService
    ) {
        // this.state = this.defaultState;
        this.pagination = new Pagination();
        this.listState = 'init';
        this.viewportBreakpoint = this.deviceService.viewportBreakpoint;
        this.titleService.setTitle('billing.client_statements.page_title');

        this.applyUserData(this.userService.getUserData());
        this.addSub(this.userService.onUserDataUpdated.subscribe(userData => this.applyUserData(userData)));
        this.addSub(this.uiService.activateBackButton().subscribe(() => this.goBack()));

        // this.filtersForm = this.formBuilder.group(mapValues(this.state.sidebar.filters, v => [ v ]));

        this.addSub(this.deviceService.onResize.subscribe(message => {
            if (message.breakpointChange) {
                this.viewportBreakpoint = this.deviceService.viewportBreakpoint;
            }
        }));

        this.addSub(zip(
            this.projectsService.fetchProjectsStatuses(true),
            this.statementsService.fetchClientsStatementsState()
        ).subscribe(
            ([ projectStatuses, state ] : [ any, any ]) => {
                this.projectStatusOptions = projectStatuses.map(status => ({
                    display: status.display,
                    value: status.key
                }));

                // -----------------

                let date = new Date(),
                    lastMonth = date.getMonth() - 1,
                    year = date.getFullYear() - Number(lastMonth < 0);

                if (lastMonth < 0) {
                    lastMonth = 11;
                }

                console.warn(this.selectDateFormat);

                this.defaultState.sidebar.filters = {
                    name: '',
                    status: (this.projectStatusOptions.find(s => s.value === 'closed') || this.projectStatusOptions[0]).value,
                    from: new Date(year, lastMonth, 1).getTime(),
                    to: new Date(year, lastMonth + 1, 0).getTime(),
                    closedFrom: null,
                    closedTo: null,
                    key: '',
                    hasInvoice: this.invoiceOptions[0].value
                };

                // -----------------

                state = state || {};

                if (isSameObjectsLayout(this.defaultState, state)) {
                    this.state = state;
                } else {
                    this.state = updateObject(this.defaultState, state);
                    this.saveState();
                }

                this.filtersForm = this.formBuilder.group(mapValues(this.state.sidebar.filters, v => [ v ]));

                // this.filtersForm.setValue(this.state.sidebar.filters);

                this.fetchStatements('init');
            },
            () => {
                this.listState = 'error';
            }
        ));
    }

    public ngOnDestroy () : void {
        this.subs.forEach(sub => sub.unsubscribe());
        this.uiService.deactivateBackButton();
    }

    public canDeactivate () : Promise<boolean> {
        return new Promise<boolean>((resolve) => {
            if (!this.statementItemsToSave || this.statementItemsToSave.length === 0) {
                resolve(true);
                return;
            }

            this.popupService.confirm({
                message: [ 'guards.discard' ],
            }).subscribe(({ isOk }) => resolve(isOk));
        });
    }

    public addSub (sub : Subscription) : void {
        this.subs = [ ...this.subs, sub ];
    }

    public applyUserData (userData : UserData) : void {
        this.selectDateFormat = userData.settings.formats.date.select;
        this.displayDatetimeFormat = userData.settings.formats.datetime.display;
    }

    public onLimitChange () : void {
        this.listState = 'loading';

        if (this.updateDebounceTimer !== null) {
            clearTimeout(this.updateDebounceTimer);
        }

        this.updateDebounceTimer = setTimeout(() => {
            this.updateDebounceTimer = null;
            this.fetchFirstPage('loading');
        }, 250);
    }

    public onSidebarToggle (isActive : boolean) : void {
        this.updateState({
            sidebar: { isActive }
        });
    }

    public onSidebarSectionCollapse (section : string, isCollapsed : boolean) : void {
        this.updateState({
            sidebar: {
                collapse: {
                    [ section ]: isCollapsed
                }
            }
        });
    }

    public onFiltersSubmit (withReset : boolean = false) : void {
        if (this.viewportBreakpoint !== 'desktop' && this.sidebar) {
            this.sidebar.deactivate();
        }

        if (withReset) {
            this.filtersForm.reset(this.defaultState.sidebar.filters);
        }


        this.updateState({
            sidebar: {
                filters: this.filtersForm.getRawValue()
            }
        });

        this.fetchFirstPage('loading');
    }

    public onSwitchPage ({ page, isContinue } : PaginationLoadEvent) : void {
        this.updateState({
            pagination: { page }
        });

        this.fetchStatements('loading-more', isContinue);
    }

    public updatePagination (updateWith : any = null) : void {
        this.pagination = updateWith ? merge({}, this.pagination || new Pagination(), updateWith) : null;
    }

    public updateState (updateWith : any = null) : void {
        if (this.state) {
            this.state = merge({}, this.state, updateWith);
            this.saveState();
        }
    }

    public saveState () : void {
        if (this.stateChangeDebounceTimer !== null) {
            clearTimeout(this.stateChangeDebounceTimer);
        }

        this.stateChangeDebounceTimer = setTimeout(() => {
            this.stateChangeDebounceTimer = null;
            this.statementsService.saveClientsStatementsState(this.state);
        }, 200);
    }

    public get isDesktopSidebarActive () : boolean {
        return this.listState !== 'init' && this.state && this.state.sidebar.isActive;
    }

    public fetchFirstPage (listState : ListState) : void {
        this.updateState({
            pagination: { page: 0 }
        });

        this.fetchStatements(listState);
    }
    public fetchStatements (listState : ListState, isLoadingMore : boolean = false) : void {
        this.listState = listState;

        if (this.statementsRequest) {
            this.statementsRequest.unsubscribe();
            this.statementsRequest = null;
        }

        const filters : any = merge({}, this.state.sidebar.filters, {
            page: this.state.pagination.page,
            size: this.state.pagination.size
        });

        const dateFields = [ 'from', 'to', 'closedFrom', 'closedTo' ];

        Object.keys(filters).forEach(key => {
            const value = filters[key];
            const valueStr = String(value).trim();

            if (
                (key === 'status' && valueStr === 'any') ||
                valueStr === '' || value === '' || value === null || value === undefined
            ) {
                delete filters[key];
            } else if (dateFields.includes(key)) {
                filters[key] = this.datetimeService.getMoment(value).format('YYYY-MM-DD');
            } else {
                filters[key] = valueStr;
            }
        });

        const sub = this.statementsRequest = this.statementsService.fetchClientsStatements(filters).subscribe(
            (response : any) => {
                console.log(response);
                this.statementItemsToSave = [];

                this.statementsPages = [
                    ...(isLoadingMore && this.statementsPages || []),
                    {
                        page: response.number,
                        items: response.statements.map(statement => {
                            const groups = statement.items.reduce((acc, item) => {
                                if (!(item.currency in acc)) {
                                    acc[item.currency] = {
                                        gross: 0,
                                        net: 0
                                    };
                                }

                                acc[item.currency].gross += item.gross;
                                acc[item.currency].net += item.net;

                                return acc;
                            }, {});

                            statement.total = Object.keys(groups).reduce((acc, key) => {
                                groups[key].currency = key;
                                acc.push(groups[key]);
                                return acc;
                            }, []);

                            return statement;
                        })
                    }
                ];

                delete response['statements'];
                this.updatePagination(response);

                if (this.statementsPages.some(p => p.items.length > 0)) {
                    this.listState = 'list';
                } else {
                    this.statementsPages = [];
                    this.listState = 'empty';
                }

                if (sub === this.statementsRequest) {
                    this.statementsRequest.unsubscribe();
                    this.statementsRequest = null;
                }
            },
            (error : any) => {
                this.listState = 'error';
                this.statementsPages = [];
                this.updatePagination(null);

                if (sub === this.statementsRequest) {
                    this.statementsRequest.unsubscribe();
                    this.statementsRequest = null;
                }
            }
        );
    }

    public onChangeItem (statementItem : ClientStatementItem) : void {
        if (this.statementItemsToSave.indexOf(statementItem) === -1) {
            this.statementItemsToSave.push(statementItem);
        }
    }

    public getClientIdByItem (statementItem : any) : number {
        console.log(1);
        for (let i = 0; i < this.statementsPages.length; i++){
            for (let j = 0; j < this.statementsPages[i].items.length; j++) {
                for (let k = 0; k < this.statementsPages[i].items[j].items.length; k++) {
                    if (statementItem === this.statementsPages[i].items[j].items[k]) {
                        return this.statementsPages[i].items[j].clientId;
                    }
                }
            }
        }
        console.log(2);

        return null;
    }

    public onSave () : void {
        if (this.isSaving) {
            return;
        }

        this.isSaving = true;

        this.addSub(zip(...this.statementItemsToSave.map(item => this.statementsService.saveClientStatementItem({
            projectId: item.projectId,
            comment: item.comment,
            invoice: item.invoice,
            sent: item.invoiceSent,
            clientId: this.getClientIdByItem(item)
        }))).subscribe(
            () => {
                this.statementItemsToSave = [];
                this.isSaving = false;
                this.toastService.create({
                    message: [ 'billing.client_statements.save_success' ]
                });
            },
            () => {
                console.warn('Error');
                this.isSaving = false;
                this.toastService.create({
                    message: [ 'billing.client_statements.save_failed' ]
                });
            }
        ));
    }

    public onToggleDetails (statement : ClientStatement) : void {
        this.activeDetailsStatement = this.activeDetailsStatement === statement ? null : statement;
    }

    public goBack () : void {
        this.router.navigateByUrl('/dashboard/reports');
    }
}
