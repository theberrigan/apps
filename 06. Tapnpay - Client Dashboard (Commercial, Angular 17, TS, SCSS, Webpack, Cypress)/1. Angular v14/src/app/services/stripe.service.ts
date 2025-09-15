import {Injectable} from '@angular/core';
import {Location} from '@angular/common';
import {CONFIG} from '../../../config/app/dev';
import {catchError, map, take} from 'rxjs/operators';
import {Observable, throwError} from 'rxjs';
import {HttpService} from './http.service';
import {DEFAULT_LANG, LangService} from './lang.service';
import {DeviceService} from './device.service';

export interface StripeGetWalletOptions {
    amount : number;
    currency : string;
    label? : string;
}

export type StripeErrorType = 'api_connection_error' | 'api_error' | 'authentication_error' | 'card_error' | 'idempotency_error' | 'invalid_request_error' | 'rate_limit_error';

export interface StripeError {
    type : StripeErrorType;
    code : string;             // https://stripe.com/docs/error-codes
    message : string;
    decline_code? : string;    // https://stripe.com/docs/declines/codes
    param? : string;
    payment_intent? : any;
    charge? : string;
    doc_url? : string;
    payment_method? : any;
    payment_method_type? : string;
    setup_intent? : any;
    source? : any;
}

export type PaymentMethodWallet = 'APPLEPAY' | 'GOOGLEPAY';

export type WalletSupport = {
    [ key in PaymentMethodWallet ] : boolean;
};

export interface GetWalletPaymentRequest {
    paymentRequest : any;
    wallets : WalletSupport;
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

export const WALLET_TYPES : {
    [ key in PaymentMethodWallet ] : string;
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
    private stripeInstance : any = null;

    private stripePromise : Promise<any>;

    constructor (
        private location : Location,
        private http : HttpService,
        private langService : LangService,
        private deviceService : DeviceService,
    ) {}

    createStripeInstance () : any {
        // https://stripe.com/docs/js/initializing
        return (<any>window).Stripe(CONFIG.stripe.apiKey, {
            locale: 'en',
        });
    }

    async getStripeInstance () : Promise<any> {
        if (!this.stripePromise) {
            this.stripePromise = new Promise((resolve) => {
                if (this.stripeInstance) {
                    return resolve(this.stripeInstance);
                }

                if ('Stripe' in window) {
                    this.stripeInstance = this.createStripeInstance();
                    return resolve(this.stripeInstance);
                }

                const script : any = document.createElement('script');

                script.addEventListener('load', () => {
                    this.stripeInstance = this.createStripeInstance();
                    resolve(this.stripeInstance);
                });

                script.addEventListener('error', () => {
                    this.stripeInstance = null;
                    this.stripePromise = null;
                    resolve(this.stripeInstance);
                });

                script.src = 'https://js.stripe.com/v3/';
                document.head.appendChild(script);
            });
        }

        return this.stripePromise;
    }

    fetchSetupIntent () : Observable<string> {
        return this.http.get('endpoint://payment.getSetupIntent').pipe(
            take(1),
            map(response => response.client_secret),
            catchError(error => {
                console.warn('fetchSetupIntent error:', error);
                return throwError(error);
            })
        );
    }

    getPreferredElementsLang () {
        const langCode = this.langService.getCurrentLangCode();

        if (STRIPE_ELEMENTS_LOCALES.includes(langCode)) {
            return langCode;
        } else if (STRIPE_ELEMENTS_LOCALES.includes(DEFAULT_LANG.code)){
            return DEFAULT_LANG.code
        } else {
            return 'en';
        }
    }

    async createElements () {
        const stripe = await this.getStripeInstance();

        return stripe.elements({
            locale: this.getPreferredElementsLang(),
            fonts: [
                {
                    cssSrc: 'https://fonts.googleapis.com/css2?family=Montserrat:wght@600&display=swap'
                }
            ],
        });
    }

    async getWalletPaymentRequest (options : StripeGetWalletOptions) : Promise<GetWalletPaymentRequest> {
        const stripe = await this.getStripeInstance();

        return new Promise((resolve) => {
            if (this.deviceService.device.desktop) {
                return resolve({
                    paymentRequest: null,
                    wallets: null
                });
            }

            const paymentRequest = stripe.paymentRequest({
                country: 'US',
                currency: (options.currency || 'usd').toLowerCase(),
                total: {
                    label: (options.label || 'Total'),
                    amount: options.amount,
                },
            });

            paymentRequest.canMakePayment().then((result : null | {
                applePay : boolean;
                googlePay : boolean;
            }) => {
                console.warn('getWalletPaymentRequest', result);
                if (!result) {
                    return resolve({
                        paymentRequest: null,
                        wallets: null
                    });
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

    isSyncPaymentRequest () : boolean {
        return this.deviceService.browser.safari || this.deviceService.browser.chrome;
    }

    getWalletName (walletType : PaymentMethodWallet) : string {
        return WALLET_TYPES[walletType] || walletType;
    }

    // https://js.stripe.com/v3/fingerprinted/data/es-8eec44de02549f758e28238f8a0f898f.json
    localizeStripeError (error : StripeError) : {
        key : string,
        data? : any
    } {
        if (!error) {
            return null;
        }

        switch (error.code) {
            // Card decline reasons
            case 'card_declined':
                return {
                    key: `stripe.error.decline.${ error.decline_code }`
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
                    key: `stripe.error.specific.${ error.code }`
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
