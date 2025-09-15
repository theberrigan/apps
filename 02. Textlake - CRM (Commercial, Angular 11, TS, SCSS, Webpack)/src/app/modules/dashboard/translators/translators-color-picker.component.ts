import {
    Component, forwardRef, HostListener, Input,
    OnDestroy,
    OnInit,
    ViewEncapsulation
} from '@angular/core';
import {ControlValueAccessor, NG_VALUE_ACCESSOR} from '@angular/forms';
import {cloneDeep, isArray} from 'lodash';
import {DomService} from '../../../services/dom.service';
import {uniqueId} from '../../../lib/utils';

@Component({
    selector: 'translators-color-picker',
    exportAs: 'translatorsColorPicker',
    templateUrl: './translators-color-picker.component.html',
    styleUrls: [ './translators-color-picker.component.scss' ],
    encapsulation: ViewEncapsulation.None,
    providers: [
        {
            provide: NG_VALUE_ACCESSOR,
            useExisting: forwardRef(() => TranslatorsColorPickerComponent),
            multi: true
        }
    ],
    host: {
        'class': 'translators-color-picker',
        '[class.translators-color-picker_disabled]': 'isDisabled'
    }
})
export class TranslatorsColorPickerComponent implements OnInit, OnDestroy, ControlValueAccessor {
    public color : string;

    public isDisabled : boolean = false;

    public colorCodes : string[] = [
        'f766be', 'ef4747', '9c27b0', '673ab7', '3f51b5',
        '2196f3', '00bcd4', '009688', '4caf50', '8bc34a',
        'cddc39', 'ffeb3b', 'ffc107', 'ff9800', 'ff5722',
        '795548', '607d8b', '000000', '1b5e20', '827717'
    ];

    public id : string;

    public isActive : boolean = false;

    public onTouched : any = () => {};

    public onChange : any = (_ : any) => {};

    constructor (
        private domService : DomService
    ) {
        this.id = uniqueId();
    }

    public ngOnInit () : void {

    }

    public ngOnDestroy () : void {

    }

    public writeValue (value : string) : void {
        this.color = (value || '').toLowerCase();
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

    public onColorSelect (color : string, e : any) : void {
        if (this.color !== color) {
            this.color = color;
            this.onChange(color);
        }
        this.domService.markEvent(e, 'colorCellClick' + this.id);
    }

    public onDisplayClick (e : any) {
        this.onTouched();
        this.domService.markEvent(e, 'displayClick' + this.id);
    }

    public onPopupClick (e : any) {
        this.domService.markEvent(e, 'popupClick' + this.id);
    }

    @HostListener('document:click', [ '$event' ])
    public onDocumentClick (e : any) : void {
        if (this.isDisabled) {
            return;
        }

        if (this.domService.hasEventMark(e, 'displayClick' + this.id)) {
            this.isActive = !this.isActive;
        } else if (
            this.domService.hasEventMark(e, 'colorCellClick' + this.id) ||
            !this.domService.hasEventMark(e, 'popupClick' + this.id)
        ) {
            this.isActive = false;
        }
    }
}




