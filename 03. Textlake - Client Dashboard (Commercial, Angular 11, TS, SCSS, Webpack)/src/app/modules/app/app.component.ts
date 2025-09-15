import {Component, OnInit, Renderer2} from '@angular/core';
import {NavigationEnd, Router} from '@angular/router';
import { forIn } from 'lodash';
import {UserService} from '../../services/user.service';
import {DeviceService} from '../../services/device.service';
import {TitleService} from '../../services/title.service';
import {PopupService} from '../../services/popup.service';
import {DomService} from '../../services/dom.service';

@Component({
    selector: 'app-root',
    templateUrl: './app.component.html'
})
export class AppComponent implements OnInit {
    constructor(
        private renderer: Renderer2,
        private router: Router,
        private userService: UserService,
        private deviceService: DeviceService,
        private titleService: TitleService,
        private popupService: PopupService,
        private domService: DomService
    ) {
        this.titleService.setRawTitle('Textlake', false);

        // When very first route loaded, hide app screen
        const routerSub = router.events.subscribe(e => {
            if (e instanceof NavigationEnd) {
                routerSub.unsubscribe();
                this.hideAppScreen();
            }
        });
    }

    public ngOnInit() {
        this.setDeviceClasses();
        this.setViewportObserver();

        this.userService.onForceSignOut.subscribe(() => {
            // use 'location' instead of 'router' to ignore angular router guards
            // this.router.navigateByUrl('/auth/sign-in');
            window.location.href = '/auth/sign-in';
        });

        this.domService.onPageScrollToggle.subscribe((show: boolean) => {
            if (show) {
                this.renderer.removeClass(document.body, 'no-scroll');
            } else {
                this.renderer.addClass(document.body, 'no-scroll');
            }
        });

        this.domService.onDraggingToggle.subscribe((isDragging: boolean) => {
            if (isDragging) {
                this.renderer.addClass(document.body, 'dragging');
            } else {
                this.renderer.removeClass(document.body, 'dragging');
            }
        });
    }

    public hideAppScreen(): void {
        const appScreen = document.querySelector('.app-screen');
        this.renderer.listen(appScreen, 'transitionend', () => this.renderer.removeChild(appScreen.parentNode, appScreen));
        this.renderer.addClass(appScreen, 'app-screen_fade-out');
    }

    public setViewportObserver(): void {
        this.renderer.addClass(document.documentElement, `viewport_${this.deviceService.viewportBreakpoint}`);

        this.deviceService.onResize.subscribe(message => {
            if (message.breakpointChange) {
                const {last, current} = message.breakpointChange;

                this.renderer.removeClass(document.documentElement, `viewport_${last}`);
                this.renderer.addClass(document.documentElement, `viewport_${current}`);
            }
        });
    }

    public setDeviceClasses(): void {
        const params = {
            browser: this.deviceService.browser,
            os: this.deviceService.os,
            device: this.deviceService.device,
        };

        forIn(params, (paramSection: any, paramSectionKey: string) => {
            forIn(paramSection, (paramValue: any, paramKey: string) => {
                if (paramValue === true) {
                    this.renderer.addClass(document.documentElement, `${paramSectionKey}_${paramKey}`);
                }
            });
        });

        document.documentElement.dataset.browserVersion = this.deviceService.browser.version;
    }
}
