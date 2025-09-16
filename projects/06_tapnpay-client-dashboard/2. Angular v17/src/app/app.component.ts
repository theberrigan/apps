import {ChangeDetectionStrategy, Component, OnDestroy, OnInit, Renderer2, ViewEncapsulation} from '@angular/core';
import {forIn} from 'lodash-es';
import {NavigationEnd, Router} from '@angular/router';
import {DeviceService, ViewportBreakpoint} from './services/device.service';
import {TitleService} from './services/title.service';
import {Subscription} from "rxjs";

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
export class AppComponent implements OnInit, OnDestroy {
    public viewportBreakpoint : ViewportBreakpoint;
    private resizeSubscription: Subscription;


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

    public setDeviceClasses(): void {
        const params = {
            browser: this.deviceService.browser,
            os:      this.deviceService.os,
            device:  this.deviceService.device,
        };

        Object.entries(params).forEach(([paramSectionKey, paramSection]) => {
            Object.entries(paramSection as Record<string, boolean>).forEach(([paramKey, paramValue]) => {
                if (paramValue === true) {
                    this.renderer.addClass(document.documentElement, `${paramSectionKey}_${paramKey}`);
                }
            });
        });

        this.renderer.setAttribute(document.documentElement, 'data-browser-version', this.deviceService.browser.version);
    }


    /**
     * Sets up an observer to handle viewport changes.
     * Adds and removes CSS classes based on the current viewport breakpoint.
     */
    public setViewportObserver(): void {
        this.renderer.addClass(document.documentElement, `viewport_${this.deviceService.viewportBreakpoint}`);

        this.resizeSubscription = this.deviceService.onResize.subscribe({
            next: (message) => {
                if (message.breakpointChange) {
                    const { last, current } = message.breakpointChange;

                    this.renderer.removeClass(document.documentElement, `viewport_${last}`);
                    this.renderer.addClass(document.documentElement, `viewport_${current}`);
                }
            },
            error: (err) => {
                // Handle any errors here
                console.error('Error handling viewport changes:', err);
            }
        });
    }

    ngOnDestroy(): void {
        if (this.resizeSubscription) {
            this.resizeSubscription.unsubscribe();
        }
    }


    public hideAppScreen(): void {
        const appScreenSelector = '.app-screen';
        const fadeOutClass = 'app-screen_fade-out';

        const appScreen = document.querySelector(appScreenSelector);

        if (appScreen) {
            const removeListener = this.renderer.listen(appScreen, 'transitionend', () => {
                this.renderer.removeChild(appScreen.parentNode, appScreen);
                removeListener(); // Clean up the listener
            });

            this.renderer.addClass(appScreen, fadeOutClass);
        } else {
            console.warn(`Element with selector "${appScreenSelector}" not found.`);
        }
    }

    /*
    __testStripe () {
        const apiKey = 'pk_test_TYooMQauvdEDq54NiTphI7jx';

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
