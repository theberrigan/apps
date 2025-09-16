import {ChangeDetectionStrategy, Component, OnInit, Renderer2} from '@angular/core';
import {NavigationEnd, Router} from '@angular/router';
import {forIn} from 'lodash';
import {DeviceService} from '../../services/device.service';

@Component({
    selector: 'app-root',
    templateUrl: './app.component.html',
    changeDetection: ChangeDetectionStrategy.Default
})
export class AppComponent implements OnInit {
    public appScreen : HTMLElement = null;

    constructor (
        private renderer : Renderer2,
        private router : Router,
        private deviceService : DeviceService
    ) {
        // When very first route loaded, hide app screen
        const routerSub = router.events.subscribe(e => {
            if (e instanceof NavigationEnd) {
                routerSub.unsubscribe();
                this.hideAppScreen();
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

    public removeAppScreen () : void {
        if (this.appScreen) {
            this.renderer.removeChild(this.appScreen.parentNode, this.appScreen);
            this.appScreen = null;
        }
    }

    public hideAppScreen () : void {
        this.appScreen = document.querySelector('.app-screen');
        this.renderer.listen(this.appScreen, 'transitionend', () => this.removeAppScreen());
        setTimeout(() => this.removeAppScreen(), 180);  // fuse
        this.renderer.addClass(this.appScreen, 'app-screen_fade-out');
    }
}
