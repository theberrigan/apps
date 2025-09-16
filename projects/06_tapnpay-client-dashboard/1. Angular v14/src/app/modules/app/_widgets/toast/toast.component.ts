import {Component, EventEmitter, HostBinding, Input, OnDestroy, OnInit, Output, ViewEncapsulation} from '@angular/core';
import {Toast, ToastType} from '../../../../services/toast.service';
import {animate, keyframes, state, style, transition, trigger} from '@angular/animations';
import {LangService} from '../../../../services/lang.service';


@Component({
    selector: 'toast',
    templateUrl: './toast.component.html',
    styleUrls: [ './toast.component.scss' ],
    encapsulation: ViewEncapsulation.None,
    host: {
        class: 'toast',
        '[class.toast_type_default]': `type === 'default'`,
        '[class.toast_type_error]': `type === 'error'`,
        '[class.toast_type_success]': `type === 'success'`,
        '[@animation]': 'true'
    },
    animations: [
        // trigger('animation', [
        //     state('show', style({ height: '*', opacity: 1, transform: 'translateX(0)'})),
        //     transition('* => show', [
        //         animate('450ms ease-out', keyframes([
        //             style({ height: '0px', opacity: 0, transform: 'translateX(20px)', offset: 0   }),
        //             style({ height: '*',   opacity: 0, transform: 'translateX(20px)', offset: 0.5 }),
        //             style({ height: '*',   opacity: 1, transform: 'translateY(0)',    offset: 1   })
        //         ]))
        //     ]),
        //     state('hide', style({ height: '0px', opacity: 0, transform: 'translateX(20px)' })),
        //     transition('show => hide', [
        //         animate('350ms ease-out', keyframes([
        //             style({ height: '*',   opacity: 1, transform: 'translateY(0)',    offset: 0   }),
        //             style({ height: '*',   opacity: 0, transform: 'translateX(20px)', offset: 0.5 }),
        //             style({ height: '0px', opacity: 0, transform: 'translateX(20px)', offset: 1   })
        //         ]))
        //     ]),
        // ])
        trigger('animation', [
            transition('void => *', [
                animate('250ms ease-out', keyframes([
                    style({ height: '0px', opacity: 0, transform: 'translateY(-10px)', offset: 0   }),
                    style({ height: '*',   opacity: 1, transform: 'translateY(0)', offset: 1 }),
                ]))
            ]),
            transition('* => void', [
                animate('350ms ease-out', keyframes([
                    style({ height: '*',   opacity: 1, offset: 0   }),
                    style({ height: '0px', opacity: 0, offset: 1   })
                ]))
            ]),
        ])
    ]
})
export class ToastComponent implements OnInit, OnDestroy {
    public message : string;

    public timeout : number;

    public type : ToastType;

    @Input()
    public toast : Toast;

    @Output()
    public onHide : EventEmitter<void> = new EventEmitter<void>();

    constructor (
        public langService : LangService
    ) {

    }

    public ngOnInit () : void {
        const toast = this.toast;

        if (Array.isArray(toast.message)) {
            const [ messageKey, messageValues = null ] = <any[]>toast.message;
            this.message = this.langService.translate(messageKey, messageValues).trim();
        } else {
            this.message = (toast.message || '').trim();
        }

        this.type = toast.type || 'default';

        this.timeout = Math.max(2500, toast.timeout || (this.message.length * 50));

        if (this.message.length > 0) {
            setTimeout(() => this.onHide.emit(), this.timeout);
        } else {
            this.onHide.emit();
        }
    }

    public ngOnDestroy () : void {

    }
}
