import {
    ChangeDetectorRef,
    Component,
    OnDestroy,
    OnInit,
    Renderer2, ViewChild,
    ViewEncapsulation,
} from '@angular/core';
import {ActivatedRoute, Router} from '@angular/router';
import {animateChild, query, transition, trigger} from '@angular/animations';
import {delay, firstValueFrom, forkJoin, Observable, of, shareReplay, Subject, Subscription} from 'rxjs';
import {TitleService} from '../../../services/title.service';
import {DeviceService, ViewportBreakpoint} from '../../../services/device.service';
import {
    AllLicensePlatesHttpResponse, GetLicensePlatesResponseV2,
    LicensePlateItem,
    LicensePlatesService, LicensePlateType, PendingLPN,
    PendingLPNResponse, PendingLPNsInvoiceResponse
} from '../../../services/license-plates.service';
import {ToastService} from '../../../services/toast.service';
import {Base64Service} from '../../../services/base64.service';
import {Location} from '@angular/common';
import {
    MakePaymentByEmailResponse,
    PayByMailData,
    PaymentConfig, PaymentMethodType,
    PaymentService
} from '../../../services/payment.service';
import {PaymentMethodWallet, StripeService} from '../../../services/stripe.service';
import {CurrencyService} from '../../../services/currency.service';
import {InvoicePaymentComponent} from '../../invoices/invoice-payment/invoice-payment.component';
import {PaymentMethodDoneEvent} from '../../payment-method/payment-method/payment-method.component';
import {
    InvoicePaymentInvoice, InvoicePaymentRequestData,
    InvoicePaymentResponseWithError,
    InvoicesService
} from '../../invoices/invoices.service';
import {AccountPaymentModel, UserService} from '../../../services/user.service';
import {
    AbstractControl,
    UntypedFormBuilder,
    UntypedFormControl,
    UntypedFormGroup,
    Validators
} from "@angular/forms";
import {FormValidationService} from "../../../_shared/validation-message/form-validation.service";
import {
    maxDateValidator,
    minDateTodayValidator, minDateValidator,
    minOneHourDurationValidator, minOneHourExtendDurationValidator
} from "../../../_shared/validators/date-validator";
import {paymentActions, PendingPlateCreateModel} from "../../dashboard/dashboard.component";
import {
    ConfirmFleetPaymentService,
    EmmitNewPendingLicensePlatesListToPayParams
} from "../../_services/confirm-fleet-payment.service";
import {
    FleetLpnRegisterComponent,
    FleetLpRegistrationEvent
} from "../../../_modals/modals-components/fleet-lpn-register/fleet-lpn-register.component";
import {Dialog, DialogRef} from "@angular/cdk/dialog";
import {catchError, map, take} from "rxjs/operators";
import {SubscriptionApiService} from "../../../subscriptions/_services/subscription-api.service";
import {FlowGlobalStateService} from "../../../subscriptions/_services/flow-global-state.service";
import {IsShowAddVehicleModalAfterLoginService} from "../../../services/is-show-add-vehicle-modal-after-login.service";
import {
    CheckSubscriptionActionsResponse,
    CurrentSubscriptionResponse
} from "../../../subscriptions/_models/subscription.models";
import PaymentIntent = stripe.paymentIntents.PaymentIntent;
import Stripe = stripe.Stripe;
import PaymentIntentResponse = stripe.PaymentIntentResponse;

type ListState = 'loading' | 'list' | 'error';
type ActivePopup =
    'add'
    | 'unregister-confirm'
    | 'payment-result'
    | 'payment'
    | 'payment-method'
    | 'error'
    | 'fleet-lpn'
    | 'fleet-lpn-zip'
    | 'fleet-wallet-payment-confirm'
    | 'extend-rental-lpn-period'
    | 'subscription-limit';

type PaymentSubmittingBy = null | 'yes' | 'no';

interface ErrorMessage {
    key: string;
    data?: any
}

enum API_RESPONSE_CODES {
    // Generic
    'GENERIC_ERROR' = 1,

    // Authentication
    'AUTHENTICATION_ERROR' = 100,
    'AUTHENTICATION_REQUIRED',
    'PIN_DEACTIVATED',
    'MISSING_ROLE',
    'REQUEST_THROTTLED',
    'ACCOUNT_LOCKED',
    'STRIPE_WEBHOOK_SIGNATURE_ERROR',

    // Account issues
    'ACCOUNT_EXISTS' = 200,
    'INVALID_DATA',
    'INVALID_PAYMENT_DATA',
    'LICENSE_PLATE_REGISTRATION_ERROR',
    'OUTSTANDING_INVOICE_EXISTS',
    'LICENSE_PLATE_REGISTERED_WITHOUT_PAYMENT',
    'STRIPE_WEBHOOK_DATA_ERROR',
    'INVALID_REQUEST',
    'INVALID_LICENSE_PLATE_FORMAT',
    'LICENSE_PLATE_REGISTRATION_WITH_ACCOUNT_LOCK',
    'LICENSE_PLATE_REGISTRATION_WITH_PAYMENT_LOCK',
    'LICENSE_PLATE_ASSIGNED_TO_ACCOUNT_ERROR',
    'LICENSE_PLATE_BELONGS_TO_ANOTHER_FLEET',
    'LICENSE_PLATE_ALREADY_REGISTERED',
    'PAYPAL_WEBHOOK_DATA_ERROR',
    'LICENSE_PLATE_WITH_OUTSTANDING_PBM_INVOICE',
    'LICENSE_PLATE_REGISTRATION_FEE_REQUIRED',
    'PENDING_DISPUTE_EXISTS',
    'INVALID_RENTAL_END_DATE',

    // Payment issues
    'DCB_INSUFFICIENT_CREDIT' = 300,
    'PAYMENT_GATEWAY_ERROR',
    'PAYMENT_LOCK',
    'ZIP_CODE_LIMIT_REACHED',
    'ZIP_CODE_MISMATCH',
    'PAYMENT_CHANNEL_NOT_DEFINED',
    'THIRD_PARTY_PAYMENT_SETUP_ERROR',
    'REFUND_REQUIRED_ERROR',
    'PAYMENT_CARD_DECLINED',
    'CARD_INSUFFICIENT_CREDIT',
    'CARD_NOT_SUPPORTED',
    'PAYMENT_POTENTIAL_FRAUD',
    'PAYMENT_VELOCITY_ERROR',
}


interface WelcomeMessageData {
    licensePlates: string;
    hoursToPay: number;
    invoice: string;
    amount: string;
}

interface PaymentRequestOptions {
    pbmId: string;
    makePayment: boolean;
    verificationCode?: string;
    returnUrl?: string;
    cancelUrl?: string;
}

export interface SortedVehiclesList {
    active: {
        usual: LicensePlateItem[];
        rental: LicensePlateItem[];
    };
    deactivated: {
        usual: LicensePlateItem[];
        rental: LicensePlateItem[];
    };
}

@Component({
    selector: 'vehicles',
    exportAs: 'vehicles',
    templateUrl: './vehicles.component.html',
    styleUrls: ['./vehicles.component.scss'],
    encapsulation: ViewEncapsulation.None,
    host: {
        'class': 'vehicles',
        '[@vehiclesHost]': 'true'
    },
    animations: [
        trigger('vehiclesHost', [
            transition(':enter', [
                query('@*', animateChild(), {optional: true}),
            ]),
        ]),
    ]
})
export class VehiclesComponent implements OnInit, OnDestroy {
    viewportBreakpoint: ViewportBreakpoint;
    private readonly _notification_message_timeout_MS = 9000;
    subs: Subscription[] = [];

    listState: ListState = 'loading';

    listOfLicensePlates: LicensePlateItem[];
    listOfRentalLicensePlates: LicensePlateItem[];

    vehiclesList: SortedVehiclesList = {
        'active': {
            'usual': [],
            'rental': []
        },
        'deactivated': {
            'usual': [],
            'rental': []
        }
    }

    readonly vehiclesListTitlesTranslations = {
        'active': {
            'usual': 'vehicles.plates_list_personal_title',
            'rental': 'vehicles.plates_list_rental_title'
        },
        'deactivated': {
            'usual': 'vehicles.plates_list_personal_title_inactive',
            'rental': 'vehicles.plates_list_rental_title_inactive'
        }
    }

    activeVehiclesListTitlesTranslations = this.vehiclesListTitlesTranslations.active;


    activeVehiclesList = this.vehiclesList.active;

    isLoading: boolean = false;

    lpToUnregister: LicensePlateItem;

    activePopup: null | ActivePopup = null;

    isLpnValid: boolean = false;

    newLpnName: string = '';
    newLpnIsRentalCheckboxModel: boolean = false;

    addPopupError: ErrorMessage = null;

    errorPopupMessage: ErrorMessage = null;

    paymentConfig: PaymentConfig = null;

    stripe: any;

    mobileWalletPaymentAttrs: {
        paymentRequest: any;
    } = null;

    paymentSubmittingBy: PaymentSubmittingBy = null;

    isPaymentZipRequired: boolean = false;

    zipCode: string = '';

    payByMailConfirmMessageKey: string;

    paymentResultMessageKey: string;

    paymentResultMessageData: WelcomeMessageData = {
        licensePlates: '',
        hoursToPay: 47,
        invoice: '',
        amount: '',
    };

    @ViewChild('paymentComponent', {read: InvoicePaymentComponent})
    paymentComponent: InvoicePaymentComponent;

    pbmData: PayByMailData;

    isPaymentPopupValid: boolean = false;

    lastLPN: string;

    // --------------------------------------------------------

    accountPaymentModel: AccountPaymentModel = null;

    pendingLPNResponse: PendingLPNResponse = null;

    isSelectedForPaymentPendingLPNByIdMap: { [id: string]: boolean } = null;
    mapOfDatesForRentalPendingLPNs: {} = null;

    selectedForPaymentPendingLPNsCount: number = 0;

    activePendingLPNsTotal: number = 0;

    pendingLPNsInvoice: PendingLPNsInvoiceResponse = null;

    isConfirmingFleet: boolean = false;

    isFleetZipSubmitting: boolean = false;

    isFleetZipValid: boolean = false;

    isFleetWalletSubmitting: boolean = false;

    walletFleetPaymentAttrs: {
        amountFormatted: string;
        wallet: string;
        paymentRequest: any;
    } = null;

    attemptsToSelectPaymentMethodForFleet: number = 0;

    extendLPNPeriodForm: UntypedFormGroup = new UntypedFormGroup({
        end_date: new UntypedFormControl(null, Validators.required),
        end_time: new UntypedFormControl(null, Validators.required),

    });
    public selectedLPNForExtend: LicensePlateItem | null = null;

    pendingLPNsForm: UntypedFormGroup;
    public MAX_RENTAL_CAR_PERIOD_DATE: Date;
    public MAX_DAYS_FOR_RENTAL_CAR_PERIOD: number = 1;
    private fleetPendingPayDialog: DialogRef<unknown, FleetLpnRegisterComponent>;
    private fleetPendingToPayLPNsSubscription: Subscription;
    private supportedLPNTypes: string[];

    historyItems: LicensePlateItem[];
    private subscriptionInfo: CurrentSubscriptionResponse = null;
    membershipLicensePlatesLimit: number = 0;
    usedLicensePlatesCount: number = 0;
    private pageUpdateEvent$: Subject<boolean> = new Subject<boolean>();

    constructor(
        private renderer: Renderer2,
        private router: Router,
        private activatedRoute: ActivatedRoute,
        private location: Location,
        private titleService: TitleService,
        private deviceService: DeviceService,
        private licensePlatesService: LicensePlatesService,
        private toastService: ToastService,
        private paymentService: PaymentService,
        private stripeService: StripeService,
        private currencyService: CurrencyService,
        private invoicesService: InvoicesService,
        private base64Service: Base64Service,
        private userService: UserService,
        public formValidationService: FormValidationService,
        public fb: UntypedFormBuilder,
        public formValidatorService: FormValidationService,
        private confirmFleetPaymentService: ConfirmFleetPaymentService,
        private subscriptionApiService: SubscriptionApiService,
        private flowGlobalStateService: FlowGlobalStateService,
        public dialog: Dialog,
        public flowGlobalState: FlowGlobalStateService,
        private changeDetectorRef: ChangeDetectorRef,
        private isShowAddVehicleModalAfterLoginService: IsShowAddVehicleModalAfterLoginService
    ) {
        window.scroll(0, 0);

        this.accountPaymentModel = this.userService.getUserData().account.paymentModel;

        this.viewportBreakpoint = this.deviceService.viewportBreakpoint;
        this.subs.push(this.deviceService.onResize.subscribe((message) => {
            if (message.breakpointChange) {
                this.viewportBreakpoint = message.breakpointChange.current;
            }
        }));

        this.listState = 'loading';
    }

    async ngOnInit() {
        this.titleService.setTitle('vehicles.page_title');
        await this.init();
        this.pendingLPNsForm = this.fb.group({});
        this.getLPNSupportedTypes();

        if (this.isShowAddVehicleModalAfterLoginService.isShow()) {
            this.onAddVehicle();
        }

        this.subs.push(this.pageUpdateEvent$.pipe(
            delay(1000)
        ).subscribe(() => {
            this.loadDataInParallel();
        }));
    }

    async init() {
        await this.handleUrlAction();
        this.loadDataInParallel();
    }

    public openPendingLPNsPayDialog() {

        this.fleetPendingToPayLPNsSubscription = this.confirmFleetPaymentService.newPendingLicensePlatesListToPay$.subscribe(
            (data: EmmitNewPendingLicensePlatesListToPayParams) => {
                if (data) {
                    this.onConfirmFleetPayment(data).then(_r => null);
                }
            }
        );

        this.fleetPendingPayDialog = this.dialog.open(FleetLpnRegisterComponent, {
            minWidth: '300px',
            data: null
        });

        this.fleetPendingPayDialog.componentInstance.add.subscribe((event: FleetLpRegistrationEvent) => {
            this.closePendingLPNsPayDialog();
            this.emmitPageDataUpdate();
            this.flowGlobalStateService.navigateLicensePlateAddedAcknowledgement();
        })

        this.fleetPendingPayDialog.componentInstance.cancel.subscribe((event: FleetLpRegistrationEvent) => {
            this.closePendingLPNsPayDialog();
            this.flowGlobalStateService.navigateLicensePlateDeclinedAcknowledgement();
        })

    }

    public closePendingLPNsPayDialog() {
        if (this.fleetPendingPayDialog) {
            this.fleetPendingToPayLPNsSubscription.unsubscribe();
            this.fleetPendingPayDialog.componentInstance?.add?.unsubscribe()
            this.fleetPendingPayDialog.componentInstance?.cancel?.unsubscribe();
            this.fleetPendingPayDialog.close();
        }
    }

    private async handleUrlAction() {
        const currentUrl = new URL(window.location.href);
        const fromURLPaymentAction: paymentActions = currentUrl.searchParams.get('action') as paymentActions;

        if (fromURLPaymentAction) {
            switch (fromURLPaymentAction) {
                case 'veh_pbm_paypal_payment_complete':
                case 'veh_pbm_paypal_payment_cancel': {
                    this.location.replaceState('/dashboard/profile/vehicles');

                    const result = this.decodeUrlToJson(currentUrl.searchParams.get('veh_pbm_paypal_payment_result'));

                    if (result) {
                        this.pbmData = result.pbmData;
                        this.paymentResultMessageData = result.messageData;

                        if (fromURLPaymentAction === 'veh_pbm_paypal_payment_cancel') {
                            await this.declinePBM(this.pbmData, 'paypal payment canceled or failed');
                        }

                        this.showSuccessPaymentMessage(result.messageKey);

                        const transactionId = currentUrl.searchParams.get('transaction_id');

                        if (transactionId && fromURLPaymentAction === 'veh_pbm_paypal_payment_complete') {
                            await firstValueFrom(this.paymentService.completePaymentIntent(transactionId));
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

                        if (transactionId && fromURLPaymentAction === 'veh_fleet_lpn_ppp_complete') {
                            await this.paymentService.completePaymentIntent(transactionId).toPromise().catch(() => false);
                        }

                        this.paymentResultMessageData = result.messageData;
                        this.showFleetResultMessage(result.messageKey);
                    }

                    this.emmitPageDataUpdate();

                    break;
                }
            }
        }
    }

    public addControlToPendingLPNsForm(controlName: string) {
        this.pendingLPNsForm.addControl(controlName, this.fb.group({
                endDate: ['',
                    Validators.compose([
                        Validators.required,
                        minDateTodayValidator(),
                    ])
                ],
                endTime: ['',
                    Validators.compose([
                        Validators.required,
                        minOneHourDurationValidator()
                    ])
                ],
            }, {validators: [maxDateValidator(this.MAX_RENTAL_CAR_PERIOD_DATE)]}
        ));
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

    async executePBM(isPaymentMethodChanged: boolean) {
        const response: [Stripe, PayByMailData, PaymentConfig, number] = await Promise.all([
            this.stripeService.getStripeInstance(),
            firstValueFrom(this.paymentService.fetchPayByMail()),
            firstValueFrom(this.paymentService.fetchPaymentConfig()),
            firstValueFrom(this.paymentService.fetchHoursToPay()),
        ]).catch(() => null);

        if (!response) {
            this.showSuccessPaymentMessage('profile.pbm.common_error');
            console.warn('Something wrong with PBM init');
            return;
        }

        const [stripe, pbmData, paymentConfig, hoursToPay] = response;

        if (!pbmData || pbmData.status !== 'OK' || !pbmData.pbm_id) {
            this.showSuccessPaymentMessage('profile.pbm.common_error');
            console.warn('Something wrong with PBM init');
            return;
        }

        this.stripe = stripe;
        this.paymentResultMessageData.hoursToPay = hoursToPay;
        this.paymentResultMessageData.licensePlates = `<strong>${this.lastLPN}</strong>`;

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

    async declinePBM(payByMailData: PayByMailData, reason: string = null): Promise<void> {
        const response = await this.sendPaymentRequest({
            pbmId: payByMailData.pbm_id,
            makePayment: false,
        });

        if (response.status === 'OK') {
            console.warn(`PBM rejected (reason: ${reason})`);
        } else {
            console.warn(`PBM must be rejected (reason: ${reason}) but an error occurred`)
        }
    }

    async sendPaymentRequest(options: PaymentRequestOptions): Promise<MakePaymentByEmailResponse> {
        let requestData = {
            make_payment: options.makePayment,
            verification_code: options.verificationCode || null,
            payment_method_type: this.paymentConfig && this.paymentConfig.payment_method_type || null,
            payment_method_id: this.paymentConfig && this.paymentConfig.payment_method_id || null,
            return_url: options.returnUrl || null,
            cancel_url: options.cancelUrl || null,
        };
        return firstValueFrom(this.paymentService.makePaymentByEmail(options.pbmId, requestData))
            .then(response => {
                if (response.status !== 'OK' && !response.errorCode) {
                    response.errorCode = API_RESPONSE_CODES.LICENSE_PLATE_REGISTERED_WITHOUT_PAYMENT;
                }

                return response;
            })
            .catch((errorCode: number) => {
                return {
                    status: 'ERROR',
                    errorCode
                };
            });
    }

    showSuccessPaymentMessage(paymentResultMessageKey: string) {
        this.paymentResultMessageKey = paymentResultMessageKey;
        this.activePopup = 'payment-result';
    }

    hidePaymentResultMessage() {
        this.activePopup = null;
    }

    showPaymentError(_: number) {
        /*switch (errorCode) {
            case 203:
            case API_RESPONSE_CODES.LICENSE_PLATE_REGISTERED_WITHOUT_PAYMENT:
            case 307:
                this.showSuccessPaymentMessage(`dashboard.welcome.message_${ errorCode }`);
                return;
        }*/

        this.showSuccessPaymentMessage('profile.pbm.common_error');
    }

    async payByPayPal() {
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
            returnUrl: `/dashboard/profile/vehicles?action=veh_pbm_paypal_payment_complete&veh_pbm_paypal_payment_result=${successResultData}`,
            cancelUrl: `/dashboard/profile/vehicles?action=veh_pbm_paypal_payment_cancel&veh_pbm_paypal_payment_result=${cancelResultData}`,
        });

        const approveUrl = response?.payment_intent?.approve_payment_url;

        if (!response || response.status !== 'OK' || !approveUrl) {
            await this.declinePBM(this.pbmData, 'fetch paypal order error');
            this.showPaymentError(response && response.errorCode || API_RESPONSE_CODES.LICENSE_PLATE_REGISTERED_WITHOUT_PAYMENT);
        } else {
            window.location.assign(approveUrl);
        }
    }

    async payByCarrier() {
        const zipCode: string = this.isPaymentZipRequired ? (this.zipCode || '').trim() : null;
        const intentResponse = await this.sendPaymentRequest({
            pbmId: this.pbmData.pbm_id,
            makePayment: true,
            verificationCode: zipCode,
        });

        this.emmitPageDataUpdate();

        console.warn(intentResponse);

        if (intentResponse.status === 'OK') {
            this.showSuccessPaymentMessage('profile.pbm.message_approved');
        } else {
            this.showPaymentError(intentResponse && intentResponse.errorCode || API_RESPONSE_CODES.LICENSE_PLATE_REGISTERED_WITHOUT_PAYMENT);
        }
    }

    async payByCard() {
        const intentResponse = await this.sendPaymentRequest({
            pbmId: this.pbmData.pbm_id,
            makePayment: true,
        });

        if (!intentResponse || intentResponse.status !== 'OK') {
            await this.declinePBM(this.pbmData, 'fetch payment intent error');
            this.showPaymentError(intentResponse && intentResponse.errorCode || API_RESPONSE_CODES.LICENSE_PLATE_REGISTERED_WITHOUT_PAYMENT);
            return;
        }

        // Payment done w/o 3D secure
        if (intentResponse.payment_complete) {
            this.emmitPageDataUpdate();
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

        const isPaymentIntentCompleted = await this.paymentService.completePaymentIntent(intentResponse.transaction_id).toPromise().catch(() => false);

        if (isPaymentIntentCompleted) {
            this.showSuccessPaymentMessage('profile.pbm.message_approved');
            this.emmitPageDataUpdate();
            return;
        }

        // Unexpected state or 3D secure fail
        this.showSuccessPaymentMessage('profile.pbm.common_error');
    }

    async prepareWalletPayment() {
        const {paymentRequest} = await this.stripeService.getMobileWalletPaymentRequest({
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
                this.showPaymentError(intentResponse && intentResponse.errorCode || API_RESPONSE_CODES.LICENSE_PLATE_REGISTERED_WITHOUT_PAYMENT);
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
                this.showSuccessPaymentMessage('profile.pbm.message_approved');
                this.emmitPageDataUpdate();
            } else {
                this.showSuccessPaymentMessage('profile.pbm.common_error');
            }
        });

        paymentRequest.on("cancel", async () => {
            await this.declinePBM(this.pbmData, 'wallet payment canceled');
            this.showSuccessPaymentMessage('profile.pbm.common_error');
        });

        this.mobileWalletPaymentAttrs = {paymentRequest};
        this.showPaymentPopup();
    }

    showPaymentPopup() {
        this.resetPaymentPopup();
        this.activePopup = 'payment';
    }

    async onSubmitPayment(makePayment: boolean) {
        if (this.paymentSubmittingBy) {
            return;
        }

        this.paymentSubmittingBy = makePayment ? 'yes' : 'no';

        if (!makePayment) {
            await this.declinePBM(this.pbmData, 'declined by user');
            this.showSuccessPaymentMessage('profile.pbm.message_declined');
            return;
        }

        const paymentMethodActions = {
            'DCB': async () => await this.payByCarrier(),
            'PAYPAL': async () => await this.payByPayPal(),
            'DEBIT_CARD': async () => await this.payByCard(),
            'CREDIT_CARD': async () => await this.payByCard(),
            'GOOGLEPAY': () => {
                this.mobileWalletPaymentAttrs.paymentRequest.show();
                this.mobileWalletPaymentAttrs = null;
            },
            'APPLEPAY': () => {
                this.mobileWalletPaymentAttrs.paymentRequest.show();
                this.mobileWalletPaymentAttrs = null;
            },
            'VENMO': async () => await this.payByVenmo(),
        };

        const accountPaymentMethodType = this.paymentConfig.payment_method_type;
        const paymentAction = paymentMethodActions[accountPaymentMethodType];

        if (paymentAction) {
            await paymentAction();
        } else {
            console.error(`Undefined payment method: ${this.paymentConfig.payment_method_type}`);
        }
    }

    async payByVenmo() {
        const response = await this.sendPaymentRequest({
            pbmId: this.pbmData.pbm_id,
            makePayment: true,
        });

        if (!response || response.status !== 'OK') {
            await this.declinePBM(this.pbmData, 'failed to pay pbm with venmo');
            this.showPaymentError(response?.errorCode || API_RESPONSE_CODES.LICENSE_PLATE_REGISTERED_WITHOUT_PAYMENT);
            return;
        }

        this.showSuccessPaymentMessage('profile.pbm.message_approved');
    }

    validatePaymentPopup() {
        this.isPaymentPopupValid = (
            this.paymentConfig.payment_method_type !== 'DCB' ||
            !this.isPaymentZipRequired ||
            (this.zipCode || '').trim().length >= 4
        );
    }

    resetPaymentPopup() {
        this.zipCode = '';
        this.paymentSubmittingBy = null;
        this.validatePaymentPopup();
    }

    async onPaymentMethodSelected(event: PaymentMethodDoneEvent) {
        if (this.accountPaymentModel === 'POSTPAID') {
            this.executePBM(true);
        } else if (this.accountPaymentModel === 'FLEET') {
            if (event.isOk && (await this.paymentService.checkCurrentPaymentMethod(event.paymentConfig))) {
                await this.executeFleetPayment();
            } else {
                this.showFleetResultMessage('profile.fleet.message_issues');
            }
        }
    }

    showPaymentMethodPopup() {
        this.dialog.closeAll();
        this.activePopup = 'payment-method';
    }

    private processLicensePlatesResponse(res: GetLicensePlatesResponseV2): void {
        if (res.plates === null) {
            this.listOfLicensePlates = null;
            this.listOfRentalLicensePlates = null;
            return;
        }

        this.sortLicensePLateList(res.plates);

        this.usedLicensePlatesCount = this.vehiclesList.active.usual.length + this.vehiclesList.active.rental.length;

        this.setListState(this.vehiclesList);
    }

    private sortLicensePLateList(licensePlateList: LicensePlateItem[]) {
        this.vehiclesList = this.licensePlatesService.sortLicensePlateList(licensePlateList);
        this.activeVehiclesList = this.vehiclesList.active;
    }


    private loadDataInParallel(): void {
        forkJoin({
            licensePlates: this.licensePlatesService.getAllLicensePlatesV2(),
            subscriptionInfo: this.subscriptionApiService.getCurrentSubscription(),
        }).subscribe({
            next: ({licensePlates, subscriptionInfo}) => {
                this.processLicensePlatesResponse(licensePlates);
                this.subscriptionInfo = subscriptionInfo;
                this.membershipLicensePlatesLimit = this.subscriptionInfo.max_lp;
            },
            error: (err) => {
                console.error('Error loading data:', err);
            }
        });
    }

    ngOnDestroy(): void {
        this.subs.forEach(sub => sub.unsubscribe());
    }

    private setListState(vehiclesList: SortedVehiclesList): void {

        const isActiveUsual = vehiclesList.active.usual;
        const isActiveRental = vehiclesList.active.rental;
        const isDeactivatedUsual = vehiclesList.deactivated.usual;
        const isDeactivatedRental = vehiclesList.deactivated.rental;

        if (!isActiveUsual || !isActiveRental || !isDeactivatedUsual || !isDeactivatedRental) {
            this.listState = 'error';
            return;
        }

        this.listState = 'list';
    }


    public unregisterLicensePlate(licensePlate: LicensePlateItem) {
        if (this.isLoading) {
            return;
        }

        this.lpToUnregister = licensePlate;
        this.activePopup = 'unregister-confirm';
    }

    hideUnregisterPopup() {
        this.activePopup = null;
        this.lpToUnregister = null;
        this.emmitPageDataUpdate();
    }

    onUnregisterCancel() {
        if (this.isLoading) {
            return;
        }

        this.hideUnregisterPopup();
    }

    async onUnregisterConfirm() {
        if (this.isLoading) {
            return;
        }

        this.isLoading = true;

        const lpnId = this.lpToUnregister.id;
        const errorCode: number = await firstValueFrom(this.licensePlatesService.unregLicensePlate(lpnId));

        this.isLoading = false;

        this.hideUnregisterPopup();

        switch (errorCode) {
            case 0:  // Ok
                this.setListState(this.vehiclesList);

                this.toastService.create({
                    message: ['vehicles.unreg_ok'],
                    timeout: this._notification_message_timeout_MS
                });
                this.emmitPageDataUpdate();
                break;
            case 204:
                this.showErrorPopup(`vehicles.unreg_error_${errorCode}`);
                break;
            default:
                this.toastService.create({
                    message: ['vehicles.unreg_error'],
                    timeout: this._notification_message_timeout_MS
                });
                break;
        }

    }

    showErrorPopup(key: string, data?: any) {
        this.errorPopupMessage = {key, data};
        this.activePopup = 'error';
    }

    hideErrorPopup() {
        this.errorPopupMessage = null;
        this.activePopup = null;
    }

    onAddVehicle(): void {
        this.subscriptionApiService.checkSubscriptionActions().subscribe({
            next: (response: CheckSubscriptionActionsResponse) => {
                this.resetAddVehicleState();
                this.activePopup = response.add_license_plate ? 'add' : 'subscription-limit';
            },
            error: (err) => {
                console.error('Error checking subscription actions:', err);
            }
        });
    }

    private resetAddVehicleState(): void {
        this.newLpnName = '';
        this.isLpnValid = false;
        this.addPopupError = null;
    }


    onCloseAddPopup() {
        // If the add vehicle modal is being shown as part of onboarding, show the informational modal
        if (this.isShowAddVehicleModalAfterLoginService.isShow()) {
            this.showFleetResultMessage('dashboard.fleet.message_declined');
            this.isShowAddVehicleModalAfterLoginService.hide();
        } else {
            this.activePopup = null;
        }
    }


    async submitNewLPNForm() {
        if (this.isLoading) {
            return;
        }
        this.addPopupError = null;
        this.isLoading = true;

        const licensePlate = (this.newLpnName || '').trim().replace(/\s+/g, ' ');

        this.lastLPN = licensePlate;

        let newLPN = {
            lp: licensePlate,
            rental: this.newLpnIsRentalCheckboxModel || false
        }

        const result = await firstValueFrom(this.licensePlatesService.addLicensePlate(newLPN)).catch(e => e);
        switch (result) {
            case 0 :
                this.isLoading = false;
                this.onCloseAddPopup();
                this.toastService.create({
                    message: ['vehicles.add_success'],
                    timeout: this._notification_message_timeout_MS
                });
                this.emmitPageDataUpdate();
                break;
            case API_RESPONSE_CODES.LICENSE_PLATE_REGISTRATION_ERROR:
            case API_RESPONSE_CODES.INVALID_LICENSE_PLATE_FORMAT:
            case API_RESPONSE_CODES.LICENSE_PLATE_REGISTRATION_WITH_ACCOUNT_LOCK:
            case API_RESPONSE_CODES.LICENSE_PLATE_REGISTRATION_WITH_PAYMENT_LOCK:
            case API_RESPONSE_CODES.LICENSE_PLATE_ASSIGNED_TO_ACCOUNT_ERROR:
            case API_RESPONSE_CODES.LICENSE_PLATE_BELONGS_TO_ANOTHER_FLEET:
            case API_RESPONSE_CODES.LICENSE_PLATE_ALREADY_REGISTERED:
                this.isLoading = false;
                this.addPopupError = {key: `vehicles.add_error_${result}`};
                break;
            case API_RESPONSE_CODES.LICENSE_PLATE_WITH_OUTSTANDING_PBM_INVOICE:
                await this.executePBM(false);
                this.isLoading = false;
                break;
            case API_RESPONSE_CODES.LICENSE_PLATE_REGISTRATION_FEE_REQUIRED:
                await this.executeFleetPayment();
                this.isLoading = false;
                this.newLpnIsRentalCheckboxModel = false;
                break;
            default:
                this.isLoading = false;
                this.addPopupError = {key: `vehicles.add_error_common`};
        }
    }


    validateLpn() {
        this.isLpnValid = !!(this.newLpnName || '').trim();
    }

    onGoBack() {
        this.router.navigateByUrl('/dashboard/profile');
    }

    // --------------------------------------------------------------------

    async executeFleetPayment() {
        this.attemptsToSelectPaymentMethodForFleet++;

        this.pendingLPNResponse = await firstValueFrom(this.licensePlatesService.getPendingLPNs()).catch(() => null);

        const pendingLPNS = this.pendingLPNResponse.plates;

        let isPendingLPNs = (pendingLPNS || []).length > 0;
        if (isPendingLPNs) {
            this.activePopup = null;
            this.openPendingLPNsPayDialog();

        } else {
            this.pendingLPNResponse = null;
            this.closePendingLPNsPayDialog();
            this.activePopup = null;
        }
    }

    // @todo change to new logic add subscription to changes inn service
    activeVehiclesTab: 'active' | 'inactive' = 'active';

    async onConfirmFleetPayment(data: EmmitNewPendingLicensePlatesListToPayParams) {
        const listOfSelectedLPNs = data ? data.listOfLPns : null;
        const listOfSelectedLPNsNames = data ? data.lpnNames : null;


        if (this.isConfirmingFleet || !this.pendingLPNResponse) {
            return;
        }

        this.isConfirmingFleet = true;

        this.paymentConfig = await firstValueFrom(this.paymentService.fetchPaymentConfig()).catch(() => null);

        if (!this.paymentConfig) {
            this.isConfirmingFleet = false;
            this.pendingLPNResponse = null;
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
            this.pendingLPNResponse = null;

            if (this.attemptsToSelectPaymentMethodForFleet <= 1) {
                this.closePendingLPNsPayDialog();
                this.showPaymentMethodPopup();
            } else {
                this.showFleetResultMessage('profile.fleet.message_issues');
            }

            return;
        }

        await this.getInvoicesForPendingLPNs(listOfSelectedLPNs);
        this.makePaymentByType(this.paymentConfig.payment_method_type);

    }

    private async getInvoicesForPendingLPNs(listOfSelectedLPNs: {
        pending_license_plate_id: string;
        end_date?: Date | string | null
    }[]) {
        this.pendingLPNsInvoice = await firstValueFrom(this.licensePlatesService.acceptPendingLPNsWithRental(listOfSelectedLPNs)).catch(() => null);

        const isInvoiceEmpty = !this.pendingLPNsInvoice || !this.pendingLPNsInvoice.invoice_id || !this.pendingLPNsInvoice.invoice_items;
        if (isInvoiceEmpty) {
            this.cancelOfAddingNewLPNs();
            return;
        }
    }

    private cancelOfAddingNewLPNs() {
        this.isConfirmingFleet = false;
        this.pendingLPNResponse = null;
        this.showFleetResultMessage('dashboard.fleet.message_declined');
    }

    private makePaymentByType(type: PaymentMethodType) {
        switch (type) {
            case 'DCB':
                if (this.paymentConfig.payment_verification_required) {
                    this.showFleetZipPopup();
                } else {
                    this.submitFleetZipPayment();
                }
                break;
            case 'PAYPAL':
                this.payFleetPayPal();
                break;
            case 'DEBIT_CARD':
            case 'CREDIT_CARD':
                this.payFleetCard();
                break;
            case 'GOOGLEPAY':
            case 'APPLEPAY':
                this.payFleetWallet();
                break;
            case 'VENMO':
                this.payFleetVenmo();
                break;
        }
    }

    async payFleetVenmo() {
        const requestData = {
            invoices: this.getInvoiceForFleetPayment(),
            verification_code: null,
            payment_method_type: this.paymentConfig.payment_method_type,
            payment_method_id: this.paymentConfig.payment_method_id,
            return_url: null,
            cancel_url: null,
        };

        const {
            response,
            errorCode
        } = await firstValueFrom(this.invoicesService.makePayment(requestData)).catch(error => error);

        this.isConfirmingFleet = false;

        if (!errorCode && response.payment_complete) {
            this.newLPNAddedSusses();
        } else {
            this.showFleetResultMessage('profile.fleet.message_issues');
        }
    }

    private newLPNAddedSusses() {
        this.closePendingLPNsPayDialog();
        this.showFleetResultMessage('profile.fleet.message_ok');
        this.emmitPageDataUpdate();
    }

    private getInvoiceForFleetPayment(): InvoicePaymentInvoice[] {
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

    async payFleetPayPal() {
        const successResultData = this.encodeJsonToUrl({
            messageKey: 'profile.fleet.message_ok',
            messageData: this.paymentResultMessageKey,
        });

        const cancelResultData = this.encodeJsonToUrl({
            messageKey: 'profile.fleet.message_issues',
            messageData: this.paymentResultMessageKey,
        });

        let returnUrl = `/dashboard/profile/vehicles?action=veh_fleet_lpn_ppp_complete&veh_fleet_lpn_ppp_result=${successResultData}`;
        let cancelUrl = `/dashboard/profile/vehicles?action=veh_fleet_lpn_ppp_cancel&veh_fleet_lpn_ppp_result=${cancelResultData}`;

        let requestData = {
            invoices: this.getInvoiceForFleetPayment(),
            verification_code: null,
            payment_method_type: this.paymentConfig.payment_method_type,
            payment_method_id: this.paymentConfig.payment_method_id,
            return_url: returnUrl,
            cancel_url: cancelUrl,
        };
        const {response, errorCode} = <InvoicePaymentResponseWithError>await this.invoicesService.makePayment(requestData).toPromise().catch(error => error);

        const approveUrl = response?.payment_intent?.approve_payment_url;

        if (errorCode || !approveUrl) {
            this.isConfirmingFleet = false;
            this.showFleetResultMessage('profile.fleet.message_issues');
        } else {
            window.location.assign(approveUrl);
        }
    }

    async payFleetCard() {
        let requestData: InvoicePaymentRequestData = {
            invoices: this.getInvoiceForFleetPayment(),
            verification_code: null,
            payment_method_type: this.paymentConfig.payment_method_type,
            payment_method_id: this.paymentConfig.payment_method_id,
            return_url: null,
            cancel_url: null,
        };
        const {response: intentResponse, errorCode} = await firstValueFrom(this.invoicesService.makePayment(requestData)).catch(error => error);

        if (errorCode) {
            this.isConfirmingFleet = false;
            this.showFleetResultMessage('profile.fleet.message_issues');
            return;
        }

        const paymentIntent: PaymentIntent = intentResponse.payment_intent;

        if (intentResponse.payment_complete) {
            this.isConfirmingFleet = false;
            this.newLPNAddedSusses();
            return;
        }

        // Payment incomplete
        // -------------------------------------------------------

        const confirmCardPaymentResponse: PaymentIntentResponse = await this.stripe.confirmCardPayment(paymentIntent.client_secret).catch(() => null);

        if (!confirmCardPaymentResponse) {
            this.isConfirmingFleet = false;
            this.showFleetResultMessage('profile.fleet.message_issues');
            return;
        }

        if (confirmCardPaymentResponse.error) {
            this.isConfirmingFleet = false;
            const error = this.stripeService.localizeStripeError(confirmCardPaymentResponse.error);
            this.showFleetResultMessage('profile.fleet.message_issues');
            console.warn('Failed to auth 3D secure:', confirmCardPaymentResponse, error);
            return;
        }

        const isOkOrError: boolean = await firstValueFrom(this.paymentService.completePaymentIntent(intentResponse.transaction_id)).catch(errorCode => errorCode);

        this.isConfirmingFleet = false;

        if (isOkOrError === true) {
            this.newLPNAddedSusses();
        } else {
            this.showFleetResultMessage('profile.fleet.message_issues');
        }
    }

    resetFleetZipPopup() {
        this.zipCode = '';
        this.isFleetZipSubmitting = false;
        this.validateFleetZipPopup();
    }

    showFleetZipPopup() {
        this.isConfirmingFleet = false;
        this.closePendingLPNsPayDialog();
        this.activePopup = 'fleet-lpn-zip';
    }

    validateFleetZipPopup() {
        this.isFleetZipValid = (this.zipCode || '').trim().length >= 4;
    }

    async submitFleetZipPayment() {
        if (!this.isFleetZipValid || this.isFleetZipSubmitting) {
            return;
        }

        this.isFleetZipSubmitting = true;

        const requestData: InvoicePaymentRequestData = {
            invoices: this.getInvoiceForFleetPayment(),
            verification_code: this.paymentConfig.payment_verification_required ? (this.zipCode || '').trim() : null,
            payment_method_type: this.paymentConfig.payment_method_type,
            payment_method_id: this.paymentConfig.payment_method_id,
            return_url: null,
            cancel_url: null,
        };
        const {errorCode} = await firstValueFrom(this.invoicesService.makePayment(requestData)).catch(error => error);

        this.isFleetZipSubmitting = false;

        if (!errorCode) {
            this.newLPNAddedSusses();
        } else {
            this.closePendingLPNsPayDialog();
            this.showFleetResultMessage('profile.fleet.message_issues');
        }
    }

    async payFleetWallet() {
        const walletType = <PaymentMethodWallet>this.paymentConfig.payment_method_type;

        const {response: intentResponse, errorCode} = await firstValueFrom(this.invoicesService.makePayment({
            invoices: this.getInvoiceForFleetPayment(),
            verification_code: null,
            payment_method_type: walletType,
            payment_method_id: this.paymentConfig.payment_method_id,
            return_url: null,
            cancel_url: null,
        })).catch(error => error);

        if (errorCode) {
            this.isConfirmingFleet = false;
            this.showFleetResultMessage('profile.fleet.message_issues');
            return;
        }

        const paymentIntent: PaymentIntent = intentResponse.payment_intent;

        const {paymentRequest} = await this.stripeService.getMobileWalletPaymentRequest({
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
                payment_method: e.paymentMethod.id,
                setup_future_usage: 'off_session'
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

            const isActionRequired = confirmResponse.paymentIntent.status === 'requires_action';
            if (isActionRequired) {

                const confirmCardPaymentResult: PaymentIntentResponse = await this.stripe.confirmCardPayment(paymentIntent.client_secret);
                const confirmCardPaymentResultError = confirmCardPaymentResult.error;
                const isCardDeclined: boolean = confirmResponse.error.code === 'card_declined'

                if (confirmCardPaymentResultError) {
                    console.warn('Failed to auth 3D secure:', confirmCardPaymentResultError);

                    if (isCardDeclined) {
                        this.isConfirmingFleet = false;
                        const error = this.stripeService.localizeStripeError(confirmCardPaymentResultError);
                        this.showFleetResultMessage('profile.fleet.message_issues');
                        console.warn('Failed:', error);
                        return;
                    }

                    isOk = false;
                }
            }

            if (isOk) {
                // tested in GPay walletName is 'googlePay' which is consistent with what server expects
                const walletName = this.paymentService.transformPaymentMethodName(e.paymentMethod.card.wallet.type);
                const paymentMethodId = e?.paymentMethod?.id;
                if (walletName && paymentMethodId) {
                    await firstValueFrom(this.paymentService.setNewPaymentMethod({
                        payment_method_type: walletName,
                        payment_method_id: paymentMethodId
                    })).catch(() => null);
                }
                await firstValueFrom(this.paymentService.completePaymentIntent(intentResponse.transaction_id)).catch(() => false);
            }

            this.isConfirmingFleet = false;

            if (isOk) {
                this.newLPNAddedSusses();
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

    onShowWalletPaymentConfirmPopup(paymentRequest: any, paymentIntent: PaymentIntent, walletType: PaymentMethodWallet) {
        this.isConfirmingFleet = false;
        this.isFleetWalletSubmitting = false;

        this.walletFleetPaymentAttrs = {
            amountFormatted: this.currencyService.format(paymentIntent.amount, paymentIntent.currency),
            wallet: this.stripeService.getWalletName(walletType),
            paymentRequest
        };

        this.activePopup = 'fleet-wallet-payment-confirm';
    }

    onConfirmFleetWalletPayment() {
        this.walletFleetPaymentAttrs.paymentRequest.show();
    }

    showFleetResultMessage(messageKey: string) {
        this.closePendingLPNsPayDialog();
        this.paymentResultMessageKey = messageKey;
        this.activePopup = 'payment-result';
    }


    public onCancelExtendRentalPeriodPopup() {
        this.activePopup = null;
        this.selectedLPNForExtend = null;
        this.extendLPNPeriodForm.patchValue({end_date: null});
        this.extendLPNPeriodForm.patchValue({end_time: null});
    }


    public onSubmitExtendRentalPeriodPopup() {
        const formValue = this.extendLPNPeriodForm.value;

        if (this.extendLPNPeriodForm.valid) {
            const endDate = new Date(formValue.end_date);
            const endTime = new Date(formValue.end_time);

            const endDateTime = this.getMixedDateTimeFromTwoDates(endDate, endTime);

            this.activePopup = null;

            this.extendRentalPeriod(endDateTime.toISOString());
        } else {
            this.formValidationService.validateFormGroup(this.extendLPNPeriodForm);
        }
    }

    private getMixedDateTimeFromTwoDates(dateForDate: Date, DateForTime: Date) {
        const mixedDate = new Date(
            dateForDate.getFullYear(),
            dateForDate.getMonth(),
            dateForDate.getDate(),
            DateForTime.getHours(),
            DateForTime.getMinutes()
        );
        return mixedDate || null;
    }


    onExtendLPNRentalPeriod(licensePlate: LicensePlateItem) {
        this.selectedLPNForExtend = licensePlate;
        this.extendLPNPeriodForm.patchValue({end_date: this.getDateFromDateTime(licensePlate.end_date)});
        this.extendLPNPeriodForm.patchValue({end_time: this.getTimeFromDateTime(licensePlate.end_date)});
        const endDateControl = this.extendLPNPeriodForm.get('end_date');
        const endTimeControl = this.extendLPNPeriodForm.get('end_time');

        endDateControl.setValidators([Validators.required, minDateValidator(this.getDateFromDateTime(licensePlate.end_date))]);
        endTimeControl.setValidators([Validators.required, minOneHourExtendDurationValidator(this.getDateFromDateTime(licensePlate.end_date), this.getTimeFromDateTime(licensePlate.end_date))]);

        this.activePopup = 'extend-rental-lpn-period';
    }

    private getDateFromDateTime(dateTime: string): Date {
        const date = new Date(dateTime);
        date.setHours(0, 0, 0, 0);
        return date;
    }

    private getTimeFromDateTime(dateTime: string): Date {
        const date = new Date(dateTime);
        date.setFullYear(1970, 0, 1);
        return date;
    }


    private extendRentalPeriod(endDateTime: string) {
        this.licensePlatesService.extendLPNRentalPeriod(this.selectedLPNForExtend, endDateTime).subscribe(
            {
                next: () => {
                    this.toastService.create({
                        message: ['vehicles.rental_period_extend_susses'],
                        timeout: this._notification_message_timeout_MS
                    });
                    this.emmitPageDataUpdate();
                },
                error: () => {
                    this.toastService.create({
                        message: ['vehicles.rental_period_extend_error'],
                        timeout: this._notification_message_timeout_MS
                    });
                }
            }
        )
    }

    private getEndDateForRentalLPN(plate: PendingLPN): Date {
        const formValue = this.pendingLPNsForm.value?.[plate.id];
        const endDate = new Date(formValue?.endDate);
        const endTime = new Date(formValue?.endTime);

        return this.getMixedDateTimeFromTwoDates(endDate, endTime);
    }

    public getControl(controlName, formGroup: UntypedFormGroup = this.extendLPNPeriodForm): AbstractControl | null {
        return this.formValidatorService.getFormControl(controlName, formGroup);
    }

    public changePendingLPNType(plate: PendingLPN) {
        plate.rental ? this.addControlToPendingLPNsForm(plate.id) : this.removeControlFromPendingLPNsForm(plate.id);
    }

    private removeControlFromPendingLPNsForm(controlName: string) {
        this.pendingLPNsForm.removeControl(controlName);
    }

    public getLPNSupportedTypes() {
        return this.licensePlatesService.getSupportedTaLPNTypes().pipe(
            map(response => response.supported_types),
            catchError(() => of(false)),
            take(1)
        ).subscribe(
            (supportedTypes: string[]) => {
                this.supportedLPNTypes = supportedTypes;
            }
        );
    }

    isRentalTypeSupported() {
        return this.supportedLPNTypes.includes('RENTAL');
    }

    public onSubscriptionLimitCancel(event: any) {
        this.activePopup = null
    }

    public onSubscriptionLimitUpdate(event: any) {
        this.activePopup = null
        this.flowGlobalState.navigateSubscriptionSelection();
    }

    showLicensePlateStatusHistory(licensePlate: LicensePlateItem) {
        this.licensePlatesService.getAllLicensePlatesHistory(licensePlate.id).subscribe(resp => {
            this.historyItems = resp.items;
            this.changeDetectorRef.detectChanges();
        })
    }

    onHistoryClose() {
        this.historyItems = null;
    }

    onSwitchVehiclesTab(state: 'active' | 'inactive') {
        this.activeVehiclesTab = state;
        state === 'active' ? this.setTabState('active') : this.setTabState('inactive');
    }

    setTabState(state) {
        switch (state) {
            case 'active':
                this.activeVehiclesList = this.vehiclesList.active;
                this.activeVehiclesListTitlesTranslations = this.vehiclesListTitlesTranslations.active;
                break;
            case 'inactive':
                this.activeVehiclesList = this.vehiclesList.deactivated;
                this.activeVehiclesListTitlesTranslations = this.vehiclesListTitlesTranslations.deactivated;
                break;
        }
    }

    emmitPageDataUpdate() {
        this.pageUpdateEvent$.next(true);
    }
}
