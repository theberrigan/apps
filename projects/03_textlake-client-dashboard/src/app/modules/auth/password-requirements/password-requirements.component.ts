import {Component, HostBinding, Input, OnDestroy, OnInit, Renderer2, ViewEncapsulation} from '@angular/core';
import {isString} from 'lodash';
import {
    IPasswordRequirements,
    PasswordRequirementsStatus, REQUIREMENTS,
    SPECIAL_CHARACTERS_REGEXP
} from '../../../validators/password.validator';


@Component({
    selector: 'password-requirements',
    templateUrl: './password-requirements.component.html',
    styleUrls: [ './password-requirements.component.scss' ],
    encapsulation: ViewEncapsulation.None,
    host: {
        class: 'password-requirements',
    }
})
export class PasswordRequirementsComponent implements OnDestroy {
    @Input()
    public set password (value : string) {
        value = isString(value) ? value : '';

        this.requirementsStatus = {
            minLength: value.length >= (this.requirements.minLength || 0),
            specialCharacters: SPECIAL_CHARACTERS_REGEXP.test(value),
            lowercaseLetters: value !== value.toUpperCase(),
            uppercaseLetters: value !== value.toLowerCase(),
            digits: /\d/.test(value),
        };
    }

    @Input()
    public set input (input : any) {
        this.unlisten();

        if (input) {
            this.listeners = [
                this.renderer.listen(input, 'focusin', () => this.isActive = true),
                this.renderer.listen(input, 'focusout', () => this.isActive = false),
            ];
        }
    }

    @HostBinding('class.password-requirements_active')
    public isActive : boolean = false;

    public readonly requirements : IPasswordRequirements;

    public requirementsStatus : PasswordRequirementsStatus;

    public listeners : any[];

    constructor (
        public renderer : Renderer2
    ) {
        this.requirements = REQUIREMENTS;
        this.requirementsStatus = new PasswordRequirementsStatus();
    }

    public ngOnDestroy () : void {
        this.unlisten();
    }

    public unlisten () : void {
        if (this.listeners) {
            this.listeners.forEach(unlisten => unlisten());
            this.listeners = [];
        }
    }
}
