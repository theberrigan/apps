import {
    Component, ElementRef, forwardRef, HostBinding, HostListener, Input,
    ViewEncapsulation
} from '@angular/core';
import {ControlValueAccessor, NG_VALUE_ACCESSOR} from '@angular/forms';

@Component({
    selector: 'switch',
    exportAs: 'switch',
    templateUrl: './switch.component.html',
    styleUrls: [ './switch.component.scss' ],
    encapsulation: ViewEncapsulation.None,
    host: {
        'class': 'switch'
    },
    providers: [
        {
            provide: NG_VALUE_ACCESSOR,
            useExisting: forwardRef(() => SwitchComponent),
            multi: true
        }
    ],
})
export class SwitchComponent implements ControlValueAccessor {
    @HostBinding('class.switch_on')
    isOn : boolean = false;

    @Input()
    @HostBinding('class.switch_disabled')
    isDisabled : boolean = false;

    onTouched : any = () => {};

    onChange : any = (_ : any) => {};

    constructor (
        public hostEl : ElementRef
    ) {}

    @HostListener('click')
    onHostClick () {
        if (this.checkDisabled()) {
            return;
        }

        this.isOn = !this.isOn;

        if (this.onChange) {
            this.onChange(this.isOn);
        }

        if (this.onTouched) {
            this.onTouched();
        }
    }

    @HostListener('blur')
    onBlur () {
        if (this.onTouched) {
            this.onTouched();
        }
    }

    checkDisabled () : boolean {
        return this.isDisabled || !!this.hostEl.nativeElement.closest('fieldset:disabled');
    }

    writeValue (isOn : boolean) {
        this.isOn = !!isOn;
    }

    registerOnChange (fn : any) {
        this.onChange = fn;
    }

    registerOnTouched (fn : any) {
        this.onTouched = fn;
    }

    setDisabledState (isDisabled : boolean) {
        this.isDisabled = !!isDisabled;
    }
}
