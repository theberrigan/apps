import { Injectable } from '@angular/core';
import {fromEvent, Observable, ReplaySubject, Subject} from 'rxjs';
import { debounceTime} from 'rxjs/operators';

interface ScreenResolution {
    x : number;
    y : number;
}

export type ViewportBreakpoint = 'desktop' | 'tablet' | 'mobile';

@Injectable({
    providedIn: 'root'
})
export class DeviceService {
    public readonly browser : any;
    public readonly os : any;
    public readonly device : any;
    public readonly isShadowDomSupported : boolean;

    public readonly onResize : Observable<any>;

    public readonly onActionPanelStateChange = new ReplaySubject<any>();
    // public readonly onSidebarStateChange = new ReplaySubject<any>();

    public viewportBreakpoint : ViewportBreakpoint = null;

    constructor () {
        // Features support
        // ---------------------
        this.isShadowDomSupported = !!Element.prototype.attachShadow;

        // Screen resize
        // ---------------------
        this.onResize = (() => {
            const emitter : Subject<any> = new Subject<any>();

            const update = () => {
                const viewportWidth = this.viewportFullSize.x;
                const viewportBreakpoint = viewportWidth < 768 ? 'mobile' : viewportWidth >= 992 ? 'desktop' : 'tablet';
                const message : any = {};

                if (viewportBreakpoint !== this.viewportBreakpoint) {
                    message.breakpointChange = {
                        last: this.viewportBreakpoint,
                        current: viewportBreakpoint
                    };

                    this.viewportBreakpoint = viewportBreakpoint;
                }

                emitter.next(message);
            };

            fromEvent(window, 'resize')
                .pipe(debounceTime(100))
                .subscribe(() => update());

            update();

            return emitter.asObservable();
        })();

        // Browser, OS & device
        // ---------------------
        [
            this.browser,
            this.os,
            this.device
        ] = (() => {
            const browser : any = {};
            const os : any = {};
            const device : any = {};

            browser.agent = window.navigator.userAgent;

            const ua : string = browser.agent.toLowerCase();

            // Version
            browser.version = (ua.match(/.+(?:me|ox|on|rv|it|era|opr|ie|edge)[\/: ]([\d.]+)/) || [ null, '0' ])[1];

            browser.opera = /opera/i.test(ua) || /opr/i.test(ua);
            browser.vivaldi = /vivaldi/i.test(ua);
            browser.amigo = /amigo.*mrchrome soc/i.test(ua);

            // MS browsers
            browser.IE = !browser.opera && /(msie|trident\/)/i.test(ua);

            browser.IE6 = browser.IE && /msie 6/i.test(ua);
            browser.IE7 = browser.IE && /msie 7/i.test(ua);
            browser.IE8 = browser.IE && /msie 8/i.test(ua);
            browser.IE9 = browser.IE && /msie 9/i.test(ua);
            browser.IE10 = browser.IE && /10\.\d+/.test(browser.version);
            browser.IE11 = browser.IE && /11\.\d+/.test(browser.version);
            browser.badIE = browser.IE6 || browser.IE7 || browser.IE8 || browser.IE9;  // Unsupported IEs

            browser.edge = !browser.IE && /edge/i.test(ua);

            // Evergreen browsers
            browser.firefox = /firefox/i.test(ua);
            browser.chrome = !browser.edge && /chrome/i.test(ua);
            browser.safari = !browser.chrome && /webkit|safari|khtml/i.test(ua);

            // Others
            browser.bot = /(yandex|google|stackrambler|aport|slurp|msnbot|bingbot|twitterbot|ia_archiver|facebookexternalhit)/i.test(ua);
            browser.smartTV = /smart-?tv/i.test(ua);

            // Is bad browser
            // TODO: add other bad browsers
            browser.bad = browser.badIE;

            // OS
            // -----------------
            os.ios = /iphone|ipod|ipad/i.test(ua);
            os.mac = !os.ios && /mac/i.test(ua);
            os.android = /android/i.test(ua);
            os.windowsMobile = /iemobile/i.test(ua);
            os.windows = !os.windowsMobile && /windows nt/i.test(ua);
            os.windowsXp = /windows nt 5\.\d/i.test(ua);
            os.windowsVista = /windows nt 6\.0/i.test(ua);
            os.windows7 = /windows nt 6\.1/i.test(ua);

            // DEVICE
            // ------------------

            // Device class
            device.mobile = os.ios || os.android || os.windowsMobile || /opera (mobi|mini)/i.test(ua);
            device.desktop = !device.mobile;

            // Device type
            device.iphone = /iphone/i.test(ua);
            device.ipod = /ipod/i.test(ua);
            device.ipad = /ipad/i.test(ua);

            // Is touch device
            device.touch = (() => {
                const touchQuery = [ '(', '),(-webkit-', '),(-moz-', '),(-o-', '),(-ms-', ')' ].join('touch-enabled');

                return (
                    ('ontouchstart' in window) ||
                    (<any>window).DocumentTouch && document instanceof (<any>window).DocumentTouch ||
                    'matchMedia' in window && (<any>window).matchMedia(touchQuery).matches
                );
            })();

            return [ browser, os, device ];
        })();
    }

    /**
     * Viewport size with scrollbars (aka CSS-viewport used in @media-queries)
     * See: https://stackoverflow.com/questions/1248081/get-the-browser-viewport-dimensions-with-javascript
     */
    public get viewportFullSize () : ScreenResolution {
        return {
            x: window.innerWidth || 0,
            y: window.innerHeight || 0,
        };
    }

    /**
     * Viewport size without scrollbars
     * See: https://stackoverflow.com/questions/1248081/get-the-browser-viewport-dimensions-with-javascript
     */
    public get viewportClientSize () : ScreenResolution {
        return {
            x: document.documentElement.clientWidth || 0,
            y: document.documentElement.clientHeight || 0
        };
    }

    public get isLandscape () : boolean {
        const viewportSize : ScreenResolution = this.viewportFullSize;
        return viewportSize.x >= viewportSize.y;
    }

    public get pixelRatio () : number {
        return window.devicePixelRatio || 1;
    }

    public hideActionPanel () : void {
        this.onActionPanelStateChange.next(false);
    }

    public showActionPanel () : void {
        this.onActionPanelStateChange.next(true);
    }

    // public hideSidebar () : void {
    //     this.onSidebarStateChange.next(false);
    // }
    //
    // public showSidebar () : void {
    //     this.onSidebarStateChange.next(true);
    // }
}
