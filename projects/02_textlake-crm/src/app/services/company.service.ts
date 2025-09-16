import { Injectable } from '@angular/core';
import {Observable, throwError} from 'rxjs';
import {isArray} from 'lodash';
import {catchError, map, retry, take} from 'rxjs/operators';
import {HttpService} from './http.service';
import {Translator} from './translators.service';
import {Contact} from './offers.service';
import {UserService} from './user.service';

export class Coordinator {
    id : number;
    email : string;
    firstName : string;
    lastName : string;
    active : boolean;
    verifiedEmail : boolean;

    constructor (init? : Coordinator) {
        Object.assign(this, init || {});
    }
}

export class Company {
    bankAccount : string = '';
    bankName : string = '';
    city : string = '';
    country : string = '';
    email : string = '';
    fax : string = '';
    name : string = '';
    phone : string = '';
    state : string = '';
    street : string = '';
    street2 : string = '';
    timeZone : string = '0';
    tin : string = '';
    zipCode : string = '';
    preferredLanguage : string = '';
}

export class CompanyServiceItem {
    id : number = 0;
    from : string = null;
    to : string = null;
    name : string = '';
    parentId : number = null;
    price : number = 0;
    rate : number = null;
    shortName : string = '';
    unit : string = '';
    used : boolean = false;
}

interface Option {
    value : any;
    display : string;
}

interface IKN {
    id : number;
    key : string;
    name : string;
}

@Injectable({
    providedIn: 'root'
})
export class CompanyService {
    constructor (
        private http : HttpService,
        private userService : UserService,
    ) {}

    public fetchCoordinators (addDefault : boolean = false) : Observable<Coordinator[]> {
        return this.http.get('endpoint://company.getCoordinators').pipe(
            retry(1),
            take(1),
            map(response => {
                const coordinators : Coordinator[] = response.coordinators || [];

                if (addDefault) {
                    coordinators.unshift(new Coordinator({
                        id: -1,
                        email: '',
                        firstName: '',
                        lastName: '',
                        active: true,
                        verifiedEmail: true
                    }));
                }

                return coordinators;
            }),
            catchError(error => {
                console.warn('fetchCoordinators error:', error);
                return throwError(error);
            })
        );
    }

    public getCompany () : Observable<Company> {
        return this.http.get('endpoint://company.getInfo').pipe(
            retry(1),
            take(1),
            map(response => response.company as Company),
            catchError(error => {
                console.warn('getCompany error:', error);
                return throwError(error);
            })
        );
    }

    public updateCompany (company : Company) : Observable<void> {
        return this.http.put('endpoint://company.updateCompany', {
            body: company
        }).pipe(
            retry(1),
            take(1),
            catchError(error => {
                console.warn('updateCompany error:', error);
                return throwError(error);
            })
        );
    }

    public cloneService (serviceId : number, rateId : number) : Observable<CompanyServiceItem> {
        return this.http.post('endpoint://company.cloneService', {
            body: {
                sourceServiceId: serviceId,
                destinationRateId: rateId
            }
        }).pipe(
            retry(1),
            take(1),
            map(response => response.service),
            catchError(error => {
                console.warn('cloneService error:', error);
                return throwError(error);
            })
        );
    }

    public createService (service : CompanyServiceItem) : Observable<CompanyServiceItem> {
        return this.http.post('endpoint://company.createService', {
            body: { service }
        }).pipe(
            retry(1),
            take(1),
            map(response => response.service),
            catchError(error => {
                console.warn('createService error:', error);
                return throwError(error);
            })
        );
    }

    public updateService (service : CompanyServiceItem) : Observable<CompanyServiceItem> {
        return this.http.put('endpoint://company.updateService', {
            body: { service }
        }).pipe(
            retry(1),
            take(1),
            map(response => response.service),
            catchError(error => {
                console.warn('updateService error:', error);
                return throwError(error);
            })
        );
    }

    public deleteService (serviceId : number) : Observable<void> {
        return this.http.delete('endpoint://company.deleteService', {
            urlParams: { serviceId }
        }).pipe(
            take(1),
            catchError(error => {
                console.warn('deleteService error:', error);
                return throwError(error);
            })
        );
    }

    public fetchTranslationTypes (asOptions : boolean = false) : Observable<any> {
        return this.http.get('endpoint://company.getTranslationTypes').pipe(
            retry(1),
            take(1),
            map(response => {
                const translationTypes : IKN[] = (response.translationTypes || []).map(translationType => {
                    translationType.name = 'translation_type.' + translationType.key.replace(/\./g, '_');
                    return translationType;
                });

                if (!asOptions) {
                    return translationTypes;
                }

                return translationTypes.map(translationType => ({
                    display: translationType.name,
                    value: translationType.id
                }));
            }),
            catchError(error => {
                console.warn('fetchTranslationTypes error:', error);
                return throwError(error);
            })
        );
    }

    public fetchSubjectAreas (asOptions : boolean = false) : Observable<IKN[] | Option[]> {
        return this.http.get('endpoint://company.getSubjectAreas').pipe(
            retry(1),
            take(1),
            map(response => {
                const subjectAreas : IKN[] = (response.fields || []).map(subjectArea => {
                    subjectArea.name = 'subject_area.' + subjectArea.key.replace(/\./g, '_');
                    return subjectArea;
                });

                if (!asOptions) {
                    return subjectAreas;
                }

                return subjectAreas.map(subjectArea => ({
                    display: subjectArea.name,
                    value: subjectArea.id
                }));
            }),
            catchError(error => {
                console.warn('fetchSubjectAreas error:', error);
                return throwError(error);
            })
        );
    }

    public fetchBasicServices (asOptions : boolean = false) : Observable<CompanyServiceItem[] | Option[]> {
        return this.http.get('endpoint://company.getBasicServices').pipe(
            retry(1),
            take(1),
            map(response => {
                const services : CompanyServiceItem[] = response.services || [];

                if (!asOptions) {
                    return services;
                }

                return services.map(service => ({
                    display: service.name,
                    value: service.id
                }));
            }),
            catchError(error => {
                console.warn('fetchBasicServices error:', error);
                return throwError(error);
            })
        );
    }

    public fetchServices (params : any) : Observable<CompanyServiceItem[]> {
        return this.http.get('endpoint://company.getServices', {
            params
        }).pipe(
            retry(1),
            take(1),
            // map(response => response.services),
            catchError(error => {
                console.warn('fetchServices error:', error);
                return throwError(error);
            })
        );
    }

    public fetchServicesListState () : Observable<any> {
        return this.userService.fetchFromStorage('services_list_state').pipe(
            retry(1),
            take(1),
            catchError(error => {
                console.warn('fetchServicesListState error:', error);
                return throwError(error);
            })
        );
    }

    public saveServicesListState (state : any) : Promise<boolean> {
        return this.userService.saveToStorage('services_list_state', state);
    }

    public fetchCalcRule ()  : Observable<string> {
        return this.http.get('endpoint://company.getCalcRule').pipe(
            retry(1),
            take(1),
            map(response => response.calculation_rule),
            catchError(error => {
                console.warn('fetchCalcRule error:', error);
                return throwError(error);
            })
        );
    }

    public saveCalcRule (calcRule : string)  : Observable<string> {
        return this.http.put('endpoint://company.saveCalcRule', {
            body: {
                calculation_rule: calcRule
            }
        }).pipe(
            retry(1),
            take(1),
            map(response => response.calculation_rule),
            catchError(error => {
                console.warn('saveCalcRule error:', error);
                return throwError(error);
            })
        );
    }
}
