import {
    Component, OnDestroy, OnInit, Renderer2,
    ViewEncapsulation
} from '@angular/core';
import {DeviceService} from '../../../services/device.service';

@Component({
    selector: 'popup-content',
    exportAs: 'popupContent',
    templateUrl: './popup-content.component.html',
    styleUrls: [ './popup-content.component.scss' ],
    encapsulation: ViewEncapsulation.None,
    host: {
        'class': 'popup__content'
    }
})
export class PopupContentComponent implements OnInit, OnDestroy {
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
