import {Injectable} from '@angular/core';
import {HttpService} from '../../services/http.service';
import {catchError, map, retry, take} from 'rxjs/operators';
import {Observable, throwError} from 'rxjs';
import { HttpErrorResponse } from '@angular/common/http';
import {PaymentMethodType} from '../../services/payment.service';

export type DisputeType = 'NOT_MY_VEHICLE' | 'VEHICLE_STOLEN' | 'VEHICLE_SOLD' | 'OWNER_DECEASED' | 'OWNER_BANKRUPTCY';
export type DisputeReason = 'NONE' | DisputeType;

export interface DisputeReasonOption {
    display: string;
    value: DisputeReason;
}

export interface Transaction {
    lpn: string;
    lps: string;
    item_id: string;
    toll_date: string;
    toll_location: string;
    invoice_amount: number;
    disputable: boolean;
}

export interface AllInvoicesHttpResponseModel {
    invoices: InvoiceItemBackendModel[];
    surcharge?: number;

}

export interface InvoiceItemBackendModel {
    invoice_id: string;
    invoice_name: string;
    invoice_amount: number;
    invoice_date: string;
    invoice_expiration_date: string;
    invoice_type: 'TOLL_USAGE' | 'SUBSCRIPTION_RENEWAL' | string;
    items: Transaction[];
}

export interface TransactionItem {
    id: string;
    location: string;
    amount: number;               // transaction.invoice_amount
    createTs: number;
    isDisputable: boolean;        // transaction.disputable
    disputeReason: DisputeReason;
    transaction: Transaction;
}

export interface LicensePlate {
    lpNumber: string                     // full license plate (lps + lpn)
    amount: number;                      // calculated amount (w/o disputed)
    transactionItems: TransactionItem[];
}

export interface InvoiceItemUIModel {
    id: string;                  // tracking
    name: string;                // to show
    amount: number;              // calculated amount (w/o disputed)
    transactionCount: number;    // calculated transactions count (w/o disputed)
    createTs: number;            // creation timestamp
    hoursLeft: number;
    isPassedDue: boolean;
    isLowTimeLeft: boolean;
    showTimeLeft: boolean;
    isSelectedToPay: boolean;          // is checked in 'invoice-list' layout
    invoice: InvoiceItemBackendModel;            // original invoice received from the server
    licensePlates: LicensePlate[];
}

export interface InvoicePaymentTransaction {
    item_id: string;
    approved: boolean;
    dispute_type: DisputeType;
}

export interface InvoicePaymentInvoice {
    invoice_id: string;
    items: InvoicePaymentTransaction[];
}

export interface InvoicePaymentRequestData {
    invoices: InvoicePaymentInvoice[];
    verification_code: string;
    payment_method_type: PaymentMethodType;
    payment_method_id: null | string;
    return_url: null | string;  // /hook.html?...
    cancel_url: null | string;  // /hook.html?...
}

export interface InvoicePaymentResponse {
    status: 'OK' | 'ERROR';
    payment_complete?: boolean;
    transaction_id?: string;
    payment_intent?: {
        id?: string;
        client_secret?: string;
        amount?: number;
        currency?: string;
        approve_payment_url?: string;
    };
}

export interface InvoicePaymentResponseWithError {
    errorCode: null | number;
    metadata?: {
        license_plates_over_limit?: string;
    };
    response: null | InvoicePaymentResponse;
}

export const DEFAULT_INVOICES_PAYMENT_ERROR_CODE = 301;

@Injectable({
    providedIn: 'root'
})
export class InvoicesService {
    constructor(
        private http: HttpService,
    ) {
    }

    fetchInvoices(): Observable<AllInvoicesHttpResponseModel> {
        return this.http.get('endpoint://invoices.fetchAll')
            .pipe(
                retry(1),
                take(1),
                catchError(error => {
                    console.warn('fetchInvoices error:', error);
                    return throwError(error);
                })
            );
    }

    makePayment(requestData: InvoicePaymentRequestData): Observable<null | InvoicePaymentResponseWithError> {

        return this.http.post('endpoint://invoices.makePayment', {
            body: requestData
        }).pipe(
            take(1),
            map((response: InvoicePaymentResponse) => ({
                errorCode: response.status === 'OK' ? null : DEFAULT_INVOICES_PAYMENT_ERROR_CODE,
                response
            })),
            catchError((error: HttpErrorResponse) => {
                console.warn('makePayment error:', error);
                return throwError({
                    errorCode: error.error.status_code || error.error.status || DEFAULT_INVOICES_PAYMENT_ERROR_CODE,
                    metadata: error.error.metadata,
                    response: null
                });
            })
        );
    }

    getDisputeReasonOptions(): DisputeReasonOption[] {
        const reasons: DisputeReason[] = [
            'NONE',
            'NOT_MY_VEHICLE',
            'VEHICLE_STOLEN',
            'VEHICLE_SOLD',
            'OWNER_DECEASED',
            'OWNER_BANKRUPTCY'
        ];

        return reasons.map((reason: DisputeReason) => ({
            display: `invoices.dispute_reasons.${reason.toLowerCase()}`,
            value: reason
        }));
    }
}
