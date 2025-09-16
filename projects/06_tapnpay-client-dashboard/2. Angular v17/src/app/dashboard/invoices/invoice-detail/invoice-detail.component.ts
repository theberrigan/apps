import {
    ChangeDetectionStrategy,
    Component,
    EventEmitter,
    HostListener,
    Input,
    OnDestroy,
    OnInit,
    Output,
    Renderer2,
    ViewChild,
    ViewEncapsulation
} from '@angular/core';
import {Router} from '@angular/router';
import {TitleService} from '../../../services/title.service';
import {DeviceService, ViewportBreakpoint} from '../../../services/device.service';
import {Subscription} from 'rxjs';
import {
    DisputeReason,
    DisputeReasonOption,
    InvoiceItemUIModel,
    InvoicesService,
    LicensePlate,
    TransactionItem
} from '../invoices.service';
import {DomService} from '../../../services/dom.service';
import {animate, animateChild, query, style, transition, trigger} from '@angular/animations';
import {ConfirmBoxComponent} from '../../../_widgets/popup/confirm-box/confirm-box.component';
import {InvoicePaymentComponent} from '../invoice-payment/invoice-payment.component';
import {CoverageLocation, CoverageLocationMap} from '../../../services/coverage.service';
import {UserService} from '../../../services/user.service';

type DisputeReasonMap = { [key in DisputeReason]: string };


@Component({
    selector: 'app-invoice-detail',
    exportAs: 'invoiceDetail',
    templateUrl: './invoice-detail.component.html',
    styleUrls: ['./invoice-detail.component.scss'],
    changeDetection: ChangeDetectionStrategy.Default,
    encapsulation: ViewEncapsulation.None,
    host: {
        'class': 'invoice-detail',
        '[@invoiceDetailHost]': 'true'
    },
    animations: [
        trigger('invoiceDetailHost', [
            transition(':enter', [
                query('@*', animateChild(), {optional: true}),
            ]),
        ]),
        trigger('dispute', [
            transition(':enter', [
                style({opacity: 0}),
                animate('0.1s cubic-bezier(0.5, 1, 0.89, 1)', style({opacity: '*'}))
            ]),
            transition(':leave', [
                style({opacity: '*'}),
                animate('0.1s cubic-bezier(0.5, 1, 0.89, 1)', style({opacity: 0}))
            ])
        ]),
    ],
})
export class InvoiceDetailComponent implements OnInit, OnDestroy {
    viewportBreakpoint: ViewportBreakpoint;

    subs: Subscription[] = [];

    @Output()
        // eslint-disable-next-line @angular-eslint/no-output-on-prefix
    onClose = new EventEmitter<void>();

    @Output()
        // eslint-disable-next-line @angular-eslint/no-output-on-prefix
    onDone = new EventEmitter<string[]>();

    @Input() allInvoices: { regular: InvoiceItemUIModel[], subscription: InvoiceItemUIModel[] } = {
        regular: [],
        subscription: []
    };

    @Input()
    invoiceItems: InvoiceItemUIModel[];

    @Input()
    coverageLocations: CoverageLocation[];

    @Input() surchargeSum: number;

    @ViewChild('disputeReasonResetConfirmBox', {read: ConfirmBoxComponent})
    disputeReasonResetConfirmBox: ConfirmBoxComponent;

    @ViewChild('paymentComponent', {read: InvoicePaymentComponent})
    paymentComponent: InvoicePaymentComponent;

    isReady: boolean;

    totalAmount: number = 0;

    canPay: boolean = false;

    disputeReasonOptions: DisputeReasonOption[] = [];

    disputeReason: DisputeReason = 'NONE';

    disputeReasonMap: DisputeReasonMap;

    disputeInterfaceId: string;

    menuActiveTransactionItemId: string;

    isDisputeRejectedPopupVisible: boolean = false;

    isSubmitting: boolean = false;

    printDate: Date = new Date();

    coverageLocationMap: CoverageLocationMap;

    activeCoverageLocation: CoverageLocation;

    isMapAvailable: boolean;

    isDispute: boolean;

    constructor(
        private renderer: Renderer2,
        private router: Router,
        private titleService: TitleService,
        private deviceService: DeviceService,
        private domService: DomService,
        private invoicesService: InvoicesService,
        private userService: UserService,
    ) {
        window.scroll(0, 0);

        this.isMapAvailable = true;

        this.viewportBreakpoint = this.deviceService.viewportBreakpoint;
        this.subs.push(this.deviceService.onResize.subscribe((message) => {
            if (message.breakpointChange) {
                this.viewportBreakpoint = message.breakpointChange.current;
            }
        }));

        this.isReady = false;
    }

    ngOnInit() {
        this.titleService.setTitle('invoices.invoice_detail.page_title');

        this.disputeReasonOptions = this.invoicesService.getDisputeReasonOptions();
        this.disputeReasonMap = this.disputeReasonOptions.reduce((map: DisputeReasonMap, disputeReasonOption: DisputeReasonOption) => {
            map[disputeReasonOption.value] = disputeReasonOption.display;
            return map;
        }, {} as DisputeReasonMap);

        this.createLocationMap();
        this.calcAllInvoices();

        this.isReady = true;
    }

    ngOnDestroy(): void {
        this.subs.forEach(sub => sub.unsubscribe());
    }

    createLocationMap() {
        this.coverageLocationMap = {};

        if (!this.isMapAvailable || !this.coverageLocations) {
            return;
        }

        this.invoiceItems.forEach(({licensePlates}) => {
            licensePlates.forEach(({transactionItems}) => {
                transactionItems.forEach(({location}) => {
                    if (!location) {
                        return;
                    }
                    location = location.trim().toUpperCase();
                    this.coverageLocationMap[location] = this.getCoverageLocationByName(location);
                });
            });
        });
    }

    private getCoverageLocationByName(location: string) {
        return this.coverageLocations.find(item => {
            const gantryCode = item.gantry.code.trim().toUpperCase();
            return location.startsWith(gantryCode);
        });
    }

    calcAllInvoices() {
        this.totalAmount = 0;

        this.invoiceItems.forEach((invoiceItem: InvoiceItemUIModel) => {
            this.updateInvoiceItem(invoiceItem);
            this.totalAmount += invoiceItem.amount;
        });

        if (this.totalAmount > 0) {
            this.totalAmount += this.surchargeSum;
        }

        // this.canPay = this.totalAmount >= this.paymentConfig.min_payment_amount;
        this.canPay = this.totalAmount > 0;

        this.invoiceItems = [...this.invoiceItems];
    }

    hasLocationRoute(location: string): boolean {
        return !!(this.isMapAvailable && this.coverageLocationMap && this.coverageLocationMap[location]);
    }

    updateInvoiceItem(invoiceItem: InvoiceItemUIModel): InvoiceItemUIModel {
        invoiceItem.amount = 0;

        invoiceItem.licensePlates.forEach((licensePlate: LicensePlate) => {
            this.updateLicensePlate(licensePlate);
            invoiceItem.amount += licensePlate.amount;
        });

        return invoiceItem;
    }

    updateLicensePlate(licensePlate: LicensePlate): LicensePlate {
        licensePlate.amount = 0;

        licensePlate.transactionItems.forEach((transactionItem: TransactionItem) => {
            if (transactionItem.disputeReason === 'NONE') {
                licensePlate.amount += transactionItem.amount;
            } else {
                this.isDispute = true;
            }
        });

        return licensePlate;
    }

    onCommitDisputeReason(licensePlate: LicensePlate, transactionItem: TransactionItem) {
        if (this.isSubmitting) {
            return;
        }

        const disputedSiblings: TransactionItem[] = licensePlate.transactionItems.filter((item: TransactionItem) => {
            return item.id !== transactionItem.id && item.disputeReason !== 'NONE';
        });

        if (disputedSiblings.length === 0 || disputedSiblings[0].disputeReason === this.disputeReason) {
            transactionItem.disputeReason = this.disputeReason;
            this.calcAllInvoices();
            this.onHideDisputeInterface();
        } else {
            this.disputeReasonResetConfirmBox.confirm().subscribe((isOk: boolean) => {
                if (isOk) {
                    transactionItem.disputeReason = this.disputeReason;
                    disputedSiblings.forEach((item: TransactionItem) => item.disputeReason = this.disputeReason);
                    this.calcAllInvoices();
                    this.onHideDisputeInterface();
                }
            });
        }
    }

    onShowDisputeRejectedPopup() {
        this.isDisputeRejectedPopupVisible = true;
    }

    onHideDisputeRejectedPopup() {
        this.isDisputeRejectedPopupVisible = false;
    }

    onShowDisputeInterface(licensePlate: LicensePlate, transactionItem: TransactionItem) {
        if (this.isSubmitting) {
            return;
        }

        if (!transactionItem.isDisputable) {
            this.onShowDisputeRejectedPopup();
            return;
        }

        const disputedSibling = licensePlate.transactionItems.find((item: TransactionItem) => {
            return item.id !== transactionItem.id && item.disputeReason !== 'NONE';
        });

        if (transactionItem.disputeReason === 'NONE' && disputedSibling) {
            this.disputeReason = disputedSibling.disputeReason;
        } else {
            this.disputeReason = transactionItem.disputeReason;
        }

        this.disputeInterfaceId = transactionItem.id;
    }

    onHideDisputeInterface() {
        if (this.isSubmitting) {
            return;
        }

        this.disputeReason = 'NONE';
        this.disputeInterfaceId = null;
        this.invoiceItems = [...this.invoiceItems];
    }

    onCancelDispute(transactionItem: TransactionItem) {
        if (this.isSubmitting) {
            return;
        }

        transactionItem.disputeReason = 'NONE';
        this.calcAllInvoices();
    }

    onPay(event: { autoPayControlIsShown: boolean, isAutoPaymentEnabled: boolean }) {
        if (this.isSubmitting) {
            return;
        }

        this.paymentComponent.makePayment(event.isAutoPaymentEnabled, event.autoPayControlIsShown);
    }

    // --------------------------------------

    onMenuTriggerClick(transactionItem: TransactionItem, e: MouseEvent) {
        if (this.isSubmitting) {
            return;
        }

        this.domService.markEvent(e, 'idmMenuTriggerClick');

        // if (!transactionItem.isDisputable) {
        //     return;
        // }

        if (this.menuActiveTransactionItemId === transactionItem.id) {
            this.menuActiveTransactionItemId = null;
        } else {
            this.menuActiveTransactionItemId = transactionItem.id;
        }
    }

    onMenuClick(e: MouseEvent) {
        if (this.isSubmitting) {
            return;
        }

        this.domService.markEvent(e, 'idmMenuClick');
    }

    onMenuItemClick(e: MouseEvent) {
        if (this.isSubmitting) {
            return;
        }

        this.domService.markEvent(e, 'idmMenuItemClick');
    }

    @HostListener('document:click', ['$event'])
    onDocClick(e: MouseEvent) {
        if (this.isSubmitting) {
            return;
        }

        const isTriggerClick = this.domService.isHasEventMark(e, 'idmMenuTriggerClick');
        const isMenuClick = this.domService.isHasEventMark(e, 'idmMenuClick');
        const isMenuItemClick = this.domService.isHasEventMark(e, 'idmMenuItemClick');

        if (!isTriggerClick && (!isMenuClick || isMenuItemClick)) {
            this.menuActiveTransactionItemId = null;
        }
    }

    onShowMobileDisputeInterface(licensePlate: LicensePlate, transactionItem: TransactionItem, e: MouseEvent) {
        if (this.isSubmitting) {
            return;
        }

        this.onMenuItemClick(e);
        this.onShowDisputeInterface(licensePlate, transactionItem);
    }

    onCancelDisputeMobile(transactionItem: TransactionItem, e: MouseEvent) {
        if (this.isSubmitting) {
            return;
        }

        this.onMenuItemClick(e);
        this.onCancelDispute(transactionItem);
    }

    onPaymentSuccess(paidInvoiceIds: string[]) {

        this.isSubmitting = false;
        this.onDone.emit(paidInvoiceIds);
    }

    onPaymentBegin() {
        this.isSubmitting = true;
    }

    onPaymentCancel() {
        this.isSubmitting = false;
    }

    // --------------------------------------

    onShowLocationMap(location: string) {
        if (!this.isMapAvailable || !this.hasLocationRoute(location)) {
            return;
        }

        this.activeCoverageLocation = this.coverageLocationMap[location];
    }

    onMapClose() {
        this.activeCoverageLocation = null;
    }

    // --------------------------------------


    onGoBack() {
        if (this.isSubmitting) {
            return;
        }

        this.onClose.emit();
    }

    @HostListener('window:beforeprint')
    onBeforePrint() {
        this.printDate = new Date();
    }

    onPrint() {
        window.print();
    }

    isShowPaymentMessage(): boolean {
        return this.invoiceItems && this.invoiceItems.length > 0 && this.invoiceItems.length === 1;
    }

    isSubscriptionRenewal(invoiceItem: InvoiceItemUIModel): boolean {
        return invoiceItem.invoice.invoice_type === 'SUBSCRIPTION_RENEWAL';
    }

    trackByFn(index, item: InvoiceItemUIModel | TransactionItem) {
        return item.id; // Use the 'id' property as the unique identifier
    }
}
