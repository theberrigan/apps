import { Injectable } from '@angular/core';
import {HttpService} from './http.service';
import {catchError, map, retry, take} from 'rxjs/operators';
import {Observable, throwError} from 'rxjs';
import {UserService} from './user.service';
import {Plan} from './plans.service';


export interface SubscriptionRequest {
    fundingSource : string;
    plan : string;
    quantity : number;
}

export interface Subscription {
    subscriptionId : number;
}

export interface FundingSource {
    brand : string;
    expMonth : number;
    extYear : number;
    last4 : string;
}

export interface SubscriptionDetails {
    id : string;
    canceledAt : string;
    created : string;
    currentPeriodEnd : string;
    currentPeriodStart : string;
    daysUntilDue : number;
    endedAt : string;
    platformFee : number;
    quantity : number;
    fundingSource : FundingSource;
    plan : Plan;
}

export interface UpdateSubscriptionRequest {
    fundingSource : string;
    quantity : number;
}

export interface SubscriptionInvoice {
    currency : string;
    date : number;
    invoiceId : string;
    number : string;
    paid : boolean;
    periodEnd : number;
    periodStart : number;
    total : number;
}

export interface UpcomingInvoice {
    amountDue : number;
    currency : string;
    periodEnd : string;
    periodStart : string;
}


@Injectable({
    providedIn: 'root'
})
export class SubscriptionService {
    constructor (
        private http : HttpService,
    ) {}

    public subscribe (data : SubscriptionRequest) : Observable<Subscription> {
        return this.http.post('endpoint://subscription.subscribe', {
            body: data
        }).pipe(
            retry(1),
            take(1),
            map(response => response.subscription),
            catchError(error => {
                console.warn('subscribe error:', error);
                return throwError(error);
            })
        );
    }

    public fetchSubscription () : Observable<SubscriptionDetails> {
        return this.http.get('endpoint://subscription.getSubscription').pipe(
            retry(1),
            take(1),
            map(response => response.subscriptionDetails),
            catchError(error => {
                console.warn('fetchSubscription error:', error);
                return throwError(error);
            })
        );
    }

    public updateSubscription (data : UpdateSubscriptionRequest) : Observable<SubscriptionDetails> {
        return this.http.put('endpoint://subscription.updateSubscription', {
            body: data
        }).pipe(
            retry(1),
            take(1),
            map(response => response.subscriptionDetails),
            catchError(error => {
                console.warn('updateSubscription error:', error);
                return throwError(error);
            })
        );
    }

    public fetchInvoices () : Observable<SubscriptionInvoice[]> {
        return this.http.get('endpoint://subscription.getInvoices').pipe(
            retry(1),
            take(1),
            map(response => response.invoices),
            catchError(error => {
                console.warn('fetchInvoices error:', error);
                return throwError(error);
            })
        );
    }

    public payTheInvoice (invoiceId : string, fundingSource : any = null) : Observable<SubscriptionInvoice> {
        return this.http.post('endpoint://subscription.payTheInvoice', {
            urlParams: { invoiceId },
            body: { fundingSource }
        }).pipe(
            retry(1),
            take(1),
            map(response => response.invoice),
            catchError(error => {
                console.warn('payTheInvoice error:', error);
                return throwError(error);
            })
        );
    }

    public fetchNextBill () : Observable<UpcomingInvoice> {
        return this.http.get('endpoint://subscription.getNextBill').pipe(
            retry(1),
            take(1),
            map(response => response.invoice),
            catchError(error => {
                console.warn('fetchNextBill error:', error);
                return throwError(error);
            })
        );
    }
}
