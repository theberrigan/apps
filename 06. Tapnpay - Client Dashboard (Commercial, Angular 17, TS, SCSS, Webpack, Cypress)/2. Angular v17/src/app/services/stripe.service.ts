import {Injectable} from '@angular/core';
import {Location} from '@angular/common';
import {CONFIG} from '../../../config/app/dev';
import {catchError, map, take} from 'rxjs/operators';
import {Observable, throwError} from 'rxjs';
import {HttpService} from './http.service';
import {DEFAULT_LANG, LangService} from './lang.service';
import {DeviceService} from './device.service';
import Stripe = stripe.Stripe;
import ElementsCreateOptions = stripe.elements.ElementsCreateOptions;
import StripePaymentRequestOptions = stripe.paymentRequest.StripePaymentRequestOptions;
import StripePaymentRequest = stripe.paymentRequest.StripePaymentRequest;
import Error = stripe.Error;
import Elements = stripe.elements.Elements;

export interface StripeGetWalletOptions {
    amount: number;
    currency: string;
    label?: string;
}

export type PaymentMethodWallet = 'APPLEPAY' | 'GOOGLEPAY';

export type WalletSupport = {
    [key in PaymentMethodWallet]: boolean;
};

export interface GetWalletPaymentRequest {
    paymentRequest: StripePaymentRequest;
    wallets: WalletSupport;
}

// https://stripe.com/docs/js/appendix/supported_locales
export const STRIPE_ELEMENTS_LOCALES = [
    'auto', 'ar', 'bg', 'cs', 'da', 'de',
    'el', 'en', 'en-GB', 'es', 'es-419',
    'et', 'fi', 'fr', 'fr-CA', 'he', 'id',
    'it', 'ja', 'lt', 'lv', 'ms', 'nb',
    'nl', 'pl', 'pt-BR', 'pt', 'ru', 'sk',
    'sl', 'sv', 'th', 'zh'
];

export const STRIPE_CHECKOUT_LOCALES = [
    'auto', 'bg', 'cs', 'da', 'de', 'el',
    'en', 'en-GB', 'es', 'es-419', 'et',
    'fi', 'fr', 'fr-CA', 'hu', 'id', 'it',
    'ja', 'lt', 'lv', 'ms', 'mt', 'nb',
    'nl', 'pl', 'pt-BR', 'pt', 'ro', 'ru',
    'sk', 'sl', 'sv', 'tr', 'zh', 'zh-HK', 'zh-TW'
];

export const WALLET_TYPES: {
    [key in PaymentMethodWallet]: string;
} = {
    'APPLEPAY': 'Apple Pay',
    'GOOGLEPAY': 'Google Pay'
};

// https://stripe.com/docs/payments/3d-secure
// https://stripe.com/docs/testing#payment-intents-api
@Injectable({
    providedIn: 'root'
})
export class StripeService {
    private stripeInstance: Stripe = null;

    private stripeInstanceCreatePromise: Promise<Stripe>;

    constructor(
        private location: Location,
        private http: HttpService,
        private langService: LangService,
        private deviceService: DeviceService,
    ) {
    }

    createStripeInstance(): Stripe {
        // https://stripe.com/docs/js/initializing
        return (<any>window).Stripe(CONFIG.stripe.apiKey, {
            locale: 'en',
        });
    }

    async getStripeInstance(): Promise<Stripe> {
        if (!this.stripeInstanceCreatePromise) {
            this.stripeInstanceCreatePromise = new Promise((resolve) => {
                if (this.stripeInstance) {
                    return resolve(this.stripeInstance);
                }

                if ('Stripe' in window) {
                    this.stripeInstance = this.createStripeInstance();
                    return resolve(this.stripeInstance);
                }

                const script: HTMLScriptElement = document.createElement('script');

                script.addEventListener('load', () => {
                    this.stripeInstance = this.createStripeInstance();
                    resolve(this.stripeInstance);
                });

                script.addEventListener('error', () => {
                    this.stripeInstance = null;
                    this.stripeInstanceCreatePromise = null;
                    resolve(this.stripeInstance);
                });

                script.src = 'https://js.stripe.com/v3/';
                document.head.appendChild(script);
            });
        }

        return this.stripeInstanceCreatePromise;
    }

    public fetchSetupIntent(): Observable<string> {
        return this.http.get('endpoint://payment.getSetupIntent').pipe(
            take(1),
            map(response => response.client_secret),
            catchError(error => {
                console.warn('fetchSetupIntent error:', error);
                return throwError(error);
            })
        );
    }

    private getPreferredElementsLang(): string {
        const langCode = this.langService.getCurrentLangCode();

        if (STRIPE_ELEMENTS_LOCALES.includes(langCode)) {
            return langCode;
        } else if (STRIPE_ELEMENTS_LOCALES.includes(DEFAULT_LANG.code)) {
            return DEFAULT_LANG.code
        } else {
            return 'en';
        }
    }

    async createElements(): Promise<Elements> {
        const stripe: Stripe = await this.getStripeInstance();

        const stripeElementsOptions: ElementsCreateOptions = {
            locale: this.getPreferredElementsLang(),
            fonts: [
                {
                    cssSrc: 'https://fonts.googleapis.com/css2?family=Montserrat:wght@600&display=swap'
                }
            ],
        };
        return stripe.elements(stripeElementsOptions);
    }

    async getMobileWalletPaymentRequest(options: StripeGetWalletOptions): Promise<GetWalletPaymentRequest> {
        const stripe: Stripe = await this.getStripeInstance();

        return new Promise((resolve) => {

            const stripePaymentRequestOptions: StripePaymentRequestOptions = {
                country: 'US',
                currency: (options.currency || 'usd').toLowerCase(),
                total: {
                    label: options.label || 'Total',
                    amount: options.amount,
                },
            };
            const paymentRequest: StripePaymentRequest = stripe.paymentRequest(stripePaymentRequestOptions);

            paymentRequest.canMakePayment().then((result: {
                applePay?: boolean | undefined,
                googlePay?: boolean | undefined
            }) => {
                console.warn('getWalletPaymentRequest', result);
                if (!result) {
                    resolve({
                        paymentRequest: null,
                        wallets: null
                    });
                    return;
                }

                resolve({
                    paymentRequest,
                    wallets: {
                        GOOGLEPAY: !!result.googlePay,
                        APPLEPAY: !!result.applePay,
                    }
                });
            });
        });
    }


    isSyncPaymentRequest(): boolean {
        return this.deviceService.browser.safari || this.deviceService.browser.chrome;
    }

    getWalletName(walletType: PaymentMethodWallet): string {
        return WALLET_TYPES[walletType] || walletType;
    }

    // https://js.stripe.com/v3/fingerprinted/data/es-8eec44de02549f758e28238f8a0f898f.json
    localizeStripeError(error: Error): {
        key: string,
        data?: any
    } {
        if (!error) {
            return null;
        }

        switch (error.code) {
            // Card decline reasons
            case 'card_declined':
                return {
                    key: `stripe.error.decline.${error.decline_code}`
                };

            // Specific Stripe errors
            case 'amount_too_large':
            case 'amount_too_small':
            case 'authentication_required':
            case 'balance_insufficient':
            case 'card_decline_rate_limit_exceeded':
            case 'customer_max_payment_methods':
            case 'email_invalid':
            case 'expired_card':
            case 'incorrect_address':
            case 'incorrect_cvc':
            case 'incorrect_number':
            case 'incorrect_zip':
            case 'invalid_card_type':
            case 'invalid_characters':
            case 'invalid_cvc':
            case 'invalid_expiry_month':
            case 'invalid_expiry_year':
            case 'invalid_number':
            case 'payment_intent_authentication_failure':
            case 'payment_method_provider_decline':
            case 'payment_method_provider_timeout':
            case 'setup_attempt_failed':
            case 'setup_intent_authentication_failure':
            case 'postal_code_invalid':
            case 'processing_error':
                return {
                    key: `stripe.error.specific.${error.code}`
                };

            // Payment-related errors
            case 'invalid_charge_amount':
            case 'invoice_no_customer_line_items':
            case 'invoice_no_payment_method_types':
            case 'invoice_no_subscription_line_items':
            case 'invoice_not_editable':
            case 'invoice_payment_intent_requires_action':
            case 'invoice_upcoming_none':
            case 'payment_intent_action_required':
            case 'payment_intent_incompatible_payment_method':
            case 'payment_intent_invalid_parameter':
            case 'payment_intent_payment_attempt_failed':
            case 'payment_intent_unexpected_state':
            case 'payment_method_invalid_parameter':
            case 'payment_method_unactivated':
            case 'payment_method_unexpected_state':
            case 'payment_method_unsupported_type':
                return {
                    key: 'stripe.error.common.payment_failure'
                };
        }

        switch (error.type) {
            // Unhandled card errors
            case 'card_error':
                return {
                    key: 'stripe.error.common.card_failure'
                };
        }

        return {
            key: 'stripe.error.common.generic'
        };
    }
}
