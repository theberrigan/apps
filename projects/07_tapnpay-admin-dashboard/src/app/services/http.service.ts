import { Injectable } from '@angular/core';
import {HttpClient, HttpHeaders, HttpParams} from '@angular/common/http';
import {forIn, merge} from 'lodash-es';
import {CONFIG} from '../../../config/app/dev';
import {Observable} from 'rxjs';


export enum AuthType {
    Authorized = 1,
    Unauthorized = 2,
    Manual = 3,
    External = 4
}

class Endpoint {
    url? : string = null;
    body? : any;
    headers? : any = {};
    params? : any = {};
    responseType? : 'arraybuffer' | 'blob' | 'text' | 'json';
    withCredentials? : boolean;
    // -----------
    urlParams? : any = {};
    endpointVersion? : number = 1;
    authType? : AuthType;
}

export class RequestOptions {
    body? : any;
    headers? : HttpHeaders | { [ header : string ]: string | string[]; };
    observe? : any;
    params? : HttpParams | { [ param : string ]: string | string[]; };  // === queryParams
    reportProgress? : boolean;
    responseType? : 'arraybuffer' | 'blob' | 'text' | 'json';
    withCredentials? : boolean;
    // ------------------------
    urlParams? : { [ key : string ]: any };
    endpointVersion? : number;
}

export class InterceptorOptions {
    public useAccessToken : boolean = false;
    public authType : AuthType;
}

export class InterceptorHttpParams extends HttpParams {
    constructor(
        public interceptorOptions : InterceptorOptions,
        params? : any
    ) {
        super({ fromObject: params });
    }
}

export const API_REQUEST_HEADER_PREFIX = 'X-TNP-CNS';
export const API_TOKEN_HEADER_KEY = `${ API_REQUEST_HEADER_PREFIX }-ACCESS-TOKEN`;

const ENDPOINT_PREFIX : string = 'endpoint://';

// https://tnp-console-dev-server.eu.ngrok.io/ping/custom_value
const ENDPOINTS : any = {
    // + substitution of api host
    // + substitution of params
    //   access token: manual control
    manual: {

    },

    // + substitution of api host
    // + substitution of params
    //   access token: auto inject in interceptor
    authorized: {
        'storage.get':                   '/console/storage/{key}',
        'storage.create':                '/console/storage/{key}',
        'storage.update':                '/console/storage/{key}',
        'storage.delete':                '/console/storage/{key}',
        'search.get':                    '/console/search/accounts',
        'account.getSummary':            '/console/accounts/{accountId}/summary',
        'account.getInvoices':           '/console/accounts/{accountId}/invoices',
        'account.getInvoiceExtensions':  '/console/accounts/{accountId}/invoices/extension',
        'account.saveInvoiceExtension':  '/console/accounts/{accountId}/invoices/extension',
        'account.getTransactions':       '/console/accounts/{accountId}/transactions',
        'account.getDisputes':           '/console/accounts/{accountId}/disputes',
        'account.getSmsLog':             '/console/accounts/{accountId}/sms/log',
        'account.getInvoiceDetails':     '/console/accounts/{accountId}/invoices/{invoiceId}',
        'account.reinstate':             '/console/accounts/{accountId}/lock',
        'account.close':                 '/console/accounts/{accountId}',
        'account.block':                 '/console/accounts/{accountId}/suspicious-activity',
        'account.sendSMS':               '/console/accounts/{accountId}/sms/custom',
        'account.sendPIN':               '/console/accounts/{accountId}/sms/pin',
        'faq.uploadFile':                '/console/faq',
        'disputes.uploadFile':           '/console/disputes/upload',
        'coverage.get':                  '/console/map',
        'coverage.set':                  '/console/map',
        'ta.getAll':                     '/console/toll-authorities',
        'ta.create':                     '/console/toll-authorities',
        'ta.getProps':                   '/console/toll-authorities/{id}/properties',
        'ta.updateProps':                '/console/toll-authorities/{id}/properties',

        'contracts.getAllCarrier':       '/console/carrier-contract',
        'contracts.createCarrier':       '/console/carrier-contract',
        'contracts.getCarrier':          '/console/carrier-contract/{contractId}',
        'contracts.updateCarrier':       '/console/carrier-contract/{contractId}',
        'contracts.getIntegrators':      '/console/carrier-contract/integrators',
        'contracts.getCarrierGroups':    '/console/carrier-contract/carrier-groups',

        'contracts.getAllPG':            '/console/payment-gateway-contract',
        'contracts.createPG':            '/console/payment-gateway-contract',
        'contracts.getPG':               '/console/payment-gateway-contract/{contractId}',
        'contracts.updatePG':            '/console/payment-gateway-contract/{contractId}',
        'contracts.getGateways':         '/console/payment-gateway-contract/gateways',

        'contracts.getAllTA':            '/console/toll-authority-contract',
        'contracts.createTA':            '/console/toll-authority-contract',
        'contracts.getTA':               '/console/toll-authority-contract/{contractId}',
        'contracts.updateTA':            '/console/toll-authority-contract/{contractId}',
        'contracts.getSaasFee':          '/console/toll-authority-contract/saas-fee-structure',

        'documents.getDownUrl':          '/console/documents/{documentId}',
        'documents.getUpUrl':            '/console/documents',

        'graph.getOne':                  '/console/graph/{nodeId}'
    },

    // + substitution of api host
    // + substitution of params
    //   access token: no at all
    unauthorized: {
        'auth.validateToken':   '/console/auth/token',
        'auth.get-url':         '/console/auth/brands/{brand}',
        'auth.get-token':       '/console/auth/token',
        'auth.getPermissions':  '/console/auth/permissions',
    },

    // - substitution of api host
    // + substitution of params
    //   access token: no at all
    external: {
        'coverage.get_loc':     'https://tnp-console-dev-server.eu.ngrok.io/console/coverage',
        'coverage.set_loc':     'https://tnp-console-dev-server.eu.ngrok.io/console/coverage',
    }
};

// https://github.com/angular/angular/tree/7.2.15/packages/common/http/src
// https://angular.io/guide/http
@Injectable({
    providedIn: 'root'
})
export class HttpService {
    public static _instances : number = 0;

    private readonly endpoints : { [ endpointKey : string ] : Endpoint };

    constructor (
        private http : HttpClient
    ) {
        if (++HttpService._instances > 1) {
            throw new Error('Unexpected: it can be only one instance of this class');
        }

        // -------------

        const authTypes = {
            authorized:   AuthType.Authorized,
            unauthorized: AuthType.Unauthorized,
            manual:       AuthType.Manual,
            external:     AuthType.External
        };

        const apiHost : string = CONFIG.server.replace(/\/*$/, '/');

        const endpointDefaults = new Endpoint();

        const plainEndpoints : { [ endpointKey : string ] : Endpoint } = {};

        forIn(ENDPOINTS, (endpoints : { [ authType : string ] : string | Endpoint }, authGroupKey : string) => {
            forIn(endpoints, (endpoint : Endpoint, endpointKey : string) => {
                const authType : AuthType = authTypes[authGroupKey];

                if (typeof(endpoint) === 'string') {
                    endpoint = { url: endpoint };
                }

                const url = authType !== AuthType.External ? (apiHost + endpoint.url.replace(/^\/*/, '')) : endpoint.url;

                plainEndpoints[endpointKey] = merge({}, endpointDefaults, endpoint, { url, authType });
            });
        });

        this.endpoints = plainEndpoints;
    }

    public parseOptions (url : string, options : RequestOptions = {}) : any {
        let endpoint : Endpoint;

        if (url.indexOf(ENDPOINT_PREFIX) === 0) {
            const endpointKey : string = url.slice(ENDPOINT_PREFIX.length);
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

        forIn(urlParams, (value : any, key : string) => {
            url = url.replace(new RegExp(`{\\s*${ key }\\s*}`, 'g'), String(value));
        });

        const interceptorOptions = {
            useAccessToken: endpoint && endpoint.authType === AuthType.Authorized,
            authType: endpoint ? endpoint.authType : AuthType.External
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

    public post2 (url : string, options : RequestOptions = {}) : Promise<any> {
        const requestOptions = this.parseOptions(url, options);

        if (!requestOptions) {
            return Promise.reject();
        }

        return new Promise((resolve, reject) => {
            this.http.post(requestOptions.url, requestOptions.body, requestOptions.options)
                .subscribe(
                    response => resolve(response),
                    error => reject(error)
                );
        });
    }

    public put2 (url : string, options : RequestOptions = {}) : Promise<any> {
        const requestOptions = this.parseOptions(url, options);

        if (!requestOptions) {
            return Promise.reject();
        }

        return new Promise((resolve, reject) => {
            this.http.put(requestOptions.url, requestOptions.body, requestOptions.options)
                .subscribe(
                    response => resolve(response),
                    error => reject(error)
                );
        });
    }

    public get2 (url : string, options : RequestOptions = {}) : Promise<any> {
        const requestOptions = this.parseOptions(url, options);

        if (!requestOptions) {
            return Promise.reject();
        }

        return new Promise((resolve, reject) => {
            this.http.get(requestOptions.url, requestOptions.options)
                .subscribe(
                    response => resolve(response),
                    error => reject(error)
                );
        });
    }

    public delete2 (url : string, options : RequestOptions = {}) : Promise<any> {
        const requestOptions = this.parseOptions(url, options);

        if (!requestOptions) {
            return Promise.reject();
        }

        return new Promise((resolve, reject) => {
            this.http.delete(requestOptions.url, requestOptions.options)
                .subscribe(
                    response => resolve(response),
                    error => reject(error)
                );
        });
    }

    // ----------------------------------

    public get (url : string, options : RequestOptions = {}): Observable<any> {
        const args = this.parseOptions(url, options);
        return this.http.get(args.url, args.options);
    }

    public post (url : string, options : RequestOptions = {}): Observable<any> {
        const args = this.parseOptions(url, options);
        return this.http.post(args.url, args.body, args.options);
    }

    public put (url : string, options : RequestOptions = {}): Observable<any> {
        const args = this.parseOptions(url, options);
        return this.http.put(args.url, args.body, args.options);
    }

    public delete (url : string, options : RequestOptions = {}): Observable<any> {
        const args = this.parseOptions(url, options);
        args.options.body = args.body;
        return this.http.delete(args.url, args.options);
    }

    public options (url : string, options : RequestOptions = {}): Observable<any> {
        const args = this.parseOptions(url, options);
        return this.http.options(args.url, args.options);
    }
}
