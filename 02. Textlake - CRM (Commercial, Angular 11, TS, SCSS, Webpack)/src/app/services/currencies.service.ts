import { Injectable } from '@angular/core';
import {HttpService} from './http.service';
import {Observable, throwError} from 'rxjs';
import {catchError, map, retry, take} from 'rxjs/operators';
import {Transaction} from './client.service';

// used only in offer editor
export class OfferCurrency {
    constructor (source : any = {}) {
        for (let key in source) {
            if (key in this) {
                this[key] = source[key];
            }
        }
    }

    key : string = null;
    name : string = null;
    rate : number = 0;
}

interface Option {
    value : string;
    display : string;
}

export class Currency {
    key : string = null;
    name : string = null;
}

export class CurrencyExchangeRate {
    key : string = null;
    name : string = null;
    rate : number = null;
}

export class GetCurrencyRatesResponse {
    primaryCurrency : Currency = null;
    rates : CurrencyExchangeRate[] = [];
}

export class UpdateCurrencyRate {
    key : string = null;
    rate : number = null;
}

export class UpdateCurrencyRatesRequest {
    primaryCurrency : string = null;
    rates : UpdateCurrencyRate[] = [];
}

export class CurrencyHistory {
    created : string = null;
    rate : number = null;
    user : string = '';
}

export class GetCurrencyHistoryResponse {
    fromKey : string = null;
    toKey : string = null;
    fromName : string = null;
    toName : string = null;
    rates : CurrencyHistory[] = [];
}

@Injectable({
    providedIn: 'root'
})
export class CurrenciesService {
    constructor (
        private http : HttpService
    ) {}

    public fetchCurrencies (options : {
        activeOnly? : boolean,
        asOptions? : boolean,
        addDefault? : boolean,
    } = {
        activeOnly: false,
        asOptions: false,
        addDefault: false,
    }) : Observable<Currency[] | Option[]> {
        const endpoint = (
            options.activeOnly === true ?
            'endpoint://currencies.getActive' :
            'endpoint://currencies.getAll'
        );

        return this.http.get(endpoint).pipe(
            retry(1),
            take(1),
            map(response => {
                const currencies : Currency[] = response.currencies || [];

                if (options.asOptions !== true) {
                    return currencies;
                }

                const currencyOptions = currencies.map(currency => ({
                    display: currency.name,
                    value: currency.key
                }));

                if (options.asOptions === true) {
                    currencyOptions.unshift({
                        value: null,
                        display: ''
                    });
                }

                return currencyOptions;
            }),
            catchError(error => {
                console.warn('fetchCurrencies error:', error);
                return throwError(error);
            })
        );
    }

    public fetchCurrenciesRates () : Observable<GetCurrencyRatesResponse> {
        return this.http.get('endpoint://currencies.getCurrenciesRates').pipe(
            retry(1),
            take(1),
            catchError(error => {
                console.warn('fetchCurrenciesRates error:', error);
                return throwError(error);
            })
        );
    }

    public fetchCurrenciesRatesHistory (fromKey : string, toKey : string) : Observable<GetCurrencyHistoryResponse> {
        return this.http.get('endpoint://currencies.getCurrenciesRatesHistory', {
            urlParams: { fromKey, toKey }
        }).pipe(
            retry(1),
            take(1),
            catchError(error => {
                console.warn('fetchCurrenciesRatesHistory error:', error);
                return throwError(error);
            })
        );
    }

    public updateCurrenciesRates (ratesData : UpdateCurrencyRatesRequest) : Observable<void> {
        return this.http.post('endpoint://currencies.updateCurrenciesRates', {
            body: ratesData
        }).pipe(
            retry(1),
            take(1),
            catchError(error => {
                console.warn('updateCurrenciesRates error:', error);
                return throwError(error);
            })
        );
    }
}
