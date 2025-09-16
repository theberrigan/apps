import {Injectable, Pipe, PipeTransform} from '@angular/core';
import {DatetimeService} from '../services/datetime.service';
import {isEmpty} from '../lib/utils';

@Injectable()
@Pipe({
    name: 'datetime',
    pure: false
})
export class DatetimePipe implements PipeTransform {
    public lang : string;

    constructor(
        public datetimeService : DatetimeService
    ) {}

    public transform (value : any, format : string = 'D MMM YYYY HH:mm') : string {
        const moment = !isEmpty(value) && this.datetimeService.getMoment(value) || null;
        return moment && moment.format(format) || '';
    }
}
