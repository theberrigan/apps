import {NgModule} from '@angular/core';
import {CommonModule} from '@angular/common';
import {PaymentMethodComponent} from "./payment-method/payment-method.component";
import {LoaderModule} from "../../_widgets/loader/loader.module";
import {PopupModule} from "../../_widgets/popup/popup.module";
import {TranslateModule} from "@ngx-translate/core";
import {ButtonModule} from "../../_widgets/button/button.module";
import {FormsModule} from "@angular/forms";
import {CheckboxModule} from "../../_widgets/checkbox/checkbox.module";
import { PaymentIconSecuredStripeComponent } from './payment-method/payment-icon-secured-stripe/payment-icon-secured-stripe.component';
import { PaymentIconLogoCardsComponent } from './payment-method/payment-icon-logo-cards/payment-icon-logo-cards.component';
import { PaymentIconLogoGooglePlayComponent } from './payment-method/payment-icon-logo-google-play/payment-icon-logo-google-play.component';
import { PaymentIconLogoPaypalComponent } from './payment-method/payment-icon-logo-paypal/payment-icon-logo-paypal.component';


@NgModule({
    declarations: [PaymentMethodComponent, PaymentIconSecuredStripeComponent, PaymentIconLogoCardsComponent, PaymentIconLogoGooglePlayComponent, PaymentIconLogoPaypalComponent],
    imports: [
        LoaderModule,
        PopupModule,
        TranslateModule,
        ButtonModule,
        FormsModule,
        CommonModule,
        CheckboxModule
    ],
    exports: [
        PaymentMethodComponent
    ]
})
export class PaymentMethodModule {
}
