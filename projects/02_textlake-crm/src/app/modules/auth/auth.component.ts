import {Component, HostListener, OnDestroy, OnInit, Renderer2, ViewEncapsulation} from '@angular/core';
import {ActivatedRoute, Router} from '@angular/router';
import {UserData, UserService} from '../../services/user.service';
import {ILang, LANGS, LangService} from '../../services/lang.service';
import {includes} from 'lodash';
import {TermsService} from '../../services/terms.service';

// type AuthAction = 'sign-in' | 'sign-up' | 'new-password' | 'forgot-password' | 'reset-password' | 'handle-token';

const AUTH_ACTIONS = [ 'sign-in', 'sign-up', 'new-password', 'forgot-password', 'reset-password', 'handle-token' ];

export type SocialAuthProvider = 'Google' | 'Facebook';

@Component({
    selector: 'auth',
    templateUrl: './auth.component.html',
    styleUrls: [ './auth.component.scss' ],
    encapsulation: ViewEncapsulation.None,
    host: {
        class: 'auth'
    }
})
export class AuthComponent implements OnInit, OnDestroy {
    public action : string = 'sign-in';

    public isBusy : boolean = false;

    public langs : ILang[] = LANGS;

    public isLangMenuActive : boolean = false;

    public isLangMenuDisabled : boolean = false;

    public userData : UserData;

    public currentLang : ILang;

    public isReady : boolean = false;

    public year : number = 2019;

    public listeners : any[] = [];

    constructor (
        private router : Router,
        private route : ActivatedRoute,
        private renderer : Renderer2,
        private userService : UserService,
        private langService : LangService,
        private termsService : TermsService
    ) {}

    public ngOnInit () : void {
        this.year = (new Date()).getFullYear();
        this.userData = this.userService.getUserData();
        this.currentLang = this.langService.getLangByCode(this.userData.local.language);

        this.route.params.subscribe((params : any) => {
            const action = params['action'];

            if (includes(AUTH_ACTIONS, action)) {
                this.action = action;
            } else {
                this.router.navigateByUrl('/not-found');
            }
        });

        this.isReady = true;

        this.listeners = [ ...this.listeners, this.renderer.listen(document.documentElement, 'click', () => this.deactivateLangMenu()) ];
    }

    public ngOnDestroy () : void {
        this.listeners.forEach(unlisten => unlisten());
    }

    public onProgressStateChange (isBusy : boolean) : void {
        this.isBusy = isBusy;
    }

    public onAfterSignIn () : void {
        this.router.navigateByUrl('/dashboard');
    }

    public executeSocialAuth (provider : SocialAuthProvider) : void {
        this.isBusy = true;

        this.userService
            .executeSocialAuth(provider)
            .then((result : any) => {
                this.isBusy = false;

                switch (result.action) {
                    case 'COMPLETE':
                        this.onAfterSignIn();
                        break;
                    case 'ERROR':
                        this.userService.onAuthMessage.next({
                            type: 'error',
                            messageKey: result.error,
                            messageData: result.errorData
                        });
                        break;
                    default:
                        console.warn('Unexpected behavior');
                }
            });
    }

    public onLanguageChange (lang : ILang) : void {
        this.isLangMenuDisabled = true;

        this.currentLang = lang;
        // this.langService.use(lang.code);
        this.userData.local.language = lang.code;
        this.userData.local.updateRemoteLangAfterSignIn = true;

        this.userService
            .updateUserData({ data: this.userData })
            .then(() => {
                this.isLangMenuDisabled = false;
            });
    }

    public toggleLangMenu (e : any) : void {
        e.stopPropagation();

        if (!this.isLangMenuDisabled) {
            this.isLangMenuActive = !this.isLangMenuActive;
        }
    }

    // @HostListener('document:click')
    public deactivateLangMenu () : void {
        this.isLangMenuActive = false;
    }

    public showTerms (e : any) : void {
        e.preventDefault();
        this.termsService.showPublicTerms(); // .subscribe((e) => console.log(e));
    }
}
