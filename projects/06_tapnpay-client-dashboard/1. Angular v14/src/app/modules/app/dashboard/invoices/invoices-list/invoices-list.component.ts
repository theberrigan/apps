import {
    ChangeDetectionStrategy,
    Component,
    Input,
    OnDestroy,
    OnInit, Output,
    Renderer2,
    ViewEncapsulation,
    EventEmitter, ViewChild
} from '@angular/core';
import {CanDeactivate, Router} from '@angular/router';
import {TitleService} from '../../../../../services/title.service';
import {DeviceService, ViewportBreakpoint} from '../../../../../services/device.service';
import {Subscription, zip} from 'rxjs';
import {
    DisputeReason, DisputeReasonOption,
    Invoice,
    InvoiceItem,
    InvoicesService,
    LicensePlate,
    Transaction, TransactionItem
} from '../../../../../services/invoices.service';
import {cloneDeep} from 'lodash-es';
import {DomService} from '../../../../../services/dom.service';
import {animate, animateChild, query, style, transition, trigger} from '@angular/animations';
import {PaymentConfig, PaymentService} from '../../../../../services/payment.service';
import {InvoicePaymentComponent} from '../invoice-payment/invoice-payment.component';
import {defer} from '../../../../../lib/utils';
import {Coverage, CoverageLocation, CoverageService} from '../../../../../services/coverage.service';
import {AccountPaymentModel, AccountTollAuthority, UserService} from '../../../../../services/user.service';

type ListState = 'loading' | 'list' | 'empty' | 'error';

export interface OnInvoicesListInitedEvent {
    invoiceItems : InvoiceItem[];
    coverageLocations : CoverageLocation[];
}

@Component({
    selector: 'invoices-list',
    exportAs: 'invoicesList',
    templateUrl: './invoices-list.component.html',
    styleUrls: [ './invoices-list.component.scss' ],
    changeDetection: ChangeDetectionStrategy.Default,
    encapsulation: ViewEncapsulation.None,
    host: {
        'class': 'invoices-list',
        '[@invoicesListHost]': 'true'
    },
    animations: [
        trigger('invoicesListHost', [
            transition(':enter', [
                query('@*', animateChild(), { optional: true }),
            ]),
        ]),
        trigger('invoicesListMobileActions', [
            transition(':enter', [
                style({ transform: 'translateY(100%)', opacity: 0 }),
                animate('0.2s cubic-bezier(0.5, 1, 0.89, 1)', style({ transform: '*', opacity: '*' }))
            ]),
            transition(':leave', [
                style({ transform: '*', opacity: '*' }),
                animate('0.15s cubic-bezier(0.5, 1, 0.89, 1)', style({ transform: 'translateY(100%)', opacity: 0 }))
            ])
        ]),
    ]
})
export class InvoicesListComponent implements OnInit, OnDestroy {
    viewportBreakpoint : ViewportBreakpoint;

    subs : Subscription[] = [];

    listState : ListState = 'loading';

    readonly lowExpireThreshold = 1 * 60 * 60 * 1000;

    readonly showExpireThreshold = 24 * 60 * 60 * 1000;

    readonly isAllInvoicesSelectedByDefault : boolean = true;

    @Input()
    invoiceItems : InvoiceItem[];

    invoiceItemsToPay : InvoiceItem[];

    // @Input()
    paymentConfig : PaymentConfig;

    // @Input()
    // paymentMethod : PaymentMethod;

    @Output()
    onInvoicesListInited = new EventEmitter<OnInvoicesListInitedEvent>();

    @Output()
    onShowInvoiceDetails = new EventEmitter<InvoiceItem[]>();

    @ViewChild('paymentComponent', { read: InvoicePaymentComponent })
    paymentComponent : InvoicePaymentComponent;

    isAllInvoicesChecked : boolean = false;

    checkedInvoiceAmount : number = 0;

    isActionsVisible : boolean = false;

    onPaymentConfigChangedSub : Subscription;

    isSubmitting : boolean = false;

    coverageLocations : CoverageLocation[];

    fetchSub : Subscription;

    paymentModel : AccountPaymentModel = null;

    tollAuthority : AccountTollAuthority = null;

    constructor (
        private renderer : Renderer2,
        private router : Router,
        private titleService : TitleService,
        private deviceService : DeviceService,
        private domService : DomService,
        private invoicesService : InvoicesService,
        private paymentService : PaymentService,
        private userService : UserService,
        private coverageService : CoverageService,
    ) {
        window.scroll(0, 0);

        const { account } = this.userService.getUserData();

        this.paymentModel = account.paymentModel;
        this.tollAuthority = account.tollAuthority;

        this.viewportBreakpoint = this.deviceService.viewportBreakpoint;
        this.subs.push(this.deviceService.onResize.subscribe((message) => {
            if (message.breakpointChange) {
                this.viewportBreakpoint = message.breakpointChange.current;
            }
        }));
    }

    ngOnInit () {
        this.titleService.setTitle('invoices.invoices_list.page_title');

        if (this.invoiceItems === null || this.invoiceItems === undefined) {
            this.fetchInvoices();
        } else {
            // TODO: mb uncheck all invoiceItems?
            this.checkIsAllInvoicesChecked();
            this.onSelectionChanged();
            this.listState = this.invoiceItems.length > 0 ? 'list' : 'empty';
        }
    }

    ngOnDestroy () : void {
        this.subs.forEach(sub => sub.unsubscribe());

        if (this.onPaymentConfigChangedSub) {
            this.onPaymentConfigChangedSub.unsubscribe();
        }
    }

    fetchInvoices () {
        this.listState = 'loading';

        this.fetchSub?.unsubscribe();

        this.fetchSub = zip(
            this.invoicesService.fetchInvoices(),
            this.paymentService.fetchPaymentConfig(),
            this.coverageService.fetchCoverage()
        ).subscribe(
            async ([ invoices, paymentConfig, coverage ] : [ Invoice[], PaymentConfig, Coverage ]) => {
                this.coverageLocations = await this.coverageService.coverageToLocations(coverage, this.tollAuthority);
                this.paymentConfig = paymentConfig;

                if (invoices.length > 0) {
                    this.invoiceItems = this.convertInvoicesToItems(invoices); // this.convertInvoicesToItems(this._modifyInvoices(invoices));
                    this.checkIsAllInvoicesChecked();
                    this.onSelectionChanged();
                    this.listState = 'list';
                } else {
                    this.invoiceItems = [];
                    this.listState = 'empty';
                }

                if (this.onPaymentConfigChangedSub) {
                    this.onPaymentConfigChangedSub.unsubscribe();
                }

                this.onPaymentConfigChangedSub = (
                    this.paymentService.onPaymentConfigChanged
                        .asObservable()
                        .subscribe((paymentConfig : PaymentConfig) => {
                            // paymentConfig.payment_method_type = 'wallet';
                            this.paymentConfig = paymentConfig;
                            this.calcCheckedInvoices();
                            console.warn('Invoice list payment config updated:', this.paymentConfig);
                        })
                );

                this.notifyOnInvoicesListInited();
            },
            () => {
                this.paymentConfig = null;
                this.invoiceItems = null;
                this.listState = 'error';

                this.notifyOnInvoicesListInited();
            }
        );
    }

    _modifyInvoices (invoices : Invoice[]) : Invoice[] {
        while (invoices.length < 10) {
            invoices = [ ...invoices, cloneDeep(invoices[0]) ];
        }

        invoices.forEach(invoice => {
            invoice.invoice_date = new Date().toISOString();
            (<any>invoice).invoice_expire = new Date(Date.now() + Math.round(172800000 * Math.random())).toISOString();

            //---------------------------------------

            const states = [
                'AK', 'AL', 'AR', 'AZ', 'CA', 'CO',
                'CT', 'DC', 'DE', 'FL', 'GA', 'HI',
                'IA', 'ID', 'IL', 'IN', 'KS', 'KY',
                'LA', 'MA', 'MD', 'ME', 'MI', 'MN',
                'MO', 'MS', 'MT', 'NC', 'ND', 'NE',
                'NH', 'NJ', 'NM', 'NV', 'NY', 'OH',
                'OK', 'OR', 'PA', 'RI', 'SC', 'SD',
                'TN', 'TX', 'UT', 'VA', 'VT', 'WA',
                'WI', 'WV', 'WY'
            ];

            invoice.items.forEach((transaction, i) => {
                transaction.lps = states[ Math.trunc(i / 3) ];
                // transaction.toll_location = 'NTE-00910-50';
            });

            //---------------------------------------
        });

        return invoices;
    }

    convertInvoicesToItems (invoices : Invoice[]) : InvoiceItem[] {
        return invoices.map((invoice : Invoice) : InvoiceItem => {
            const expireTs = new Date(invoice.invoice_expiration_date).getTime();
            const expireMs = Math.max(0, Math.round(expireTs - Date.now()));

            return {
                id: invoice.invoice_id,
                name: invoice.invoice_name,
                amount: invoice.invoice_amount,
                transactionCount: invoice.items.length,
                createTs: new Date(invoice.invoice_date).getTime(),
                hoursLeft: Math.max(1, Math.round(expireMs / 1000 / 60 / 60)),
                isLowTimeLeft: expireMs <= this.lowExpireThreshold,
                showTimeLeft: expireMs < this.showExpireThreshold,
                isChecked: this.isAllInvoicesSelectedByDefault,
                invoice,
                licensePlates: this.convertTransactionsToLicensePlates(invoice.items)
            };
        });
    }

    convertTransactionsToLicensePlates (transactions : Transaction[]) : LicensePlate[] {
        const licensePlateMap = transactions.reduce((acc : { [ key : string ] : TransactionItem[] }, transaction : Transaction) => {
            const fullLicensePlate = [ transaction.lps, transaction.lpn ].join(' ');
            const createTs = new Date(transaction.toll_date).getTime();
            const licensePlateTransactions = acc[fullLicensePlate] = acc[fullLicensePlate] || [];

            licensePlateTransactions.push({
                id: transaction.item_id,
                location: transaction.toll_location,
                amount: transaction.invoice_amount,
                createTs,
                isDisputable: transaction.disputable,
                disputeReason: 'NONE',
                transaction,
            });

            return acc;
        }, {});

        return Object.keys(licensePlateMap).map((fullLicensePlate : string) : LicensePlate => {
            const transactionItems : TransactionItem[] = licensePlateMap[fullLicensePlate];
            const amount = transactionItems.reduce((sum : number, item : TransactionItem) => sum + item.amount, 0);

            return {
                lpNumber: fullLicensePlate,
                amount,
                transactionItems
            };
        });
    }

    calcCheckedInvoices () {
        if (!this.invoiceItems) {
            return;
        }

        this.checkedInvoiceAmount = this.invoiceItems.reduce((sum : number, item : InvoiceItem) : number => {
            return sum + (item.isChecked ? item.amount : 0);
        }, 0);

        this.isActionsVisible = this.checkedInvoiceAmount > 0;
    }

    checkIsAllInvoicesChecked () {
        this.isAllInvoicesChecked = this.invoiceItems.every(item => item.isChecked);
    }

    onCheckAllInvoices () {
        if (this.isSubmitting) {
            return;
        }

        const isAllChecked = this.isAllInvoicesChecked = !this.isAllInvoicesChecked;
        this.invoiceItems.forEach(item => item.isChecked = isAllChecked);
        this.onSelectionChanged();
    }

    onCheckOneInvoice (invoiceItem : InvoiceItem) {
        invoiceItem.isChecked = !invoiceItem.isChecked;
        this.checkIsAllInvoicesChecked();
        this.onSelectionChanged();
    }

    onCheckboxCellClick (invoiceItem : InvoiceItem, e : MouseEvent) {
        if (this.isSubmitting) {
            return;
        }

        this.domService.markEvent(e, 'dontOpenInvoice');
        this.onCheckOneInvoice(invoiceItem);
    }

    onItemClick (invoiceItem : InvoiceItem, e : MouseEvent) {
        if (this.isSubmitting) {
            return;
        }

        if (!this.domService.hasEventMark(e, 'dontOpenInvoice')) {
            this.notifyOnShowInvoiceDetails([ invoiceItem ]);
        }
    }

    onSelectionChanged () {
        this.calcCheckedInvoices();
        this.invoiceItemsToPay = this.invoiceItems.filter((invoiceItem : InvoiceItem) => invoiceItem.isChecked);
    }

    onShowDetails () {
        const itemsToPay = this.getCheckedItems(this.invoiceItems);

        if (itemsToPay.length === 0) {
            return;
        }

        this.notifyOnShowInvoiceDetails(itemsToPay);
    }

    onPaymentSuccess (paidInvoiceIds : string[]) {
        this.invoiceItems = this.invoiceItems.filter((invoiceItem : InvoiceItem) => {
            return !paidInvoiceIds.includes(invoiceItem.id);
        });

        this.checkIsAllInvoicesChecked();
        this.calcCheckedInvoices();
        this.notifyOnInvoicesListInited(); // TODO: rename

        this.listState = this.invoiceItems.length > 0 ? 'list' : 'empty';
        this.isSubmitting = false;
    }

    onPaymentBegin () {
        this.isSubmitting = true;
    }

    onPaymentCancel () {
        this.isSubmitting = false;
    }

    onPaymentChecked () {
        defer(() => this.fetchInvoices());
    }

    onMakePayment () {
        this.paymentComponent.makePayment();
    }

    // -------------------------------------------

    getCheckedItems (invoiceItems : InvoiceItem[]) : InvoiceItem[] {
        if (!invoiceItems) {
            return [];
        }

        return invoiceItems.filter(invoice => invoice.isChecked);
    }

    getInvoicesFromItems (invoiceItems : InvoiceItem[]) : Invoice[] {
        if (!invoiceItems) {
            return null;
        }

        return invoiceItems.map(item => item.invoice);
    }

    notifyOnInvoicesListInited () {
        this.onInvoicesListInited.emit({
            invoiceItems: this.invoiceItems,
            coverageLocations: this.coverageLocations
        });
    }

    notifyOnShowInvoiceDetails (invoiceItems : InvoiceItem[]) {
        this.onShowInvoiceDetails.emit(invoiceItems);
    }
}
