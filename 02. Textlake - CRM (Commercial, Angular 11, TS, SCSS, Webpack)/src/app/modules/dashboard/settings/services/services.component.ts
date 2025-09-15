import {Component, OnDestroy, ViewChild, ViewEncapsulation} from '@angular/core';
import {ActivatedRoute, Router} from '@angular/router';
import {Subscription, zip} from 'rxjs';
import {DeviceService, ViewportBreakpoint} from '../../../../services/device.service';
import {TitleService} from '../../../../services/title.service';
import {UserData, UserService} from '../../../../services/user.service';
import {UiService} from '../../../../services/ui.service';
import {cloneDeep, find, forIn, mapValues, merge} from 'lodash';
import {FormBuilder, FormGroup} from '@angular/forms';
import {
    defer,
    deleteFromArray,
    findByRegexp, isEmailValid, isIntString,
    isSameObjectsLayout,
    str2regexp,
    updateObject
} from '../../../../lib/utils';
import {CompanyService, CompanyServiceItem} from '../../../../services/company.service';
import {LangService} from '../../../../services/lang.service';
import {Rate, RatesService} from '../../../../services/rates.service';
import {TranslateService} from '@ngx-translate/core';
import {PopupService} from '../../../../services/popup.service';
import {PopupComponent} from '../../../../widgets/popup/popup.component';
import {Mailbox} from '../../../../services/mailbox.service';
import {ToastService} from '../../../../services/toast.service';
import {SidebarComponent} from '../../../shared/sidebar/sidebar.component';
import {Pagination, PaginationLoadEvent} from '../../../../widgets/pagination/pagination.component';
import {Client} from '../../../../services/client.service';


// type ListState = 'loading' | 'error' | 'empty' | 'list';
type ListState = 'init' | 'loading' | 'loading-more' | 'error' | 'empty' | 'list';
type Layout = 'main' | 'clone';
type EditorMode = 'create' | 'edit';


interface CompanyServiceWrap {
    service : CompanyServiceItem;
    isBasic : boolean;
    isSelected : boolean;
}

interface State {
    sort : {
        by : string;
        direction : number;
    };
    pagination : {
        page : number;
        size : number;
    };
    sidebar : {
        isActive : boolean;
        filters : {
            name : string;
            shortName : string;
            unit : string;
            rate : number;
            'language-from' : string;
            'language-to' : string;
        };
    };
}

@Component({
    selector: 'services',
    templateUrl: './services.component.html',
    styleUrls: [ './services.component.scss' ],
    encapsulation: ViewEncapsulation.None,
    host: {
        'class': 'services-editor',
    }
})
export class ServicesSettingsComponent implements OnDestroy {
    public subs : Subscription[] = [];

    public viewportBreakpoint : ViewportBreakpoint;

    public isCloning : boolean = false;

    public isDeleting : boolean = false;

    public isSaving : boolean = false;

    public listState : ListState;

    public layout : Layout;

    public state : State;

    public stateChangeDebounceTimer : any = null;

    public selectedServicesCount : number = 0;

    // public filteredServiceWraps : CompanyServiceWrap[];
    //
    // public serviceWraps : CompanyServiceWrap[];

    public serviceWrapsToClone : CompanyServiceWrap[];

    public cloneRate : number;

    public isEveryCloneServiceHasRate : boolean;

    @ViewChild('sidebar')
    public sidebar : SidebarComponent;

    @ViewChild('editor')
    public editor : PopupComponent;

    public editorMode : EditorMode;

    public isEditorFormValid : boolean = false;

    public serviceWrapToEdit : CompanyServiceWrap;

    // public serviceWrapToEditPage : any;
    //
    // public serviceWrapToEditIndex : number;

    public filtersForm : FormGroup;

    public ratesMap : { [ rateId : number ] : Rate };

    public rateOptions : any[];

    public langOptions : any[];

    public sortOptions : any[] = [
        {
            display: 'settings.services.list.name',
            value: 'name'
        },
        {
            display: 'settings.services.list.short_name',
            value: 'shortName'
        },
        {
            display: 'settings.services.list.from',
            value: 'from'
        },
        {
            display: 'settings.services.list.to',
            value: 'to'
        },
        {
            display: 'settings.services.list.unit',
            value: 'unit'
        },
        {
            display: 'settings.services.list.price',
            value: 'price'
        },
        {
            display: 'settings.services.list.rate',
            value: 'rate'
        },
    ];

    public readonly sizeOptions : number[] = [ 10, 25, 50, 75, 100 ];

    public readonly defaultState : State = {
        sort: {
            by: this.sortOptions[0].value,
            direction: 1
        },
        pagination: {
            page: 0,
            size: this.sizeOptions[1],
        },
        sidebar: {
            isActive: true,
            filters: {
                name: '',
                shortName: '',
                unit: '',
                rate: null,
                'language-from': null,
                'language-to': null,
            }
        }
    };

    public updateDebounceTimer : any = null;

    public orderDebounceTimer : any = null;

    public pagination : Pagination;

    public servicesRequest : Subscription = null;

    public servicesPages : {
        page : number,
        items : CompanyServiceWrap[]
    }[] = [];

    public isActionChecked : boolean = false;

    constructor (
        private router : Router,
        private route : ActivatedRoute,
        private formBuilder : FormBuilder,
        private titleService : TitleService,
        private userService : UserService,
        private translateService : TranslateService,
        private deviceService : DeviceService,
        private uiService : UiService,
        private langService : LangService,
        private ratesService : RatesService,
        private companyService : CompanyService,
        private toastService : ToastService,
        private popupService : PopupService
    ) {
        this.state = cloneDeep(this.defaultState);
        this.pagination = new Pagination();
        this.listState = 'init';
        this.layout = 'main';

        this.viewportBreakpoint = this.deviceService.viewportBreakpoint;
        this.titleService.setTitle('settings.services.list.page_title');

        this.state.sidebar.isActive = false;

        this.addSub(this.uiService.activateBackButton().subscribe(() => this.goBack()));

        this.addSub(this.deviceService.onResize.subscribe(message => {
            if (message.breakpointChange) {
                this.viewportBreakpoint = this.deviceService.viewportBreakpoint;
            }
        }));

        this.filtersForm = this.formBuilder.group(mapValues(this.state.sidebar.filters, v => [ v ]));

        this.addSub(zip(
            this.companyService.fetchServicesListState(),
            this.ratesService.fetchRates(),
            this.langService.fetchLanguages({ addDefault: true }),
        ).subscribe(
            ([ state, rates, langs ] : [ any, Rate[], any[] ]) => {
                this.ratesMap = rates.reduce((acc, rate) => {
                    acc[rate.id] = rate;
                    return acc;
                }, {});

                this.rateOptions = [
                    {
                        value: null,
                        display: ''
                    },
                    ...rates.map(rate => ({
                        value: rate.id,
                        display: rate.name
                    }))
                ];

                this.langOptions = langs;

                // -----------------

                state = state || {};

                if (isSameObjectsLayout(this.defaultState, state)) {
                    this.state = state;
                } else {
                    this.state = updateObject(this.defaultState, state);
                    this.saveState();
                }

                this.filtersForm.setValue(this.state.sidebar.filters);

                // -----------------

                this.fetchServices('init');
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

    public onCreate () : void {
        this.serviceWrapToEdit = {
            service: new CompanyServiceItem(),
            isSelected: false,
            isBasic: true
        };
        this.serviceWrapToEdit.service.rate = find(this.ratesMap, r => r.basic).id;
        this.editorMode = 'create';
        this.prepareEditor();
        defer(() => this.editor.activate());
    }

    // TODO: modify to support
    public onEdit (serviceWrap : CompanyServiceWrap) : void {
        // this.serviceWrapToEditPage = page;
        // this.serviceWrapToEditIndex = page.items.indexOf(serviceWrap);
        this.serviceWrapToEdit = cloneDeep(serviceWrap);
        this.editorMode = 'edit';
        this.prepareEditor();
        defer(() => this.editor.activate());
    }

    public prepareEditor () : void {
        this.isEditorFormValid = false;
        this.validate();
    }

    public validate () : void {
        defer(() => {
            let isValid : boolean = null;

            forIn(this.serviceWrapToEdit.service, (value, key) => {
                const valueStr = String(value).trim();

                switch (key) {
                    case 'name':
                    case 'unit':
                        isValid = isValid != false && !!value && !!valueStr;
                        break;
                    case 'from':
                    case 'to':
                        isValid = isValid != false && value !== this.langOptions[0].value;
                        break;
                    case 'rate':
                        isValid = isValid != false && value !== this.rateOptions[0].value;
                        break;
                }

                if (isValid === false) {
                    return false;
                }
            });

            this.isEditorFormValid = isValid;
        });
    }

    public onDelete (page : any, serviceWrap : CompanyServiceWrap) : void {
        if (this.isDeleting) {
            return;
        }

        this.popupService.confirm({
            message: [ 'settings.services.list.confirm_delete', {
                service: serviceWrap.service.name || serviceWrap.service.shortName
            } ],
        }).subscribe(({ isOk }) => {
            if (isOk) {
                this.isDeleting = true;

                this.addSub(this.companyService.deleteService(serviceWrap.service.id).subscribe(
                    () => {
                        deleteFromArray(page.items, serviceWrap);
                        this.listState = 'empty';
                        this.selectedServicesCount = 0;

                        this.servicesPages.forEach(servicesPage => {
                            servicesPage.items.forEach(serviceWrap => {
                                this.listState = 'list';
                                this.selectedServicesCount += serviceWrap.isSelected ? 1 : 0;
                            });
                        });

                        if (this.listState === 'empty') {
                            this.servicesPages = [];
                        }

                        this.isDeleting = false;

                        this.toastService.create({
                            message: [ `settings.services.list.delete_success` ]
                        });
                    },
                    () => {
                        this.isDeleting = false;

                        this.toastService.create({
                            message: [ `settings.services.list.delete_failed` ]
                        });
                    }
                ));
            }
        });
    }

    public onSwitchLayout (layout : Layout) : void {
        if (this.isCloning) {
            return;
        }

        if (layout === 'clone') {
            if (this.selectedServicesCount === 0) {
                return;
            }

            this.cloneRate = this.rateOptions[0].value;
            this.isEveryCloneServiceHasRate = false;

            this.serviceWrapsToClone = this.servicesPages.reduce((acc, page) => {
                page.items.forEach(serviceWrap => {
                    if (serviceWrap.isSelected) {
                        serviceWrap = cloneDeep(serviceWrap);
                        serviceWrap.service.rate = this.cloneRate;
                        acc.push(serviceWrap);
                    }
                });
                return acc;
            }, []);

        } else if (this.layout === 'clone') {
            this.servicesPages.forEach(page => {
                page.items.forEach(sw => this.setServiceSelectionState(sw, false));
            });
            this.serviceWrapsToClone = null;
            this.cloneRate = null;
            this.isEveryCloneServiceHasRate = false;
        }

        this.layout = layout;
    }

    // public onOrderChange () : void {
    //     if (this.orderDebounceTimer !== null) {
    //         clearTimeout(this.orderDebounceTimer);
    //     }
    //
    //     this.orderDebounceTimer = setTimeout(() => {
    //         this.orderDebounceTimer = null;
    //         this.servicesPages = this.sortServiceWraps(this.servicesPages);
    //     }, 200);
    // }

    public onReload () : void {
        this.listState = 'loading';

        if (this.updateDebounceTimer !== null) {
            clearTimeout(this.updateDebounceTimer);
        }

        this.updateDebounceTimer = setTimeout(() => {
            this.updateDebounceTimer = null;
            this.fetchFirstPage('loading');
        }, 250);
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

        this.fetchServices('loading-more', isContinue);
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
            this.companyService.saveServicesListState(this.state);
        }, 200);
    }

    public fetchFirstPage (listState : ListState) : void {
        this.updateState({
            pagination: { page: 0 }
        });

        this.fetchServices(listState);
    }

    public fetchServices (listState : ListState, isLoadingMore : boolean = false) : void {
        this.listState = listState;

        if (this.servicesRequest) {
            this.servicesRequest.unsubscribe();
            this.servicesRequest = null;
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

            if (valueStr === '' || value === '' || value === null || value === undefined) {
                delete filters[key];
            } else {
                filters[key] = valueStr;
            }
        });

        const sub = this.servicesRequest = this.companyService.fetchServices(filters).subscribe(
            (response : any) => {
                this.servicesPages = [
                    ...(isLoadingMore && this.servicesPages || []),
                    {
                        page: response.number,
                        items: response.services.map(service => ({
                            service,
                            isBasic: this.ratesMap[service.rate].basic,
                            isSelected: false,
                        }))
                    }
                ];

                delete response['services'];
                this.updatePagination(response);

                if (this.servicesPages.some(p => p.items.length > 0)) {
                    this.listState = 'list';
                } else {
                    this.servicesPages = [];
                    this.listState = 'empty';
                }

                if (sub === this.servicesRequest) {
                    this.servicesRequest.unsubscribe();
                    this.servicesRequest = null;
                }

                if (!this.isActionChecked) {
                    this.route.queryParams.subscribe(queryParams => {
                        if (queryParams['action'] === 'create') {
                            this.onCreate();
                        }
                    });

                    this.isActionChecked = true;
                }
            },
            (error : any) => {
                this.listState = 'error';
                this.servicesPages = [];
                this.updatePagination(null);

                if (sub === this.servicesRequest) {
                    this.servicesRequest.unsubscribe();
                    this.servicesRequest = null;
                }
            }
        );
    }

    /*
    public sortServiceWraps (servicesPages : any[]) : any[] {
        let serviceWraps : CompanyServiceWrap[] = [].concat(...servicesPages.map(page => page.items));

        if (!serviceWraps.length) {
            return servicesPages;
        }

        const pageLimit = this.state.pagination.size;
        const { by, direction } = this.state.sort;

        let langNames = null;

        serviceWraps = serviceWraps.sort((sw1, sw2) => {
            const s1 = sw1.service;
            const s2 = sw2.service;

            let a = s1[by],
                b = s2[by];

            if (typeof(a) == 'number' || typeof(b) == 'number') {
                return (((a || 0) - (b || 0)) || (s1.id - s2.id)) * direction;
            }

            a = a === null ? '' : String(a);
            b = b === null ? '' : String(b);

            if (by === 'from' || by === 'to') {
                (!langNames) && (langNames = this.langService.translate('langs'));
                a = langNames[ (a || '').toLowerCase() ] || '';
                b = langNames[ (b || '').toLowerCase() ] || '';
            } else if (by === 'rate') {
                a = this.getRateName(a) || '';
                b = this.getRateName(b) || '';
            }

            return (a.localeCompare(b) || (s1.id - s2.id)) * direction;
        });

        servicesPages = [];

        for (let page = 0; serviceWraps.length; page++) {
            servicesPages.push({
                page,
                items: serviceWraps.splice(0, pageLimit)
            });
        }

        return servicesPages;
    }
    */

    // public filterServiceWraps (serviceWraps : CompanyServiceWrap[]) : CompanyServiceWrap[] {
    //     const defaultFilters = this.defaultState.sidebar.filters;
    //     const filters = this.state.sidebar.filters;
    //
    //     const nameRegexp = new RegExp(str2regexp((filters.name || '').trim()), 'i');
    //     const shortNameRegexp = new RegExp(str2regexp((filters.shortName || '').trim()), 'i');
    //     const unitRegexp = new RegExp(str2regexp((filters.unit || '').trim()), 'i');
    //
    //     return serviceWraps.filter(serviceWrap => {
    //         const service = serviceWrap.service;
    //
    //         if (
    //             (filters.name === defaultFilters.name || nameRegexp.test(service.name)) &&
    //             (filters.shortName === defaultFilters.shortName || shortNameRegexp.test(service.shortName)) &&
    //             (filters.unit === defaultFilters.unit || unitRegexp.test(service.unit)) &&
    //             (filters.rate === defaultFilters.rate || filters.rate === service.rate) &&
    //             (filters.from === defaultFilters.from || filters.from === service.from) &&
    //             (filters.to === defaultFilters.to || filters.to === service.to)
    //         ) {
    //             return true;
    //         }
    //
    //         // Filtered out services can't be selected
    //         this.setServiceSelectionState(serviceWrap, false);
    //         return false;
    //     });
    // }

    public setServiceSelectionState (serviceWrap : CompanyServiceWrap, state : boolean) : void {
        if (serviceWrap.isSelected !== state) {
            this.selectedServicesCount += state ? 1 : -1;
            serviceWrap.isSelected = state;
        }
    }

    public getLangName (code : string) : string {
        return code ? ('langs.' + code.toLowerCase()) : '';
    }

    public getRateName (rateId : number) : string {
        return (this.ratesMap[rateId] || { name: '' }).name;
    }

    public onCloneRateChange (rate : number, serviceWrap : CompanyServiceWrap = null) : void {
        console.log(serviceWrap && serviceWrap.service.name, rate);
        const defaultRateId = this.rateOptions[0].value;

        if (serviceWrap) {
            serviceWrap.service.rate = rate;
            if (!this.serviceWrapsToClone.every(sw => sw.service.rate === rate)) {
                this.cloneRate = defaultRateId;
            }
        } else {
            this.serviceWrapsToClone.forEach(sw => (sw.service.rate = this.cloneRate));
        }

        this.isEveryCloneServiceHasRate = this.serviceWrapsToClone.every(sw => sw.service.rate !== defaultRateId);
    }

    public onClone () : void {
        if (this.isCloning) {
            return;
        }

        this.isCloning = true;

        this.addSub(zip(
            ...this.serviceWrapsToClone.map(sw => this.companyService.cloneService(sw.service.id, sw.service.rate))
        ).subscribe(
            (services : CompanyServiceItem[]) => {
                console.log('Cloned services:', services);
                // this.serviceWraps = [
                //     ...this.serviceWraps,
                //     ...services.map(service => ({
                //         service,
                //         isBasic: this.ratesMap[service.rate].basic,
                //         isSelected: false,
                //     }))
                // ];
                //
                // this.filteredServiceWraps = this.sortServiceWraps(this.filterServiceWraps(this.serviceWraps));
                this.isCloning = false;

                this.onSwitchLayout('main');

                this.fetchServices('loading');

                this.toastService.create({
                    message: [ `settings.services.list.clone_services_success` ]
                });
            },
            () => {
                this.toastService.create({
                    message: [ `settings.services.list.clone_services_failed2` ]
                });
                this.isCloning = false;
            }
        ));
    }

    public onHideEditor (byOverlay : boolean = false) : void {
        if (byOverlay || this.isSaving) {
            return;
        }

        this.editor.deactivate().then(() => {
            this.editorMode = null;
            this.serviceWrapToEdit = null;
            // this.serviceWrapToEditIndex = null;
            // this.serviceWrapToEditPage = null;
            this.router.navigate([], {
                queryParams: {
                    action: null,
                },
                queryParamsHandling: 'merge'
            })
        });
    }

    public onSave () : void {
        if (!this.isEditorFormValid || this.isSaving) {
            return;
        }

        this.isSaving = true;

        if (this.editorMode === 'create') {
            this.addSub(this.companyService.createService(this.serviceWrapToEdit.service).subscribe(
                service => {
                    // this.serviceWraps.push({
                    //     service,
                    //     isSelected: false,
                    //     isBasic: this.ratesMap[service.rate].basic
                    // });
                    // this.filteredServiceWraps = this.sortServiceWraps(this.filterServiceWraps(this.serviceWraps));
                    this.isSaving = false;
                    this.onHideEditor();

                    this.fetchServices('loading');

                    this.toastService.create({
                        message: [ `settings.services.editor.save_success` ]
                    });
                },
                () => {
                    this.isSaving = false;
                    this.toastService.create({
                        message: [ `settings.services.editor.save_failed` ]
                    });
                }
            ));
        } else {
            this.addSub(this.companyService.updateService(this.serviceWrapToEdit.service).subscribe(
                service => {
                    // this.serviceWrapToEditPage.items[this.serviceWrapToEditIndex] = {
                    //     service,
                    //     isSelected: false,
                    //     isBasic: this.ratesMap[service.rate].basic
                    // };
                    // this.servicesPages = this.sortServiceWraps(this.servicesPages);
                    this.isSaving = false;
                    this.onHideEditor();

                    this.fetchServices('loading');

                    this.toastService.create({
                        message: [ `settings.services.editor.save_success` ]
                    });
                },
                () => {
                    this.isSaving = false;
                    this.toastService.create({
                        message: [ `settings.services.editor.save_failed` ]
                    });
                }
            ));
        }
    }

    public goBack () : void {
        switch (this.layout) {
            case 'clone':
                this.onSwitchLayout('main');
                break;
            case 'main':
                this.router.navigateByUrl('/dashboard/settings');
                break;
        }
    }
}

