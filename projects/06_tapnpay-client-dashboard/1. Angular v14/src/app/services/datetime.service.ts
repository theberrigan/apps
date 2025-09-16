import { Injectable } from '@angular/core';
import {TranslateService, TranslationChangeEvent} from '@ngx-translate/core';
import * as moment from 'moment';
import {capitalize} from 'lodash';
import {ILangFormat, LANGS, LangService} from './lang.service';
import {Moment} from 'moment';
import {flatten} from '../lib/utils';

const HAS_FORMAT_TIME_REGEXP : RegExp = /A|a|aa|H|HH|k|kk|h|hh|m|mm|s|ss|S|SS|SSS|LLL|LLLL|LT|LTS/;

const IS_TWELVE_HOURS_FORMAT_REGEXP : RegExp = /A|a|aa|h|hh|LLL|LLLL|LT|LTS/;

// https://momentjs.com/docs/#/displaying/format/
@Injectable({
    providedIn: 'root'
})
export class DatetimeService {
    private readonly defaultFormat : { [ key : string ]: ILangFormat } = {};

    private readonly defaultFormatFlat : { [ key : string ]: {
        [ key : string ]: string
    } } = {};

    formatCache : any = {};

    constructor (
        private langService : LangService
    ) {
        LANGS.forEach(lang => {
            this.defaultFormat[lang.code] = lang.format;
            this.defaultFormatFlat[lang.code] = flatten(lang.format);
        });

        this.onLangChange();
        this.langService.onLangChange(() => this.onLangChange());
    }

    onLangChange () {
        const locale = this.langService.getCurrentLangCode();

        if (!this.setLocale(locale)) {
            console.warn('Failed to change moment\'s locale to:', locale);
        } else {
            this.formatCache = {};
        }
    }

    setLocale (locale : string) : boolean {
        return locale === moment.locale(locale);
    }

    parse (source : Date | number | string, format? : string, strict : boolean = true) : any {
        const date = moment(source, format, strict);
        return date.isValid() ? date : null;
    }

    getMoment (source? : Date | number | string) : Moment {
        return moment(source);
    }

    getShortMonths () : string[] {
        return moment.localeData().monthsShort().map(month => capitalize(month.replace(/\./g, '')));
    }

    // get subjective or nominative month name
    getMonthName (indexOrMoment : any) : string {
        if (typeof(indexOrMoment) === 'number') {
            return capitalize(moment.localeData().months()[indexOrMoment]);
        } else {
            return capitalize(moment.localeData().months(indexOrMoment, 'D MMMM'));
        }
    }

    getShortWeekdays (firstDayOfWeek : 'mon' | 'sun' = 'sun') : string[] {
        const weekdays = moment.localeData().weekdaysShort().map(day => capitalize(day.replace(/\./g, '')));
        return firstDayOfWeek === 'mon' ? [ ...weekdays.slice(1), weekdays[0] ] : weekdays;
    }

    isTwelveHoursFormat (format : string) : boolean {
        return IS_TWELVE_HOURS_FORMAT_REGEXP.test(format);
    }

    getFormatByAlias (formatAlias : string) : string {
        const langCode = this.langService.getCurrentLangCode();
        const langFormat = this.defaultFormatFlat[langCode];

        if (formatAlias in langFormat) {
            return langFormat[formatAlias];
        } else {
            return formatAlias;
        }
    }

    format (source : Date | number | string, formatOrAlias : string) : string {
        const cacheKeyLang = this.langService.getCurrentLangCode();
        const cacheKeySource = source instanceof Date ? source.getTime() : String(source);
        const cacheKey = `${ cacheKeyLang }.${ cacheKeySource }.${ formatOrAlias }`;

        if (cacheKey in this.formatCache) {
            return this.formatCache[cacheKey];
        }

        const format = this.getFormatByAlias((formatOrAlias || '').trim() || 'display.datetime');
        const formattedDate = moment(source).format(format);

        this.formatCache[cacheKey] = formattedDate;

        return formattedDate;
    }

    getFirstDayOfWeek () : 'mon' | 'sun' {
        return moment.localeData().firstDayOfWeek() === 1 ? 'mon' : 'sun';
    }

    hasFormatTime (format : string) : boolean {
        return HAS_FORMAT_TIME_REGEXP.test(format);
    }
}
