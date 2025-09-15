import {
    ChangeDetectionStrategy,
    Component,
    EventEmitter,
    Input,
    OnDestroy,
    OnInit,
    Output,
    ViewChild,
    ViewEncapsulation
} from '@angular/core';
import {TitleService} from '../../../services/title.service';
import {DeviceService, ViewportBreakpoint} from '../../../services/device.service';
import {forkJoin, Observable, Subscription} from 'rxjs';
import {
    AllInvoicesHttpResponseModel,
    InvoiceItemBackendModel,
    InvoiceItemUIModel,
    InvoicesService,
    LicensePlate,
    Transaction,
    TransactionItem
} from '../invoices.service';
import {DomService} from '../../../services/dom.service';
import {animateChild, query, transition, trigger} from '@angular/animations';
import {PaymentConfig, PaymentService} from '../../../services/payment.service';
import {InvoicePaymentComponent} from '../invoice-payment/invoice-payment.component';
import {defer} from '../../../lib/utils';
import {Coverage, CoverageLocation, CoverageService} from '../../../services/coverage.service';
import {AccountPaymentModel, AccountTollAuthority, UserService} from '../../../services/user.service';
import {catchError} from "rxjs/operators";

type ListState = 'loading' | 'list' | 'empty' | 'error';

export interface OnInvoicesListInitedEvent {
    invoiceItems: { regular: InvoiceItemUIModel[], subscription: InvoiceItemUIModel[] };
    coverageLocations: CoverageLocation[];
    surchargeSum: number;
}

@Component({
    selector: 'app-invoices-list',
    exportAs: 'invoicesList',
    templateUrl: './invoices-list.component.html',
    styleUrls: ['./invoices-list.component.scss'],
    changeDetection: ChangeDetectionStrategy.Default,
    encapsulation: ViewEncapsulation.None,
    host: {
        'class': 'invoices-list',
        '[@invoicesListHost]': 'true'
    },
    animations: [
        trigger('invoicesListHost', [
            transition(':enter', [
                query('@*', animateChild(), {optional: true}),
            ]),
        ]),
    ]
})
export class InvoicesListComponent implements OnInit, OnDestroy {
    viewportBreakpoint: ViewportBreakpoint;

    subs: Subscription[] = [];

    listState: ListState = 'loading';

    readonly lowExpireThreshold = 60 * 60 * 1000;

    readonly showExpireThreshold = 24 * 60 * 60 * 1000;

    readonly isAllInvoicesSelectedByDefault: boolean = true;

    @Input() allInvoices: { regular: InvoiceItemUIModel[], subscription: InvoiceItemUIModel[] } = {
        regular: [],
        subscription: []
    };

    @Input() surchargeSum: number = 0;

    invoiceItemsToPay: InvoiceItemUIModel[];

    // @Input()
    paymentConfig: PaymentConfig;

    // @Input()
    // paymentMethod : PaymentMethod;

    @Output()
    invoicesListInited = new EventEmitter<OnInvoicesListInitedEvent>();

    @Output()
    showInvoiceDetails = new EventEmitter<InvoiceItemUIModel[]>();

    @ViewChild('paymentComponent', {read: InvoicePaymentComponent})
    paymentComponent: InvoicePaymentComponent;

    isAllInvoicesSelectedToPay: boolean = false;

    checkedInvoiceAmountSum: number = 0;

    isActionsVisible: boolean = false;

    onPaymentConfigChangedSub: Subscription;

    isSubmitting: boolean = false;

    coverageLocations: CoverageLocation[];

    allDataFetchSub$: Subscription;

    paymentModel: AccountPaymentModel = null;

    tollAuthority: AccountTollAuthority = null;

    private invoices$: Observable<AllInvoicesHttpResponseModel> = this.invoicesService.fetchInvoices();
    private paymentConfig$: Observable<PaymentConfig> = this.paymentService.fetchPaymentConfig();
    private coverage$: Observable<Coverage> = this.coverageService.getMapCoverageFullData();

    constructor(
        private titleService: TitleService,
        private domService: DomService,
        private invoicesService: InvoicesService,
        private paymentService: PaymentService,
        private userService: UserService,
        private coverageService: CoverageService,
        private deviceService: DeviceService,
    ) {
        window.scroll(0, 0);

        const {account} = this.userService.getUserData();

        this.paymentModel = account.paymentModel;
        this.tollAuthority = account.tollAuthority;

    }

    ngOnInit() {
        this.titleService.setTitle('invoices.invoices_list.page_title');

        const isEmptyListsOfInvoices = !!this.allInvoices && this.allInvoices.regular.length === 0
            && this.allInvoices.subscription.length === 0;
        if (isEmptyListsOfInvoices) {
            this.fetchInvoices();
        } else {
            // TODO: mb uncheck all invoiceItems?
            this.checkIsAllInvoicesChecked();
            this.onSelectionChanged();
            this.listState = this.getListState(this.allInvoices);
        }

        this.viewportBreakpoint = this.deviceService.viewportBreakpoint;
        this.subs.push(this.deviceService.onResize.subscribe((message) => {
            if (message.breakpointChange) {
                this.viewportBreakpoint = message.breakpointChange.current;
            }
        }));
    }

    ngOnDestroy(): void {
        this.subs.forEach(sub => sub.unsubscribe());
        this.unsubscribeFetchSub();

        if (this.onPaymentConfigChangedSub) {
            this.onPaymentConfigChangedSub.unsubscribe();
        }
    }

    public fetchInvoices() {
        this.listState = 'loading';
        this.unsubscribeFetchSub();

        this.allDataFetchSub$ = forkJoin([this.invoices$, this.paymentConfig$, this.coverage$])
            .pipe(
                catchError(error => {
                    this.handleError();
                    throw error;
                })
            )
            .subscribe(async ([invoices, paymentConfig, coverage]) => {
                await this.handleSuccessfulFetch(invoices, paymentConfig, coverage);
            });
    }

    private async handleSuccessfulFetch(invoicesResponse: AllInvoicesHttpResponseModel, paymentConfig: PaymentConfig, coverage: Coverage) {
        console.log("handleSuccessfulFetch");
        this.coverageLocations = await this.coverageService.coverageToLocations(coverage, this.tollAuthority, false);
        this.paymentConfig = paymentConfig;

        this.surchargeSum = invoicesResponse.surcharge;

        this.allInvoices.regular = invoicesResponse.invoices.length ? this.convertInvoicesFromBackendToUIModel(this.excludeInvoicesByType(invoicesResponse.invoices, 'SUBSCRIPTION_RENEWAL')) : [];
        this.allInvoices.subscription = invoicesResponse.invoices.length ? this.convertInvoicesFromBackendToUIModel(this.filterBackendInvoicesByType(invoicesResponse.invoices, 'SUBSCRIPTION_RENEWAL')) : [];
        this.listState = (this.allInvoices.regular.length > 0 || this.allInvoices.subscription.length > 0) ? 'list' : 'empty';

        this.checkIsAllInvoicesChecked();
        this.onSelectionChanged();
        this.managePaymentConfigSubscription();
        this.notifyOnInvoicesListInited();

    }

    private handleError() {
        this.paymentConfig = null;
        this.allInvoices = null;
        this.listState = 'error';
        this.notifyOnInvoicesListInited();
    }

    private managePaymentConfigSubscription() {
        this.onPaymentConfigChangedSub?.unsubscribe();

        this.onPaymentConfigChangedSub = this.paymentService.onPaymentConfigChanged$
            .subscribe(paymentConfig => {
                this.paymentConfig = paymentConfig;
                this.calcCheckedInvoices();
            });
    }

    private unsubscribeFetchSub() {
        this.allDataFetchSub$?.unsubscribe();
    }

    convertInvoicesFromBackendToUIModel(invoices: InvoiceItemBackendModel[]): InvoiceItemUIModel[] {
        return invoices.map((invoice: InvoiceItemBackendModel): InvoiceItemUIModel => {
            const expirationTimestamp = new Date(invoice.invoice_expiration_date).getTime();
            const timeUntilExpiration: number = Math.round(expirationTimestamp - Date.now());
            const millisecondsUntilExpiration = Math.max(0, timeUntilExpiration);

            return {
                id: invoice.invoice_id,
                name: invoice.invoice_name,
                amount: invoice.invoice_amount,
                transactionCount: invoice.items.length,
                createTs: new Date(invoice.invoice_date).getTime(),
                hoursLeft: Math.max(1, Math.round(millisecondsUntilExpiration / 1000 / 60 / 60)),
                isPassedDue: timeUntilExpiration < 0,
                isLowTimeLeft: millisecondsUntilExpiration <= this.lowExpireThreshold,
                showTimeLeft: millisecondsUntilExpiration < this.showExpireThreshold,
                isSelectedToPay: this.isAllInvoicesSelectedByDefault,
                invoice,
                licensePlates: this.convertTransactionsToLicensePlates(invoice.items)
            };
        });
    }

    convertTransactionsToLicensePlates(transactions: Transaction[]): LicensePlate[] {
        const groupedByLicensePlate = this.groupTransactionsByLicensePlate(transactions);
        return this.convertGroupsToLicensePlates(groupedByLicensePlate);
    }

    private groupTransactionsByLicensePlate(transactions: Transaction[]): { [key: string]: TransactionItem[] } {
        return transactions.reduce((acc: { [key: string]: TransactionItem[] }, transaction: Transaction) => {
            const fullLicensePlate = `${transaction.lps} ${transaction.lpn}`;
            const createTs = new Date(transaction.toll_date).getTime();

            const licensePlateTransactions = acc[fullLicensePlate] || [];
            licensePlateTransactions.push({
                id: transaction.item_id,
                location: transaction.toll_location,
                amount: transaction.invoice_amount,
                createTs,
                isDisputable: transaction.disputable,
                disputeReason: 'NONE',
                transaction,
            });

            acc[fullLicensePlate] = licensePlateTransactions;
            return acc;
        }, {});
    }

    private convertGroupsToLicensePlates(groupedByLicensePlate: { [key: string]: TransactionItem[] }): LicensePlate[] {
        return Object.keys(groupedByLicensePlate).map(fullLicensePlate => {
            const transactionItems = groupedByLicensePlate[fullLicensePlate];
            const totalAmount = this.calculateTotalAmount(transactionItems);

            return {
                lpNumber: fullLicensePlate,
                amount: totalAmount,
                transactionItems
            };
        });
    }

    private calculateTotalAmount(transactionItems: TransactionItem[]): number {
        return transactionItems.reduce((sum, item) => sum + item.amount, 0);
    }


    private calcCheckedInvoices() {
        if (!this.allInvoices?.regular && !this.allInvoices?.subscription) {
            this.checkedInvoiceAmountSum = 0;
            this.isActionsVisible = false;
            return;
        }

        const calculateSum = (invoices: { isSelectedToPay: boolean, amount: number }[]) =>
            invoices.reduce((sum, {isSelectedToPay, amount}) =>
                sum + (isSelectedToPay ? amount : 0), 0);

        const checkedInvoicesSum = this.allInvoices.regular ? calculateSum(this.allInvoices.regular) : 0;
        const checkedSubscriptionInvoicesSum = this.allInvoices.subscription ? calculateSum(this.allInvoices.subscription) : 0;


        this.checkedInvoiceAmountSum = checkedInvoicesSum + checkedSubscriptionInvoicesSum;
        if (this.checkedInvoiceAmountSum > 0) {
            this.checkedInvoiceAmountSum += this.surchargeSum;
        }

        this.isActionsVisible = this.checkedInvoiceAmountSum > 0;
    }


    checkIsAllInvoicesChecked() {
        const invoicesListsNotEmpty = this.allInvoices && (this.allInvoices.regular.length > 0 || this.allInvoices.subscription.length > 0);

        if (!invoicesListsNotEmpty) {
            this.isAllInvoicesSelectedToPay = false;
            return;
        }

        const allInvoicesSelectedToPay = this.allInvoices.regular.every(item => item.isSelectedToPay);
        const allSubscriptionInvoicesSelectedToPay = this.allInvoices.subscription.every(item => item.isSelectedToPay);
        this.isAllInvoicesSelectedToPay = allInvoicesSelectedToPay && allSubscriptionInvoicesSelectedToPay;
    }

    onCheckAllInvoices() {
        if (this.isSubmitting) {
            return;
        }

        const isAllInvoicesSelectedToPay = this.isAllInvoicesSelectedToPay = !this.isAllInvoicesSelectedToPay;


        this.allInvoices.regular.forEach(
            invoiceItem => invoiceItem.isSelectedToPay = isAllInvoicesSelectedToPay
        );

        this.allInvoices.subscription.forEach(
            invoiceItem => invoiceItem.isSelectedToPay = isAllInvoicesSelectedToPay
        );

        this.onSelectionChanged();
    }

    onCheckOneInvoice(invoiceItem: InvoiceItemUIModel) {
        invoiceItem.isSelectedToPay = !invoiceItem.isSelectedToPay;
        this.checkIsAllInvoicesChecked();
        this.onSelectionChanged();
    }

    onCheckboxCellClick(invoiceItem: InvoiceItemUIModel, e: MouseEvent) {
        e.preventDefault();
        e.stopPropagation();
        if (this.isSubmitting) {
            return;
        }

        this.domService.markEvent(e, 'dontOpenInvoice');
        this.onCheckOneInvoice(invoiceItem);
    }

    onItemClick(invoiceItem: InvoiceItemUIModel, e: MouseEvent) {
        if (this.isSubmitting) {
            return;
        }

        if (!this.domService.isHasEventMark(e, 'dontOpenInvoice')) {
            this.notifyOnShowInvoiceDetails([invoiceItem]);
        }
    }

    onSelectionChanged() {
        this.calcCheckedInvoices();
        this.invoiceItemsToPay = [
            ...this.allInvoices.regular.filter(
                (invoiceItem: InvoiceItemUIModel) => invoiceItem.isSelectedToPay
            ),
            ...this.allInvoices.subscription.filter(
                (invoiceItem: InvoiceItemUIModel) => invoiceItem.isSelectedToPay
            )];
    }

    onShowDetails() {
        const invoiceItems = [...this.allInvoices.regular, ...this.allInvoices.subscription];
        const itemsToPay = this.getSelectedToPayInvoicesItems(invoiceItems);

        if (itemsToPay.length === 0) {
            return;
        }

        this.notifyOnShowInvoiceDetails(itemsToPay);
    }

    onPaymentSuccess() {
        this.fetchInvoices();
        this.isSubmitting = false;
    }

    onPaymentBegin() {
        this.isSubmitting = true;
    }

    onPaymentCancel() {
        this.isSubmitting = false;
    }

    onPaymentChecked() {
        defer(() => this.fetchInvoices());
    }

    onMakePayment(event: { autoPayControlIsShown: boolean, isAutoPaymentEnabled: boolean }) {
        this.paymentComponent.makePayment(event.isAutoPaymentEnabled, event.autoPayControlIsShown);
    }

    // -------------------------------------------

    getSelectedToPayInvoicesItems(invoiceItems: InvoiceItemUIModel[]): InvoiceItemUIModel[] {
        if (!invoiceItems) {
            return [];
        }

        return invoiceItems.filter(invoice => invoice.isSelectedToPay);
    }

    getInvoicesFromItems(invoiceItems: InvoiceItemUIModel[]): InvoiceItemBackendModel[] {
        if (!invoiceItems) {
            return null;
        }

        return invoiceItems.map(item => item.invoice);
    }

    notifyOnInvoicesListInited() {
        this.invoicesListInited.emit({
            invoiceItems: this.allInvoices,
            coverageLocations: this.coverageLocations,
            surchargeSum: this.surchargeSum
        });
    }

    notifyOnShowInvoiceDetails(invoiceItems: InvoiceItemUIModel[]) {
        this.showInvoiceDetails.emit(invoiceItems);
    }

    private excludeInvoicesByType(invoices: InvoiceItemBackendModel[], type: string): InvoiceItemBackendModel[] {
        return invoices.filter(invoice => invoice.invoice_type !== type);
    }

    private filterBackendInvoicesByType(invoices: InvoiceItemBackendModel[], type: string): InvoiceItemBackendModel[] {
        return invoices.filter(invoice => invoice.invoice_type === type);
    }

    trackByFn(index: number, item: InvoiceItemUIModel) {
        return item.id;
    }

    private getListState(invoices: {
        regular: InvoiceItemUIModel[];
        subscription: InvoiceItemUIModel[];
    }): ListState {
        const regularInvoices = invoices.regular;
        const subscriptionInvoices = invoices.subscription;

        const isRegularInvoicesEmpty = regularInvoices.length === 0;
        const isSubscriptionInvoicesEmpty = subscriptionInvoices.length === 0;

        if (isRegularInvoicesEmpty && isSubscriptionInvoicesEmpty) {
            return 'empty';
        } else {
            return 'list';
        }
    }
}
