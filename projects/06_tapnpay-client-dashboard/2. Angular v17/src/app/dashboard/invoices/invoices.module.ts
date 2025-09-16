import {NgModule} from '@angular/core';
import {CommonModule} from '@angular/common';
import {RouterModule, Routes} from "@angular/router";
import {InvoicesListComponent} from "./invoices-list/invoices-list.component";
import {InvoicesComponent} from "./invoices.component";
import {InvoicePaymentComponent} from "./invoice-payment/invoice-payment.component";
import {InvoiceDetailComponent} from "./invoice-detail/invoice-detail.component";
import {InvoiceListHeaderComponent} from "./invoices-list/invoice-list-header/invoice-list-header.component";
import {InvoiceListItemComponent} from "./invoices-list/invoice-list-item/invoice-list-item.component";
import {FormsModule} from "@angular/forms";
import {TranslateModule} from "@ngx-translate/core";
import {PopupModule} from "../../_widgets/popup/popup.module";
import {ButtonModule} from "../../_widgets/button/button.module";
import {AppBarModule} from "../../app-bar/app-bar.module";
import {PagePanelModule} from "../page-panel/page-panel.module";
import {GoogleMapModule} from "../../_widgets/google-map/google-map.module";
import {MainPipesModule} from "../../_shared/main-pipes/main-pipes.module";
import {LoaderModule} from "../../_widgets/loader/loader.module";
import {ContextPanelModule} from "../../_widgets/context-panel/context-panel.module";
import {CheckboxStaticModule} from "../../_widgets/checkbox-static/checkbox-static.module";
import {PaymentMethodModule} from "../payment-method/payment-method.module";
import { AlertComponent } from './alert/alert.component';
import { PayPanelComponent } from './pay-panel/pay-panel.component';
import {CheckboxModule} from "../../_widgets/checkbox/checkbox.module";
import {UserMainInfoModule} from "../user-main-info/user-main-info.module";
import { SubscriptionInvoiceCardComponent } from './invoice-detail/subscription-invoice-card/subscription-invoice-card.component';

const routes: Routes = [
    {
        path: '',
        component: InvoicesComponent,
    }
];


@NgModule({
    declarations: [
        InvoicesComponent,
        InvoicesListComponent,
        InvoicePaymentComponent,
        InvoiceDetailComponent,
        InvoiceListHeaderComponent,
        InvoiceListItemComponent,
        AlertComponent,
        PayPanelComponent,
        SubscriptionInvoiceCardComponent

    ],
    exports: [
        InvoicesComponent
    ],
    imports: [
        CommonModule,
        FormsModule,
        TranslateModule,
        PopupModule,
        ButtonModule,
        AppBarModule,
        PagePanelModule,
        GoogleMapModule,
        RouterModule.forChild(routes),
        MainPipesModule,
        LoaderModule,
        ContextPanelModule,
        CheckboxStaticModule,
        PaymentMethodModule,
        CheckboxModule,
        UserMainInfoModule
    ]
})
export class InvoicesModule {
}
