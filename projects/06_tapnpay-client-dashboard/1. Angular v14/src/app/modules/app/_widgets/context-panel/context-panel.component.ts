import {
    Component, HostBinding, Input,
    OnDestroy,
    OnInit,
    ViewEncapsulation
} from '@angular/core';
import {animate, animateChild, query, style, transition, trigger} from '@angular/animations';

@Component({
    selector: 'context-panel',
    exportAs: 'contextPanel',
    templateUrl: './context-panel.component.html',
    styleUrls: [ './context-panel.component.scss' ],
    encapsulation: ViewEncapsulation.None,
    host: {
        'class': 'context-panel',
        '[@contextPanelHost]': 'true'
    },
    animations: [
        trigger('contextPanelHost', [
            transition(':enter, :leave', [
                query('@contextPanelBox', animateChild()),
            ]),
        ]),
        trigger('contextPanelBox', [
            transition(':enter', [
                style({ transform: 'translateY(-50%) rotateX(20deg)', opacity: 0 }),
                animate('0.2s cubic-bezier(0.5, 1, 0.89, 1)', style({ transform: '*', opacity: '*' }))
            ]),
            transition(':leave', [
                style({ transform: '*', opacity: '*' }),
                animate('0.15s cubic-bezier(0.5, 1, 0.89, 1)', style({ transform: 'translateY(-50%) rotateX(20deg)', opacity: 0 }))
            ])
        ]),
    ]
})
export class ContextPanelComponent {
    constructor () {}
}
