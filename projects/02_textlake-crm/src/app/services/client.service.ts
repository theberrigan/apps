import { Injectable } from '@angular/core';
import {Observable, throwError} from 'rxjs';
import {isArray} from 'lodash';
import {catchError, map, retry, take} from 'rxjs/operators';
import {HttpService} from './http.service';
import {UserService} from './user.service';
import {Rate} from './rates.service';
import {Contact} from './offers.service';

export class Client {
    id : number = 0;
    addressLine : string = '';
    city : string = '';
    country : string = '';
    email : string = '';
    legalName : string = '';
    name : string = '';
    phone : string = '';
    zip : string = '';
    addressLine2 : string = '';
    email2 : string = '';
    fax : string = '';
    note : string = '';
    phone2 : string = '';
    state : string = '';
    tin : string = '';
    bankAccount : string = '';
    bankName : string = '';
    currency : string = '';
    paymentType : string = '';
    tax : number = 0;
    deleted : boolean = false;
    preferredLanguage : string = '';
}

export class ClientBalanceRecord {
    public amount : number = 0;
    public balance : number = 0;
    public comment : string = '';
    public created : string = '';
    public credited : number = 0;
    public currency : string = '';
    public exchangeRate : number = 0;
    public offerKey : string = '';
    public projectKey : string = '';
}

export class ClientBalance {
    public balance : number = 0;
    public items : ClientBalanceRecord[] = [];
}

export interface Transaction {
    amount : number;
    comment : string;
    currency : string;
}

@Injectable({
    providedIn: 'root'
})
export class ClientsService {
    constructor (
        private http : HttpService,
        private userService : UserService
    ) {}

    public fetchClients (params : any) : Observable<any> {
        return this.http.get('endpoint://clients.get', {
            params
        }).pipe(
            retry(1),
            take(1),
            catchError(error => {
                console.warn('fetchClients error:', error);
                return throwError(error);
            })
        );
    }

    public loadClient (clientId : number) : Observable<any> {
        return this.http.get('endpoint://clients.getInfoById', {
            urlParams: { clientId }
        }).pipe(
            retry(1),
            take(1),
            map(response => response.client as Client),
            catchError(error => {
                console.warn('loadClient error:', error);
                return throwError(error);
            })
        );
    }

    public fetchClientCompanies (name : string) : Observable<any> {
        return this.http.get('endpoint://clients.getCompanies', {
            params: { name }
        }).pipe(
            retry(1),
            take(1),
            catchError(error => {
                console.warn('fetchClientCompanies error:', error);
                return throwError(error);
            })
        );
    }

    public fetchClientCompanyContacts (clientCompanyId : number) : Observable<any> {
        return this.http.get('endpoint://clients.getCompanyContacts', {
            urlParams: { clientCompanyId }
        }).pipe(
            retry(1),
            take(1),
            catchError(error => {
                console.warn('fetchClientCompanyContacts error:', error);
                return throwError(error);
            })
        );
    }

    public createClientCompany (name : string) : Observable<any> {
        return this.http.post('endpoint://clients.createCompany', {
            urlParams: { name: encodeURIComponent(name) }
        }).pipe(
            retry(1),
            take(1),
            catchError(error => {
                console.warn('createClientCompany error:', error);
                return throwError(error);
            })
        );
    }

    public createClient (client : Client) : Observable<any> {
        return this.http.post('endpoint://clients.create', {
            body: { client }
        }).pipe(
            retry(1),
            take(1),
            map(response => response.client as Client),
            catchError(error => {
                console.warn('createClient error:', error);
                return throwError(error);
            })
        );
    }

    public saveClient (client : Client) : Observable<any> {
        return this.http.put('endpoint://clients.saveOne', {
            body: { client },
            urlParams: {
                clientId: client.id
            }
        }).pipe(
            retry(1),
            take(1),
            map(response => response.client as Client),
            catchError(error => {
                console.warn('saveClient error:', error);
                return throwError(error);
            })
        );
    }

    public createContact (clientId : number, contact : Contact) : Observable<any> {
        return this.http.post('endpoint://clients.createContact', {
            body: { contact },
            urlParams: {
                clientId
            }
        }).pipe(
            retry(1),
            take(1),
            map(response => response.contact as Contact),
            catchError(error => {
                console.warn('createContact error:', error);
                return throwError(error);
            })
        );
    }

    public saveContact (clientId : number, contact : Contact) : Observable<any> {
        return this.http.put('endpoint://clients.saveContact', {
            body: { contact },
            urlParams: {
                clientId,
                contactId: contact.id
            }
        }).pipe(
            retry(1),
            take(1),
            map(response => response.contact as Contact),
            catchError(error => {
                console.warn('saveContact error:', error);
                return throwError(error);
            })
        );
    }

    public fetchClientsListState () : Observable<any> {
        return this.userService.fetchFromStorage('clients_list_state').pipe(
            retry(1),
            take(1),
            catchError(error => {
                console.warn('fetchClientsListState error:', error);
                return throwError(error);
            })
        );
    }

    public saveClientsListState (state : any) : Promise<boolean> {
        return this.userService.saveToStorage('clients_list_state', state);
    }


    public fetchRates (clientId : number) : Observable<Rate[]> {
        return this.http.get('endpoint://clients.getRates', {
            urlParams: { clientId }
        }).pipe(
            retry(1),
            take(1),
            map(response => response.rates as Rate[]),
            catchError(error => {
                console.warn('fetchRates error:', error);
                return throwError(error);
            })
        );
    }

    public fetchContacts (clientId : number) : Observable<Contact[]> {
        return this.http.get('endpoint://clients.getContacts', {
            urlParams: { clientId }
        }).pipe(
            retry(1),
            take(1),
            map(response => response.contacts as Contact[]),
            catchError(error => {
                console.warn('fetchContacts error:', error);
                return throwError(error);
            })
        );
    }

    public fetchBalance (clientId : number) : Observable<any> {
        return this.http.get('endpoint://clients.getBalance', {
            urlParams: { clientId }
        }).pipe(
            retry(1),
            take(1),
            map(response => response.balance as ClientBalance),
            catchError(error => {
                console.warn('fetchBalance error:', error);
                return throwError(error);
            })
        );
    }

    public saveTransaction (clientId : number, transaction : Transaction) : Observable<any> {
        return this.http.post('endpoint://clients.saveTransaction', {
            body: transaction,
            urlParams: {
                clientId
            }
        }).pipe(
            retry(1),
            take(1),
            map(response => response.transaction),
            catchError(error => {
                console.warn('saveTransaction error:', error);
                return throwError(error);
            })
        );
    }
}
