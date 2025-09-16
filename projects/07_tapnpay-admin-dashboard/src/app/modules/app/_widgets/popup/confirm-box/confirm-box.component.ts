import {Component, Input, ViewEncapsulation} from '@angular/core';
import { Observable, Subject } from 'rxjs';
import { take } from 'rxjs/operators';

export interface ConfirmPopupButtons {
    ok : string;
    cancel : string;
}

@Component({
    selector: 'confirm-box',
    exportAs: 'confirmBox',
    templateUrl: './confirm-box.component.html',
    styleUrls: [ './confirm-box.component.scss' ],
    encapsulation: ViewEncapsulation.None,
    host: {
        'class': 'confirm-box'
    }
})
export class ConfirmBoxComponent {
    responseSubject : Subject<boolean>;

    isPopupVisible : boolean = false;

    @Input()
    buttons : ConfirmPopupButtons = {
        'ok': 'confirm_box.ok',
        'cancel': 'confirm_box.cancel',
    }

    constructor () {}

    confirm () : Observable<boolean> {
        this.isPopupVisible = true;
        this.responseSubject = new Subject<boolean>();

        return this.responseSubject.asObservable().pipe(take(1));
    }

    onSubmit (isOk : boolean) {
        this.isPopupVisible = false;
        this.responseSubject.next(isOk);
    }
}
