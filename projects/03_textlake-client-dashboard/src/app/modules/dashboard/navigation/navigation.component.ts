import {AfterViewInit, Component, EventEmitter, NgZone, OnDestroy, OnInit, Output, ViewEncapsulation} from '@angular/core';
import {DeviceService, ViewportBreakpoint} from '../../../services/device.service';
import {TermsService} from '../../../services/terms.service';
import {UserData, UserService} from '../../../services/user.service';
import {NavigationStart, Router} from '@angular/router';
import {CONFIG} from '../../../../../config/app/dev';
import {defer, int} from '../../../lib/utils';
import {Subscription} from 'rxjs';
import {first} from 'rxjs/operators';
import {ToastService} from '../../../services/toast.service';
import {TooltipOptions} from 'ng2-tooltip-directive';

@Component({
    selector: 'navigation',
    exportAs: 'navigation',
    templateUrl: './navigation.component.html',
    styleUrls: [ './navigation.component.scss' ],
    encapsulation: ViewEncapsulation.None,
    host: {
        'class': 'nav',
    }
})
export class NavigationComponent implements OnInit, OnDestroy {
    public isMobileActive : boolean = false;
    public isMinimizedTablet : boolean = true;
    public isMinimizedDesktop : boolean = false;
    public isDev : boolean = false;
    public viewportBreakpoint : ViewportBreakpoint = null;
    public userData : UserData;
    public subs : Subscription[] = [];

    @Output()
    public onMinimizeChange = new EventEmitter<boolean>();

    @Output()
    public onMobileActiveChange = new EventEmitter<boolean>();

    public get isMinimized () : boolean {
        switch (this.viewportBreakpoint) {
            case 'desktop':
                return this.isMinimizedDesktop;
            case 'tablet':
                return this.isMinimizedTablet;
            default:
                return true;
        }
    }

    public set isMinimized (isMinimized : boolean) {
        switch (this.viewportBreakpoint) {
            case 'desktop':
                this.isMinimizedDesktop = isMinimized;
                break;
            case 'tablet':
                this.isMinimizedTablet = isMinimized;
                break;
        }

        this.notifyMinimize();
        defer(() => window.localStorage.setItem('navState', String(Number(this.isMinimizedDesktop))));
    }

    public itemTooltipOptions : TooltipOptions = {
        placement: 'right',
        autoPlacement: false,
        'show-delay': 150,
        'hide-delay': 17,
        display: false,
        displayTouchscreen: false,
        'z-index': 11000,
        'animation-duration': 100,
        shadow: false
    };

    constructor (
        private router : Router,
        private deviceService : DeviceService,
        private userService : UserService,
        private toastService : ToastService,
        private zone: NgZone
    ) {
        this.isDev = !CONFIG.isProduction;
        this.isMinimizedDesktop = !!(int(window.localStorage.getItem('navState')) || 0);
        this.zone.onStable.pipe(first()).subscribe(() => this.notifyMinimize());
        this.userData = this.userService.getUserData();
        this.viewportBreakpoint = this.deviceService.viewportBreakpoint;

        this.addSub(
            this.userService.onUserDataUpdated.subscribe((userData : UserData) => {
                this.userData = userData;
            }),
            this.deviceService.onResize.subscribe((message) => {
                if (message.breakpointChange) {
                    if ((this.viewportBreakpoint = this.deviceService.viewportBreakpoint) === 'tablet') {
                        this.isMinimized = true;
                    }

                    this.notifyMinimize();
                }
            }),
            this.router.events.subscribe(e => {
                if (e instanceof NavigationStart) {
                    this.deactivate();
                }
            })
        );
    }

    public ngOnInit () : void {
        this.notifyMinimize();
    }

    public ngOnDestroy () : void {
        this.subs.forEach(sub => sub.unsubscribe());
        this.toastService.onNavToggle.next('nav_absent');
    }

    public addSub (...sub) : void {
        this.subs = [ ...this.subs, ...sub ];
    }

    // Only for mobile
    public deactivate () : void {
        if (this.viewportBreakpoint === 'mobile') {
            this.isMobileActive = false;
            this.notifyMobileActive();
        }
    }

    public toggle () : void {
        if (this.viewportBreakpoint === 'mobile') {
            this.isMobileActive = !this.isMobileActive;
            this.notifyMobileActive();
        } else {
            this.isMinimized = !this.isMinimized;
        }
    }

    public notifyMobileActive () : void {
        this.onMobileActiveChange.emit(this.isMobileActive);
    }

    public notifyMinimize () : void {
        const ttOptions = { ...this.itemTooltipOptions };
        ttOptions.display = this.viewportBreakpoint === 'desktop' && this.isMinimized;
        this.itemTooltipOptions = ttOptions;

        this.onMinimizeChange.emit(this.isMinimized);
        this.toastService.onNavToggle.next(this.isMinimized ? 'nav_collapsed' : 'nav_expanded');
    }

    public isNavItemVisible (feature : string) : boolean {
        return this.userData && this.userData.features && this.userData.features.can(feature);
    }
}
