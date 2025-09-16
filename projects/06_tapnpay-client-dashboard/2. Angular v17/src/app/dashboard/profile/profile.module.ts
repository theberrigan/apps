import {NgModule} from '@angular/core';
import {CommonModule} from '@angular/common';
import {ProfileNavComponent} from "./profile-nav/profile-nav.component";
import {ProfileComponent} from "./profile/profile.component";
import {SubscriptionSummaryComponent} from "./subscription-summary/subscription-summary.component";
import {
    SubscriptionInfoCardComponent
} from "./subscription-summary/subscription-info-card/subscription-info-card.component";
import {RouterModule} from "@angular/router";
import {PaymentMethodModule} from "../payment-method/payment-method.module";
import {PopupModule} from "../../_widgets/popup/popup.module";
import {TranslateModule} from "@ngx-translate/core";
import {FormsModule, ReactiveFormsModule} from "@angular/forms";
import {ButtonModule} from "../../_widgets/button/button.module";
import {MainPipesModule} from "../../_shared/main-pipes/main-pipes.module";
import {TimepickerModule} from "../../_widgets/timepicker/timepicker.module";
import {PagePanelModule} from "../page-panel/page-panel.module";
import {AppBarModule} from "../../app-bar/app-bar.module";
import {LoaderModule} from "../../_widgets/loader/loader.module";
import {SubscriptionLimitsModule} from "../../subscriptions/subscription-limit/subscription-limits.module";
import {SwitchModule} from "../../_widgets/switch/switch.module";
import { AutoPaymentCardComponent } from './profile-nav/auto-payment-card/auto-payment-card.component';


export const routes = [
    {
        path: '',
        component: ProfileComponent,
    },
    {
        path: 'vehicles',
        loadChildren: () => import('./vehicles/vehicles.module').then(m => m.VehiclesModule)
    },
    {
        path: 'subscription',
        component: SubscriptionSummaryComponent,
    },
];

@NgModule({
    declarations: [
        ProfileComponent,
        ProfileNavComponent,
        SubscriptionSummaryComponent,
        SubscriptionInfoCardComponent,
        AutoPaymentCardComponent
    ],
    imports: [
        CommonModule,
        RouterModule.forChild(routes),
        PaymentMethodModule,
        PopupModule,
        TranslateModule,
        FormsModule,
        ButtonModule,
        MainPipesModule,
        TimepickerModule,
        PagePanelModule,
        AppBarModule,
        LoaderModule,
        ReactiveFormsModule,
        SubscriptionLimitsModule,
        SwitchModule
    ]
})
export class ProfileModule {
}
