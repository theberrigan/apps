import {Component, HostBinding, OnDestroy, ViewChild, ViewEncapsulation} from '@angular/core';
import {DeviceService, ViewportBreakpoint} from '../../../services/device.service';
import {Subscription} from 'rxjs';
import {Client, ClientsService} from '../../../services/client.service';
import {merge} from 'lodash';
import {FormBuilder, FormGroup} from '@angular/forms';
import {Router} from '@angular/router';
import {defer, isSameObjectsLayout, updateObject} from '../../../lib/utils';
import {TitleService} from '../../../services/title.service';
import {Pagination, PaginationLoadEvent} from '../../../widgets/pagination/pagination.component';
import {UserData, UserService} from '../../../services/user.service';
import {SidebarComponent} from '../../shared/sidebar/sidebar.component';

type ListState = 'init' | 'loading' | 'loading-more' | 'error' | 'empty' | 'list';

@Component({
    selector: 'clients',
    templateUrl: './clients.component.html',
    styleUrls: [ './clients.component.scss' ],
    encapsulation: ViewEncapsulation.None,
    host: {
        'class': 'clients',
    }
})
export class ClientsComponent implements OnDestroy {
    public readonly sizeOptions : number[] = [ 10, 25, 50, 75, 100 ];

    public readonly sortOptions : any[] = [
        {
            display: 'clients.list.name',
            value: 'name'
        },
        {
            display: 'clients.list.legal_name',
            value: 'legalName'
        },
        {
            display: 'clients.list.email',
            value: 'email'
        },
        {
            display: 'clients.list.phone',
            value: 'phone'
        },
        {
            display: 'clients.list.city',
            value: 'city'
        },
        {
            display: 'clients.list.country',
            value: 'country'
        },
        {
            display: 'clients.list.zip_code',
            value: 'zip'
        },
        {
            display: 'clients.list.address',
            value: 'addressLine'
        }
    ];

    public readonly defaultState : any = {
        view: {
            tablet: 'grid-detailed',
            desktop: 'grid-detailed',
        },
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
                country: '',
                city: '',
                tin: '',
                address: '',
                email: '',
                phone: '',
                contact: '',
                deleted: false
            },
            collapse: {
                options: false,
                filters: false
            }
        }
    };

    public subs : Subscription[] = [];

    public viewportBreakpoint : ViewportBreakpoint;

    public state : any;

    public updateDebounceTimer : any = null;

    public orderDebounceTimer : any = null;

    public stateChangeDebounceTimer : any = null;

    public listState : ListState;

    public filtersForm : FormGroup;

    public pagination : Pagination;

    public canEdit : boolean;

    public clientsRequest : Subscription = null;

    public clientsPages : { page : number, items : Client[] }[] = [];

    @ViewChild('sidebar')
    public sidebar : SidebarComponent;

    public constructor (
        private formBuilder : FormBuilder,
        private router : Router,
        private titleService : TitleService,
        private userService : UserService,
        private deviceService : DeviceService,
        private clientsService : ClientsService
    ) {
        this.state = this.defaultState;
        this.pagination = new Pagination();
        this.listState = 'init';
        this.viewportBreakpoint = this.deviceService.viewportBreakpoint;
        this.titleService.setTitle('clients.list.page_title');

        this.applyUserData(this.userService.getUserData());
        this.addSub(this.userService.onUserDataUpdated.subscribe(userData => this.applyUserData(userData)));

        this.filtersForm = this.formBuilder.group({
            name: [ '' ],
            country: [ '' ],
            city: [ '' ],
            tin: [ '' ],
            address: [ '' ],
            email: [ '' ],
            phone: [ '' ],
            contact: [ '' ],
            deleted: [ false ]
        });

        this.addSub(
            this.deviceService.onResize.subscribe(message => {
                if (message.breakpointChange) {
                    this.viewportBreakpoint = this.deviceService.viewportBreakpoint;
                }
            })
        );

        this.clientsService.fetchClientsListState().subscribe(state => {
            state = state || {};

            if (isSameObjectsLayout(this.defaultState, state)) {
                this.state = state;
            } else {
                this.state = updateObject(this.defaultState, state);
                this.saveState();
            }

            this.filtersForm.setValue(this.state.sidebar.filters);

            this.fetchClients('init');
        });
    }

    public ngOnDestroy () : void {
        this.subs.forEach(sub => sub.unsubscribe());
    }

    public addSub (sub : Subscription) : void {
        this.subs = [ ...this.subs, sub ];
    }

    public applyUserData (userData : UserData) : void {
        this.canEdit = userData.features.can('edit:clients');
    }

    public onOrderChange () : void {
        if (this.orderDebounceTimer !== null) {
            clearTimeout(this.orderDebounceTimer);
        }

        this.orderDebounceTimer = setTimeout(() => {
            this.orderDebounceTimer = null;
            this.clientsPages = this.sortClients(this.clientsPages);
        }, 200);
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

        this.fetchClients('loading-more', isContinue);
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
            this.clientsService.saveClientsListState(this.state);
        }, 200);
    }

    public get isDesktopSidebarActive () : boolean {
        return this.listState !== 'init' && this.state && this.state.sidebar.isActive;
    }

    public fetchFirstPage (listState : ListState) : void {
        this.updateState({
            pagination: { page: 0 }
        });

        this.fetchClients(listState);
    }

    public fetchClients (listState : ListState, isLoadingMore : boolean = false) : void {
        this.listState = listState;

        if (this.clientsRequest) {
            this.clientsRequest.unsubscribe();
            this.clientsRequest = null;
        }

        const filters : any = merge({}, this.state.sidebar.filters, {
            page: this.state.pagination.page,
            size: this.state.pagination.size
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

        const sub = this.clientsRequest = this.clientsService.fetchClients(filters).subscribe(
            (response : any) => {
                console.log(response);
                this.clientsPages = this.sortClients([
                    ...(isLoadingMore && this.clientsPages || []),
                    {
                        page: response.number,
                        items: response.clients
                    }
                ]);

                delete response['clients'];
                this.updatePagination(response);

                if (this.clientsPages.some(p => p.items.length > 0)) {
                    this.listState = 'list';
                    console.log('--->', this.clientsPages);
                } else {
                    this.clientsPages = [];
                    this.listState = 'empty';
                }

                if (sub === this.clientsRequest) {
                    this.clientsRequest.unsubscribe();
                    this.clientsRequest = null;
                }
            },
            (error : any) => {
                this.listState = 'error';
                this.clientsPages = [];
                this.updatePagination(null);

                if (sub === this.clientsRequest) {
                    this.clientsRequest.unsubscribe();
                    this.clientsRequest = null;
                }
            }
        );
    }

    public sortClients (clientsPages : any[]) : any[] {
        let clients : Client[] = [].concat(...clientsPages.map(page => page.items));

        if (!clients.length) {
            return clientsPages;
        }

        const pageLimit = this.state.pagination.size;
        const orderBy = this.state.sort.by;
        const orderDir = this.state.sort.direction;

        clients = clients.sort((c1, c2) => {
            let a : any = c1[orderBy] === null ? '' : String(c1[orderBy]),
                b : any = c2[orderBy] === null ? '' : String(c2[orderBy]);

            return (a.localeCompare(b) || (c1.id - c2.id)) * orderDir;
        });

        clientsPages = [];

        for (let page = 0; clients.length; page++) {
            clientsPages.push({
                page,
                items: clients.splice(0, pageLimit)
            });
        }

        return clientsPages;
    }

    public get viewType () : 'grid' | 'grid-detailed' | 'table' {
        const bp = this.viewportBreakpoint;

        if (bp === 'desktop') {
            return this.state.view.desktop;
        } else {
            return bp === 'tablet' ? 'grid-detailed' : 'grid';
        }
    }

    public goToClient (client : Client) : void {
        this.router.navigateByUrl('/dashboard/client/' + client.id);
    }
}
