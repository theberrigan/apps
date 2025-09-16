import { Injectable } from '@angular/core';
import {float} from '../lib/utils';

const CURRENCIES_MAP = {
    'USD': '$'
};

@Injectable({
    providedIn: 'root'
})
export class CurrencyService {
    constructor () {}

    format (value : number, currency : string = '$') {
        currency = CURRENCIES_MAP[currency.toUpperCase()] || currency;
        return currency + (float(value) / 100.0).toFixed(2);
    }
}
