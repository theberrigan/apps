import {
    AfterViewInit,
    Component, ElementRef, forwardRef,
    HostBinding,
    HostListener, Input,
    OnDestroy,
    OnInit, ViewChild,
    ViewEncapsulation
} from '@angular/core';
import {ControlValueAccessor, NG_VALUE_ACCESSOR} from '@angular/forms';

import flatpickr from 'flatpickr';

import * as English from 'flatpickr/dist/l10n/default.js';
import { Spanish } from 'flatpickr/dist/l10n/es.js';

import {LangService} from '../../../../services/lang.service';
import {DatetimeService} from '../../../../services/datetime.service';

const localeMap = {
    'en': English,
    'es': Spanish
};

// https://momentjs.com/docs/#/displaying/format/
// https://flatpickr.js.org/formatting/#date-formatting-tokens
const momentToFlatpickrFormatMap = {
    'DD': 'd',
    'ddd': 'D',
    'dddd': 'l',
    'D': 'j',
    'e': 'w',
    'W': 'W',
    'MMMM': 'F',
    'MM': 'm',
    'M': 'n',
    'MMM': 'M',
    'X': 'U',
    'YY': 'y',
    'YYYY': 'Y',
};

@Component({
    selector: 'flatpicker',
    exportAs: 'flatpicker',
    templateUrl: './flatpicker.component.html',
    styleUrls: [ './flatpicker.component.scss' ],
    encapsulation: ViewEncapsulation.None,
    providers: [
        {
            provide: NG_VALUE_ACCESSOR,
            useExisting: forwardRef(() => FlatpickerComponent),
            multi: true
        }
    ],
    host: {
        'class': 'datepicker'
    }
})
export class FlatpickerComponent implements OnInit, AfterViewInit, OnDestroy, ControlValueAccessor {
    @Input()
    isDisabled : boolean = false;

    @Input()
    format : string;

    public onTouched : any = () => {};

    public onChange : any = (_ : any) => {};

    @ViewChild('inputEl')
    inputEl : ElementRef;

    flatpickr : any;

    isActive : boolean = false;

    momentFormat : string;

    flatpickrFormat : string;

    model : Date;

    constructor (
        public el : ElementRef,
        public langService : LangService,
        public datetimeService : DatetimeService,
    ) {

    }

    // ISO String -> datepicker -> (format for fp, convert format for fp) -> set to input formatted, set to model ISO string
    // onChange => selectedDates[0] to Iso string
    public ngOnInit () : void {
        this.momentFormat = this.datetimeService.getFormatByAlias(this.format);
        this.flatpickrFormat = this.convertMomentToFlatpckrFormat(this.momentFormat);
    }

    public ngAfterViewInit () : void {
        const langCode = this.langService.getCurrentLangCode();

        this.flatpickr = flatpickr(this.inputEl.nativeElement, {
            locale: localeMap[langCode] || English,
            enableTime: false,
            dateFormat: this.flatpickrFormat,
            disableMobile: true,
            onOpen: () => this.setActivity(true),
            onClose: () => this.setActivity(false),
            onChange: (selectedDates : Date[]) => {
                const date : Date = selectedDates[0];
                this.onChange(date instanceof Date ? date.toISOString() : date);
            }
        });

        this.updateFlatpckrFromModel();
    }

    public ngOnDestroy () : void {
        if (this.flatpickr) {
            this.flatpickr.destroy();
        }
    }

    convertMomentToFlatpckrFormat (momentFormat : string) : string {
        const momentTokens = Object.keys(momentToFlatpickrFormatMap).sort((a, b) => b.length - a.length);
        let flatpickrFormat : string = momentFormat;

        momentTokens.forEach(momentToken => {
            flatpickrFormat = flatpickrFormat.replace(
                new RegExp(momentToken, 'g'),
                momentToFlatpickrFormatMap[momentToken]
            );
        });

        return flatpickrFormat;
    }

    setActivity (isActive : boolean) {
        this.isActive = isActive;
    }

    updateFlatpckrFromModel () {
        if (!this.flatpickr) {
            return;
        }

        this.flatpickr.setDate(this.model, false);
    }

    public onFocus () : void {
        this.onTouched();
    }

    public onBlur () : void {
        this.onTouched();
    }

    public writeValue (source : Date | string | number) : void {
        this.model = new Date(source);
        this.updateFlatpckrFromModel();
    }

    public registerOnChange (fn : any) : void {
        this.onChange = fn;
    }

    public registerOnTouched (fn : any) : void {
        this.onTouched = fn;
    }

    public setDisabledState (isDisabled : boolean) : void {
        this.isDisabled = isDisabled;
    }
}
