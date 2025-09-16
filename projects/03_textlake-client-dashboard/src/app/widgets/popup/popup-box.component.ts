import {
    Component, ElementRef, HostListener, Input,
    OnDestroy,
    OnInit, ViewChild,
    ViewEncapsulation
} from '@angular/core';
import {DomService} from '../../services/dom.service';


@Component({
    selector: 'popup-box',
    exportAs: 'popup-box',
    templateUrl: './popup-box.component.html',
    styleUrls: [ './popup-box.component.scss' ],
    encapsulation: ViewEncapsulation.None,
    host: {
        class: 'popup__box'
    }
})
export class PopupBoxComponent implements OnInit, OnDestroy {
    @ViewChild('sizeIframe')
    public sizeIframe : ElementRef;

    constructor (
        public el : ElementRef,
        private domService : DomService,
    ) {}

    public ngOnInit () : void {

    }

    public ngOnDestroy () : void {

    }

    @HostListener('click', [ '$event' ])
    public onBoxClick (e : any) : void {
        this.domService.markEvent(e, 'popupBoxClick');
    }
}
