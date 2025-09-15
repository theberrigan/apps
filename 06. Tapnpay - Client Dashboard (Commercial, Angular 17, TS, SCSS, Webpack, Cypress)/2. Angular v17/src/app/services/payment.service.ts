import {Injectable} from '@angular/core';
import {HttpErrorResponse} from '@angular/common/http';
import {HttpService} from './http.service';
import {catchError, map, retry, take} from 'rxjs/operators';
import {firstValueFrom, Observable, Subject, throwError} from 'rxjs';
import {PaymentMethodWallet, StripeService} from './stripe.service';
import {StorageService} from './storage.service';
import {BraintreeService} from './braintree.service';

export type PaymentMethodCard = 'CREDIT_CARD' | 'DEBIT_CARD';
export type PaymentMethodType = 'DCB' | 'PAYPAL' | PaymentMethodWallet | PaymentMethodCard | 'VENMO';

export const CARD_TYPES: PaymentMethodCard[] = ['CREDIT_CARD', 'DEBIT_CARD'];
export const WALLET_TYPES: PaymentMethodWallet[] = ['GOOGLEPAY', 'APPLEPAY'];

export const CARD_TYPE_TO_FUNDING_MAP: { [key in PaymentMethodCard]: PaymentCardFunding[] } = {
    'CREDIT_CARD': ['credit'],
    'DEBIT_CARD': ['debit', 'prepaid'],
};

export const FUNDING_TO_CARD_TYPE_MAP: { [key in PaymentCardFunding]: PaymentMethodCard } = {
    'credit': 'CREDIT_CARD',
    'debit': 'DEBIT_CARD',
    'prepaid': 'DEBIT_CARD',
    'unknown': null
};

export interface PaymentConfig {
    status: 'OK' | 'ERROR ';
    setup_complete: boolean;
    payment_method_type: null | PaymentMethodType;
    payment_method_id: null | string;
    payment_verification_required: boolean;
    min_payment_amount: number;
    max_payment_amount: number;
}

export interface PaymentMethodAttach {
    status: 'OK' | 'ERROR ';
    payment_method_type: null | PaymentMethodType;
    payment_method_id: null | string;
    stripe_user_id: null | string;
}

export interface UpdatePaymentConfigRequestData {
    payment_method_type: PaymentMethodType;
    payment_method_id: null | string;
}

export type PaymentCarrier = 'ATT' | 'VERIZON';

export type PaymentCardFunding = 'credit' | 'debit' | 'prepaid' | 'unknown';

export interface PaymentCard {
    id: string;
    last4: string;
    funding: PaymentCardFunding;
    brand: string;
    created: number;
}

export type DCBStatus = 'ELIGIBLE' | 'INELIGIBLE' | 'UNKNOWN';

export interface PaymentOptions {
    DCB: {
        enabled: boolean;
        status: DCBStatus;
        carrier: PaymentCarrier;
    };
    CREDIT_CARD: {
        enabled: boolean;
        cards: PaymentCard[];
    };
    DEBIT_CARD: {
        enabled: boolean;
        cards: PaymentCard[];
    };
    PAYPAL: {
        enabled: boolean;
    };
    WALLET: {
        enabled: boolean;
    };
    VENMO: {
        enabled: boolean;
        payment_method_token: null | string;
        description: null | string;
    };
}

export interface PayByMailData {
    status: string;
    pbm_id: string;
    name: string;
    amount: number;
    currency: string;
}

export interface MakePaymentByEmailData {
    make_payment: boolean;
    verification_code: string;
    payment_method_type: PaymentMethodType;
    payment_method_id: null | string;
    return_url: null | string;  // /hook.html?...
    cancel_url: null | string;  // /hook.html?...
}

export interface MakePaymentByEmailResponse {
    status: 'OK' | 'ERROR';
    errorCode?: number;
    payment_complete?: boolean;
    lpn?: string;
    lps?: string;
    transaction_id?: string;
    payment_intent?: {
        id?: string;
        client_secret?: string;
        amount?: number;
        currency?: string;
        approve_payment_url?: string;
    };
}

export interface UpdateVenmoResponse {
    status: 'OK' | 'ERROR';
    payment_method_token: null | string;
    description: null | string;
}

export interface PaymentRequestOptions {
    pbmId: string;
    makePayment: boolean;
    verificationCode?: string;
    returnUrl?: string;
    cancelUrl?: string;
}

export const _TEST_VENMO_ = false;

@Injectable({
    providedIn: 'root'
})


/*
all payment execute by 4 payments providers
1. Stripe (Credit/Debit Card, Google Pay, Apple Pay)
2. Braintree (Venmo)
4. PayPal (PayPal)
* */

export class PaymentService {
    onPaymentConfigChanged$ = new Subject<PaymentConfig>();

    constructor(
        private http: HttpService,
        private stripeService: StripeService,
        private braintreeService: BraintreeService,
    ) {
    }

    checkDCBEligibility(): Observable<DCBStatus> {
        return this.http.put('endpoint://payment.checkDCBEligibility')
            .pipe(
                take(1),
                map(response => response.dcb_status || null),
                catchError(error => {
                    console.warn('checkDCBEligibility error:', error);
                    return throwError(error);
                })
            );
    }

    async checkCurrentPaymentMethod(
        config?: null | PaymentConfig,
        options?: null | PaymentOptions,
        walletData?: null | {
            amount: number,
            currency: string
        },
        venmoInstance?: null | any
    ): Promise<boolean> {
        if (!config) {
            config = await this.fetchPaymentConfig().toPromise().catch(() => null);
        }

        if (!config || !config.setup_complete) {
            return false;
        }

        if (!options) {
            options = await this.fetchPaymentOptions().toPromise().catch(() => null);
        }

        if (!options) {
            return false;
        }

        const methodType = config.payment_method_type || null;
        const methodId = config.payment_method_id || null;
        const optionType = WALLET_TYPES.includes(<PaymentMethodWallet>methodType) ? 'WALLET' : methodType;
        const option = options[optionType] || null;

        // Common check
        if (!option || !option.enabled) {
            return false;
        }

        // Card check
        if (CARD_TYPES.includes(<PaymentMethodCard>optionType)) {
            return (option.cards || []).some((card: PaymentCard) => {
                return card.id === methodId && CARD_TYPE_TO_FUNDING_MAP[optionType].includes(card.funding);
            });
        }

        // Wallet check
        if (optionType === 'WALLET') {
            const {paymentRequest, wallets} = await this.stripeService.getMobileWalletPaymentRequest({
                amount: walletData?.amount || 150,
                currency: walletData?.currency || 'usd',
                label: 'Total',
            });

            return !!(paymentRequest && wallets[methodType]);
        }

        if (methodType === 'VENMO') {
            venmoInstance = venmoInstance || (await this.braintreeService.createVenmoComponent());

            if (!venmoInstance || !venmoInstance.isBrowserSupported()) {
                return false;
            }
        }

        return true;
    }

    fetchPaymentOptions(): Observable<PaymentOptions> {
        return this.http.get('endpoint://payment.fetchOptions').pipe(
            retry(1),
            take(1),
            map(response => {
                const options: PaymentOptions = Object.keys(response).reduce((acc: PaymentOptions, key: string) => {
                    acc[key.toUpperCase()] = response[key];
                    return acc;
                }, {} as PaymentOptions);

                CARD_TYPES.forEach(cardType => {
                    if (!options[cardType]) {
                        options[cardType] = {
                            enabled: false,
                            cards: []
                        };
                    }

                    if (!options[cardType].cards) {
                        options[cardType].cards = [];
                    }
                });

                // options.CREDIT_CARD.enabled = false;
                // options.DEBIT_CARD.enabled = false;

                if (!options.VENMO) {
                    options.VENMO = {
                        enabled: false,
                        payment_method_token: null,
                        description: null
                    };
                }

                return options;
            }),
            catchError(error => {
                console.warn('fetchPaymentOptions error:', error);
                return throwError(error);
            })
        );
    }

    fetchPaymentConfig(): Observable<PaymentConfig> {
        return this.http.get('endpoint://payment.fetchConfig')
            .pipe(
                retry(1),
                take(1),
                map(response => response.status === 'OK' ? response : null),
                catchError(error => {
                    console.warn('fetchPaymentConfig error:', error);
                    return throwError(error);
                })
            );
    }

    setNewPaymentMethod(requestData: UpdatePaymentConfigRequestData): Observable<null | PaymentConfig> {
        return this.http.put('endpoint://payment.updateConfig', {
            body: requestData
        }).pipe(
            take(1),
            map((response: PaymentConfig) => {
                if (response.status === 'OK') {
                    this.onPaymentConfigChanged$.next(response)
                    return response;
                }

                return null;
            }),
            catchError(error => {
                console.warn('updatePaymentConfig error:', error);
                return throwError(error);
            })
        );
    }

    deletePaymentMethod(cardId: string): Observable<null | PaymentConfig> {
        return this.http.delete('endpoint://payment.deleteMethod', {
            urlParams: {cardId}
        }).pipe(
            take(1),
            map(response => response.status === 'OK' ? response : null),
            catchError(error => {
                console.warn('deletePaymentMethod error:', error);
                return throwError(error);
            })
        );
    }

    fetchPayByMail(): Observable<PayByMailData> {
        return this.http.get('endpoint://pay-by-mail.get')
            .pipe(
                retry(1),
                take(1),
                catchError(error => {
                    console.warn('fetchPayByMail error:', error);
                    return throwError(error);
                })
            );
    }

    fetchHoursToPay(): Observable<number> {
        return this.http.get('endpoint://payment.hours-to-pay')
            .pipe(
                retry(1),
                take(1),
                map(response => response.non_payment_hours),
                catchError(error => {
                    console.warn('fetchHoursToPay error:', error);
                    return throwError(error);
                })
            );
    }

    fetchPaymentMethodType(stripePaymentMethodId: string): Observable<PaymentMethodType> {
        return this.http.post('endpoint://payment.getPaymentType', {
            body: {
                payment_method_id: stripePaymentMethodId
            }
        }).pipe(
            take(1),
            map(response => response.payment_method_type),
            catchError(error => {
                console.warn('fetchPaymentMethodType error:', error);
                return throwError(error);
            })
        );
    }

    makePaymentByEmail(pbmId: string, requestData: MakePaymentByEmailData): Observable<MakePaymentByEmailResponse> {
        if (_TEST_VENMO_) {
            return this.http.post('endpoint://pbm.submitPayment', {
                urlParams: {pbmId},
                body: requestData
            }).pipe(
                take(1),
                catchError((error: HttpErrorResponse) => {
                    console.warn('makePaymentByEmail error:', error);
                    return throwError(error.error.status_code || error.error.status);
                })
            );
        }

        // return throwError(307);
        return this.http.post('endpoint://pay-by-mail.make', {
            urlParams: {pbmId},
            body: requestData
        }).pipe(
            take(1),
            catchError((error: HttpErrorResponse) => {
                console.warn('makePaymentByEmail error:', error);
                return throwError(error.error.status_code || error.error.status);
            })
        );
    }

    _tmp_makePaymentByEmail(pbmId: string, requestData: MakePaymentByEmailData): Observable<MakePaymentByEmailResponse> {
        // return throwError(307);
        return this.http.post('endpoint://payment.getPBMPayment', {
            urlParams: {pbmId},
            body: requestData
        }).pipe(
            take(1),
            catchError((error: HttpErrorResponse) => {
                console.warn('_tmp_makePaymentByEmail error:', error);
                return throwError(error.error.status_code || error.error.status);
            })
        );
    }

    completePaymentIntent(transactionId: string): Observable<boolean> {
        return this.http.post('endpoint://payment.completePaymentIntent', {
            urlParams: {transactionId},
        }).pipe(
            take(1),
            map((response: {
                'status': "OK" | "ERROR"
            }) => response.status === 'OK'),
            catchError((error: HttpErrorResponse) => {
                console.warn('completePaymentIntent error:', error);
                return throwError(error.error.status_code || error.error.status);
            })
        );
    }

    // -----------------------------------------------

    updateVenmoPaymentMethod(nonce: string): Observable<null | any> {
        return this.http.put('endpoint://bt.updateVenmoPaymentMethod', {
            body: {
                payment_method_nonce: nonce
            }
        }).pipe(
            take(1),
            map((response: UpdateVenmoResponse) => {
                return response.status === 'OK' ? response : null;
            }),
            catchError((error: HttpErrorResponse) => {
                console.warn('updateVenmoPaymentMethod error:', error);
                return throwError(error);
            })
        );
    }

    detachVenmoPaymentMethod(): Observable<null | PaymentConfig> {
        return this.http.delete('endpoint://bt.detachVenmoPaymentMethod').pipe(
            take(1),
            map(response => response.status === 'OK' ? response : null),
            catchError((error: HttpErrorResponse) => {
                console.warn('detachVenmoPaymentMethod error:', error);
                return throwError(error);
            })
        );
    }

    async sendPaymentRequest(paymentMethodOptions: PaymentRequestOptions, paymentConfig): Promise<MakePaymentByEmailResponse> {
        const {
            pbmId,
            makePayment,
            verificationCode,
            returnUrl,
            cancelUrl
        } = paymentMethodOptions;
        const {
            payment_method_type,
            payment_method_id
        } = paymentConfig || {};

        const paymentOptions: MakePaymentByEmailData = {
            make_payment: makePayment,
            verification_code: verificationCode || null,
            payment_method_type: payment_method_type || null,
            payment_method_id: payment_method_id || null,
            return_url: returnUrl || null,
            cancel_url: cancelUrl || null,
        }

        return firstValueFrom(this.makePaymentByEmail(paymentMethodOptions.pbmId, paymentOptions))
            .then(response => {
                console.warn(response);
                if (response.status !== 'OK' && !response.errorCode) {
                    response.errorCode = 205;
                }

                return response;
            })
            .catch((errorCode: number) => {
                console.warn(errorCode);
                return {
                    status: 'ERROR',
                    errorCode
                };
            });
    }

    public transformPaymentMethodName(paymentMethod: 'apple_pay' | 'google_pay' | string): PaymentMethodWallet {
        return paymentMethod.split('_').join('').toUpperCase() as PaymentMethodWallet;
    }
}
