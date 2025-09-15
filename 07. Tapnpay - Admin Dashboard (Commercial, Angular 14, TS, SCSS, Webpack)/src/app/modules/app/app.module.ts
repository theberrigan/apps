import { APP_INITIALIZER, NgModule } from '@angular/core';
import {HTTP_INTERCEPTORS, HttpClient, HttpClientModule} from '@angular/common/http';
import {BrowserAnimationsModule} from '@angular/platform-browser/animations';
import {Observable} from 'rxjs';

import {TranslateModule, TranslateLoader, TranslateCompiler} from '@ngx-translate/core';

import { AppRoutingModule } from './app-routing.module';
import { AppComponent }     from './app.component';
import { NotFoundComponent } from './not-found/not-found.component';
import { SharedModule } from '../shared.module';
import {UserService} from '../../services/user.service';
import {DEFAULT_LANG, LangService, LOCALES} from '../../services/lang.service';
import {MESSAGE_FORMAT_CONFIG, TranslateMessageFormatCompiler} from 'ngx-translate-messageformat-compiler';
import {AuthComponent} from './auth/auth.component';
import {DashboardComponent} from './dashboard/dashboard.component';
import {ApiRequestInterceptor} from '../../interceptors/api-request-interceptor';
import {PaginationComponent} from './_widgets/pagination/pagination.component';
import {AuthGuard} from '../../guards/auth.guard';
import {CanDeactivateGuard} from '../../guards/can-deactivate.guard';
import {AccountsComponent} from './dashboard/accounts/accounts.component';
import {TabsComponent} from './_widgets/tabs/tabs.component';
import {TabComponent} from './_widgets/tabs/tab/tab.component';
import {PanelComponent} from './dashboard/panel/panel.component';
import {SearchComponent} from './dashboard/panel/search/search.component';
import {NavComponent} from './dashboard/panel/nav/nav.component';
import {AccountEditorComponent} from './dashboard/accounts/account-editor/account-editor.component';
import {AccountEditorSummaryComponent} from './dashboard/accounts/account-editor/account-editor-summary/account-editor-summary.component';
import {AccountEditorInvoicesComponent} from './dashboard/accounts/account-editor/account-editor-invoices/account-editor-invoices.component';
import {AccountEditorPaymentsComponent} from './dashboard/accounts/account-editor/account-editor-payments/account-editor-payments.component';
import {AccountEditorSmsLogComponent} from './dashboard/accounts/account-editor/account-editor-sms-log/account-editor-sms-log.component';
import {AccountEditorActionsComponent} from './dashboard/accounts/account-editor/account-editor-actions/account-editor-actions.component';
import {DatepickerComponent} from './_widgets/datepicker/datepicker.component';
import {AccountEditorInvoiceDetailsComponent} from './dashboard/accounts/account-editor/account-editor-invoice-details/account-editor-invoice-details.component';
import {ContextMenuComponent} from './_widgets/context-menu/context-menu.component';
import {AccountsGuard} from '../../guards/accounts.guard';
import {FAQComponent} from './dashboard/faq/faq.component';
import {FaqGuard} from '../../guards/faq.guard';
import {SwitchComponent} from './_widgets/switch/switch.component';
import {CoverageComponent} from './dashboard/coverage/coverage.component';
import {SliderComponent} from './_widgets/slider/slider.component';
import {TAListComponent} from './dashboard/ta/ta-list.component';
import {TAEditorComponent} from './dashboard/ta/ta-editor.component';
import {CoverageGuard} from '../../guards/coverage.guard';
import {TAListGuard} from '../../guards/ta-list.guard';
import {TAEditorGuard} from '../../guards/ta-editor.guard';
import {DropdownMenuComponent} from './_widgets/dropdown-menu/dropdown-menu.component';
import {CarrierContractListComponent} from './dashboard/contracts/carrier-contract-list.component';
import {CarrierContractComponent} from './dashboard/contracts/carrier-contract.component';
import {TAContractListComponent} from './dashboard/contracts/ta-contract-list.component';
import {TAContractComponent} from './dashboard/contracts/ta-contract.component';
import {PGContractListComponent} from './dashboard/contracts/pg-contract-list.component';
import {PGContractComponent} from './dashboard/contracts/pg-contract.component';
import {CarrierContractListGuard} from '../../guards/carrier-contract-list.guard';
import {CarrierContractGuard} from '../../guards/carrier-contract.guard';
import {TAContractListGuard} from '../../guards/ta-contract-list.guard';
import {TAContractGuard} from '../../guards/ta-contract.guard';
import {PGContractListGuard} from '../../guards/pg-contract-list.guard';
import {PGContractGuard} from '../../guards/pg-contract.guard';
import {AccountEditorDisputesComponent} from './dashboard/accounts/account-editor/account-editor-disputes/account-editor-disputes.component';
import {DisputesGuard} from '../../guards/disputes.guard';
import {DisputesComponent} from './dashboard/disputes/disputes.component';

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
) {
    return () : Promise<any> => {
        return new Promise((resolve) => {
            langService.setDefaultLang(DEFAULT_LANG.code);
            userService.initUser().then(() => {
                return Promise.all([
                    langService.use(userService.getLang()).toPromise(),
                ]);
            }).then(() => resolve());
        });
    }
}

@NgModule({
    declarations: [
        AppComponent,
        NotFoundComponent,
        AuthComponent,
        DashboardComponent,
        PaginationComponent,
        AccountsComponent,
        AccountEditorComponent,
        AccountEditorSummaryComponent,
        AccountEditorInvoicesComponent,
        AccountEditorPaymentsComponent,
        AccountEditorDisputesComponent,
        AccountEditorSmsLogComponent,
        AccountEditorActionsComponent,
        AccountEditorInvoiceDetailsComponent,
        FAQComponent,
        CoverageComponent,
        CarrierContractListComponent,
        CarrierContractComponent,
        TAContractListComponent,
        TAContractComponent,
        PGContractListComponent,
        PGContractComponent,
        TAListComponent,
        TAEditorComponent,
        TabsComponent,
        TabComponent,
        PanelComponent,
        SearchComponent,
        NavComponent,
        DatepickerComponent,
        ContextMenuComponent,
        DropdownMenuComponent,
        SwitchComponent,
        SliderComponent,
        DisputesComponent
    ],
    imports: [
        BrowserAnimationsModule,
        // BrowserModule,
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
    exports: [
        NotFoundComponent,
        AuthComponent,
        DashboardComponent,
        PaginationComponent,
        AccountsComponent,
        AccountEditorComponent,
        AccountEditorSummaryComponent,
        AccountEditorInvoicesComponent,
        AccountEditorPaymentsComponent,
        AccountEditorDisputesComponent,
        AccountEditorSmsLogComponent,
        AccountEditorActionsComponent,
        AccountEditorInvoiceDetailsComponent,
        FAQComponent,
        TAListComponent,
        TAEditorComponent,
        CoverageComponent,
        CarrierContractListComponent,
        CarrierContractComponent,
        TAContractListComponent,
        TAContractComponent,
        PGContractListComponent,
        PGContractComponent,
        TabsComponent,
        TabComponent,
        PanelComponent,
        SearchComponent,
        NavComponent,
        DatepickerComponent,
        ContextMenuComponent,
        DropdownMenuComponent,
        SwitchComponent,
        SliderComponent,
        DisputesComponent
    ],
    providers: [
        AuthGuard,
        AccountsGuard,
        FaqGuard,
        DisputesGuard,
        CoverageGuard,
        TAListGuard,
        TAEditorGuard,
        CarrierContractListGuard,
        CarrierContractGuard,
        TAContractListGuard,
        TAContractGuard,
        PGContractListGuard,
        PGContractGuard,
        CanDeactivateGuard,
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
