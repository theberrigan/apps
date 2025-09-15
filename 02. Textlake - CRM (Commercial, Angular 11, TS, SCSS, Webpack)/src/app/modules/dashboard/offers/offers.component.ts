import {
    ChangeDetectionStrategy,
    Component, ElementRef,
    OnChanges,
    SimpleChanges,
    ViewChild,
    ViewEncapsulation
} from '@angular/core';
import {DeviceService, ViewportBreakpoint} from '../../../services/device.service';
import {LangService} from '../../../services/lang.service';
import {OfferColumn, OffersService, OffersSettings, OfferStatus} from '../../../services/offers.service';
import {UserData, UserService} from '../../../services/user.service';
import {CompanyService, Coordinator} from '../../../services/company.service';
import {Subscription, zip} from 'rxjs';
import {isSameObjectsLayout, updateObject} from '../../../lib/utils';
import {DatetimeService} from '../../../services/datetime.service';
import {FormBuilder, FormGroup} from '@angular/forms';
import {cloneDeep, forOwn, merge} from 'lodash';
import {Pagination, PaginationLoadEvent} from '../../../widgets/pagination/pagination.component';
import {PopupComponent} from '../../../widgets/popup/popup.component';
import {Router} from '@angular/router';
import {SidebarComponent} from '../../shared/sidebar/sidebar.component';
import {TitleService} from '../../../services/title.service';

@Component({
    selector: 'offers',
    templateUrl: './offers.component.html',
    styleUrls: [ './offers.component.scss' ],
    encapsulation: ViewEncapsulation.None,
    // changeDetection: ChangeDetectionStrategy.OnPush,
    host: {
        'class': 'offers'
    }
})
export class OffersComponent implements OnChanges {
    // @ViewChild(PopupComponent)
    // public settingsPopup : PopupComponent;

    public limit : any = 10;
    public viewportBreakpoint : ViewportBreakpoint = null;

    public format = 'DD MMM YYYY hh:mm:ss a';// HH:mm:ss a     hh:mm:ss a

    public __tmp : boolean = false;
    public __tmp2 : boolean = false;
    public __tmpDateModel;/// = (+(new Date()));
    public __tmpDateModel_isDisabled : boolean = false;/// = (+(new Date()));

    public offersPages = [];

    public sort : any;

    public sortOptions : any[] = [];

    public view : any;

    // ------------------------

    public sizeOptions = [ 10, 25, 50, 75, 100 ];

    public dateFormat : any;

    public statuses : OfferStatus[];

    public columnsVisibility : any;

    public _offersSettings : OffersSettings;

    public get offersSettings (): OffersSettings {
        return this._offersSettings;
    }

    public set offersSettings (offersSettings : OffersSettings) {
        this._offersSettings = offersSettings;
        this.columnsVisibility = offersSettings.columns.reduce((acc, column) => {
            acc[column.key] = column.isVisible;
            return acc;
        }, {});

        console.log(this.columnsVisibility);
    }

    public coordinators : Coordinator[];

    public defaultState : any;

    public state : any;

    public filtersForm : FormGroup;

    public listState : 'init' | 'continue' | 'loading' | 'error' | 'empty' | 'ready';

    public paginationData : Pagination;

    public reloadTimeout : any = null;

    public offersRequest : Subscription;

    @ViewChild('settingsPopup')
    public settingsPopup : PopupComponent;

    public settingsPopupColumnsVisibility : any;

    @ViewChild('sidebar')
    public sidebar : SidebarComponent;

    public canEdit : boolean = false;

    public isHorizontalScrollHintAlreadyShown : boolean = true;

    constructor (
        private formBuilder : FormBuilder,
        private router : Router,
        private offersService : OffersService,
        private deviceService : DeviceService,
        private userService : UserService,
        private companyService : CompanyService,
        private datetimeService : DatetimeService,
        private titleService : TitleService,
        private langService : LangService,
    ) {
        this.titleService.setTitle('offers.list.page_title');
        this.listState = 'init';

        this.viewportBreakpoint = this.deviceService.viewportBreakpoint;

        this.deviceService.onResize.subscribe((message) => {
            if (message.breakpointChange) {
                this.viewportBreakpoint = this.deviceService.viewportBreakpoint;
            }
        });

        this.applyUserData(this.userService.getUserData());

        this.userService.onUserDataUpdated.subscribe(userData => this.applyUserData(userData));

        zip(
            this.offersService.fetchOfferStatuses(true),
            this.offersService.fetchOffersSettings(),
            this.offersService.fetchOffersListState(),
            this.companyService.fetchCoordinators(true),
            this.userService.fetchFromStorage('h_scroll_hint_shown')
        ).subscribe((
            [ statuses,      offersSettings, state, coordinators,  isHorizontalScrollHintShown ] :
            [ OfferStatus[], OffersSettings, any,   Coordinator[], boolean ]
        ) => {
            this.isHorizontalScrollHintAlreadyShown = isHorizontalScrollHintShown === true;
            this.statuses = statuses;
            this.offersSettings = offersSettings;

            //offersSettings.colorizeEntireRow = true;

            this.coordinators = coordinators;
            this.defaultState = this.createDefaultState();
            this.sortOptions = offersSettings.columns.map(column => {
                return {
                    display: column.display,
                    value: column.key
                };
            });

            // ---------------

            this.state = state || cloneDeep(this.defaultState);

            if (!isSameObjectsLayout(this.defaultState, this.state)) {
                this.state = updateObject(this.defaultState, this.state);
                this.saveState();
            }

            // ---------------

            const filters = this.state.sidebar.filters;

            this.filtersForm = this.formBuilder.group({
                status: [ filters.status ],
                name: [ filters.name ],
                company: [ filters.company ],
                contact: [ filters.contact ],
                phone: [ filters.phone ],
                email: [ filters.email ],
                coordinator: [ filters.coordinator ],
                from: [ filters.from ],
                to: [ filters.to ]
            });

            this.getOffers().then(() => {

            });

            console.log(statuses, offersSettings, coordinators, this.defaultState, state);
        });
    }

    public ngOnChanges (changes: SimpleChanges): void {
        console.log(changes);
    }

    public getSortableColumn (currentSortKey : string) : OfferColumn {
        const columns = this._offersSettings.columns;

        return (
            columns.find(column => column.isVisible && column.isSortable && column.key === currentSortKey) ||
            columns.find(column => column.isVisible && column.isSortable)
        );
    }

    public createDefaultState () : any {
        const sortableColumn = this.getSortableColumn('offerKey');

        return {
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
                size: this.sizeOptions[1],
            },
            sidebar: {
                isActive: true,
                filters: {
                    status: this.statuses[0].key,
                    phone: '',
                    email: '',
                    from: null, // 2019-06-06
                    to: null, // 2019-06-15
                    company: '',
                    contact: '',
                    name: '',
                    coordinator: this.coordinators[0].id,
                },
                collapse: {
                    options: false,
                    filters: false
                }
            }
        };
    }

    public saveState () : void {
        this.offersService.saveOffersListState(this.state);
    }

    public applyUserData (userData : UserData) : void {
        this.dateFormat = userData.settings.formats;
        this.canEdit = userData.features.can('edit:offers');
    }

    public getOffers (isContinue : boolean = false) : Promise<any> {
        return new Promise((resolve) => {
            if (this.offersRequest) {
                this.offersRequest.unsubscribe();
                this.offersRequest = null;
            }

            if (!isContinue) {
                this.listState = 'loading';
            }

            const filters : any = {};
            const stateFilters = this.state.sidebar.filters = this.filtersForm.getRawValue();
            const defaultFilters = this.defaultState.sidebar.filters;

            console.warn('stateFilters', stateFilters, defaultFilters);

            filters.page = this.state.pagination.page;
            filters.size = this.state.pagination.size;

            filters['sort-by'] = this.state.sort.by;
            filters['sort-ascending'] = this.state.sort.direction === 1 ? 'true' : 'false';

            ([
                'from',
                'to'
            ]).forEach(filterKey => {
                const value = stateFilters[filterKey];

                if (value) {
                    filters[filterKey] = this.datetimeService.getMoment(value).format('YYYY-MM-DD');
                }
            });

            ([
                'status',
                'coordinator'
            ]).forEach(filterKey => {
                const value = stateFilters[filterKey];

                if (value !== defaultFilters[filterKey]) {
                    filters[filterKey] = value;
                }
            });

            ([
                'phone',
                'email',
                'company',
                'contact',
                'name'
            ]).forEach(filterKey => {
                const value = stateFilters[filterKey];

                if (value) {
                    filters[filterKey] = value;
                }
            });

            console.log('filters', filters);

            const sub = this.offersRequest = this.offersService.fetchOffers(filters).subscribe(
                (response : any) => {
                    console.log(response);
                    this.offersPages = [
                        ...(isContinue && this.offersPages || []),
                        {
                            page: response.number,
                            items: response.offers
                        }
                    ];

                    delete response['offers'];
                    this.updatePagination(response);

                    this.listState = this.offersPages.some(p => p.items.length > 0) ? 'ready' : 'empty';
                },
                (error : any) => {
                    this.listState = 'error';
                    this.offersPages = [];
                    this.updatePagination(null);
                },
                () => {
                    resolve();
                    if (sub === this.offersRequest) {
                        this.offersRequest.unsubscribe();
                        this.offersRequest = null;
                    }
                }
            );
        });
    }

    public onSidebarSectionCollapse (section, isCollapsed) : void {
        console.log(section, isCollapsed);
        this.updateState({
            sidebar: {
                collapse: {
                    [ section ]: isCollapsed
                }
            }
        });

        this.saveState();
    }

    public onSidebarToggle (isActive : boolean) : void {
        this.updateState({
            sidebar: { isActive }
        });

        this.saveState();
    }

    public onFiltersSubmit () : void {
        if (this.viewportBreakpoint !== 'desktop' && this.sidebar) {
            this.sidebar.deactivate();
        }

        this.fetchFirstPage();
    }

    public onFiltersReset () : void {
        if (this.viewportBreakpoint !== 'desktop' && this.sidebar) {
            this.sidebar.deactivate();
        }

        this.filtersForm.reset(this.defaultState.sidebar.filters);
        this.fetchFirstPage();
    }

    public get isMobile () : boolean {
        return this.viewportBreakpoint !== 'desktop';
    }

    public onViewOptionChange () : void {
        this.listState = 'loading';

        if (this.reloadTimeout !== null) {
            clearTimeout(this.reloadTimeout);
        }

        this.reloadTimeout = setTimeout(() => {
            this.reloadTimeout = null;
            this.fetchFirstPage();
        }, 250);
    }

    public fetchFirstPage () : void {
        this.updateState({
            pagination: { page: 0 }
        });

        this.getOffers();
        this.saveState();
    }

    public onSwitchPage ({ page, isContinue } : PaginationLoadEvent) : void {
        this.updateState({
            pagination: { page }
        });

        this.listState = 'continue';
        this.getOffers(isContinue);
        this.saveState();
    }

    public updateState (updateWith : any) : void {
        if (!this.state) {
            throw new Error('updateState: this.state is undefined');
        }

        this.state = merge({}, this.state, updateWith);
        // TODO: save state
    }

    public updatePagination (updateWith : any) : void {
        this.paginationData = updateWith ? merge({}, this.paginationData || new Pagination(), updateWith) : null;
        console.warn('this.paginationData', this.paginationData);
    }

    public goToOffer (offer : any) : void {
        this.router.navigateByUrl('/dashboard/offer/' + offer.offerKey);
    }

    public showSettingsPopup () : void {
        if (!this.offersSettings) {
            return;
        }

        this.settingsPopup.activate();
        this.settingsPopupColumnsVisibility = cloneDeep(this.offersSettings.columns);
    }

    public hideSettingsPopup () : void {
        const offersSettings = cloneDeep(this.offersSettings);
        offersSettings.columns = this.settingsPopupColumnsVisibility;
        this.offersSettings = offersSettings;
        this.settingsPopup.deactivate();
        this.offersService.saveOffersSettings(offersSettings);
    }

    public shouldShowHorizontalScrollHint () : boolean {
        return !this.isHorizontalScrollHintAlreadyShown && this.viewportBreakpoint === 'desktop' && this.state?.view?.desktop === 'table';
    }

    public onCloseHorizontalScrollHint () : void {
        this.isHorizontalScrollHintAlreadyShown = true;
        this.userService.saveToStorage('h_scroll_hint_shown', true);
    }

    public __print (data) {
        console.warn('__print', data);
        /*
        1. Статусы, координаторы, state, userData (date format), offers settings
        1.1. Получить старый стейт, если надо первый раз создать новый стейт
        1.2. Восстановить стейт и сохранить, если надо
        2. Получить офферы в соответствии с фильтрами

        Подобрать стейт из урла.
        Если есть хоть один намёк, что в урле есть стейт, то перезаписать существующий стейт на урловый.
        Проверить, соответствует ли урловый стейт всем настройкам. Если нет - обновить здесь и на сервере.
         */

        /*
        const state = {
            view: {
                mobile: '',
                tablet: '',
                desktop: '',
            },
            sort: {
                by: '',
                direction: 1
            },
            pagination: {
                page: 0,
                size: 10,
            },
            sidebar: {
                isActive: true,
                filters: {
                    status: 'any',
                    phone: '',
                    email: '',
                    from: '', // 2019-06-06
                    to: '', // 2019-06-15
                    company: '',
                    contact: '',
                    name: ''
                    coordinator: 0
                    sort-by: 'offerKey'
                    sort-ascending: 'false'
                },
                collapse: {
                    options: true,
                    filters: true
                }
            }
        };

        const settings = {
            fieldsVisibility: {
                // ...
            },
            statusColors: {
                // ...
            }
        };
        */
    }
}
