import {AbstractControl} from '@angular/forms';
import {CONFIG} from '../../../config/app/dev';

export const REQUIREMENTS : IPasswordRequirements = CONFIG.passwordRequirements as IPasswordRequirements;

// https://docs.aws.amazon.com/en_us/cognito/latest/developerguide/user-pool-settings-policies.html
export const SPECIAL_CHARACTERS = '^$*.[]{}()?-"!@#%&/\\,><\':;|_~`';
export const SPECIAL_CHARACTERS_REGEXP = /[\^$*.[\]{}()?\-"!@#%&/\\,><':;|_~`]/;

export class IPasswordRequirements {
    minLength : number;
    specialCharacters : boolean;
    lowercaseLetters : boolean;
    uppercaseLetters : boolean;
    digits : boolean;
}

export class PasswordRequirementsStatus {
    minLength : boolean = false;
    specialCharacters : boolean = false;
    lowercaseLetters : boolean = false;
    uppercaseLetters : boolean = false;
    digits : boolean = false;
}


export const passwordValidator = (control : AbstractControl) => {
    const value : string = control.value || '';

    const isValid : boolean = (
        (REQUIREMENTS.minLength ? value.length >= REQUIREMENTS.minLength : true) &&
        (REQUIREMENTS.specialCharacters ? SPECIAL_CHARACTERS_REGEXP.test(value) : true) &&
        (REQUIREMENTS.lowercaseLetters ? value !== value.toUpperCase() : true) &&
        (REQUIREMENTS.uppercaseLetters ? value !== value.toLowerCase() : true) &&
        (REQUIREMENTS.digits ? /\d/.test(value) : true)
    );

    return isValid ? null : { 'password' : { value: control.value }};
};
