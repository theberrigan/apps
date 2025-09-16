import {
    ChangeDetectionStrategy,
    Component,
    HostBinding,
    Input, OnDestroy,
    OnInit,
    Renderer2,
    ViewEncapsulation
} from '@angular/core';
import {Router} from '@angular/router';
import {ReplaySubject, Subject, Subscription} from 'rxjs';
import {defer} from '../../../lib/utils';
import {LANGS, LangService} from '../../../services/lang.service';
import {TermsService, TermsSession} from '../../../services/terms.service';
import {NavService} from '../../../services/nav.service';
import {UserService} from '../../../services/user.service';
import {DashboardService} from '../../../services/dashboard.service';

type Layout = 'nav' | 'langs';

@Component({
    selector: 'nav-mobile',
    templateUrl: './nav-mobile.component.html',
    styleUrls: [ './nav-mobile.component.scss' ],
    changeDetection: ChangeDetectionStrategy.Default,
    encapsulation: ViewEncapsulation.None,
    host: {
        'class': 'nav-mobile'
    }
})
export class NavMobileComponent implements OnInit, OnDestroy {
    readonly langs = LANGS;

    @HostBinding('class.nav-mobile_open')
    isActive : boolean = false;

    activeLayout : Layout = 'nav';

    subs : Subscription[] = [];

    currentLang : string = null;

    termsSession : TermsSession;

    isLoggedIn : boolean = false;

    isInDashboard : boolean = false;

    constructor (
        private renderer : Renderer2,
        private router : Router,
        private langService : LangService,
        private termsService : TermsService,
        private navService : NavService,
        private userService : UserService,
        private dashboardService : DashboardService,
    ) {
        this.currentLang = this.langService.getCurrentLangCode();
        this.subs.push(this.userService.onLoginStateChange.subscribe(isLoggedIn => {
            this.isLoggedIn = isLoggedIn;
        }));

        this.subs.push(this.dashboardService.onDashboardStateChange.subscribe(isInDashboard => {
            defer(() => this.isInDashboard = isInDashboard);
        }));

        this.setTermsState(this.termsService.getTermsSession());
        this.subs.push(this.termsService.onTermsSessionChange.subscribe(session => {
            defer(() => this.setTermsState(session));
        }));
    }

    public ngOnInit () {
        this.subs.push(
            this.navService.navMessagePipe.subscribe(message => {
                console.log(message);
                defer(() => {
                    switch (message.action) {
                        case 'toggle':
                            this.setNavState(!this.isActive);
                            break;
                        case 'hide':
                            this.setNavState(false);
                            break;
                        case 'show':
                            this.setNavState(true);
                            break;
                    }
                });
            })
        );

        this.subs.push(this.langService.onLangChange(() => {
            this.currentLang = this.langService.getCurrentLangCode();
        }));
    }

    public ngOnDestroy () : void {
        this.setNavState(false);
        this.subs.forEach(sub => sub.unsubscribe());
    }

    isCoverageVisible () : boolean {
        return true;  // this.userService.getUserData().account.paymentModel !== 'FLEET';
    }

    setTermsState (termsSession : TermsSession) {
        this.termsSession = termsSession;
    }

    onOverlayClick () {
        this.setNavState(false);
    }

    onClose () {
        this.setNavState(false);
    }

    setNavState (isActive : boolean) {
        if (isActive) {
            this.renderer.addClass(document.body, 'nav-mobile-active');
            this.isActive = true;
        } else {
            this.renderer.removeClass(document.body, 'nav-mobile-active');
            this.isActive = false;
        }
    }

    onSwitchLayout (layout : Layout) {
        this.activeLayout = layout;
    }

    onSwitchLang (langCode : string) {
        this.currentLang = langCode;
        this.userService.setLang(langCode);
        this.onSwitchLayout('nav');
        this.setNavState(false);
    }

    onLogout () {
        this.userService.logout();
        this.router.navigateByUrl('/auth');
        this.onClose();
    }
}
