import { Injectable } from '@angular/core';
import {TranslateService, TranslationChangeEvent} from '@ngx-translate/core';
import * as moment from 'moment';
import {capitalize} from 'lodash';

const HAS_FORMAT_TIME_REGEXP : RegExp = /A|a|aa|H|HH|k|kk|h|hh|m|mm|s|ss|S|SS|SSS|LLL|LLLL|LT|LTS/;

const IS_TWELVE_HOURS_FORMAT_REGEXP : RegExp = /A|a|aa|h|hh|LLL|LLLL|LT|LTS/;

@Injectable({
    providedIn: 'root'
})
export class DatetimeService {
    constructor (
        private translateService : TranslateService
    ) {
        this.translateService.onTranslationChange.subscribe((event: TranslationChangeEvent) => {
            console.warn('onTranslationChange', event);
        });

        this.translateService.onLangChange.subscribe((event) => {
            console.warn('onTranslationChange', event);
        });

        // TODO: remove
        (window as any).moment = moment;
    }

    public setLocale (locale : string) : boolean {
        return locale === moment.locale(locale);
    }

    /**
     *
     * @param source - ISO string, timestamp without format | formatted date with format
     * @param format
     * @param strict
     */
    public parse (source : string | number | Date | any, format? : string, strict : boolean = true) : any {
        const date = moment(source, format, strict);
        return date.isValid() ? date : null;
    }

    public getMoment (date? : Date | number[] | string | Object) : any {
        return moment(date);
    }

    public hasFormatTime (format : string) : boolean {
        return HAS_FORMAT_TIME_REGEXP.test(format);
    }

    public isTwelveHoursFormat (format : string) : boolean {
        return IS_TWELVE_HOURS_FORMAT_REGEXP.test(format);
    }

    public getFirstDayOfWeek () : 'mon' | 'sun' {
        return moment.localeData().firstDayOfWeek() === 1 ? 'mon' : 'sun';
    }

    public getShortMonths () : string[] {
        return moment.localeData().monthsShort().map(month => capitalize(month.replace(/\./g, '')));
    }

    // get subjective or nominative month name
    public getMonthName (indexOrMoment : any) : string {
        if (typeof(indexOrMoment) === 'number') {
            return capitalize(moment.localeData().months()[indexOrMoment]);
        } else {
            return capitalize(moment.localeData().months(indexOrMoment, 'D MMMM'));
        }
    }

    public getShortWeekdays (firstDayOfWeek : 'mon' | 'sun' = 'sun') : string[] {
        const weekdays = moment.localeData().weekdaysShort().map(day => capitalize(day.replace(/\./g, '')));
        return firstDayOfWeek === 'mon' ? [ ...weekdays.slice(1), weekdays[0] ] : weekdays;
    }

    public isMoment (obj : any) : boolean {
        return moment.isMoment(obj);
    }

    public fetchTimezones () : {
        value : string,
        display : string
    }[] {
        return [
            {
                value: '-12.0',
                display: "(GMT -12:00) Eniwetok, Kwajalein"
            },
            {
                value: '-11.0',
                display: "(GMT -11:00) Midway Island, Samoa"
            },
            {
                value: '-10.0',
                display: "(GMT -10:00) Hawaii"
            },
            {
                value: '-9.0',
                display: "(GMT -9:00) Alaska"
            },
            {
                value: '-8.0',
                display: "(GMT -8:00) Pacific Time (US &amp; Canada)"
            },
            {
                value: '-7.0',
                display: "(GMT -7:00) Mountain Time (US &amp; Canada)"
            },
            {
                value: '-6.0',
                display: "(GMT -6:00) Central Time (US &amp; Canada), Mexico City"
            },
            {
                value: '-5.0',
                display: "(GMT -5:00) Eastern Time (US &amp; Canada), Bogota, Lima"
            },
            {
                value: '-4.0',
                display: "(GMT -4:00) Atlantic Time (Canada), Caracas, La Paz"
            },
            {
                value: '-3.5',
                display: "(GMT -3:30) Newfoundland"
            },
            {
                value: '-3.0',
                display: "(GMT -3:00) Brazil, Buenos Aires, Georgetown"
            },
            {
                value: '-2.0',
                display: "(GMT -2:00) Mid-Atlantic"
            },
            {
                value: '-1.0',
                display: "(GMT -1:00) Azores, Cape Verde Islands"
            },
            {
                value: '0',
                display: "(GMT) Western Europe Time, London, Lisbon, Casablanca"
            },
            {
                value: '1.0',
                display: "(GMT +1:00) Brussels, Copenhagen, Madrid, Paris"
            },
            {
                value: '2.0',
                display: "(GMT +2:00) Kaliningrad, South Africa"
            },
            {
                value: '3.0',
                display: "(GMT +3:00) Baghdad, Riyadh, Moscow, St. Petersburg"
            },
            {
                value: '3.5',
                display: "(GMT +3:30) Tehran"
            },
            {
                value: '4.0',
                display: "(GMT +4:00) Abu Dhabi, Muscat, Baku, Tbilisi"
            },
            {
                value: '4.5',
                display: "(GMT +4:30) Kabul"
            },
            {
                value: '5.0',
                display: "(GMT +5:00) Ekaterinburg, Islamabad, Karachi, Tashkent"
            },
            {
                value: '5.5',
                display: "(GMT +5:30) Bombay, Calcutta, Madras, New Delhi"
            },
            {
                value: '5.75',
                display: "(GMT +5:45) Kathmandu"
            },
            {
                value: '6.0',
                display: "(GMT +6:00) Almaty, Dhaka, Colombo"
            },
            {
                value: '7.0',
                display: "(GMT +7:00) Bangkok, Hanoi, Jakarta"
            },
            {
                value: '8.0',
                display: "(GMT +8:00) Beijing, Perth, Singapore, Hong Kong"
            },
            {
                value: '9.0',
                display: "(GMT +9:00) Tokyo, Seoul, Osaka, Sapporo, Yakutsk"
            },
            {
                value: '9.5',
                display: "(GMT +9:30) Adelaide, Darwin"
            },
            {
                value: '10.0',
                display: "(GMT +10:00) Eastern Australia, Guam, Vladivostok"
            },
            {
                value: '11.0',
                display: "(GMT +11:00) Magadan, Solomon Islands, New Caledonia"
            },
            {
                value: '12.0',
                display: "(GMT +12:00) Auckland, Wellington, Fiji, Kamchatka"
            }
        ];
    }

    // --------------

    // public isLeapYear (year : number) : boolean {
    //     return year % 4 === 0 && year % 100 !== 0 || year % 400 === 0;
    // }
    //
    // public getMeridiem (hours : number, minutes : number) : string {
    //     return moment.localeData().meridiem(hours, minutes, false);
    // }
    //
    // public monthShort (index : number, format : string = '-MMM-') : string {
    //     return moment.monthsShort(format, index);
    // }

    // moment.localeData().months(moment({ month: 0, date: 7 }), 'D MMMM') - января
}
