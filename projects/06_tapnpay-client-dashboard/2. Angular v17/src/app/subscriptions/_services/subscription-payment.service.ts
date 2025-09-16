import {Injectable, OnDestroy} from '@angular/core';
import {PaymentConfig, PaymentMethodType, PaymentService} from "../../services/payment.service";
import {
    SetSubscriptionPaymentIntent,
    SetSubscriptionPlanOptions,
    SetSubscriptionPlanResponse,
    SubscriptionListItem, SubscriptionUpdateType
} from "../_models/subscription.models";
import {SubscriptionApiService} from "./subscription-api.service";
import {FlowGlobalStateService} from "./flow-global-state.service";
import {firstValueFrom, Observable, Subject, Subscription} from "rxjs";

import {PaymentMethodWallet, StripeService} from "../../services/stripe.service";
import StripePaymentMethodPaymentResponse = stripe.paymentRequest.StripePaymentMethodPaymentResponse;
import PaymentIntentResponse = stripe.PaymentIntentResponse;
import PaymentIntentStatus = stripe.paymentIntents.PaymentIntentStatus;

export interface SubscriptionPaymentError {
    translationKey: string;
    error: any;
}

@Injectable({
    providedIn: 'root'
})
export class SubscriptionPaymentService implements OnDestroy {
    private autoPaymentStatusSubscription: Subscription;
    private currentAutoPaymentStatus: boolean = false;

    private selectedSubscription: SubscriptionListItem = null
    private selectedPaymentMethod: PaymentConfig = null;

    public paymentError$: Subject<SubscriptionPaymentError>;

    constructor(
        private subscriptionApi: SubscriptionApiService,
        private flowGlobalState: FlowGlobalStateService,
        private stripeService: StripeService,
        private paymentService: PaymentService) {
    }


    paySubscription(selectedPaymentMethod: PaymentConfig,
                    selectedSubscription: SubscriptionListItem,
                    confirmationType: SubscriptionUpdateType) {
        this.selectedSubscription = selectedSubscription;
        this.selectedPaymentMethod = selectedPaymentMethod;

        let setSubscriptionPlanData: SetSubscriptionPlanOptions = this.prepareSubscriptionPaymentConfigByPaymentMethod(this.selectedPaymentMethod.payment_method_type, confirmationType);

        return this.subscriptionApi.setSubscriptionPlan(setSubscriptionPlanData);
    }

    // TODO make it reusable because vehicles.component.ts has the similar one code block
    public async completeWalletPayment(subscriptionPlanResponse: SetSubscriptionPlanResponse): Promise<void> {
        const paymentIntent: SetSubscriptionPaymentIntent = subscriptionPlanResponse.payment_intent;

        const {paymentRequest} = await this.stripeService.getMobileWalletPaymentRequest({
            amount: paymentIntent.amount,
            currency: paymentIntent.currency,
            label: 'Total',
        });

        if (!paymentRequest) {
            throw new Error('profile.fleet.message_issues'); // TODO new message
        }

        const stripe = await this.stripeService.getStripeInstance();

        return new Promise<void>((resolve, reject) => {
            paymentRequest.on('paymentmethod', async (e: StripePaymentMethodPaymentResponse) => {
                try {
                    const confirmCardPaymentResponse: PaymentIntentResponse = await stripe.confirmCardPayment(
                        paymentIntent.client_secret,
                        {
                            payment_method: e.paymentMethod.id,
                            setup_future_usage: 'off_session'
                        },
                        {handleActions: false}
                    );

                    if (confirmCardPaymentResponse.error) {
                        e.complete('fail');
                        const error = this.stripeService.localizeStripeError(confirmCardPaymentResponse.error);
                        console.warn('Failed:', error);
                        return reject(new Error('profile.fleet.message_issues')); // TODO: заменить на корректное сообщение
                    }

                    e.complete('success');

                    let isOk = true;
                    const paymentIntentStatus: PaymentIntentStatus = confirmCardPaymentResponse.paymentIntent.status;
                    if (paymentIntentStatus === 'requires_action') {
                        const confirmCardPaymentPaymentIntentResponse: PaymentIntentResponse = await stripe.confirmCardPayment(paymentIntent.client_secret);

                        if (confirmCardPaymentPaymentIntentResponse.error) {
                            console.warn('Failed to auth 3D secure:', confirmCardPaymentPaymentIntentResponse.error);

                            if (confirmCardPaymentResponse.error.code === 'card_declined') {
                                const error = this.stripeService.localizeStripeError(confirmCardPaymentPaymentIntentResponse.error);
                                console.warn('Failed:', error);
                                return reject(new Error('profile.fleet.message_issues')); // TODO: заменить на корректное сообщение
                            }

                            isOk = false;
                        }
                    }

                    if (isOk) {
                        const walletName = this.paymentService.transformPaymentMethodName(e.paymentMethod.card.wallet.type);
                        const paymentMethodId = e.paymentMethod.id;
                        if (walletName && paymentMethodId) {
                            await firstValueFrom(this.paymentService.setNewPaymentMethod({
                                payment_method_type: walletName,
                                payment_method_id: paymentMethodId
                            })).catch(() => null);
                        }
                        await firstValueFrom(this.paymentService.completePaymentIntent(subscriptionPlanResponse.transaction_id)).catch(() => false);
                        resolve();
                    } else {
                        return reject(new Error('profile.fleet.message_issues'));
                    }
                } catch (err) {
                    return reject(err);
                }
            });

            paymentRequest.on('cancel', () => {
                return reject(new Error('profile.fleet.message_issues'));
            });

            paymentRequest.show();
        });
    }


    private prepareSubscriptionPaymentConfigByPaymentMethod(paymentMethod: PaymentMethodType, confirmationType: SubscriptionUpdateType): SetSubscriptionPlanOptions {
        switch (paymentMethod) {
            case "DCB":
                // TODO implement POST CODE verification
                return this.preparePaymentByDCB();
            case "DEBIT_CARD":
            case 'CREDIT_CARD':
                return this.preparePaymentByCard();
            case 'PAYPAL':
                return this.preparePaymentByPayPal(confirmationType);
            case 'GOOGLEPAY':
            case 'APPLEPAY':
                return this.preparePaymentByMobileWallet();
            default:
                return this.preparePaymentByCard();
        }
    }

    private preparePaymentByCard(): SetSubscriptionPlanOptions {
        return this.getPaymentConfig({});
    }

    private preparePaymentByPayPal(confirmationType: SubscriptionUpdateType): SetSubscriptionPlanOptions {
        let cancel_url = '/dashboard/paypal-redirect/subscription-cancel';
        let return_url = '/dashboard/paypal-redirect/subscription-confirm?ackType=' + confirmationType;

        return this.getPaymentConfig({return_url, cancel_url});
    }

    private preparePaymentByMobileWallet(): SetSubscriptionPlanOptions {
        return this.getPaymentConfig({});
    }

    getPaymentConfig(paramsToSet: { verification_code?: string, return_url?: string, cancel_url?: string }) {
        let setSubscriptionPlanData: SetSubscriptionPlanOptions = {
            subscription_plan_id: this.selectedSubscription.id,
            payment_method_type: this.selectedPaymentMethod.payment_method_type,
            payment_method_id: this.selectedPaymentMethod.payment_method_id,
            verification_code: paramsToSet.verification_code || '',
            return_url: paramsToSet.return_url || '',
            cancel_url: paramsToSet.cancel_url || '',
        };
        return setSubscriptionPlanData;
    }

    private preparePaymentByDCB() {
        return undefined;
    }

    ngOnDestroy(): void {
        if (this.autoPaymentStatusSubscription) {
            this.autoPaymentStatusSubscription.unsubscribe();
        }
    }
}
