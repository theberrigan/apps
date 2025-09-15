import {Component, ElementRef, OnDestroy, OnInit, ViewChild, ViewEncapsulation} from '@angular/core';
import {Subscription, zip} from 'rxjs';
import {DeviceService, ViewportBreakpoint} from '../../../services/device.service';
import {UserData, UserService} from '../../../services/user.service';
import {TitleService} from '../../../services/title.service';
import {ProjectColumn, ProjectsListItem, ProjectsService, ProjectsSettings} from '../../../services/projects.service';
import {CompanyService} from '../../../services/company.service';
import {cloneDeep, mapValues, merge} from 'lodash';
import {defer, updateObject} from '../../../lib/utils';
import {LangService} from '../../../services/lang.service';
import {FormBuilder, FormGroup} from '@angular/forms';
import {PopupComponent} from '../../../widgets/popup/popup.component';
import {SidebarComponent} from '../../shared/sidebar/sidebar.component';
import {Pagination, PaginationLoadEvent} from '../../../widgets/pagination/pagination.component';
import {DatetimeService} from '../../../services/datetime.service';
import {Router} from '@angular/router';

type ListState = 'init' | 'loading' | 'loading-more' | 'empty' | 'error' | 'list';

@Component({
    selector: 'projects',
    templateUrl: './projects.component.html',
    styleUrls: [ './projects.component.scss' ],
    encapsulation: ViewEncapsulation.None,
    host: {
        'class': 'projects',
    }
})
export class ProjectsComponent implements OnInit, OnDestroy {
    public filtersForm : FormGroup;

    public viewportBreakpoint : ViewportBreakpoint;

    public subs : Subscription[] = [];

    public dateFormats : any;

    public columnsVisibility : { [ columnKey : string ] : boolean };

    public infoColumnsVisibility : { [ columnKey : string ] : boolean };

    public projectsSettings : ProjectsSettings;

    public projectsSettingsToEdit : ProjectsSettings;

    public listState : ListState;

    public reloadDebounceTimer : any = null;

    public stateChangeDebounceTimer : any = null;

    public projectsRequest : Subscription = null;

    public pagination : Pagination;

    public projects : { page : number, items : ProjectsListItem[] }[];

    public summary : any = {};

    public activeSummary : string;

    public activeSummaryItems : any[];

    public state : any;

    public defaultState : any;

    public defaultFilters : any;

    public langs : { [ langKey : string ] : string } = {};

    public langOptions : any[];

    public sizeOptions = [ 10, 25, 50, 75, 100 ];

    public projectStatusOptions : any[];

    public coordinatorsOptions : any[];

    public sortOptions : any[];

    public invoiceOptions : any[] = [
        {
            value: null,
            display: ''
        },
        {
            value: 0,
            display: 'projects.list.invoice_not_sent'
        },
        {
            value: 1,
            display: 'projects.list.invoice_sent'
        }
    ];

    public yearOptions : any[] = [
        {
            value: null,
            display: 'projects.list.filter_pbm_year__option'
        }
    ];

    public monthOptions : any[] = [
        {
            value: null,
            display: 'projects.list.filter_pbm_month__option'
        },
        {
            value: 1,
            display: 'projects.list.filter_pbm_january__option'
        },
        {
            value: 2,
            display: 'projects.list.filter_pbm_february__option'
        },
        {
            value: 3,
            display: 'projects.list.filter_pbm_march__option'
        },
        {
            value: 4,
            display: 'projects.list.filter_pbm_april__option'
        },
        {
            value: 5,
            display: 'projects.list.filter_pbm_may__option'
        },
        {
            value: 6,
            display: 'projects.list.filter_pbm_june__option'
        },
        {
            value: 7,
            display: 'projects.list.filter_pbm_july__option'
        },
        {
            value: 8,
            display: 'projects.list.filter_pbm_august__option'
        },
        {
            value: 9,
            display: 'projects.list.filter_pbm_september__option'
        },
        {
            value: 10,
            display: 'projects.list.filter_pbm_october__option'
        },
        {
            value: 11,
            display: 'projects.list.filter_pbm_november__option'
        },
        {
            value: 12,
            display: 'projects.list.filter_pbm_december__option'
        }
    ];

    @ViewChild('tableWrap')
    public tableWrap : ElementRef;

    @ViewChild('settingsPopup')
    public settingsPopup : PopupComponent;

    public _sidebarEl : SidebarComponent = null;

    @ViewChild('sidebar')
    public set sidebarEl (sidebarEl : SidebarComponent) {
        defer(() => this._sidebarEl = sidebarEl);
    }

    public get sidebarEl () : SidebarComponent {
        return this._sidebarEl;
    }

    public maxSummaryWidth : number = 2000;

    constructor (
        private router : Router,
        private formBuilder : FormBuilder,
        private titleService : TitleService,
        private userService : UserService,
        private deviceService : DeviceService,
        private langService : LangService,
        private projectsService : ProjectsService,
        private datetimeService : DatetimeService,
        private companyService : CompanyService,
    ) {
        this.listState = 'init';
        this.titleService.setTitle('projects.list.page_title');

        this.applyUserData(this.userService.getUserData());
        this.addSub(this.userService.onUserDataUpdated.subscribe(userData => this.applyUserData(userData)));

        this.viewportBreakpoint = this.deviceService.viewportBreakpoint;
        this.addSub(this.deviceService.onResize.subscribe((message) => {
            if (message.breakpointChange) {
                this.viewportBreakpoint = message.breakpointChange.current;
            }
        }));

        for (let i = (new Date()).getFullYear(); i >= 2016; --i) {
            this.yearOptions.push({
                value: i,
                display: String(i)
            });
        }

        this.state = this.createDefaultState({
            sidebar: {
                isActive: false
            }
        });

        this.filtersForm = this.formBuilder.group(mapValues(this.state.sidebar.filters, v => [v]));
        this.filtersForm.disable();

        this.addSub(zip(
            this.projectsService.fetchProjectsStatuses(true),  // 0 (add 'Any')
            this.projectsService.fetchProjectsListState(),     // 1
            this.projectsService.fetchProjectsSettings(),      // 2
            this.companyService.fetchCoordinators(true),       // 3 (add default)
            this.langService.fetchLanguages({
                addDefault: true
            })       // 4 (all langs, as options)
        ).subscribe(([ statuses, state, settings, coordinators, langs ]) => {
            this.projectStatusOptions = statuses;
            this.projectsSettings = settings;
            //this.projectsSettings.colorizeEntireRow = true;
            this.coordinatorsOptions = coordinators.map(coordinator => ({
                value: coordinator.id,
                display: [ coordinator.firstName, coordinator.lastName ].join(' ')
            }));
            this.langOptions = langs;
            langs.forEach(lang => {
                if (lang.value !== null) {
                    this.langs[lang.value] = lang.display;
                }
            });

            // deps: projectsSettings
            this.defaultState = this.createDefaultState();
            this.state = updateObject(this.defaultState, state || {});
            this.filtersForm.setValue(this.state.sidebar.filters);
            console.log(this.state.sidebar.filters, this.filtersForm.getRawValue());

            // deps: projectsSettings, state
            this.updateColumns();

            this.fetchProjects('init');
        }, () => {
            this.listState = 'error';
        }));
    }

    public ngOnInit () : void {

    }

    public ngOnDestroy () : void {
        this.projectsRequest && this.projectsRequest.unsubscribe();
        this.subs.forEach(sub => sub.unsubscribe());
        this.subs = [];
    }

    public addSub (sub : Subscription) : void {
        this.subs = [ ...this.subs, sub ];
    }

    public applyUserData (userData : UserData) : void {
        this.dateFormats = userData.settings.formats;
    }

    public updateColumns () : void {
        const infoColumnsVisibility : any = {};

        this.projectsSettings.infoColumns.forEach(column => {
            infoColumnsVisibility[column.key] = column.isVisible;
        });

        this.infoColumnsVisibility = infoColumnsVisibility;

        // ------------------------------------------------

        const columnsVisibility : any = {};
        const sortOptions : any[] = [];

        this.projectsSettings.columns.forEach(column => {
            columnsVisibility[column.key] = column.isVisible;
            if (column.isVisible && column.isSortable) {
                sortOptions.push({
                    display: column.display,
                    value: column.key
                });
            }
        });

        this.columnsVisibility = columnsVisibility;
        this.sortOptions = sortOptions;

        const currentSortKey = this.state.sort.by;
        const sortableColumn = this.getSortableColumn(currentSortKey);

        if (sortableColumn.key !== currentSortKey) {
            this.updateState({
                sort: {
                    by: sortableColumn.key,
                    direction: sortableColumn.sortDirection
                }
            });
        }
    }

    public getSortableColumn (currentSortKey : string) : ProjectColumn {
        if (!this.projectsSettings) {
            return null;
        }

        const columns = this.projectsSettings.columns;

        return (
            columns.find(column => column.isVisible && column.isSortable && column.key === currentSortKey) ||
            columns.find(column => column.isVisible && column.isSortable) || null
        );
    }

    public createDefaultState (overrideWith : any = {}) : any {
        const sortableColumn = this.getSortableColumn('projectKey');

        const state = {
            view: {
                tablet: 'grid-detailed',
                desktop: 'grid-detailed',
            },
            sort: {
                by: sortableColumn ? sortableColumn.key : null,
                direction: sortableColumn ? sortableColumn.sortDirection : null
            },
            pagination: {
                page: 0,
                size: this.sizeOptions ? this.sizeOptions[1] : null,
            },
            sidebar: {
                isActive: true,
                filters: {
                    key: '',
                    status: this.projectStatusOptions ? this.projectStatusOptions[0].key : null,
                    company: '',
                    contact: '',
                    description: '',
                    coordinator: this.coordinatorsOptions ? this.coordinatorsOptions[0].value : null,
                    external: '',
                    email: '',
                    phone: '',
                    translator: '',
                    languageFrom: this.langOptions ? this.langOptions[0].value : null,
                    languageTo: this.langOptions ? this.langOptions[0].value : null,
                    deadline: null,
                    year: this.yearOptions ? this.yearOptions[0].value : null,
                    month: this.monthOptions ? this.monthOptions[0].value : null,
                    invoice: this.invoiceOptions ? this.invoiceOptions[0].value : null,
                    invoiceNumber: ''
                },
                collapse: {
                    options: false,
                    filters: false
                }
            }
        };

        return merge({}, state, overrideWith || {});
    }

    public fetchFirstPage (listState : ListState) : void {
        this.updateState({
            pagination: { page: 0 }
        });

        this.fetchProjects(listState);
    }

    public fetchProjects (listState : ListState, isLoadingMore : boolean = false) : void {
        this.listState = listState;

        if (this.projectsRequest) {
            this.projectsRequest.unsubscribe();
        }

        const filters : any = merge({}, this.state.sidebar.filters, {
            page: this.state.pagination.page,
            size: this.state.pagination.size,
            'sort-by': this.state.sort.by,
            'sort-ascending': this.state.sort.direction === 1
        });

        Object.keys(filters).forEach(key => {
            const value = filters[key];
            const valueStr = String(value).trim();

            console.log(key, value);

            if (
                valueStr === '' || value === null || value === undefined ||
                (key === 'coordinator' && value === -1) || (key === 'status' && value === 'any')
            ) {
                delete filters[key];
            } else if (key === 'deadline') {
                filters[key] = this.datetimeService.getMoment(value).format('YYYY-MM-DD');
            } else {
                filters[key] = valueStr;
            }
        });

        this.projectsRequest = this.projectsService.fetchProjects(filters).subscribe((response : any) => {
            const projects = response.projects;

            if (projects.length) {
                this.projects = [
                    ...(isLoadingMore && this.projects || []),
                    {
                        page: response.number,
                        items: projects
                    }
                ];
            } else {
                this.projects = [];
            }

            delete response.projects;
            this.updatePagination(response);
            this.listState = this.projects.length ? 'list' : 'empty';

            if (this.filtersForm.disabled) {
                this.filtersForm.enable();
            }

            this.projectsRequest.unsubscribe();
            this.projectsRequest = null;
        }, () => {
            this.projects = [];
            this.updatePagination(null);
            this.listState = 'error';

            if (this.filtersForm.disabled) {
                this.filtersForm.enable();
            }

            this.projectsRequest.unsubscribe();
            this.projectsRequest = null;
        });
    }

    public updatePagination (updateWith : any) : void {
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
            this.projectsService.saveProjectsListState(this.state);
        }, 350);
    }

    public onReload () : void {
        this.listState = 'loading';

        if (this.reloadDebounceTimer !== null) {
            clearTimeout(this.reloadDebounceTimer);
        }

        this.reloadDebounceTimer = setTimeout(() => {
            this.reloadDebounceTimer = null;
            this.fetchFirstPage('loading');
        }, 500);

        this.saveState();
    }

    public onViewChange () : void {
        this.saveState();
    }

    public onSidebarActivityChange (isActive : boolean) : void {
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
        if (this.viewportBreakpoint !== 'desktop' && this.sidebarEl) {
            this.sidebarEl.deactivate();
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
        if (this.listState === 'loading-more') {
            return;
        }

        this.updateState({
            pagination: { page }
        });

        this.fetchProjects('loading-more', isContinue);
    }

    public showSettingsPopup () : void {
        if (!this.projectsSettings) {
            return;
        }

        this.projectsSettingsToEdit = cloneDeep(this.projectsSettings);
        this.settingsPopup.activate();
    }

    public hideSettingsPopup (byOverlay : boolean = false) : void {
        if (byOverlay) {
            return;
        }

        this.projectsSettings = this.projectsSettingsToEdit;
        this.updateColumns();
        this.projectsService.saveProjectsSettings(this.projectsSettings);
        this.settingsPopup.deactivate().then(() => {
            this.projectsSettingsToEdit = null;
        });
    }

    public get viewType () : 'grid' | 'grid-detailed' | 'table' {
        const bp = this.viewportBreakpoint;

        if (bp === 'desktop') {
            return this.state.view.desktop;
        } else {
            return bp === 'tablet' ? 'grid-detailed' : 'grid';
        }
    }

    public onToggleSummary (projectKey : string, e : any = null) : void {
        if (e) {
            e.stopPropagation();
        }

        if (this.activeSummary === projectKey) {
            this.activeSummary = null;
            this.activeSummaryItems = null;
            return;
        }

        if (this.viewportBreakpoint === 'desktop' && this.state?.view?.desktop === 'table' && this.tableWrap) {
            this.maxSummaryWidth = this.tableWrap.nativeElement.getBoundingClientRect().width - 1;
        }

        const projectSummary = this.summary[projectKey] || (this.summary[projectKey] = {
            state: 'awaiting',
            items: null
        });

        this.activeSummary = projectKey;

        if (projectSummary.state === 'list') {
            this.activeSummaryItems = projectSummary.items;
        } else if (projectSummary.state === 'loading' || projectSummary.state === 'empty') {
            this.activeSummaryItems = null;
        } else if (projectSummary.state === 'awaiting' || projectSummary.state === 'error') {
            projectSummary.state = 'loading';

            this.addSub(this.projectsService.fetchProjectSummary(projectKey).subscribe(
                (items : any) => {
                    projectSummary.items = items || [];
                    projectSummary.state = projectSummary.items.length ? 'list' : 'empty';
                    if (this.activeSummary === projectKey) {
                        this.activeSummaryItems = projectSummary.items;
                    }
                },
                () => {
                    projectSummary.state = 'error';
                }
            ));
        }
    }

    public goToProject (projectKey : string) : void {
        this.router.navigateByUrl('/dashboard/project/' + projectKey);
    }
}
