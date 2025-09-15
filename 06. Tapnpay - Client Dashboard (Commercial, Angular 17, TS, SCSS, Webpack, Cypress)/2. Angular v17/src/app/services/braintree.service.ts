import {Injectable} from '@angular/core';
import {catchError, map, take} from 'rxjs/operators';
import {Observable, throwError} from 'rxjs';
import {HttpService} from './http.service';
import * as braintree from 'braintree-web';
import { HttpErrorResponse } from '@angular/common/http';

// https://developer.paypal.com/braintree/docs/guides/client-sdk/setup/javascript/v3
// https://developer.paypal.com/braintree/docs/guides/venmo/client-side
// https://developer.paypal.com/braintree/docs/start/hello-client
// https://developer.paypal.com/braintree/docs/start/hello-server/python
@Injectable({
    providedIn: 'root'
})
export class BraintreeService {
    constructor(
        private http: HttpService,
    ) {
    }

    async createClient(): Promise<null | any> {
        const clientToken: null | string = await this.fetchClientToken().toPromise().catch(() => null);

        if (!clientToken) {
            return null;
        }

        return await braintree.client.create({authorization: clientToken}).catch((err) => {
            console.warn('Failed to create Braintree client:', err);
            return null;
        });
    }

    async createVenmoComponent(clientInstance?: any): Promise<null | any> {
        clientInstance = clientInstance || (await this.createClient());

        if (!clientInstance) {
            return null;
        }

        return await braintree.venmo.create({
            client: clientInstance,
            allowDesktop: true,
            paymentMethodUsage: 'multi_use', // available in v3.77.0+
            // TODO: Add allowNewBrowserTab: false if your checkout page does not support
            // relaunching in a new tab when returning from the Venmo app. This can
            // be omitted otherwise.
            allowNewBrowserTab: false
        }).catch((err) => {
            console.warn('Failed to create Venmo component:', err);
            return null;
        });
    }

    fetchClientToken(): Observable<null | string> {
        return this.http.get('endpoint://bt.getClientToken').pipe(
            take(1),
            map((response: { client_token: string }) => {
                return response.client_token;
            }),
            catchError((error: HttpErrorResponse) => {
                console.warn('fetchClientToken error:', error);
                return throwError(error);
            })
        );
    }
}
