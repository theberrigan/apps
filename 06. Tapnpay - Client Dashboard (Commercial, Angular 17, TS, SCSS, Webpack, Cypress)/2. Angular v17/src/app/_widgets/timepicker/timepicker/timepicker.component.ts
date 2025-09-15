import {
    ChangeDetectorRef,
    Component,
    DoCheck,
    forwardRef,
    HostListener,
    OnChanges,
    Self,
    SimpleChanges
} from '@angular/core';
import {
    AbstractControl,
    ControlValueAccessor,
    NG_VALIDATORS,
    NG_VALUE_ACCESSOR, NgControl,
    ValidationErrors,
    Validator
} from "@angular/forms";


@Component({
    selector: 'app-timepicker',
    templateUrl: './timepicker.component.html',
    styleUrls: ['./timepicker.component.scss'],
    providers: [
        {
            provide: NG_VALUE_ACCESSOR,
            useExisting: forwardRef(() => TimepickerComponent),
            multi: true
        },

        {
            provide: NG_VALIDATORS,
            useExisting: forwardRef(() => TimepickerComponent),
            multi: true,
        },
    ],
})
export class TimepickerComponent implements ControlValueAccessor, Validator {

    internalValue: string;
    displayValue: string;

    isShowDropdown = false;
    currentTime = new Date();


    hourInputValue: string = '';
    minuteInputValue: string = '';
    meridiemInputValue = 'AM';


    onChange = (value: any) => {
    };

    onTouched = () => {
    };

    constructor(private cdr: ChangeDetectorRef) {

    }

    isValid12hTime(time: string): boolean {
        const pattern = /^(0[1-9]|1[0-2]):([0-5][0-9]) (AM|PM)$/;
        return pattern.test(time);
    }


    toggleDropdown(): void {
        this.isShowDropdown = !this.isShowDropdown;
        if (this.isShowDropdown) {
            this.internalValue ? this.setTimeToInputs(new Date(this.internalValue)) : this.setCurrentTime12hToInputs();
        }
    }

    setTimeValueFromSelector(): void {
        this.displayValue = `${this.hourInputValue}:${this.minuteInputValue} ${this.meridiemInputValue}`;
        this.internalValue = this.convert12hTimeFormatToISODateString(this.displayValue);
        this.onChange(this.internalValue);
        setTimeout(() => this.isShowDropdown = false);
        this.cdr.detectChanges();
    }

    @HostListener('document:click', ['$event'])
    clickOutside(event: Event): void {
        if (!event.target['closest']('.timepicker')) {
            this.isShowDropdown = false;
        }
    }

    private convert12hTimeFormatToISODateString(timeString: string): string {
        const date = new Date();
        const [time, meridiem] = timeString.split(' ');
        const [hoursStr, minutesStr] = timeString.split(':');
        const hoursNumber = parseInt(hoursStr, 10);
        const minutesNumber = parseInt(minutesStr, 10);

        if (meridiem === 'PM' && hoursNumber < 12) {
            date.setHours(hoursNumber + 12);
        } else if (meridiem === 'AM' && hoursNumber === 12) {
            date.setHours(0);
        } else {
            date.setHours(hoursNumber);
        }

        date.setMinutes(minutesNumber);
        return date.toISOString();
    }

    private convertISODateStringTo12hTimeFormat(dateString: string): string {
        const date = new Date(dateString);
        const hours = date.getHours();
        const minutes = date.getMinutes();
        const meridiem = this.getMerridiemByHour(hours);

        const hours12 = this.parseHour24To12String(hours);
        const minutesStr = this.numberToString(minutes);

        return `${hours12}:${minutesStr} ${meridiem}`;
    }


    numberToString(number: number): string {
        return number < 10 ? `0${number}` : `${number}`;
    }

    writeValue(value: any): void {
        this.internalValue = value;
        this.displayValue = value ? this.convertISODateStringTo12hTimeFormat(value) : '';
    }

    registerOnChange(fn: any): void {
        this.onChange = fn;
    }


    registerOnTouched(fn: any): void {
        this.onTouched = fn;
    }

    setDisabledState?(isDisabled: boolean) {

    }

    validate(control: AbstractControl): ValidationErrors | null {
        return null;
    }

    private setTimeToInputs(date: Date) {
        const hours = date.getHours();
        const minutes = date.getMinutes();

        this.hourInputValue = this.parseHour24To12String(hours);
        this.minuteInputValue = this.formatNumberWithZero(minutes);
        this.meridiemInputValue = this.getMerridiemByHour(hours);

        this.displayValue = `${this.hourInputValue}:${this.minuteInputValue} ${this.meridiemInputValue}`;
        this.internalValue = this.convert12hTimeFormatToISODateString(this.displayValue);

    }


    private setCurrentTime12hToInputs() {
        const currentTime = new Date();
        const currentHours = this.parseHour24To12String(currentTime.getHours());
        const currentMinutes = this.numberToString(currentTime.getMinutes());
        const currentMeridiem = this.getMerridiemByHour(currentTime.getHours());

        this.hourInputValue = currentHours;
        this.minuteInputValue = currentMinutes;
        this.meridiemInputValue = currentMeridiem;

    }


    parseStringNumberToNumber(stringNumber: string): number {
        return parseInt(stringNumber, 10);
    }

    parseHour24To12String(hour: number): string {
        let transformedHour = hour > 12 ? hour - 12 : hour;
        return this.formatNumberWithZero(transformedHour);
    }

    formatNumberWithZero(value: number): string {
        return value < 10 ? `0${value}` : `${value}`;
    }

    public adjustHour(operation: 'plus' | 'minus', delta: number): void {
        const hour = this.parseStringNumberToNumber(this.hourInputValue);
        let newHour = operation === 'plus' ? hour + delta : hour - delta;
        if (newHour < 0) {
            newHour = 12;
        }
        if (newHour > 12) {
            newHour = 0;
        }
        this.hourInputValue = this.formatNumberWithZero(newHour);
    }

    public adjustMinute(operation: 'plus' | 'minus', delta: number): void {
        const minute = this.parseStringNumberToNumber(this.minuteInputValue);
        let newMinute = operation === 'plus' ? minute + delta : minute - delta;
        if (newMinute < 0) {
            newMinute = 59;
        }
        if (newMinute > 59) {
            newMinute = 0;
        }
        this.minuteInputValue = this.formatNumberWithZero(newMinute);

    }

    onInput(event: Event) {
        const inputValue = (event.target as HTMLInputElement).value;
        this.displayValue = inputValue;
        this.internalValue = this.convert12hTimeFormatToISODateString(inputValue);
        this.onChange(this.internalValue);
        this.onTouched();
        this.isShowDropdown = false;
    }

    setMeridiem(period: 'AM' | 'PM') {
        this.meridiemInputValue = period;
    }

    public isActiveMeridiem(period: 'AM' | 'PM'): boolean {
        return this.meridiemInputValue === period;
    }

    getMerridiemByHour(hour: number): 'AM' | 'PM' {
        return hour > 12 ? 'PM' : 'AM';
    }
}
