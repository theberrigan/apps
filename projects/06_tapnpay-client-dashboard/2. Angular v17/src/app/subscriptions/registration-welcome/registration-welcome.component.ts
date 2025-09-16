import { Component, OnInit } from '@angular/core';
import { DialogRef } from "@angular/cdk/dialog";
import { TranslateService } from '@ngx-translate/core';
import { FormBuilder, FormGroup, Validators, AbstractControl } from '@angular/forms';
import { LangService } from '../../services/lang.service';
import { RegistrationService } from '../../services/registration.service';
import { finalize } from 'rxjs/operators';
import { Router } from '@angular/router';
import { NEO_RIDE_LOGO_URL } from '../../constants/logo.constants';

@Component({
    selector: 'app-registration-welcome',
    templateUrl: './registration-welcome.component.html',
    styleUrls: ['./registration-welcome.component.scss']
})
export class RegistrationWelcomeComponent implements OnInit {
    public isLoaded: boolean = true;
    public isSubmitting: boolean = false;
    public isSubmitted: boolean = false;
    public registrationForm: FormGroup;
    public attemptedSubmit: boolean = false;
    public languages = [
        { code: 'en', name: 'English' },
        { code: 'es', name: 'Spanish' }
    ];
    public termsUrl: string;
    public NEO_RIDE_LOGO_URL = NEO_RIDE_LOGO_URL;
    public submitted = false;

    // Custom validators
    private namePattern = /^[a-zA-Z\s-']+$/;
    private emailPattern = /^[a-zA-Z0-9._-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$/;

    constructor(
        public dialogRef: DialogRef<any>,
        private translate: TranslateService,
        private fb: FormBuilder,
        private langService: LangService,
        private registrationService: RegistrationService,
        private router: Router
    ) {
        this.registrationForm = this.fb.group({
            firstName: ['', [
                Validators.required,
                Validators.minLength(2),
                Validators.maxLength(50),
                Validators.pattern(this.namePattern)
            ]],
            lastName: ['', [
                Validators.required,
                Validators.minLength(2),
                Validators.maxLength(50),
                Validators.pattern(this.namePattern)
            ]],
            email: ['', [
                Validators.required,
                Validators.pattern(this.emailPattern),
                Validators.maxLength(100)
            ]],
            language: ['en', [Validators.required]],
            termsAccepted: [false, [Validators.requiredTrue]]
        });
    }

    ngOnInit() {
        // Set initial language selection based on current language
        const currentLang = this.translate.currentLang;
        this.registrationForm.patchValue({ language: currentLang });
        this.updateTermsUrl(currentLang);
    }

    onLanguageChange(event: any) {
        const langCode = event.target.value;
        this.langService.use(langCode).subscribe();
        this.updateTermsUrl(langCode);
    }

    updateTermsUrl(langCode: string) {
        this.termsUrl = `/assets/locale/terms/neoride-081623.${langCode}.html`;
    }

    openTerms() {
        window.open(this.termsUrl, '_blank');
    }

    showError(controlName: string): boolean {
        const control = this.registrationForm.get(controlName);
        return !!control && control.invalid && (control.dirty || (this.submitted && (control.value === '' || control.value === false)));
    }

    onContinue() {
        this.submitted = true;
        this.onSubmit();
    }

    onSubmit() {
        this.attemptedSubmit = true;
        if (this.registrationForm.valid && !this.isSubmitting) {
            this.isSubmitting = true;
            
            const formData = this.registrationForm.value;
            const registrationData = {
                first_name: formData.firstName,
                last_name: formData.lastName,
                email: formData.email,
                terms_accepted: formData.termsAccepted,
                language: formData.language
            };

            this.registrationService.registerUser(registrationData)
                .pipe(
                    finalize(() => this.isSubmitting = false)
                )
                .subscribe({
                    next: (response) => {
                        if (response.status === 'Success') {
                            this.dialogRef.close(true);
                        } else if (response.status === 'EmailAlreadyExists') {
                            const emailControl = this.registrationForm.get('email');
                            emailControl?.setErrors({ emailExists: true });
                            emailControl?.markAsTouched();
                        } else {
                            console.error('Unexpected registration response:', response);
                        }
                    },
                    error: (error) => {
                        if (error.status === 409) {
                            const emailControl = this.registrationForm.get('email');
                            emailControl?.setErrors({ emailExists: true });
                            emailControl?.markAsTouched();
                        } else {
                            console.error('Registration error:', error);
                        }
                    }
                });
        }
    }

    onCancel() {
        this.dialogRef.close();
        this.router.navigate(['/auth']);
    }

    // Helper methods to get error messages
    getFirstNameErrorMessage(): string {
        const control = this.registrationForm.get('firstName');
        if (control?.errors) {
            if (control.errors['required']) {
                return this.translate.instant('registration.first_name_required');
            }
            if (control.errors['minlength']) {
                return this.translate.instant('registration.first_name_min_length');
            }
            if (control.errors['maxlength']) {
                return this.translate.instant('registration.first_name_max_length');
            }
            if (control.errors['pattern']) {
                return this.translate.instant('registration.first_name_invalid_chars');
            }
        }
        return '';
    }

    getLastNameErrorMessage(): string {
        const control = this.registrationForm.get('lastName');
        if (control?.errors) {
            if (control.errors['required']) {
                return this.translate.instant('registration.last_name_required');
            }
            if (control.errors['minlength']) {
                return this.translate.instant('registration.last_name_min_length');
            }
            if (control.errors['maxlength']) {
                return this.translate.instant('registration.last_name_max_length');
            }
            if (control.errors['pattern']) {
                return this.translate.instant('registration.last_name_invalid_chars');
            }
        }
        return '';
    }

    getEmailErrorMessage(): string {
        const control = this.registrationForm.get('email');
        if (control?.errors) {
            if (control.errors['required']) {
                return this.translate.instant('registration.email_required');
            }
            if (control.errors['pattern']) {
                return this.translate.instant('registration.email_invalid');
            }
            if (control.errors['maxlength']) {
                return this.translate.instant('registration.email_max_length');
            }
            if (control.errors['emailExists']) {
                return this.translate.instant('registration.email_exists');
            }
        }
        return '';
    }

    getTermsErrorMessage(): string {
        const control = this.registrationForm.get('termsAccepted');
        if (control?.errors && control.errors['required']) {
            return this.translate.instant('registration.terms_required');
        }
        return '';
    }
} 