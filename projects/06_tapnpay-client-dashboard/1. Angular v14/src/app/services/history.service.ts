import { Injectable } from '@angular/core';
import {HttpService} from './http.service';
import {catchError, map, retry, take} from 'rxjs/operators';
import {Observable, throwError} from 'rxjs';
import {Pagination} from '../modules/app/_widgets/pagination/pagination.component';
import {PaymentMethodWallet} from './stripe.service';
import {PaymentMethodCard} from './payment.service';

export type InvoiceHistoryPaymentMethod = 'DCB' | 'PAYPAL' | 'WALLET' | PaymentMethodWallet | PaymentMethodCard;

export interface InvoiceHistoryItem {
    invoice_id : string;
    payment_date : string;
    invoice_name : string;
    currency : string;
    toll_usages : number;
    invoice_amount : number;
    discount_amount : number;
    payment_amount : number;
    payment_method_type : InvoiceHistoryPaymentMethod;
}

export interface TransactionHistoryItem {
    id : string;
    payment_amount : number;
    invoice_amount : number;
    currency : string;
    transaction_date : string;
    location : string;
    lps : string;
    lpn : string;
    status : string;
}

export interface InvoiceHistoryResponse {
    page : Pagination;
    invoices : InvoiceHistoryItem[];
}

export interface TransactionHistoryResponse {
    page : Pagination;
    tolls : TransactionHistoryItem[];
}

export interface InvoiceHistoryRequestData {
    page : number;
    page_size : number;
    from_date : string;
    to_date : string;
}

export interface TransactionHistoryRequestData {
    page : number;
    page_size : number;
    invoice_id : number;
    paid : boolean;
    disputed : boolean;
    from_date : string;
    to_date : string;
}

export interface SpecificInvoiceHistoryToll {
    id : string;
    payment_amount : number;
    currency : string;
    transaction_date : string;
    location : string;
    lps : string;
    lpn : string;
    status : string;
}

export interface SpecificInvoiceHistoryInvoice {
    invoice_id : string;
    payment_date : string;
    invoice_name : string;
    currency : string;
    items : number;
    invoice_amount : number;
    discount_amount : number;
    payment_amount : number;
    payment_method_type : string;
}

export interface SpecificInvoiceHistoryPBM {
    id : string;
    payment_amount : number;
    currency : string;
    pay_by_name : string;
    lps : string;
    lpn : string;
}

export interface SpecificInvoiceHistoryFee {
    id : string;
    payment_amount : number;
    currency : string;
    lps : string;
    lpn : string;
}

export interface SpecificInvoiceHistory {
    fee : SpecificInvoiceHistoryFee;
    invoice : SpecificInvoiceHistoryInvoice;
    tolls : SpecificInvoiceHistoryToll[];
    pbm	: SpecificInvoiceHistoryPBM;
}

@Injectable({
    providedIn: 'root'
})
export class HistoryService {
    constructor (
        private http : HttpService,
    ) {}

    fetchInvoiceHistory (requestData : InvoiceHistoryRequestData) : Observable<InvoiceHistoryResponse> {
        return this.http.post('endpoint://history.fetchInvoices', {
            body: requestData
        })
            .pipe(
                retry(1),
                take(1),
                catchError(error => {
                    console.warn('fetchInvoiceHistory error:', error);
                    return throwError(error);
                })
            );
    }

    fetchTransactionsHistory (requestData : TransactionHistoryRequestData) : Observable<TransactionHistoryResponse> {
        return this.http.post('endpoint://history.fetchTransactions', {
            body: requestData
        })
            .pipe(
                retry(1),
                take(1),
                catchError(error => {
                    console.warn('fetchTransactionsHistory error:', error);
                    return throwError(error);
                })
            );
    }

    fetchSpecificInvoiceHistory (invoiceId : string) : Observable<SpecificInvoiceHistory> {
        return this.http.get('endpoint://history.fetchInvoiceHistory', {
            urlParams: { invoiceId }
        })
            .pipe(
                retry(1),
                take(1),
                catchError(error => {
                    console.warn('fetchSpecificInvoiceHistory error:', error);
                    return throwError(error);
                })
            );
    }
}
