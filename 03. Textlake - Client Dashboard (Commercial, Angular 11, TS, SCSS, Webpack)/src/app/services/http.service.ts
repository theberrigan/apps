import { Injectable } from '@angular/core';
import {HttpClient, HttpHeaders, HttpParams} from '@angular/common/http';
import {forIn, merge} from 'lodash';
import {CONFIG} from '../../../config/app/dev';
import {Observable} from 'rxjs';


enum AuthType {
    Authorized,
    Unauthorized,
    Manual,
    External
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
}

export class InterceptorHttpParams extends HttpParams {
    constructor(
        public interceptorOptions : InterceptorOptions,
        params? : any
    ) {
        super({ fromObject: params });
    }
}

export const API_TOKEN_HEADER_KEY = 'X-TSM-ACCESS-TOKEN';

const ENDPOINT_PREFIX : string = 'endpoint://';

const ENDPOINTS : any = {
    // + substitution of api host
    // + substitution of params
    //   access token: manual control
    manual: {
        'challenge.login': '/rest/v{endpointVersion}/challenges/login',
    },

    // + substitution of api host
    // + substitution of params
    //   access token: auto inject in interceptor
    authorized: {
        'currencies.getAll':          '/rest/v{endpointVersion}/currencies',
        'currencies.getActive':       '/rest/v{endpointVersion}/currencies/active',
        'currencies.getCurrenciesRatesHistory':  '/rest/v{endpointVersion}/currencies/rates/history/{fromKey}/{toKey}',
        'currencies.getCurrenciesRates':         '/rest/v{endpointVersion}/currencies/rates',
        'currencies.updateCurrenciesRates':      '/rest/v{endpointVersion}/currencies/rates',
        'clients.get':                '/rest/v{endpointVersion}/clients',
        'clients.getInfoById':        '/rest/v{endpointVersion}/clients/{clientId}',
        'clients.getCompanies':       '/rest/v{endpointVersion}/clients',
        'clients.getCompanyContacts': '/rest/v{endpointVersion}/clients/{clientCompanyId}/contacts',
        'clients.getRates':           '/rest/v{endpointVersion}/clients/{clientId}/rates',
        'clients.getContacts':        '/rest/v{endpointVersion}/clients/{clientId}/contacts',
        'clients.create':             '/rest/v{endpointVersion}/clients',
        'clients.saveOne':            '/rest/v{endpointVersion}/clients/{clientId}',
        'clients.createCompany':      '/rest/v{endpointVersion}/clients/{name}',
        'clients.createContact':      '/rest/v{endpointVersion}/clients/{clientId}/contacts',
        'clients.saveContact':        '/rest/v{endpointVersion}/clients/{clientId}/contacts/{contactId}',
        'clients.getBalance':         '/rest/v{endpointVersion}/clients/{clientId}/balance',
        'clients.saveTransaction':    '/rest/v{endpointVersion}/clients/{clientId}/transaction',
        'company.getInfo':            '/rest/v{endpointVersion}/company',
        'company.updateCompany':      '/rest/v{endpointVersion}/company',
        'company.getCoordinators':    '/rest/v{endpointVersion}/company/coordinators',
        'company.getTranslationTypes': '/rest/v{endpointVersion}/company/translation-types',
        'company.getBasicServices':   '/rest/v{endpointVersion}/company/services/basic',
        'company.getServices':        '/rest/v{endpointVersion}/company/services',
        'company.getCalcRule':        '/rest/v{endpointVersion}/company/calculation-rules',
        'company.saveCalcRule':       '/rest/v{endpointVersion}/company/calculation-rules',
        'company.getSubjectAreas':    '/rest/v{endpointVersion}/company/fields',
        'company.createService':      '/rest/v{endpointVersion}/company/services',
        'company.updateService':      '/rest/v{endpointVersion}/company/services',
        'company.deleteService':      '/rest/v{endpointVersion}/company/services/{serviceId}',
        'company.cloneService':       '/rest/v{endpointVersion}/company/services/clone',
        'userStorage':                '/rest/v{endpointVersion}/storage/{key}',
        'profile.userProfile':        '/rest/v{endpointVersion}/profile/me',
        'profile.switchAccount':      '/rest/v{endpointVersion}/profile/active-user/{accountId}',
        'profile.verifyEmail':        '/rest/v{endpointVersion}/profile/verify',
        'profile.sendVerificationCode': '/rest/v{endpointVersion}/profile/primary-email/code',
        'profile.checkVerificationCode': '/rest/v{endpointVersion}/profile/primary-email/validate',
        'feature.features':           '/rest/v{endpointVersion}/features',
        'test.createNotification':    '/rest/v{endpointVersion}/test/create-notification',
        'test.createTask':            '/rest/v{endpointVersion}/test/create-task',
        'terms.getAccepted':          '/rest/v{endpointVersion}/terms',
        'terms.getEligible':          '/rest/v{endpointVersion}/terms/eligible',
        'terms.accept':               '/rest/v{endpointVersion}/terms/{termsId}',
        'notifications.get':          '/rest/v{endpointVersion}/notifications/top/{count}',
        'notifications.markAsViewed': '/rest/v{endpointVersion}/notifications/displayed',
        'tasks.get':                  '/rest/v{endpointVersion}/tasks',
        'offers.get':                 '/rest/v{endpointVersion}/offers',
        'offers.getStatuses':         '/rest/v{endpointVersion}/offers/statuses',
        'offers.getOne':              '/rest/v{endpointVersion}/offers/{offerKey}',
        'offers.getEmail':            {
            url: '/rest/v{endpointVersion}/offers/{offerKey}/original-email',
            responseType: 'text'
        },
        'offers.getEmailContent':     '/rest/v{endpointVersion}/files/view-orphan/{uuid}',
        'offers.getTransactions':     '/rest/v{endpointVersion}/transactions/offers/{offerKey}',
        'offers.saveTransaction':     '/rest/v{endpointVersion}/transactions',
        'offers.sendQuote':           '/rest/v{endpointVersion}/offers/{offerKey}/send',
        'offers.getHistory':          '/rest/v{endpointVersion}/logs/OFFER/{offerKey}',
        'offers.getAvailCompanyServices': '/rest/v{endpointVersion}/company/services/available',
        'offers.save':                '/rest/v{endpointVersion}/offers',
        'projects.create':            '/rest/v{endpointVersion}/projects/{offerKey}',
        'projects.getStatuses':       '/rest/v{endpointVersion}/projects/statuses',
        'projects.getOne':            '/rest/v{endpointVersion}/projects/{projectKey}',
        'projects.getMultiple':       '/rest/v{endpointVersion}/projects',
        'projects.getProjectSummary': '/rest/v{endpointVersion}/projects/{projectKey}/summary',
        'projects.getProjectCoordinators': '/rest/v{endpointVersion}/projects/{projectKey}/coordinators',
        'projects.getProjectServiceProviders': '/rest/v{endpointVersion}/services/{projectServiceId}/providers',
        'projects.getProjectServiceAssignments': '/rest/v{endpointVersion}/services/{projectServiceId}/assignments',
        'projects.getHistory':        '/rest/v{endpointVersion}/logs/PROJECT/{projectKey}',
        'projects.presignOutcome':    '/rest/v{endpointVersion}/assignments/{assignmentId}/outcome',
        'projects.createAssignment':  '/rest/v{endpointVersion}/services/{projectServiceId}/assignments',
        'projects.updateAssignment':  '/rest/v{endpointVersion}/services/{projectServiceId}/assignments/{assignmentId}',
        'projects.deleteAssignment':  '/rest/v{endpointVersion}/services/{projectServiceId}/assignments/{assignmentId}',
        'projects.updateDeadline':    '/rest/v{endpointVersion}/projects/{projectKey}/deadline',
        'projects.updateProject':     '/rest/v{endpointVersion}/projects/{projectKey}',
        'files.presign':              '/rest/v{endpointVersion}/files/presign',
        'files.getParams':            '/rest/v{endpointVersion}/files/{uuid}/presign',
        'languages.getAll':           '/rest/v{endpointVersion}/languages',
        'languages.getPreferred':     '/rest/v{endpointVersion}/languages/preferred',
        'rates.getAll':               '/rest/v{endpointVersion}/rates',
        'rates.getAvailable':         '/rest/v{endpointVersion}/rates/available',
        'rates.delete':               '/rest/v{endpointVersion}/rates/{rateId}',
        'rates.create':               '/rest/v{endpointVersion}/rates',
        'rates.update':               '/rest/v{endpointVersion}/rates/{rateId}',
        'tax.getAll':                 '/rest/v{endpointVersion}/taxes',
        'tax.delete':                 '/rest/v{endpointVersion}/taxes/{taxId}',
        'tax.create':                 '/rest/v{endpointVersion}/taxes',
        'mailboxes.getMailboxes':     '/rest/v{endpointVersion}/mailboxes/',
        'mailboxes.getMailboxFolders': '/rest/v{endpointVersion}/mailboxes/{mailboxKey}/folders',
        'mailboxes.getMessages':      '/rest/v{endpointVersion}/mailboxes/{mailboxKey}/{folderName}/messages/{startIndex}/{endIndex}',
        'mailboxes.saveColor':        '/rest/v{endpointVersion}/emails/color',
        'mailboxes.getMessage':       {
            url: '/rest/v{endpointVersion}/mailboxes/{mailboxKey}/{folderKey}/email/{mailUID}',
            responseType: 'text'
        },
        'mailboxes.delete':           '/rest/v{endpointVersion}/mailboxes/{mailboxKey}',
        'mailboxes.save':             '/rest/v{endpointVersion}/mailboxes/{mailboxKey}',
        'mailboxes.create':           '/rest/v{endpointVersion}/mailboxes',
        'mailboxes.test':             '/rest/v{endpointVersion}/mailboxes/verify',
        'mailboxes.getAttachmentUrl': '/rest/v{endpointVersion}/mailboxes/{mailboxKey}/{folderKey}/email/{mailUID}/attachment/{attachmentName}',
        'mailboxes.storeAttachments': '/rest/v{endpointVersion}/mailboxes/storeAttachments',
        'translators.getAll':         '/rest/v{endpointVersion}/translators',
        'translators.getOne':         '/rest/v{endpointVersion}/translators/{translatorId}',
        'translators.getTranslatorServices': '/rest/v{endpointVersion}/translators/{translatorId}/services',
        'translators.getTranslatorFinancial':  '/rest/v{endpointVersion}/translators/{translatorId}/financial',
        'translators.getTranslatorSSN':  '/rest/v{endpointVersion}/translators/{translatorId}/national-identification-number',
        'translators.create':         '/rest/v{endpointVersion}/translators',
        'translators.update':         '/rest/v{endpointVersion}/translators/{translatorId}',
        'translators.saveFinancial':  '/rest/v{endpointVersion}/translators/{translatorId}/financial',
        'translators.createService':  '/rest/v{endpointVersion}/translators/{translatorId}/services',
        'translators.updateService':  '/rest/v{endpointVersion}/translators/{translatorId}/services/{serviceId}',
        'translators.deleteService':  '/rest/v{endpointVersion}/translators/{translatorId}/services/{serviceId}',
        'statements.getClientsStatements':      '/rest/v{endpointVersion}/statements/clients',
        'statements.saveClientStatementItem':   '/rest/v{endpointVersion}/statements/client-item',
        'statements.getCoordinatorsStatements': '/rest/v{endpointVersion}/statements/coordinators',
        'statements.getProjectsStatements':     '/rest/v{endpointVersion}/statements/projects',
        'statements.getTranslatorsStatements':  '/rest/v{endpointVersion}/statements/translators',
        'statements.saveStatementItem':         '/rest/v{endpointVersion}/statements/item',
        'users.getAllUsers':           '/rest/v{endpointVersion}/users',
        'users.updateUser':            '/rest/v{endpointVersion}/users/{userId}',
        'users.getAllRoles':           '/rest/v{endpointVersion}/roles',
        'users.getUserRoles':          '/rest/v{endpointVersion}/users/{userId}/roles',
        'users.setUserRole':           '/rest/v{endpointVersion}/users/{userId}/roles/{roleKey}',
        'users.deleteUserRole':        '/rest/v{endpointVersion}/users/{userId}/roles/{roleKey}',
        'invitations.getInvitations':      '/rest/v{endpointVersion}/invitations',
        'invitations.createInvitation':    '/rest/v{endpointVersion}/invitations',
        'invitations.updateInvitation':    '/rest/v{endpointVersion}/invitations/{invitationId}',
        'invitations.deleteInvitation':    '/rest/v{endpointVersion}/invitations/{invitationId}',
        'paymentProviders.getSofort':      '/rest/v{endpointVersion}/payment-providers/sofort',
        'paymentProviders.updateSofort':   '/rest/v{endpointVersion}/payment-providers/sofort',
        'paymentProviders.getStripe':      '/rest/v{endpointVersion}/payment-providers/stripe',
        'paymentProviders.updateStripe':   '/rest/v{endpointVersion}/payment-providers/stripe',
        'subscription.subscribe':          '/rest/v{endpointVersion}/subscriptions',
        'subscription.getSubscription':    '/rest/v{endpointVersion}/subscriptions/active',
        'subscription.updateSubscription': '/rest/v{endpointVersion}/subscriptions/active',
        'subscription.getInvoices':        '/rest/v{endpointVersion}/subscriptions/invoices',
        'subscription.payTheInvoice':      '/rest/v{endpointVersion}/subscriptions/invoices/{invoiceId}',
        'subscription.getNextBill':        '/rest/v{endpointVersion}/subscriptions/next_bill',
        'plans.getPlans':                  '/rest/v{endpointVersion}/plans',
    },

    // + substitution of api host
    // + substitution of params
    //   access token: no at all
    unauthorized: {
        'terms.getPublic': '/rest/v{endpointVersion}/terms/unauthenticated',
    },

    // - substitution of api host
    // + substitution of params
    //   access token: no at all
    external: {

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
        return this.http.delete(args.url, args.options);
    }
}
