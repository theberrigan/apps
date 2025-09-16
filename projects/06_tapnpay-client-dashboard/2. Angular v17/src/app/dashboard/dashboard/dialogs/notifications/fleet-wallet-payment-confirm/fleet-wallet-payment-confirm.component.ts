import {Component, EventEmitter, Input, Output} from '@angular/core';
import {WalletFleetPaymentAttrs} from "../../../dashboard.component";

@Component({
    selector: 'app-fleet-wallet-payment-confirm',
    templateUrl: './fleet-wallet-payment-confirm.component.html',
    styleUrls: ['./fleet-wallet-payment-confirm.component.css']
})
export class FleetWalletPaymentConfirmComponent {
    @Input() isProgress!: boolean;
    @Output() confirm = new EventEmitter<boolean>();
    @Input() walletFleetPaymentAttrs: WalletFleetPaymentAttrs | undefined;

    emmitConfirm() {
        this.confirm.emit(true);
    }

}
