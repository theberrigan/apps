import {Component, HostBinding, Renderer2, ViewChild, ViewEncapsulation} from '@angular/core';
import {DeviceService, ViewportBreakpoint} from '../../services/device.service';
import {UserData, UserService} from '../../services/user.service';
import {PopupComponent} from '../../widgets/popup/popup.component';
import {Subscription, timer} from 'rxjs';
import {ActivatedRoute, Router} from '@angular/router';
import {HttpService} from '../../services/http.service';
import {DomService} from '../../services/dom.service';
import {TitleService} from '../../services/title.service';
import {TermsService} from '../../services/terms.service';
import {ToastService} from '../../services/toast.service';
import {defer} from '../../lib/utils';
import {take} from 'rxjs/operators';
import { ProfileComponent } from './settings/profile/profile.component';

@Component({
    selector: 'dashboard',
    exportAs: 'dashboard',
    templateUrl: './dashboard.component.html',
    styleUrls: [ './dashboard.component.scss' ],
    encapsulation: ViewEncapsulation.None,
    host: {
        class: 'dashboard',
    }
})
export class DashboardComponent {
    @ViewChild('nav')
    public nav : any;

    public viewportBreakpoint : ViewportBreakpoint = null;

    public userData : UserData;

    public year : number = 2019;

    @HostBinding('class.dashboard_nav-minimized')
    public isNavMinimized : boolean = false;

    @HostBinding('class.dashboard_nav-active')
    public isNavMobileActive : boolean = false;

    @ViewChild('profile')
    public profile : ProfileComponent;

    @ViewChild('emailVerificationPopup')
    public emailVerificationPopup : PopupComponent;

    public isEmailVerificationPopupVisible : boolean = false;

    public isVerifying : boolean = false;

    public isVerificationCodeValid : boolean = false;

    public verificationCode : string = '';

    public codeResendTimer : Subscription = null;

    public codeResendTimerFormattedValue : string = '0:00';

    public readonly codeResendTimeout : number = 75000;

    constructor (
        private router : Router,
        private route : ActivatedRoute,
        private renderer : Renderer2,
        private http : HttpService,
        private userService : UserService,
        private deviceService : DeviceService,
        private domService : DomService,
        private titleService : TitleService,
        private termsService : TermsService,
        private toastService : ToastService
    ) {
        this.titleService.setTitle('dashboard.page_title');
        this.year = (new Date()).getFullYear();

        this.viewportBreakpoint = this.deviceService.viewportBreakpoint;
        this.deviceService.onResize.subscribe((message) => {
            if (message.breakpointChange) {
                this.viewportBreakpoint = message.breakpointChange.current;
            }
        });

        this.applyUserData(this.userService.getUserData());
        this.userService.onUserDataUpdated.subscribe(userData => this.applyUserData(userData));
    }

    public ngOnInit () {
        this.deviceService.onResize.subscribe(message => {
            if (message.breakpointChange) {
                this.viewportBreakpoint = this.deviceService.viewportBreakpoint;
                this.nav.deactivate();
            }
        });

        const postAuthAction = this.userService.postAuthAction;

        switch (postAuthAction) {
            case 'TERMS':
                this.termsService.showEligibleTerms().subscribe((e) => console.log(e));
                break;
        }

        if (postAuthAction !== 'TERMS') {
            // TODO: refactor terms to do not requesting terms twice
            /*this.termsService.fetchTerms('terms.getEligible').then(terms => {
                if (terms) {
                    this.termsService.showEligibleTerms().subscribe((e) => console.log(e));
                }
            }).catch(() => console.warn('Can`t get eligible terms!'));*/
        }
    }

    public ngOnDestroy () : void {
        // TODO: unsub
    }

    public applyUserData (userData : UserData) : void {
        this.userData = userData;
    }

    public onShowTerms (e : any) : void {
        e.preventDefault();
        this.termsService.showAcceptedTerms();
    }

    public onNavMinimizeChange (isNavMinimized : boolean) {
        defer(() => {
            this.isNavMinimized = isNavMinimized;
        });
    }

    public onNavMobileActiveChange (isNavMobileActive : boolean) {
        defer(() => {
            this.isNavMobileActive = isNavMobileActive;
        });
    }

    public resetEmailVerificationPopup () : void {
        this.clearCodeResendTimer();
        this.isVerifying = false;
        this.isVerificationCodeValid = false;
        this.verificationCode = '';
        this.codeResendTimerFormattedValue = '0:00';
    }

    public showEmailVerificationPopup () : void {
        this.isEmailVerificationPopupVisible = true;
        this.resetEmailVerificationPopup();
        this.sendVerificationCode();
        defer(() => this.emailVerificationPopup.activate());
    }

    public hideEmailVerificationPopup (byOverlay : boolean = false) : void {
        if (byOverlay || this.isVerifying) {
            return;
        }

        this.emailVerificationPopup.deactivate().then(() => {
            this.isEmailVerificationPopupVisible = false;
            this.resetEmailVerificationPopup();
        });
    }

    public onSubmitVerificationCode () : void {
        if (this.isVerifying) {
            return;
        }

        this.isVerifying = true;

        const code = (this.verificationCode || '').trim();

        this.userService.checkVerificationCode(code).subscribe(
            (isOk : boolean) => {
                this.isVerifying = false;

                if (isOk) {
                    this.toastService.create({
                        message: [ 'verification.successfully_verified' ]
                    });

                    this.hideEmailVerificationPopup();

                    const userData = this.userService.getUserData();
                    userData.profile.primaryEmailVerified = true;
                    this.userService.updateUserData({ data: userData }).then(() => {
                        //this.profile.updateVerificationState();
                    });
                } else {
                    this.toastService.create({
                        message: [ 'verification.incorrect_code' ]
                    });
                }
            },
            () => {
                this.isVerifying = false;

                this.toastService.create({
                    message: [ 'verification.cant_verify_code' ]
                });
            }
        );
    }

    public validateVerificationCode () : void {
        defer(() => {
            this.isVerificationCodeValid = (this.verificationCode || '').trim().length >= 4;
        });
    }

    public sendVerificationCode () : void {
        this.runCodeResendTimer();

        this.userService.sendVerificationCode().subscribe(
            (isOk : boolean) => {
                if (!isOk) {
                    this.toastService.create({
                        message: [ 'verification.cant_send_code' ]
                    });

                    this.clearCodeResendTimer();
                }
            },
            () => {
                this.toastService.create({
                    message: [ 'verification.cant_send_code' ]
                });

                this.clearCodeResendTimer();
            }
        );
    }

    public clearCodeResendTimer () : void {
        if (this.codeResendTimer) {
            this.codeResendTimer.unsubscribe();
            this.codeResendTimer = null;
        }
    }

    public runCodeResendTimer () : void {
        this.clearCodeResendTimer();

        const timeoutSeconds = parseInt(<any>(this.codeResendTimeout / 1000), 10);

        // 0 - emit first value without delay
        // 1000 - emit consequent values every second
        this.codeResendTimer = timer(0, 1000).pipe(
            take(timeoutSeconds + 1)  // +1 because first value is emitted immediately
        ).subscribe(elapsedSeconds => {
            const secondsLeft = timeoutSeconds - elapsedSeconds;
            const fmtMinutes = parseInt(<any>(secondsLeft / 60), 10);
            const fmtSeconds = `0${ parseInt(<any>(secondsLeft % 60), 10) }`.slice(-2);
            this.codeResendTimerFormattedValue = `${ fmtMinutes }:${ fmtSeconds }`;

            if (elapsedSeconds === timeoutSeconds) {
                this.clearCodeResendTimer();
            }
        });
    }
}
