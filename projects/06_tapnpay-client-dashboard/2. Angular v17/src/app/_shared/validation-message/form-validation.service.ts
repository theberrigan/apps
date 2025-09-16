import {Injectable} from '@angular/core';
import {AbstractControl, UntypedFormArray, UntypedFormControl, UntypedFormGroup} from "@angular/forms";

@Injectable({
    providedIn: 'root'
})
export class FormValidationService {

    constructor() {
    }

    public getFormControl(controlName: string, parentFormGroup: UntypedFormGroup): AbstractControl {
        if (parentFormGroup) {
            const field = parentFormGroup.get(controlName);
            return field ? field : new UntypedFormControl('');
        }
        return new UntypedFormControl('');
    }


    private makeFormGroupTouched(formGroup: UntypedFormGroup): void {
        if (formGroup) {
            formGroup.markAllAsTouched();
        }
    }

    public validateFormGroup(formGroup: UntypedFormGroup): void {
        if (formGroup) {
            this.makeFormGroupTouched(formGroup);
            this.markFormDirty(formGroup);
        }
    }

    private markFormDirty(form: UntypedFormGroup): void {
        this.markGroupDirty(form);
    }

    private markGroupDirty(formGroup: UntypedFormGroup) {
        Object.keys(formGroup.controls).forEach(key => {
            switch (formGroup.get(key).constructor.name) {
                case "FormGroup":
                    this.markGroupDirty(formGroup.get(key) as UntypedFormGroup);
                    break;
                case "FormArray":
                    this.markArrayDirty(formGroup.get(key) as UntypedFormArray);
                    break;
                case "FormControl":
                    this.markControlDirty(formGroup.get(key) as UntypedFormControl);
                    break;
            }
        });
    }

    private markArrayDirty(formArray: UntypedFormArray) {
        formArray.controls.forEach(control => {
            switch (control.constructor.name) {
                case "FormGroup":
                    this.markGroupDirty(control as UntypedFormGroup);
                    break;
                case "FormArray":
                    this.markArrayDirty(control as UntypedFormArray);
                    break;
                case "FormControl":
                    this.markControlDirty(control as UntypedFormControl);
                    break;
            }
        });
    }

    private markControlDirty(formControl: UntypedFormControl) {
        formControl.markAsDirty();
    }

    public deleteFormControlFromFormGroup(controlName: string, formGroup: UntypedFormGroup): void {
        if (formGroup) {
            formGroup.removeControl(controlName);
        }
    }

    public deleteAllFormControlsFromFormGroup(formGroup: UntypedFormGroup): void {
        if (formGroup) {
            const formControls = formGroup.controls;
            Object.keys(formControls).forEach(key => {
                formGroup.removeControl(key);
            })
        }
    }

}
