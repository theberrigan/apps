import {
    Component, forwardRef,
    HostBinding,
    HostListener, Input,
    OnDestroy,
    OnInit,
    ViewEncapsulation
} from '@angular/core';
import {ControlValueAccessor, NG_VALUE_ACCESSOR} from '@angular/forms';

@Component({
    selector: 'checkbox',
    exportAs: 'checkbox',
    templateUrl: './checkbox.component.html',
    styleUrls: [ './checkbox.component.scss' ],
    encapsulation: ViewEncapsulation.None,
    providers: [
        {
            provide: NG_VALUE_ACCESSOR,
            useExisting: forwardRef(() => CheckboxComponent),
            multi: true
        }
    ],
    host: {
        'class': 'checkbox'
    }
})
export class CheckboxComponent implements OnInit, OnDestroy, ControlValueAccessor {
    @HostBinding('class.checkbox_disabled')
    public isDisabled : boolean = false;

    @HostBinding('class.checkbox_active')
    public isActive : boolean = false;

    @Input()
    @HostBinding('class.checkbox_without-caption')
    public withoutCaption : boolean = false;

    public onTouched : any = () => {};

    public onChange : any = (_ : any) => {};

    constructor () {}

    public ngOnInit () : void {

    }

    public ngOnDestroy () : void {

    }

    @HostListener('click')
    public onClick () : void {
        if (!this.isDisabled) {
            this.isActive = !this.isActive;
            this.onChange(this.isActive);
            this.onTouched();
        }
    }

    @HostListener('blur')
    public onBlur () : void {
        this.onTouched();
    }

    public writeValue (isActive : boolean) : void {
        this.isActive = isActive;
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
