import {NgModule} from '@angular/core';
import {CommonModule} from '@angular/common';
import {LpnCardComponent} from "./lpn-card.component";
import {SharedModule} from "../../../../_shared/shared.module";
import {DatepickerModule} from "../../../../_widgets/datepicker/datepicker.module";
import {TimepickerModule} from "../../../../_widgets/timepicker/timepicker.module";
import {CheckboxModule} from "../../../../_widgets/checkbox/checkbox.module";
import {MainPipesModule} from "../../../../_shared/main-pipes/main-pipes.module";
import {ValidationMessageModule} from "../../../../_shared/validation-message/validation-message.module";


@NgModule({
    declarations: [LpnCardComponent],
    imports: [
        CommonModule,
        SharedModule,
        DatepickerModule,
        TimepickerModule,
        CheckboxModule,
        MainPipesModule,
        ValidationMessageModule
    ],
    exports: [
        LpnCardComponent
    ]
})
export class LpnCardModule {
}
