import {Component, forwardRef} from '@angular/core';
import {ControlValueAccessor, NG_VALUE_ACCESSOR} from "@angular/forms";

@Component({
    selector: 'app-switch',
    templateUrl: './switch.component.html',
    styleUrls: ['./switch.component.scss'],
    providers: [
        {
            provide: NG_VALUE_ACCESSOR,
            useExisting: forwardRef(() => SwitchComponent),
            multi: true
        }
    ]
})
export class SwitchComponent implements ControlValueAccessor {
    checked: boolean = false;
    private onChange: any = () => {
    };
    private onTouched: any = () => {
    };

    toggle(): void {
        this.checked = !this.checked;
        this.onChange(this.checked);
        this.onTouched();
    }

    writeValue(value: any): void {
        this.checked = value;
    }

    registerOnChange(fn: any): void {
        this.onChange = fn;
    }

    registerOnTouched(fn: any): void {
        this.onTouched = fn;
    }

    setDisabledState?(isDisabled: boolean): void {
        // Implement this method to handle the disabled state if needed
    }

}
