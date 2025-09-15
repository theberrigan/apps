import {
    Component, EventEmitter, HostBinding, HostListener, Input, OnDestroy, OnInit, Output, Renderer2,
    ViewEncapsulation
} from '@angular/core';
import { trigger, state, style, transition, animate } from '@angular/animations';
import { Subscription } from 'rxjs';
import { DeviceService, ViewportBreakpoint } from '../../../services/device.service';
import { uniqueId } from '../../../lib/utils';
import { DomService } from '../../../services/dom.service';

@Component({
    selector: 'popup-custom',
    exportAs: 'popup',
    templateUrl: './popup.component.html',
    styleUrls: ['./popup.component.scss'],
    encapsulation: ViewEncapsulation.None,
    animations: [
        trigger('modalAnimation', [
            state('void', style({ opacity: 0, transform: 'scale(0.9)' })),
            state('visible', style({ opacity: 1, transform: 'scale(1)' })),
            transition('void => visible', [
                animate('300ms ease-out')
            ]),
            transition('visible => void', [
                animate('200ms ease-in')
            ]),
        ]),
        trigger('backdropAnimation', [
            state('void', style({ opacity: 0 })),
            state('visible', style({ opacity: 0.5 })),
            transition('void <=> visible', [
                animate('200ms ease-out')
            ])
        ])
    ],
    host: {
        'class': 'popup'
    }
})
export class PopupComponent implements OnInit, OnDestroy {
    viewportBreakpoint: ViewportBreakpoint;
    subs: Subscription[] = [];
    id: string;
    noScrollClass: string;
    styleEl: HTMLStyleElement;

    @Input() isDisabled: boolean = false;
    @Input() @HostBinding('class.popup_size_small') isSmall: boolean = false;

    @Input() isVisible: boolean = false; // Control modal visibility
    @Output() onClose = new EventEmitter();

    constructor(
        private renderer: Renderer2,
        private deviceService: DeviceService,
        private domService: DomService,
    ) {
        this.viewportBreakpoint = this.deviceService.viewportBreakpoint;
        this.subs.push(this.deviceService.onResize.subscribe((message) => {
            if (message.breakpointChange) {
                this.viewportBreakpoint = message.breakpointChange.current;
            }
        }));
    }

    ngOnInit() {
        this.id = uniqueId();
        this.injectStyle();
    }

    ngOnDestroy() {
        this.removeStyle();
        this.subs.forEach(sub => sub.unsubscribe());
    }

    toggleModal() {
        this.isVisible = !this.isVisible;
        if (this.isVisible) {
            this.hidePageScroll();
        } else {
            this.showPageScroll();
        }
    }

    hidePageScroll() {
        this.noScrollClass = `no-scroll_${this.id}`;
        this.renderer.addClass(document.body, this.noScrollClass);
    }

    showPageScroll() {
        this.renderer.removeClass(document.body, this.noScrollClass);
    }

    injectStyle() {
        const style = this.styleEl = this.renderer.createElement('style');
        const styleText = this.renderer.createText(`.${this.noScrollClass} { overflow: hidden !important; }`);
        this.renderer.appendChild(style, styleText);
        this.renderer.appendChild(document.head, style);
    }

    removeStyle() {
        if (this.styleEl) {
            this.renderer.removeChild(document.head, this.styleEl);
        }
    }

    closeModal() {
        this.isVisible = false;
        this.showPageScroll();
        this.onClose.emit();
    }

    @HostListener('click', ['$event'])
    onBackdropClick(e: MouseEvent) {
        if (this.domService.isHasEventMark(e, 'popupCloseClick')) {
            this.closeModal();
        }
    }
}
