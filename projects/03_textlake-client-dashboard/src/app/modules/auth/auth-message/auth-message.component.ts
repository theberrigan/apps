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
export class AuthMessageComponent {
    @Input()
    public type : 'error' | 'info' = 'error';

    @Output()
    public onClose = new EventEmitter<void>();

    public close () : void {
        this.onClose.emit();
    }
}
