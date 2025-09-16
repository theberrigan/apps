import {Component, Input, Output, EventEmitter} from '@angular/core';

@Component({
    selector: 'app-account-notification-popup',
    templateUrl: './account-notification-popup.component.html',
    styleUrls: ['./account-notification-popup.components.scss']
})
export class AccountNotificationPopupComponent {
    @Input() isStretched: boolean = true;
    @Input() modalType: 'account-debt-lock' | 'account-soft-lock' | 'account_subscription_invoice_expired';
    @Output() confirm = new EventEmitter<void>();

    config: { messageKey: string, buttonLabelKey: string } = null;

    accountBlockModalsConfig = {
        'account-debt-lock': {
            messageKey: 'debt_lock.welcome_message',
            buttonLabelKey: 'debt_lock.pay_debt_button',
        },
        'account-soft-lock': {
            messageKey: 'dashboard.account_soft_lock.message',
            buttonLabelKey: 'dashboard.account_soft_lock.btn',
        },
        'account_subscription_invoice_expired': {
            messageKey: 'dashboard.user_subscription_invoice_expired.message',
            buttonLabelKey: 'dashboard.user_subscription_invoice_expired.btn',
        }
    };


    constructor() {

    }

    ngOnInit() {
        this.config = this.accountBlockModalsConfig[this.modalType];
    }


    onConfirm() {
        this.confirm.emit();
    }


}
