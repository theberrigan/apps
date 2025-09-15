import {ChangeDetectionStrategy, Component, OnInit, Renderer2, ViewEncapsulation} from '@angular/core';
import {Router} from '@angular/router';
import {UntypedFormBuilder, UntypedFormGroup} from '@angular/forms';
import {TitleService} from '../../../services/title.service';
import {defer} from '../../../lib/utils';
import {ToastService} from '../../../services/toast.service';
import {ContactUsRequestData, ContactUsService} from '../../../services/contact-us.service';
import {UserService} from '../../../services/user.service';
import { Subscription } from 'rxjs';
import { NgRecaptcha3Service } from "ng-recaptcha3";
import {CONFIG} from '../../../../../config/app/dev';
@Component({
    selector: 'contact-us-inner',
    templateUrl: './contact-us-inner.component.html',
    styleUrls: [ './contact-us-inner.component.scss' ],
    changeDetection: ChangeDetectionStrategy.Default,
    encapsulation: ViewEncapsulation.None,
    host: {
        'class': 'contact-us-inner'
    }
})
export class ContactUsInnerComponent implements OnInit {
    isFormValid : boolean = false;

    isSubmitting : boolean = false;

    form : UntypedFormGroup;

    isDashboard : boolean = false;

    brandOptions = [
        {
            value: null,
            display: '',
        },
        {
            value: 'NTTA',
            display: 'Dallas/Ft Worth',
        },
        {
            value: 'SUNPASS',
            display: 'Florida',
        },
        {
            value: 'FASTRAK',
            display: 'California',
        },
        {
            value: 'IPASS',
            display: 'Illinois',
        },
        {
            value: 'GOODTOGO',
            display: 'Washington',
        },
        {
            value: 'TXHUB',
            display: 'Texas/Oklahoma/Kansas',
        },
    ];

    userBrand : string = null;

    constructor (
        private renderer : Renderer2,
        private router : Router,
        private formBuilder : UntypedFormBuilder,
        private titleService : TitleService,
        private toastService : ToastService,
        private userService : UserService,
        private contactUsService : ContactUsService,
        private recaptcha3: NgRecaptcha3Service
    ) {
        window.scroll(0, 0);
    }

    public ngOnInit () {
        this.titleService.setTitle('contact_us.page_title');

        this.isDashboard = this.router.url.toLowerCase().startsWith('/dashboard');

        this.userBrand = null;
        this.recaptcha3.init(CONFIG.RECAPTCHA_SITE_KEY);
        this.resetForm();
    }

    validate () {
        defer(() => {
            const form = this.form.getRawValue();

            this.isFormValid = !!(
                form.firstName.trim() &&
                form.lastName.trim() &&
                form.email.trim() &&
                form.phone.trim() &&
                form.comment.trim()
            );
        });
    }

    resetForm () {
        if (this.form) {
            this.form.reset({
                firstName: '',
                lastName: '',
                email: '',
                phone: '',
                brand: this.userBrand,
                comment: '',
            }, { emitEvent: true });
        } else {
            this.form = this.formBuilder.group({
                firstName: [ '' ],
                lastName: [ '' ],
                email: [ '' ],
                phone: [ '' ],
                brand: [ this.userBrand ],
                comment: [ '' ]
            });

            this.validate();
            this.form.valueChanges.subscribe(() => this.validate());
        }
    }

    onSubmit () {
        if (!this.isFormValid || this.isSubmitting) {
            return;
        }
        this.isSubmitting = true;

        this.recaptcha3.getToken().then(
            token => {
                // console.log({token})
                this.sendContactForm(token);
            },
            error => {
              // handle error here
              console.log(error);
              this.isSubmitting = false;
            }
          );

    }

    sendContactForm(token){

        const formData = this.form.getRawValue();
        const requestData : ContactUsRequestData = {
            email: formData.email.trim(),
            phone: formData.phone.trim(),
            comment: formData.comment.trim(),
            first_name: formData.firstName.trim(),
            last_name: formData.lastName.trim(),
            brand: formData.brand
        };

        this.contactUsService.sendData(requestData,token).subscribe(
            (isOk : boolean) => this.onResponse(isOk),
            () => this.onResponse(false)
        );
    }

    onResponse (isOk : boolean) {
        this.isSubmitting = false;

        if (isOk) {
            this.resetForm();

            this.toastService.create({
                message: [ 'contact_us.submit.ok' ],
                timeout: 7000
            });
        } else {
            this.toastService.create({
                message: [ 'contact_us.submit.error' ],
                timeout: 7000
            });
        }
    }

    ngOnDestroy(): void {
            this.recaptcha3.destroy();
      }
}
