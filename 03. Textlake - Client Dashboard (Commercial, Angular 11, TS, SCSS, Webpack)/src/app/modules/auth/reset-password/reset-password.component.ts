import {Component, EventEmitter, OnInit, Output, ViewEncapsulation} from '@angular/core';
import {ActivatedRoute, Router} from '@angular/router';
import {FormBuilder, FormControl, FormGroup, Validators} from '@angular/forms';
// import {UserService} from '../../../services/user.service';
import {passwordValidator} from '../../../validators/password.validator';
// import {TitleService} from '../../../services/title.service';
// import {ToastService} from '../../../services/toast.service';

@Component({
    selector: 'reset-password',
    templateUrl: './reset-password.component.html',
    encapsulation: ViewEncapsulation.None,
    host: {
        class: 'auth__form'
    }
})
export class ResetPasswordComponent implements OnInit {
    public form : FormGroup;

    public extra : any;

    public isUnknownUser : boolean = false;

    public message : any;

    public isRequest : boolean = false;

    @Output()
    public onProgressStateChange = new EventEmitter<boolean>();

    constructor (
        private formBuilder : FormBuilder,
        private router : Router,
        private route : ActivatedRoute,
        // private userService : UserService,
        // private titleService : TitleService,
        // private toastService : ToastService
    ) {
        // this.titleService.setTitle('auth.reset_password.page_title');
    }

    public ngOnInit () : void {
        const code : string = (this.route.snapshot.queryParams.code || '').trim();

        // const resetPasswordData : any = this.userService.getRouterData('reset-password') || {};
        // this.extra = resetPasswordData.extra || {};
        this.extra = {};

        this.form = this.formBuilder.group({
            code: [ code, Validators.required ],
            newPassword: [
                '',
                [
                    Validators.required,
                    passwordValidator
                ]
            ]
        });

        this.isUnknownUser = !this.extra.user;

        if (this.isUnknownUser) {
            this.form.addControl('email', new FormControl('', [ Validators.required, Validators.email ]));
        }

        if (this.extra.destination) {
            this.message = {
                type: 'info',
                messageKey: 'auth.reset_password.code_sent_to__message',
                messageData: {
                    destination: this.extra.destination
                }
            };
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

        /*
        this.userService
            .confirmPassword({
                ...this.form.getRawValue(),  // code, newPassword, email?
                ...this.extra        // user (CognitoUser instance)
            })
            .then((result : any) => {
                this.isRequest = false;
                this.form.enable();
                this.onProgressStateChange.emit(false);

                switch (result.action) {
                    case 'COMPLETE':
                        this.toastService.create({
                            message: [ `auth.reset_password.reset_ok` ]
                        });
                        this.router.navigateByUrl('/auth/sign-in');
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
         */
    }
}
