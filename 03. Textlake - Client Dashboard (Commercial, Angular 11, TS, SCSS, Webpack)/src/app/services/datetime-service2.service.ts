import { Injectable }       from '@angular/core';
import { TranslateService } from '@ngx-translate/core';

@Injectable({
    providedIn: 'root'
})
export class DatetimeService2 {
    private monthsNames : string[] = [ 'January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December' ];

    private shortMonthsNames : string[] = [ 'Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec' ];

    private daysNames : string[] = [ 'Sunday', 'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday' ];

    private shortDaysNames : string[] = [ 'Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat' ];

    private timeMarks : string[] = [ 'AM', 'PM' ];

    private cache : { [ key : string ] : string } = {};

    private formatAliases : { [ key : string ] : string } = {}; // TODO: add custom aliases

    private iso8601Regex : RegExp = /^(\d{4})-?(\d\d)-?(\d\d)(?:(T\d\d)(?::?(\d\d)(?::?(\d\d)(?:(\.\d+))?)?)?(?:(Z)|([+-]\d\d):?(\d\d)?)?)?$/;
    //                                1YYYY    2MM     3DD      4Thh        5mm        6ss      7.ms            8Z  9+/-HH      10MM

    private addToCache : boolean = false;

    // --------------------

    private markers : string[] = [  // !!! Desc sorted markers
        'GGGG', 'MMMM', 'EEEE', 'MMM', 'GGG', 'EEE',
        'dd', 'yy', 'MM', 'jj', 'hh', 'HH', 'mm',
        'ss', 'y', 'M', 'j', 'L', 'h', 'd', 'H',
        'G', 'm', 'a', 's', 'z', 'Z', 'E'
    ];

    private whitespaces : string[] = [ '', ' ', '  ', '   ', '    ' ];

    private chunksCache : { [ key : string ] : any[][] } = {};

    private formatRegexes : any = {
        yy:   '(\\d{4})',    // 2018
        y:    '(\\d{2})',    // 18 (year)
        // -------------------------
        MMMM: () => `(${ this.translatedMonths.join('|') })`,    // January
        MMM:  () => `(${ this.translatedShortMonths.join('|') })`,    // Jan
        MM:   '(\\d{2})',    // 01 (number of month with zero pad)
        M:    '(\\d{1,2})',  //  1 (number of month)
        // -------------------------
        dd:   '(\\d{2})',    // 09 (day of month w/ zero pad)
        d:    '(\\d{1,2})',  //  9 (day of month)
        // -------------------------
        jj:   () => `(\\d{2}\\s+(?:${ this.translatedTimeMarks.join('|') }))`,    // 09 PM/AM (12-hours hour with zero pad)
        j:    () => `(\\d{1,2}\\s+(?:${ this.translatedTimeMarks.join('|') }))`,  //  9 PM/AM (12-hours hour)
        hh:   '(\\d{2})',    // 09 (12-hours hour)
        h:    '(\\d{1,2})',  //  9 (12-hours hour with zero pad)
        HH:   '(\\d{2})',    // 09 (24-hours hour)
        H:    '(\\d{1,2})',  //  9 (24-hours hour with zero pad)
        // -------------------------
        mm:   '(\\d{2})',    // 05 (minutes with zero pad)
        m:    '(\\d{1,2})',  //  5 (minutes)
        // -------------------------
        ss:   '(\\d{2})',    // 06 (minutes with zero pad)
        s:    '(\\d{1,2})',  //  6 (minutes)
        // -------------------------
        a:    () => `(${ this.translatedTimeMarks.join('|') })`,    // AM/PM
        // -------------------------
        GGGG: 'Anno\\sDomini',   // Era
        GGG:  'AD',              // Era (abbreviation)
        G:    'A',               // Era (first letter)
        L:    '\\w',             // Month name (first letter)
        EEEE: '\\w+',            // Weekday
        EEE:  '\\w{3}',          // Weekday (first 3 letters)
        E:    '\\w',             // Weekday (first letter)
        z:    '',                // -
        Z:    'GMT[+-]\\d{1,2}:\\d{2}'  // GMT+-X:YY
    };

    private matchParsers : any = {
        yy: (v) => this.parseNumber(v),  // 2018
        y:  (v) => {    // 18 (year)
            const
                y : number = this.parseNumber(v),
                currentYear : number = (new Date()).getFullYear();

            return y === null ? null : ((currentYear - 1900 - y) < (2000 + y - currentYear) ? 1900 : 2000) + y;
        },
        // ---------------------
        MMMM: (v : string) => {    // January
            const month : number = this.translatedMonths.indexOf(v.toLowerCase());
            return month >= 0 ? month : null;
        },
        MMM: (v : string) => {    // Jan
            const month : number = this.translatedShortMonths.indexOf(v.toLowerCase());
            return month >= 0 ? month : null;
        },
        MM: (v : string) => {    // 01 (number of month with zero pad)
            const month : number = Number(v) - 1;
            return Number.isFinite(month) ? month : null;
        },
        M:  (v : string) => this.matchParsers.MM(v),    // 1 (number of month)
        // ------------------------
        dd: (v : string) => this.parseNumber(v),    // 09 (day of month w/ zero pad)
        d:  (v : string) => this.parseNumber(v),    //  9 (day of month)
        // ------------------------
        jj: (v : string) => {    // 09 PM/AM (12-hours hour with zero pad)
            const [ h, timeMark ] : string[] = v.split(/\s+/);

            const timeMarkIndex : number = this.translatedTimeMarks.indexOf(timeMark.toUpperCase());

            let hour : number = this.parseNumber(h);

            if (hour === null || timeMarkIndex === -1) {
                return null;
            }

            return [ hour, this.timeMarks[ timeMarkIndex ] ];
        },
        j:  (v : string) => this.matchParsers.jj(v), //  9 PM/AM (12-hours hour)
        hh: (v : string) => this.parseNumber(v),     // 09 (12-hours hour with zero pad)
        h:  (v : string) => this.parseNumber(v),     //  9 (12-hours hour)
        HH: (v : string) => this.parseNumber(v),     // 09 (24-hours hour with zero pad)
        H:  (v : string) => this.parseNumber(v),     //  9 (24-hours hour)
        // -----------------------
        mm: (v : string) => this.parseNumber(v),     // 05 (minutes with zero pad)
        m:  (v : string) => this.parseNumber(v),     //  5 (minutes)
        // -----------------------
        ss: (v : string) => this.parseNumber(v),     // 06 (seconds with zero pad)
        s:  (v : string) => this.parseNumber(v),     //  6 (seconds)

        a: (v : string) => {    // AM/PM
            const timeMarkIndex : number = this.translatedTimeMarks.indexOf(v.toUpperCase());
            return timeMarkIndex === -1 ? null : this.timeMarks[ timeMarkIndex ];
        }
    };

    private translatedMonths : string[] = null;

    private translatedShortMonths : string[] = null;

    private translatedTimeMarks : string[] = null;

    private significantMarkers : string[] = [
        'a', 'yy', 'y', 'MMMM', 'MMM', 'MM',
        'M', 'dd', 'd', 'jj', 'j', 'hh', 'h',
        'HH', 'H', 'mm', 'm', 'ss', 's'
    ];

    constructor (
        private translate : TranslateService
    ) {
        // (<any>window).hasTimeFormat = this.hasTimeFormat;
        // (<any>window).hasTimeFormatContext = this;
    }

    public parseSource (source : Date | number | string) : Date | null {
        if (source === null || source === '' || source !== source) {
            return null;
        }

        let date : Date = null;

        // if source is Date
        if (source instanceof Date) {
            return source; // Date

        // if source is number
        } else if (typeof(source) === 'number') {
            return this.createDate(source); // Date || null

        // if source is string
        } else if (typeof(source) === 'string') {
            source = source.trim();

            // if date only
            if (/^(\d{4}-\d{1,2}-\d{1,2})$/.test(source)) {
                const [ y, m, d ] = source.split('-').map((n) => Number(n));
                return this.createDate(y, m - 1, d);

            // if ISO-8601 string
            } else {
                let date : Date = this.createDate(source);

                if (date !== null) {
                    return date;
                }

                const fixedIso : string = this.fixIsoString(source);

                if (fixedIso) {
                    return this.createDate(fixedIso); // Date || null
                }
            }
        }

        return null;
    }

    public formatDatetime (source : Date | number | string, format : string = 'dd.MM.yy') : string {
        if (typeof(source) == 'undefined' || source === null || source === '' || source !== source) {
            return null;
        }

        this.addToCache = true;

        let date : Date = null,
            cacheKey : string = `${this.translate.currentLang}|${format}|`;

        // if source is Date
        if (source instanceof Date) {
            if (!isNaN(source.valueOf())) {
                cacheKey += source.toISOString();

                if (this.cache[cacheKey]) {
                    return this.cache[cacheKey];
                }

                date = source;
            }

        // if source is number
        } else if (typeof(source) === 'number') {
            cacheKey += String(source);

            if (this.cache[cacheKey]) {
                return this.cache[cacheKey];
            }

            date = this.createDate(source);

        // if source is string
        } else if (typeof(source) === 'string') {
            source = source.trim();
            cacheKey += source;

            if (this.cache[cacheKey]) {
                return this.cache[cacheKey];
            }

            // if only date
            if (/^(\d{4}-\d{1,2}-\d{1,2})$/.test(source)) {
                const [ y, m, d ] = source.split('-').map(Number);
                date = this.createDate(y, m - 1, d);

            // if ISO-8601 string
            } else if ((date = this.createDate(source)) === null) {
                const fixedIso : string = this.fixIsoString(source);
                fixedIso && (date = this.createDate(fixedIso));
            }
        }

        if (date === null) {
            throw Error(`InvalidPipeArgument: '${ source }' for pipe 'FormatDatePipe'`);
        }

        let formatted : string = this.formatDate(date, this.formatAliases[format] || format);

        return this.addToCache ? (this.cache[cacheKey] = formatted) : formatted;
    }

    private fixIsoString (isoSource : string) : string | null {
        const match : RegExpMatchArray = isoSource.match(this.iso8601Regex);

        if (match) {
            let iso = match[1] + '-' + match[2] + '-' + match[3];

            // fix iso string
            if (match[4]) {
                iso += match[4];                                                // Thh
                iso += ':' + (match[5] || '00');                                // :mm
                iso += ':' + (match[6] || '00');                                // :ss
                iso += match[7] || '';                                          // :ms
                iso += match[8] || '';                                          // Z
                iso += match[9] ? (match[9] + ':' + (match[10] || '00')) : '';  // +/-HH:MM
            }

            return iso; // try fixed iso 8601
        }

        return null;
    }

    private getTranslation (key : string) : string {
        let i18nKey = `datetime_service.${key}__message`.toLowerCase(),
            message = this.translate.instant(i18nKey);

        this.addToCache = this.addToCache && message != i18nKey;
        return message == i18nKey ? key : message;
    }

    private zeroPad (value : string | number, length : number = 2) : string {
        return `0000${value}`.substr(-length);
    }

    private createDate (...args : any[]) : Date {
        let date : Date = new (Function.prototype.bind.call(Date, null, ...args)); // TS signature error: new Date(...args);
        return isNaN(date.valueOf()) ? null : date;
    };

    private repeatString (source : string, length : number) : string {
        let result : string = '';

        while (result.length < length) {
            result += source;
        }

        return result;
    }

    private formatDate (date : Date, format : string) : string {
        const patterns = {
            GGGG: 'Anno Domini',
            GGG:  'AD',
            G:    'A',
            yy:   String(date.getFullYear()),                                     // 2018
            y:    String(date.getFullYear()).slice(-2),                           // 18 (year)
            L:    this.getTranslation(this.monthsNames[date.getMonth()])[0],           // J (first letter of name of month)
            MMMM: this.getTranslation(this.monthsNames[date.getMonth()]),              // January
            MMM:  this.getTranslation(this.shortMonthsNames[date.getMonth()]), // Jan
            MM:   this.zeroPad(date.getMonth() + 1),                              // 01 (number of month with zero pad)
            M:    String(date.getMonth() + 1),                                    // 1 (number of month)
            dd:   this.zeroPad(date.getDate()),                                   // 09 (day of month w/ zero pad)
            d:    String(date.getDate()),                                         // 9 (day of month)
            EEEE: this.getTranslation(this.daysNames[date.getDay()]),                  //
            EEE:  this.getTranslation(this.shortDaysNames[date.getDay()]),
            E:    this.getTranslation(this.daysNames[date.getDay()])[0],
            jj:   this.zeroPad(date.getHours() % 12 || 12) + ' ' + this.getTranslation(date.getHours() >= 12 ? 'PM' : 'AM'),
            j:    String(date.getHours() % 12 || 12) + ' ' + this.getTranslation(date.getHours() >= 12 ? 'PM' : 'AM'),
            hh:   this.zeroPad(date.getHours() % 12 || 12),
            h:    String(date.getHours() % 12 || 12),
            HH:   this.zeroPad(date.getHours()),
            H:    String(date.getHours()),
            mm:   this.zeroPad(date.getMinutes()),
            m:    String(date.getMinutes()),
            ss:   this.zeroPad(date.getSeconds()),
            s:    String(date.getSeconds()),
            z:    '', // TODO: Implement
            Z:    (() => {
                      let offset : number = date.getTimezoneOffset();
                      return 'GMT' + (offset > 0 ? '-' : '+') + (Math.abs(offset) / 60 | 0) + ':' + this.zeroPad(Math.abs(offset) % 60);
                  })(),
            a:    this.getTranslation(date.getHours() >= 12 ? 'PM' : 'AM')
        };

        const chunks : any[][] = this.parseFormatString(format);

        let result : string = '';

        for (let i : number = 0, len : number = chunks.length; i < len; i++) {
            const chunk : any[] = chunks[ i ];
            result += chunk[ 0 ] == 0 ? patterns[ chunk[ 1 ] ] : chunk[ 1 ];
        }

        return result;
    }

    // ----------------------------

    // Parses format string to chunks
    public parseFormatString (format : string) : any[][] {
        const cached : any[][] = this.chunksCache[ format ];

        if (cached) {
            return cached;
        }

        const
            cacheKey : string = format,
            result : any[][] = [];

        let prevIndex : number = 0,
            chunks : any[][] = [];

        // Extract markers positions
        for (let j : number = 0, len : number = this.markers.length; j < len; j++) {
            const
                marker : string = this.markers[ j ],
                markerLen : number = marker.length;

            let i;

            while ((i = format.indexOf(marker)) > -1) {
                chunks.push([
                    i,             // start position
                    i + markerLen, // end position
                    marker         // content
                ]);
                format = format.replace(marker, this.whitespaces[ markerLen ]);
            }
        }

        // Sort chunks by start index
        chunks = chunks.sort((a, b) => a[0] - b[0]);

        for (let i : number = 0, len : number = chunks.length; i < len; i++) {
            const chunk : any[] = chunks[ i ];

            if (prevIndex != chunk[0]) {
                result.push([
                    1,   // type: 1 - original string part
                    format.slice(prevIndex, chunk[0])
                ]);
            }

            result.push([
                0,     // type: 0 - marker
                chunk[2]
            ]);

            prevIndex = chunk[1];
        }

        if (format.length != prevIndex) {
            result.push([
                1,   // type: 1 - original string part
                format.slice(prevIndex)
            ]);
        }

        this.chunksCache[ cacheKey ] = result;

        return result;
    }

    public formatToRegex (format : string) : any[] | null {
        // prepare months & time formats
        this.translatedMonths = this.getMonthsNames().map((v) => v.toLowerCase());

        this.translatedShortMonths = this.getShortMonthsNames().map((v) => v.toLowerCase());

        // console.log('this.translatedShortMonths', this.translatedShortMonths);

        const translatedTimeMarks : string[] = [];

        for (let i : number = 0, len = this.timeMarks.length; i < len; i++) {
            translatedTimeMarks.push(this.getTranslation(this.timeMarks[i]).toUpperCase());
        }

        this.translatedTimeMarks = translatedTimeMarks;

        // -----------------

        const chunks : any[][] = this.parseFormatString(format);

        let formatRegex : string = '^';

        const markerGroups : string[] = [];

        for (let i : number = 0, len : number = chunks.length; i < len; i++) {
            const chunk : any[] = chunks[i];

            if (chunk[0] == 1) {  // trash chunk
                formatRegex += this.escapeRegex(chunk[1]);
                continue;
            }

            // not trash chunk
            const
                marker : string = chunk[1],
                markerRegex : any = this.formatRegexes[marker];

            formatRegex += typeof(markerRegex) === 'string' ? markerRegex : markerRegex();

            this.significantMarkers.indexOf(marker) !== -1 && markerGroups.push(marker);
        }

        formatRegex += '$';

        try {
            return [ new RegExp(formatRegex, 'i'), markerGroups ];
        } catch (e) {
            console.warn('[formatToRegex] can`t compile regex:', formatRegex, e);
            return null;
        }
    }

    //
    public formattedToDate (formatted : string, format : string) : Date | null | any {
        const regexWithGroups : any[] = this.formatToRegex(format);

        if (!regexWithGroups) {
            return null;
        }

        const matches : RegExpMatchArray = formatted.match(regexWithGroups[0]);

        if (!matches) {
            console.warn(`[formattedToDate] provided formatted string doesn't match the regex`);

            console.log('\tformatted:', formatted);
            console.log('\tformat:', format);
            console.log('\tregexWithGroups:', regexWithGroups);
            console.log('\tmatches:', matches);

            return null;
        }

        const
            markers : string[] = regexWithGroups[1],
            values : any = {};

        for (let i : number = 0, len : number = markers.length; i < len; i++) {
            const
                marker : string = markers[i],
                match : string = matches[i + 1];

            if ((values[marker] = this.matchParsers[marker](match)) === null) {
                console.warn(`[formattedToDate] can't parse value of marker:`, marker, match);
                return null;
            }
        }

        // console.log('\tvalues:', values);

        const date : Date = new Date(0);

        // ------------------

        // year
        const year : number = values.yy || values.y;
        year && date.setFullYear(year);

        // month
        const month : number = 'M' in values ? values.M : 'MM' in values ? values.MM : 'MMM' in values ? values.MMM : 'MMMM' in values ? values.MMMM : null;
        month !== null && date.setMonth(month);

        // day
        const day : number = values.d || values.dd;
        day && date.setDate(day);

        // hour
        let hour : number = 'H' in values ? values.H : 'HH' in values ? values.HH : null;

        if (hour !== null) {
            date.setHours(hour);
        } else {
            let pair : number = 'j' in values ? values.j : 'jj' in values ? values.j : null;

            if (pair) {
                date.setHours(this.time12hrTo24hr(pair[0], pair[1]));
            } else {
                hour = 'h' in values ? values.h : 'hh' in values ? values.hh : null;

                if (hour !== null) {
                    date.setHours(this.time12hrTo24hr(hour, values.a));
                }
            }
        }

        // minutes
        const minutes : number = 'm' in values ? values.m : 'mm' in values ? values.mm : null;
        minutes !== null && date.setMinutes(minutes);

        // seconds
        const seconds : number = 's' in values ? values.s : 'ss' in values ? values.ss : null;
        seconds !== null && date.setSeconds(seconds);

        // ------------------

        return date;
    }

    public time12hrTo24hr (hours : number, mark : string) : number {  // 12, 'AM'
        mark = mark.toUpperCase();
        return hours + (mark == 'AM' && hours == 12 ? -12 : mark == 'PM' && hours >= 1 && hours <= 11 ? 12 : 0);
    }

    // 0 - no time format
    // 1 - 24-hours format
    // 2 - 12-hours format
    public hasTimeFormat (format : string) : number {
        let f : any = {
            j:  false,
            jj: false,
            H:  false,
            HH: false,
            h:  false,
            hh: false,
            a:  false,
            m:  false,
            mm: false
        };

        const chunks : any[][] = this.parseFormatString(format);

        for (let i : number = 0, len : number = chunks.length; i < len; i++) {
            const chunk : any[] = chunks[i];

            if (chunk[0] == 0 && f.hasOwnProperty(chunk[1])) {
                f[chunk[1]] = true;
            }
        }

        return ((f.j || f.jj) && 2) || ((f.m || f.mm) && ((f.H || f.HH) && 1 || (f.h || f.hh) && f.a && 2)) || 0;
    }

    private escapeRegex (str : string) : string {
        str = str.replace(/\s+/g, ' ');

        let result : string = '';

        for (let i : number = 0, len : number = str.length; i < len; i++) {
            const char = str[i];
            result += char == ' ' ? '\\s+' : ('\\u' + (`000` + char.charCodeAt(0).toString(16)).slice(-4));
        }

        return result;
    }

    private parseNumber (str : string) : number | null {
        const num : number = Number(str);
        return Number.isFinite(num) ? num : null;
    }

    // ------------------------

    public getShortDaysNames () : string[] {
        const shortDaysNames : string[] = [];

        for (let i : number = 0, len = this.shortDaysNames.length; i < len; i++) {
            shortDaysNames.push(this.getTranslation(this.shortDaysNames[i]));
        }

        return shortDaysNames;
    }

    public getDaysNames () : string[] {
        const daysNames : string[] = [];

        for (let i : number = 0, len = this.daysNames.length; i < len; i++) {
            daysNames.push(this.getTranslation(this.daysNames[i]));
        }

        return daysNames;
    }

    public getMonthsNames () : string[] {
        const monthsNames : string[] = [];

        for (let i : number = 0, len = this.monthsNames.length; i < len; i++) {
            monthsNames.push(this.getTranslation(this.monthsNames[i]));
        }

        return monthsNames;
    }

    public getShortMonthsNames () : string[] {
        const shortMonthsNames : string[] = [];

        for (let i : number = 0, len = this.shortMonthsNames.length; i < len; i++) {
            const name : string = this.shortMonthsNames[i];
            const translated : string = this.getTranslation(name + (name.toLowerCase() == 'may' ? '2' : ''));
            shortMonthsNames.push(translated.toLowerCase() == 'may2' ? name : translated);
        }

        return shortMonthsNames;
    }

    public getTimeMarksNames () : { [ key : string] : string } {
        return {
            AM: this.getTranslation('AM'),
            PM: this.getTranslation('PM')
        };
    }
}
