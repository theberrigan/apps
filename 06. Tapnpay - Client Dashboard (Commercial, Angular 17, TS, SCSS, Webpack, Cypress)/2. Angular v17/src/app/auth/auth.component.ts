import {
    ChangeDetectionStrategy,
    Component,
    ElementRef,
    HostListener,
    NgZone,
    OnDestroy,
    OnInit,
    Renderer2,
    ViewChild,
    ViewEncapsulation
} from '@angular/core';
import {Router} from '@angular/router';
import {TitleService} from '../services/title.service';
import {defer} from '../lib/utils';
import {FormControl, FormGroup, UntypedFormBuilder, Validators} from '@angular/forms';
import {ToastService} from '../services/toast.service';
import {animate, style, transition, trigger} from '@angular/animations';
import {firstValueFrom, Subscription, timer} from 'rxjs';
import {debounceTime, distinctUntilChanged, map, take} from 'rxjs/operators';
import {DomService} from '../services/dom.service';
import {TEST_ACCOUNT_CREATE_PHONES, UserService} from '../services/user.service';
import {TermsService, TermsSession} from '../services/terms.service';
import {MessageService} from '../services/message.service';
import {DebugService} from '../services/debug.service';

enum AUTH_FIELDS {
    PHONE = 'phone',
    PIN_CODE = 'pin'
}

export interface AuthData {
    token: string;
    phone: string;
    pin: number;
}

const minPinCodeLength = 4;

const {required, maxLength, minLength} = Validators;

type authErrorsCodes = 100 | 102 | 104 | 105 | 107 | 108;

enum TnpResponseStatusCode {
    AUTHENTICATION_ERROR = 100,
    AUTHENTICATION_REQUIRED = 101,
    PIN_DEACTIVATED = 102,
    MISSING_ROLE = 103,
    REQUEST_THROTTLED = 104,
    ACCOUNT_LOCKED = 105,
    STRIPE_WEBHOOK_SIGNATURE_ERROR = 106,
    MOBILE_APP_LOGIN_DISABLED = 107,
    PHONE_NOT_FOUND = 108,
}

@Component({
    selector: 'auth',
    templateUrl: './auth.component.html',
    styleUrls: ['./auth.component.scss'],
    changeDetection: ChangeDetectionStrategy.Default,
    encapsulation: ViewEncapsulation.None,
    host: {
        'class': 'auth'
    },
    animations: [
        trigger('showHidePin', [
            transition(':enter', [
                style({height: 0}),
                animate('0.25s cubic-bezier(0.5, 1, 0.89, 1)', style({height: '*'}))
            ]),
            transition(':leave', [
                style({height: '*'}),
                animate('0.25s cubic-bezier(0.5, 1, 0.89, 1)', style({height: 0}))
            ])
        ]),
        trigger('showHidePhoneClear', [
            transition(':enter', [
                style({transform: 'scale(0.25)', opacity: 0}),
                animate('0.25s cubic-bezier(0.5, 1, 0.89, 1)', style({transform: 'scale(1)', opacity: 1}))
            ]),
            transition(':leave', [
                style({transform: '*', opacity: '*'}),
                animate('0.25s cubic-bezier(0.5, 1, 0.89, 1)', style({transform: 'scale(0.25)', opacity: 0}))
            ])
        ]),
    ]
})
export class AuthComponent implements OnInit, OnDestroy {
    subs: Subscription[] = [];

    isSubmitLoading: boolean = false;

    isFormValid: boolean = false;

    @ViewChild('phoneInput')
    phoneInputElementRef: ElementRef<HTMLInputElement>;

    @ViewChild('pinInput')
    pinInputElementRef: ElementRef<HTMLInputElement>;

    loginForm: {
        phone: string;
        pin: string;
    };

    private readonly _phoneValidationPattern = /^\(\d{3}\) \d{3}-\d{4}$/;
    authForm: FormGroup = new FormGroup({
        phone: new FormControl('',
            [Validators.required, Validators.pattern(this._phoneValidationPattern)]),
        pin: new FormControl('',
            [Validators.required, Validators.minLength(minPinCodeLength), Validators.maxLength(6)])

    });

    activeField: 'phone' | 'pin' = AUTH_FIELDS.PHONE;

    resendPinTimer$: Subscription;

    resendPinTimerTimeout: number;

    isEtcMenuActive: boolean = false;

    readonly minPhoneLength = 6;

    readonly maxPhoneLength = 10;

    readonly pinResendTimeoutInSeconds: number = 60;

    termsSession: TermsSession;

    phonePrefix: string = '1';

    constructor(
        private renderer: Renderer2,
        private router: Router,
        private formBuilder: UntypedFormBuilder,
        private titleService: TitleService,
        private toastService: ToastService,
        private domService: DomService,
        private userService: UserService,
        private termsService: TermsService,
        private messageService: MessageService,
        private debugService: DebugService,
        private zone: NgZone,
    ) {
        window.scroll(0, 0);
        this.titleService.setTitle('auth.page_title');
        this.resetLoginForm();
        this.validateLoginForm();

        this.setTermsState(this.termsService.getTermsSession());
        this.subs.push(this.termsService.onTermsSessionChange.subscribe(session => {
            defer(() => this.setTermsState(session));
        }));
    }

    ngOnInit(): void {
        const authError = this.messageService.extractMessageDataFromURL(window.location.href, 'authError');

        if (authError) {
            this.toastService.create({
                message: [authError.key, authError.data],
                timeout: 8000
            });
        }

        this.registerDebugConsoleCommands();

        this.subs.push(
            this.authForm.get('phone').valueChanges.pipe(
                debounceTime(100),
                distinctUntilChanged()
            ).subscribe(
                () => {
                    if (this.formError.isShow) {
                        this.resetFormError();
                    }
                }
            ));

        this.subs.push(
            this.authForm.get('pin').valueChanges.pipe(
                debounceTime(100),
                distinctUntilChanged()
            ).subscribe(
                () => {
                    if (this.formError.isShow) {
                        this.resetFormError();
                    }
                }
            ));
    }

    // TODO: move to service
    private registerDebugConsoleCommands() {

        this.debugService.registerNewConsoleCommand('autoLogin', (() => {
            let timeout = null;

            const unsetTimeout = () => {
                if (timeout !== null) {
                    clearTimeout(timeout);
                    timeout = null;
                }
            };

            return () => {
                unsetTimeout();
                this.userService.createTestAccount().subscribe(accountData => {
                    timeout = setTimeout(() => {
                        this.authForm.get('phone').setValue(accountData.phone);
                        this.authForm.updateValueAndValidity();

                        this.onSubmit();

                        const checkIsActivePin = () => {
                            const phoneWithPrefix = '1' + accountData.phone;
                            const isActiveFormControlPin = this.activeField === AUTH_FIELDS.PIN_CODE;

                            if (isActiveFormControlPin) {
                                this.userService.getTestAccountPin(phoneWithPrefix).subscribe((pin: string) => {
                                    this.authForm.get('pin').setValue(pin);
                                    this.authForm.updateValueAndValidity();
                                    this.zone.run(
                                        () => this.onSubmit()
                                    );
                                    unsetTimeout();
                                    console.warn(`Test account: ${accountData.phone} / ${pin}`);
                                });
                            } else {
                                timeout = setTimeout(() => checkIsActivePin(), 1000);
                            }
                        };

                        unsetTimeout();
                        checkIsActivePin();
                    }, 50);
                });
            }
        })(), {help: 'Create test POSTPAID account'});


        Object.keys(TEST_ACCOUNT_CREATE_PHONES).forEach((key: string) => {
            const phone = TEST_ACCOUNT_CREATE_PHONES[key];

            this.debugService.registerNewConsoleCommand(`autoLogin${key}`, async () => {
                const authData: AuthData = await this.userService.createTestFleetAccount(phone).toPromise().catch(() => null);

                if (await this.userService.applyToken(authData.token)) {
                    await this.zone.run(() => {
                        const redirectURL = '/dashboard';
                        return this.router.navigateByUrl(redirectURL);
                    });
                }
            }, {help: `Create test ${key} account`});

            this.debugService.registerNewConsoleCommand(`autoLogin${key}OTF`, async () => {
                const authData: AuthData = await this.userService.createTestFleetAccountWithOTFSubscription(phone).toPromise().catch(() => null);

                if (await this.userService.applyToken(authData.token)) {
                    await this.zone.run(() => {
                        const redirectURL = '/dashboard';
                        return this.router.navigateByUrl(redirectURL);
                    });
                }
            }, {help: `Create test ${key} account`});
        });


    }

    ngOnDestroy(): void {
        this.subs.forEach(sub => sub.unsubscribe());
    }

    setTermsState(termsSession: TermsSession) {
        this.termsSession = termsSession;
    }

    private resetLoginForm() {
        this.authForm.reset();
    }


    // TODO: replace to Angular form validation
    validateLoginForm() {
        if (this.activeField === AUTH_FIELDS.PHONE) {
            this.isFormValid = this.authForm.get('phone').valid;
        } else if (this.activeField === AUTH_FIELDS.PIN_CODE) {
            this.isFormValid = this.authForm.get('pin').valid;
        }
        return this.isFormValid;
    }

    isPhoneValid() {
        return this.authForm.get('phone').valid;
    }

    isPinValid() {
        return this.authForm.get('pin').valid;
    }

    isAllFormValid() {
        if (this.activeField === AUTH_FIELDS.PHONE) {
            return this.isPhoneValid();
        }
        if (this.activeField === AUTH_FIELDS.PIN_CODE) {
            return this.isPinValid();
        }
        return false;
    }

    onInputKeyUp(e: KeyboardEvent): void {
        if (e.key.toLowerCase() === 'enter') {
            this.onSubmit();
        }
    }

    public onSubmit(): void {
        if (this.isSubmitLoading || !this.isAllFormValid()) {
            return;
        }

        switch (this.activeField) {
            case AUTH_FIELDS.PHONE:
                this.onSubmitPhone();
                break;
            case AUTH_FIELDS.PIN_CODE:
                this.onSubmitPin();
                break;
            default:
                console.warn('Unknown field:', this.activeField);
                break;
        }
    }


    private onSubmitPhone(): void {
        this.startSubmitLoader('phone');

        this.submitPhoneStepToApi().then(isPhoneNumberSubmitted => {
            if (isPhoneNumberSubmitted) {
                this.runResendPinTimer();
                defer(() => {
                    this.activeField = AUTH_FIELDS.PIN_CODE;
                    this.validateLoginForm();
                });
            } else {
                this.toastService.create({
                    message: ['auth.phone_error'],
                    timeout: 5000
                });
            }

            this.endSubmitLoading('phone');
        });
    }

    private startSubmitLoader(control: 'phone' | 'pin'): void {
        this.isSubmitLoading = true;
        if (control === 'phone') {
            this.disableControl('phone');
        }
        if (control === 'pin') {
            this.disableFullForm();
        }
    }

    // phone: "PT-AG-307004"
    // pin: "1440"
    // PT-AG-641400, pin: 4213
    onSubmitPin(): void {
        this.startSubmitLoader('pin');
        const phone = this.getClearPhoneValue(this.authForm.get('phone').value);
        const pin = (this.authForm.get('pin').value).trim();

        this.login(phone, pin);
    }

    private login(phone: string, pin: string) {
        this.userService.login({phone, pin}).then(({isOk, errorCode}) => {
            if (isOk) {
                this.router.navigateByUrl('/dashboard/invoices');
            } else {
                this.showErrorMessage(errorCode);
                this.endSubmitLoading('pin');
            }
        });
    }

    private showErrorMessage(errorCode: TnpResponseStatusCode) {

        const errorsTranslatesKeysMap = {
            [TnpResponseStatusCode.AUTHENTICATION_ERROR]: 'auth.pin_error_100',
            [TnpResponseStatusCode.PIN_DEACTIVATED]: 'auth.pin_error_102',
            [TnpResponseStatusCode.REQUEST_THROTTLED]: 'auth.error_104',
            [TnpResponseStatusCode.ACCOUNT_LOCKED]: 'auth.error_105',
            [TnpResponseStatusCode.MOBILE_APP_LOGIN_DISABLED]: 'auth.error_107',
            [TnpResponseStatusCode.PHONE_NOT_FOUND]: 'auth.error_108',
            "default": 'auth.pin_error'
        }
        const messageTranslateKey = errorsTranslatesKeysMap[errorCode] || errorsTranslatesKeysMap["default"];
        this.setFormError(messageTranslateKey);
    }

    private endSubmitLoading(control: 'phone' | 'pin') {
        if (control === 'pin') {
            this.enableControl('pin');
        }
        this.isSubmitLoading = false;
    }

    onPinShown(e: any): void {
        if (e.fromState === 'void' && this.pinInputElementRef) {
            this.setFormFocusOnPin();
        }
    }

    public resendNewPin(): void {
        if (this.isSubmitLoading || this.activeField !== AUTH_FIELDS.PIN_CODE) {
            return;
        }

        this.authForm.get('pin').reset();
        this.authForm.get('pin').updateValueAndValidity();
        this.runResendPinTimer();
        this.setFormFocusOnPin();

        this.submitPhoneStepToApi().then(isOk => {

            if (isOk) {
                this.toastService.create({
                    message: ['auth.pin_resend_ok'],
                    timeout: 5000
                });
            } else {
                this.toastService.create({
                    message: ['auth.pin_error'],
                    timeout: 5000
                });
            }
        });
    }

    onClearPhone(): void {
        this.resetLoginForm();
        this.authForm.updateValueAndValidity();
        this.activeField = AUTH_FIELDS.PHONE;
        this.enableControl('phone');
        this.setFormFocusOnPhone();
    }

    public isActiveControl(controlName: 'phone' | 'pin'): boolean {
        return this.activeField === controlName;
    }

    public disableControl(controlName: 'phone' | 'pin'): void {
        this.authForm.get(controlName)?.disable();
    }

    public enableControl(controlName: 'phone' | 'pin'): void {
        this.authForm.get(controlName)?.enable();
    }

    public disableFullForm(): void {
        this.authForm.disable();
    }

    private runResendPinTimer(): void {
        this.clearResendTimer();

        const pinResendTimeoutSeconds = this.pinResendTimeoutInSeconds;
        this.resendPinTimer$ = this.createResendPinTimer(pinResendTimeoutSeconds).subscribe(
            (remainingSeconds: number) => this.updateResendPinTimer(remainingSeconds)
        );
    }

    private createResendPinTimer(duration: number) {
        return timer(0, 1000).pipe(
            take(duration + 1),
            map(elapsedSeconds => duration - elapsedSeconds)
        );
    }

    private updateResendPinTimer(remainingSeconds: number): void {
        this.resendPinTimerTimeout = remainingSeconds;
        if (remainingSeconds === 0) {
            this.clearResendTimer();
        }
    }

    private clearResendTimer(): void {
        if (this.resendPinTimer$) {
            this.resendPinTimer$.unsubscribe();
        }
        this.resendPinTimerTimeout = 0;
    }

    private setFormFocusOnPhone() {
        if (this.phoneInputElementRef) {
            defer(() => this.phoneInputElementRef.nativeElement.focus());
        }
    }

    private setFormFocusOnPin() {
        if (this.pinInputElementRef) {
            defer(() => this.pinInputElementRef.nativeElement.focus());
        }
    }

    private submitPhoneStepToApi(): Promise<boolean> {
        const phone = this.getClearPhoneValue(this.authForm.get('phone').value);
        this.disableControl('phone');

        return firstValueFrom(this.userService.sendPhone(phone)) as Promise<boolean>;
    }

    // -----------------------------
    formError: {
        isShow: boolean;
        messageTranslateKey: string;
    } = {
        isShow: false,
        messageTranslateKey: ''
    };

    private getOnlyNumbersFromPhoneValue(phoneValue: string): string {
        return phoneValue.replace(/\D/g, '');
    }

    onEtcItemClick(e: any) {
        this.domService.markEvent(e, 'etcItemClick');
    }

    onEtcMenuClick(e: any) {
        this.domService.markEvent(e, 'etcMenuClick');
    }

    onEtcTriggerClick(e: any) {
        this.domService.markEvent(e, 'etcTriggerClick');
    }

    @HostListener('document:click', ['$event'])
    onDocClick(e: any) {
        if (this.domService.isHasEventMark(e, 'etcTriggerClick')) {
            this.isEtcMenuActive = !this.isEtcMenuActive;
        } else if (!this.domService.isHasEventMark(e, 'etcMenuClick') || this.domService.isHasEventMark(e, 'etcItemClick')) {
            this.isEtcMenuActive = false;
        }
    }

    private getClearPhoneValue(value: string): string {
        return this.phonePrefix + this.getOnlyNumbersFromPhoneValue(value);
    }

    setFormError(messageTranslateKey: string) {
        this.formError.isShow = true;
        this.formError.messageTranslateKey = messageTranslateKey;
    }

    resetFormError() {
        this.formError.isShow = false;
        this.formError.messageTranslateKey = '';
    }
}

