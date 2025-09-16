import {
    ChangeDetectionStrategy,
    Component,
    OnDestroy,
    OnInit,
    ViewChild,
    ViewEncapsulation
} from '@angular/core';
import {Router, NavigationEnd} from '@angular/router';
import {TitleService} from '../../services/title.service';
import {DeviceService, ViewportBreakpoint} from '../../services/device.service';
import {firstValueFrom, forkJoin, Subscription} from 'rxjs';
import {AccountPaymentModel, UserService} from '../../services/user.service';
import {DashboardService} from '../../services/dashboard.service';
import {
    InvoicePaymentInvoice,
    InvoicePaymentRequestData,
    InvoicePaymentResponseWithError,
    InvoicesService
} from '../invoices/invoices.service';
import {
    MakePaymentByEmailResponse,
    PayByMailData,
    PaymentConfig,
    PaymentMethodType,
    PaymentService
} from '../../services/payment.service';
import {
    AllLicensePlatesHttpResponse,
    LicensePlatesService,
    PendingLPNResponse,
    PendingLPNsInvoiceResponse
} from '../../services/license-plates.service';
import {InvoicePaymentComponent} from '../invoices/invoice-payment/invoice-payment.component';
import {defer} from '../../lib/utils';
import {CurrencyService} from '../../services/currency.service';
import {
    PaymentMethodDoneEvent,
    PaymentMethodPopupMode
} from '../payment-method/payment-method/payment-method.component';
import {PaymentMethodWallet, StripeService} from '../../services/stripe.service';
import {TidioService} from '../../services/tidio.service';
import {Base64Service} from '../../services/base64.service';
import {Location} from '@angular/common';
import {DebugService} from '../../services/debug.service';
import {AsyncJsScriptLoaderService} from "../../services/async-js-script-loader.service";
import {
    ConfirmFleetPaymentService,
    EmmitNewPendingLicensePlatesListToPayParams,
    LPNType
} from "../_services/confirm-fleet-payment.service";
import {
    FleetLpnRegisterComponent,
    FleetLpRegistrationEvent
} from "../../_modals/modals-components/fleet-lpn-register/fleet-lpn-register.component";
import {Dialog, DialogRef} from "@angular/cdk/dialog";
import {SubscriptionApiService} from "../../subscriptions/_services/subscription-api.service";
import {
    SubscriptionSelectComponent,
    SubscriptionSelectionDialogData
} from "../../subscriptions/subscription-select/subscription-select.component";
import {
    CurrentSubscriptionResponse
} from "../../subscriptions/_models/subscription.models";
import {
    AddSubscriptionFlowEvent,
    FlowGlobalStateService
} from "../../subscriptions/_services/flow-global-state.service";
import {
    SubscriptionPaymentPreviewComponent
} from "../../subscriptions/subscription-payment-preview/subscription-payment-preview.component";
import {
    UserRegistrationFlowTypeService,
    userRegistrationFlowType
} from "../../services/user-registration-flow-type.service";
import {
    SubscriptionAcknowledgementComponent, SubscriptionAcknowledgementDialogData
} from "../../subscriptions/subscription-acknowledgement/subscription-acknowledgement.component";
import Stripe = stripe.Stripe;
import PaymentIntentResponse = stripe.PaymentIntentResponse;
import Error = stripe.Error;
import {IsShowAddVehicleModalAfterLoginService} from "../../services/is-show-add-vehicle-modal-after-login.service";
import { RegistrationWelcomeComponent } from '../../subscriptions/registration-welcome/registration-welcome.component';
import { filter } from 'rxjs/operators';

interface WelcomeMessageData {
    licensePlates: string;
    hoursToPay: number;
    invoice: string;
    amount: string;
}

type ModalsToShow =
    null
    | 'payment-method'
    | 'payment'
    | 'welcome'
    | 'fleet-lpn'
    | 'fleet-lpn-zip'
    | 'fleet-wallet-payment-confirm'
    | 'account-debt-lock'
    | 'account-soft-lock'
    | 'subscription-expired';

type PaymentSubmittingBy = null | 'yes' | 'no';

export enum PaymentModels {
    POSTPAID = 'POSTPAID',
    FLEET = 'FLEET',
}

const fleetMessages = {
    ok: 'dashboard.fleet.message_ok',
    declined: 'dashboard.fleet.message_declined',
    issues: 'dashboard.fleet.message_issues'
}

export type paymentActions =
    'veh_pbm_paypal_payment_complete' |
    'veh_pbm_paypal_payment_cancel' |
    'veh_fleet_lpn_ppp_complete' |
    'veh_fleet_lpn_ppp_cancel'
    ;

export interface PendingPlateCreateModel {
    pending_license_plate_id: string;
    start_date?: string | null;
    end_date?: string | null;
    license_plate_type: LPNType;
    license_plate_category: string;
}


enum ModalType {
    ACCOUNT_DEBT_LOCK = 'account-debt-lock',
    ACCOUNT_SOFT_LOCK = 'account-soft-lock',
    SUBSCRIPTION_EXPIRED = 'subscription-expired',
    PAYMENT_METHOD = 'payment-method',
    WELCOME = 'welcome',
    FLEET_WALLET_PAYMENT_CONFIRM = 'fleet-wallet-payment-confirm',
    FLEET_LPN_ZIP = 'fleet-lpn-zip',
    PAYMENT = 'payment',
}

export interface WalletFleetPaymentAttrs {
    amountFormatted: string;
    wallet: string;
    paymentRequest: any;
}

@Component({
    selector: 'app-dashboard',
    templateUrl: './dashboard.component.html',
    styleUrls: ['./dashboard.component.scss'],
    changeDetection: ChangeDetectionStrategy.Default,
    encapsulation: ViewEncapsulation.None,
    host: {
        'class': 'dashboard'
    }
})
export class DashboardComponent implements OnInit, OnDestroy {
    viewportBreakpoint: ViewportBreakpoint;

    subs: Subscription[] = [];


    payByMailConfirmMessageKey: string;

    welcomeMessageKey: string;

    welcomeMessageData: WelcomeMessageData = {
        licensePlates: '',
        hoursToPay: 47,
        invoice: '',
        amount: '',
    };

    @ViewChild('paymentComponent', {read: InvoicePaymentComponent})
    paymentComponent: InvoicePaymentComponent;

    pbmData: PayByMailData;

    isPaymentPopupValid: boolean = false;

    paymentSubmittingBy: PaymentSubmittingBy = null;

    isPaymentZipRequired: boolean = false;

    zipCode: string = '';

    activeModal: ModalsToShow = null;

    paymentConfig: PaymentConfig = null;

    stripeInstance: Stripe = null;

    mobileWalletPaymentAttrs: {
        paymentRequest: any;
    } = null;

    tollAuthorityPaymentModel: AccountPaymentModel = null;

    pendingLPNResponse: PendingLPNResponse = null;
    selectedForPaymentPendingLPNsTotalSum: number = 0;
    pendingLPNsInvoice: PendingLPNsInvoiceResponse = null;

    fleetPaymentState = {
        zipSubmitting: false,
        zipValid: false,
        confirming: false,
        walletSubmitting: false,
    }


    walletFleetPaymentAttrs: WalletFleetPaymentAttrs = null;

    paymentMethodPopupMode: PaymentMethodPopupMode = 'setup';


    private fleetPendingPayDialog: DialogRef<unknown, FleetLpnRegisterComponent>;
    private fleetPendingToPayLPNsSubscription$: Subscription;

    private flowConfig: {
        currentSubscription: CurrentSubscriptionResponse;
    } = {
        currentSubscription: null,
    };

    subscriptionPaymentError: Error = null;
    private flowEventsSubscription$: Subscription;

    isHidePaymentMethodSelectCancelButton: boolean = true;

    constructor(
        private router: Router,
        private location: Location,
        private titleService: TitleService,
        private deviceService: DeviceService,
        private userService: UserService,
        private dashboardService: DashboardService,
        private paymentService: PaymentService,
        private stripeService: StripeService,
        private licensePlatesService: LicensePlatesService,
        private currencyService: CurrencyService,
        private tidioService: TidioService,
        private base64Service: Base64Service,
        private invoicesService: InvoicesService,
        private debugService: DebugService,
        private asyncScriptLoader: AsyncJsScriptLoaderService,
        private confirmFleetPaymentService: ConfirmFleetPaymentService,
        public dialog: Dialog,
        private subscriptionApiService: SubscriptionApiService,
        private registrationFlowGlobalStateService: FlowGlobalStateService,
        private registrationFlowTypeService: UserRegistrationFlowTypeService,
        private isShowAddVehicleModalAfterLoginService: IsShowAddVehicleModalAfterLoginService,
    ) {
        window.scroll(0, 0);


        this.tollAuthorityPaymentModel = this.userService.getUserData().account.paymentModel;
        this.viewportBreakpoint = this.deviceService.viewportBreakpoint;
        this.subs.push(this.deviceService.onResize.subscribe((message) => {
            if (message.breakpointChange) {
                this.viewportBreakpoint = message.breakpointChange.current;
            }
        }));


        this.debugService.initConsoleCommands();
    }

    async ngOnInit() {
        this.titleService.setTitle('dashboard.page_title');
        this.dashboardService.setDashboardState(true);
        this.tidioService.changeVisibility(true);

        const accountStatus = this.userService.getUserData().account.accountStatus;

        switch (accountStatus) {
            case 'ACCOUNT_DEBT_LOCK':
                this.setActiveModal(ModalType.ACCOUNT_DEBT_LOCK);
                break;
            case 'ACCOUNT_SOFT_LOCK':
                this.setActiveModal(ModalType.ACCOUNT_SOFT_LOCK);
                break;
            case 'SUBSCRIPTION_EXPIRED':
                this.setActiveModal(ModalType.SUBSCRIPTION_EXPIRED);
                break;
            case 'ACTIVE':
            case 'OTHER':
                await this.RunActiveUserActions();
                break;
            default:
                this.executeNewUserPipeline();
        }
    }

    onDownloadNeorideClick() {
        var platform = this.getDevicePlatform();
        let url = 'https://www.neoride.com/';
        
        if (platform === 'iOS') {
            url = 'https://apps.apple.com/us/app/neoride-easy-toll-payments/id1545182574';
        } else if (platform === 'Android') {
            url = 'https://play.google.com/store/apps/details?id=com.neology.vado';
        }
        
        // Open in new tab to preserve session state
        window.open(url, '_blank');
        // window.open(url, '_self');
    }
    getDevicePlatform(){
        var userAgent = navigator.userAgent || navigator.vendor;

        if (/iPad|iPhone|iPod/.test(userAgent)) {
            return 'iOS';
        }

        if (/android/i.test(userAgent)) {
            return 'Android';
        }

        return 'Web';
    };

    ngOnDestroy(): void {
        this.subs.forEach(sub => sub.unsubscribe());
        this.dashboardService.setDashboardState(false);
        this.tidioService.changeVisibility(false);
    }

    private subscribeToFlowEvents() {
        if (this.flowEventsSubscription$) return; // prevent double subscription
        this.flowEventsSubscription$ = this.registrationFlowGlobalStateService.flowEvents$.subscribe((event: AddSubscriptionFlowEvent) => {
            switch (event.name) {
                case 'subscriptionSelection':
                    this.showSubscriptionSelectModal(event.data?.subscription_plan_id);
                    break;
                case 'paymentMethodSelection':
                    this.setSubscriptionPaymentError(event.data);
                    this.showPaymentMethodSelectModal();
                    break;
                case 'subscriptionConfirmation':
                    this.showSubscriptionPaymentPreviewModal();
                    break;
                case 'subscriptionAcknowledgement':
                    this.showSubscriptionAcknowledgement(event.data);
                    break;
                case 'pendingLicensePlates':
                    this.openPendingLPNsDialog();
                    break;
                case 'licensePlateAddedAcknowledgement':
                    this.showFleetResultMessage(fleetMessages.ok);
                    break;
                case 'licensePlateDeclinedAcknowledgement':
                    this.showFleetResultMessage(fleetMessages.declined);
                    break;
                case 'vehicles':
                    this.isShowAddVehicleModalAfterLoginService.setToShow();
                    this.router.navigateByUrl('/dashboard/profile/vehicles');
                    break;
                case "membership":
                    break;
                default:
                    this.router.navigateByUrl('/dashboard');
            }
        });
        this.subs.push(this.flowEventsSubscription$);
    }

    async RunActiveUserActions() {
        try {
            // Step 1: Fetch flow type and pending LPNs concurrently
            const [flowTypeResult] = await Promise.all([
                this.registrationFlowTypeService.getFlowType(),
                this.getPendingLPNS()
            ]);

            // Step 2: Set flow type and handle "pay per bundle" flow
            this.registrationFlowGlobalStateService.setFlowType(flowTypeResult);
            if (this.registrationFlowGlobalStateService.isPayPerBundle()) {
                if (!this.userService.isAccountActive()) {
                    // New user: run onboarding flow (which will subscribe after registration dialog)
                    this.executePayPerBundleFlow();
                    // After onboarding, ensure modals are closed and show add vehicle or welcome screen
                    // (Implement showAddVehicleOrWelcomeScreen as needed)
                    // this.closeAllModals();
                    // this.showAddVehicleOrWelcomeScreen();
                } else {
                    // Existing user: just subscribe to flow events
                    this.subscribeToFlowEvents();
                    await this.handlePayPerCarFlow();
                }
            }

            // Step 3: Fetch payment configuration
            this.paymentConfig = await this.fetchPaymentConfigSafe();

            // Step 4: Handle Pay-Per-Car Flow
            // await this.handlePayPerCarFlow();
            } catch (error) {
                console.error('Error in RunActiveUserActions:', error);
            }
        }

    private async fetchPaymentConfigSafe(): Promise<any> {
        try {
            return await firstValueFrom(this.paymentService.fetchPaymentConfig());
        } catch {
            return null;
        }
    }

    private async handlePayPerCarFlow() {
        // Fetch active user license plates
        const activeUserLicensePlates = await firstValueFrom(this.licensePlatesService.getCountOfActiveLPNs());
        // Check if payment method type is DCB
        if (this.paymentConfig?.payment_method_type === 'DCB') {
            this.isHidePaymentMethodSelectCancelButton = false;
            this.paymentMethodPopupMode = 'change';
            this.activeModal = 'payment-method';
        }
        // Handle pending LPNs
        const pendingLPNsListNotEmpty = this.pendingLPNResponse?.plates?.length > 0;
        if (pendingLPNsListNotEmpty) {
            this.openPendingLPNsDialog();
            return;
        }
        // Show modal if user has no active vehicles
        const isUserNotHaveActiveVehicles = activeUserLicensePlates.active < 1;
        if (isUserNotHaveActiveVehicles) {
            this.isShowAddVehicleModalAfterLoginService.setToShow();
            this.isShowAddVehicleModalAfterLoginService.checkAndShow();
        }
    }


    public openPendingLPNsDialog() {
        this.fleetPendingToPayLPNsSubscription$ = this.confirmFleetPaymentService.newPendingLicensePlatesListToPay$.subscribe(
            (data) => {
                if (data) {
                    this.onConfirmFleetPayment(data).then(_r => null);
                }
            }
        );

        this.fleetPendingPayDialog = this.dialog.open(FleetLpnRegisterComponent, {
            minWidth: '300px',
            data: null
        });

        this.fleetPendingPayDialog.componentInstance.add.subscribe((_event: FleetLpRegistrationEvent) => {
            console.log("Fleet Pending LP add() handler")
            this.closePendingLPNsPayDialog();
            this.registrationFlowGlobalStateService.navigateLicensePlateAddedAcknowledgement();
        })

        this.fleetPendingPayDialog.componentInstance.cancel.subscribe((_event: FleetLpRegistrationEvent) => {
            console.log("Fleet Pending LP cancel() handler")
            this.closePendingLPNsPayDialog();
            this.registrationFlowGlobalStateService.navigateLicensePlateDeclinedAcknowledgement();
        })
    }


    /*
    * if user don`t have subscription we need to run subscription selection and payment flow
    *
    * */
    executePayPerBundleFlow() {
        // First check if user is new
        // if (!this.userService.isNewUser()) {
        //     // For existing users, just navigate to dashboard
        //     this.router.navigateByUrl('/dashboard');
        //     return;
        // }
        console.log('Calling isAccountActive:', this.userService.isAccountActive()); 
        if (this.userService.isAccountActive()) {
            this.router.navigateByUrl('/dashboard/invoices');
            return;
        }

        // For new users, show registration flow
        const registrationDialog = this.dialog.open(RegistrationWelcomeComponent, {
            minWidth: '300px',
            maxWidth: '400px',
            disableClose: true,
            hasBackdrop: true
        });

        // Subscribe to Global Flow Events only after registration dialog is closed
        registrationDialog.closed.subscribe(() => {
            // Subscribe to flow events and show subscription dialog
            this.flowEventsSubscription$ = this.registrationFlowGlobalStateService.flowEvents$.subscribe((event: AddSubscriptionFlowEvent) => {
                switch (event.name) {
                    case 'subscriptionSelection':
                        this.showSubscriptionSelectModal(event.data?.subscription_plan_id);
                        break;
                    case 'paymentMethodSelection':
                        this.setSubscriptionPaymentError(event.data);
                        this.showPaymentMethodSelectModal();
                        break;
                    case 'subscriptionConfirmation':
                        this.showSubscriptionPaymentPreviewModal();
                        break;
                    case 'subscriptionAcknowledgement':
                        this.showSubscriptionAcknowledgement(event.data);
                        break;
                    case 'pendingLicensePlates':
                        this.openPendingLPNsDialog();
                        break;
                    case 'licensePlateAddedAcknowledgement':
                        this.showFleetResultMessage(fleetMessages.ok);
                        break;
                    case 'licensePlateDeclinedAcknowledgement':
                        this.showFleetResultMessage(fleetMessages.declined);
                        break;
                    case 'vehicles':
                        this.isShowAddVehicleModalAfterLoginService.setToShow();
                        this.router.navigateByUrl('/dashboard/profile/vehicles');
                        break;
                    case "membership":
                        break;
                    default:
                        this.router.navigateByUrl('/dashboard');
                }
            });

            this.subs.push(this.flowEventsSubscription$);

            // After registration dialog closes, trigger subscription selection
            setTimeout(() => {
                this.registrationFlowGlobalStateService.navigateSubscriptionSelection();
            }, 300);
        });

        // Initialize subscription data
        forkJoin({
            currentSubscription: this.subscriptionApiService.getCurrentSubscription(),
        }).subscribe(({currentSubscription}) => {
            this.flowConfig = {
                currentSubscription,
            };
            this.registrationFlowGlobalStateService.setFlowInitCompleted();
        });
    }

    private isNavigateFlowOnInit() {
        const url = this.router.url;
        return !url.includes("paypal-redirect");
    }

    showSubscriptionSelectModal(selectedPlanId: string) {
        const data: SubscriptionSelectionDialogData = {
            selectedPlanId: selectedPlanId
        }
        this.dialog.open(SubscriptionSelectComponent, {
            minWidth: '300px',
            maxWidth: '400px',
            data: data
        })
    }

    showSubscriptionAcknowledgement(data: SubscriptionAcknowledgementDialogData) {
        this.dialog.open(SubscriptionAcknowledgementComponent, {
            minWidth: '300px',
            maxWidth: '400px',
            data: data
        })
    }

    executeNewUserPipeline() {
        this.registrationFlowTypeService.getFlowType().then((flowType: userRegistrationFlowType) => {
            this.registrationFlowGlobalStateService.setFlowType(flowType);
            this.executeUserRegistrationFlowByType(flowType);
        })
    }


    /*
    * active user can have 3 ways after the registration
    * 1. NO_PAY_CAR for users with old registration model without registration payment
    * 2. PAY_PER_CAR for users with old registration model with registration payment
    * 3. PAY_PER_BUNDLE for users with new registration model with subscription payment
    * after user login we need to check the flow type and execute the flow
    * */

    private executeUserRegistrationFlowByType(flowType: userRegistrationFlowType) {
        switch (flowType) {
            case userRegistrationFlowType.NO_PAY_CAR:
                this.executeRegularUserFlow().then(_ => null);
                break;
            case userRegistrationFlowType.PAY_PER_CAR:
                this.executeRegularUserFlow().then(_ => null);
                break;
            case userRegistrationFlowType.PAY_PER_BUNDLE:
                this.executePayPerBundleFlow();
                break;
            default:
                break;
        }
    }

    // TODO this method should be spit in two : for NO_PAY_CAR and PAY_PER_CAR
    async executeRegularUserFlow() {
        const currentUrl: URL = new URL(window.location.href);
        const actionFromUrlParam: string = currentUrl.searchParams.get('action');

        const paymentActions = [
            'veh_pbm_paypal_payment_complete',
            'veh_pbm_paypal_payment_cancel',
            'veh_fleet_lpn_ppp_complete',
            'veh_fleet_lpn_ppp_cancel',
        ];

        const isNewUserWithoutUrlAction = this.userService.isNewUser() && !paymentActions.includes(actionFromUrlParam);

        if (actionFromUrlParam) {
            await this.handleUrlAction(currentUrl, actionFromUrlParam);
        } else if (isNewUserWithoutUrlAction) {
            await this.executeNewUserFlow();
        }
    }

    async handleUrlAction(currentUrl: URL, action: string) {
        if (['pbm_paypal_payment_complete', 'pbm_paypal_payment_cancel'].includes(action)) {
            await this.runPBMPaypalAction(currentUrl, action);
        } else if (['fleet_lpn_ppp_complete', 'fleet_lpn_ppp_cancel'].includes(action)) {
            await this.runFleetLPNAction(currentUrl, action);
        }

        this.location.replaceState('/dashboard/invoices');
    }

    async executeNewUserFlow(): Promise<void> {
        const paymentConfig = await firstValueFrom(this.paymentService.fetchPaymentConfig());
        const isSetupComplete = paymentConfig?.setup_complete;

        const isPostpaidPaymentModelActive = this.isActivePaymentModel(PaymentModels.POSTPAID);
        const isFleetPaymentModelActive = this.isActivePaymentModel(PaymentModels.FLEET);

        const shouldInitializePostpaidModel = isPostpaidPaymentModelActive && (!paymentConfig || isSetupComplete);
        const shouldInitializeFleetModel = isFleetPaymentModelActive && paymentConfig && isSetupComplete;

        if (shouldInitializePostpaidModel) {
            await this.initUserByPostpaidModel();
            return;
        }

        if (shouldInitializeFleetModel) {
            await this.initUserByFleetModel();
            return;
        }

        this.showPaymentMethodSelectModal();
    }


    private isActivePaymentModel(model: PaymentModels) {
        return this.tollAuthorityPaymentModel === model;
    }

    private async runFleetLPNAction(currentUrl: URL, action: string) {
        const result = this.decodeUrlToJson(currentUrl.searchParams.get('fleet_lpn_ppp_result'));

        if (result) {
            const transactionId = currentUrl.searchParams.get('transaction_id');

            if (transactionId && action === 'fleet_lpn_ppp_complete') {
                await firstValueFrom(this.paymentService.completePaymentIntent(transactionId)).catch(() => false);
            }

            this.welcomeMessageData = result.messageData;
            this.showFleetResultMessage(result.messageKey);
        }
    }

    private async runPBMPaypalAction(currentUrl: URL, action: string) {
        const pbmPaypalPaymentResult = currentUrl.searchParams.get('pbm_paypal_payment_result');
        const paymentResultFromUrl = this.decodeUrlToJson(pbmPaypalPaymentResult);

        if (paymentResultFromUrl) {
            // welcomeMessageData contains information necessarily for showing welcome message
            this.pbmData = paymentResultFromUrl.pbmData;
            this.welcomeMessageData = paymentResultFromUrl.messageData;

            if (action === 'pbm_paypal_payment_cancel') {
                // нужно показать сообщение такое же ка до начала платежа
                //await this.declinePBM(this.pbmData, 'paypal payment canceled or failed');
                this.initUserByPostpaidModel().then(_ => null);

            }

            if (action !== 'pbm_paypal_payment_cancel') {
                this.showWelcomeMessage(paymentResultFromUrl.messageKey);
            }

            const transactionId = currentUrl.searchParams.get('transaction_id');

            if (transactionId && action === 'pbm_paypal_payment_complete') {
                this.paymentService.completePaymentIntent(transactionId).toPromise().catch(() => false);
            }
        }
    }

    async initUserByPostpaidModel(): Promise<boolean> {
        const pbmData: PayByMailData = await firstValueFrom(this.paymentService.fetchPayByMail()).catch(() => null);

        if (this.userService.isRegNPay() || pbmData && pbmData.pbm_id) {
            this.executePBM(pbmData).then(_ => null);
            return true;
        }

        return false;
    }

    showPaymentMethodSelectModal() {
        this.setActiveModal(ModalType.PAYMENT_METHOD);
    }

    setSubscriptionPaymentError(error?: Error) {
        if (error) {
            this.subscriptionPaymentError = error;
        } else {
            return;
        }
    }

    hidePaymentMethodPopup() {
        this.setActiveModal(null);
    }

    async onPaymentMethodSelected(event: PaymentMethodDoneEvent) {
        if (event && event.paymentConfig) {
            try {
                this.registrationFlowGlobalStateService.setSelectedPaymentConfig(event.paymentConfig);
                if (this.paymentMethodPopupMode === 'setup') {
                    return await this.handlePaymentMethodSelectSetupMode(event);
                }
                if (this.paymentMethodPopupMode === 'change') {
                    return await this.handlePaymentMethodSelectChangeMode(event);
                }
            } catch (error) {
                console.error('Error in onPaymentMethodSelected:', error);
            }
        } else {
            this.hidePaymentMethodPopup();
        }
    }

    private async handlePaymentMethodSelectSetupMode(event: PaymentMethodDoneEvent) {
        if (this.isActivePaymentModel(PaymentModels.POSTPAID)) {
            const isPBMExecuted = await this.initUserByPostpaidModel();
            if (!isPBMExecuted) {
                this.hidePaymentMethodPopup();
            }
            return;
        }

        if (this.isActivePaymentModel(PaymentModels.FLEET) && event.isOk &&
            await this.paymentService.checkCurrentPaymentMethod(event.paymentConfig)) {
            this.hidePaymentMethodPopup();

            if (this.registrationFlowGlobalStateService.isPayPerBundle()) {
                this.registrationFlowGlobalStateService.navigateSubscriptionConfirmation();
            } else {
                await this.initUserByFleetModel();
            }

        } else {
            this.hidePaymentMethodPopup();
            defer(() => this.showPaymentMethodSelectModal());
        }
    }

    private async handlePaymentMethodSelectChangeMode(event: PaymentMethodDoneEvent) {
        if (event.isOk && await this.paymentService.checkCurrentPaymentMethod(event.paymentConfig)) {
            this.paymentConfig = event.paymentConfig;
            await this.initUserByFleetModel();
        } else {
            this.onShowChangePaymentMethodPopup();
        }
    }


    async fetchRequiredDataForPBM(): Promise<[Stripe, PaymentConfig, number]> {
        return await Promise.all([
            this.stripeService.getStripeInstance(),
            this.paymentService.fetchPaymentConfig().toPromise(),
            this.paymentService.fetchHoursToPay().toPromise(),
        ]).catch(() => null);
    }

    async verifyPaymentMethod(pbmData: PayByMailData, paymentConfig: PaymentConfig): Promise<boolean> {
        return await this.paymentService.checkCurrentPaymentMethod(paymentConfig, null, {
            amount: pbmData.amount,
            currency: pbmData.currency
        }).catch(() => false);
    }

    async handleFailedPBMVerification(pbmData: PayByMailData, reason: string): Promise<void> {
        await this.declinePBM(pbmData, reason);
        this.showWelcomeMessage('dashboard.welcome.message_205');
    }

    handlePBMData(pbmData: PayByMailData, paymentConfig: PaymentConfig): void {
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

        this.asyncScriptLoader.loadScript();
    }

    async executePBM(pbmData: PayByMailData): Promise<void> {
        const response: [Stripe, PaymentConfig, number] = await this.fetchRequiredDataForPBM();

        if (!pbmData || pbmData.status !== 'OK' || !pbmData.pbm_id || !response) {
            this.showWelcomeMessage('dashboard.welcome.message_default');
            console.warn('Something wrong with PBM init');
            return;
        }

        const [stripe, paymentConfig, hoursToPay] = response;

        this.stripeInstance = stripe;
        this.welcomeMessageData.hoursToPay = hoursToPay;

        const isPaymentMethodOk = await this.verifyPaymentMethod(pbmData, paymentConfig);

        if (!isPaymentMethodOk) {
            await this.handleFailedPBMVerification(pbmData, 'something wrong with payment method');
            return;
        }

        const isAmountLessThanMin = pbmData.amount < paymentConfig.min_payment_amount;
        const isAmountGreaterThanMax = pbmData.amount > paymentConfig.max_payment_amount;

        if (isAmountLessThanMin || isAmountGreaterThanMax) {
            await this.handleFailedPBMVerification(pbmData, 'limits');
            return;
        }

        this.handlePBMData(pbmData, paymentConfig);

        const isPaymentByMobileWallet: boolean = paymentConfig.payment_method_type === 'GOOGLEPAY' || paymentConfig.payment_method_type === 'APPLEPAY';
        if (isPaymentByMobileWallet) {
            await this.preparePaymentByMobileWallet();
        } else {
            this.showPaymentPopup();
        }
    }


    async declinePBM(payByMailData: PayByMailData, reason: string = null): Promise<void> {
        const response = await this.paymentService.sendPaymentRequest({
            pbmId: payByMailData.pbm_id,
            makePayment: false,
        }, this.paymentConfig);

        if (response.status === 'OK') {
            console.warn(`PBM rejected (reason: ${reason})`);
        } else {
            console.warn(`PBM must be rejected (reason: ${reason}) but an error occurred`)
        }
    }

    showWelcomeError(errorCode: number) {
        switch (errorCode) {
            case 203:
            case 205:
            case 307:
                this.showWelcomeMessage(`dashboard.welcome.message_${errorCode}`);
                return;
        }

        this.showWelcomeMessage('dashboard.welcome.message_205');
    }

    showWelcomeMessage(welcomeMessageKey: string) {
        // call fetchLicensePlates after makePaymentByEmail
        this.licensePlatesService.getAllLicensePlates()
            .toPromise()
            .catch(() => [])
            .then((licensePlatesResponse: AllLicensePlatesHttpResponse) => {
                licensePlatesResponse.plates = (licensePlatesResponse.plates || []);
                const isLicenseListMultiple = licensePlatesResponse.plates &&
                    licensePlatesResponse.plates.length > 1;

                if (isLicenseListMultiple) {
                    licensePlatesResponse.plates = this.licensePlatesService.sortLicensePlatesByRegistrationDate(licensePlatesResponse.plates);
                }

                const lp = licensePlatesResponse.plates[0] || null;

                if (lp) {
                    this.welcomeMessageData.licensePlates = `<strong>${lp.lps}&nbsp;${lp.lpn}</strong>`;
                } else {
                    this.welcomeMessageData.licensePlates = null;
                }

                this.welcomeMessageKey = welcomeMessageKey;
                this.setActiveModal(ModalType.WELCOME);
            });
    }

    hideWelcomeMessage() {
        this.setActiveModal(null);
        this.router.navigateByUrl('/dashboard/profile/vehicles');
    }

    // -----------------------------------

    showPaymentPopup() {
        this.resetPaymentPopup();
        this.setActiveModal(ModalType.PAYMENT);
    }

    async onSubmitPayment(makePayment: boolean) {
        if (this.paymentSubmittingBy) {
            return;
        }

        this.paymentSubmittingBy = makePayment ? 'yes' : 'no';

        if (!makePayment) {
            await this.declinePBM(this.pbmData, 'declined by user');
            this.showWelcomeMessage('dashboard.welcome.message_declined');
            return;
        }

        const paymentMethodActions = {
            'DCB': async () => await this.payByCarrier(),
            'PAYPAL': async () => await this.payByPayPal(),
            'DEBIT_CARD': async () => await this.payByPlasticCard(),
            'CREDIT_CARD': async () => await this.payByPlasticCard(),
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

    async payByPayPal() {
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

        const returnUrl = `/dashboard/invoices?action=pbm_paypal_payment_complete&pbm_paypal_payment_result=${successResultData}`;
        const cancelUrl = `/dashboard/invoices?action=pbm_paypal_payment_cancel&pbm_paypal_payment_result=${cancelResultData}`;

        const response = await this.paymentService.sendPaymentRequest({
            pbmId: this.pbmData.pbm_id,
            makePayment: true,
            returnUrl: returnUrl,
            cancelUrl: cancelUrl,
        }, this.paymentConfig);

        const payPalRenderPageUrl = response?.payment_intent?.approve_payment_url;

        if (this.isDeclinedPBMPaymentResponse(response) || !payPalRenderPageUrl) {
            await this.declinePBM(this.pbmData, 'fetch paypal order error');
            this.showWelcomeError(response && response.errorCode || 205);
        } else {
            window.location.assign(payPalRenderPageUrl);
        }
    }

    async payByCarrier() {
        const zipCode: string = this.isPaymentZipRequired ? (this.zipCode || '').trim() : null;
        const intentResponse = await this.paymentService.sendPaymentRequest({
            pbmId: this.pbmData.pbm_id,
            makePayment: true,
            verificationCode: zipCode,
        }, this.paymentConfig);

        console.warn(intentResponse);

        if (intentResponse.status === 'OK') {
            this.showWelcomeMessage('dashboard.welcome.message_approved');
        } else {
            this.showWelcomeError(intentResponse && intentResponse.errorCode || 205);
        }
    }

    async payByVenmo() {
        const response = await this.paymentService.sendPaymentRequest({
            pbmId: this.pbmData.pbm_id,
            makePayment: true,
        }, this.paymentConfig);

        if (this.isDeclinedPBMPaymentResponse(response)) {
            await this.declinePBM(this.pbmData, 'failed to pay pbm with venmo');
            this.showWelcomeError(response && response.errorCode || 205);
            return;
        }

        this.showWelcomeMessage('dashboard.welcome.message_approved');
    }

    async payByPlasticCard() {
        const response = await this.paymentService.sendPaymentRequest({
            pbmId: this.pbmData.pbm_id,
            makePayment: true,
        }, this.paymentConfig);

        if (this.isDeclinedPBMPaymentResponse(response)) {
            await this.declinePBM(this.pbmData, 'fetch payment intent error');
            this.showWelcomeError(response && response.errorCode || 205);
            return;
        }

        // Payment done w/o 3D secure
        if (response.payment_complete) {
            this.showWelcomeMessage('dashboard.welcome.message_approved');
            return;
        }

        const paymentIntent = response.payment_intent;

        // There is payment intent with status !== 'succeeded'
        // 3D secure required
        const confirmCardResponse: PaymentIntentResponse = await this.stripeInstance.confirmCardPayment(paymentIntent.client_secret).catch(() => null);

        if (!confirmCardResponse || confirmCardResponse.error) {
            console.warn(confirmCardResponse);
            await this.declinePBM(this.pbmData, '3D Secure failed');
            this.showWelcomeMessage('dashboard.welcome.message_205');
            return;
        }

        const isOk = await this.paymentService.completePaymentIntent(response.transaction_id).toPromise().catch(() => false);

        if (isOk) {
            this.showWelcomeMessage('dashboard.welcome.message_approved');
            return;
        }

        // Unexpected state or 3D secure fail
        this.showWelcomeMessage('dashboard.welcome.message_205');
    }

    private isDeclinedPBMPaymentResponse(response: MakePaymentByEmailResponse) {
        return !response || response.status !== 'OK';
    }

    async preparePaymentByMobileWallet() {

        const {paymentRequest} = await this.stripeService.getMobileWalletPaymentRequest({
            amount: this.pbmData.amount,
            currency: this.pbmData.currency,
            label: 'Total',
        });

        paymentRequest.on('paymentmethod', async (e) => {
            // [POST /pay-by-mail/<pbm_id>]
            const intentResponse: MakePaymentByEmailResponse = await this.paymentService.sendPaymentRequest({
                pbmId: this.pbmData.pbm_id,
                makePayment: true,
            }, this.paymentConfig);

            if (this.isDeclinedPBMPaymentResponse(intentResponse) || intentResponse.errorCode || !intentResponse.payment_intent) {
                e.complete('fail');
                await this.declinePBM(this.pbmData, 'fetch payment intent error');
                this.showWelcomeError(intentResponse && intentResponse.errorCode || 205);
                return;
            }

            const paymentIntent = intentResponse.payment_intent;
            const confirmResponse = await this.stripeInstance.confirmCardPayment(paymentIntent.client_secret, {
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

            const isRequiresAction: boolean = confirmResponse.paymentIntent.status === 'requires_action';
            if (isRequiresAction) {
                const confirmResult: PaymentIntentResponse = await this.stripeInstance.confirmCardPayment(paymentIntent.client_secret);

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

        paymentRequest.on('cancel', async () => {
            await this.declinePBM(this.pbmData, 'wallet payment canceled');
            this.showWelcomeMessage('dashboard.welcome.message_205');
        });

        this.mobileWalletPaymentAttrs = {paymentRequest};
        this.showPaymentPopup();
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

    async initUserByFleetModel() {
        await this.getPendingLPNS();

        const isUserHasPendingLPNs = (this.pendingLPNResponse?.plates || []).length > 0;

        if (isUserHasPendingLPNs) {

            const response: [Stripe, number] = await Promise.all([
                this.stripeService.getStripeInstance(),
                firstValueFrom(this.paymentService.fetchHoursToPay())
            ]).catch(() => null);

            if (!response) {
                console.warn('Failed to get Stripe or hoursToPay');
                return;
            }

            const [stripe, hoursToPay] = response;

            this.stripeInstance = stripe;
            this.welcomeMessageData.hoursToPay = hoursToPay;

            this.setActiveModal(null);
            this.openPendingLPNsDialog();
        } else {
            this.pendingLPNResponse = null;
            this.setActiveModal(null);
        }
    }

    private async getPendingLPNS() {
        this.pendingLPNResponse = await firstValueFrom(this.licensePlatesService.getPendingLPNs());
    }

    async onConfirmFleetPayment(data: EmmitNewPendingLicensePlatesListToPayParams) {
        const listOfSelectedLPNs = data ? data.listOfLPns : null;
        const listOfSelectedLPNsNames = data ? data.lpnNames : null;

        if (this.fleetPaymentState.confirming || !this.pendingLPNResponse) {
            return;
        }

        this.fleetPaymentState.confirming = true;

        const [stripeInstance, paymentConfig, hoursToPay] = await Promise.all([
            this.stripeService.getStripeInstance(),
            firstValueFrom<PaymentConfig>(this.paymentService.fetchPaymentConfig()),
            firstValueFrom<number>(this.paymentService.fetchHoursToPay())
        ]).catch(() => [null, null]);

        if (!stripeInstance || !paymentConfig) {
            this.fleetPaymentState.confirming = false;
            this.pendingLPNResponse = null;
            this.activeModal = null;
            return;
        }

        this.stripeInstance = stripeInstance;
        this.paymentConfig = paymentConfig;
        this.welcomeMessageData.hoursToPay = hoursToPay;

        const isZeroFee = this.pendingLPNResponse.fee <= 0;
        const isPaymentMethodOk = isZeroFee || (await this.paymentService.checkCurrentPaymentMethod(this.paymentConfig, null, {
            amount: this.selectedForPaymentPendingLPNsTotalSum,
            currency: 'USD'
        }).catch(() => false));

        if (!isPaymentMethodOk) {
            this.fleetPaymentState.confirming = false;
            this.pendingLPNResponse = null;
            this.showPaymentMethodSelectModal();
            return;
        }


        this.welcomeMessageData.licensePlates = listOfSelectedLPNsNames ? listOfSelectedLPNsNames.join(', ') : '';


        this.pendingLPNsInvoice = await firstValueFrom(this.licensePlatesService.acceptPendingLPNsWithRental(listOfSelectedLPNs)).catch(() => null);

        if (!this.pendingLPNsInvoice || !this.pendingLPNsInvoice.invoice_id || !this.pendingLPNsInvoice.invoice_items) {
            this.fleetPaymentState.confirming = false;
            this.pendingLPNResponse = null;
            this.showFleetResultMessage('dashboard.fleet.message_declined');
            return;
        }

        const requestData: InvoicePaymentRequestData = {
            invoices: this.getInvoiceForFleetPayment(),
            verification_code: null,
            payment_method_type: this.paymentConfig.payment_method_type,
            payment_method_id: this.paymentConfig.payment_method_id,
            return_url: null,
            cancel_url: null,
        };

        if (isZeroFee) {
            const {response: intentResponse} = await firstValueFrom(this.invoicesService.makePayment(requestData));

            this.fleetPaymentState.confirming = false;

            if (intentResponse?.payment_complete) {
                this.showFleetResultMessage(fleetMessages.ok);
            } else {
                this.showFleetResultMessage(fleetMessages.issues);
            }

            return;
        }
        this.makePaymentByType(this.paymentConfig.payment_method_type)
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
                this.payByPayPal();
                break;
            case 'DEBIT_CARD':
            case 'CREDIT_CARD':
                this.payByCardFleet()
                break;
            case 'GOOGLEPAY':
            case 'APPLEPAY':
                this.payByMobileWalletFleet()
                break;
            case 'VENMO':
                this.payByVenmoFleet()
                break;
        }

    }

    getInvoiceForFleetPayment(): InvoicePaymentInvoice[] {
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

    async payByPayPalFleet() {
        const successResultData = this.encodeJsonToUrl({
            messageKey: fleetMessages.ok,
            messageData: this.welcomeMessageData,
            isOk: true,
        });

        const cancelResultData = this.encodeJsonToUrl({
            messageKey: fleetMessages.issues,
            messageData: this.welcomeMessageData,
            isOk: false,
        });

        const requestData: InvoicePaymentRequestData = {
            invoices: this.getInvoiceForFleetPayment(),
            verification_code: null,
            payment_method_type: this.paymentConfig.payment_method_type,
            payment_method_id: this.paymentConfig.payment_method_id,
            return_url: `/dashboard/invoices?action=fleet_lpn_ppp_complete&fleet_lpn_ppp_result=${successResultData}`,
            cancel_url: `/dashboard/invoices?action=fleet_lpn_ppp_cancel&fleet_lpn_ppp_result=${cancelResultData}`,
        };

        const {
            response,
            errorCode
        } = <InvoicePaymentResponseWithError>await this.invoicesService.makePayment(requestData).toPromise().catch(error => error);

        const approveUrl = response?.payment_intent?.approve_payment_url;

        if (errorCode || !approveUrl) {
            // TODO: show_payment_method
            this.fleetPaymentState.confirming = false;
            // this.showFleetResultMessage('dashboard.fleet.message_issues');
            this.onShowChangePaymentMethodPopup();
        } else {
            window.location.assign(approveUrl);
        }
    }

    async payByCardFleet() {

        const requestData = {
            invoices: this.getInvoiceForFleetPayment(),
            verification_code: null,
            payment_method_type: this.paymentConfig.payment_method_type,
            payment_method_id: this.paymentConfig.payment_method_id,
            return_url: null,
            cancel_url: null,
        };

        const {
            response: intentResponse,
            errorCode
        } = await firstValueFrom(this.invoicesService.makePayment(requestData));

        if (errorCode) {
            // TODO: show_payment_method
            this.fleetPaymentState.confirming = false;
            // this.showFleetResultMessage('dashboard.fleet.message_issues');
            this.onShowChangePaymentMethodPopup();
            return;
        }

        const paymentIntent = intentResponse.payment_intent;

        if (intentResponse.payment_complete) {
            this.fleetPaymentState.confirming = false;
            this.showFleetResultMessage(fleetMessages.ok);
            return;
        }

        // Payment incomplete
        // -------------------------------------------------------

        const response: PaymentIntentResponse = await this.stripeInstance.confirmCardPayment(paymentIntent.client_secret).catch(() => null);

        if (!response) {
            this.fleetPaymentState.confirming = false;
            this.onShowChangePaymentMethodPopup();
            return;
        }

        if (response.error) {
            // TODO: show_payment_method
            this.fleetPaymentState.confirming = false;
            const error = this.stripeService.localizeStripeError(response.error);
            // this.showFleetResultMessage('dashboard.fleet.message_issues');
            this.onShowChangePaymentMethodPopup();
            console.warn('Failed to auth 3D secure:', response, error);
            return;
        }

        const isOkOrError = await firstValueFrom(this.paymentService.completePaymentIntent(intentResponse.transaction_id));

        this.fleetPaymentState.confirming = false;

        if (isOkOrError === true) {
            this.showFleetResultMessage(fleetMessages.ok);
        } else {
            // TODO: show_payment_method
            // this.showFleetResultMessage('dashboard.fleet.message_issues');
            this.onShowChangePaymentMethodPopup();
        }
    }

    async payByVenmoFleet() {
        const requestData: InvoicePaymentRequestData = {
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
        } = await firstValueFrom(this.invoicesService.makePayment(requestData));

        this.fleetPaymentState.confirming = false;

        // response.payment_complete = false;

        if (!errorCode && response.payment_complete) {
            this.showFleetResultMessage(fleetMessages.ok);
        } else {
            // TODO: show_payment_method
            // this.showFleetResultMessage('dashboard.fleet.message_issues');
            this.onShowChangePaymentMethodPopup();
        }
    }

    showFleetZipPopup() {
        this.fleetPaymentState.confirming = false;
        this.setActiveModal(ModalType.FLEET_LPN_ZIP);
    }

    validateFleetZipPopup() {
        this.fleetPaymentState.zipValid = (this.zipCode || '').trim().length >= 4;
    }

    async submitFleetZipPayment() {
        if (!this.fleetPaymentState.zipValid || this.fleetPaymentState.zipSubmitting) {
            return;
        }

        this.fleetPaymentState.zipSubmitting = true;

        const fleetZipPaymentRequestData: InvoicePaymentRequestData = {
            invoices: this.getInvoiceForFleetPayment(),
            verification_code: this.paymentConfig.payment_verification_required ? (this.zipCode || '').trim() : null,
            payment_method_type: this.paymentConfig.payment_method_type,
            payment_method_id: this.paymentConfig.payment_method_id,
            return_url: null,
            cancel_url: null,
        };

        const {errorCode} = await this.invoicesService.makePayment(fleetZipPaymentRequestData).toPromise().catch(error => error);

        this.fleetPaymentState.zipSubmitting = false;

        if (!errorCode) {
            this.showFleetResultMessage(fleetMessages.ok);
        } else {
            this.showFleetResultMessage(fleetMessages.issues);
        }
    }

    async payByMobileWalletFleet() {
        const walletType: PaymentMethodWallet = <PaymentMethodWallet>this.paymentConfig.payment_method_type;

        const walletFleetPaymentRequestData: InvoicePaymentRequestData = {
            invoices: this.getInvoiceForFleetPayment(),
            verification_code: null,
            payment_method_type: walletType,
            payment_method_id: this.paymentConfig.payment_method_id,
            return_url: null,
            cancel_url: null,
        };

        const {
            response: intentResponse,
            errorCode
        } = await firstValueFrom(this.invoicesService.makePayment(walletFleetPaymentRequestData)).catch(error => error);

        if (errorCode) {
            this.fleetPaymentState.confirming = false;
            this.onShowChangePaymentMethodPopup();
            return;
        }

        const paymentIntent = intentResponse.payment_intent;

        const {paymentRequest} = await this.stripeService.getMobileWalletPaymentRequest({
            amount: paymentIntent.amount,
            currency: paymentIntent.currency,
            label: 'Total',
        });

        if (!paymentRequest) {
            this.fleetPaymentState.confirming = false;
            this.onShowChangePaymentMethodPopup();
            return;
        }

        paymentRequest.on('paymentmethod', async (e) => {
            const confirmResponse: PaymentIntentResponse = await this.stripeInstance.confirmCardPayment(paymentIntent.client_secret, {
                payment_method: e.paymentMethod.id,
                setup_future_usage: 'off_session'
            }, {
                handleActions: false
            });

            if (confirmResponse.error) {
                // TODO: show_payment_method
                e.complete('fail');
                this.fleetPaymentState.confirming = false;
                const localizeStripeError = this.stripeService.localizeStripeError(confirmResponse.error);
                // this.showFleetResultMessage('dashboard.fleet.message_issues');
                this.onShowChangePaymentMethodPopup();
                console.warn('Failed:', localizeStripeError);
                return;
            }

            e.complete('success');

            let isPaymentSuccess = true;

            if (confirmResponse.paymentIntent.status === 'requires_action') {
                const confirmResult = await this.stripeInstance.confirmCardPayment(paymentIntent.client_secret);

                if (confirmResult.error) {
                    console.warn('Failed to auth 3D secure:', confirmResult.error);

                    if (confirmResponse.error.code === 'card_declined') {
                        // TODO: show_payment_method
                        this.fleetPaymentState.confirming = false;
                        const error = this.stripeService.localizeStripeError(confirmResult.error);
                        this.onShowChangePaymentMethodPopup();
                        // this.showFleetResultMessage('dashboard.fleet.message_issues');
                        console.warn('Failed:', error);
                        return;
                    }

                    isPaymentSuccess = false;
                }
            }

            if (isPaymentSuccess) {
                // tested in GPay walletName is 'googlePay' which is consistent with what server expects
                const walletName = this.paymentService.transformPaymentMethodName(e.paymentMethod.card.wallet.type);
                const paymentMethodId = e.paymentMethod.id
                if (walletName && paymentMethodId) {
                    await firstValueFrom(this.paymentService.setNewPaymentMethod({
                        payment_method_type: walletName,
                        payment_method_id: paymentMethodId
                    })).catch(() => null);
                }
                await firstValueFrom(this.paymentService.completePaymentIntent(intentResponse.transaction_id));
            }

            this.fleetPaymentState.confirming = false;

            if (isPaymentSuccess) {
                this.showFleetResultMessage(fleetMessages.ok);
            } else {
                // TODO: show_payment_method
                // this.showFleetResultMessage('dashboard.fleet.message_issues');
                this.onShowChangePaymentMethodPopup();
            }
        });

        paymentRequest.on('cancel', () => {
            this.fleetPaymentState.confirming = false;
            this.onShowChangePaymentMethodPopup();
        });

        if (this.stripeService.isSyncPaymentRequest()) {
            this.onShowWalletPaymentConfirmPopup(paymentRequest, paymentIntent, walletType);
        } else {
            paymentRequest.show();
        }
    }

    onShowWalletPaymentConfirmPopup(paymentRequest: any, paymentIntent: any, walletType: PaymentMethodWallet) {
        this.fleetPaymentState.confirming = false;
        this.fleetPaymentState.walletSubmitting = false;

        this.walletFleetPaymentAttrs = {
            amountFormatted: this.currencyService.format(paymentIntent.amount, paymentIntent.currency),
            wallet: this.stripeService.getWalletName(walletType),
            paymentRequest
        };

        this.setActiveModal(ModalType.FLEET_WALLET_PAYMENT_CONFIRM);
    }

    onConfirmFleetWalletPayment() {
        this.walletFleetPaymentAttrs.paymentRequest.show();
    }

    showFleetResultMessage(messageKey: string) {
        this.welcomeMessageKey = messageKey;
        this.setActiveModal(ModalType.WELCOME);
    }

    onShowChangePaymentMethodPopup() {
        this.paymentMethodPopupMode = 'change';
        this.setActiveModal(ModalType.PAYMENT_METHOD);
    }

    onPayDebt() {
        this.setActiveModal(null);
        this.router.navigateByUrl('/dashboard/invoices');
    }

    isCoverageVisible(): boolean {
        return true;  // this.userService.getUserData().account.paymentModel !== 'FLEET';
    }

    public isActiveModal(modalName: ModalsToShow): boolean {
        return modalName ? this.activeModal === modalName : false;
    }

    private setActiveModal(modalName: ModalsToShow) {
        if (this.fleetPendingPayDialog) {
            this.closePendingLPNsPayDialog();
        }
        this.activeModal = modalName;
    }

    private closePendingLPNsPayDialog(): void {
        this.fleetPendingToPayLPNsSubscription$?.unsubscribe();
        this.fleetPendingPayDialog?.componentInstance?.add?.unsubscribe()
        this.fleetPendingPayDialog?.componentInstance?.cancel?.unsubscribe();
        this.fleetPendingPayDialog?.close();
    }

    private isUserNotHasSelectedPaymentMethod() {
        return this.paymentConfig.setup_complete;
    }

    private showSubscriptionPaymentPreviewModal() {
        this.dialog.open(SubscriptionPaymentPreviewComponent, {
            width: '300px',
        });
    }

    showRegistrationWelcomeModal() {
        this.dialog.open(RegistrationWelcomeComponent, {
            minWidth: '300px',
            maxWidth: '400px'
        });
    }

}
