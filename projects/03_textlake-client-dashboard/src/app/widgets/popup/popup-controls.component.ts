import {
    Component, ElementRef,
    OnDestroy,
    OnInit,
    ViewEncapsulation
} from '@angular/core';

@Component({
    selector: 'popup-controls',
    exportAs: 'popup-controls',
    templateUrl: './popup-controls.component.html',
    styleUrls: [ './popup-controls.component.scss' ],
    encapsulation: ViewEncapsulation.None,
    host: {
        'class': 'popup__controls'
    }
})
export class PopupControlsComponent implements OnInit, OnDestroy {
    constructor (
        public el : ElementRef
    ) {}

    public ngOnInit () : void {

    }

    public ngOnDestroy () : void {

    }
}
