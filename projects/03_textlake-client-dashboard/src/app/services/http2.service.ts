import { Injectable }  from '@angular/core';
import { HttpClient, HttpHeaders } from '@angular/common/http';
import { Observable } from 'rxjs';
import { Endpoints } from '../data/endpoints';
import { RequestFlags } from '../enums/request-flags.enum';
import { CONFIG } from '../../../config/app/dev';

@Injectable({
    providedIn: 'root',
})
export class HttpService2 {
    constructor (
        private http : HttpClient
    ) {}

    static get ENDPOINT_PREFIX () : string {
        return 'endpoint://';
    }

    static get PARAM_REGEXP () : RegExp {
        return /{\s*([^\s}]+)\s*}/;
    }

    static get SERVER_NAME () : string {
        return CONFIG.server.replace(/\/*$/, '');
    }

    static get REQUEST_FLAGS_HEADER () : string {
        return 'Request-Flags';
    }

    static get ACCESS_TOKEN_HEADER () : string {
        return 'X-TSM-ACCESS-TOKEN';
    }

    public process (options : any) : any {
        const result : any = {
            url: null,
            body: null,
            options: null
        };

        options = Object.assign({}, options);

        // requests flags
        let requestFlags : RequestFlags = RequestFlags.None;

        // params
        let params : any = Object.assign({}, options.params || {});
        delete options.params;

        // queryParams
        // TODO: assign with defaults
        if (options.queryParams) {
            options.params = options.queryParams;
            delete options.queryParams;
        }

        // url
        let url : string = options.url;
        delete options.url;

        if (url.toLocaleLowerCase().indexOf(HttpService2.ENDPOINT_PREFIX) == 0) {
            const endpointKey : string = url.slice(HttpService2.ENDPOINT_PREFIX.length);

            if (!Endpoints.hasOwnProperty(endpointKey)) {
                throw new Error(`[HttpService.processUrl] Endpoint '${ endpointKey }' doesn't exist.`);
            }

            const endpoint : any = typeof(Endpoints[endpointKey]) == 'string' ? { url: Endpoints[endpointKey] } : Endpoints[endpointKey];

            url = endpoint.url;
            params = Object.assign(endpoint.params || {}, params);

            if (endpoint.hasOwnProperty('requestFlags')) {
                requestFlags = endpoint.requestFlags
            }

            let match : any;

            while ((match = url.match(HttpService2.PARAM_REGEXP))) {
                const paramKey : string = match[1];

                if (!params.hasOwnProperty(paramKey)) {
                    throw new Error(`[HttpService.processUrl] Params object doesn't have key '${ paramKey }' (endpoint url: '${ url }').`);
                }

                url = url.replace(match[0], params[paramKey]);
            }

            url = HttpService2.SERVER_NAME + '/' + url.replace(/^\/*/, '');
        }

        result.url = url;

        // headers
        options.headers = (
            options.headers && options.headers instanceof HttpHeaders ?
            options.headers :
            new HttpHeaders(options.headers || {})
        ).set(HttpService2.REQUEST_FLAGS_HEADER, String(requestFlags));

        // body
        if (options.hasOwnProperty('body')) {
            // let body : any = options.body;

            // const dataType : string = (options.dataType || 'json').toLowerCase();
            //
            // switch (dataType) {
            //     case 'json':
            //         body = JSON.stringify(body);
            //         options.headers.set('Content-Type', 'application/json');
            //         break;
            // }

            // result.body = body;

            // -----------------

            result.body = options.body;
        }

        delete options.body;
        delete options.dataType;

        // Other params...
        result.options = options;

        return result;
    }

    public get (params : any) : Observable<any> {
        const { url, options } = this.process(params);
        return this.http.get(url, options);
    }

    public post (params : any) : Observable<any> {
        const { url, body, options } = this.process(params);
        return this.http.post(url, body, options);
    }

    // request(first: string | HttpRequest<any>, url?: string, options: {...}): Observable<any>
    // delete(url: string, options: {...}): Observable<any>
    // get(url: string, options: {...}): Observable<any>
    // head(url: string, options: {...}): Observable<any>
    // jsonp<T>(url: string, callbackParam: string): Observable<T>
    // options(url: string, options: {...}): Observable<any>
    // patch(url: string, body: any | null, options: {...}): Observable<any>
    // post(url: string, body: any | null, options: {...}): Observable<any>
    // put(url: string, body: any | null, options: {...}): Observable<any>

    put () : any {

    }

    delete () : any {

    }

    head () : any {

    }

    jsonp () : any {

    }

    options () : any {

    }

    patch () : any {

    }
}
