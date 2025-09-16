import {ChangeDetectionStrategy, Component, OnDestroy, OnInit, Renderer2, ViewEncapsulation} from '@angular/core';
import {Router} from '@angular/router';
import {TitleService} from '../../../../services/title.service';
import {DeviceService, ViewportBreakpoint} from '../../../../services/device.service';
import {Subscription} from 'rxjs';
import {UserService} from '../../../../services/user.service';
import {ToastService} from '../../../../services/toast.service';

@Component({
    selector: 'profile',
    templateUrl: './profile.component.html',
    styleUrls: [ './profile.component.scss' ],
    changeDetection: ChangeDetectionStrategy.Default,
    encapsulation: ViewEncapsulation.None,
    host: {
        'class': 'profile'
    }
})
export class ProfileComponent implements OnInit, OnDestroy {
    viewportBreakpoint : ViewportBreakpoint;

    subs : Subscription[] = [];

    isDeactivatePopupVisible : boolean = false;

    isDeactivateAccountSubmitting : boolean = false;

    activePopup : 'deactivate-account' | 'deactivate-account-result' | 'payment-method';

    deactivateAccountResultMsgKey : string = null;

    deactivateAccountResultMsgData : any = null;

    isDebtLock : boolean = false;

    constructor (
        private renderer : Renderer2,
        private router : Router,
        private titleService : TitleService,
        private deviceService : DeviceService,
        private userService : UserService,
        private toastService : ToastService,
    ) {
        window.scroll(0, 0);

        this.isDebtLock = this.userService.getUserData().account.accountStatus === 'ACCOUNT_DEBT_LOCK';

        this.viewportBreakpoint = this.deviceService.viewportBreakpoint;
        this.subs.push(this.deviceService.onResize.subscribe((message) => {
            if (message.breakpointChange) {
                this.viewportBreakpoint = message.breakpointChange.current;
            }
        }));
    }

    ngOnInit () {
        this.titleService.setTitle('profile.page_title');
    }

    ngOnDestroy () : void {
        this.subs.forEach(sub => sub.unsubscribe());
    }

    onDeactivateAccount () {
        if (this.isDebtLock) {
            return;
        }

        this.activePopup = 'deactivate-account';
    }

    onCloseDeactivatePopup () {
        this.activePopup = null;
    }

    onConfirmDeactivateAccount () {
        if (this.isDeactivateAccountSubmitting) {
            return;
        }

        this.isDeactivateAccountSubmitting = true;

        this.userService.deactivateAccount().subscribe(
            (isOk : boolean) => this.onDeactivateAccountResponse(isOk),
            (errorCode : number) => this.onDeactivateAccountResponse(false, errorCode),
        );
    }

    onDeactivateAccountResponse (isOk : boolean, errorCode : number = null) {
        this.isDeactivateAccountSubmitting = false;

        if (isOk) {
            this.onCloseDeactivatePopup();
            this.userService.logout();
            this.router.navigateByUrl('/auth');

            this.toastService.create({
                message: [ 'profile.deactivate_account_ok' ],
                timeout: 9000
            });
        } else {
            switch (errorCode) {
                case 204:
                case 217:  // Fleet model
                    this.deactivateAccountResultMsgKey = `profile.deactivate_account_error_${ errorCode }`;
                    this.deactivateAccountResultMsgData = null;
                    break;
                default:
                    this.deactivateAccountResultMsgKey = 'profile.deactivate_account_error';
                    this.deactivateAccountResultMsgData = null;
            }

            this.activePopup = 'deactivate-account-result';
        }
    }

    onShowPaymentMethodPopup () {
        this.activePopup = 'payment-method';
    }

    onClosePaymentMethodPopup () {
        this.activePopup = null;
    }

    onCloseDeactivateResultPopup () {
        this.activePopup = null;
        this.deactivateAccountResultMsgKey = null;
        this.deactivateAccountResultMsgData = null;
    }
}
