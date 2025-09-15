import { Injectable } from '@angular/core';
import {Observable, throwError} from 'rxjs';
import {isArray} from 'lodash';
import {catchError, map, retry, take} from 'rxjs/operators';
import {HttpService} from './http.service';
import {UserService} from './user.service';
import {isSameObjectsLayout, updateObject} from '../lib/utils';
import {Rate} from './rates.service';

export class Attachment {
    constructor (source : any = {}) {
        for (let key in source) {
            key in this && (this[key] = source[key]);
        }
    }

    public id : number = 0;
    public fileId : number = 0;
    public uuid : string = '';
    public name : string = '';
    public publicComment : string = '';
    public privateComment : string = '';
    public type : string = '';
}

export class CompanyServiceItem {
    id : number = 0;
    name : string = '';
    shortName : string = '';
    from : string = '';
    to : string = '';
    price : number = 0;
    rate : number = 0;
    unit : string = '';
}
export class ClientCompany {
    id : number = null;
    name : string = null;
}

export class Contact {
    constructor (source : any = {}) {
        for (let key in source) {
            key in this && (this[key] = source[key]);
        }
    }

    public id : number = 0;
    public inactive : boolean = false;
    public primary : boolean = false;
    public email : string = '';
    public fax : string = '';
    public fullName : string = '';
    public notes : string = '';
    public phone : string = '';
    public position : string = '';
    public title : string = '';
}

export class ShippingAddress {
    companyName : string = null;
    firstName : string = null;
    lastName : string = null;
    street : string = null;
    suite : string = null;
    zipCode : string = null;
    state : string = null;
    country : string = null;
    city : string = null;
}

export class Offer {
    constructor (source : any = {}) {
        for (let key in source) {
            key in this && (this[key] = source[key]);
        }
    }

    key : string = null;
    projectKey : string = null;
    statusId : number = null;
    coordinatorId : number = null;
    currency : string = null;
    currencyRate : number = null;
    updateCurrencyRate : boolean = false;
    net : number = null;
    gross : number = null;
    description : string = null;
    created: number = null;
    client : ClientCompany = null;
    contact : Contact = null;
    externalId : string = null;
    priorityId : number = null;
    deliveryTypeId : number = null;
    days : number = null;
    fieldId : number = null;
    translationTypeId : number = null;
    notary : boolean = false;
    tax : any = null;
    sendBill : boolean = false;
    emailNote : string = null;
    instruction : string = null;
    attachments : Attachment[] = [];
    shippingAddress : ShippingAddress = null;
    services : OfferServiceItem[] = null;
}

export class OfferServiceItem {
    constructor (source : any = {}) {
        for (let key in source) {
            key in this && (this[key] = source[key]);
        }
    }

    serviceId : number = null;
    name : string = null;
    shortName : string = null;
    from : string = null;
    to : string = null;
    basePrice : number = 0;
    price : number = 0;
    unit : string = null;
    rate : string = null;
    billable : boolean = true;
    in : number = 0;
    outRounded : number = 0;
    outPrecise : number = 0;
    discount : number = 0;
    net : number = 0;
    gross : number = 0;
    ratio : number = 10000;
    attachments : string[] = [];
}

export class OfferStatus {
    id : number;  // -1 == any
    key : string;
    display : string;
}

class OfferStatusColor {
    bg : string;
    text : string;
}

export class OfferColumn {
    display : string;
    key : string;
    isVisible : boolean;
    isSortable : boolean;
    sortDirection? : number;
}

class OffersStatusesColors {
    new : OfferStatusColor = {
        bg: '#5b7cd2',
        text: '#fff'
    };

    sent : OfferStatusColor = {
        bg: '#9059bd',
        text: '#fff'
    };

    accepted : OfferStatusColor = {
        bg: '#499036',
        text: '#fff'
    };

    rejected : OfferStatusColor = {
        bg: '#c14848',
        text: '#fff'
    };
}

export class OffersSettings {
    statusesColors : OffersStatusesColors = new OffersStatusesColors();
    colorizeEntireRow : boolean = false;
    columns : OfferColumn[] = [
        {
            display: 'offers.columns.status',
            key: 'statusKey',
            isVisible: true,
            isSortable: true,
            sortDirection: 1
        },
        {
            display: 'offers.columns.offer',
            key: 'offerKey',
            isVisible: true,
            isSortable: true,
            sortDirection: -1
        },
        {
            display: 'offers.columns.company',
            key: 'client',
            isVisible: true,
            isSortable: true,
            sortDirection: 1
        },
        {
            display: 'offers.columns.contact',
            key: 'contact',
            isVisible: true,
            isSortable: true,
            sortDirection: 1
        },
        {
            display: 'offers.columns.phone',
            key: 'phone',
            isVisible: true,
            isSortable: true,
            sortDirection: 1
        },
        {
            display: 'offers.columns.email',
            key: 'email',
            isVisible: true,
            isSortable: true,
            sortDirection: 1
        },
        {
            display: 'offers.columns.net',
            key: 'net',
            isVisible: true,
            isSortable: true,
            sortDirection: 1
        },
        {
            display: 'offers.columns.gross',
            key: 'gross',
            isVisible: true,
            isSortable: true,
            sortDirection: 1
        },
        {
            display: 'offers.columns.currency',
            key: 'currencyKey',
            isVisible: true,
            isSortable: true,
            sortDirection: 1
        },
        {
            display: 'offers.columns.coordinator',
            key: 'coordinator',
            isVisible: true,
            isSortable: true,
            sortDirection: 1
        },
        {
            display: 'offers.columns.date',
            key: 'created',
            isVisible: true,
            isSortable: true,
            sortDirection: 1
        },
        {
            display: 'offers.columns.description',
            key: 'description',
            isVisible: true,
            isSortable: false
        },
    ];
}

export interface OfferTransaction {
    amount : number;
    comment : string;
    created : string;
    currency : string;
    exchangeRate : number;
    fees : number;
    paymentProvider : string;
    received : number;
    status : string;
    transactionId : string;
    updated : string;
}

export interface OfferTransactionsResponse {
    currency : string;
    totalAmount : number;
    totalFees : number;
    totalReceived : number;
    transactions : OfferTransaction[];
}


@Injectable({
    providedIn: 'root'
})
export class OffersService {
    public OfferizeData : any = null;

    public set offerizeData (offerizeData : any) {
        this.OfferizeData = offerizeData;
    }

    public get offerizeData () : any {
        const offerizeData : any = this.OfferizeData;
        this.OfferizeData = null;
        return offerizeData;
    }

    constructor (
        private http : HttpService,
        private userService : UserService
    ) {}

    // page={page}&size={size}&status={status}&phone={phone}&email={email}&from={from}&to={to}&company={company}&contact={contact}&name={name}
    public fetchOffers (params : any) : Observable<any> {
        return this.http.get('endpoint://offers.get', {
            params
        }).pipe(
            retry(1),
            take(1),
            catchError(error => {
                console.warn('fetchOffers error:', error);
                return throwError(error);
            })
        );
    }

    public fetchOffer (offerKey : string, fromAddress : string = null) : Observable<any> {
        return this.http.get('endpoint://offers.getOne', {
            params: fromAddress ? { fromAddress } : null,
            urlParams: { offerKey },
        })
        .pipe(
            retry(1),
            take(1),
            catchError(error => {
                console.warn('fetchOffer error:', error);
                return throwError(error);
            })
        );
    }

    public fetchOfferStatuses (addAny : boolean = false) : Observable<OfferStatus[]> {
        return this.http.get('endpoint://offers.getStatuses').pipe(
            retry(1),
            take(1),
            map(response => {
                let statuses = response.statuses.map(status => {
                    return {
                        id: status.id,
                        key: status.key,
                        display: ('offers.statuses.' + status.key.toLowerCase().replace(/\./g, '_'))
                    };
                });

                if (addAny) {
                    statuses = [
                        {
                            id: -1,
                            key: 'any',
                            display: 'offers.statuses.any'
                        },
                        ...statuses
                    ];
                }

                return statuses;
            }),
            catchError(error => {
                console.warn('fetchOfferStatuses error:', error);
                return throwError(error);
            })
        );
    }

    public fetchOfferEmail (offerKey : string) : Observable<string> {
        return this.http.get('endpoint://offers.getEmail', {
            urlParams: { offerKey }
        }).pipe(
            retry(1),
            take(1),
            map(response => response),  // TODO .text()
            catchError(error => {
                console.warn('fetchOfferEmail error:', error);
                return throwError(error);
            })
        );
    }

    public fetchOfferEmailContent (uuid : string) : Observable<string> {
        return this.http.get('endpoint://offers.getEmailContent', {
            urlParams: { uuid }
        }).pipe(
            retry(1),
            take(1),
            map(response => response),  // TODO .text()
            catchError(error => {
                console.warn('fetchOfferEmailContent error:', error);
                return throwError(error);
            })
        );
    }

    public fetchOfferTransactions (offerKey : string) : Observable<OfferTransactionsResponse> {
        return this.http.get('endpoint://offers.getTransactions', {
            urlParams: { offerKey }
        }).pipe(
            retry(1),
            take(1),
            catchError(error => {
                console.warn('fetchOfferTransactions error:', error);
                return throwError(error);
            })
        );
    }

    public saveTransaction (data : any) : Observable<any> {
        return this.http.post('endpoint://offers.saveTransaction', {
            body: data
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

    public fetchOfferHistory (offerKey : string) : Observable<any[]> {
        return this.http.get('endpoint://offers.getHistory', {
            urlParams: { offerKey }
        }).pipe(
            retry(1),
            take(1),
            map(response => response.records),
            catchError(error => {
                console.warn('fetchOfferHistory error:', error);
                return throwError(error);
            })
        );
    }

    public fetchCompanyServices (clientId : number = null) : Observable<any> {
        return this.http.get('endpoint://offers.getAvailCompanyServices', {
            params: clientId !== null ? { clientId: String(clientId) } : null,
        }).pipe(
            retry(1),
            take(1),
            catchError(error => {
                console.warn('fetchCompanyServices error:', error);
                return throwError(error);
            })
        );
    }

    /*
    public fetchOffersStatusesColors () : Observable<OffersStatusesColors> {
        return this.userService.fetchFromStorage('offers_statuses_colors').pipe(
            retry(1),
            take(1),
            map(colors => {
                if (!colors) {
                    colors = {
                        new: {
                            bg: '#5b7cd2',
                            text: '#fff'
                        },
                        sent: {
                            bg: '#9059bd',
                            text: '#fff'
                        },
                        accepted: {
                            bg: '#499036',
                            text: '#fff'
                        },
                        rejected: {
                            bg: '#c14848',
                            text: '#fff'
                        }
                    };

                    this.userService.saveToStorage('offers_statuses_colors', colors);
                }

                return colors;
            }),
            catchError(error => {
                console.warn('fetchOffersStatusesColors error:', error);
                return throwError(error);
            })
        );
    }
    */

    public fetchOffersSettings () : Observable<OffersSettings> {
        // this.userService.deleteFromStorage('offers_settings');
        return this.userService.fetchFromStorage('offers_settings').pipe(
            retry(1),
            take(1),
            map((settings : OffersSettings) => {
                const defaultSettings = new OffersSettings();

                if (!isSameObjectsLayout(defaultSettings, settings || {})) {
                    // TODO: check colors validity and contrast
                    settings = updateObject(defaultSettings, settings || {});
                    this.userService.saveToStorage('offers_settings', settings);
                }

                return settings;
            }),
            catchError(error => {
                console.warn('fetchOffersSettings error:', error);
                return throwError(error);
            })
        );
    }

    public saveOffersSettings (settings : any) : Promise<boolean> {
        return this.userService.saveToStorage('offers_settings', settings);
    }

    public saveOffer (offer : any) : Observable<any> {
        return this.http.post('endpoint://offers.save', {
            body: offer
        }).pipe(
            retry(1),
            take(1),
            catchError(error => {
                console.warn('saveOffer error:', error);
                return throwError(error);
            })
        );
    }

    public fetchOffersListState () : Observable<any> {
        return this.userService.fetchFromStorage('offers_list_state').pipe(
            retry(1),
            take(1),
            catchError(error => {
                console.warn('fetchOffersListState error:', error);
                return throwError(error);
            })
        );
    }

    public saveOffersListState (state : any) : Promise<boolean> {
        return this.userService.saveToStorage('offers_list_state', state);
    }

    public presignFile (fileName : string) : any {
        return this.http.post2('endpoint://files.presign', {
            body: {
                fileName
            }
        });
    }

    public sendQuote (offerKey : string, quoteAttrs : any) : Observable<any> {
        return this.http.post('endpoint://offers.sendQuote', {
            urlParams: { offerKey },
            body: quoteAttrs
        }).pipe(
            retry(1),
            take(1),
            map(() => null),
            catchError(error => {
                console.warn('sendQuote error:', error);
                return error.messageKey;
            })
        );
    }
}
