import {NgModule} from '@angular/core';
import {CommonModule} from '@angular/common';
import {FleetLpnRegisterComponent} from './modals-components/fleet-lpn-register/fleet-lpn-register.component';
import {PopupModule} from "../_widgets/popup/popup.module";
import {LpnCardModule} from "./modals-components/fleet-lpn-register/lpn-card/lpn-card.module";
import {ButtonModule} from "../_widgets/button/button.module";
import {TranslateModule} from "@ngx-translate/core";
import {ReactiveFormsModule} from "@angular/forms";
import {SharedModule} from "../_shared/shared.module";
import {MainPipesModule} from "../_shared/main-pipes/main-pipes.module";
import { NewTestModalComponent } from './modals-components/new-test-modal/new-test-modal.component';
import { JustTestComponent } from './modals-components/just-test/just-test.component';



@NgModule({
    declarations: [
        FleetLpnRegisterComponent,
        NewTestModalComponent,
        JustTestComponent,
    ],
    imports: [
        CommonModule,
        PopupModule,
        LpnCardModule,
        ButtonModule,
        TranslateModule,
        ReactiveFormsModule,
        SharedModule,
        MainPipesModule,
    ]
})
export class ModalsModule {
}
