import { Injectable } from '@angular/core';
import {HttpService} from './http.service';
import {catchError, map, retry, take} from 'rxjs/operators';
import {Observable, throwError} from 'rxjs';
import {UserService} from './user.service';

export class Rate {
    public id : number = 0;
    public basic : boolean = false;
    public created : string = '';
    public description : string = '';
    public enabled : boolean = false;
    public global : boolean = false;
    public selected : boolean = false;
    public name : string = '';
    public updated : string = '';
}

@Injectable({
    providedIn: 'root'
})
export class RatesService {
    constructor (
        private http : HttpService,
        private userService : UserService,
    ) {}

    public loadAvailableRates (clientId : number = null) : Observable<Rate[]> {
        return this.http.get('endpoint://rates.getAvailable', {
            params: clientId !== null ? { clientId: String(clientId) } : null,
        }).pipe(
            retry(1),
            take(1),
            map(response => response.rates as Rate[]),
            catchError(error => {
                console.warn('loadAvailableRates error:', error);
                return throwError(error);
            })
        );
    }

    public fetchRates () : Observable<Rate[]> {
        return this.http.get('endpoint://rates.getAll').pipe(
            retry(1),
            take(1),
            map(response => response.rates as Rate[]),
            catchError(error => {
                console.warn('fetchRates error:', error);
                return throwError(error);
            })
        );
    }

    public deleteRate (rateId : number) : Observable<void> {
        return this.http.delete('endpoint://rates.delete', {
            urlParams: { rateId }
        }).pipe(
            retry(1),
            take(1),
            catchError(error => {
                console.warn('deleteRate error:', error);
                return throwError(error);
            })
        );
    }

    public createRates (rate : Rate) : Observable<Rate> {
        return this.http.post('endpoint://rates.create', {
            body: { rate }
        }).pipe(
            retry(1),
            take(1),
            map(response => response.rate as Rate),
            catchError(error => {
                console.warn('createRates error:', error);
                return throwError(error);
            })
        );
    }

    public updateRates (rate : Rate) : Observable<Rate> {
        return this.http.put('endpoint://rates.update', {
            urlParams: {
                rateId: rate.id
            },
            body: { rate }
        }).pipe(
            retry(1),
            take(1),
            map(response => response.rate as Rate),
            catchError(error => {
                console.warn('updateRates error:', error);
                return throwError(error);
            })
        );
    }

    public fetchRatesListState () : Observable<any> {
        return this.userService.fetchFromStorage('rates_list_state').pipe(
            retry(1),
            take(1),
            catchError(error => {
                console.warn('fetchRatesListState error:', error);
                return throwError(error);
            })
        );
    }

    public saveRatesListState (state : any) : Promise<boolean> {
        return this.userService.saveToStorage('rates_list_state', state);
    }
}
