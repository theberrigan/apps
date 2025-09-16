import {
    AfterContentInit, AfterViewInit, ApplicationRef, ChangeDetectorRef,
    Component, ContentChild,
    ElementRef, EventEmitter,
    HostBinding,
    Input,
    OnDestroy,
    OnInit, Output,
    Renderer2, ViewChild,
    ViewEncapsulation
} from '@angular/core';
import {PopupOptions, PopupService} from '../../services/popup.service';
import {DomService} from '../../services/dom.service';
import {merge} from 'lodash';
import {defer, getType, isEmpty} from '../../lib/utils';
import {PopupHeaderComponent} from './popup-header.component';
import {PopupControlsComponent} from './popup-controls.component';
import {PopupBoxComponent} from './popup-box.component';
import {DeviceService, ViewportBreakpoint} from '../../services/device.service';
import {Subscription} from 'rxjs';

// TODO: setCustomState({ showSpinner: <boolean>, showBox: <boolean | 'transparent'> })



/*

[fixHeader] : boolean = false              - fix header
[fixControls] : boolean = false            - fix controls
[isActive] : boolean = false               - true == automatically activate popup right after it has been inject into DOM
[closeBy] : 'cross-overlay' | 'cross' | 'overlay' | 'manual' = 'cross-overlay';
[showCross] : boolean = true;
[canBeClosed] : boolean = true;
[isDisabled] : boolean = false // canBeClosed + disable all controls // wrap popup with fieldset[disabled] && disable cross
[stickyHeader] : boolean = false;
[stickyControls] : boolean = false;

(onCloseRequest)
(onBeforeDeactivate)
(onAfterDeactivate)
(onBeforeActivate)
(onAfterActivate)

TODO: z-index
TODO: в app component отправлять hideBodyScroll, showBodyScroll, а компонент должен ++ -- кол-во этих вызовов

Если нужно

*/


@Component({
    selector: 'popup-custom',
    templateUrl: './popup.component.html',
    styleUrls: [ './popup.component.scss' ],
    encapsulation: ViewEncapsulation.None,
    host: {
        'class': 'popup',
        '[class.popup_has-cross]': 'options.showCross',
        '[class.popup_closable]': 'options.canBeClosed',
        '[class.popup_active]': 'isActive',
        '[class.popup_fix-header]': 'isHeaderFixed',
        // '[class.popup_fix-controls]': 'isControlsFixed',
        '[class.popup_show-box]': `visibleElement === 'box'`,
        '[class.popup_show-spinner]': `visibleElement === 'spinner'`,
        '[class.popup_box-transparent]': 'isBoxTransparent'
    }
})
export class PopupComponent implements OnInit, OnDestroy, AfterContentInit, AfterViewInit {
    @Output()
    public onActivate = new EventEmitter<void>();

    @Output()
    public onDeactivate = new EventEmitter<void>();

    @Output()
    public onShow = new EventEmitter<void>();

    @Output()
    public onHide = new EventEmitter<void>();

    @Output()
    public onCloseRequest = new EventEmitter<boolean>();

    @ContentChild(PopupBoxComponent)
    public popupBox : PopupBoxComponent;

    @ContentChild(PopupHeaderComponent)
    public popupHeader : PopupHeaderComponent;

    @ContentChild(PopupControlsComponent)
    @HostBinding('class.popup_has-controls')
    public popupControls : PopupControlsComponent;

    @ViewChild('scrollEl')
    public scrollEl : ElementRef;

    public _options : PopupOptions = new PopupOptions();

    @Input()
    public set options (options : PopupOptions) {
        this._options = merge({}, new PopupOptions(), options);
    }

    public get options () : PopupOptions {
        return this._options;
    }

    public redrawCb : any = () => {};

    public domListeners : any[] = [];

    public isActive : boolean = false;

    public isHeaderFixed : boolean = false;

    @HostBinding('class.popup_fix-controls')
    public isControlsFixed : boolean = false;

    public visibleElement : 'box' | 'spinner' = 'box';

    public isBoxTransparent : boolean = false;

    public subs : Subscription[] = [];

    constructor (
        private renderer : Renderer2,
        private domService : DomService,
        private popupService : PopupService,
        private appRef : ApplicationRef,
        private deviceService : DeviceService,
    ) {

    }

    public ngOnInit () : void {
        if (this.options.isActive) {
            this.activate();
        }
    }

    public ngOnDestroy () : void {
        this.subs.forEach(sub => sub.unsubscribe());
        this.domListeners.forEach(unlistenCb => unlistenCb());
        this.deactivate();
    }

    public ngAfterViewInit () : void {
        this.initRedraw();

        if (this.popupHeader) {
            this.popupHeader.onClose.subscribe(() => this.requestClose());
        }
    }

    public ngAfterContentInit () : void {

    }

    public addSub (sub : Subscription) : void {
        this.subs = [ ...this.subs, sub ];
    }

    public initRedraw () : void {
        const scrollEl = this.scrollEl && this.scrollEl.nativeElement;
        const boxEl = this.popupBox && this.popupBox.el && this.popupBox.el.nativeElement;
        const headerEl = this.popupHeader && this.popupHeader.el && this.popupHeader.el.nativeElement;
        const controlsEl = this.popupControls && this.popupControls.el && this.popupControls.el.nativeElement;

        const fixHeader = !!(this.options.stickyHeader && headerEl);
        const fixControls = !!(this.options.stickyControls && controlsEl);

        if (!fixHeader && !fixControls || !scrollEl || !boxEl) {
            return;
        }

        const calcWidth = (boxRect? : ClientRect) => {
            if (!this.isActive || this.visibleElement !== 'box') {
                return;
            }

            const boxWidth = (boxRect || boxEl.getBoundingClientRect()).width + 'px';

            fixHeader && this.renderer.setStyle(headerEl, 'width', this.isHeaderFixed ? boxWidth : '');
            fixControls && this.renderer.setStyle(controlsEl, 'width', this.isControlsFixed ? boxWidth : '');
        };

        const redraw = this.redrawCb = () => {
            if (!this.isActive || this.visibleElement !== 'box') {
                return;
            }

            const boxRect : ClientRect = boxEl.getBoundingClientRect();
            const scrollRect : ClientRect = scrollEl.getBoundingClientRect();
            const headerRect : ClientRect = fixHeader && headerEl.getBoundingClientRect();
            const controlsRect : ClientRect = fixControls && controlsEl.getBoundingClientRect();

            if (fixHeader) {
                const isFixed = this.isHeaderFixed = boxRect.top <= 0;
                this.renderer.setStyle(boxEl, 'padding-top', isFixed ? (headerRect.height + 'px') : '');
            }

            if (fixControls) {
                const isFixed = this.isControlsFixed = boxRect.bottom >= scrollRect.height;
                // console.log('isFixed', isFixed);
                this.renderer.setStyle(boxEl, 'padding-bottom', isFixed ? (controlsRect.height + 'px') : '');
            }

            calcWidth(boxRect);

            this.appRef.tick();
        };

        if (this.popupBox && this.popupBox.sizeIframe) {
            this.domListeners.push(this.renderer.listen(this.popupBox.sizeIframe.nativeElement.contentWindow, 'resize', () => redraw()));
        }

        this.domListeners = [
            ...this.domListeners,
            this.renderer.listen(scrollEl, 'scroll', () => redraw()),
            this.renderer.listen(window, 'resize', () => redraw())
        ];
    }

    public redraw () : void {
        this.redrawCb && this.redrawCb();
    }

    public activate () : Promise<void> {
        return new Promise((resolve) => {
            this.popupService.activatePopup(this).then(() => {
                this.onActivate.emit();
                resolve();
            });
        });
    }

    public deactivate () : Promise<void> {
        return new Promise((resolve) => {
            this.popupService.deactivatePopup(this).then(() => {
                this.onDeactivate.emit();
                resolve();
            });
        });
    }

    public showBox (isTransparent : boolean = false) : void {
        this.visibleElement = 'box';
        this.isBoxTransparent = isTransparent;
        requestAnimationFrame(() => this.redraw());
    }

    public showSpinner () : void {
        this.visibleElement = 'spinner';
        requestAnimationFrame(() => this.redraw());
    }

    // Функции ниже используются только системой попапов
    // -------------------------------------------------

    // ! show()/hide() не нужно использовать в большинстве случаев !
    public show () : Promise<void> {
        return new Promise((resolve) => {
            defer(() => {
                this.isActive = true;
                requestAnimationFrame(() => this.redrawCb());
                this.onShow.emit();
                resolve();
            });
        });
    }

    public hide () : Promise<void> {
        return new Promise((resolve) => {
            defer(() => {
                this.isActive = false;
                this.onHide.emit();
                resolve();
            });
        });
        // defer(() => {
        //     this.isActive = false;
        //     this.onHide.emit();
        // });
    }

    public onScrollAreaClick (e : any) : void {
        if (!this.domService.hasEventMark(e, 'popupBoxClick')) {
            this.requestClose(true);
        }
    }

    public requestClose (byOverlay? : boolean) : void {
        if (!this.options.canBeClosed) {
            return;
        }

        const closeBy = this.options.closeBy;

        if (closeBy === 'manual') {
            this.onCloseRequest.emit(byOverlay);
        } else if (!byOverlay || byOverlay && (closeBy === 'overlay' || closeBy === 'cross-overlay')) {
            this.deactivate();
        }
    }
}
