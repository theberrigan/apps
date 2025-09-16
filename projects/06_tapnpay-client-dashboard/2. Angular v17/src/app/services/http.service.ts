import {Injectable} from '@angular/core';
import { HttpClient, HttpHeaders, HttpParams } from '@angular/common/http';
import {forIn, merge} from 'lodash-es';
import {CONFIG} from '../../../config/app/dev';
import {Observable} from 'rxjs';


enum AuthType {
    Authorized,
    Unauthorized,
    Manual,
    External
}

class Endpoint {
    url?: string = null;
    body?: any;
    headers?: any = {};
    params?: any = {};
    responseType?: 'arraybuffer' | 'blob' | 'text' | 'json';
    withCredentials?: boolean;
    // -----------
    urlParams?: any = {};
    endpointVersion?: number = 1;
    authType?: AuthType;
}

export class RequestOptions {
    body?: any;
    headers?: HttpHeaders | { [header: string]: string | string[]; };
    observe?: any;
    params?: HttpParams | { [param: string]: string | string[]; };  // === queryParams
    reportProgress?: boolean;
    responseType?: 'arraybuffer' | 'blob' | 'text' | 'json';
    withCredentials?: boolean;
    // ------------------------
    urlParams?: { [key: string]: any };
    endpointVersion?: number;
}

export class InterceptorOptions {
    public useAccessToken: boolean = false;
}

export class InterceptorHttpParams extends HttpParams {
    constructor(
        public interceptorOptions: InterceptorOptions,
        params?: any
    ) {
        super({fromObject: params});
    }
}

export const API_TOKEN_HEADER_KEY = 'X-TNP-ACCESS-TOKEN';

const ENDPOINT_PREFIX: string = 'endpoint://';

const ENDPOINTS: any = {
    // + substitution of api host
    // + substitution of params
    //   access token: manual control
    manual: {},

    // + substitution of api host
    // + substitution of params
    //   access token: auto inject in interceptor
    authorized: {
        'account.getUserData': '/account',
        'user.getDetails': '/user-details',
        'invoices.fetchAll': '/account-invoices',
        'invoices.makePayment': '/account-invoices',
        'invoices.makePayment_err': '/account-invoices/this-url-throws-error',
        'history.fetchInvoices': '/history/invoices',
        'history.fetchTransactions': '/history/tolls',
        'history.fetchInvoiceHistory': '/history/invoices/{invoiceId}',
        'payment.checkDCBEligibility': '/payment/dcb',
        'payment.fetchOptions': '/payment/options',
        'payment.fetchConfig': '/payment/config',
        'payment.updateConfig': '/payment/config',
        'payment.deleteMethod': '/payment/method/{cardId}',
        'payment.getSetupIntent': '/payment/stripe/setup-intent',
        'payment.completePaymentIntent': '/payment/transactions/{transactionId}/complete',
        'payment.getPaymentType': '/payment/stripe/card-type',
        'bt.getClientToken': '/payment/braintree/client-token',
        'bt.updateVenmoPaymentMethod': '/payment/braintree/payment-method',
        'bt.detachVenmoPaymentMethod': '/payment/braintree/payment-method',
        'storage.get': '/storage/{key}',
        'storage.create': '/storage/{key}',
        'storage.update': '/storage/{key}',
        'storage.delete': '/storage/{key}',
        'pay-by-mail.get': '/pay-by-mail',
        'pay-by-mail.make': '/pay-by-mail/{pbmId}',
        'payment.hours-to-pay': '/toll-authority',
        'license-plates.get': '/license-plates',
        'license-plates.get-all': '/license-plates/all',
        'license-plates.get-active': '/license-plates/count/active',
        'license-plates.add': '/license-plates',
        'license-plates.delete': '/license-plates/{licensePlateId}',
        'license-plates.getPendingLPNs': '/license-plates/pending',
        'license-plates.acceptPendingLPNs': '/license-plates/pending',
        'license-plates.extendRentalPeriod': '/license-plates/{id}/extend',
        'license-plates.getLicensePlateCategories': '/license-plates/categories',
        'license-plates.getLicensePlateCoverage': '/license-plates/{licensePlateId}/coverage',
        'license-plates.getLicensePlateHistory': '/license-plates/{licensePlateId}/history',
        'license-plates.getSupportedTaLPNTypes': '/license-plates/supported-types',
        'account.deactivate': '/account',
        'faq.get': '/faq',
        'coverage.get': '/map',
        'terms.getAccepted': '/terms',
        'extend-coverage.extended': '/extended-coverage/options',
        'extend-coverage.enrolled': '/extended-coverage',
        'extend-coverage.extend': '/extended-coverage',
        'extend-coverage.mapping': '/extended-coverage/mapping',
        'subscription.getAll': '/subscription/plans',
        'subscription.getCurrent': '/subscription',
        'subscription.set': '/subscription',
        'subscription.cancel': '/subscription',
        'subscription.compare': '/subscription/plans/{planId}/compare',
        'subscription.actions': '/subscription/actions',
        'feedback.set': '/feedback',
        'autopayment.set': '/is-autopayment-approved',
        'autopayment.check': '/autopayment-approval-status',
        'account.register-user': '/register-user',
    },

    // + substitution of api host
    // + substitution of params
    //   access token: no at all
    unauthorized: {
        'terms.accept': '/terms/accept',
        'terms.verify': '/terms/verify',
        'auth.send-phone': '/auth/V2/pin',
        'auth.send-pin': '/auth/V2/token',
        'auth.validate-token': '/auth/token',
        'email.verify': '/email-verification/confirm-verify-email/{token}',
        'test.create-account': '/test/create-account',
        'test.get-account-pin': '/test/pin/{phone}',
        'test.create-pbm': '/test/pbm-registration',
        'contact-us.send': '/contact-us',
    },

    // - substitution of api host
    // + substitution of params
    //   access token: no at all
    external: {
        'invoices.makePayment_dev': 'https://tnp-payment.eu.ngrok.io/account-invoices',
        'pbm.submitPayment': 'https://tnp-payment.eu.ngrok.io/pay-by-mail/{pbmId}',
        'payment.getPayCfg': 'https://tnp-payment.eu.ngrok.io/payment/config',
        'payment.getPaymentOpts': 'https://tnp-payment.eu.ngrok.io/payment/options',
        'payment.updPaymentConfig': 'https://tnp-payment.eu.ngrok.io/payment/config',
        'payment.createPayPalOrder': 'https://tnp-payment.eu.ngrok.io/account-invoices',
        'payment.getPBMPayment': 'https://tnp-payment.eu.ngrok.io/pay-by-mail/{pbmId}',
        'license-plates.getWithPBM': 'https://mock-app.oriondev.org/probe/test/create-lp-with-pbm',
        'fleet.createTestAcc': 'https://mock-app.oriondev.org/probe/test/create-fleet-account/{phone}',
        'fleet.createTestAccOTF': 'https://mock-app.oriondev.org/probe/test/create-fleet-account-otf/{phone}',
        'fleet.generateInvoices': 'https://mock-app.oriondev.org/probe/test/generate-invoices/{phone}',
        'fleet.feeReg': 'https://mock-app.oriondev.org/probe/test/lp-with-fee-registration',
        'account.lock': 'https://mock-app.oriondev.org/probe/test/lock/{phone}/{lock_type}',
    }
};

// https://github.com/angular/angular/tree/7.2.15/packages/common/http/src
// https://angular.io/guide/http
@Injectable({
    providedIn: 'root'
})
export class HttpService {
    public static _instances: number = 0;

    private readonly endpoints: { [endpointKey: string]: Endpoint };

    constructor(
        private http: HttpClient
    ) {
        if (++HttpService._instances > 1) {
            throw new Error('Unexpected: it can be only one instance of this class');
        }

        // -------------

        const authTypes = {
            authorized: AuthType.Authorized,
            unauthorized: AuthType.Unauthorized,
            manual: AuthType.Manual,
            external: AuthType.External
        };

        const apiHost: string = CONFIG.server.replace(/\/*$/, '/');

        const endpointDefaults = new Endpoint();

        const plainEndpoints: { [endpointKey: string]: Endpoint } = {};

        forIn(ENDPOINTS, (endpoints: { [authType: string]: string | Endpoint }, authGroupKey: string) => {
            forIn(endpoints, (endpoint: Endpoint, endpointKey: string) => {
                const authType: AuthType = authTypes[authGroupKey];

                if (typeof (endpoint) === 'string') {
                    endpoint = {url: endpoint};
                }

                const url = authType !== AuthType.External ? (apiHost + endpoint.url.replace(/^\/*/, '')) : endpoint.url;

                plainEndpoints[endpointKey] = merge({}, endpointDefaults, endpoint, {url, authType});
            });
        });

        this.endpoints = plainEndpoints;
    }

    public parseOptions(url: string, options: RequestOptions = {}): any {
        let endpoint: Endpoint;

        if (url.indexOf(ENDPOINT_PREFIX) === 0) {
            const endpointKey: string = url.slice(ENDPOINT_PREFIX.length);
            endpoint = this.endpoints[endpointKey];

            if (!endpoint) {
                console.warn('Unknown endpoint key:', endpointKey);
                return null;
            }

            url = endpoint.url;
        }

        const urlParams = merge({}, endpoint ? endpoint.urlParams : {}, options.urlParams || {});

        if (endpoint && endpoint.authType !== AuthType.External) {
            urlParams.endpointVersion = options.endpointVersion || endpoint.endpointVersion;
        }

        forIn(urlParams, (value: any, key: string) => {
            url = url.replace(new RegExp(`{\\s*${ key }\\s*}`, 'g'), String(value));
        });

        const interceptorOptions = {
            useAccessToken: endpoint && endpoint.authType === AuthType.Authorized
        };

        return {
            url,
            body: ('body' in options) ? options.body : endpoint ? endpoint.body : undefined,
            options: {
                headers: merge({}, endpoint ? endpoint.headers : {}, options.headers || {}),
                observe: options.observe,
                params: new InterceptorHttpParams(interceptorOptions, merge({}, endpoint ? endpoint.params : {}, options.params || {})),
                reportProgress: options.reportProgress,
                responseType: options.responseType || endpoint && endpoint.responseType,
                withCredentials: 'withCredentials' in options ? options.withCredentials : endpoint ? endpoint.withCredentials : undefined
            }
        };
    }

// ----------------------------------

    public get(url: string, options: RequestOptions = {}): Observable<any> {
        const args = this.parseOptions(url, options);
        return this.http.get(args.url, args.options);
    }

    public post(url: string, options: RequestOptions = {}): Observable<any> {
        const args = this.parseOptions(url, options);
        return this.http.post(args.url, args.body, args.options);
    }

    public put(url: string, options: RequestOptions = {}): Observable<any> {
        const args = this.parseOptions(url, options);
        return this.http.put(args.url, args.body, args.options);
    }

    public delete(url: string, options: RequestOptions = {}): Observable<any> {
        const args = this.parseOptions(url, options);
        return this.http.delete(args.url, args.options);
    }

    public options(url: string, options: RequestOptions = {}): Observable<any> {
        const args = this.parseOptions(url, options);
        return this.http.options(args.url, args.options);
    }
}
