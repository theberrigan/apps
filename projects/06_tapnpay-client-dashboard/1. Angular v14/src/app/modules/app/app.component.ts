import {ChangeDetectionStrategy, Component, HostListener, OnInit, Renderer2, ViewEncapsulation} from '@angular/core';
import {forIn} from 'lodash-es';
import {NavigationEnd, Router} from '@angular/router';
import {DeviceService, ViewportBreakpoint} from '../../services/device.service';
import {TitleService} from '../../services/title.service';
import {StorageService} from '../../services/storage.service';

@Component({
    selector: 'app-root',
    templateUrl: './app.component.html',
    styleUrls: [ './app.component.scss' ],
    changeDetection: ChangeDetectionStrategy.Default,
    encapsulation: ViewEncapsulation.None,
    host: {
        class: 'app'
    }
})
export class AppComponent implements OnInit {
    public viewportBreakpoint : ViewportBreakpoint;

    constructor (
        private renderer : Renderer2,
        private router : Router,
        private deviceService : DeviceService,
        private titleService : TitleService,
    ) {
        this.titleService.setRawTitle('tapNpay', false);

        // When very first route loaded, hide app screen
        const routerSub = router.events.subscribe(e => {
            if (e instanceof NavigationEnd) {
                routerSub.unsubscribe();
                this.hideAppScreen();
            }
        });

        this.viewportBreakpoint = this.deviceService.viewportBreakpoint;
        this.deviceService.onResize.subscribe((message) => {
            if (message.breakpointChange) {
                this.viewportBreakpoint = message.breakpointChange.current;
            }
        });
    }

    public ngOnInit () {
        this.setDeviceClasses();
        this.setViewportObserver();
    }

    public setDeviceClasses () : void {
        const params = {
            browser: this.deviceService.browser,
            os:      this.deviceService.os,
            device:  this.deviceService.device,
        };

        forIn(params, (paramSection : any, paramSectionKey : string) => {
            forIn(paramSection, (paramValue : any, paramKey : string) => {
                if (paramValue === true) {
                    this.renderer.addClass(document.documentElement, `${ paramSectionKey }_${ paramKey }`);
                }
            });
        });

        document.documentElement.dataset.browserVersion = this.deviceService.browser.version;
    }

    public setViewportObserver () : void {
        this.renderer.addClass(document.documentElement, `viewport_${ this.deviceService.viewportBreakpoint }`);

        this.deviceService.onResize.subscribe(message => {
            if (message.breakpointChange) {
                const { last, current } = message.breakpointChange;

                this.renderer.removeClass(document.documentElement, `viewport_${ last }`);
                this.renderer.addClass(document.documentElement, `viewport_${ current }`);
            }
        });
    }

    public hideAppScreen () : void {
        const appScreen = document.querySelector('.app-screen');
        this.renderer.listen(appScreen, 'transitionend', () => this.renderer.removeChild(appScreen.parentNode, appScreen));
        this.renderer.addClass(appScreen, 'app-screen_fade-out');
    }

    /*
    __testStripe () {
        const apiKey = 'xxx';

        new Promise((resolve) => {
            if ('Stripe' in window) {
                resolve((<any>window).Stripe);
                return;
            }

            const script : any = document.createElement('script');
            script.addEventListener('load', () => resolve((<any>window).Stripe));
            script.src = 'https://js.stripe.com/v3/';
            document.head.appendChild(script);
        }).then((Stripe : any) => {
            const stripe = Stripe(apiKey);

            fetch("http://localhost:15016/create-checkout-session", {
                method: "POST",
            }).then(function (response) {
                return response.json();
            }).then(function (session) {
                return stripe.redirectToCheckout({
                    sessionId: session.id
                });
            }).then(function (result) {
                // If redirectToCheckout fails due to a browser or network
                // error, you should display the localized error message to your
                // customer using error.message.
                if (result.error) {
                    alert(result.error.message);
                }
            }).catch(function (error) {
                console.error("Error:", error);
            });

        });
    }
     */
}
