import {AfterViewInit, Directive, ElementRef, Input, NgZone, Renderer2} from '@angular/core';
import SimpleBar from 'simplebar';

@Directive({
    selector: '[scrollbar]'
})
export class ScrollbarDirective implements AfterViewInit {
    public simplebar : SimpleBar = null;

    public _apply : boolean = true;

    public isViewReady : boolean = false;

    @Input()
    public set scrollbar (apply : boolean) {
        // console.warn('apply', apply);
        (this._apply = apply !== false) ? this.mount() : this.unmount();
    }

    public get scrollbar () : boolean {
        return this._apply;
    }

    constructor (
        private el : ElementRef,
        private zone : NgZone,
    ) {}

    public mount () : void {
        if (!this.isViewReady || !this._apply || this.simplebar) {
            return;
        }

        this.zone.runOutsideAngular(() => {
            this.simplebar = new SimpleBar(this.el.nativeElement, {
                autoHide: false,
                classNames: {
                    content: 'scrollbar__content',
                    scrollContent: 'scrollbar__scroll-content',
                    scrollbar: 'scrollbar__handle',
                    track: 'scrollbar__track'
                }
            });
        });
    }

    public unmount () : void {
        if (this.simplebar) {
            // console.warn('unmount');
            this.simplebar.unMount();
            this.simplebar = null;
        }
    }

    public ngAfterViewInit () : void {
        // console.warn('ngAfterViewInit');
        this.isViewReady = true;
        this.mount();
    }
}
