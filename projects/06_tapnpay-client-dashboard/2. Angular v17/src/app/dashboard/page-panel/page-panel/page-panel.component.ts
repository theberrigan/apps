import {
    ChangeDetectionStrategy,
    Component,
    HostListener,
    OnDestroy,
    OnInit,
    Renderer2,
    ViewEncapsulation
} from '@angular/core';
import {Router} from '@angular/router';
import {DeviceService, ViewportBreakpoint} from '../../../services/device.service';
import {Subscription} from 'rxjs';
import {DomService} from '../../../services/dom.service';
import {UserService} from '../../../services/user.service';
import {ILang, LANGS, LangService} from '../../../services/lang.service';
import {defer} from '../../../lib/utils';

@Component({
    selector: 'page-panel',
    templateUrl: './page-panel.component.html',
    styleUrls: ['./page-panel.component.scss'],
    changeDetection: ChangeDetectionStrategy.Default,
    encapsulation: ViewEncapsulation.None,
    host: {
        'class': 'page-panel'
    }
})
export class PagePanelComponent implements OnInit, OnDestroy {
    viewportBreakpoint: ViewportBreakpoint;

    subs: Subscription[] = [];

    isUserMenuActive: boolean = false;

    isLangLayoutActive: boolean = false;

    readonly langs = LANGS;

    currentLang: ILang;

    constructor(
        private renderer: Renderer2,
        private router: Router,
        private deviceService: DeviceService,
        private domService: DomService,
        private langService: LangService,
        private userService: UserService,
    ) {
        this.viewportBreakpoint = this.deviceService.viewportBreakpoint;
        this.subs.push(this.deviceService.onResize.subscribe((message) => {
            if (message.breakpointChange) {
                this.viewportBreakpoint = message.breakpointChange.current;
            }
        }));

        this.updateCurrentLang();
        this.subs.push(this.langService.onLangChange(() => this.updateCurrentLang()));
    }

    ngOnInit() {

    }

    ngOnDestroy(): void {
        this.subs.forEach(sub => sub.unsubscribe());
    }

    updateCurrentLang() {
        const currentLangCode = this.langService.getCurrentLangCode();
        this.currentLang = this.langs.find(lang => lang.code === currentLangCode);
    }

    onLangItemClick(lang: ILang, e: MouseEvent) {
        this.domService.markEvent(e, 'userItemClick');
        this.userService.setLang(lang.code);
        defer(() => this.isLangLayoutActive = false)
    }

    onLogout(e: any) {
        this.onUserMenuItemClick(e);
        this.userService.logout();
        this.router.navigateByUrl('/auth');
    }

    // -----------------------------

    onUserMenuItemClick(e: any) {
        this.domService.markEvent(e, 'userItemClick');
    }

    onUserMenuClick(e: any) {
        this.domService.markEvent(e, 'userMenuClick');
    }

    onUserMenuTriggerClick(e: any) {
        this.domService.markEvent(e, 'userTriggerClick');
    }

    @HostListener('document:click', ['$event'])
    onDocClick(e: any) {
        if (this.domService.isHasEventMark(e, 'userTriggerClick')) {
            this.isUserMenuActive = !this.isUserMenuActive;
        } else if (
            !this.domService.isHasEventMark(e, 'userMenuClick') ||
            !this.domService.isHasEventMark(e, 'langTriggerClick') ||
            this.domService.isHasEventMark(e, 'userItemClick')
        ) {
            this.isUserMenuActive = false;
        }
    }

    onToggleLangLayout(isActive: boolean, e: MouseEvent) {
        this.domService.markEvent(e, 'langTriggerClick');
        this.isLangLayoutActive = isActive;
    }
}
