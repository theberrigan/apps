import {
    Component,
    OnDestroy,
    OnInit,
    ViewEncapsulation
} from '@angular/core';

@Component({
    selector: 'popup-content',
    exportAs: 'popup-content',
    templateUrl: './popup-content.component.html',
    styleUrls: [ './popup-content.component.scss' ],
    encapsulation: ViewEncapsulation.None,
    host: {
        'class': 'popup__content'
    }
})
export class PopupContentComponent implements OnInit, OnDestroy {
    constructor () {}

    public ngOnInit () : void {

    }

    public ngOnDestroy () : void {

    }
}
