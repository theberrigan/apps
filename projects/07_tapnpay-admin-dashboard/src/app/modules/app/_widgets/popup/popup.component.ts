import {
    Component, EventEmitter, HostListener, Input, OnDestroy, OnInit, Output, Renderer2,
    ViewEncapsulation
} from '@angular/core';
import {Subscription} from 'rxjs';
import {DeviceService, ViewportBreakpoint} from '../../../../services/device.service';
import {uniqueId} from '../../../../lib/utils';
import {DomService} from '../../../../services/dom.service';

@Component({
    selector: 'popup-custom',
    exportAs: 'popup',
    templateUrl: './popup.component.html',
    styleUrls: [ './popup.component.scss' ],
    encapsulation: ViewEncapsulation.None,
    host: {
        'class': 'popup'
    }
})
export class PopupComponent implements OnInit, OnDestroy {
    viewportBreakpoint : ViewportBreakpoint;

    subs : Subscription[] = [];

    id : string;

    noScrollClass : string;

    styleEl : HTMLStyleElement;

    @Input()
    isDisabled : boolean = false;

    @Output()
    onClose = new EventEmitter();

    constructor (
        private renderer : Renderer2,
        private deviceService : DeviceService,
        private domService : DomService,
    ) {
        this.viewportBreakpoint = this.deviceService.viewportBreakpoint;
        this.subs.push(this.deviceService.onResize.subscribe((message) => {
            if (message.breakpointChange) {
                this.viewportBreakpoint = message.breakpointChange.current;
            }
        }));
    }

    ngOnInit () {
        this.id = uniqueId();
        this.injectStyle();
        this.hidePageScroll();
    }

    ngOnDestroy () {
        this.showPageScroll();
        this.removeStyle();
        this.subs.forEach(sub => sub.unsubscribe());
    }

    hidePageScroll () {
        this.renderer.addClass(document.body, this.noScrollClass);
        // this.renderer.addClass(document.documentElement, this.noScrollClass);  // don't because page scrolls to top
    }

    showPageScroll () {
        this.renderer.removeClass(document.body, this.noScrollClass);
        // this.renderer.removeClass(document.documentElement, this.noScrollClass);
    }

    injectStyle () {
        this.noScrollClass = `no-scroll_${ this.id }`;

        const style = this.styleEl = this.renderer.createElement('style');
        const styleText = this.renderer.createText(`.${ this.noScrollClass } { overflow: hidden !important; }`);
        this.renderer.appendChild(style, styleText);
        this.renderer.appendChild(document.head, style);
    }

    removeStyle () {
        if (this.styleEl) {
            this.renderer.removeChild(document.head, this.styleEl);
        }
    }

    @HostListener('click', [ '$event' ])
    onClick (e : MouseEvent) {
        if (this.domService.hasEventMark(e, 'popupCloseClick')) {
            this.onClose.emit();
        }
    }
}
