import {
    ChangeDetectionStrategy,
    Component, Input,
    OnDestroy,
    OnInit, Output,
    Renderer2,
    ViewChild,
    ViewEncapsulation,
    EventEmitter, ElementRef
} from '@angular/core';
import {Router} from '@angular/router';
import {TitleService} from '../../../../services/title.service';
import {DeviceService, ViewportBreakpoint} from '../../../../services/device.service';
import {Subscription, zip} from 'rxjs';
import {
    StripeService,
    WalletSupport,
} from '../../../../services/stripe.service';
import {
    CARD_TYPE_TO_FUNDING_MAP,
    CARD_TYPES,
    DCBStatus, FUNDING_TO_CARD_TYPE_MAP,
    PaymentCard,
    PaymentConfig, PaymentMethodCard,
    PaymentMethodType,
    PaymentOptions,
    PaymentService, UpdateVenmoResponse
} from '../../../../services/payment.service';
import {DomService} from '../../../../services/dom.service';
import {defer} from '../../../../lib/utils';
import {ToastService} from '../../../../services/toast.service';
import {BraintreeService} from '../../../../services/braintree.service';

type ActivePopup = 'method' | 'card' | 'card-delete' | 'venmo-delete';

interface SelectedPaymentMethod {
    type : PaymentMethodType;
    id : null | string;
}

interface UIMessage {
    key : string;
    data? : any;
}

export interface PaymentMethodDoneEvent {
    isOk : boolean;
    paymentConfig? : null | PaymentConfig;
}

export type PaymentMethodPopupMode = 'setup' | 'change' | 'edit';

interface PaymentCardItem {
    type : PaymentMethodCard;
    isAvailable : boolean;
    card : PaymentCard;
}

@Component({
    exportAs: 'paymentMethod',
    selector: 'payment-method',
    templateUrl: './payment-method.component.html',
    styleUrls: [ './payment-method.component.scss' ],
    changeDetection: ChangeDetectionStrategy.Default,
    encapsulation: ViewEncapsulation.None,
    host: {
        'class': 'payment-method'
    }
})
export class PaymentMethodComponent implements OnInit, OnDestroy {
    viewportBreakpoint : ViewportBreakpoint;

    subs : Subscription[] = [];

    activePopup : ActivePopup = null;

    paymentOptions : PaymentOptions;

    isAnyCardEnabled : boolean = false;

    cards : PaymentCardItem[] = [];

    hasCards : boolean = false;

    cardOptionLabelKey : string = null;

    addCardButtonCaptionKey : string = null;

    cardPopupHeaderKey : string = null;

    cardTypeErrorKey : string = null;

    paymentConfig : PaymentConfig;

    @Input()
    setupRedirectPath : string = '/dashboard/invoices';

    stripe : any = null;

    isReady : boolean = false;

    readonly cardBrands = {
        amex: 'American Express',
        diners: 'Diners Club',
        discover: 'Discover',
        jcb: 'JCB',
        mastercard: 'MasterCard',
        unionpay: 'UnionPay',
        visa: 'Visa',
        unknown: ''
    };

    readonly cardTypes = {
        credit: 'payment_method.card_type.credit',
        debit: 'payment_method.card_type.debit',
        prepaid: 'payment_method.card_type.prepaid',
        unknown: 'payment_method.card_type.unknown',
    };

    @Output()
    onPaymentMethodSelected = new EventEmitter<any>();

    @ViewChild('cardElement')
    cardElementRef : ElementRef;

    readonly stripeInputStyle = {
        base: {
            backgroundColor: '#fff',
            iconColor: '#3f444e',
            color: '#3f444e',
            fontWeight: '600',
            fontFamily: 'Montserrat, Helvetica Neue, sans-serif',
            fontSize: '14px',
            fontSmoothing: 'antialiased',
            // lineHeight: '18px',
            ':-webkit-autofill': {
                backgroundColor: '#fff',
                color: '#3f444e',
            },
            '::placeholder': {
                color: '#99a0aa',
            },
        },
        invalid: {
            iconColor: '#e64f4f',
            color: '#e64f4f',
        },
        complete: {
            backgroundColor: '#fff',
            ':-webkit-autofill': {
                backgroundColor: '#fff',
                color: '#3f444e',
            },
        }
    };

    readonly stripeInputClasses = {
        focus: 'payment-method__card-popup-input_focus',
        invalid: 'payment-method__card-popup-input_has-error',
    }

    @ViewChild('cardNumberNest')
    cardNumberNest : ElementRef = null;

    @ViewChild('cardExpireNest')
    cardExpireNest : ElementRef = null;

    @ViewChild('cardCVCNest')
    cardCVCNest : ElementRef = null;

    cardNumber : any = null;

    cardNumberState : any = null;

    hasCardNumberFocus : boolean = false;

    cardExpire : any = null;

    cardExpireState : any = null;

    hasCardExpireFocus : boolean = false;

    cardCVC : any = null;

    cardCVCState : any = null;

    hasCardCVCFocus : boolean = false;

    cardForm = {
        isAccepted: false
    };

    // ----------------------------------

    methodPopupState : 'init' | 'ready' | 'error';

    wallets : WalletSupport;

    isMethodPopupSubmitting : boolean = false;

    isCheckingDCBEligibility : boolean = false;

    selectedPaymentMethod : SelectedPaymentMethod = null;

    methodPopupError : UIMessage;

    methodHeader : UIMessage;

    // ----------------------------------

    cardPopupState : 'init' | 'ready' | 'error';

    cardPopupError : UIMessage;

    isCardPopupSubmitting : boolean = false;

    // ----------------------------------

    isCardDeletePopupSubmitting : boolean = false;

    cardToDelete : PaymentCard;

    isVenmoDeletePopupSubmitting : boolean = false;

    venmoAccountToDetach : string = null;

    isVenmoUpdating : boolean = false;

    // ----------------------------------

    @Input()
    mode : PaymentMethodPopupMode = 'setup';

    @Input()
    hideCancelButton : boolean = false;

    @Input()
    isSilentInit : boolean = false;

    @Output()
    onDone = new EventEmitter<PaymentMethodDoneEvent>();

    @Output()
    onShow = new EventEmitter<void>();

    @Output()
    onReady = new EventEmitter<void>();

    constructor (
        private renderer : Renderer2,
        private router : Router,
        private titleService : TitleService,
        private deviceService : DeviceService,
        private domService : DomService,
        private stripeService : StripeService,
        private paymentService : PaymentService,
        private braintreeService : BraintreeService,
        private toastService : ToastService,
    ) {
        window.scroll(0, 0);

        this.viewportBreakpoint = this.deviceService.viewportBreakpoint;
        this.subs.push(this.deviceService.onResize.subscribe((message) => {
            if (message.breakpointChange) {
                this.viewportBreakpoint = message.breakpointChange.current;
            }
        }));
    }

    ngOnInit () {
        this.init();
    }

    ngOnDestroy () : void {
        this.subs.forEach(sub => sub.unsubscribe());
        // TODO: stripe destroy?
    }

    async init () {
        this.stripe = await this.stripeService.getStripeInstance();

        if (this.isSilentInit) {
            await this.initMethodPopup();
            this.activePopup = 'method';
            this.onShow.emit();
            this.onReady.emit();
        } else {
            this.methodPopupState = 'init';
            this.activePopup = 'method';
            this.onShow.emit();
            this.initMethodPopup().then(() => {
                this.onReady.emit();
            });
        }
    }

    async initMethodPopup () : Promise<void> {
        return new Promise((resolve) => {
            this.methodPopupState = 'init';

            Promise.all([
                this.paymentService.fetchPaymentOptions().toPromise(),
                this.paymentService.fetchPaymentConfig().toPromise(),
                this.stripeService.getWalletPaymentRequest({
                    amount: 50,
                    currency: 'usd'
                })
            ]).then(([ paymentOptions, paymentConfig, wallet ]) => {
                // paymentOptions.DCB.status = 'UNKNOWN'; // TODO: DELETE!!!!
                // paymentConfig.payment_method_type = 'APPLEPAY'; // TODO: DELETE!!!!
                this.updatePaymentOptions(paymentOptions);
                this.paymentConfig = paymentConfig;
                this.wallets = wallet.wallets;

                this.updateSelectedPaymentMethod();
                this.setMethodPopupHeader();

                this.methodPopupState = 'ready';
            }).catch((e) => {
                console.warn('Error initMethodPopup:', e);
                this.methodPopupState = 'error';
            }).then(() => {
                resolve();
            });
        });
    }

    getCardsList (paymentOptions : null | PaymentOptions) : PaymentCardItem[] {
        if (!paymentOptions) {
            return [];
        }

        const knownCards : string[] = [];

        const cards : PaymentCardItem[] = CARD_TYPES.reduce((acc : PaymentCardItem[], cardType) => {
            const option = paymentOptions[cardType];

            option.cards.forEach(card => {
                if (knownCards.includes(card.id)) {
                    return;
                }

                const optionType = FUNDING_TO_CARD_TYPE_MAP[card.funding];
                const option = paymentOptions[optionType];

                acc.push({
                    type: optionType,
                    isAvailable: option?.enabled === true,
                    card
                });

                knownCards.push(card.id);
            });

            return acc;
        }, []);

        return cards.sort((a, b) => a.card.created - b.card.created);
    }

    updatePaymentOptions (paymentOptions : null | PaymentOptions) {
        const isDebitCardEnabled = paymentOptions?.DEBIT_CARD?.enabled === true;
        const isCreditCardEnabled = paymentOptions?.CREDIT_CARD?.enabled === true;

        this.paymentOptions = paymentOptions || null;
        this.isAnyCardEnabled = isDebitCardEnabled || isCreditCardEnabled;
        this.cards = this.getCardsList(paymentOptions);
        this.hasCards = this.cards.length > 0;

        if (isDebitCardEnabled && isCreditCardEnabled) {
            this.cardOptionLabelKey = 'payment_method.options.card';
            this.addCardButtonCaptionKey = 'payment_method.add_card';
            this.cardPopupHeaderKey = 'payment_method.card.card_header';
            this.cardTypeErrorKey = 'payment_method.error.credit_and_debit_only';
        } else if (isDebitCardEnabled) {
            this.cardOptionLabelKey = 'payment_method.options.card_debit';
            this.addCardButtonCaptionKey = 'payment_method.add_card_debit';
            this.cardPopupHeaderKey = 'payment_method.card.card_debit_header';
            this.cardTypeErrorKey = 'payment_method.error.debit_only';
        } else if (isCreditCardEnabled) {
            this.cardOptionLabelKey = 'payment_method.options.card_credit';
            this.addCardButtonCaptionKey = 'payment_method.add_card_credit';
            this.cardPopupHeaderKey = 'payment_method.card.card_credit_header';
            this.cardTypeErrorKey = 'payment_method.error.credit_only';
        } else {
            this.cardOptionLabelKey = null;
            this.addCardButtonCaptionKey = null;
            this.cardPopupHeaderKey = null;
            this.cardTypeErrorKey = null;
        }
    }

    setMethodPopupHeader () {
        switch (this.mode) {
            case 'setup':
                this.methodHeader = { key: 'payment_method.method_header.setup' };
                break;
            case 'change':
                if (this.paymentConfig && this.paymentConfig.setup_complete) {
                    this.methodHeader = { key: 'payment_method.method_header.change' };
                } else {
                    this.methodHeader = { key: 'payment_method.method_header.first_change' };
                }
                break;
            case 'edit':
                this.methodHeader = { key: 'payment_method.method_header.edit' };
                break;
        }
    }

    async setupCardElements () {
        const elements = await this.stripeService.createElements();

        return Promise.all([
            new Promise((resolve) => {
                this.cardNumber = elements.create('cardNumber', {
                    style: this.stripeInputStyle,
                    classes: this.stripeInputClasses
                });
                this.cardNumber.on('change', (event : any) => this.cardNumberState = event);
                this.cardNumber.on('ready', () => resolve());
                this.cardNumber.on('focus', () => this.hasCardNumberFocus = true);
                this.cardNumber.on('blur', () => this.hasCardNumberFocus = false);
                this.cardNumber.mount(this.cardNumberNest.nativeElement);
            }),
            new Promise((resolve) => {
                this.cardExpire = elements.create('cardExpiry', {
                    style: this.stripeInputStyle,
                    classes: this.stripeInputClasses
                });
                this.cardExpire.on('change', (event : any) => this.cardExpireState = event);
                this.cardExpire.on('ready', () => resolve());
                this.cardExpire.on('focus', () => this.hasCardExpireFocus = true);
                this.cardExpire.on('blur', () => this.hasCardExpireFocus = false);
                this.cardExpire.mount(this.cardExpireNest.nativeElement);

            }),
            new Promise((resolve) => {
                this.cardCVC = elements.create('cardCvc', {
                    style: this.stripeInputStyle,
                    classes: this.stripeInputClasses
                });
                this.cardCVC.on('change', (event : any) => this.cardCVCState = event);
                this.cardCVC.on('ready', () => resolve());
                this.cardCVC.on('focus', () => this.hasCardCVCFocus = true);
                this.cardCVC.on('blur', () => this.hasCardCVCFocus = false);
                this.cardCVC.mount(this.cardCVCNest.nativeElement);
            })
        ]);
    }

    onNewCardClick () {
        if (this.isMethodPopupSubmitting || this.isCheckingDCBEligibility) {
            return;
        }

        this.activePopup = 'card';
        this.cardPopupState = 'init';

        defer(() => {
            this.methodPopupError = null;

            this.setupCardElements().then(() => {
                this.resetCard();
                this.cardPopupState = 'ready';
            }).catch(() => {
                this.cardPopupState = 'error';
            });
        });
    }

    onDeleteCardClick (card : any, e : any) {
        console.log(card);
        this.domService.markEvent(e, 'cardDeleteClick');

        const isSelectedCard = this.selectedPaymentMethod.id === card.id;
        const isActiveMethod = this.paymentConfig.payment_method_id === card.id;

        if (this.isMethodPopupSubmitting || this.isCheckingDCBEligibility || isSelectedCard || isActiveMethod) {
            return;
        }

        this.methodPopupError = null;
        this.cardToDelete = card;
        this.activePopup = 'card-delete';
    }

    async onSubmitDeleteCard () {
        if (this.isCardDeletePopupSubmitting) {
            return
        }

        this.isCardDeletePopupSubmitting = true;

        const cardId = this.cardToDelete.id;
        const paymentConfig = await this.paymentService.deletePaymentMethod(cardId).toPromise().catch(() => null);

        if (paymentConfig) {
            this.paymentConfig = paymentConfig;

            const paymentOptions = await this.paymentService.fetchPaymentOptions().toPromise().catch(() => null);

            this.updatePaymentOptions(paymentOptions);
            this.updateSelectedPaymentMethod();
        } else {
            this.methodPopupError = {
                key: 'payment_method.error.card_delete_failed'
            };
        }

        this.activePopup = 'method';
        this.cardToDelete = null;
        this.isCardDeletePopupSubmitting = false;
    }

    onCancelDeleteCard () {
        this.activePopup = 'method';
        this.cardToDelete = null;
        this.isCardDeletePopupSubmitting = false;
    }

    setCardPopupSubmitting (isSubmitting : boolean) {
        this.isCardPopupSubmitting = isSubmitting;

        if (this.cardNumber) {
            this.cardNumber.update({ disabled: isSubmitting });
        }

        if (this.cardExpire) {
            this.cardExpire.update({ disabled: isSubmitting });
        }

        if (this.cardCVC) {
            this.cardCVC.update({ disabled: isSubmitting });
        }
    }

    async onSubmitCard () {
        if (this.isCardPopupSubmitting || !this.isCardValid()) {
            return;
        }

        this.cardPopupError = null;
        this.setCardPopupSubmitting(true);

        const clientSecret = await this.stripeService.fetchSetupIntent().toPromise().catch(() => null);

        if (!clientSecret) {
            this.cardPopupError = { key: 'stripe.error.common.generic' };
            this.setCardPopupSubmitting(false);
            return;
        }

        const setupCardResult = await this.stripe.confirmCardSetup(clientSecret, {
            payment_method: {
                card: this.cardNumber,
            },
        }).catch(() => null);

        if (!setupCardResult) {
            this.cardPopupError = { key: 'stripe.error.common.generic' };
            console.warn('Setup stripe.confirmCardSetup error');
            this.setCardPopupSubmitting(false);
            return;
        }

        if (setupCardResult.error) {
            this.cardPopupError = this.stripeService.localizeStripeError(setupCardResult.error);
            console.warn('Setup card error:', setupCardResult);
            this.setCardPopupSubmitting(false);
            return;
        }

        if (setupCardResult.setupIntent.status !== 'succeeded') {
            this.cardPopupError = { key: 'stripe.error.common.generic' };
            console.warn('Setup card unexpected state:', setupCardResult);
            this.setCardPopupSubmitting(false);
            return;
        }

        // DO NOT automatically attach newly created card to the customer
        // const paymentMethod : PaymentMethod = await this.paymentService.updatePaymentMethod({
        //     payment_method_type: 'card',
        //     payment_method_id: setupCardResult.setupIntent.payment_method
        // }).toPromise().catch(() => null);
        //
        // if (paymentMethod) {
        //     this.paymentMethod = paymentMethod;
        //     this.updateSelectedPaymentMethod();
        // } else {
        //     this.methodPopupError = {
        //         key: 'payment_method.error.new_card_not_attached'
        //     };
        // }

        const cardId : string = setupCardResult.setupIntent.payment_method;
        const cardType : null | PaymentMethodType = await this.paymentService.fetchPaymentMethodType(cardId).toPromise().catch(() => null);

        if (this.paymentOptions[cardType]?.enabled !== true) {
            await this.paymentService.deletePaymentMethod(cardId).toPromise().catch(() => null);
            this.cardPopupError = { key: this.cardTypeErrorKey };
            console.warn('Disallowed card type:', cardType);
            this.setCardPopupSubmitting(false);
            return;
        }

        const paymentOptions = await this.paymentService.fetchPaymentOptions().toPromise().catch(() => null);

        if (paymentOptions) {
            this.updatePaymentOptions(paymentOptions);
            this.updateSelectedPaymentMethod(cardId);
        } else {
            console.warn('Failed to update payment methods list after card was added');
        }

        this.setCardPopupSubmitting(false);
        this.destroyCard();
        this.activePopup = 'method';
    }

    onCancelCard () {
        this.destroyCard()
        this.activePopup = 'method';
    }

    destroyCard () {
        this.resetCard();

        if (this.cardNumber) {
            this.cardNumber.destroy();
            this.cardNumber = null;
        }

        if (this.cardExpire) {
            this.cardExpire.destroy();
            this.cardExpire = null;
        }

        if (this.cardCVC) {
            this.cardCVC.destroy();
            this.cardCVC = null;
        }

        this.cardNumberState = null;
        this.cardExpireState = null;
        this.cardCVCState = null;
    }

    resetCard () {
        this.cardPopupError = null;

        this.cardForm = {
            isAccepted: false
        };

        if (this.cardNumber) {
            this.cardNumber.clear();
        }

        if (this.cardExpire) {
            this.cardExpire.clear();
        }

        if (this.cardCVC) {
            this.cardCVC.clear();
        }
    }

    isCardValid () : boolean {
        return !!(
            this.cardForm.isAccepted &&
            this.cardNumberState &&
            !this.cardNumberState.error &&
            this.cardNumberState.complete &&
            this.cardExpireState &&
            !this.cardExpireState.error &&
            this.cardExpireState.complete &&
            this.cardCVCState &&
            !this.cardCVCState.error &&
            this.cardCVCState.complete
        );
    }

    onDCBMethodClick () {
        const status = this.paymentOptions.DCB.status;

        if (status === 'UNKNOWN') {
            this.onCheckDCBEligibility();
        } else if (status !== 'INELIGIBLE') {
            this.onMethodClick('DCB');
        }
    }

    onMethodClick (methodType : PaymentMethodType, methodId : null | string = null, e : any = null) {
        console.log(methodType, methodId);

        if (
            this.isMethodPopupSubmitting ||
            this.isCheckingDCBEligibility ||
            methodType === 'DCB' && ([ 'UNKNOWN', 'INELIGIBLE' ].includes(this.paymentOptions.DCB.status)) ||
            CARD_TYPES.includes(<PaymentMethodCard>methodType) && !this.paymentOptions[methodType].enabled ||
            [ 'GOOGLEPAY', 'APPLEPAY' ].includes(methodType) && (!this.paymentOptions.WALLET.enabled || !this.wallets || !this.wallets[methodType]) ||
            (e && (this.domService.hasEventMark(e, 'cardDeleteClick') || this.domService.hasEventMark(e, 'venmoActionClick')))
        ) {
            return;
        }

        console.warn('Change:', methodType, methodId);

        this.selectedPaymentMethod = {
            type: methodType,
            id: methodId
        };
    }

    async onSubmitMethod () {
        if (!this.canSubmitMethod()) {
            return;
        }

        this.methodPopupError = null;
        this.isMethodPopupSubmitting = true;

        if (this.selectedPaymentMethod.type === 'VENMO' && !this.selectedPaymentMethod.id) {
            const isVenmoConnectedOk = await this.onSubmitVenmo();

            if (!isVenmoConnectedOk) {
                this.isMethodPopupSubmitting = false;
                return;
            }
        }

        const paymentConfig : PaymentConfig = await this.paymentService.updatePaymentConfig({
            payment_method_type: this.selectedPaymentMethod.type,
            payment_method_id: this.selectedPaymentMethod.id
        }).toPromise().catch(() => null);

        if (paymentConfig) {
            this.paymentConfig = paymentConfig;

            const paymentOptions = await this.paymentService.fetchPaymentOptions().toPromise().catch(() => null);

            this.updatePaymentOptions(paymentOptions);
            this.updateSelectedPaymentMethod();

            this.onDone.emit({
                isOk: true,
                paymentConfig
            });
        } else {
            this.isMethodPopupSubmitting = false;
            this.methodPopupError = {
                key: 'payment_method.error.method_submit_failed'
            };
        }
    }

    async onSubmitVenmo () : Promise<boolean> {
        const venmoInstance : null | any = await this.braintreeService.createVenmoComponent();

        if (!venmoInstance) {
            this.methodPopupError = {
                key: 'payment_method.error.venmo_attach_failed'
            };
            return false;
        }

        if (!venmoInstance.isBrowserSupported()) {
            this.methodPopupError = {
                key: 'payment_method.error.venmo_attach_failed'
            };
            console.log('Browser does not support Venmo');
            return false;
        }

        // noinspection TypeScriptValidateJSTypes
        const payload : null | any = await venmoInstance.tokenize().catch((error) => {
            console.log('Failed to tokenize Venmo:', error);
            return null;
        });

        if (!payload) {
            this.methodPopupError = {
                key: 'payment_method.error.venmo_attach_failed'
            };
            return false;
        }

        console.log(payload);

        const response : UpdateVenmoResponse = await this.paymentService.updateVenmoPaymentMethod(payload.nonce).toPromise().catch(() => null);

        console.log(response);

        if (!response) {
            this.methodPopupError = {
                key: 'payment_method.error.venmo_attach_failed'
            };
            return false;
        }

        this.selectedPaymentMethod.type = 'VENMO';
        this.selectedPaymentMethod.id = null;  // response.payment_method_token;

        return true;
    }

    async onDetachVenmo (e : MouseEvent) {
        this.domService.markEvent(e, 'venmoActionClick');

        if (
            this.isMethodPopupSubmitting ||
            this.isCheckingDCBEligibility ||
            this.selectedPaymentMethod.type === 'VENMO' ||
            this.paymentConfig.payment_method_type === 'VENMO'
        ) {
            return;
        }

        this.methodPopupError = null;
        this.venmoAccountToDetach = this.paymentOptions.VENMO.description;
        this.activePopup = 'venmo-delete';
    }

    async onSubmitDeleteVenmo () {
        if (this.isVenmoDeletePopupSubmitting) {
            return
        }

        this.isVenmoDeletePopupSubmitting = true;

        // const token = this.paymentOptions.VENMO.payment_method_token;
        const paymentConfig = await this.paymentService.detachVenmoPaymentMethod().toPromise().catch(() => null);

        if (paymentConfig) {
            this.paymentConfig = paymentConfig;

            const paymentOptions = await this.paymentService.fetchPaymentOptions().toPromise().catch(() => null);

            this.updatePaymentOptions(paymentOptions);
            this.updateSelectedPaymentMethod();
        } else {
            this.methodPopupError = {
                key: 'payment_method.error.venmo_delete_failed'
            };
        }

        this.activePopup = 'method';
        this.venmoAccountToDetach = null;
        this.isVenmoDeletePopupSubmitting = false;
    }

    onCancelDeleteVenmo () {
        this.activePopup = 'method';
        this.venmoAccountToDetach = null;
        this.isCardDeletePopupSubmitting = false;
    }

    async onReplaceVenmo (e : MouseEvent) {
        this.domService.markEvent(e, 'venmoActionClick');

        if (this.isVenmoUpdating) {
            return;
        }

        this.isVenmoUpdating = true;
        this.methodPopupError = null;

        const isVenmoConnectedOk = await this.onSubmitVenmo();

        if (isVenmoConnectedOk) {
            const [ paymentOptions, paymentConfig ] = await Promise.all([
                this.paymentService.fetchPaymentOptions().toPromise(),
                this.paymentService.fetchPaymentConfig().toPromise()
            ]);

            this.updatePaymentOptions(paymentOptions);
            this.paymentConfig = paymentConfig;
            this.updateSelectedPaymentMethod();
        } else {
            this.methodPopupError = {
                key: 'payment_method.error.venmo_attach_failed'
            };
        }

        this.isVenmoUpdating = false;
    }

    onCancelMethod () {
        if (this.mode === 'setup' && this.methodPopupState !== 'error') {
            return;
        }

        this.onDone.emit({
            isOk: false
        });
    }

    canSubmitMethod () : boolean {
        return !!(
            !this.isMethodPopupSubmitting &&
            !this.isCheckingDCBEligibility &&
            this.selectedPaymentMethod &&
            this.selectedPaymentMethod.type
        );
    }

    updateSelectedPaymentMethod (selectCardId? : string) {
        this.selectedPaymentMethod = {
            type: null,
            id: null
        };

        if (selectCardId) {
            const cardItem = this.cards.find(item => item.card.id === selectCardId);

            if (cardItem && this.paymentOptions[cardItem.type].enabled) {
                this.selectedPaymentMethod.type = cardItem.type;
                this.selectedPaymentMethod.id = cardItem.card.id;
            }

            return;
        }

        const currentMethodType = this.paymentConfig.payment_method_type;
        const currentMethodId = this.paymentConfig.payment_method_id;

        switch (currentMethodType) {
            case 'DCB': {
                const paymentOption = this.paymentOptions[currentMethodType];

                if (paymentOption.enabled && paymentOption.status === 'ELIGIBLE') {
                    this.selectedPaymentMethod.type = 'DCB';
                }

                break;
            }
            case 'APPLEPAY':
            case 'GOOGLEPAY': {
                if (this.paymentOptions.WALLET.enabled && this.wallets && this.wallets[currentMethodType]) {
                    this.selectedPaymentMethod.type = currentMethodType;
                }

                break;
            }
            case 'PAYPAL': {
                this.selectedPaymentMethod.type = 'PAYPAL';
                break;
            }
            case 'CREDIT_CARD':
            case 'DEBIT_CARD': {
                const paymentOption = this.paymentOptions[currentMethodType];

                if (paymentOption.enabled && paymentOption.cards.some(card => {
                    return card.id === currentMethodId && FUNDING_TO_CARD_TYPE_MAP[card.funding] === currentMethodType;
                })) {
                    this.selectedPaymentMethod.type = currentMethodType;
                    this.selectedPaymentMethod.id = currentMethodId;
                }

                break;
            }
            case 'VENMO':
                if (this.paymentOptions.VENMO.enabled && currentMethodId) {
                    this.selectedPaymentMethod.type = currentMethodType;
                    this.selectedPaymentMethod.id = currentMethodId;
                }

                break;
        }
    }

    async _timeout () {
        return new Promise(resolve => setTimeout(resolve, 2000));
    }

    async onCheckDCBEligibility () {
        if (this.isMethodPopupSubmitting || this.isCheckingDCBEligibility || this.paymentOptions.DCB.status !== 'UNKNOWN') {
            return;
        }

        this.isCheckingDCBEligibility = true;

        // await this._timeout();

        const newDCBStatus : DCBStatus = await this.paymentService.checkDCBEligibility().toPromise().catch(() => null);

        if (newDCBStatus) {
            this.paymentOptions.DCB.status = newDCBStatus;

            this.toastService.create({
                message: [ 'payment_method.eligibility_check.check_success' ],
                timeout: 6000
            });
        } else {
            this.toastService.create({
                message: [ 'payment_method.eligibility_check.check_error' ],
                timeout: 6000
            });
        }

        this.isCheckingDCBEligibility = false;
    }
}
