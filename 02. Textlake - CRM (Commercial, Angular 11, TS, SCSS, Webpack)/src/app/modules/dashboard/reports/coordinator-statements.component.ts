import {Component, HostBinding, OnDestroy, ViewChild, ViewEncapsulation} from '@angular/core';
import {CanDeactivate, Router} from '@angular/router';
import {Subscription, zip} from 'rxjs';
import {DeviceService, ViewportBreakpoint} from '../../../services/device.service';
import {FormBuilder, FormGroup} from '@angular/forms';
import {Pagination, PaginationLoadEvent} from '../../../widgets/pagination/pagination.component';
import {
    CoordinatorStatement, CoordinatorStatementItem,
    StatementsService
} from '../../../services/statements.service';
import {TitleService} from '../../../services/title.service';
import {UserData, UserService} from '../../../services/user.service';
import {UiService} from '../../../services/ui.service';
import {PopupService} from '../../../services/popup.service';
import {DatetimeService} from '../../../services/datetime.service';
import {ProjectsService} from '../../../services/projects.service';
import {isSameObjectsLayout, updateObject} from '../../../lib/utils';
import {mapValues, merge} from 'lodash';
import {OffersService} from '../../../services/offers.service';
import {CompanyService} from '../../../services/company.service';
import {ToastService} from '../../../services/toast.service';
import {SidebarComponent} from '../../shared/sidebar/sidebar.component';

type ListState = 'init' | 'loading' | 'loading-more' | 'error' | 'empty' | 'list';

@Component({
    selector: 'coordinator-statements',
    templateUrl: './coordinator-statements.component.html',
    styleUrls: [ './coordinator-statements.component.scss' ],
    encapsulation: ViewEncapsulation.None,
    host: {
        'class': 'coordinator-statements',
    }
})
export class CoordinatorStatementsComponent implements OnDestroy {
    public subs : Subscription[] = [];

    public viewportBreakpoint : ViewportBreakpoint;

    public state : any;

    public updateDebounceTimer : any = null;

    public stateChangeDebounceTimer : any = null;

    public listState : ListState;

    public filtersForm : FormGroup;

    public pagination : Pagination;

    public statementsRequest : Subscription = null;

    public statementsPages : { page : number, items : CoordinatorStatement[] }[] = [];

    public selectDateFormat : string;

    public displayDatetimeFormat : string;

    public projectStatusOptions : any[];

    public offerStatusOptions : any[];

    public coordinatorOptions : any[];

    public readonly sizeOptions : number[] = [ 10, 25, 50, 75, 100 ];

    public defaultState : any = {
        pagination: {
            page: 0,
            size: this.sizeOptions[1],
        },
        sidebar: {
            isActive: true,
            filters: {
                coordinatorId: 0, // eq. 'unassigned'
                offerCreatedFrom: null,
                offerCreatedTo: null,
                offerStatus: null,
                projectCreatedFrom: null,
                projectCreatedTo: null,
                projectCompletedFrom: null,
                projectCompletedTo: null,
                projectStatus: null
            },
            collapse: {
                options: false,
                filters: false
            }
        }
    };

    public coordinatorName : string;

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
        private offersService : OffersService,
        private companyService : CompanyService,
        private statementsService : StatementsService
    ) {
        this.pagination = new Pagination();
        this.listState = 'init';
        this.viewportBreakpoint = this.deviceService.viewportBreakpoint;
        this.titleService.setTitle('billing.coordinator_statements.page_title');

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
            this.offersService.fetchOfferStatuses(true),
            this.companyService.fetchCoordinators(),
            this.statementsService.fetchCoordinatorsStatementsState()
        ).subscribe(
            ([ projectStatuses, offersStatuses, coordinators, state ] : [ any[], any[], any[], any ]) => {
                this.projectStatusOptions = projectStatuses.map(status => ({
                    display: status.display,
                    value: status.key
                }));

                this.offerStatusOptions = offersStatuses.map(status => ({
                    display: status.display,
                    value: status.key
                }));

                this.coordinatorOptions = coordinators.map(coordinator => ({
                    display: [ coordinator.firstName, coordinator.lastName ].join(' '),
                    value: coordinator.id
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
                    coordinatorId: 0, // eq. 'unassigned'
                    offerCreatedFrom: new Date(year, lastMonth, 1).getTime(),
                    offerCreatedTo: new Date(year, lastMonth + 1, 0).getTime(),
                    offerStatus: this.offerStatusOptions[0].value,
                    projectCreatedFrom: null,
                    projectCreatedTo: null,
                    projectCompletedFrom: null,
                    projectCompletedTo: null,
                    projectStatus: this.projectStatusOptions[0].value
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

        console.warn(this.filtersForm.getRawValue());

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
            this.statementsService.saveCoordinatorsStatementsState(this.state);
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

        const dateFields = [
            'offerCreatedFrom',
            'offerCreatedTo',
            'projectCreatedFrom',
            'projectCreatedTo',
            'projectCompletedFrom',
            'projectCompletedTo'
        ];

        Object.keys(filters).forEach(key => {
            const value = filters[key];
            const valueStr = String(value).trim();

            if (
                ((key === 'offerStatus' || key === 'projectStatus') && valueStr === 'any') ||
                valueStr === '' || value === '' || value === null || value === undefined
            ) {
                delete filters[key];
            } else if (dateFields.includes(key)) {
                filters[key] = this.datetimeService.getMoment(value).format('YYYY-MM-DD');
            } else {
                filters[key] = valueStr;
            }
        });

        const sub = this.statementsRequest = this.statementsService.fetchCoordinatorsStatements(filters).subscribe(
            (response : any) => {
                console.log(response);
                this.statementsPages = [
                    ...(isLoadingMore && this.statementsPages || []),
                    {
                        page: response.number,
                        items: [ response.statement ]
                    }
                ];

                this.coordinatorName = (
                    this.state.sidebar.filters.coordinatorId !== null ?
                    (this.coordinatorOptions.find(c => c.value === this.state.sidebar.filters.coordinatorId) || { display: null }).display :
                    null
                );

                delete response['statement'];
                this.updatePagination(response);

                if (this.statementsPages[0].items[0].items.length > 0) {
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

    public goBack () : void {
        this.router.navigateByUrl('/dashboard/reports');
    }
}
