import {Pipe, PipeTransform} from '@angular/core';
import {CurrencyService} from '../services/currency.service';

@Pipe({
    name: 'currency'
})
export class CurrencyPipe implements PipeTransform {
    constructor (
        public currencyService : CurrencyService
    ) {}

    transform (value : number, currency : string = '$') : string {
        return this.currencyService.format(value, currency);
    }
}
