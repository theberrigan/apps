import {
    Component, ElementRef, EventEmitter, Input,
    OnDestroy,
    OnInit, Output, Renderer2,
    ViewEncapsulation
} from '@angular/core';
import {DeviceService, ViewportBreakpoint} from '../../../services/device.service';
import {defer} from '../../../lib/utils';
import {Subscription} from 'rxjs';


@Component({
    selector: 'sidebar',
    exportAs: 'sidebar',
    templateUrl: './sidebar.component.html',
    styleUrls: [ './sidebar.component.scss' ],
    encapsulation: ViewEncapsulation.None,
    host: {
        'class': 'sidebar',
    }
})
export class SidebarComponent implements OnInit, OnDestroy {
    public subs : Subscription[] = [];
    public viewportBreakpoint : ViewportBreakpoint = null;
    public _isMobileActive : boolean = false;
    public _isDesktopActive : boolean = true;
    public dashboardEl : any;

    public set isMobileActive (isActive : boolean) {
        this._isMobileActive = isActive;

        if (this.viewportBreakpoint !== 'desktop') {
            isActive ? this.show() : this.hide();
        }
    }

    public get isMobileActive () : boolean {
        return this._isMobileActive;
    }

    @Output()
    public isDesktopActiveChange = new EventEmitter<boolean>();

    @Input()
    public set isDesktopActive (isActive : boolean) {
        this._isDesktopActive = isActive;

        if (this.viewportBreakpoint === 'desktop') {
            defer(() => {
                isActive ? this.show() : this.hide();
            });
        }
    }

    public get isDesktopActive () : boolean {
        return this._isDesktopActive;
    }

    public set isActive (isActive : boolean) {
        if (this.viewportBreakpoint === 'desktop') {
            this.isDesktopActive = isActive;
            this.isDesktopActiveChange.emit(isActive);
        } else {
            this.isMobileActive = isActive;
        }
    }

    public get isActive () : boolean {
        return this.viewportBreakpoint === 'desktop' ? this.isDesktopActive : this.isMobileActive;
    }

    // 1. call constructor
    // 2. sync input properties
    // 3. call ngOnInit
    // TODO: on mobile: disable page scroll whe activate
    constructor (
        private renderer : Renderer2,
        private deviceService : DeviceService
    ) {
        this.dashboardEl = document.querySelector('dashboard.dashboard');
        this.viewportBreakpoint = this.deviceService.viewportBreakpoint;

        this.addSub(
            this.deviceService.onResize.subscribe((message) => {
                if (message.breakpointChange) {
                    this.viewportBreakpoint = this.deviceService.viewportBreakpoint;

                    if (this.viewportBreakpoint === 'desktop') {
                        this.isMobileActive = false;
                    }

                    this.isActive ? this.show() : this.hide();
                }
            })
        );
    }

    public ngOnInit () : void {
        this.isActive ? this.show() : this.hide();
    }

    public addSub (sub : Subscription) : void {
        this.subs = [ ...this.subs, sub ];
    }

    public ngOnDestroy () : void {
        this.subs.forEach(sub => sub.unsubscribe());
        this.hide();
    }

    public toggle () : void {
        this.isActive = !this.isActive;
    }

    public activate () : void {
        this.isActive = true;
    }

    public deactivate () : void {
        this.isActive = false;
    }

    public hide () : void {
        this.renderer.removeClass(this.dashboardEl, 'dashboard_sidebar-active');
    }

    public show () : void {
        this.renderer.addClass(this.dashboardEl, 'dashboard_sidebar-active');
    }

    public get useCustomScrollbar () : boolean {
        return !this.deviceService.device.touch && !this.deviceService.browser.chrome;
    }

    public get isDesktop () : boolean {
        return this.viewportBreakpoint === 'desktop';
    }
}




