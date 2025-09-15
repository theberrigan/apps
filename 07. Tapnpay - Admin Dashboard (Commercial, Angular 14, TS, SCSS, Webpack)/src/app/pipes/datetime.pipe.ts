import {Pipe, PipeTransform} from '@angular/core';
import {DatetimeService} from '../services/datetime.service';

@Pipe({
    name: 'datetime',
    pure: false
})
export class DatetimePipe implements PipeTransform {
    constructor (
        private datetimeService : DatetimeService
    ) {}

    // value - timestamp (ms) or ISO string
    transform (value : Date | number | string, format? : string) : string {
        if (value === undefined || value === null || value === 0 || value === '') {
            return null;
        }

        return this.datetimeService.format(value, format);
    }
}
