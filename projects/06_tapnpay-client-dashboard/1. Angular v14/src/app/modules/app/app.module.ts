import { APP_INITIALIZER, NgModule } from '@angular/core';
import {HTTP_INTERCEPTORS, HttpClient, HttpClientModule} from '@angular/common/http';

import {TranslateModule, TranslateLoader, TranslateCompiler} from '@ngx-translate/core';

import { AppRoutingModule } from './app-routing.module';
import { AppComponent }     from './app.component';
import { NotFoundComponent } from './not-found/not-found.component';
import { SharedModule } from '../shared.module';
import {UserService} from '../../services/user.service';
import {DEFAULT_LANG, LangService, LOCALES} from '../../services/lang.service';
import { CONFIG } from '../../../../config/app/dev';
import {BrowserAnimationsModule} from '@angular/platform-browser/animations';
import {Observable} from 'rxjs';
import {MESSAGE_FORMAT_CONFIG, TranslateMessageFormatCompiler} from 'ngx-translate-messageformat-compiler';
import {TermsComponent} from './terms/terms.component';
import {FaqComponent} from './faq/faq.component';
import {ContactUsComponent} from './contact-us/contact-us.component';
import {NavMobileComponent} from './nav-mobile/nav-mobile.component';
import {AppBarComponent} from './app-bar/app-bar.component';
import {AuthComponent} from './auth/auth.component';
import {HelpPageComponent} from './help-page/help-page.component';
import {LangSwitcherComponent} from './_widgets/lang-switcher/lang-switcher.component';
import {DashboardComponent} from './dashboard/dashboard.component';
import {InvoicesComponent} from './dashboard/invoices/invoices.component';
import {ProfileComponent} from './dashboard/profile/profile.component';
import {HistoryComponent} from './dashboard/history/history.component';
import {PagePanelComponent} from './dashboard/page-panel/page-panel.component';
import {TermsService} from '../../services/terms.service';
import {CommonModule} from '@angular/common';
import {ApiRequestInterceptor} from '../../interceptors/api-request-interceptor';
import {InvoicesListComponent} from './dashboard/invoices/invoices-list/invoices-list.component';
import {InvoiceDetailComponent} from './dashboard/invoices/invoice-detail/invoice-detail.component';
import {InvoicePaymentComponent} from './dashboard/invoices/invoice-payment/invoice-payment.component';
import {FaqInnerComponent} from './_shared/faq-inner/faq-inner.component';
import {FaqDashboardComponent} from './dashboard/faq-dashboard/faq-dashboard.component';
import {ContactUsInnerComponent} from './_shared/contact-us-inner/contact-us-inner.component';
import {ContactUsDashboardComponent} from './dashboard/contact-us-dashboard/contact-us-dashboard.component';
import {TermsInnerComponent} from './_shared/terms-inner/terms-inner.component';
import {TermsDashboardComponent} from './dashboard/terms-dashboard/terms-dashboard.component';
import {PaginationComponent} from './_widgets/pagination/pagination.component';
import {VehiclesComponent} from './dashboard/profile/vehicles/vehicles.component';
import {InvoiceHistoryComponent} from './dashboard/history/invoice-history/invoice-history.component';
import {AutoAuthComponent} from './auth/auto-auth/auto-auth.component';
import {PaymentMethodComponent} from './dashboard/payment-method/payment-method.component';
import {AuthGuard} from '../../guards/auth.guard';
import {CanDeactivateGuard} from '../../guards/can-deactivate.guard';
import {GoogleMapComponent} from './_widgets/google-map/google-map.component';
import {CoverageComponent} from './dashboard/coverage/coverage.component';
import {DatepickerComponent} from './_widgets/datepicker/datepicker.component';
import {FlatpickerComponent} from './_widgets/flatpicker/flatpicker.component';
import {CoverageGuard} from '../../guards/coverage.guard';

export class LocaleHttpLoader implements TranslateLoader {
    private readonly hashes = LOCALES_HASHES;

    constructor (
        private http : HttpClient
    ) {}

    public getTranslation (lang : string) : Observable<Object> {
        const hash = (
            this.hashes[ lang.toLowerCase() ] || APP_VERSION ||
            new Date().toISOString().match(/^\d+-\d+-\d+/)[0]
        );

        return this.http.get(`/assets/locale/${ lang }.json?${ hash }`);
    }
}

export function initApp (
    userService : UserService,
    langService : LangService,
    termsService : TermsService
) {
    return () : Promise<any> => {
        return new Promise((resolve) => {
            langService.setDefaultLang(DEFAULT_LANG.code);
            userService.initUser().then(() => {
                return Promise.all([
                    langService.use(userService.getLang()).toPromise(),
                    termsService.initTerms()
                ]);
            }).then(() => resolve());
        });
    }
}

const components = [
    AppComponent,
    NotFoundComponent,
    TermsComponent,
    TermsInnerComponent,
    TermsDashboardComponent,
    FaqComponent,
    FaqDashboardComponent,
    FaqInnerComponent,
    ContactUsComponent,
    ContactUsInnerComponent,
    ContactUsDashboardComponent,
    NavMobileComponent,
    AppBarComponent,
    AuthComponent,
    AutoAuthComponent,
    HelpPageComponent,
    LangSwitcherComponent,
    DashboardComponent,
    InvoicesComponent,
    InvoicesListComponent,
    InvoiceDetailComponent,
    InvoicePaymentComponent,
    ProfileComponent,
    HistoryComponent,
    PagePanelComponent,
    PaginationComponent,
    DatepickerComponent,
    VehiclesComponent,
    InvoiceHistoryComponent,
    PaymentMethodComponent,
    GoogleMapComponent,
    CoverageComponent,
    FlatpickerComponent
];

@NgModule({
    declarations: components,
    imports: [
        BrowserAnimationsModule,
        SharedModule,
        HttpClientModule,
        AppRoutingModule,
        TranslateModule.forRoot({
            loader: {
                provide: TranslateLoader,
                useClass: LocaleHttpLoader,
                deps: [ HttpClient ]
            },
            compiler: {
                provide: TranslateCompiler,
                useClass: TranslateMessageFormatCompiler  // http://messageformat.github.io/messageformat/guide/
            }
        })
    ],
    exports: components,
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
        {
            provide: MESSAGE_FORMAT_CONFIG,
            useValue: {
                locales: LOCALES
            }
        }
    ],
    bootstrap: [
        AppComponent
    ]
})
export class AppModule {}
