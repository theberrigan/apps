import {Component, EventEmitter, OnInit, Output, ViewEncapsulation} from '@angular/core';
import {ActivatedRoute, Router} from '@angular/router';
import {FormBuilder, FormGroup, Validators} from '@angular/forms';
import {UserService} from '../../../services/user.service';
import {passwordValidator} from '../../../validators/password.validator';
import {TitleService} from '../../../services/title.service';

@Component({
    selector: 'new-password',
    templateUrl: './new-password.component.html',
    encapsulation: ViewEncapsulation.None,
    host: {
        class: 'auth__form'
    }
})
export class NewPasswordComponent implements OnInit {
    public form : FormGroup;

    public extra : any;

    public message : any;

    public isRequest : boolean = false;

    @Output()
    public onProgressStateChange = new EventEmitter<boolean>();

    @Output()
    public onAfterSignIn = new EventEmitter<void>();

    constructor (
        private formBuilder : FormBuilder,
        private router : Router,
        private route : ActivatedRoute,
        private userService : UserService,
        private titleService : TitleService
    ) {
        this.titleService.setTitle('auth.new_password.page_title');
    }

    public ngOnInit () : void {
        this.message = {
            type: 'info',
            messageKey: 'auth.new_password.set_new_password__message'
        };

        const newPasswordData : any = this.userService.getRouterData('new-password') || {};

        this.form = this.formBuilder.group({
            newPassword: [
                '',
                [
                    Validators.required,
                    passwordValidator
                ]
            ]
        });

        if (!(this.extra = newPasswordData.extra)) {
            this.router.navigateByUrl('/auth/sign-in');
            return;
        }
    }

    public onSubmit () : void {
        if (this.form.disabled) {
            return;
        }

        this.isRequest = true;
        this.form.disable();
        this.onProgressStateChange.emit(true);
        this.message = null;

        this.userService
            .completeNewPasswordChallenge({
                ...this.form.getRawValue(),  // newPassword
                ...this.extra        // email, remember, user, userAttributes
            })
            .then((result : any) => {
                this.isRequest = false;
                this.form.enable();
                this.onProgressStateChange.emit(false);

                switch (result.action) {
                    case 'COMPLETE':
                        this.onAfterSignIn.emit();
                        break;
                    case 'ERROR':
                        this.message = {
                            type: 'error',
                            messageKey: result.error,
                            messageData: result.errorData
                        };
                        break;
                    default:
                        console.warn('Unexpected behavior');
                }
            });
    }
}
