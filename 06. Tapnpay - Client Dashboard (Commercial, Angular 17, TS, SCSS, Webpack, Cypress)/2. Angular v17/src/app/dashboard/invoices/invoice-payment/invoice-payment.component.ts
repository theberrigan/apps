import {
    ChangeDetectionStrategy,
    Component,
    Input,
    OnDestroy,
    OnInit, Output,
    ViewEncapsulation,
    EventEmitter
} from '@angular/core';
import {Router} from '@angular/router';
import {Location} from '@angular/common';
import {DeviceService, ViewportBreakpoint} from '../../../services/device.service';
import {firstValueFrom, Subscription} from 'rxjs';
import {
    DEFAULT_INVOICES_PAYMENT_ERROR_CODE, InvoiceItemUIModel,
    InvoicePaymentInvoice,
    InvoicePaymentResponseWithError,
    InvoicePaymentTransaction,
    InvoicesService,
    LicensePlate,
    TransactionItem
} from '../invoices.service';
import {animateChild, query, transition, trigger} from '@angular/animations';
import {PaymentConfig, PaymentService} from '../../../services/payment.service';
import {CurrencyService} from '../../../services/currency.service';
import {DatetimeService} from '../../../services/datetime.service';
import {StripeService, PaymentMethodWallet} from '../../../services/stripe.service';
import {
    PaymentMethodDoneEvent,
    PaymentMethodPopupMode
} from '../../payment-method/payment-method/payment-method.component';
import {Base64Service} from '../../../services/base64.service';
import {AccountPaymentModel, AccountStatus, UserService} from '../../../services/user.service';
import {AutopaymentService} from "../../../services/autopayment.service";
import {ToastService} from "../../../services/toast.service";
import PaymentIntentResponse = stripe.PaymentIntentResponse;

type ActivePopup =
    'zip'
    | 'method'
    | 'invoice-payment-result'
    | 'wallet-payment-confirm'
    | 'invoice-payment-result-402';

@Component({
    selector: 'invoice-payment',
    exportAs: 'invoicePayment',
    templateUrl: './invoice-payment.component.html',
    styleUrls: ['./invoice-payment.component.scss'],
    changeDetection: ChangeDetectionStrategy.Default,
    encapsulation: ViewEncapsulation.None,
    host: {
        'class': 'invoice-payment',
        '[@invoicePaymentHost]': 'true'
    },
    animations: [
        trigger('invoicePaymentHost', [
            transition(':enter', [
                query('@*', animateChild(), {optional: true}),
            ]),
        ]),
    ],
})
export class InvoicePaymentComponent implements OnInit, OnDestroy {
    viewportBreakpoint: ViewportBreakpoint;
    subs: Subscription[] = [];

    @Input()
    invoiceItems: InvoiceItemUIModel[];

    @Input()
    totalAmount: number = 0;
    paymentConfig: PaymentConfig;

    @Output()
    paymentBegin = new EventEmitter<void>();

    @Output()
    paymentSuccess = new EventEmitter<string[]>();

    @Output()
    paymentCancel = new EventEmitter<void>();

    @Output()
    paymentChecked = new EventEmitter<void>();

    zipCode: string = '';

    isIncorrectZipVisible: boolean = false;

    isZipPopupValid: boolean = false;

    isSubmitting: boolean = false;

    paidInvoiceIds: string[];

    resultMessageKey: string;

    resultMessageData: any;

    isPaymentResultOk: boolean = false;

    methodPopupMode: PaymentMethodPopupMode;

    extremePopupMessageKey: string;

    extremePopupMessageData: any = {};

    stripe: any;

    onPaymentConfigChangedSub: Subscription;

    activePopup: ActivePopup = null;

    walletPaymentAttrs: {
        amountFormatted: string;
        wallet: string;
        paymentRequest: any;
    } = null;

    hasDisputed: boolean = false;

    paymentModel: AccountPaymentModel = null;

    accountStatus: AccountStatus = null;

    constructor(
        private router: Router,
        private location: Location,
        private deviceService: DeviceService,
        private invoicesService: InvoicesService,
        private currencyService: CurrencyService,
        private datetimeService: DatetimeService,
        private paymentService: PaymentService,
        private stripeService: StripeService,
        private base64Service: Base64Service,
        private userService: UserService,
        private autoPaymentService: AutopaymentService,
        private toastService: ToastService
    ) {
        window.scroll(0, 0);

        this.paymentModel = this.userService.getUserData().account.paymentModel;
        this.accountStatus = this.userService.getUserData().account.accountStatus;

        this.viewportBreakpoint = this.deviceService.viewportBreakpoint;
        this.subs.push(this.deviceService.onResize.subscribe((message) => {
            if (message.breakpointChange) {
                this.viewportBreakpoint = message.breakpointChange.current;
            }
        }));
    }

    ngOnInit() {
        if (this.onPaymentConfigChangedSub) {
            this.onPaymentConfigChangedSub.unsubscribe();
        }

        this.onPaymentConfigChangedSub = (
            this.paymentService.onPaymentConfigChanged$
                .asObservable()
                .subscribe((paymentConfig: PaymentConfig) => {
                    this.paymentConfig = paymentConfig;
                })
        );

        this.checkPayPalPaymentResult();
    }

    ngOnDestroy(): void {
        this.subs.forEach(sub => sub.unsubscribe());

        if (this.onPaymentConfigChangedSub) {
            this.onPaymentConfigChangedSub.unsubscribe();
        }
    }

    async makePayment(isAutoPaymentEnabled: boolean = false, autoPayControlIsShown: boolean = false) {
        this.paymentBegin.emit();

        if (isAutoPaymentEnabled && autoPayControlIsShown) {
            this.enableAutoPayment();
        }

        this.paymentConfig = await firstValueFrom(this.paymentService.fetchPaymentConfig());
        //this.paymentConfig.payment_method_type = 'APPLEPAY';
        this.stripe = await this.stripeService.getStripeInstance();

        const isPaymentMethodAvailable = await this.isCurrentPaymentMethodAvailable();

        if (isPaymentMethodAvailable) {
            await this.payUsingCurrentMethod();
        } else {
            this.showPaymentMethodPopup();
        }
    }

    async isCurrentPaymentMethodAvailable(): Promise<boolean> {
        return this.paymentService.checkCurrentPaymentMethod(this.paymentConfig);
    }

    async onPaymentMethodSelected(event: PaymentMethodDoneEvent) {
        this.paymentConfig = event.isOk && event.paymentConfig || event.paymentConfig;

        const isPaymentMethodAvailable = await this.isCurrentPaymentMethodAvailable();

        if (isPaymentMethodAvailable) {
            this.payUsingCurrentMethod();
        } else {
            this.showResultPopup(false, 'invoices.invoice_payment.payment_error_no_avail_method');
        }
    }

    showPaymentMethodPopup(popupMode: PaymentMethodPopupMode = 'change') {
        this.methodPopupMode = popupMode;
        this.activePopup = 'method';
    }

    async payUsingCurrentMethod() {
        if (!this.checkLimits()) {
            return;
        }

        switch (this.paymentConfig.payment_method_type) {
            case 'DCB':
                this.payByCarrier();
                break;
            case 'PAYPAL':
                await this.payByPayPal();
                break;
            case 'DEBIT_CARD':
            case 'CREDIT_CARD':
                await this.payByCard();
                break;
            case 'GOOGLEPAY':
            case 'APPLEPAY':
                await this.payByWallet();
                break;
            case 'VENMO':
                await this.payByVenmo();
                break;
        }
    }

    async payByVenmo() {
        if (this.isSubmitting) {
            return;
        }

        this.isSubmitting = true;

        const {response, errorCode, metadata} = await this.invoicesService.makePayment({
            invoices: this.collectPaymentInvoices(),
            verification_code: null,
            payment_method_type: this.paymentConfig.payment_method_type,
            payment_method_id: this.paymentConfig.payment_method_id,
            return_url: null,
            cancel_url: null,
        }).toPromise().catch(error => error);

        this.isSubmitting = false;

        if (!errorCode && response.payment_complete) {
            this.showPaymentSuccess();
        } else {
            this.showPaymentError(errorCode, metadata);
        }
    }

    async payByPayPal() {
        if (this.isSubmitting) {
            return;
        }

        this.isSubmitting = true;

        let successMessageKey = 'invoices.invoice_payment.payment_success';

        if (this.paymentModel === 'FLEET' && this.hasDisputed) {
            successMessageKey = 'invoices.invoice_payment.payment_success_fleet_has_disputed';
        }

        const successMessageData = this.getSuccessMessageData();

        const successResultData = this.encodeJsonToUrl({
            messageKey: successMessageKey,
            messageData: successMessageData,
            hasDisputed: this.hasDisputed,
            accountStatus: this.accountStatus,
        });

        const cancelResultData = this.encodeJsonToUrl({
            messageKey: `invoices.invoice_payment.payment_error_${DEFAULT_INVOICES_PAYMENT_ERROR_CODE}`,
            messageData: {},
            hasDisputed: this.hasDisputed,
            accountStatus: this.accountStatus,
        });

        const {
            response,
            errorCode,
            metadata
        } = <InvoicePaymentResponseWithError>await this.invoicesService.makePayment({
            invoices: this.collectPaymentInvoices(),
            verification_code: null,
            payment_method_type: this.paymentConfig.payment_method_type,
            payment_method_id: this.paymentConfig.payment_method_id,
            return_url: `/dashboard/invoices?action=invoice_paypal_payment_complete&invoice_paypal_payment_result=${successResultData}`,
            cancel_url: `/dashboard/invoices?action=invoice_paypal_payment_cancel&invoice_paypal_payment_result=${cancelResultData}`,
        }).toPromise().catch(error => error);

        if (response?.payment_complete) {
            this.isSubmitting = false;
            this.showPaymentSuccess();
            // this.showResultPopup(true, successMessageKey, successMessageData);
            return;
        }

        const approveUrl = response?.payment_intent?.approve_payment_url;

        if (errorCode || !approveUrl) {
            this.isSubmitting = false;
            this.showPaymentError(errorCode || DEFAULT_INVOICES_PAYMENT_ERROR_CODE, metadata);
        } else {
            window.location.assign(approveUrl);
        }
    }

    async checkPayPalPaymentResult() {
        const currentUrl = new URL(window.location.href);
        const action = currentUrl.searchParams.get('action');

        switch (action) {
            case 'invoice_paypal_payment_complete':
            case 'invoice_paypal_payment_cancel':
                this.location.replaceState('/dashboard/invoices');

                const result = this.decodeUrlToJson(currentUrl.searchParams.get('invoice_paypal_payment_result'));

                if (result) {
                    this.hasDisputed = !!result.hasDisputed;
                    this.accountStatus = result.accountStatus;
                    this.showResultPopup(true, result.messageKey, result.messageData);
                }

                const transactionId = currentUrl.searchParams.get('transaction_id');

                if (transactionId && action === 'invoice_paypal_payment_complete') {
                    await this.paymentService.completePaymentIntent(transactionId).toPromise().catch(() => false);
                }

                this.paymentChecked.emit();

                break;
        }
    }

    encodeJsonToUrl(data: any): string {
        return encodeURIComponent(this.base64Service.encode(JSON.stringify(data)));
    }

    decodeUrlToJson(data: any): any {
        try {
            return JSON.parse(this.base64Service.decode(decodeURIComponent(data)));
        } catch (e) {
            return null;
        }
    }

    payByCarrier() {
        if (this.paymentConfig.payment_verification_required) {
            this.showZipPopup();
        } else {
            this.makeCarrierPaymentRequest();
        }
    }

    async makeCarrierPaymentRequest() {
        if (this.isSubmitting) {
            return;
        }

        this.isSubmitting = true;

        const zipCode: string = this.getZipCode();
        const invoices: InvoicePaymentInvoice[] = this.collectPaymentInvoices();

        const requestData = {
            invoices,
            verification_code: zipCode,
            payment_method_type: this.paymentConfig.payment_method_type,
            payment_method_id: this.paymentConfig.payment_method_id,
            return_url: null,
            cancel_url: null,
        };
        const {errorCode, metadata} = await firstValueFrom(
            this.invoicesService.makePayment(requestData)
        )

        this.isSubmitting = false;

        if (!errorCode) {
            this.showPaymentSuccess();
        } else {
            this.showPaymentError(errorCode, metadata);
        }
    }

    async payByCard() {
        if (this.isSubmitting) {
            return;
        }

        this.isSubmitting = true;

        const invoices: InvoicePaymentInvoice[] = this.collectPaymentInvoices();

        const requestData = {
            invoices,
            verification_code: null,
            payment_method_type: this.paymentConfig.payment_method_type,
            payment_method_id: this.paymentConfig.payment_method_id,
            return_url: null,
            cancel_url: null,
        };
        const {
            response: intentResponse,
            errorCode,
            metadata
        } = await this.invoicesService.makePayment(requestData).toPromise().catch(error => error);

        if (errorCode) {
            this.isSubmitting = false;
            this.showPaymentError(errorCode, metadata);
            return;
        }

        const paymentIntent = intentResponse.payment_intent;

        if (intentResponse.payment_complete) {
            this.isSubmitting = false;
            this.showPaymentSuccess();
            return;
        }

        // Payment incomplete
        // -------------------------------------------------------

        const paymentIntentResponse: PaymentIntentResponse = await this.stripe.confirmCardPayment(paymentIntent.client_secret).catch(() => null);

        if (!paymentIntentResponse) {
            this.isSubmitting = false;
            this.showPaymentError();
            return;
        }

        if (paymentIntentResponse.error) {
            this.isSubmitting = false;
            const error = this.stripeService.localizeStripeError(paymentIntentResponse.error);
            await this.showResultPopup(false, error.key, error.data);
            console.warn('Failed to auth 3D secure:', paymentIntentResponse);
            return;
        }

        const isOkOrError = await this.paymentService.completePaymentIntent(intentResponse.transaction_id).toPromise().catch(errorCode => errorCode);

        this.isSubmitting = false;

        if (isOkOrError === true) {
            this.showPaymentSuccess();
        } else if (isOkOrError === 308 || isOkOrError === 309) {
            this.showPaymentError(isOkOrError);
        } else if (isOkOrError === false) {
            this.showPaymentError();
        }
    }

    async payByWallet() {
        if (this.isSubmitting) {
            return;
        }

        this.isSubmitting = true;

        const invoices: InvoicePaymentInvoice[] = this.collectPaymentInvoices();
        const walletType = <PaymentMethodWallet>this.paymentConfig.payment_method_type;
        const {response: intentResponse, errorCode, metadata} = await firstValueFrom(
            this.invoicesService.makePayment({
                invoices,
                verification_code: null,
                payment_method_type: walletType,
                payment_method_id: null,
                return_url: null,
                cancel_url: null,
            })
        );

        if (errorCode) {
            this.isSubmitting = false;
            this.showPaymentError(errorCode, metadata);
            return;
        }

        if (intentResponse.payment_complete) {
            this.isSubmitting = false;
            this.showPaymentSuccess();
            return;
        }

        const paymentIntent = intentResponse.payment_intent;

        const {paymentRequest} = await this.stripeService.getMobileWalletPaymentRequest({
            amount: paymentIntent.amount,
            currency: paymentIntent.currency,
            label: 'Total',
        });

        if (!paymentRequest) {
            this.isSubmitting = false;
            this.showPaymentError();
            return;
        }

        paymentRequest.on('paymentmethod', async (e) => {
            const confirmResponse = await this.stripe.confirmCardPayment(paymentIntent.client_secret, {
                payment_method: e.paymentMethod.id,
                setup_future_usage: 'off_session'
            }, {
                handleActions: false
            });

            if (confirmResponse.error) {
                e.complete('fail');
                this.isSubmitting = false;
                const error = this.stripeService.localizeStripeError(confirmResponse.error);
                this.showResultPopup(false, error.key, error.data);
                return;
            }

            e.complete('success');

            let isOk = true;

            if (confirmResponse.paymentIntent.status === 'requires_action') {
                const confirmResult = await this.stripe.confirmCardPayment(paymentIntent.client_secret);

                if (confirmResult.error) {
                    console.warn('Failed to auth 3D secure:', confirmResult.error);

                    if (confirmResponse.error.code === 'card_declined') {
                        this.isSubmitting = false;
                        const error = this.stripeService.localizeStripeError(confirmResult.error);
                        this.showResultPopup(false, error.key, error.data);
                        return;
                    }

                    isOk = false;
                }
            }

            if (isOk) {
                // tested in GPay walletName is 'googlePay' which is consistent with what server expects
                const walletName = this.paymentService.transformPaymentMethodName(e.paymentMethod.card.wallet.type);
                const paymentMethodId = e.paymentMethod.id;
                if (walletName && paymentMethodId) {
                    await firstValueFrom(this.paymentService.setNewPaymentMethod({
                        payment_method_type: walletName,
                        payment_method_id: paymentMethodId
                    })).catch(() => null);
                }
                await this.paymentService.completePaymentIntent(intentResponse.transaction_id).toPromise().catch(() => false);
            }

            this.isSubmitting = false;

            if (isOk) {
                this.showPaymentSuccess();
            } else {
                this.showPaymentError();
            }
        });

        paymentRequest.on('cancel', () => {
            this.isSubmitting = false;
            this.showPaymentError();
        });

        if (this.stripeService.isSyncPaymentRequest()) {
            this.onShowWalletPaymentConfirmPopup(paymentRequest, paymentIntent, walletType);
        } else {
            paymentRequest.show();
        }
    }

    onShowWalletPaymentConfirmPopup(paymentRequest: any, paymentIntent: any, walletType: PaymentMethodWallet) {
        this.isSubmitting = false;
        this.walletPaymentAttrs = {
            amountFormatted: this.currencyService.format(paymentIntent.amount, paymentIntent.currency),
            wallet: this.stripeService.getWalletName(walletType),
            paymentRequest
        };
        this.activePopup = 'wallet-payment-confirm';
    }

    onCloseWalletPaymentConfirmPopup(isConfirmed: boolean) {
        this.isSubmitting = isConfirmed;

        if (isConfirmed) {
            this.walletPaymentAttrs.paymentRequest.show();
        } else {
            this.paymentCancel.emit();
            this.activePopup = null;
            this.walletPaymentAttrs = null;
        }

        this.resultMessageKey = null;
        this.resultMessageData = null;
        this.paidInvoiceIds = null;
        this.isPaymentResultOk = false;
    }

    checkLimits(): boolean {
        if (this.totalAmount <= 0) {
            return true;
        }

        if (this.totalAmount < this.paymentConfig.min_payment_amount) {
            this.showResultPopup(false, 'invoices.invoice_payment.payment_error_min_limit');
            return false;
        } else if (this.totalAmount > this.paymentConfig.max_payment_amount) {
            this.showResultPopup(false, 'invoices.invoice_payment.payment_error_max_limit');
            return false;
        }

        return true;
    }

    async showResultPopup(isOk: boolean, messageKey: string, messageData: any = null, isSubscriptionError: boolean = false) {
        if (this.paymentModel === 'FLEET') {
            const [{accountStatus}, invoicesResponse] = await Promise.all([
                this.userService.getAccountUserData(this.userService.getUserData().auth.token),
                this.invoicesService.fetchInvoices().toPromise()
            ]);

            if (isOk && this.accountStatus === 'ACCOUNT_DEBT_LOCK' && (accountStatus === 'ACTIVE' || !invoicesResponse.invoices.length)) {
                messageKey = 'invoices.invoice_payment.payment_success_debt_unlock';
            }

            this.accountStatus = accountStatus;
        }

        this.isPaymentResultOk = isOk;
        this.resultMessageKey = messageKey;

        if (!messageData) {
            messageData = this.getSuccessMessageData();
        }

        this.resultMessageData = messageData;
        if (isSubscriptionError) {
            this.activePopup = 'invoice-payment-result-402';
        } else {
            this.activePopup = 'invoice-payment-result';
        }
    }

    private getSuccessMessageData() {
        const {disputedInvoices, disputedAmount} = this.invoiceItems.reduce((acc, invoiceItem: InvoiceItemUIModel) => {
            invoiceItem.licensePlates.forEach((licensePlate: LicensePlate) => {
                licensePlate.transactionItems.forEach((transactionItem: TransactionItem) => {
                    if (transactionItem.disputeReason !== 'NONE') {
                        if (!acc.disputedInvoices.includes(invoiceItem.name)) {
                            acc.disputedInvoices.push(invoiceItem.name);
                        }

                        acc.disputedAmount += transactionItem.amount;
                    }
                });
            });

            return acc;
        }, {
            disputedInvoices: [],
            disputedAmount: 0
        });

        this.hasDisputed = disputedInvoices.length > 0;

        return {
            invoices: this.invoiceItems.map(item => `<strong>${item.name}</strong>`).join(', '),
            amount: this.currencyService.format(this.totalAmount, 'usd'),
            date: this.datetimeService.format(Date.now(), 'display.date'),
            disputedInvoices: disputedInvoices.map(item => `<strong>${item}</strong>`).join(', '),
            disputedAmount: this.currencyService.format(disputedAmount, 'usd'),
        };
    }

    onHideResultPopup(changePaymentMethod: boolean) {
        if (this.isPaymentResultOk) {
            this.paymentSuccess.emit(this.paidInvoiceIds || []);
            this.activePopup = null;
        } else {
            if (changePaymentMethod) {
                this.showPaymentMethodPopup('edit');
            } else {
                this.paymentCancel.emit();
                this.activePopup = null;
            }
        }

        this.walletPaymentAttrs = null;
        this.resultMessageKey = null;
        this.resultMessageData = null;
        this.paidInvoiceIds = null;
        this.isPaymentResultOk = false;
    }

    // ------------------------------------------------------------------------------------

    showZipPopup() {
        this.resetZipPopup();
        this.activePopup = 'zip';
    }

    hideZipPopup() {
        this.resetZipPopup();
        this.activePopup = null;
    }

    onCloseZipPopup() {
        this.hideZipPopup();
        this.paymentCancel.emit();
    }

    validateZipPopup() {
        this.isZipPopupValid = (this.zipCode || '').trim().length >= 4;
    }

    resetZipPopup() {
        this.zipCode = '';
        this.validateZipPopup();
        this.hideIncorrectZip();
    }

    showIncorrectZip() {
        this.isIncorrectZipVisible = true;
    }

    hideIncorrectZip() {
        this.isIncorrectZipVisible = false;
    }

    onSubmitZipPopup() {
        if (!this.isZipPopupValid || this.isSubmitting) {
            return;
        }

        this.hideIncorrectZip();
        this.makeCarrierPaymentRequest();
    }

    // ------------------------------------------------------------------------------------

    collectPaymentInvoices(): InvoicePaymentInvoice[] {
        return this.invoiceItems.map((invoiceItem: InvoiceItemUIModel) => {
            const items: InvoicePaymentTransaction[] = [];

            invoiceItem.licensePlates.forEach((licensePlate: LicensePlate) => {
                licensePlate.transactionItems.forEach((transactionItem: TransactionItem) => {
                    items.push({
                        item_id: transactionItem.id,
                        approved: transactionItem.disputeReason === 'NONE',
                        dispute_type: transactionItem.disputeReason === 'NONE' ? null : transactionItem.disputeReason
                    });
                });
            });

            return {
                invoice_id: invoiceItem.id,
                items
            };
        });
    }

    getZipCode(): null | string {
        return (
            this.paymentConfig &&
            this.paymentConfig.payment_method_type === 'DCB' &&
            this.paymentConfig.payment_verification_required &&
            (this.zipCode || '').trim() ||
            null
        );
    }

    showPaymentError(errorCode: number = DEFAULT_INVOICES_PAYMENT_ERROR_CODE, metaData: any = null) {
        const defaultMessageKey = `invoices.invoice_payment.payment_error_${DEFAULT_INVOICES_PAYMENT_ERROR_CODE}`;
        const licensePlatesOverLimit = metaData?.license_plates_over_limit || 0;

        switch (errorCode) {
            case 300:
            case 301:
            case 302:
            case 303:
            case 308:
            case 309:
            case 312:
                if (this.activePopup === 'zip') {
                    this.hideZipPopup();
                }
                this.showResultPopup(false, `invoices.invoice_payment.payment_error_${errorCode}`);
                return;
            case 304:
                if (this.activePopup === 'zip') {
                    this.showIncorrectZip();
                } else {
                    this.showResultPopup(false, defaultMessageKey);
                }
                return;
            case 402:
                this.showResultPopup(false, 'invoices.invoice_payment.payment_error_402', {
                    licensePlatesOverLimit
                }, true);
                return;
        }

        this.showResultPopup(false, defaultMessageKey);
    }

    showPaymentSuccess() {
        this.paidInvoiceIds = this.invoiceItems.map(item => item.id);

        if (this.activePopup === 'zip') {
            this.hideZipPopup();
        }

        // hack-huyak
        this.getSuccessMessageData();

        if (this.paymentModel === 'FLEET' && this.hasDisputed) {
            this.showResultPopup(true, 'invoices.invoice_payment.payment_success_fleet_has_disputed');
        } else {
            this.showResultPopup(true, 'invoices.invoice_payment.payment_success');
        }
    }

    // ------------------------------------------------------------------------------------

    __print(...args) {
        console.log(...args);
    }

    public goToSubscriptionManagePage() {
        this.activePopup = null;
        this.paymentCancel.emit();
        this.router.navigateByUrl('/dashboard/profile/subscription').then(r => console.log(r));
    }

    private enableAutoPayment() {
        this.autoPaymentService.enableAutopayment().subscribe({
            next: () => {
                this.toastService.create({
                    message: ['invoices_auto_payment.auto_payment_enabled'],
                    timeout: 1000
                });
            },
            error: () => {
                this.toastService.create({
                    message: ['invoices_auto_payment.auto_payment_enable_error'],
                    timeout: 1000
                });
            }
        });
    }
}
