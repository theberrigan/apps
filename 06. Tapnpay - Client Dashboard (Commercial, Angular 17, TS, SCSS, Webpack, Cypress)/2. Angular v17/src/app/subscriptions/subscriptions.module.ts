import {NgModule} from '@angular/core';
import {CommonModule} from '@angular/common';
import {SubscriptionSelectComponent} from './subscription-select/subscription-select.component';
import {ButtonModule} from "../_widgets/button/button.module";
import {LpnCardModule} from "../_modals/modals-components/fleet-lpn-register/lpn-card/lpn-card.module";
import {SharedModule} from "../_shared/shared.module";
import {TranslateModule} from "@ngx-translate/core";
import {PopupModule} from "../_widgets/popup/popup.module";
import { SubscriptionPaymentPreviewComponent } from './subscription-payment-preview/subscription-payment-preview.component';
import { SubscriptionAcknowledgementComponent } from './subscription-acknowledgement/subscription-acknowledgement.component';
import { SubscriptionItemComponent } from './subscription-select/subscription-item/subscription-item.component';
import {MainPipesModule} from "../_shared/main-pipes/main-pipes.module";
import { RegistrationWelcomeComponent } from './registration-welcome/registration-welcome.component';
import { ReactiveFormsModule } from '@angular/forms';


@NgModule({
    declarations: [
        SubscriptionSelectComponent,
        SubscriptionPaymentPreviewComponent,
        SubscriptionAcknowledgementComponent,
        SubscriptionItemComponent,
        RegistrationWelcomeComponent
    ],
    imports: [
        CommonModule,
        ButtonModule,
        LpnCardModule,
        SharedModule,
        TranslateModule,
        PopupModule,
        MainPipesModule,
        ReactiveFormsModule
    ],
})
export class SubscriptionsModule {
}
