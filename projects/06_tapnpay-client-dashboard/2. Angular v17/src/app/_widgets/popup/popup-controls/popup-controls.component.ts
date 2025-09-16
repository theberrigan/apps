import {
    Component, HostBinding, Input, ViewEncapsulation
} from '@angular/core';

@Component({
    selector: 'popup-controls',
    exportAs: 'popupControls',
    templateUrl: './popup-controls.component.html',
    styleUrls: ['./popup-controls.component.scss'],
    encapsulation: ViewEncapsulation.None,
    host: {
        'class': 'popup__controls'
    }
})
export class PopupControlsComponent {
    @Input()
    @HostBinding('class.popup__controls_stretch')
    isStretched: boolean = false;

    @Input()
    @HostBinding('class.popup__controls_column')
    isColumn: boolean = false;


    constructor() {

    }


}
