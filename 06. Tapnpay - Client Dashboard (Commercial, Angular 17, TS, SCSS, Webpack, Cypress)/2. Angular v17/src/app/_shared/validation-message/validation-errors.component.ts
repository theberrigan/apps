import {Component, HostBinding, Input, OnChanges, OnInit} from '@angular/core';
import {AbstractControl, UntypedFormControl, UntypedFormGroup} from "@angular/forms";

@Component({
    selector: 'app-validation-errors',
    templateUrl: './validation-errors.component.html',
    styleUrls: ['./validation-errors.component.scss'],
})
export class ValidationErrorsComponent implements OnInit, OnChanges {
    @Input() validatedFormControl: AbstractControl | UntypedFormGroup = new UntypedFormControl('');
    @Input() requiredErrorMessage: string;
    @Input() messageTextAlign: 'left' | 'right' = 'right';
    @Input() maxRentalPeriodDate: Date | null = null;

    @HostBinding('class.text-left') get leftAlign() {
        return this.messageTextAlign === 'left';
    }

    @HostBinding('class.text-right') get rightAlign() {
        return this.messageTextAlign === 'right';
    }

    constructor() {
    }

    ngOnInit(): void {

    }

    ngOnChanges(): void {

    }

}
