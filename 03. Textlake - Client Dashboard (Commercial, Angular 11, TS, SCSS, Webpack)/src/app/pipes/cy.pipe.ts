import {Injectable, Pipe, PipeTransform} from '@angular/core';

@Injectable()
@Pipe({
    name: 'cy'
})
export class CyPipe implements PipeTransform {
    static get Symbols () {
        return {
            'USD': '$',
            'EUR': '€',
            'GBP': '£',
            'JPY': '¥',
            'PLN': 'zł',
            'RUB': '₽'
        };
    }

    public transform (value : string | number, currencyCode? : string, addWhitespace : boolean = false) : string | null {
        if (this.isEmpty(value)) {
            return null;
        }

        value = String(value);
        currencyCode = (currencyCode || 'USD').toUpperCase();

        const currency : string = CyPipe.Symbols[currencyCode] || currencyCode;

        return currency + (addWhitespace ? ' ' : '') + value;
    }

    public isEmpty (value : any) : boolean {
        return value == null || value === '' || value !== value;
    }
}
