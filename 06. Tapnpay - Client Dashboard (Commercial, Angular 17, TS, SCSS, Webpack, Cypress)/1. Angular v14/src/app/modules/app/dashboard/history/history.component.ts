import {
    ChangeDetectionStrategy,
    Component,
    Input,
    OnDestroy,
    OnInit, Output,
    Renderer2,
    ViewEncapsulation,
    EventEmitter, ViewChild, HostListener
} from '@angular/core';
import {Router} from '@angular/router';
import {animate, animateChild, query, style, transition, trigger} from '@angular/animations';
import {Subscription, zip} from 'rxjs';
import {TitleService} from '../../../../services/title.service';
import {DeviceService, ViewportBreakpoint} from '../../../../services/device.service';
import {
    HistoryService,
    InvoiceHistoryItem, InvoiceHistoryPaymentMethod,
    InvoiceHistoryResponse,
    TransactionHistoryItem, TransactionHistoryResponse
} from '../../../../services/history.service';
import {Pagination, PaginationLoadEvent} from '../../_widgets/pagination/pagination.component';
import {DomService} from '../../../../services/dom.service';
import {cloneDeep} from 'lodash-es';
import {DisputeReason, DisputeReasonOption, Invoice, InvoicesService} from '../../../../services/invoices.service';
import {Coverage, CoverageLocation, CoverageLocationMap, CoverageService} from '../../../../services/coverage.service';
import {PaymentConfig} from '../../../../services/payment.service';
import {FlatpickerComponent} from '../../_widgets/flatpicker/flatpicker.component';
import {DatepickerComponent} from '../../_widgets/datepicker/datepicker.component';
import {AccountPaymentModel, AccountTollAuthority, UserService} from '../../../../services/user.service';

type ListState = 'loading' | 'list' | 'empty' | 'error';
type Tab = 'invoices' | 'transactions' | 'disputes';

interface Filters {
    from : string;
    to : string;
}

type DisputeReasonMap = { [ key in DisputeReason ] : string };

@Component({
    selector: 'history',
    exportAs: 'history',
    templateUrl: './history.component.html',
    styleUrls: [ './history.component.scss' ],
    changeDetection: ChangeDetectionStrategy.Default,
    encapsulation: ViewEncapsulation.None,
    host: {
        'class': 'history',
        '[@historyHost]': 'true'
    },
    animations: [
        trigger('historyHost', [
            transition(':enter', [
                query('@*', animateChild(), { optional: true }),
            ]),
        ]),
    ]
})
export class HistoryComponent implements OnInit, OnDestroy {
    viewportBreakpoint : ViewportBreakpoint;

    subs : Subscription[] = [];

    listState : ListState = 'loading';

    isLoadingPage : boolean = false;

    activeTab : Tab;

    fetchSub : Subscription = null;

    paginationData : Pagination = null;

    invoiceItems : InvoiceHistoryItem[];

    transactionItems : TransactionHistoryItem[];

    disputeItems : TransactionHistoryItem[];

    isFiltersVisible : boolean = false;

    readonly itemsPerPage : number = 10;

    filters : Filters;

    readonly defaultFilters : Filters = {
        from: '1970-01-01T00:00:00.000Z',
        to: '2030-01-01T00:00:00.000Z'
    };

    disputeReasonMap : DisputeReasonMap;

    @ViewChild('dpFrom', { read: DatepickerComponent })
    dpFrom : DatepickerComponent

    @ViewChild('dpTo', { read: DatepickerComponent })
    dpTo : DatepickerComponent

    readonly paymentMethodNames : { [ key in InvoiceHistoryPaymentMethod ] : string } = {
        DCB: 'payment_methods.dcb',
        PAYPAL: 'payment_methods.paypal',
        CREDIT_CARD: 'payment_methods.credit_card',
        DEBIT_CARD: 'payment_methods.debit_card',
        WALLET: 'payment_methods.wallet',
        GOOGLEPAY: 'payment_methods.google_pay',
        APPLEPAY: 'payment_methods.apple_pay',
    };

    coverageLocations : CoverageLocation[];

    coverageLocationMap : CoverageLocationMap;

    activeCoverageLocation : CoverageLocation;

    isMapAvailable : boolean;

    paymentModel : AccountPaymentModel = null;

    tollAuthority : AccountTollAuthority = null;

    constructor (
        private renderer : Renderer2,
        private router : Router,
        private titleService : TitleService,
        private deviceService : DeviceService,
        private domService : DomService,
        private invoicesService : InvoicesService,
        private historyService : HistoryService,
        private userService : UserService,
        private coverageService : CoverageService,
    ) {
        window.scroll(0, 0);

        this.isMapAvailable = true;  // this.userService.getUserData().account.paymentModel !== 'FLEET';

        const { account } = this.userService.getUserData();

        this.paymentModel = account.paymentModel;
        this.tollAuthority = account.tollAuthority;

        this.viewportBreakpoint = this.deviceService.viewportBreakpoint;
        this.subs.push(this.deviceService.onResize.subscribe((message) => {
            if (message.breakpointChange) {
                this.viewportBreakpoint = message.breakpointChange.current;
            }
        }));

        const currentTime = new Date();

        this.defaultFilters = {
            from: new Date(currentTime.getTime() - (30 * 24 * 60 * 60 * 1000)).toISOString(),
            to: currentTime.toISOString(),
        };

        const disputeReasons = this.invoicesService.getDisputeReasonOptions();

        this.disputeReasonMap = disputeReasons.reduce((map : DisputeReasonMap, disputeReasonOption : DisputeReasonOption) => {
            map['DISPUTE_' + disputeReasonOption.value] = disputeReasonOption.display;
            return map;
        }, {} as DisputeReasonMap);
    }

    ngOnInit () {
        this.titleService.setTitle('history.page_title');
        this.onSwitchTab('invoices');
    }

    ngOnDestroy () : void {
        this.subs.forEach(sub => sub.unsubscribe());
    }

    onSwitchTab (tab : Tab) {
        this.activeTab = tab;
        this.paginationData = null;
        this.resetFilters();

        if (this.fetchSub) {
            this.fetchSub.unsubscribe();
            this.fetchSub = null;
        }

        switch (this.activeTab) {
            case 'invoices':
                this.fetchInvoices();
                break;
            case 'transactions':
                this.fetchTransactions();
                break;
            case 'disputes':
                this.fetchDisputes();
                break;
        }
    }

    async createLocationMap (transactions : TransactionHistoryItem[]) : Promise<CoverageLocationMap> {
        const locationMap : CoverageLocationMap = {};

        if (!this.isMapAvailable || !transactions) {
            return locationMap;
        }

        if (!this.coverageLocations) {
            const coverage = await this.coverageService.fetchCoverage().toPromise().catch(() => null);
            this.coverageLocations = await this.coverageService.coverageToLocations(coverage, this.tollAuthority);
        }

        if (!this.coverageLocations) {
            return locationMap;
        }

        transactions.forEach(({ location }) => {
            location = location.trim().toUpperCase();

            locationMap[location] = this.coverageLocations.find(item => {
                return location.startsWith(item.gantry.code.trim().toUpperCase());
            });
        });

        return locationMap;
    }

    hasLocationRoute (location : string) : boolean {
        return !!(this.isMapAvailable && this.coverageLocationMap && this.coverageLocationMap[location]);
    }

    onShowLocationMap (location : string) {
        if (!this.isMapAvailable || !this.hasLocationRoute(location)) {
            return;
        }

        this.activeCoverageLocation = this.coverageLocationMap[location];
    }

    onMapClose () {
        this.activeCoverageLocation = null;
    }

    fetchInvoices (page : number = 0, isLoadingPage : boolean = false) {
        this.isLoadingPage = isLoadingPage;
        this.listState = isLoadingPage ? this.listState : 'loading';

        this.fetchSub = this.historyService.fetchInvoiceHistory({
            page,
            page_size: this.itemsPerPage,
            from_date: this.filters.from,
            to_date: this.filters.to,
        }).subscribe(
            (response : InvoiceHistoryResponse) => {
                this.paginationData = response.page;
                this.invoiceItems = response.invoices;
                this.isLoadingPage = false;
                this.listState = this.invoiceItems.length > 0 ? 'list' : 'empty';
            },
            () => {
                this.paginationData = null;
                this.invoiceItems = [];
                this.isLoadingPage = false;
                this.listState = 'error';
            }
        );
    }

    fetchTransactions (page : number = 0, isLoadingPage : boolean = false) {
        this.isLoadingPage = isLoadingPage;
        this.listState = isLoadingPage ? this.listState : 'loading';

        // if (isLoadingPage) return;

        this.fetchSub = this.historyService.fetchTransactionsHistory({
            page,
            page_size: this.itemsPerPage,
            invoice_id: null,
            paid: true,
            disputed: false,
            from_date: this.filters.from,
            to_date: this.filters.to,
        }).subscribe(
            async (response : TransactionHistoryResponse) => {
                this.paginationData = response.page;
                this.transactionItems = response.tolls;
                this.coverageLocationMap = await this.createLocationMap(this.transactionItems);
                this.isLoadingPage = false;
                this.listState = this.transactionItems.length > 0 ? 'list' : 'empty';
            },
            () => {
                this.paginationData = null;
                this.transactionItems = [];
                this.isLoadingPage = false;
                this.listState = 'error';
            }
        );
    }

    fetchDisputes (page : number = 0, isLoadingPage : boolean = false) {
        this.isLoadingPage = isLoadingPage;
        this.listState = isLoadingPage ? this.listState : 'loading';

        this.fetchSub = this.historyService.fetchTransactionsHistory({
            page,
            page_size: this.itemsPerPage,
            invoice_id: null,
            paid: false,
            disputed: true,
            from_date: this.filters.from,
            to_date: this.filters.to,
        }).subscribe(
            async (response : TransactionHistoryResponse) => {
                this.paginationData = response.page;
                this.disputeItems = response.tolls;
                this.coverageLocationMap = await this.createLocationMap(this.disputeItems);
                this.isLoadingPage = false;
                this.listState = this.disputeItems.length > 0 ? 'list' : 'empty';
            },
            () => {
                this.paginationData = null;
                this.disputeItems = [];
                this.isLoadingPage = false;
                this.listState = 'error';
            }
        );
    }

    onFiltersTriggerClick (e : Event) {
        this.isFiltersVisible = !this.isFiltersVisible;
        this.domService.markEvent(e, 'filtersTriggerClick');
    }

    onFiltersPopupClick (e : Event) {
        this.domService.markEvent(e, 'filtersPopupClick');
    }

    @HostListener('document:click', [ '$event' ])
    onDocClick (e : Event) {
        if (
            !this.domService.hasEventMark(e, 'filtersTriggerClick') &&
            !this.domService.hasEventMark(e, 'filtersPopupClick') &&
            !this.domService.hasEventMark(e, 'datepickerClick')
        ) {
            this.isFiltersVisible = false;
        }
    }

    resetFilters () {
        this.filters = cloneDeep(this.defaultFilters);
    }

    onFiltersSubmit (withReset : boolean = false) {
        this.isFiltersVisible = false;

        if (withReset) {
            this.resetFilters();
        }

        switch (this.activeTab) {
            case 'invoices':
                this.fetchInvoices();
                break;
            case 'transactions':
                this.fetchTransactions();
                break;
            case 'disputes':
                this.fetchDisputes();
                break;
        }
    }

    onSwitchPage (data : PaginationLoadEvent) {
        // this.paginationData = null;
        this.resetFilters();

        if (this.fetchSub) {
            this.fetchSub.unsubscribe();
            this.fetchSub = null;
        }

        switch (this.activeTab) {
            case 'invoices':
                this.fetchInvoices(data.page, true);
                break;
            case 'transactions':
                this.fetchTransactions(data.page, true);
                break;
            case 'disputes':
                this.fetchDisputes(data.page, true);
                break;
        }
    }

    goToInvoice (invoiceId : string) {
        this.router.navigateByUrl(`/dashboard/history/invoice/${ invoiceId }`);
    }
}
