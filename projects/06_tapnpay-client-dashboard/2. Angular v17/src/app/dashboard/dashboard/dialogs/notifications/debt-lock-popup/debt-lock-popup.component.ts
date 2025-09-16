import {Component, EventEmitter, Output} from '@angular/core';

@Component({
    selector: 'app-debt-lock-popup',
    templateUrl: './debt-lock-popup.component.html',
    styleUrls: ['./debt-lock-popup.component.css']
})
export class DebtLockPopupComponent {
    @Output() confirm = new EventEmitter<boolean>();

    emmitConfirm() {
        this.confirm.emit(true);
    }
}
