import {Injectable} from '@angular/core';
import {HttpService} from './http.service';
import {catchError, map, take} from 'rxjs/operators';
import {Observable, throwError} from 'rxjs';
import {deleteJsonFromLocalStorage, readJsonFromLocalStorage, saveJsonToLocalStorage} from '../lib/utils';

export interface AccountSummaryLicensePlate {
    lp : string;
    status : string;
}

export interface AccountSummary {
    phone_number : string;
    phone_carrier : string;
    language : string;
    account_status : string;
    toll_authority : string;
    terms_accepted : string;
    lock_date : string;
    locked_until : string;
    payment_channel : string;
    plates : AccountSummaryLicensePlate[];
    total_invoices_amount : number;
    total_invoices : number;
    total_invoices_paid : number;
    average_invoice_amount : number;
    total_disputes : number;
    last_paid_invoice_date : string;
    outstanding_disputes_count : number;
    outstanding_disputes_amount : number;
}

export interface OutstandingInvoiceTransaction {
    lpn : string;
    lps : string;
    item_id : string;
    date? : string;
    toll_date? : string;
    description? : string;
    toll_location? : string;
    amount? : number;
    invoice_amount? : number;
    disputable : boolean;
}

export interface OutstandingInvoice {
    items : OutstandingInvoiceTransaction[];
    invoice_id : string;
    invoice_name : string;
    invoice_date : string;
    invoice_expiration_date : string;
    invoice_amount : number;
}

export interface InvoiceExtension {
    invoice_id : string;
    invoice_name : string;
    extended_hours : number;
    original_due_date : string;
    final_due_date : string;
}

export interface OutstandingInvoiceWithExtension {
    items : OutstandingInvoiceTransaction[];
    invoice_id : string;
    invoice_name : string;
    invoice_date : string;
    invoice_expiration_date : string;
    invoice_amount : number;
    // ------------------------------
    extended_hours : number;
    original_due_date : string;
    final_due_date : string;
    // ------------------------------
    hours : number;
}

export interface ExtendInvoiceDateRequestData {
    invoice_id : string;
    hours : number;
}

export interface TransactionsRequestData {
    page : number;
    page_size : number;
    include_succeeded : boolean;
    include_failed : boolean;
}

export interface ResponsePagination {
    total_pages : number;
    total_elements : number;
    next : boolean;
    previous : boolean;
    page : number;
    page_size : number;
}

export interface TransactionInvoice {
    invoice_id : string;
    invoice_name : string;
    invoice_type : string;
}

export interface Transaction {
    date : string;
    amount : number;
    currency : string;
    payment_channel : string;
    status : string;
    invoices : TransactionInvoice[];
}

export interface TransactionFilters {
    visibility : number;
}

export interface TransactionResponse {
    page : ResponsePagination;
    transactions : Transaction[];
    filters? : TransactionFilters;
}

export interface SmsLogRequestData {
    page_size : number;
    exclusive_start_key : string;
    from_date : string;
    to_date : string;
}

export interface SmsLogItem {
    date : string;
    sender : string;
    recipient : string;
    text : string;
}

export interface SmsLogFilters {
    from : null | string;
    to : null | string;
}

export interface SmsLogResponse {
    exclusive_start_key : string;
    items : SmsLogItem[];
    filters? : SmsLogFilters;
}

export const TRANSACTION_FETCH_COUNT = 20;
export const SMS_LOG_FETCH_COUNT = 10;

export const ACCOUNT_STATUS_COLOR = {
    'ACTIVE':             '#4875e7',
    'INACTIVE':           '#a7a7a7',
    'CLOSED_BY_OWNER':    '#6d6d6d',
    'SOFT_LOCK':          '#ff8686',
    'HARD_LOCK':          '#e64f4f',
    'FRAUD':              '#9855f9',
    'PERMANENTLY_CLOSED': '#6d6d6d',
    'PAYMENT_LOCK':       '#e89727',
    // Generics:
    '_LOCK':              '#e64f4f'
};

export const ACCOUNT_LOCAL_STORAGE_KEY = 'accounts';

export interface Dispute {
    account_invoice_item_id : string;
    invoice_id : string;
    invoice_name : string;
    toll_date : string;
    invoice_amount : number;
    dispute_date : string;
    dispute_reason : string;
}

@Injectable({
    providedIn: 'root'
})
export class AccountService {
    constructor (
        private http : HttpService
    ) {}

    fetchSummary (accountId : string) : Observable<AccountSummary> {
        return this.http.get('endpoint://account.getSummary', {
            urlParams: { accountId }
        }).pipe(
            take(1),
            // map(response => {
            //     response.account_status = 'SOFT_LOCK';
            //     response.lock_date = '2021-05-19T13:17:44.777+00:00';
            //     return response;
            // }),
            catchError(error => {
                console.warn('fetchSummary error:', error);
                return throwError(error);
            })
        )
    }

    fetchInvoices (accountId : string) : Observable<OutstandingInvoice[]> {
        return this.http.get('endpoint://account.getInvoices', {
            urlParams: { accountId }
        }).pipe(
            take(1),
            map(response => response.invoices),
            catchError(error => {
                console.warn('fetchInvoices error:', error);
                return throwError(error);
            })
        )
    }

    fetchInvoiceExtensions (accountId : string) : Observable<InvoiceExtension[]> {
        return this.http.get('endpoint://account.getInvoiceExtensions', {
            urlParams: { accountId }
        }).pipe(
            take(1),
            map(response => response.items),
            catchError(error => {
                console.warn('fetchInvoiceExtensions error:', error);
                return throwError(error);
            })
        )
    }

    async fetchExtendedInvoices (accountId : string) : Promise<OutstandingInvoiceWithExtension[]> {
        const [ invoices, extensions ] : [ OutstandingInvoice[], InvoiceExtension[] ] = await Promise.all([
            this.fetchInvoices(accountId).toPromise().catch(() => null),
            this.fetchInvoiceExtensions(accountId).toPromise().catch(() => null),
        ]);

        if (!invoices) {
            return null;
        }

        return invoices.map(invoice => {
            const extension: InvoiceExtension = (extensions || []).find(item => item.invoice_id === invoice.invoice_id) || <any>{};
            const invoiceWithExtensions = <OutstandingInvoiceWithExtension>invoice;

            invoiceWithExtensions.extended_hours = extension.extended_hours || 0;
            invoiceWithExtensions.original_due_date = extension.original_due_date || null;
            invoiceWithExtensions.final_due_date = extension.final_due_date || null;
            invoiceWithExtensions.hours = null;

            return invoiceWithExtensions;
        });
    }

    saveInvoiceExtension (accountId : string, requestData : ExtendInvoiceDateRequestData) : Observable<boolean> {
        return this.http.post('endpoint://account.saveInvoiceExtension', {
            body: requestData,
            urlParams: { accountId }
        }).pipe(
            take(1),
            map(response => response.status === 'OK'),
            catchError(error => {
                console.warn('saveInvoiceExtension error:', error);
                return throwError(error);
            })
        );
    }

    fetchTransactions (accountId : string, requestData : TransactionsRequestData) : Observable<TransactionResponse> {
        return this.http.post('endpoint://account.getTransactions', {
            body: requestData,
            urlParams: { accountId }
        }).pipe(
            take(1),
            catchError(error => {
                console.warn('fetchTransactions error:', error);
                return throwError(error);
            })
        );
    }

    fetchInvoiceDetails (accountId : string, invoiceId : string) : Observable<OutstandingInvoice> {
        return this.http.get('endpoint://account.getInvoiceDetails', {
            urlParams: { accountId, invoiceId }
        }).pipe(
            take(1),
            catchError(error => {
                console.warn('fetchInvoiceDetails error:', error);
                return throwError(error);
            })
        );
    }

    fetchSmsLog (accountId : string, requestData : SmsLogRequestData) : Observable<SmsLogResponse> {
        return this.http.post('endpoint://account.getSmsLog', {
            body: requestData,
            urlParams: { accountId }
        }).pipe(
            take(1),
            catchError(error => {
                console.warn('fetchSmsLog error:', error);
                return throwError(error);
            })
        );
    }

    reinstateAccount (accountId : string, note : string = '') : Observable<boolean> {
        return this.http.delete('endpoint://account.reinstate', {
            urlParams: { accountId },
            body: { note }
        }).pipe(
            take(1),
            map(response => response.status === 'OK'),
            catchError(error => {
                console.warn('reinstateAccount error:', error);
                return throwError(error);
            })
        );
    }

    sendSMS (accountId : string, text : string) : Observable<boolean> {
        return this.http.post('endpoint://account.sendSMS', {
            urlParams: { accountId },
            body: { text }
        }).pipe(
            take(1),
            map(response => response.status === 'OK'),
            catchError(error => {
                console.warn('sendSMS error:', error);
                return throwError(error);
            })
        );
    }

    sendPIN (accountId : string) : Observable<string> {
        return this.http.post('endpoint://account.sendPIN', {
            urlParams: { accountId }
        }).pipe(
            take(1),
            map(response => response.pin),
            catchError(error => {
                console.warn('sendPIN error:', error);
                return throwError(error);
            })
        );
    }

    closeAccount (accountId : string) : Observable<boolean> {
        return this.http.delete('endpoint://account.close', {
            urlParams: { accountId }
        }).pipe(
            take(1),
            map(response => response.status === 'OK'),
            catchError(error => {
                console.warn('closeAccount error:', error);
                return throwError(error);
            })
        );
    }

    blockAccount (accountId : string) : Observable<boolean> {
        return this.http.put('endpoint://account.block', {
            urlParams: { accountId },
            body: { note: '' }
        }).pipe(
            take(1),
            map(response => response.status === 'OK'),
            catchError(error => {
                console.warn('blockAccount error:', error);
                return throwError(error);
            })
        );
    }

    restoreAccountsFromLocalStorage () {
        return readJsonFromLocalStorage(ACCOUNT_LOCAL_STORAGE_KEY, {
            accounts: [],
            activeAccountId: null
        });
    }

    saveAccountsToLocalStorage (data) {
        saveJsonToLocalStorage(ACCOUNT_LOCAL_STORAGE_KEY, data);
    }

    deleteAccountsFromLocalStorage () {
        deleteJsonFromLocalStorage(ACCOUNT_LOCAL_STORAGE_KEY);
    }

    fetchDisputes (accountId : string) : Observable<Dispute[]> {
        return this.http.get('endpoint://account.getDisputes', {
            urlParams: { accountId }
        }).pipe(
            take(1),
            catchError(error => {
                console.warn('fetchDisputes error:', error);
                return throwError(error);
            })
        );
    }
}
