import {
    ChangeDetectionStrategy,
    Component, NgZone,
    OnDestroy,
    OnInit,
    Renderer2,
    ViewChild,
    ViewEncapsulation
} from '@angular/core';
import {Router} from '@angular/router';
import {TitleService} from '../../../services/title.service';
import {DeviceService, ViewportBreakpoint} from '../../../services/device.service';
import {Subscription, zip} from 'rxjs';
import {AccountPaymentModel, UserService} from '../../../services/user.service';
import {DashboardService} from '../../../services/dashboard.service';
import {ConfirmBoxComponent} from '../_widgets/popup/confirm-box/confirm-box.component';
import {
    DEFAULT_INVOICES_PAYMENT_ERROR_CODE, DisputeType,
    InvoiceItem,
    InvoicePaymentInvoice, InvoicePaymentRequestData, InvoicePaymentResponseWithError,
    InvoicePaymentTransaction, InvoicesService, LicensePlate,
    TransactionItem
} from '../../../services/invoices.service';
import {
    MakePaymentByEmailResponse,
    PayByMailData,
    PaymentConfig,
    PaymentService
} from '../../../services/payment.service';
import {
    LicensePlateItem,
    LicensePlatesService, PendingLPN,
    PendingLPNResponse,
    PendingLPNsInvoiceResponse
} from '../../../services/license-plates.service';
import {InvoicePaymentComponent} from './invoices/invoice-payment/invoice-payment.component';
import {ToastService} from '../../../services/toast.service';
import {defer} from '../../../lib/utils';
import {CurrencyPipe} from '../../../pipes/currency.pipe';
import {CurrencyService} from '../../../services/currency.service';
import {PaymentMethodDoneEvent, PaymentMethodPopupMode} from './payment-method/payment-method.component';
import {
    PaymentMethodWallet,
    StripeService
} from '../../../services/stripe.service';
import {TidioService} from '../../../services/tidio.service';
import {Base64Service} from '../../../services/base64.service';
import {Location} from '@angular/common';
import {cloneDeep} from 'lodash-es';
import {BraintreeService} from '../../../services/braintree.service';
import * as braintree from 'braintree-web';
import {DebugService} from '../../../services/debug.service';

interface WelcomeMessageData {
    licensePlates : string;
    hoursToPay : number;
    invoice : string;
    amount : string;
}

type ActivePaymentPopup = null | 'payment-method' | 'payment' | 'welcome' | 'fleet-lpn' | 'fleet-lpn-zip' | 'fleet-wallet-payment-confirm' | 'account-debt-lock';

type PaymentSubmittingBy = null | 'yes' | 'no';

@Component({
    selector: 'dashboard',
    templateUrl: './dashboard.component.html',
    styleUrls: [ './dashboard.component.scss' ],
    changeDetection: ChangeDetectionStrategy.Default,
    encapsulation: ViewEncapsulation.None,
    host: {
        'class': 'dashboard'
    }
})
export class DashboardComponent implements OnInit, OnDestroy {
    viewportBreakpoint : ViewportBreakpoint;

    subs : Subscription[] = [];

    readonly sidebarScrollAreaMarginRight : number = -17;

    payByMailConfirmMessageKey : string;

    welcomeMessageKey : string;

    welcomeMessageData : WelcomeMessageData = {
        licensePlates: '',
        hoursToPay: 47,
        invoice: '',
        amount: '',
    };

    @ViewChild('paymentComponent', { read: InvoicePaymentComponent })
    paymentComponent : InvoicePaymentComponent;

    pbmData : PayByMailData;

    isPaymentPopupValid : boolean = false;

    paymentSubmittingBy : PaymentSubmittingBy = null;

    isPaymentZipRequired : boolean = false;

    zipCode : string = '';

    activePaymentPopup : ActivePaymentPopup = null;

    paymentConfig : PaymentConfig = null;

    stripe : any;

    walletPaymentAttrs : {
        paymentRequest : any;
    } = null;

    paymentModel : AccountPaymentModel = null;

    pendingLPNs : PendingLPNResponse = null;

    pendingLPNsActivity : { [ id : string ] : boolean } = null;

    activePendingLPNsCount : number = 0;

    activePendingLPNsTotal : number = 0;

    pendingLPNsInvoice : PendingLPNsInvoiceResponse = null;

    isConfirmingFleet : boolean = false;

    canSubmitOneTimePayment : boolean = false;

    isFleetZipSubmitting : boolean = false;

    isFleetZipValid : boolean = false;

    isFleetWalletSubmitting : boolean = false;

    walletFleetPaymentAttrs : {
        amountFormatted : string;
        wallet : string;
        paymentRequest : any;
    } = null;

    paymentMethodPopupMode : PaymentMethodPopupMode = 'setup';

    constructor (
        private zone : NgZone,
        private renderer : Renderer2,
        private router : Router,
        private location : Location,
        private titleService : TitleService,
        private deviceService : DeviceService,
        private userService : UserService,
        private dashboardService : DashboardService,
        private paymentService : PaymentService,
        private stripeService : StripeService,
        private licensePlatesService : LicensePlatesService,
        private toastService : ToastService,
        private currencyService : CurrencyService,
        private tidioService : TidioService,
        private base64Service : Base64Service,
        private invoicesService : InvoicesService,
        private braintreeService : BraintreeService,
        private debugService : DebugService,
    ) {
        window.scroll(0, 0);

        this.sidebarScrollAreaMarginRight = -1 * this.deviceService.getScrollbarWidth();
        this.paymentModel = this.userService.getUserData().account.paymentModel;

        this.viewportBreakpoint = this.deviceService.viewportBreakpoint;
        this.subs.push(this.deviceService.onResize.subscribe((message) => {
            if (message.breakpointChange) {
                this.viewportBreakpoint = message.breakpointChange.current;
            }
        }));

        this.debugService.register('genInvoices', async (phone? : string) => {
            await this.userService.generateInvoices(phone).toPromise().catch(() => null);
        }, { help: 'Generate invoices for fleet model' });

        this.debugService.register('lockByPhone', async (phone : string, status : string = 'ACCOUNT_DEBT_LOCK') => {
            await this.userService.lockAccount(phone, status).toPromise().catch(() => null);
        }, { help: 'Lock account' });

        this.debugService.register('getPinForAcc', async (phone : string) => {
            this.userService.getTestAccountPin(phone).subscribe((pin: string) => {
                console.warn(`Test account: ${ phone } / ${ pin }`);
            });
        }, { help: 'Get PIN' });
    }

    ngOnInit () {
        this.titleService.setTitle('dashboard.page_title');
        this.dashboardService.setDashboardState(true);
        this.tidioService.changeVisibility(true);

        const accountStatus = this.userService.getUserData().account.accountStatus;

        if (accountStatus === 'ACCOUNT_DEBT_LOCK') {
            this.activePaymentPopup = 'account-debt-lock';
        } else {
            this.executeNewUserPipeline();
        }
    }

    ngOnDestroy () : void {
        this.subs.forEach(sub => sub.unsubscribe());
        this.dashboardService.setDashboardState(false);
        this.tidioService.changeVisibility(false);
    }

    async executeNewUserPipeline () {
        const currentUrl = new URL(window.location.href);
        const action = currentUrl.searchParams.get('action');

        if (action) {
            switch (action) {
                case 'pbm_paypal_payment_complete':
                case 'pbm_paypal_payment_cancel': {
                    const result = this.decodeUrlToJson(currentUrl.searchParams.get('pbm_paypal_payment_result'));

                    if (result) {
                        this.pbmData = result.pbmData;
                        this.welcomeMessageData = result.messageData;

                        if (action === 'pbm_paypal_payment_cancel') {
                            await this.declinePBM(this.pbmData, 'paypal payment canceled or failed');
                        }

                        this.showWelcomeMessage(result.messageKey);

                        const transactionId = currentUrl.searchParams.get('transaction_id');

                        if (transactionId && action === 'pbm_paypal_payment_complete') {
                            this.paymentService.completePaymentIntent(transactionId).toPromise().catch(() => false);
                        }
                    }

                    this.location.replaceState('/dashboard/invoices');
                    break;
                }
                case 'fleet_lpn_ppp_complete':
                case 'fleet_lpn_ppp_cancel': {
                    const result = this.decodeUrlToJson(currentUrl.searchParams.get('fleet_lpn_ppp_result'));

                    if (result) {
                        const transactionId = currentUrl.searchParams.get('transaction_id');

                        if (transactionId && action === 'fleet_lpn_ppp_complete') {
                            await this.paymentService.completePaymentIntent(transactionId).toPromise().catch(() => false);
                        }

                        this.welcomeMessageData = result.messageData;
                        this.showFleetResultMessage(result.messageKey);
                    }

                    this.location.replaceState('/dashboard/invoices');
                    break;
                }
            }

        } else if (this.userService.isNewUser() && [
            'veh_pbm_paypal_payment_complete',
            'veh_pbm_paypal_payment_cancel',
            'veh_fleet_lpn_ppp_complete',
            'veh_fleet_lpn_ppp_cancel',
        ].includes(action) === false) {
            const paymentConfig = await this.paymentService.fetchPaymentConfig().toPromise().catch(() => null);

            if (this.paymentModel === 'POSTPAID' && (!paymentConfig || paymentConfig.setup_complete)) {
                this.checkAndExecutePBM();
            } else if (this.paymentModel === 'FLEET' && paymentConfig && paymentConfig.setup_complete) {
                this.payFleet();
            } else {
                this.showPaymentMethodPopup();
            }
        }
    }

    async checkAndExecutePBM () : Promise<boolean> {
        const pbmData : PayByMailData = await this.paymentService.fetchPayByMail().toPromise().catch(() => null);

        if (this.userService.isRegNPay() || pbmData && pbmData.pbm_id) {
            this.executePBM(pbmData);
            return true;
        }

        return false;
    }

    showPaymentMethodPopup () {
        this.activePaymentPopup = 'payment-method';
    }

    hidePaymentMethodPopup () {
        this.activePaymentPopup = null;
    }

    async onPaymentMethodSelected (event : PaymentMethodDoneEvent) {
        if (this.paymentMethodPopupMode === 'setup') {
            if (this.paymentModel === 'POSTPAID') {
                const isPBMExecuted = await this.checkAndExecutePBM();

                if (!isPBMExecuted) {
                    this.hidePaymentMethodPopup();
                }
            } else if (this.paymentModel === 'FLEET') {
                if (event.isOk && (await this.paymentService.checkCurrentPaymentMethod(event.paymentConfig))) {
                    // this.hidePaymentMethodPopup();
                    this.payFleet();
                } else {
                    this.hidePaymentMethodPopup();
                    defer(() => this.showPaymentMethodPopup());
                }
            }
        } else if (this.paymentMethodPopupMode === 'change') {
            if (event.isOk && (await this.paymentService.checkCurrentPaymentMethod(event.paymentConfig))) {
                this.paymentConfig = event.paymentConfig;
                this.payFleet();
            } else {
                this.onShowChangePaymentMethodPopup();
            }
        }
    }

    async executePBM (pbmData : PayByMailData) {
        const response : [ any, any, PaymentConfig, number ] = await Promise.all([
            this.stripeService.getStripeInstance(),
            this.braintreeService.createClient(),
            this.paymentService.fetchPaymentConfig().toPromise(),
            this.paymentService.fetchHoursToPay().toPromise(),
        ]).catch(() => null);

        if (!pbmData || pbmData.status !== 'OK' || !pbmData.pbm_id || !response) {
            this.showWelcomeMessage('dashboard.welcome.message_default');
            console.warn('Something wrong with PBM init');
            return;
        }

        const [ stripe, btClient, paymentConfig, hoursToPay ] = response;

        console.log(btClient);

        this.stripe = stripe;
        this.welcomeMessageData.hoursToPay = hoursToPay;

        const isPaymentMethodOk = await this.paymentService.checkCurrentPaymentMethod(paymentConfig, null, {
            amount: pbmData.amount,
            currency: pbmData.currency
        }).catch(() => false);

        if (!isPaymentMethodOk) {
            await this.declinePBM(pbmData, 'something wrong with payment method');
            this.showWelcomeMessage('dashboard.welcome.message_205');
            return;
        }

        const isAmountLessThanMin = pbmData.amount < paymentConfig.min_payment_amount;
        const isAmountGreaterThanMax = pbmData.amount > paymentConfig.max_payment_amount;

        if (isAmountLessThanMin || isAmountGreaterThanMax) {
            await this.declinePBM(pbmData, 'limits');
            this.showWelcomeMessage('dashboard.welcome.message_205');
            return;
        }

        this.paymentConfig = paymentConfig;
        this.pbmData = pbmData;
        this.isPaymentZipRequired = paymentConfig.payment_verification_required;

        this.payByMailConfirmMessageKey = (
            this.paymentConfig.payment_method_type === 'DCB' && this.isPaymentZipRequired ?
            'dashboard.payment.reg_n_pay_message_has_zip' :
            'dashboard.payment.reg_n_pay_message_no_zip'
        );

        this.welcomeMessageData.invoice = this.pbmData.name;
        this.welcomeMessageData.amount = this.currencyService.format(this.pbmData.amount, this.pbmData.currency);

        if (paymentConfig.payment_method_type === 'GOOGLEPAY' || paymentConfig.payment_method_type === 'APPLEPAY') {
            this.prepareWalletPayment();
        } else {
            this.showPaymentPopup();
        }
    }

    async sendPaymentRequest (options : {
        pbmId : string,
        makePayment : boolean,
        verificationCode? : string,
        returnUrl? : string,
        cancelUrl? : string,
    }) : Promise<MakePaymentByEmailResponse> {
        return this.paymentService.makePaymentByEmail(options.pbmId, {
            make_payment: options.makePayment,
            verification_code: options.verificationCode || null,
            payment_method_type: this.paymentConfig && this.paymentConfig.payment_method_type || null,
            payment_method_id: this.paymentConfig && this.paymentConfig.payment_method_id || null,
            return_url: options.returnUrl || null,
            cancel_url: options.cancelUrl || null,
        })
            .toPromise()
            .then(response => {
                console.warn(response);
                if (response.status !== 'OK' && !response.errorCode) {
                    response.errorCode = 205;
                }

                return response;
            })
            .catch((errorCode : number) => {
                console.warn(errorCode);
                return {
                    status: 'ERROR',
                    errorCode
                };
            });
    }

    async declinePBM (payByMailData : PayByMailData, reason : string = null) : Promise<void> {
        const response = await this.sendPaymentRequest({
            pbmId: payByMailData.pbm_id,
            makePayment: false,
        });

        if (response.status === 'OK') {
            console.warn(`PBM rejected (reason: ${ reason })`);
        } else {
            console.warn(`PBM must be rejected (reason: ${ reason }) but an error occurred`)
        }
    }

    showWelcomeError (errorCode : number) {
        switch (errorCode) {
            case 203:
            case 205:
            case 307:
                this.showWelcomeMessage(`dashboard.welcome.message_${ errorCode }`);
                return;
        }

        this.showWelcomeMessage('dashboard.welcome.message_205');
    }

    showWelcomeMessage (welcomeMessageKey : string) {
        // call fetchLicensePlates after makePaymentByEmail
        this.licensePlatesService.fetchLicensePlates()
            .toPromise()
            .catch(() => [])
            .then((licensePlates : LicensePlateItem[]) => {
                licensePlates = (licensePlates || []).sort((a, b) => {
                    if (a.registered > b.registered) {
                        return -1;
                    } else if (a.registered < b.registered) {
                        return 1;
                    } else {
                        return 0;
                    }
                });

                const lp = licensePlates[0] || null;

                if (lp) {
                    this.welcomeMessageData.licensePlates = `<strong>${ lp.lps }&nbsp;${ lp.lpn }</strong>`;
                } else {
                    this.welcomeMessageData.licensePlates = null;
                }

                this.welcomeMessageKey = welcomeMessageKey;
                this.activePaymentPopup = 'welcome';
            });
    }

    hideWelcomeMessage () {
        this.activePaymentPopup = null;
    }

    // -----------------------------------

    showPaymentPopup () {
        this.resetPaymentPopup();
        this.activePaymentPopup = 'payment';
    }

    async onSubmitPayment (makePayment : boolean) {
        if (this.paymentSubmittingBy) {
            return;
        }

        this.paymentSubmittingBy = makePayment ? 'yes' : 'no';

        if (!makePayment) {
            await this.declinePBM(this.pbmData, 'declined by user');
            this.showWelcomeMessage('dashboard.welcome.message_declined');
            return;
        }

        switch (this.paymentConfig.payment_method_type) {
            case 'DCB':
                this.payByCarrier();
                break;
            case 'PAYPAL':
                this.payByPayPal();
                break;
            case 'DEBIT_CARD':
            case 'CREDIT_CARD':
                this.payByCard();
                break;
            case 'GOOGLEPAY':
            case 'APPLEPAY':
                this.walletPaymentAttrs.paymentRequest.show();
                this.walletPaymentAttrs = null;
                break;
            case 'VENMO':
                this.payByVenmo();
                break;
        }
    }

    encodeJsonToUrl (data : any) : string {
        return encodeURIComponent(this.base64Service.encode(JSON.stringify(data)));
    }

    decodeUrlToJson (data : any) : any {
        try {
            return JSON.parse(this.base64Service.decode(decodeURIComponent(data)));
        } catch (e) {
            return null;
        }
    }

    async payByPayPal () {
        const successResultData = this.encodeJsonToUrl({
            messageKey: 'dashboard.welcome.message_approved',
            messageData: this.welcomeMessageData,
            pbmData: this.pbmData
        });

        const cancelResultData = this.encodeJsonToUrl({
            messageKey: 'dashboard.welcome.message_205',
            messageData: this.welcomeMessageData,
            pbmData: this.pbmData
        });

        const response = await this.sendPaymentRequest({
            pbmId: this.pbmData.pbm_id,
            makePayment: true,
            returnUrl: `/dashboard/invoices?action=pbm_paypal_payment_complete&pbm_paypal_payment_result=${ successResultData }`,
            cancelUrl: `/dashboard/invoices?action=pbm_paypal_payment_cancel&pbm_paypal_payment_result=${ cancelResultData }`,
        });

        const approveUrl = response?.payment_intent?.approve_payment_url;

        if (!response || response.status !== 'OK' || !approveUrl) {
            await this.declinePBM(this.pbmData, 'fetch paypal order error');
            this.showWelcomeError(response && response.errorCode || 205);
        } else {
            window.location.assign(approveUrl);
        }
    }

    async payByCarrier () {
        const zipCode : string = this.isPaymentZipRequired ? (this.zipCode || '').trim() : null;
        const intentResponse = await this.sendPaymentRequest({
            pbmId: this.pbmData.pbm_id,
            makePayment: true,
            verificationCode: zipCode,
        });

        console.warn(intentResponse);

        if (intentResponse.status === 'OK') {
            this.showWelcomeMessage('dashboard.welcome.message_approved');
        } else {
            this.showWelcomeError(intentResponse && intentResponse.errorCode || 205);
        }
    }

    async payByVenmo () {
        const response = await this.sendPaymentRequest({
            pbmId: this.pbmData.pbm_id,
            makePayment: true,
        });

        if (!response || response.status !== 'OK') {
            await this.declinePBM(this.pbmData, 'failed to pay pbm with venmo');
            this.showWelcomeError(response && response.errorCode || 205);
            return;
        }

        this.showWelcomeMessage('dashboard.welcome.message_approved');
    }

    async payByCard () {
        const intentResponse = await this.sendPaymentRequest({
            pbmId: this.pbmData.pbm_id,
            makePayment: true,
        });

        if (!intentResponse || intentResponse.status !== 'OK') {
            await this.declinePBM(this.pbmData, 'fetch payment intent error');
            this.showWelcomeError(intentResponse && intentResponse.errorCode || 205);
            return;
        }

        // Payment done w/o 3D secure
        if (intentResponse.payment_complete) {
            this.showWelcomeMessage('dashboard.welcome.message_approved');
            return;
        }

        const paymentIntent = intentResponse.payment_intent;

        // There is payment intent with status !== 'succeeded'
        // 3D secure required
        const response = await this.stripe.confirmCardPayment(paymentIntent.client_secret).catch(() => null);

        if (!response || response.error) {
            console.warn(response);
            await this.declinePBM(this.pbmData, '3D Secure failed');
            this.showWelcomeMessage('dashboard.welcome.message_205');
            return;
        }

        const isOk = await this.paymentService.completePaymentIntent(intentResponse.transaction_id).toPromise().catch(() => false);

        if (isOk) {
            this.showWelcomeMessage('dashboard.welcome.message_approved');
            return;
        }

        // Unexpected state or 3D secure fail
        this.showWelcomeMessage('dashboard.welcome.message_205');
    }

    async prepareWalletPayment () {
        const { paymentRequest } = await this.stripeService.getWalletPaymentRequest({
            amount: this.pbmData.amount,
            currency: this.pbmData.currency,
            label: 'Total',
        });

        paymentRequest.on('paymentmethod', async (e) => {
            // [POST /pay-by-mail/<pbm_id>]
            const intentResponse = await this.sendPaymentRequest({
                pbmId: this.pbmData.pbm_id,
                makePayment: true,
            });

            if (!intentResponse || intentResponse.status !== 'OK' || intentResponse.errorCode || !intentResponse.payment_intent) {
                e.complete('fail');
                await this.declinePBM(this.pbmData, 'fetch payment intent error');
                this.showWelcomeError(intentResponse && intentResponse.errorCode || 205);
                return;
            }

            const paymentIntent = intentResponse.payment_intent;
            const confirmResponse = await this.stripe.confirmCardPayment(paymentIntent.client_secret, {
                payment_method: e.paymentMethod.id
            }, {
                handleActions: false
            });

            if (confirmResponse.error) {
                e.complete('fail');
                await this.declinePBM(this.pbmData, 'fail to pay with wallet');
                this.showWelcomeMessage('dashboard.welcome.message_205');
                return;
            }

            e.complete('success');
            // ------------------------
            // WALLET UI IS HIDDEN HERE
            // ------------------------

            let isOk = true;

            if (confirmResponse.paymentIntent.status === 'requires_action') {
                const confirmResult = await this.stripe.confirmCardPayment(paymentIntent.client_secret);

                if (confirmResult.error) {
                    console.warn('Failed to auth 3D secure:', confirmResult.error);
                    isOk = false;
                }
            }

            if (isOk) {
                await this.paymentService.completePaymentIntent(intentResponse.transaction_id).toPromise().catch(() => false);
            }

            if (isOk) {
                this.showWelcomeMessage('dashboard.welcome.message_approved');
            } else {
                this.showWelcomeMessage('dashboard.welcome.message_205');
            }
        });

        paymentRequest.on('cancel', async (e) => {
            await this.declinePBM(this.pbmData, 'wallet payment canceled');
            this.showWelcomeMessage('dashboard.welcome.message_205');
            console.log('cancel', e);
        });

        this.walletPaymentAttrs = { paymentRequest };
        this.showPaymentPopup();
    }

    validatePaymentPopup () {
        this.isPaymentPopupValid = (
            this.paymentConfig.payment_method_type !== 'DCB' ||
            !this.isPaymentZipRequired ||
            (this.zipCode || '').trim().length >= 4
        );
    }

    resetPaymentPopup () {
        this.zipCode = '';
        this.paymentSubmittingBy = null;
        this.validatePaymentPopup();
    }

    // -------------------------------------

    async payFleet () {
        this.pendingLPNs = await this.licensePlatesService.fetchPendingLPNs().toPromise().catch(() => null);

        if ((this.pendingLPNs?.plates || []).length > 0) {
            // TODO: Delete
            /*
            this.pendingLPNs.fee = 0;

            for (let i = 0; i < 4; i++) {
                const item = cloneDeep(this.pendingLPNs.plates[0]);
                item.id = String(Math.random());
                this.pendingLPNs.plates.push(item);
            }
            */
            // --------------

            const response : [ any, number ] = await Promise.all([
                this.stripeService.getStripeInstance(),
                this.paymentService.fetchHoursToPay().toPromise(),
            ]).catch(() => null);

            if (!response) {
                console.warn('Failed to get Stripe or hoursToPay');
                return;
            }

            const [ stripe, hoursToPay ] = response;

            this.stripe = stripe;
            this.welcomeMessageData.hoursToPay = hoursToPay;

            this.pendingLPNsActivity = this.pendingLPNs.plates.reduce((acc, plate) => {
                acc[plate.id] = true;
                return acc;
            }, {});
            this.recountActivePendingLPNs();
            this.activePaymentPopup = 'fleet-lpn';
        } else {
            this.pendingLPNs = null;
            this.activePaymentPopup = null;
        }
    }

    recountActivePendingLPNs () {
        if (this.pendingLPNs) {
            this.activePendingLPNsCount = Object.values(this.pendingLPNsActivity).filter(isActive => isActive).length;
            this.activePendingLPNsTotal = this.pendingLPNs.fee * this.activePendingLPNsCount;
        } else {
            this.activePendingLPNsCount = 0;
            this.activePendingLPNsTotal = 0;
        }

        this.canSubmitOneTimePayment = !!(this.pendingLPNs && (this.pendingLPNs.fee > 0 || this.activePendingLPNsCount > 0));
    }

    async onConfirmFleetPayment () {
        if (this.isConfirmingFleet || !this.pendingLPNs || !this.canSubmitOneTimePayment) {
            return;
        }

        this.isConfirmingFleet = true;

        const [ stripe, paymentConfig, hoursToPay ] = await Promise.all([
            this.stripeService.getStripeInstance(),
            this.paymentService.fetchPaymentConfig().toPromise(),
            this.paymentService.fetchHoursToPay().toPromise()
        ]).catch(() => [ null, null ]);

        if (!stripe || !paymentConfig) {
            this.isConfirmingFleet = false;
            this.pendingLPNs = null;
            this.activePaymentPopup = null;
            return;
        }

        this.stripe = stripe;
        this.paymentConfig = paymentConfig;
        this.welcomeMessageData.hoursToPay = hoursToPay;

        const isZeroFee = this.pendingLPNs.fee <= 0;
        const isPaymentMethodOk = isZeroFee || (await this.paymentService.checkCurrentPaymentMethod(this.paymentConfig, null, {
            amount: this.activePendingLPNsTotal,
            currency: 'USD'
        }).catch(() => false));

        if (!isPaymentMethodOk) {
            this.isConfirmingFleet = false;
            this.pendingLPNs = null;
            this.showPaymentMethodPopup();
            return;
        }

        const acceptedLPNIds : string[] = [];
        const licensePlates : string[] = [];

        this.pendingLPNs.plates.forEach((plate) => {
            if (this.pendingLPNsActivity[plate.id]) {
                acceptedLPNIds.push(plate.id);
                const lpn = [ plate.lps, plate.lpn ].join(' ').trim();
                licensePlates.push(`<strong>${ lpn }</strong>`);
            }
        });

        this.welcomeMessageData.licensePlates = licensePlates.join(', ');

        this.pendingLPNsInvoice = await this.licensePlatesService.acceptPendingLPNs(acceptedLPNIds).toPromise().catch(() => null);

        if (!this.pendingLPNsInvoice || !this.pendingLPNsInvoice.invoice_id || !this.pendingLPNsInvoice.invoice_items) {
            this.isConfirmingFleet = false;
            this.pendingLPNs = null;
            this.showFleetResultMessage('dashboard.fleet.message_declined');
            return;
        }

        if (isZeroFee) {
            const { response: intentResponse } = await this.invoicesService.makePayment({
                invoices: this.getInvoiceForFleetPayment(),
                verification_code: null,
                payment_method_type: this.paymentConfig.payment_method_type,
                payment_method_id: this.paymentConfig.payment_method_id,
                return_url: null,
                cancel_url: null,
            }).toPromise().catch(error => error);

            this.isConfirmingFleet = false;

            if (intentResponse?.payment_complete) {
                this.showFleetResultMessage('dashboard.fleet.message_ok');
            } else {
                this.showFleetResultMessage('dashboard.fleet.message_issues');
            }

            return;
        }

        switch (this.paymentConfig.payment_method_type) {
            case 'DCB':
                if (this.paymentConfig.payment_verification_required) {
                    this.showFleetZipPopup();
                } else {
                    this.submitFleetZipPayment();
                }
                break;
            case 'PAYPAL':
                this.payByPayPalFleet();
                break;
            case 'DEBIT_CARD':
            case 'CREDIT_CARD':
                this.payByCardFleet();
                break;
            case 'GOOGLEPAY':
            case 'APPLEPAY':
                this.payByWalletFleet();
                break;
            case 'VENMO':
                this.payByVenmoFleet();
                break;
        }
    }

    getInvoiceForFleetPayment () : InvoicePaymentInvoice[] {
        return [
            {
                invoice_id: this.pendingLPNsInvoice.invoice_id,
                items: this.pendingLPNsInvoice.invoice_items.map(itemId => ({
                    item_id: itemId,
                    approved: true,
                    dispute_type: null
                }))
            }
        ];
    }

    async payByPayPalFleet () {
        const successResultData = this.encodeJsonToUrl({
            messageKey: 'dashboard.fleet.message_ok',
            messageData: this.welcomeMessageData,
            isOk: true,
        });

        const cancelResultData = this.encodeJsonToUrl({
            messageKey: 'dashboard.fleet.message_issues',
            messageData: this.welcomeMessageData,
            isOk: false,
        });

        const { response, errorCode } = <InvoicePaymentResponseWithError>await this.invoicesService.makePayment({
            invoices: this.getInvoiceForFleetPayment(),
            verification_code: null,
            payment_method_type: this.paymentConfig.payment_method_type,
            payment_method_id: this.paymentConfig.payment_method_id,
            return_url: `/dashboard/invoices?action=fleet_lpn_ppp_complete&fleet_lpn_ppp_result=${ successResultData }`,
            cancel_url: `/dashboard/invoices?action=fleet_lpn_ppp_cancel&fleet_lpn_ppp_result=${ cancelResultData }`,
        }).toPromise().catch(error => error);

        const approveUrl = response?.payment_intent?.approve_payment_url;

        if (errorCode || !approveUrl) {
            // TODO: show_payment_method
            this.isConfirmingFleet = false;
            // this.showFleetResultMessage('dashboard.fleet.message_issues');
            this.onShowChangePaymentMethodPopup();
        } else {
            window.location.assign(approveUrl);
        }
    }

    async payByCardFleet () {
        const { response: intentResponse, errorCode } = await this.invoicesService.makePayment({
            invoices: this.getInvoiceForFleetPayment(),
            verification_code: null,
            payment_method_type: this.paymentConfig.payment_method_type,
            payment_method_id: this.paymentConfig.payment_method_id,
            return_url: null,
            cancel_url: null,
        }).toPromise().catch(error => error);

        if (errorCode) {
            // TODO: show_payment_method
            this.isConfirmingFleet = false;
            // this.showFleetResultMessage('dashboard.fleet.message_issues');
            this.onShowChangePaymentMethodPopup();
            return;
        }

        const paymentIntent = intentResponse.payment_intent;

        if (intentResponse.payment_complete) {
            this.isConfirmingFleet = false;
            this.showFleetResultMessage('dashboard.fleet.message_ok');
            return;
        }

        // Payment incomplete
        // -------------------------------------------------------

        const response = await this.stripe.confirmCardPayment(paymentIntent.client_secret).catch(() => null);

        if (!response) {
            // TODO: show_payment_method
            this.isConfirmingFleet = false;
            // this.showFleetResultMessage('dashboard.fleet.message_issues');
            this.onShowChangePaymentMethodPopup();
            return;
        }

        if (response.error) {
            // TODO: show_payment_method
            this.isConfirmingFleet = false;
            const error = this.stripeService.localizeStripeError(response.error);
            // this.showFleetResultMessage('dashboard.fleet.message_issues');
            this.onShowChangePaymentMethodPopup();
            console.warn('Failed to auth 3D secure:', response, error);
            return;
        }

        const isOkOrError = await this.paymentService.completePaymentIntent(intentResponse.transaction_id).toPromise().catch(errorCode => errorCode);

        this.isConfirmingFleet = false;

        if (isOkOrError === true) {
            this.showFleetResultMessage('dashboard.fleet.message_ok');
        } else {
            // TODO: show_payment_method
            // this.showFleetResultMessage('dashboard.fleet.message_issues');
            this.onShowChangePaymentMethodPopup();
        }
    }

    async payByVenmoFleet () {
        const { response, errorCode } = await this.invoicesService.makePayment({
            invoices: this.getInvoiceForFleetPayment(),
            verification_code: null,
            payment_method_type: this.paymentConfig.payment_method_type,
            payment_method_id: this.paymentConfig.payment_method_id,
            return_url: null,
            cancel_url: null,
        }).toPromise().catch(error => error);

        this.isConfirmingFleet = false;

        // response.payment_complete = false;

        if (!errorCode && response.payment_complete) {
            this.showFleetResultMessage('dashboard.fleet.message_ok');
        } else {
            // TODO: show_payment_method
            // this.showFleetResultMessage('dashboard.fleet.message_issues');
            this.onShowChangePaymentMethodPopup();
        }
    }

    resetFleetZipPopup () {
        this.zipCode = '';
        this.isFleetZipSubmitting = false;
        this.validateFleetZipPopup();
    }

    showFleetZipPopup () {
        this.isConfirmingFleet = false;
        this.activePaymentPopup = 'fleet-lpn-zip';
    }

    validateFleetZipPopup () {
        this.isFleetZipValid = (this.zipCode || '').trim().length >= 4;
    }

    async submitFleetZipPayment () {
        if (!this.isFleetZipValid || this.isFleetZipSubmitting) {
            return;
        }

        this.isFleetZipSubmitting = true;

        const { errorCode } = await this.invoicesService.makePayment({
            invoices: this.getInvoiceForFleetPayment(),
            verification_code: this.paymentConfig.payment_verification_required ? (this.zipCode || '').trim() : null,
            payment_method_type: this.paymentConfig.payment_method_type,
            payment_method_id: this.paymentConfig.payment_method_id,
            return_url: null,
            cancel_url: null,
        }).toPromise().catch(error => error);

        this.isFleetZipSubmitting = false;

        if (!errorCode) {
            this.showFleetResultMessage('dashboard.fleet.message_ok');
        } else {
            this.showFleetResultMessage('dashboard.fleet.message_issues');
        }
    }

    async payByWalletFleet () {
        const walletType = <PaymentMethodWallet>this.paymentConfig.payment_method_type;

        const { response: intentResponse, errorCode } = await this.invoicesService.makePayment({
            invoices: this.getInvoiceForFleetPayment(),
            verification_code: null,
            payment_method_type: walletType,
            payment_method_id: this.paymentConfig.payment_method_id,
            return_url: null,
            cancel_url: null,
        }).toPromise().catch(error => error);

        if (errorCode) {
            // TODO: show_payment_method
            this.isConfirmingFleet = false;
            // this.showFleetResultMessage('dashboard.fleet.message_issues');
            this.onShowChangePaymentMethodPopup();
            return;
        }

        const paymentIntent = intentResponse.payment_intent;

        const { paymentRequest } = await this.stripeService.getWalletPaymentRequest({
            amount: paymentIntent.amount,
            currency: paymentIntent.currency,
            label: 'Total',
        });

        if (!paymentRequest) {
            // TODO: show_payment_method
            this.isConfirmingFleet = false;
            // this.showFleetResultMessage('dashboard.fleet.message_issues');
            this.onShowChangePaymentMethodPopup();
            return;
        }

        paymentRequest.on('paymentmethod', async (e) => {
            const confirmResponse = await this.stripe.confirmCardPayment(paymentIntent.client_secret, {
                payment_method: e.paymentMethod.id
            }, {
                handleActions: false
            });

            if (confirmResponse.error) {
                // TODO: show_payment_method
                e.complete('fail');
                this.isConfirmingFleet = false;
                const error = this.stripeService.localizeStripeError(confirmResponse.error);
                // this.showFleetResultMessage('dashboard.fleet.message_issues');
                this.onShowChangePaymentMethodPopup();
                console.warn('Failed:', error);
                return;
            }

            e.complete('success');

            let isOk = true;

            if (confirmResponse.paymentIntent.status === 'requires_action') {
                const confirmResult = await this.stripe.confirmCardPayment(paymentIntent.client_secret);

                if (confirmResult.error) {
                    console.warn('Failed to auth 3D secure:', confirmResult.error);

                    if (confirmResponse.error.code === 'card_declined') {
                        // TODO: show_payment_method
                        this.isConfirmingFleet = false;
                        const error = this.stripeService.localizeStripeError(confirmResult.error);
                        this.onShowChangePaymentMethodPopup();
                        // this.showFleetResultMessage('dashboard.fleet.message_issues');
                        console.warn('Failed:', error);
                        return;
                    }

                    isOk = false;
                }
            }

            if (isOk) {
                await this.paymentService.completePaymentIntent(intentResponse.transaction_id).toPromise().catch(() => false);
            }

            this.isConfirmingFleet = false;

            if (isOk) {
                this.showFleetResultMessage('dashboard.fleet.message_ok');
            } else {
                // TODO: show_payment_method
                // this.showFleetResultMessage('dashboard.fleet.message_issues');
                this.onShowChangePaymentMethodPopup();
            }
        });

        paymentRequest.on('cancel', () => {
            // TODO: show_payment_method
            this.isConfirmingFleet = false;
            this.onShowChangePaymentMethodPopup();
            // this.showFleetResultMessage('dashboard.fleet.message_issues');
        });

        if (this.stripeService.isSyncPaymentRequest()) {
            this.onShowWalletPaymentConfirmPopup(paymentRequest, paymentIntent, walletType);
        } else {
            paymentRequest.show();
        }
    }

    onShowWalletPaymentConfirmPopup (paymentRequest : any, paymentIntent : any, walletType : PaymentMethodWallet) {
        this.isConfirmingFleet = false;
        this.isFleetWalletSubmitting = false;

        this.walletFleetPaymentAttrs = {
            amountFormatted: this.currencyService.format(paymentIntent.amount, paymentIntent.currency),
            wallet: this.stripeService.getWalletName(walletType),
            paymentRequest
        };

        this.activePaymentPopup = 'fleet-wallet-payment-confirm';
    }

    onConfirmFleetWalletPayment () {
        this.walletFleetPaymentAttrs.paymentRequest.show();
    }

    showFleetResultMessage (messageKey : string) {
        this.welcomeMessageKey = messageKey;
        this.activePaymentPopup = 'welcome';
    }

    onShowChangePaymentMethodPopup () {
        this.paymentMethodPopupMode = 'change';
        this.activePaymentPopup = 'payment-method';
    }

    onPayDebt () {
        this.activePaymentPopup = null;
        this.router.navigateByUrl('/dashboard/invoices');
    }

    isCoverageVisible () : boolean {
        return true;  // this.userService.getUserData().account.paymentModel !== 'FLEET';
    }
}
