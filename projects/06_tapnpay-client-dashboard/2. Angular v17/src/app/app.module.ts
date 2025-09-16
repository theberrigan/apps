import {APP_INITIALIZER, NgModule} from '@angular/core';
import {HTTP_INTERCEPTORS, HttpClient, provideHttpClient, withInterceptorsFromDi} from '@angular/common/http';

import {TranslateModule, TranslateLoader, TranslateCompiler} from '@ngx-translate/core';

import {AppRoutingModule} from './app-routing.module';
import {AppComponent} from './app.component';
import {NotFoundComponent} from './not-found/not-found.component';
import {SharedModule} from './_shared/shared.module';
import {UserService} from './services/user.service';
import {DEFAULT_LANG, LangService} from './services/lang.service';
import {BrowserAnimationsModule} from '@angular/platform-browser/animations';
import {Observable, of} from 'rxjs';
import {TranslateMessageFormatCompiler} from 'ngx-translate-messageformat-compiler';
import {TermsComponent} from './terms/terms.component';
import {NavMobileComponent} from './nav-mobile/nav-mobile.component';
import {AuthComponent} from './auth/auth.component';
import {TermsService} from './services/terms.service';
import {ApiRequestInterceptor} from './interceptors/api-request-interceptor';


import {AutoAuthComponent} from './auth/auto-auth/auto-auth.component';
import {AuthGuard} from './guards/auth.guard';
import {CanDeactivateGuard} from './guards/can-deactivate.guard';
import {FlatpickerComponent} from './_widgets/flatpicker/flatpicker.component';
import {CoverageGuard} from './guards/coverage.guard';


import {PopupModule} from "./_widgets/popup/popup.module";

import {AuthLogoComponent} from './auth/auth-logo/auth-logo.component';
import {
    DialogModule,
    DIALOG_DATA
} from "@angular/cdk/dialog";
import {ButtonModule} from "./_widgets/button/button.module";
import {ModalsModule} from "./_modals/modals.module";
import {SubscriptionsModule} from "./subscriptions/subscriptions.module";
import {catchError} from "rxjs/operators";
import {UserRegistrationFlowTypeService} from "./services/user-registration-flow-type.service";
import {SubscriptionApiService} from "./subscriptions/_services/subscription-api.service";
import {LogoNeorideModule} from "./logo-neoride/logo-neoride.module";
import {LangSwitcherModule} from "./_widgets/lang-switcher/lang-switcher.module";
import {ContactUsInnerModule} from "./_shared/contact-us-inner/contact-us-inner.module";
import {HelpPageModule} from "./help-page/help-page.module";
import {FaqInnerModule} from "./_shared/faq-inner/faq-inner.module";
import {LoaderModule} from "./_widgets/loader/loader.module";
import {TermsInnerModule} from "./_shared/terms-inner/terms-inner.module";
import {DashboardModule} from "./dashboard/dashboard.module";
import {PhoneMaskDirective} from "./auth/_directives/phone-mask.directive";
import { EmailVerificationComponent } from './email-verification/email-verification.component';

export class LocaleHttpLoader implements TranslateLoader {

    constructor(
        private http: HttpClient
    ) {
    }

    public getTranslation(lang: string): Observable<Object> {
        return this.http.get(`/assets/locale/${lang}.json`).pipe(
            catchError(error => {
                console.error(`Error loading locale ${lang}.json`);
                return of({});
            })
        );
    }
}

export function initApp(
    userService: UserService,
    langService: LangService,
    termsService: TermsService
) {
    return (): Promise<void> => {
        return new Promise((resolve) => {
            langService.setDefaultLang(DEFAULT_LANG.code);
            userService.initUser().then(() => {
                return Promise.all([
                    langService.use(userService.getLang()).toPromise(),
                    termsService.initTerms()
                ]);
            }).then(() => {
                resolve();
            });
        });
    }
}

const components = [
    AppComponent,
    NotFoundComponent,
    TermsComponent,
    NavMobileComponent,
    AuthComponent,
    AutoAuthComponent,
    FlatpickerComponent,
    EmailVerificationComponent,
];

@NgModule({
    declarations: [
        components,
        AuthLogoComponent,
        PhoneMaskDirective
    ],
    exports: [
        components,
    ],
    bootstrap: [
        AppComponent
    ], imports: [
        BrowserAnimationsModule,
        SharedModule,
        AppRoutingModule,
        TranslateModule.forRoot({
            loader: {
                provide: TranslateLoader,
                useClass: LocaleHttpLoader,
                deps: [HttpClient]
            },
            compiler: {
                provide: TranslateCompiler,
                useClass: TranslateMessageFormatCompiler
            }
        }),
        PopupModule,
        DialogModule,
        ButtonModule,
        ModalsModule,
        LogoNeorideModule,
        SubscriptionsModule,
        LangSwitcherModule,
        ContactUsInnerModule,
        HelpPageModule,
        FaqInnerModule,
        LoaderModule,
        TermsInnerModule,
        DashboardModule,
    ],
    providers: [
        AuthGuard,
        CanDeactivateGuard,
        CoverageGuard,
        {
            provide: HTTP_INTERCEPTORS,
            useClass: ApiRequestInterceptor,
            multi: true
        },
        {
            provide: APP_INITIALIZER,
            useFactory: initApp,
            deps: [
                UserService,
                LangService,
                TermsService
            ],
            multi: true
        },
        {provide: DIALOG_DATA, useValue: []},
        {
            provide: UserRegistrationFlowTypeService,
            useFactory: (SubscriptionApiService) => new UserRegistrationFlowTypeService(SubscriptionApiService),
            deps: [
                SubscriptionApiService
            ]
        },
        provideHttpClient(withInterceptorsFromDi())
    ]
})
export class AppModule {
}
