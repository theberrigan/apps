import {NgModule} from '@angular/core';
import {CommonModule} from '@angular/common';
import {SubscriptionLimitComponent} from "./subscription-limit.component";
import {PopupModule} from "../../_widgets/popup/popup.module";
import {TranslateModule} from "@ngx-translate/core";


@NgModule({
    declarations: [SubscriptionLimitComponent],
    exports: [
        SubscriptionLimitComponent
    ],
    imports: [
        CommonModule,
        PopupModule,
        TranslateModule
    ]
})
export class SubscriptionLimitsModule {
}
