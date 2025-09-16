import {
    Component, ElementRef,
    OnDestroy,
    OnInit,
    ViewEncapsulation
} from '@angular/core';
import {ReplaySubject} from 'rxjs';

@Component({
    selector: 'popup-header',
    exportAs: 'popup-header',
    templateUrl: './popup-header.component.html',
    styleUrls: [ './popup-header.component.scss' ],
    encapsulation: ViewEncapsulation.None,
    host: {
        'class': 'popup__header'
    }
})
export class PopupHeaderComponent implements OnInit, OnDestroy {
    public onClose = new ReplaySubject<void>();

    constructor (
        public el : ElementRef
    ) {}

    public ngOnInit () : void {

    }

    public ngOnDestroy () : void {

    }

    public onCloseButtonClick () : void {
        this.onClose.next();
    }
}
