import {Component, EventEmitter, Input, OnInit, Output, ViewEncapsulation} from '@angular/core';

@Component({
    selector: 'auth-message',
    templateUrl: './auth-message.component.html',
    encapsulation: ViewEncapsulation.None,
    host: {
        'class': 'auth__message',
        '[class.auth__message_error]': `type === 'error'`,
        '[class.auth__message_info]': `type === 'info'`,
    }
})
export class AuthMessageComponent implements OnInit {
    @Input()
    public type : 'error' | 'info' = 'error';

    @Output()
    public onClose = new EventEmitter<void>();

    constructor () {}

    public ngOnInit () : void {

    }

    public close () : void {
        this.onClose.emit();
    }
}
