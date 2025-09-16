import { Injectable } from '@angular/core';
import {HttpService} from './http.service';
import {catchError, map, retry, take} from 'rxjs/operators';
import {Observable, throwError} from 'rxjs';
import {UserService} from './user.service';

export interface SofortPaymentProvider {
    apiKey : string;
    customerId : number;
    enabled : boolean;
    projectId : number;
    type : string;
}

export interface SofortPaymentProviderUpdate {
    apiKey : string;
    customerId : number;
    enabled : boolean;
    projectId : number;
}

export interface StripePaymentProvider {
    enabled : boolean;
    linked : boolean;
    url : string;
}

export interface StripePaymentProviderUpdate {
    enabled : boolean;
}

@Injectable({
    providedIn: 'root'
})
export class PaymentProvidersService {
    constructor (
        private http : HttpService,
        private userService : UserService,
    ) {}

    public fetchSofort () : Observable<SofortPaymentProvider> {
        return this.http.get('endpoint://paymentProviders.getSofort').pipe(
            retry(1),
            take(1),
            catchError(error => {
                console.warn('fetchSofort error:', error);
                return throwError(error);
            })
        );
    }

    public updateSofort (provider : SofortPaymentProvider) : Observable<SofortPaymentProvider> {
        const body : SofortPaymentProviderUpdate = {
            apiKey: provider.apiKey,
            customerId: provider.customerId,
            enabled: provider.enabled,
            projectId: provider.projectId,
        };

        return this.http.put('endpoint://paymentProviders.updateSofort', { body }).pipe(
            retry(1),
            take(1),
            catchError(error => {
                console.warn('updateSofort error:', error);
                return throwError(error);
            })
        );
    }

    public fetchStripe () : Observable<StripePaymentProvider> {
        return this.http.get('endpoint://paymentProviders.getStripe').pipe(
            retry(1),
            take(1),
            map(response => response.stripe),
            catchError(error => {
                console.warn('fetchStripe error:', error);
                return throwError(error);
            })
        );
    }

    public updateStripe (provider : StripePaymentProvider) : Observable<StripePaymentProvider> {
        const body : StripePaymentProviderUpdate = {
            enabled: provider.enabled,
        };

        return this.http.put('endpoint://paymentProviders.updateStripe', { body }).pipe(
            retry(1),
            take(1),
            map(response => response.stripe),
            catchError(error => {
                console.warn('updateStripe error:', error);
                return throwError(error);
            })
        );
    }
}
