import {
    ChangeDetectionStrategy,
    Component,
    ElementRef, EventEmitter,
    Input,
    NgZone,
    OnDestroy,
    OnInit, Output, Renderer2,
    ViewChild,
    ViewEncapsulation
} from '@angular/core';
import {DeviceService} from '../../services/device.service';
import {isEmpty, isObject} from '../../lib/utils';

enum ViewType {
    None = 0,
    ShadowDom = 1,
    Iframe = 2
}

@Component({
    selector: 'isolated-view',
    exportAs: 'isolatedView',
    templateUrl: './isolated-view.component.html',
    styleUrls: [ './isolated-view.component.scss' ],
    encapsulation: ViewEncapsulation.None,
    changeDetection: ChangeDetectionStrategy.OnPush,
    host: {
        class: 'isolated-view',
    }
})
export class IsolatedViewComponent implements OnInit, OnDestroy {
    public _html : string = null;

    @Input()
    public set html (html : string) {
        if (typeof(html) === 'string') {
            this._html = html.trim() || null;
        } else if (isEmpty(html)) {
            this._html = null;
        } else {
            console.error('[isolated-view]: string | null | undefined is expected as \'html\' input property, given:', html);
        }

        this.updateView();
    }

    public get html () : string {
        return this._html;
    }

    public viewType : ViewType = ViewType.None;

    public ViewTypeEnum = ViewType;

    @ViewChild('emailNest')
    public emailNest : ElementRef;

    @ViewChild('widthTestContainer')
    public widthTestContainer : ElementRef;

    public isIframeActive : boolean = false;

    public iframeListeners : any[] = [];

    @Output()
    public onResize : EventEmitter<number> = new EventEmitter<number>();

    constructor (
        public ngZone : NgZone,
        public renderer : Renderer2,
        public deviceService : DeviceService
    ) {

    }

    public ngOnInit () : void {

    }

    public ngOnDestroy () : void {
        this.destroyIframe();
    }

    public destroyIframe () : void {
        if (this.isIframeActive) {
            this.iframeListeners.forEach(unlisten => unlisten());
            this.iframeListeners = [];
            this.isIframeActive = false;
        }
    }

    public updateView () : void {
        if (!this.html) {
            if (this.viewType === ViewType.Iframe) {
                this.destroyIframe();
            }

            this.viewType = ViewType.None;
            return;
        }

        this.viewType = this.deviceService.isShadowDomSupported ? ViewType.ShadowDom : ViewType.Iframe;

        this.widthTestContainer.nativeElement.innerHTML = this.html;

        requestAnimationFrame(() => {

            // --------------------------

            const nestEl = this.emailNest.nativeElement;

            if (this.viewType === ViewType.ShadowDom) {
                this.onResize.emit(this.widthTestContainer.nativeElement.scrollWidth || 0);

                if (!nestEl.shadowRoot) {
                    nestEl.attachShadow({ mode: 'open' });
                }

                nestEl.shadowRoot.innerHTML = this.html;
            } else {
                this.onResize.emit(0);
                const iframeDoc = nestEl.contentWindow.document;

                const rootStyle = [
                    'overflow: visible',
                    'width: 100%',
                    `max-width: ${ nestEl.contentWindow.innerWidth }px`,
                    'margin: 0 auto'
                ].join('; ');

                iframeDoc.body.innerHTML = `
                    <div id="textlake-root" style="${ rootStyle }">
                        <div style="clear: both;"></div>
                        <div id="textlake-content-root"></div>
                        <div style="clear: both;"></div>
                    </div>`;

                // TODO: x-scroll doesn't work
                // TODO: create auto-width for iframe
                iframeDoc.body.style.margin = 0;
                iframeDoc.body.style.overflowY = 'hidden';
                iframeDoc.body.style.overflowX = 'auto';

                iframeDoc.documentElement.style.overflowY = 'hidden';
                iframeDoc.documentElement.style.overflowX = 'auto';

                const rootEl = iframeDoc.querySelector('#textlake-root');
                const contentRootEl = rootEl.querySelector('#textlake-content-root');

                this.ngZone.runOutsideAngular(() => {
                    this.iframeListeners.push(
                        this.renderer.listen(nestEl.contentWindow, 'resize', () => {
                            rootEl.style.maxWidth = `${ nestEl.contentWindow.innerWidth }px`;
                        })
                    );
                });

                this.isIframeActive = true;

                contentRootEl.innerHTML = this.html;

                // If there are tables in html with height expressed in relative units,
                // _every_ resizeIframe() call will increase height of iframe, so fix it.
                // https://stackoverflow.com/q/59930980/3738245
                contentRootEl.querySelectorAll('table').forEach(table => {
                    if (/px$/.test(table.getAttribute('height') || '') === false) {
                        table.removeAttribute('height');
                    }

                    if (/px$/.test(table.style.height || '') === false) {
                        table.style.height = '';
                    }
                });

                const resizeIframe = () => {
                    nestEl.style.height = rootEl.offsetHeight + 'px';
                };

                // Initial resize
                requestAnimationFrame(() => resizeIframe());

                this.ngZone.runOutsideAngular(() => {
                    [ ...iframeDoc.images ].forEach(image => {
                        if (!image.complete) {
                            this.iframeListeners.push(
                                this.renderer.listen(image, 'load', () => resizeIframe()),
                                this.renderer.listen(image, 'error', () => resizeIframe())
                            );
                        }
                    })
                });
            }
        });
    }
}
