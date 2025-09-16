import {
    Component,
    ViewEncapsulation
} from '@angular/core';
import {DomService} from '../../../../services/dom.service';

@Component({
    selector: 'popup-header',
    exportAs: 'popupHeader',
    templateUrl: './popup-header.component.html',
    styleUrls: [ './popup-header.component.scss' ],
    encapsulation: ViewEncapsulation.None,
    host: {
        'class': 'popup__header'
    }
})
export class PopupHeaderComponent {
    constructor (
        private domService : DomService,
    ) {}

    onClose (e : MouseEvent) {
        this.domService.markEvent(e, 'popupCloseClick');
    }
}
