import { Injectable } from '@angular/core';
import {HttpService} from './http.service';
import {catchError, map, retry, take} from 'rxjs/operators';
import {Observable, throwError} from 'rxjs';
import {UserService} from './user.service';

export class Tax {
    id : number = 0;
    name : string = '';
    value : number = null;
}

@Injectable({
    providedIn: 'root'
})
export class TaxesService {
    constructor (
        private http : HttpService,
        private userService : UserService,
    ) {}

    public fetchTaxes () : Observable<Tax[]> {
        return this.http.get('endpoint://tax.getAll').pipe(
            retry(1),
            take(1),
            map(response => response.taxes),
            catchError(error => {
                console.warn('fetchTaxes error:', error);
                return throwError(error);
            })
        );
    }

    public createTax (tax : Tax) : Observable<Tax> {
        return this.http.post('endpoint://tax.create', {
            body: { tax }
        }).pipe(
            retry(1),
            take(1),
            map(response => response.tax),
            catchError(error => {
                console.warn('createTax error:', error);
                return throwError(error);
            })
        );
    }

    public deleteTax (taxId : number) : Observable<Tax> {
        return this.http.delete('endpoint://tax.delete', {
            urlParams: { taxId },
        }).pipe(
            retry(1),
            take(1),
            catchError(error => {
                console.warn('deleteTax error:', error);
                return throwError(error);
            })
        );
    }

    public fetchTaxesListState () : Observable<any> {
        return this.userService.fetchFromStorage('taxes_list_state').pipe(
            retry(1),
            take(1),
            catchError(error => {
                console.warn('fetchTaxesListState error:', error);
                return throwError(error);
            })
        );
    }

    public saveTaxesListState (state : any) : Promise<boolean> {
        return this.userService.saveToStorage('taxes_list_state', state);
    }
}
