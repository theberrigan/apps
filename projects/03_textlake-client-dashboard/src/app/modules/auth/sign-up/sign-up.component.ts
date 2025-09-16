import {Component, EventEmitter, OnInit, Output, ViewEncapsulation} from '@angular/core';
import {FormBuilder, FormGroup, Validators} from '@angular/forms';
import {Router} from '@angular/router';
// import {UserService} from '../../../services/user.service';
import {passwordValidator} from '../../../validators/password.validator';
import {UserService} from '../../../services/user.service';
// import {TitleService} from '../../../services/title.service';

@Component({
    selector: 'sign-up',
    templateUrl: './sign-up.component.html',
    encapsulation: ViewEncapsulation.None,
    host: {
        class: 'auth__form'
    }
})
export class SignUpComponent implements OnInit {
    public form : FormGroup;

    public message : any;

    public isRequest : boolean = false;

    @Output()
    public onProgressStateChange = new EventEmitter<boolean>();

    @Output()
    public onAfterSignIn = new EventEmitter<void>();

    constructor (
        private router : Router,
        private formBuilder : FormBuilder,
        private userService : UserService,
        // private titleService : TitleService
    ) {
        // this.titleService.setTitle('auth.sign_up.page_title');

        this.form = this.formBuilder.group({
            email: [
                '',
                [
                    Validators.required,
                    Validators.email
                ]
            ],
            password: [
                '',
                [
                    Validators.required,
                    passwordValidator
                ]
            ],
        });
    }

    public ngOnInit () : void {
        this.userService.onAuthMessage
            .asObservable()
            .subscribe((message) => {
                this.message = message;
            });
    }

    public onSubmit () : void {
        if (this.form.disabled) {
            return;
        }

        this.isRequest = true;
        this.form.disable();
        this.onProgressStateChange.emit(true);
        this.message = null;

        // this.userService
        //     .signUp(this.form.getRawValue())
        //     .then((result : any) => {
        //         this.isRequest = false;
        //         this.form.enable();
        //         this.onProgressStateChange.emit(false);
        //
        //         switch (result.action) {
        //             case 'ERROR':
        //                 this.message = {
        //                     type: 'error',
        //                     messageKey: result.error,
        //                     messageData: result.errorData
        //                 };
        //                 break;
        //             case 'COMPLETE':
        //                 this.onAfterSignIn.emit();
        //                 break;
        //             case 'PLAN':
        //                 this.router.navigateByUrl('/dashboard/plan');
        //                 break;
        //             default:
        //                 console.warn('Unexpected behavior');
        //         }
        //     });
    }
}
