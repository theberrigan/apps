import {Component, HostBinding, OnDestroy, ViewChild, ViewEncapsulation} from '@angular/core';
import {Subscription, zip} from 'rxjs';
import {DeviceService, ViewportBreakpoint} from '../../../services/device.service';
import {FormBuilder, FormGroup} from '@angular/forms';
import {
    ProjectStatement, ProjectStatementItem,
    StatementsService,
} from '../../../services/statements.service';
import {CanDeactivate, Router} from '@angular/router';
import {TitleService} from '../../../services/title.service';
import {UserData, UserService} from '../../../services/user.service';
import {UiService} from '../../../services/ui.service';
import {PopupService} from '../../../services/popup.service';
import {DatetimeService} from '../../../services/datetime.service';
import {ProjectsService, ProjectsSettings} from '../../../services/projects.service';
import {isSameObjectsLayout, updateObject} from '../../../lib/utils';
import {cloneDeep, mapValues, merge} from 'lodash';
import {ToastService} from '../../../services/toast.service';
import {SidebarComponent} from '../../shared/sidebar/sidebar.component';

type ListState = 'init' | 'loading' | 'error' | 'empty' | 'list';

@Component({
    selector: 'project-statements',
    templateUrl: './project-statements.component.html',
    styleUrls: [ './project-statements.component.scss' ],
    encapsulation: ViewEncapsulation.None,
    host: {
        'class': 'project-statements',
    }
})
export class ProjectStatementsComponent implements OnDestroy, CanDeactivate<boolean | Promise<boolean>> {
    public subs : Subscription[] = [];

    public viewportBreakpoint : ViewportBreakpoint;

    public state : any;

    public isSaving : boolean = false;

    public stateChangeDebounceTimer : any = null;

    public listState : ListState;

    public filtersForm : FormGroup;

    public statementsRequest : Subscription = null;

    public statements : ProjectStatement[] = [];

    public selectDateFormat : string;

    public displayDatetimeFormat : string;

    public projectStatusOptions : any[];

    public defaultState : any = {
        sidebar: {
            isActive: true,
            filters: {
                name: '',
                project: '',
                status: null,
                comment: '',
                from: null,
                to: null
            },
            collapse: {
                options: false,
                filters: false
            }
        }
    };

    public statementItemsToSave : ProjectStatementItem[] = [];

    public projectsSettings : ProjectsSettings;

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
        this.listState = 'init';
        this.viewportBreakpoint = this.deviceService.viewportBreakpoint;
        this.titleService.setTitle('billing.project_statements.page_title');

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
            this.projectsService.fetchProjectsSettings(),
            this.statementsService.fetchProjectsStatementsState()
        ).subscribe(
            ([ projectStatuses, settings, state ] : [ any, any, any ]) => {
                this.projectStatusOptions = projectStatuses.map(status => ({
                    display: status.display,
                    value: status.key
                }));

                this.projectsSettings = settings;

                // -----------------

                let date = new Date(),
                    lastMonth = date.getMonth() - 1,
                    year = date.getFullYear() - Number(lastMonth < 0);

                if (lastMonth < 0) {
                    lastMonth = 11;
                }

                this.defaultState.sidebar.filters = {
                    name: '',
                    project: '',
                    status: (this.projectStatusOptions.find(s => s.value === 'closed') || this.projectStatusOptions[0]).value,
                    comment: '',
                    from: new Date(year, lastMonth, 1).getTime(),
                    to: new Date(year, lastMonth + 1, 0).getTime()
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

                this.fetchStatements();
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

        this.listState = 'loading';
        this.fetchStatements();
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
            this.statementsService.saveProjectsStatementsState(this.state);
        }, 200);
    }

    public get isDesktopSidebarActive () : boolean {
        return this.listState !== 'init' && this.state && this.state.sidebar.isActive;
    }

    public fetchStatements () : void {
        if (this.statementsRequest) {
            this.statementsRequest.unsubscribe();
            this.statementsRequest = null;
        }

        const filters : any = cloneDeep(this.state.sidebar.filters);

        const dateFields = [ 'from', 'to' ];

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

        const sub = this.statementsRequest = this.statementsService.fetchProjectsStatements(filters).subscribe(
            (statements) => {
                console.log(statements);
                this.statementItemsToSave = [];

                this.statements = statements.map(statement => {
                    statement.total = statement.items.reduce((acc, item) => acc + item.fee, 0);
                    return statement;
                });

                this.listState = statements.length > 0 ? 'list' : 'empty';
            },
            () => {
                this.listState = 'error';
                this.statements = [];
            },
            () => {
                if (sub === this.statementsRequest) {
                    this.statementsRequest.unsubscribe();
                    this.statementsRequest = null;
                }
            }
        );
    }

    public onChangeItem (statementItem : ProjectStatementItem) : void {
        if (this.statementItemsToSave.indexOf(statementItem) === -1) {
            this.statementItemsToSave.push(statementItem);
        }
    }

    public getProjectIdByItem (statementItem : any) : number {
        for (let j = 0; j < this.statements.length; j++) {
            for (let k = 0; k < this.statements[j].items.length; k++) {
                if (statementItem === this.statements[j].items[k]) {
                    return this.statements[j].projectId;
                }
            }
        }

        return null;
    }

    public onSave () : void {
        if (this.isSaving) {
            return;
        }

        this.isSaving = true;

        this.addSub(zip(...this.statementItemsToSave.map(item => this.statementsService.saveStatementItem({
            comment: item.comment,
            payed: item.debited,
            projectId: this.getProjectIdByItem(item),
            translatorId: item.translatorId
        }))).subscribe(
            (responses) => {
                this.statementItemsToSave.forEach((item, i) => {
                    item.translatorDebitId = responses[i].translatorDebitId;
                });
                this.statementItemsToSave = [];
                this.isSaving = false;
                this.toastService.create({
                    message: [ 'billing.project_statements.save_success' ]
                });
            },
            () => {
                console.warn('Error');
                this.isSaving = false;
                this.toastService.create({
                    message: [ 'billing.project_statements.save_failed' ]
                });
            }
        ));
    }

    public goBack () : void {
        this.router.navigateByUrl('/dashboard/reports');
    }
}
