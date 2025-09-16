import {ChangeDetectorRef, Component, EventEmitter, OnInit, Output, ViewEncapsulation} from '@angular/core';
import {FormBuilder, FormGroup, Validators} from '@angular/forms';
// import {UserService} from '../../../services/user.service';
import {Router} from '@angular/router';
import {UserService} from '../../../services/user.service';
import {TitleService} from '../../../services/title.service';
// import {TitleService} from '../../../services/title.service';

@Component({
    selector: 'sign-in',
    templateUrl: './sign-in.component.html',
    encapsulation: ViewEncapsulation.None,
    host: {
        class: 'auth__form'
    }
})
export class SignInComponent implements OnInit {
    public form : FormGroup;

    public extra : any;

    public message : any;

    public isRequest : boolean = false;

    // This var used to bypass Chrome autofill shit
    public isUserInteracted : boolean = false;

    @Output()
    public onProgressStateChange = new EventEmitter<boolean>();

    @Output()
    public onAfterSignIn = new EventEmitter<void>();

    constructor (
        private router : Router,
        private formBuilder : FormBuilder,
        private userService : UserService,
        private titleService : TitleService
    ) {
        this.titleService.setTitle('auth.sign_in.page_title');

        const login : string = ''; // this.userService.restoreLogin();

        this.form = this.formBuilder.group({
            email: [
                login,
                [
                    Validators.required,
                    Validators.email
                ]
            ],
            password: [ '', Validators.required ],
            remember: [ !!login ]
        });
    }

    public ngOnInit () : void {
        const signInData : any = this.userService.getRouterData('sign-in') || {};
        this.message = signInData.message;

        this.form.statusChanges.subscribe(() => {
            this.isUserInteracted = true;
        });

        this.userService.onAuthMessage
            .asObservable()
            .subscribe((message) => {
                this.message = message;
            });
    }

    public forgotPassword (e : any) : void {
        e.preventDefault();

        if (this.isRequest) {
            return;
        }

        this.router.navigate([ '/auth/forgot-password' ], {
            queryParams: {
                email: this.form.controls['email'].value
            }
        });
    }

    public onSubmit () : void {
        if (this.form.invalid || this.isRequest) {
            return;
        }

        this.isRequest = true;
        this.form.disable();
        this.onProgressStateChange.emit(true);
        this.message = null;

        this.userService
            .signIn(this.form.getRawValue())
            .then((result : any) => {
                this.isRequest = false;
                this.form.enable();
                this.onProgressStateChange.emit(false);

                switch (result.action) {
                    case 'NEW_PASSWORD':
                        this.userService.setRouterData('new-password', {
                            extra: result.extra
                        });
                        this.router.navigateByUrl('/auth/new-password');
                        break;
                    case 'ERROR':
                        this.message = {
                            type: 'error',
                            messageKey: result.error,
                            messageData: result.errorData
                        };
                        break;
                    case 'COMPLETE':
                        this.onAfterSignIn.emit();
                        break;
                    case 'PLAN':
                        this.router.navigateByUrl('/dashboard/plan');
                        break;
                    default:
                        console.warn('Unexpected behavior');
                }
            });
    }
}
