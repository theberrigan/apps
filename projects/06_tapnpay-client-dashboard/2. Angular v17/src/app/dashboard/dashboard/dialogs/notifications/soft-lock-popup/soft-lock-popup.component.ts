import {Component, EventEmitter, Output} from '@angular/core';

@Component({
    selector: 'app-soft-lock-popup',
    templateUrl: './soft-lock-popup.component.html',
    styleUrls: ['./soft-lock-popup.component.css']
})
export class SoftLockPopupComponent {
    @Output() confirm = new EventEmitter<boolean>();

    emmitConfirm() {
        this.confirm.emit(true);
    }
}
