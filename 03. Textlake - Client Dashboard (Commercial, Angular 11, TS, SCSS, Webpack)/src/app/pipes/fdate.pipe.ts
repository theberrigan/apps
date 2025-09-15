import {Injectable, Pipe, PipeTransform} from '@angular/core';
import { DatetimeService2 } from '../services/datetime-service2.service';

@Injectable()
@Pipe({
    name: 'fdate',
    pure: false
})
export class FormatDatePipe implements PipeTransform {
    constructor (
        private dtService : DatetimeService2
    ) {}

    public transform (source : Date | number | string, format : string = 'dd.MM.yy') : string {
        return this.dtService.formatDatetime(source, format);
    }

}
