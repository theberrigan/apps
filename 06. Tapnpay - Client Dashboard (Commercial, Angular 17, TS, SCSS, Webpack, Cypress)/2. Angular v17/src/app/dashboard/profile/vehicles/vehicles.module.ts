import {NgModule} from '@angular/core';
import {CommonModule} from '@angular/common';
import {ActionsHistoryComponent} from "./actions-history/actions-history.component";
import {LpnListCardComponent} from "./lpn-list-card/lpn-list-card.component";
import {LpnsListComponent} from "./lpns-list/lpns-list.component";
import {VehiclesComponent} from "./vehicles.component";
import {PagePanelModule} from "../../page-panel/page-panel.module";
import {AppBarModule} from "../../../app-bar/app-bar.module";
import {LoaderModule} from "../../../_widgets/loader/loader.module";
import {PopupModule} from "../../../_widgets/popup/popup.module";
import {ButtonModule} from "../../../_widgets/button/button.module";
import {FormsModule, ReactiveFormsModule} from "@angular/forms";
import {CheckboxModule} from "../../../_widgets/checkbox/checkbox.module";
import {DatepickerModule} from "../../../_widgets/datepicker/datepicker.module";
import {ValidationMessageModule} from "../../../_shared/validation-message/validation-message.module";
import {TimepickerModule} from "../../../_widgets/timepicker/timepicker.module";
import {TranslateModule} from "@ngx-translate/core";
import {SubscriptionLimitsModule} from "../../../subscriptions/subscription-limit/subscription-limits.module";
import {PaymentMethodModule} from "../../payment-method/payment-method.module";
import {MainPipesModule} from "../../../_shared/main-pipes/main-pipes.module";
import {ActionHistoryItemComponent} from "./actions-history/action-history-item/action-history-item.component";
import {RouterModule} from "@angular/router";
import {IsLicensePlateExpiredPipe} from './lpn-list-card/_pipes/is-license-plate-expired.pipe';
import {IsLicensePlateRentalPipe} from './lpn-list-card/_pipes/is-license-plate-rental.pipe';
import { NoItemsComponent } from './no-items/no-items.component';
import { IsListEmptyPipe } from './is-list-empty.pipe';

const routes = [
    {
        path: '',
        component: VehiclesComponent,
    },
];

@NgModule({
    declarations: [VehiclesComponent,
        ActionsHistoryComponent,
        ActionHistoryItemComponent,
        LpnListCardComponent,
        LpnsListComponent,
        IsLicensePlateExpiredPipe,
        IsLicensePlateRentalPipe,
        NoItemsComponent,
        IsListEmptyPipe
    ],
    imports: [
        CommonModule,
        PagePanelModule,
        AppBarModule,
        LoaderModule,
        PopupModule,
        ButtonModule,
        FormsModule,
        CheckboxModule,
        ReactiveFormsModule,
        DatepickerModule,
        ValidationMessageModule,
        TimepickerModule,
        TranslateModule,
        SubscriptionLimitsModule,
        PaymentMethodModule,
        MainPipesModule,
        RouterModule.forChild(routes)
    ]
})
export class VehiclesModule {
}
