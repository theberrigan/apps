import {
    ChangeDetectionStrategy,
    Component, EventEmitter, Input,
    OnDestroy,
    OnInit, Output,
    ViewEncapsulation
} from '@angular/core';
import {Subscription} from 'rxjs';
import {AccountService, AccountSummary} from '../../../../../../services/account.service';
import {ToastService} from '../../../../../../services/toast.service';
import {UserService} from '../../../../../../services/user.service';

export interface ActionsTabDataUpdateEvent {
    summaryData : AccountSummary;
    lastPIN : string;
}

@Component({
    selector: 'account-editor-actions',
    templateUrl: './account-editor-actions.component.html',
    styleUrls: [ './account-editor-actions.component.scss' ],
    changeDetection: ChangeDetectionStrategy.Default,
    encapsulation: ViewEncapsulation.None,
    host: {
        'class': 'account-editor-actions',
    }
})
export class AccountEditorActionsComponent implements OnInit, OnDestroy {
    subs : Subscription[] = [];

    @Input()
    accountId : string;

    summaryData : AccountSummary;

    isDataSet : boolean = false;

    @Input()
    set data (data : ActionsTabDataUpdateEvent) {
        if (!this.isDataSet) {
            this.summaryData = data.summaryData;
            this.lastPIN = data.lastPIN;
            this.isDataSet = true;
        }
    }

    @Output()
    dataChange = new EventEmitter<ActionsTabDataUpdateEvent>();

    isReinstatePopupVisible : boolean = false;

    isReinstating : boolean = false;

    canSendPIN : boolean = false;

    canSendSMS : boolean = false;

    canCloseAccount : boolean = false;

    lastPIN : string = null;

    isSMSPopupVisible : boolean = false;

    isSendingSMS : boolean = false;

    smsText : string = '';

    isSMSTextValid : boolean = false;

    isPINPopupVisible : boolean = false;

    isSendingPIN : boolean = false;

    isCloseAccountPopupVisible : boolean = false;

    isClosingAccount : boolean = false;

    isBlockAccountPopupVisible : boolean = false;

    isBlockingAccount : boolean = false;

    reinstateReason : string = '';

    isReinstateReasonValid : boolean = false;

    constructor (
        private accountService : AccountService,
        private toastService : ToastService,
        private userService : UserService,
    ) {
        this.canSendPIN = this.userService.checkPermission('ACCOUNT_ACTIONS_SEND_PIN');
        this.canSendSMS = this.userService.checkPermission('ACCOUNT_ACTIONS_SEND_SMS');
        this.canCloseAccount = this.userService.checkPermission('ACCOUNT_CLOSE');
    }

    ngOnInit () {
        console.log(this.summaryData);
    }

    ngOnDestroy () : void {
        this.subs.forEach(sub => sub.unsubscribe());
    }

    canReinstateAccount () : boolean {
        return this.isAccountLocked();
    }

    isFleetAccount () : boolean {
        return true;
    }

    isAccountLocked () : boolean {
        return [ 'SOFT_LOCK', 'HARD_LOCK', 'SUSPICIOUS_ACTIVITY' ].includes(this.summaryData.account_status);
    }

    isCloseAccountVisible () : boolean {
        const isClosed = [ 'PERMANENTLY_CLOSED', 'CLOSED_BY_OWNER' ].includes(this.summaryData.account_status);
        return this.canCloseAccount && !isClosed;
    }

    hasActions () : boolean {
        return (this.isAccountLocked() || this.canSendPIN || this.canSendSMS || this.canCloseAccount);
    }

    onReinstateAccount () {
        if (!this.canReinstateAccount() || this.isReinstatePopupVisible) {
            return;
        }

        this.isReinstatePopupVisible = true;
    }

    isReinstateReasonRequired () : boolean {
        // this.summaryData.outstanding_disputes_amount = 1;
        return (
            this.isAccountLocked() &&
            this.isFleetAccount() &&
            this.summaryData.account_status === 'SUSPICIOUS_ACTIVITY' &&
            this.summaryData.outstanding_disputes_amount > 0
        );
    }

    async onConfirmReinstate (isOk : boolean) {
        if (this.isReinstating || isOk && !this.canSubmitReinstate()) {
            return;
        }

        if (!isOk) {
            this.isReinstatePopupVisible = false;
            return;
        }

        this.isReinstating = true;

        const reason = this.isReinstateReasonRequired() ? (this.reinstateReason || '').trim() : '';
        const isReinstated = await this.accountService.reinstateAccount(this.accountId, reason).toPromise().catch(() => false);

        if (isReinstated) {
            this.summaryData = await this.accountService.fetchSummary(this.accountId).toPromise().catch(() => null);
            this.notifyDataUpdate();
        }

        this.isReinstatePopupVisible = false;
        this.isReinstating = false;

        this.toastService.create({
            message: [ isReinstated ? 'accounts.actions.reinstate_success' : 'accounts.actions.reinstate_failed' ],
            timeout: 5000
        });
    }

    onSendSMS () {
        if (!this.canSendSMS) {
            return;
        }

        this.isSMSPopupVisible = true;
    }

    onChangeSMSText () {
        this.isSMSTextValid = (this.smsText || '').trim().length >= 3;
    }

    async onConfirmSendSMS (send : boolean) {
        if (this.isSendingSMS) {
            return;
        }

        if (!send) {
            this.hideSMSPopup();
            return;
        }

        this.isSendingSMS = true;

        const text = (this.smsText || '').trim();
        const isSent = await this.accountService.sendSMS(this.accountId, text).toPromise().catch(() => false);

        if (isSent) {
            this.hideSMSPopup();
        }

        this.isSendingSMS = false;

        this.toastService.create({
            message: [ isSent ? 'accounts.actions.send_sms_success' : 'accounts.actions.send_sms_failed' ],
            timeout: 5000
        });
    }

    hideSMSPopup () {
        this.isSMSPopupVisible = false;
        this.smsText = '';
        this.isSMSTextValid = false;
    }

    onConfirmIdentity () {
        if (!this.canSendPIN) {
            return;
        }

        this.isPINPopupVisible = true;
    }

    async onConfirmSendPIN (send : boolean) {
        if (this.isSendingPIN) {
            return;
        }

        if (!send) {
            this.isPINPopupVisible = false;
            return;
        }

        this.isSendingPIN = true;

        this.lastPIN = await this.accountService.sendPIN(this.accountId).toPromise().catch(() => null);
        // this.lastPIN = '1234';

        this.isPINPopupVisible = false;
        this.isSendingPIN = false;

        this.notifyDataUpdate();

        this.toastService.create({
            message: [ !!this.lastPIN ? 'accounts.actions.confirm_identity_success' : 'accounts.actions.confirm_identity_failed' ],
            timeout: 5000
        });
    }

    notifyDataUpdate () {
        this.dataChange.emit({
            lastPIN: this.lastPIN,
            summaryData: this.summaryData
        });
    }

    onCloseAccount () {
        if (!this.canCloseAccount) {
            return;
        }

        this.isCloseAccountPopupVisible = true;
    }

    async onConfirmCloseAccount (isConfirmed : boolean) {
        if (this.isClosingAccount) {
            return;
        }

        if (!isConfirmed) {
            this.isCloseAccountPopupVisible = false;
            return;
        }

        this.isClosingAccount = true;

        const isClosed = await this.accountService.closeAccount(this.accountId).toPromise().catch(() => false);

        if (isClosed) {
            this.summaryData = await this.accountService.fetchSummary(this.accountId).toPromise().catch(() => null);
            this.notifyDataUpdate();
        }

        this.isCloseAccountPopupVisible = false;
        this.isClosingAccount = false;

        this.toastService.create({
            message: [ isClosed ? 'accounts.actions.close_account_success' : 'accounts.actions.close_account_failed' ],
            timeout: 5000
        });
    }

    onBlockAccount () {
        if (this.isAccountLocked() || !this.isFleetAccount()) {
            return;
        }

        this.isBlockAccountPopupVisible = true;
    }

    async onConfirmBlockAccount (isConfirmed : boolean) {
        if (this.isBlockingAccount) {
            return;
        }

        if (!isConfirmed) {
            this.isBlockAccountPopupVisible = false;
            return;
        }

        this.isBlockingAccount = true;

        const isBlocked = await this.accountService.blockAccount(this.accountId).toPromise().catch(() => false);

        if (isBlocked) {
            this.summaryData = await this.accountService.fetchSummary(this.accountId).toPromise().catch(() => null);
            this.notifyDataUpdate();
        }

        this.isBlockAccountPopupVisible = false;
        this.isBlockingAccount = false;

        this.toastService.create({
            message: [ isBlocked ? 'accounts.actions.block_account_success' : 'accounts.actions.block_account_failed' ],
            timeout: 5000
        });
    }

    onChangeReinstateReason () {
        this.isReinstateReasonValid = (this.reinstateReason || '').trim().length >= 3;
    }

    canSubmitReinstate () : boolean {
        return !this.isReinstateReasonRequired() || this.isReinstateReasonValid;
    }
}
