import {NgModule} from '@angular/core';
import {CommonModule} from '@angular/common';
import {RouterModule, Routes} from "@angular/router";
import {CanDeactivateGuard} from "../guards/can-deactivate.guard";
import {FaqDashboardComponent} from "./faq-dashboard/faq-dashboard.component";
import {ContactUsDashboardComponent} from "./contact-us-dashboard/contact-us-dashboard.component";
import {TermsDashboardComponent} from "./terms-dashboard/terms-dashboard.component";
import {CoverageGuard} from "../guards/coverage.guard";
import {PaypalRedirectComponent} from "../payments/paypal-redirect/paypal-redirect.component";
import {DashboardComponent} from "./dashboard/dashboard.component";
import {SubscriptionsModule} from "../subscriptions/subscriptions.module";
import {LoaderModule} from "../_widgets/loader/loader.module";
import {TranslateModule} from "@ngx-translate/core";
import {PagePanelModule} from "./page-panel/page-panel.module";
import {AppBarModule} from "../app-bar/app-bar.module";
import {ContactUsInnerModule} from "../_shared/contact-us-inner/contact-us-inner.module";
import {TermsInnerModule} from "../_shared/terms-inner/terms-inner.module";
import {
    MapToolAuthorityNamesStatesModule
} from "./extend-coverage/map-tool-authority-names-states/map-tool-authority-names-states.module";
import {AccordionModule} from "../_widgets/accordion/accordion.module";
import {SharedModule} from "../_shared/shared.module";
import {PopupModule} from "../_widgets/popup/popup.module";
import {DashboardSidebarComponent} from "./dashboard-sidebar/dashboard-sidebar.component";
import {ButtonModule} from "../_widgets/button/button.module";
import {LogoNeorideModule} from "../logo-neoride/logo-neoride.module";
import {DatepickerModule} from "../_widgets/datepicker/datepicker.module";
import {FaqInnerModule} from "../_shared/faq-inner/faq-inner.module";
import {AuthGuard} from "../guards/auth.guard";
import {TimepickerModule} from "../_widgets/timepicker/timepicker.module";
import {MainPipesModule} from "../_shared/main-pipes/main-pipes.module";
import {GoogleMapModule} from "../_widgets/google-map/google-map.module";
import {PaymentMethodModule} from "./payment-method/payment-method.module";
import {CheckboxModule} from "../_widgets/checkbox/checkbox.module";
import { SoftLockPopupComponent } from './dashboard/dialogs/notifications/soft-lock-popup/soft-lock-popup.component';
import { DebtLockPopupComponent } from './dashboard/dialogs/notifications/debt-lock-popup/debt-lock-popup.component';
import { FleetWalletPaymentConfirmComponent } from './dashboard/dialogs/notifications/fleet-wallet-payment-confirm/fleet-wallet-payment-confirm.component';
import {
    AccountNotificationPopupComponent
} from "./dashboard/dialogs/notifications/account-notification-popup/account-notification-popup.component";

const routes: Routes = [
    {
        path: '',
        component: DashboardComponent,
        canActivate: [
            AuthGuard
        ],
        canActivateChild: [
            AuthGuard
        ],
        children: [
            {
                path: '',
                component: DashboardComponent
            },
            {
                path: 'profile',
                loadChildren: () => import('./profile/profile.module').then(m => m.ProfileModule),
            },
            {
                path: 'invoices',
                loadChildren: () => import('./invoices/invoices.module').then(m => m.InvoicesModule),
            },

            {
                path: 'history',
                loadChildren: () => import('./history/history.module').then(m => m.HistoryModule),
            },
            {
                path: 'faq/:id',
                component: FaqDashboardComponent,
            },
            {
                path: 'faq',
                component: FaqDashboardComponent,
            },
            {
                path: 'contact-us',
                component: ContactUsDashboardComponent,
            },
            {
                path: 'terms',
                component: TermsDashboardComponent,
            },
            {
                path: 'coverage',
                loadChildren: () => import('./coverage/coverage.module').then(m => m.CoverageModule),
            },
            {
                path: 'extend-coverage',
                loadChildren: () => import('./extend-coverage/extend-coverage.module').then(m => m.ExtendCoverageModule),
            },
            {
                path: 'paypal-redirect/:action',
                component: PaypalRedirectComponent
            },
        ]
    }
];

@NgModule({
    declarations: [
        DashboardComponent,
        DashboardSidebarComponent,
        FaqDashboardComponent,
        ContactUsDashboardComponent,
        TermsDashboardComponent,
        SoftLockPopupComponent,
        DebtLockPopupComponent,
        FleetWalletPaymentConfirmComponent,
        AccountNotificationPopupComponent
    ],
    imports: [
        CommonModule,
        SubscriptionsModule,
        LoaderModule,
        TranslateModule,
        RouterModule.forChild(routes),
        PagePanelModule,
        AppBarModule,
        ContactUsInnerModule,
        TermsInnerModule,
        MapToolAuthorityNamesStatesModule,
        AccordionModule,
        SharedModule,
        PopupModule,
        ButtonModule,
        LogoNeorideModule,
        DatepickerModule,
        FaqInnerModule,
        TimepickerModule,
        MainPipesModule,
        GoogleMapModule,
        PaymentMethodModule,
        CheckboxModule
    ]
})
export class DashboardModule {
}
