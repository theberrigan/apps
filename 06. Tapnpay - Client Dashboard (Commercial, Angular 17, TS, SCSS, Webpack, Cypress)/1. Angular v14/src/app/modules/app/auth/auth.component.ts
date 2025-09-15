import {
    ChangeDetectionStrategy,
    Component,
    ElementRef, HostListener, NgZone, OnDestroy,
    OnInit,
    Renderer2,
    ViewChild,
    ViewEncapsulation
} from '@angular/core';
import {Router} from '@angular/router';
import {TitleService} from '../../../services/title.service';
import {defer} from '../../../lib/utils';
import {FormBuilder, FormGroup} from '@angular/forms';
import {ToastService} from '../../../services/toast.service';
import {animate, state, style, transition, trigger} from '@angular/animations';
import {Subscription, timer} from 'rxjs';
import {take} from 'rxjs/operators';
import {ILang} from '../../../services/lang.service';
import {DomService} from '../../../services/dom.service';
import {DEV_PHONE_FASTRAK, DEV_PHONE_SUNPASS, UserService} from '../../../services/user.service';
import {CONFIG} from '../../../../../config/app/dev';
import {TermsService, TermsSession} from '../../../services/terms.service';
import {MessageService} from '../../../services/message.service';
import {DebugService} from '../../../services/debug.service';

@Component({
    selector: 'auth',
    templateUrl: './auth.component.html',
    styleUrls: [ './auth.component.scss' ],
    changeDetection: ChangeDetectionStrategy.Default,
    encapsulation: ViewEncapsulation.None,
    host: {
        'class': 'auth'
    },
    animations: [
        trigger('showHidePin', [
            transition(':enter', [
                style({ height: 0 }),
                animate('0.25s cubic-bezier(0.5, 1, 0.89, 1)', style({ height: '*' }))
            ]),
            transition(':leave', [
                style({ height: '*' }),
                animate('0.25s cubic-bezier(0.5, 1, 0.89, 1)', style({ height: 0 }))
            ])
        ]),
        trigger('showHidePhoneClear', [
            transition(':enter', [
                style({ transform: 'scale(0.25)', opacity: 0 }),
                animate('0.25s cubic-bezier(0.5, 1, 0.89, 1)', style({ transform: 'scale(1)', opacity: 1 }))
            ]),
            transition(':leave', [
                style({ transform: '*', opacity: '*' }),
                animate('0.25s cubic-bezier(0.5, 1, 0.89, 1)', style({ transform: 'scale(0.25)', opacity: 0 }))
            ])
        ]),
    ]
})
export class AuthComponent implements OnInit, OnDestroy {
    subs : Subscription[] = [];

    isSubmitting : boolean = false;

    isFormValid : boolean = false;

    @ViewChild('phoneInput')
    phoneInput : ElementRef;

    @ViewChild('pinInput')
    pinInput : ElementRef;

    form : {
        phone : string;
        pin : string;
    };

    activeField : 'phone' | 'pin' = 'phone';

    resendTimer : Subscription;

    resendTimerTimeout : number;

    isEtcMenuActive : boolean = false;

    readonly minPhoneLength = 6;

    readonly maxPhoneLength = 10;

    readonly resendTimeout = 60;

    termsSession : TermsSession;

    phonePrefix = '1';

    constructor (
        private renderer : Renderer2,
        private router : Router,
        private formBuilder : FormBuilder,
        private titleService : TitleService,
        private toastService : ToastService,
        private domService : DomService,
        private userService : UserService,
        private termsService : TermsService,
        private messageService : MessageService,
        private debugService : DebugService,
        private zone : NgZone,
    ) {
        window.scroll(0, 0);
        this.titleService.setTitle('auth.page_title');
        this.resetForm();
        this.validate();

        this.setTermsState(this.termsService.getTermsSession());
        this.subs.push(this.termsService.onTermsSessionChange.subscribe(session => {
            defer(() => this.setTermsState(session));
        }));
    }

    ngOnInit () : void {
        const authError = this.messageService.extractMessageDataFromURL(window.location.href, 'authError');

        if (authError) {
            this.toastService.create({
                message: [ authError.key, authError.data ],
                timeout: 8000
            });
        }

        this.debugService.register('autoLogin', (() => {
            let timeout = null;

            const unsetTimeout = () => {
                if (timeout !== null) {
                    clearTimeout(timeout);
                    timeout = null;
                }
            };

            return () => {
                unsetTimeout();
                this.userService.createTestAccount().subscribe(acc => {
                    timeout = setTimeout(() => {
                        this.form.phone = acc.phone;
                        this.onSubmit();

                        const checkPinFiledActive = () => {
                            if (this.activeField === 'pin') {
                                this.userService.getTestAccountPin('1' + acc.phone).subscribe((pin: string) => {
                                    this.form.pin = pin;
                                    this.zone.run(() => this.onSubmit());
                                    unsetTimeout();
                                    console.warn(`Test account: ${ acc.phone } / ${ pin }`);
                                });
                            } else {
                                timeout = setTimeout(() => checkPinFiledActive(), 1000);
                            }
                        };

                        unsetTimeout();
                        checkPinFiledActive();
                    }, 50);
                });
            }
        })(), { help: 'Create test POSTPAID account' });

        this.debugService.register('autoLoginSunpass', async () => {
            const authData = await this.userService.createTestFleetAccount(DEV_PHONE_SUNPASS).toPromise().catch(() => null);

            if (await this.userService.applyToken(authData.token)) {
                this.zone.run(() => this.router.navigateByUrl('/dashboard'));
            }
        }, { help: 'Create test Sunpass (PREPAID/FLEET) account' });

        this.debugService.register('autoLoginFastrak', async () => {
            const authData = await this.userService.createTestFleetAccount(DEV_PHONE_FASTRAK).toPromise().catch(() => null);

            if (await this.userService.applyToken(authData.token)) {
                this.zone.run(() => this.router.navigateByUrl('/dashboard'));
            }
        }, { help: 'Create test FasTrak (PREPAID/FLEET) account' });
    }

    ngOnDestroy () : void {
        this.subs.forEach(sub => sub.unsubscribe());
    }

    setTermsState (termsSession : TermsSession) {
        this.termsSession = termsSession;
    }

    resetForm () {
        this.form = {
            phone: '',
            pin: ''
        };
    }

    validate () {
        if (this.activeField === 'phone') {
            this.isFormValid = (this.form.phone || '').trim().length >= this.minPhoneLength;
        } else if (this.activeField === 'pin') {
            this.isFormValid = (this.form.pin || '').trim().length >= 4;
        }

        return this.isFormValid;
    }

    onInputKeyUp (e : KeyboardEvent) : void {
        if (e.key.toLowerCase() === 'enter') {
            this.onSubmit();
        }
    }

    onSubmit () : void {
        if (this.isSubmitting || !this.validate()) {
            return;
        }

        if (this.activeField === 'phone') {
            this.onSubmitPhone();
        } else if (this.activeField === 'pin') {
            this.onSubmitPin();
        }
    }

    onSubmitPhone () : void {
        this.isSubmitting = true;

        this.submitPhone().then(isOk => {
            if (isOk) {
                this.runResendTimer();
                defer(() => {
                    this.activeField = 'pin';
                    this.validate();
                });
            } else {
                this.toastService.create({
                    message: [ 'auth.phone_error' ],
                    timeout: 5000
                });
            }

            this.isSubmitting = false;
        });
    }

    // phone: "PT-AG-307004"
    // pin: "1440"
    // PT-AG-641400, pin: 4213
    onSubmitPin () : void {
        this.isSubmitting = true;
        const phone = this.phonePrefix + (this.form.phone || '').trim();
        const pin = (this.form.pin || '').trim();

        this.userService.login({ phone, pin }).then(({ isOk, errorCode }) => {
            if (isOk) {
                this.router.navigateByUrl('/dashboard');
            } else {
                switch (errorCode) {
                    case 105:
                        this.toastService.create({
                            message: [ `auth.error_${ errorCode }` ],
                            timeout: 9000
                        });
                        break;
                    default:
                        this.toastService.create({
                            message: [ 'auth.pin_error' ],
                            timeout: 9000
                        });
                }

                this.isSubmitting = false;
            }
        });
    }

    onPinShown (e : any) : void {
        if (e.fromState === 'void' && this.pinInput) {
            this.focusOnPin();
        }
    }

    onResend () : void {
        if (this.isSubmitting || this.activeField !== 'pin') {
            return;
        }

        this.runResendTimer();
        this.focusOnPin();

        this.submitPhone().then(isOk => {
            if (!isOk) {
                this.toastService.create({
                    message: [ 'auth.pin_error' ],
                    timeout: 5000
                });
            }
        });
    }

    onClearPhone () : void {
        this.resetForm();
        this.validate();
        this.activeField = 'phone';
        this.focusOnPhone();
    }

    clearResendTimer () : void {
        if (this.resendTimer) {
            this.resendTimer.unsubscribe();
            this.resendTimer = null;
        }
    }

    runResendTimer () : void {
        this.clearResendTimer();

        const timeoutSeconds = this.resendTimeout;

        // 0 - emit first value without delay
        // 1000 - emit consequent values every second
        this.resendTimer = timer(0, 1000).pipe(
            take(timeoutSeconds + 1)  // +1 because first value is emitted immediately
        ).subscribe(elapsedSeconds => {
            this.resendTimerTimeout = timeoutSeconds - elapsedSeconds;

            if (elapsedSeconds === timeoutSeconds) {
                this.clearResendTimer();
            }
        });
    }

    focusOnPhone () {
        if (this.phoneInput) {
            defer(() => this.phoneInput.nativeElement.focus());
        }
    }

    focusOnPin () {
        if (this.pinInput) {
            defer(() => this.pinInput.nativeElement.focus());
        }
    }

    submitPhone () : Promise<boolean> {
        const phone = this.phonePrefix + (this.form.phone || '').trim();

        return this.userService.sendPhone(phone).toPromise().catch(() => false);
    }

    // -----------------------------

    onEtcItemClick (e : any) {
        this.domService.markEvent(e, 'etcItemClick');
    }

    onEtcMenuClick (e : any) {
        this.domService.markEvent(e, 'etcMenuClick');
    }

    onEtcTriggerClick (e : any) {
        this.domService.markEvent(e, 'etcTriggerClick');
    }

    @HostListener('document:click', [ '$event' ])
    onDocClick (e : any) {
        if (this.domService.hasEventMark(e, 'etcTriggerClick')) {
            this.isEtcMenuActive = !this.isEtcMenuActive;
        } else if (!this.domService.hasEventMark(e, 'etcMenuClick') || this.domService.hasEventMark(e, 'etcItemClick')) {
            this.isEtcMenuActive = false;
        }
    }
}

