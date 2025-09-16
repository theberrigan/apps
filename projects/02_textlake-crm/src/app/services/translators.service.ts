import { Injectable } from '@angular/core';
import {HttpService} from './http.service';
import {UserService} from './user.service';
import {Observable, throwError} from 'rxjs';
import {catchError, map, retry, take} from 'rxjs/operators';
import {Address} from '../types/address.type';
import {updateObject} from '../lib/utils';
import {ProjectsSettings} from './projects.service';

export class TranslatorsSettings {
    colorizeEntireRow : boolean = false;
}

export class Translator {
    id : number = 0;
    nativeLanguage : string = '';
    firstName : string = '';
    middleName : string = '';
    lastName : string = '';
    legalName : string = '';
    color : string = null;
    email : string = '';
    email2 : string = '';
    phone : string = '';
    phone2 : string = '';
    fax : string = '';
    addressLine : string = '';
    addressLine2 : string = '';
    city : string = '';
    state : string = '';
    zip : string = '';
    country : string = '';
    comment : string = '';
    active : boolean = true;
    currency : string = '';
}

export class TranslatorServiceItem {
    companyServiceId : number = null;
    currency : string = null;
    extraService : boolean = false;
    fieldIds : number[] = [];
    id : number = 0;
    notary : boolean = false;
    price : number = 0;
    translationTypeId : number = null;
}

export class TranslatorFinancial {
    bankAccount : string = '';
    bankName : string = '';
    currency : string = '';
    dateOfBirth : string = null;
    ninLast4 : string = '';
    paymentType : string = '';
    personalNumber : string = '';
    placeOfBirth : string = '';
    placeOfBirthAddress : Address;
    taxAgency : string = '';
    taxAgencyAddress : Address;
    tin : string = '';
}

@Injectable({
    providedIn: 'root'
})
export class TranslatorsService {
    constructor (
        private http : HttpService,
        private userService : UserService
    ) {}

    public fetchTranslatorsSettings () : Observable<TranslatorsSettings> {
        return this.userService.fetchFromStorage('translators_settings').pipe(
            retry(1),
            take(1),
            map((settings : TranslatorsSettings) => updateObject(new TranslatorsSettings(), settings || {})),
            catchError(error => {
                console.warn('fetchTranslatorsSettings error:', error);
                return throwError(error);
            })
        );
    }

    public saveTranslatorsSettings (settings : any) : Promise<boolean> {
        return this.userService.saveToStorage('translators_settings', settings);
    }

    public fetchTranslatorsListState () : Observable<any> {
        return this.userService.fetchFromStorage('translators_list_state').pipe(
            retry(1),
            take(1),
            catchError(error => {
                console.warn('fetchTranslatorsListState error:', error);
                return throwError(error);
            })
        );
    }

    public saveTranslatorsListState (state : any) : Promise<boolean> {
        return this.userService.saveToStorage('translators_list_state', state);
    }

    public fetchTranslators (params : any) : Observable<Translator[]> {
        return this.http.get('endpoint://translators.getAll', {
            params
        }).pipe(
            retry(1),
            take(1),
            map(response => response.translators as Translator[]),
            catchError(error => {
                console.warn('fetchTranslators error:', error);
                return throwError(error);
            })
        );
    }

    public fetchTranslator (translatorId : number) : Observable<Translator> {
        return this.http.get('endpoint://translators.getOne', {
            urlParams: { translatorId }
        }).pipe(
            retry(1),
            take(1),
            map(response => response.translator as Translator),
            catchError(error => {
                console.warn('fetchTranslator error:', error);
                return throwError(error);
            })
        );
    }

    // public __testServices = {"services":[{"id":87,"companyServiceId":70,"price":2200,"translationTypeId":8,"fieldIds":[1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17],"notary":false,"extraService":false,"currency":"PLN"},{"id":88,"companyServiceId":1,"price":2200,"translationTypeId":8,"fieldIds":[1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17],"notary":false,"extraService":false,"currency":"PLN"},{"id":89,"companyServiceId":16,"price":2200,"translationTypeId":8,"fieldIds":[1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17],"notary":false,"extraService":false,"currency":"PLN"},{"id":90,"companyServiceId":14,"price":2200,"translationTypeId":8,"fieldIds":[1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17],"notary":false,"extraService":false,"currency":"PLN"},{"id":91,"companyServiceId":460,"price":3000,"translationTypeId":8,"fieldIds":[1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17],"notary":false,"extraService":false,"currency":"PLN"},{"id":92,"companyServiceId":59,"price":3000,"translationTypeId":8,"fieldIds":[1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17],"notary":false,"extraService":false,"currency":"PLN"}]};

    public fetchTranslatorServices (translatorId : number) : Observable<TranslatorServiceItem[]> {
        return this.http.get('endpoint://translators.getTranslatorServices', {
            urlParams: { translatorId }
        }).pipe(
            retry(1),
            take(1),
            map(response => {
                return (response.services || []) as TranslatorServiceItem[];
                // return this.__testServices.services as TranslatorServiceItem[];
            }),
            catchError(error => {
                console.warn('fetchTranslatorServices error:', error);
                return throwError(error);
            })
        );
    }

    public fetchTranslatorFinancial (translatorId : number) : Observable<TranslatorFinancial> {
        return this.http.get('endpoint://translators.getTranslatorFinancial', {
            urlParams: { translatorId }
        }).pipe(
            retry(1),
            take(1),
            map(response => response.financial as TranslatorFinancial),
            catchError(error => {
                console.warn('fetchTranslatorFinancial error:', error);
                return throwError(error);
            })
        );
    }

    public getTranslatorSSN (translatorId : number) : Observable<string> {
        return this.http.get('endpoint://translators.getTranslatorSSN', {
            urlParams: { translatorId }
        }).pipe(
            retry(1),
            take(1),
            map(response => response.nationalIdentificationNumber || ''),
            catchError(error => {
                console.warn('getTranslatorSSN error:', error);
                return throwError(error);
            })
        );
    }

    public deleteService (translatorId : number, serviceId : number) : Observable<any> {
        return this.http.delete('endpoint://translators.deleteService', {
            urlParams: {
                translatorId,
                serviceId
            }
        }).pipe(
            retry(1),
            take(1),
            catchError(error => {
                console.warn('deleteService error:', error);
                return throwError(error);
            })
        );
    }

    public updateService (translatorId : number, service : TranslatorServiceItem) : Observable<TranslatorServiceItem> {
        return this.http.put('endpoint://translators.updateService', {
            urlParams: {
                serviceId: service.id,
                translatorId
            },
            body: { service }
        }).pipe(
            retry(1),
            take(1),
            map(response => response.service as TranslatorServiceItem),
            catchError(error => {
                console.warn('updateService error:', error);
                return throwError(error);
            })
        );
    }

    public createService (translatorId : number, service : TranslatorServiceItem) : Observable<TranslatorServiceItem> {
        return this.http.post('endpoint://translators.createService', {
            urlParams: { translatorId },
            body: { service }
        }).pipe(
            retry(1),
            take(1),
            map(response => response.service as TranslatorServiceItem),
            catchError(error => {
                console.warn('createService error:', error);
                return throwError(error);
            })
        );
    }

    public createTranslator (translator : Translator) : Observable<Translator> {
        return this.http.post('endpoint://translators.create', {
            body: { translator }
        }).pipe(
            retry(1),
            take(1),
            map(response => response.translator as Translator),
            catchError(error => {
                console.warn('createTranslator error:', error);
                return throwError(error);
            })
        );
    }

    public updateTranslator (translator : Translator) : Observable<Translator> {
        return this.http.put('endpoint://translators.update', {
            urlParams: { translatorId: translator.id },
            body: { translator }
        }).pipe(
            retry(1),
            take(1),
            map(response => response.translator as Translator),
            catchError(error => {
                console.warn('updateTranslator error:', error);
                return throwError(error);
            })
        );
    }

    public updateFinancial (translatorId : number, translatorFinancial : TranslatorFinancial) : Observable<TranslatorFinancial> {
        return this.http.put('endpoint://translators.saveFinancial', {
            urlParams: { translatorId },
            body: { financial: translatorFinancial }
        }).pipe(
            retry(1),
            take(1),
            map(response => response.financial as TranslatorFinancial),
            catchError(error => {
                console.warn('updateFinancial error:', error);
                return throwError(error);
            })
        );
    }
}
