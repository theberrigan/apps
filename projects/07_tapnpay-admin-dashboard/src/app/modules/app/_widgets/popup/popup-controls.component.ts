import {
    Component, HostBinding, Input, OnDestroy, OnInit, Renderer2,
    ViewEncapsulation
} from '@angular/core';
import {DeviceService} from '../../../../services/device.service';

@Component({
    selector: 'popup-controls',
    exportAs: 'popupControls',
    templateUrl: './popup-controls.component.html',
    styleUrls: [ './popup-controls.component.scss' ],
    encapsulation: ViewEncapsulation.None,
    host: {
        'class': 'popup__controls'
    }
})
export class PopupControlsComponent implements OnInit, OnDestroy {
    @Input()
    @HostBinding('class.popup__controls_stretch')
    isStretched : boolean = false;

    constructor (
        private renderer : Renderer2,
        private deviceService : DeviceService,
    ) {

    }

    ngOnInit () {

    }

    ngOnDestroy () {

    }
}
