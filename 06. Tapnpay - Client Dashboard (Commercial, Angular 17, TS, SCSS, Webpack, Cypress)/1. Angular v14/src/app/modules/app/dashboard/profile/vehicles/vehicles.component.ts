import {
    ChangeDetectionStrategy,
    Component,
    OnDestroy,
    OnInit,
    Renderer2, ViewChild,
    ViewEncapsulation,
} from '@angular/core';
import {Router} from '@angular/router';
import {animateChild, query, transition, trigger} from '@angular/animations';
import {Subscription} from 'rxjs';
import {TitleService} from '../../../../../services/title.service';
import {DeviceService, ViewportBreakpoint} from '../../../../../services/device.service';
import {
    LicensePlateItem,
    LicensePlatesService,
    PendingLPNResponse, PendingLPNsInvoiceResponse
} from '../../../../../services/license-plates.service';
import {ToastService} from '../../../../../services/toast.service';
import {Base64Service} from '../../../../../services/base64.service';
import {Location} from '@angular/common';
import {
    MakePaymentByEmailResponse,
    PayByMailData,
    PaymentConfig,
    PaymentService
} from '../../../../../services/payment.service';
import {PaymentMethodWallet, StripeService} from '../../../../../services/stripe.service';
import {CurrencyService} from '../../../../../services/currency.service';
import {InvoicePaymentComponent} from '../../invoices/invoice-payment/invoice-payment.component';
import {PaymentMethodDoneEvent} from '../../payment-method/payment-method.component';
import {
    InvoicePaymentInvoice,
    InvoicePaymentResponseWithError,
    InvoicesService
} from '../../../../../services/invoices.service';
import {AccountPaymentModel, UserService} from '../../../../../services/user.service';
import {defer} from '../../../../../lib/utils';

type ListState = 'loading' | 'list' | 'empty' | 'error';
type ActivePopup = 'add' | 'unregister-confirm' | 'payment-result' | 'payment' | 'payment-method' | 'error' | 'fleet-lpn' | 'fleet-lpn-zip' | 'fleet-wallet-payment-confirm';
type PaymentSubmittingBy = null | 'yes' | 'no';

interface ErrorMessage {
    key : string;
    data? : any
}

interface WelcomeMessageData {
    licensePlates : string;
    hoursToPay : number;
    invoice : string;
    amount : string;
}

@Component({
    selector: 'vehicles',
    exportAs: 'vehicles',
    templateUrl: './vehicles.component.html',
    styleUrls: [ './vehicles.component.scss' ],
    changeDetection: ChangeDetectionStrategy.Default,
    encapsulation: ViewEncapsulation.None,
    host: {
        'class': 'vehicles',
        '[@vehiclesHost]': 'true'
    },
    animations: [
        trigger('vehiclesHost', [
            transition(':enter', [
                query('@*', animateChild(), { optional: true }),
            ]),
        ]),
    ]
})
export class VehiclesComponent implements OnInit, OnDestroy {
    viewportBreakpoint : ViewportBreakpoint;

    subs : Subscription[] = [];

    listState : ListState = 'loading';

    licensePlates : LicensePlateItem[];

    isSubmitting : boolean = false;

    lpToUnregister : LicensePlateItem;

    activePopup : null | ActivePopup = null;

    isLpnValid : boolean = false;

    lpn : string = '';

    addPopupError : ErrorMessage = null;

    errorPopupMessage : ErrorMessage = null;

    paymentConfig : PaymentConfig = null;

    stripe : any;

    walletPaymentAttrs : {
        paymentRequest : any;
    } = null;

    paymentSubmittingBy : PaymentSubmittingBy = null;

    isPaymentZipRequired : boolean = false;

    zipCode : string = '';

    payByMailConfirmMessageKey : string;

    paymentResultMessageKey : string;

    paymentResultMessageData : WelcomeMessageData = {
        licensePlates: '',
        hoursToPay: 47,
        invoice: '',
        amount: '',
    };

    @ViewChild('paymentComponent', { read: InvoicePaymentComponent })
    paymentComponent : InvoicePaymentComponent;

    pbmData : PayByMailData;

    isPaymentPopupValid : boolean = false;

    lastLPN : string;

    // --------------------------------------------------------

    paymentModel : AccountPaymentModel = null;

    pendingLPNs : PendingLPNResponse = null;

    pendingLPNsActivity : { [ id : string ] : boolean } = null;

    activePendingLPNsCount : number = 0;

    activePendingLPNsTotal : number = 0;

    pendingLPNsInvoice : PendingLPNsInvoiceResponse = null;

    isConfirmingFleet : boolean = false;

    isFleetZipSubmitting : boolean = false;

    isFleetZipValid : boolean = false;

    isFleetWalletSubmitting : boolean = false;

    walletFleetPaymentAttrs : {
        amountFormatted : string;
        wallet : string;
        paymentRequest : any;
    } = null;

    attemptsToSelectPaymentMethodForFleet : number = 0;

    updateTimeout : any = null;

    constructor (
        private renderer : Renderer2,
        private router : Router,
        private location : Location,
        private titleService : TitleService,
        private deviceService : DeviceService,
        private licensePlatesService : LicensePlatesService,
        private toastService : ToastService,
        private paymentService : PaymentService,
        private stripeService : StripeService,
        private currencyService : CurrencyService,
        private invoicesService : InvoicesService,
        private base64Service : Base64Service,
        private userService : UserService,
    ) {
        window.scroll(0, 0);

        this.paymentModel = this.userService.getUserData().account.paymentModel;

        this.viewportBreakpoint = this.deviceService.viewportBreakpoint;
        this.subs.push(this.deviceService.onResize.subscribe((message) => {
            if (message.breakpointChange) {
                this.viewportBreakpoint = message.breakpointChange.current;
            }
        }));

        this.listState = 'loading';
    }

    async ngOnInit () {
        this.titleService.setTitle('vehicles.page_title');
        await this.init();
    }

    async init () {
        const currentUrl = new URL(window.location.href);
        const action = currentUrl.searchParams.get('action');

        if (action) {
            switch (action) {
                case 'veh_pbm_paypal_payment_complete':
                case 'veh_pbm_paypal_payment_cancel': {
                    this.location.replaceState('/dashboard/profile/vehicles');

                    const result = this.decodeUrlToJson(currentUrl.searchParams.get('veh_pbm_paypal_payment_result'));

                    if (result) {
                        this.pbmData = result.pbmData;
                        this.paymentResultMessageData = result.messageData;

                        if (action === 'veh_pbm_paypal_payment_cancel') {
                            await this.declinePBM(this.pbmData, 'paypal payment canceled or failed');
                        }

                        this.showSuccessPaymentMessage(result.messageKey);

                        const transactionId = currentUrl.searchParams.get('transaction_id');

                        if (transactionId && action === 'veh_pbm_paypal_payment_complete') {
                            await this.paymentService.completePaymentIntent(transactionId).toPromise().catch(() => false);
                        }
                    }

                    break;
                }
                case 'veh_fleet_lpn_ppp_complete':
                case 'veh_fleet_lpn_ppp_cancel': {
                    this.location.replaceState('/dashboard/profile/vehicles');

                    const result = this.decodeUrlToJson(currentUrl.searchParams.get('veh_fleet_lpn_ppp_result'));

                    if (result) {
                        const transactionId = currentUrl.searchParams.get('transaction_id');

                        if (transactionId && action === 'veh_fleet_lpn_ppp_complete') {
                            await this.paymentService.completePaymentIntent(transactionId).toPromise().catch(() => false);
                        }

                        this.paymentResultMessageData = result.messageData;
                        this.showFleetResultMessage(result.messageKey);
                    }

                    this.setIntervalUpdate();

                    break;
                }
            }
        }

        await this.loadLicensePlates();
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

    async executePBM (isPaymentMethodChanged : boolean) {
        const response : [ any, PayByMailData, PaymentConfig, number ] = await Promise.all([
            this.stripeService.getStripeInstance(),
            this.paymentService.fetchPayByMail().toPromise(),
            this.paymentService.fetchPaymentConfig().toPromise(),
            this.paymentService.fetchHoursToPay().toPromise(),
        ]).catch(() => null);

        if (!response) {
            this.showSuccessPaymentMessage('profile.pbm.common_error');
            console.warn('Something wrong with PBM init');
            return;
        }

        const [ stripe, pbmData, paymentConfig, hoursToPay ] = response;

        if (!pbmData || pbmData.status !== 'OK' || !pbmData.pbm_id) {
            this.showSuccessPaymentMessage('profile.pbm.common_error');
            console.warn('Something wrong with PBM init');
            return;
        }

        this.stripe = stripe;
        this.paymentResultMessageData.hoursToPay = hoursToPay;
        this.paymentResultMessageData.licensePlates = `<strong>${ this.lastLPN }</strong>`;

        const isPaymentMethodOk = await this.paymentService.checkCurrentPaymentMethod(paymentConfig, null, {
            amount: pbmData.amount,
            currency: pbmData.currency
        }).catch(() => false);

        if (!isPaymentMethodOk) {
            if (isPaymentMethodChanged) {
                await this.declinePBM(pbmData, 'something wrong with payment method');
                this.showSuccessPaymentMessage('profile.pbm.common_error');
            } else {
                this.showPaymentMethodPopup();
            }
            return;
        }

        const isAmountLessThanMin = pbmData.amount < paymentConfig.min_payment_amount;
        const isAmountGreaterThanMax = pbmData.amount > paymentConfig.max_payment_amount;

        if (isAmountLessThanMin || isAmountGreaterThanMax) {
            await this.declinePBM(pbmData, 'limits');
            this.showSuccessPaymentMessage('profile.pbm.common_error');
            return;
        }

        this.paymentConfig = paymentConfig;
        this.pbmData = pbmData;
        this.isPaymentZipRequired = paymentConfig.payment_verification_required;

        this.payByMailConfirmMessageKey = (
            this.paymentConfig.payment_method_type === 'DCB' && this.isPaymentZipRequired ?
                'profile.pbm.confirm_with_zip' :
                'profile.pbm.confirm_without_zip'
        );

        this.paymentResultMessageData.invoice = this.pbmData.name;
        this.paymentResultMessageData.amount = this.currencyService.format(this.pbmData.amount, this.pbmData.currency);

        if (paymentConfig.payment_method_type === 'GOOGLEPAY' || paymentConfig.payment_method_type === 'APPLEPAY') {
            await this.prepareWalletPayment();
        } else {
            this.showPaymentPopup();
        }
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

    showSuccessPaymentMessage (paymentResultMessageKey : string) {
        this.paymentResultMessageKey = paymentResultMessageKey;
        this.activePopup = 'payment-result';
    }

    hidePaymentResultMessage () {
        this.activePopup = null;
    }

    showPaymentError (errorCode : number) {
        /*switch (errorCode) {
            case 203:
            case 205:
            case 307:
                this.showSuccessPaymentMessage(`dashboard.welcome.message_${ errorCode }`);
                return;
        }*/

        this.showSuccessPaymentMessage('profile.pbm.common_error');
    }

    async payByPayPal () {
        const successResultData = this.encodeJsonToUrl({
            messageKey: 'profile.pbm.message_approved',
            messageData: this.paymentResultMessageData,
            pbmData: this.pbmData
        });

        const cancelResultData = this.encodeJsonToUrl({
            messageKey: 'profile.pbm.common_error',
            messageData: this.paymentResultMessageData,
            pbmData: this.pbmData
        });

        const response = await this.sendPaymentRequest({
            pbmId: this.pbmData.pbm_id,
            makePayment: true,
            returnUrl: `/dashboard/profile/vehicles?action=veh_pbm_paypal_payment_complete&veh_pbm_paypal_payment_result=${ successResultData }`,
            cancelUrl: `/dashboard/profile/vehicles?action=veh_pbm_paypal_payment_cancel&veh_pbm_paypal_payment_result=${ cancelResultData }`,
        });

        const approveUrl = response?.payment_intent?.approve_payment_url;

        if (!response || response.status !== 'OK' || !approveUrl) {
            await this.declinePBM(this.pbmData, 'fetch paypal order error');
            this.showPaymentError(response && response.errorCode || 205);
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

        await this.loadLicensePlates();

        console.warn(intentResponse);

        if (intentResponse.status === 'OK') {
            this.showSuccessPaymentMessage('profile.pbm.message_approved');
        } else {
            this.showPaymentError(intentResponse && intentResponse.errorCode || 205);
        }
    }

    async payByCard () {
        const intentResponse = await this.sendPaymentRequest({
            pbmId: this.pbmData.pbm_id,
            makePayment: true,
        });

        if (!intentResponse || intentResponse.status !== 'OK') {
            await this.declinePBM(this.pbmData, 'fetch payment intent error');
            this.showPaymentError(intentResponse && intentResponse.errorCode || 205);
            return;
        }

        // Payment done w/o 3D secure
        if (intentResponse.payment_complete) {
            await this.loadLicensePlates();
            this.showSuccessPaymentMessage('profile.pbm.message_approved');
            return;
        }

        const paymentIntent = intentResponse.payment_intent;

        // There is payment intent with status !== 'succeeded'
        // 3D secure required
        const response = await this.stripe.confirmCardPayment(paymentIntent.client_secret).catch(() => null);

        if (!response || response.error) {
            console.warn(response);
            await this.declinePBM(this.pbmData, '3D Secure failed');
            this.showSuccessPaymentMessage('profile.pbm.common_error');
            return;
        }

        const isOk = await this.paymentService.completePaymentIntent(intentResponse.transaction_id).toPromise().catch(() => false);

        if (isOk) {
            await this.loadLicensePlates();
            this.showSuccessPaymentMessage('profile.pbm.message_approved');
            return;
        }

        // Unexpected state or 3D secure fail
        this.showSuccessPaymentMessage('profile.pbm.common_error');
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
                this.showPaymentError(intentResponse && intentResponse.errorCode || 205);
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
                this.showSuccessPaymentMessage('profile.pbm.common_error');
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
                await this.loadLicensePlates();
                this.showSuccessPaymentMessage('profile.pbm.message_approved');
            } else {
                this.showSuccessPaymentMessage('profile.pbm.common_error');
            }
        });

        paymentRequest.on('cancel', async (e) => {
            await this.declinePBM(this.pbmData, 'wallet payment canceled');
            this.showSuccessPaymentMessage('profile.pbm.common_error');
            console.log('cancel', e);
        });

        this.walletPaymentAttrs = { paymentRequest };
        this.showPaymentPopup();
    }

    showPaymentPopup () {
        this.resetPaymentPopup();
        this.activePopup = 'payment';
    }

    async onSubmitPayment (makePayment : boolean) {
        if (this.paymentSubmittingBy) {
            return;
        }

        this.paymentSubmittingBy = makePayment ? 'yes' : 'no';

        if (!makePayment) {
            await this.declinePBM(this.pbmData, 'declined by user');
            this.showSuccessPaymentMessage('profile.pbm.message_declined');
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

    async payByVenmo () {
        const response = await this.sendPaymentRequest({
            pbmId: this.pbmData.pbm_id,
            makePayment: true,
        });

        if (!response || response.status !== 'OK') {
            await this.declinePBM(this.pbmData, 'failed to pay pbm with venmo');
            this.showPaymentError(response?.errorCode || 205);
            return;
        }

        this.showSuccessPaymentMessage('profile.pbm.message_approved');
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

    async onPaymentMethodSelected (event : PaymentMethodDoneEvent) {
        if (this.paymentModel === 'POSTPAID') {
            this.executePBM(true);
        } else if (this.paymentModel === 'FLEET') {
            if (event.isOk && (await this.paymentService.checkCurrentPaymentMethod(event.paymentConfig))) {
                this.executeFleetPayment();
            } else {
                this.showFleetResultMessage('profile.fleet.message_issues');
            }
        }
    }

    showPaymentMethodPopup () {
        this.activePopup = 'payment-method';
    }

    hidePaymentMethodPopup () {
        this.activePopup = null;
    }

    // ----------------------------------------

    async loadLicensePlates () {
        const licensePlates = await this.licensePlatesService.fetchLicensePlates().toPromise().catch(() => null);

        if (licensePlates === null) {
            this.licensePlates = null;
            this.recountLicensePlates();
        } else {
            this.licensePlates = licensePlates;
            this.recountLicensePlates();
        }
    }

    ngOnDestroy () : void {
        this.clearUpdateInterval();
        this.subs.forEach(sub => sub.unsubscribe());
    }

    recountLicensePlates () {
        if (this.licensePlates === null) {
            this.listState = 'error';
        } else {
            this.listState = this.licensePlates.length > 0 ? 'list' : 'empty';
        }
    }

    onUnregisterClick (licensePlate : LicensePlateItem) {
        if (this.isSubmitting) {
            return;
        }

        this.lpToUnregister = licensePlate;
        this.activePopup = 'unregister-confirm';
    }

    hideUnregisterPopup () {
        this.activePopup = null;
        this.lpToUnregister = null;
    }

    onUnregisterCancel () {
        if (this.isSubmitting) {
            return;
        }

        this.hideUnregisterPopup();
    }

    async onUnregisterConfirm () {
        if (this.isSubmitting) {
            return;
        }

        this.isSubmitting = true;

        const lpnId = this.lpToUnregister.id;
        const errorCode : number = await this.licensePlatesService.unregLicensePlate(lpnId).toPromise().catch(e => e);

        this.isSubmitting = false;

        this.hideUnregisterPopup();

        switch (errorCode) {
            case 0:  // Ok
                this.licensePlates = this.licensePlates.filter(item => item.id !== lpnId);
                this.recountLicensePlates();

                this.toastService.create({
                    message: [ 'vehicles.unreg_ok' ],
                    timeout: 9000
                });
                break;
            case 204:
                this.showErrorPopup(`vehicles.unreg_error_${ errorCode }`);
                break;
            default:
                this.toastService.create({
                    message: [ 'vehicles.unreg_error' ],
                    timeout: 9000
                });
                break;
        }
    }

    showErrorPopup (key : string, data? : any) {
        this.errorPopupMessage = { key, data };
        this.activePopup = 'error';
    }

    hideErrorPopup () {
        this.errorPopupMessage = null;
        this.activePopup = null;
    }

    onAddVehicle () {
        this.lpn = '';
        this.isLpnValid = false;
        this.addPopupError = null;
        this.activePopup = 'add';
    }

    onCloseAddPopup () {
        this.activePopup = null;
    }

    async onCommitVehicle () {
        if (this.isSubmitting) {
            return;
        }

        this.addPopupError = null;
        this.isSubmitting = true;

        const licensePlate = (this.lpn || '').trim().replace(/\s+/g, ' ');

        this.lastLPN = licensePlate;

        const result = await this.licensePlatesService.addLicensePlate(licensePlate).toPromise().catch(e => e);
        // const result : any = 215;

        // if (this.paymentModel === 'FLEET' && [ 0, 216 ].includes(result)) {
        //
        // }

        switch (result) {
            case 0:
                this.isSubmitting = false;
                await this.loadLicensePlates();
                this.onCloseAddPopup();
                this.toastService.create({
                    message: [ 'vehicles.add_success' ],
                    timeout: 9000
                });
                break;
            case 203:
            case 208:
            case 209:
            case 210:
            case 211:
            case 212:
            case 213:
                this.isSubmitting = false;
                this.addPopupError = { key: `vehicles.add_error_${ result }` };
                break;
            case 215:
                await this.executePBM(false);
                this.isSubmitting = false;
                break;
            case 216:
                await this.executeFleetPayment();
                this.setIntervalUpdate();
                this.isSubmitting = false;
                break;
            default:
                this.isSubmitting = false;
                this.addPopupError = { key: `vehicles.add_error_common` };
        }
    }

    validateLpn () {
        this.isLpnValid = !!(this.lpn || '').trim();
    }

    onGoBack () {
        this.router.navigateByUrl('/dashboard/profile');
    }

    clearUpdateInterval () {
        console.log('clearUpdateInterval');
        if (this.updateTimeout) {
            console.log('cleared');
            clearTimeout(this.updateTimeout);
            this.updateTimeout = null;
        }
    }

    setIntervalUpdate () {
        this.loadLicensePlates();
        this.clearUpdateInterval();
        this.updateTimeout = setTimeout(() => this.setIntervalUpdate(), 30000);
    }

    // --------------------------------------------------------------------

    async executeFleetPayment () {
        this.attemptsToSelectPaymentMethodForFleet++;
        this.pendingLPNs = await this.licensePlatesService.fetchPendingLPNs().toPromise().catch(() => null);

        console.warn(this.pendingLPNs);

        if ((this.pendingLPNs?.plates || []).length > 0) {
            this.pendingLPNsActivity = this.pendingLPNs.plates.reduce((acc, plate) => {
                acc[plate.id] = true;
                return acc;
            }, {});
            this.recountActivePendingLPNs();
            this.activePopup = 'fleet-lpn';
        } else {
            this.pendingLPNs = null;
            this.activePopup = null;
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
    }

    async onConfirmFleetPayment () {
        if (this.isConfirmingFleet || !this.pendingLPNs) {
            return;
        }

        this.isConfirmingFleet = true;

        this.paymentConfig = await this.paymentService.fetchPaymentConfig().toPromise().catch(() => null);

        if (!this.paymentConfig) {
            this.isConfirmingFleet = false;
            this.pendingLPNs = null;
            this.activePopup = null;
            this.showFleetResultMessage('profile.fleet.message_issues');
            return;
        }

        const isPaymentMethodOk = await this.paymentService.checkCurrentPaymentMethod(this.paymentConfig, null, {
            amount: this.activePendingLPNsTotal,
            currency: 'USD'
        }).catch(() => false);

        if (!isPaymentMethodOk) {
            this.isConfirmingFleet = false;
            this.pendingLPNs = null;

            if (this.attemptsToSelectPaymentMethodForFleet <= 1) {
                this.showPaymentMethodPopup();
            } else {
                this.showFleetResultMessage('profile.fleet.message_issues');
            }

            return;
        }

        const acceptedLPNIds : string[] = this.pendingLPNs.plates.reduce((acc, plate) => {
            if (this.pendingLPNsActivity[plate.id]) {
                acc.push(plate.id);
            }

            return acc;
        }, []);

        this.pendingLPNsInvoice = await this.licensePlatesService.acceptPendingLPNs(acceptedLPNIds).toPromise().catch(() => null);

        if (!this.pendingLPNsInvoice || !this.pendingLPNsInvoice.invoice_id || !this.pendingLPNsInvoice.invoice_items) {
            this.isConfirmingFleet = false;
            this.pendingLPNs = null;
            this.showFleetResultMessage('profile.fleet.message_declined');
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

        if (!errorCode && response.payment_complete) {
            this.showFleetResultMessage('profile.fleet.message_ok');
        } else {
            this.showFleetResultMessage('profile.fleet.message_issues');
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
            messageKey: 'profile.fleet.message_ok',
            messageData: this.paymentResultMessageKey,
        });

        const cancelResultData = this.encodeJsonToUrl({
            messageKey: 'profile.fleet.message_issues',
            messageData: this.paymentResultMessageKey,
        });

        const { response, errorCode } = <InvoicePaymentResponseWithError>await this.invoicesService.makePayment({
            invoices: this.getInvoiceForFleetPayment(),
            verification_code: null,
            payment_method_type: this.paymentConfig.payment_method_type,
            payment_method_id: this.paymentConfig.payment_method_id,
            return_url: `/dashboard/profile/vehicles?action=veh_fleet_lpn_ppp_complete&veh_fleet_lpn_ppp_result=${ successResultData }`,
            cancel_url: `/dashboard/profile/vehicles?action=veh_fleet_lpn_ppp_cancel&veh_fleet_lpn_ppp_result=${ cancelResultData }`,
        }).toPromise().catch(error => error);

        const approveUrl = response?.payment_intent?.approve_payment_url;

        if (errorCode || !approveUrl) {
            this.isConfirmingFleet = false;
            this.showFleetResultMessage('profile.fleet.message_issues');
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
            this.isConfirmingFleet = false;
            this.showFleetResultMessage('profile.fleet.message_issues');
            return;
        }

        const paymentIntent = intentResponse.payment_intent;

        if (intentResponse.payment_complete) {
            this.isConfirmingFleet = false;
            this.showFleetResultMessage('profile.fleet.message_ok');
            return;
        }

        // Payment incomplete
        // -------------------------------------------------------

        const response = await this.stripe.confirmCardPayment(paymentIntent.client_secret).catch(() => null);

        if (!response) {
            this.isConfirmingFleet = false;
            this.showFleetResultMessage('profile.fleet.message_issues');
            return;
        }

        if (response.error) {
            this.isConfirmingFleet = false;
            const error = this.stripeService.localizeStripeError(response.error);
            this.showFleetResultMessage('profile.fleet.message_issues');
            console.warn('Failed to auth 3D secure:', response, error);
            return;
        }

        const isOkOrError = await this.paymentService.completePaymentIntent(intentResponse.transaction_id).toPromise().catch(errorCode => errorCode);

        this.isConfirmingFleet = false;

        if (isOkOrError === true) {
            this.showFleetResultMessage('profile.fleet.message_ok');
        } else {
            this.showFleetResultMessage('profile.fleet.message_issues');
        }
    }

    resetFleetZipPopup () {
        this.zipCode = '';
        this.isFleetZipSubmitting = false;
        this.validateFleetZipPopup();
    }

    showFleetZipPopup () {
        this.isConfirmingFleet = false;
        this.activePopup = 'fleet-lpn-zip';
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
            this.showFleetResultMessage('profile.fleet.message_ok');
        } else {
            this.showFleetResultMessage('profile.fleet.message_issues');
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
            this.isConfirmingFleet = false;
            this.showFleetResultMessage('profile.fleet.message_issues');
            return;
        }

        const paymentIntent = intentResponse.payment_intent;

        const { paymentRequest } = await this.stripeService.getWalletPaymentRequest({
            amount: paymentIntent.amount,
            currency: paymentIntent.currency,
            label: 'Total',
        });

        if (!paymentRequest) {
            this.isConfirmingFleet = false;
            this.showFleetResultMessage('profile.fleet.message_issues');
            return;
        }

        paymentRequest.on('paymentmethod', async (e) => {
            const confirmResponse = await this.stripe.confirmCardPayment(paymentIntent.client_secret, {
                payment_method: e.paymentMethod.id
            }, {
                handleActions: false
            });

            if (confirmResponse.error) {
                e.complete('fail');
                this.isConfirmingFleet = false;
                const error = this.stripeService.localizeStripeError(confirmResponse.error);
                this.showFleetResultMessage('profile.fleet.message_issues');
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
                        this.isConfirmingFleet = false;
                        const error = this.stripeService.localizeStripeError(confirmResult.error);
                        this.showFleetResultMessage('profile.fleet.message_issues');
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
                this.showFleetResultMessage('profile.fleet.message_ok');
            } else {
                this.showFleetResultMessage('profile.fleet.message_issues');
            }
        });

        paymentRequest.on('cancel', () => {
            this.isConfirmingFleet = false;
            this.showFleetResultMessage('profile.fleet.message_issues');
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

        this.activePopup = 'fleet-wallet-payment-confirm';
    }

    onConfirmFleetWalletPayment () {
        this.walletFleetPaymentAttrs.paymentRequest.show();
    }

    showFleetResultMessage (messageKey : string) {
        this.paymentResultMessageKey = messageKey;
        this.activePopup = 'payment-result';
    }
}
