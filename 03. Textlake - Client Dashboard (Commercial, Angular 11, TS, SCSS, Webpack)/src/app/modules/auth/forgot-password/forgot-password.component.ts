import {Component, EventEmitter, Output, ViewEncapsulation} from '@angular/core';
import {ActivatedRoute, Router} from '@angular/router';
import {FormBuilder, FormGroup, Validators} from '@angular/forms';
// import {UserService} from '../../../services/user.service';
// import {TitleService} from '../../../services/title.service';

@Component({
    selector: 'forgot-password',
    templateUrl: './forgot-password.component.html',
    encapsulation: ViewEncapsulation.None,
    host: {
        class: 'auth__form'
    }
})
export class ForgotPasswordComponent {
    public form : FormGroup;

    @Output()
    public onProgressStateChange = new EventEmitter<boolean>();

    public message : any;

    public isRequest : boolean = false;

    constructor (
        private formBuilder : FormBuilder,
        private router : Router,
        private route : ActivatedRoute,
        // private userService : UserService,
        // private titleService : TitleService
    ) {
        // this.titleService.setTitle('auth.forgot_password.page_title');
    }

    public ngOnInit () : void {
        this.message = {
            type: 'info',
            messageKey: 'auth.forgot_password.enter_email__message'
        };

        this.form = this.formBuilder.group({
            email: [
                (this.route.snapshot.queryParams.email || '').trim(),
                [
                    Validators.required,
                    Validators.email
                ]
            ]
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
    }
}
