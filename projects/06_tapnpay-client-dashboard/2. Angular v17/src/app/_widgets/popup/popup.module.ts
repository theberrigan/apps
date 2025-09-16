import {NgModule} from '@angular/core';
import {CommonModule} from '@angular/common';
import {PopupComponent} from "./popup/popup.component";
import {PopupHeaderComponent} from "./popup-header/popup-header.component";
import {PopupContentComponent} from "./popup-content/popup-content.component";
import {PopupControlsComponent} from "./popup-controls/popup-controls.component";
import {ConfirmBoxComponent} from "./confirm-box/confirm-box.component";
import {TranslateModule} from "@ngx-translate/core";


@NgModule({
    declarations: [
        PopupComponent,
        PopupHeaderComponent,
        PopupContentComponent,
        PopupControlsComponent,
        ConfirmBoxComponent,
    ],
    imports: [
        CommonModule,
        TranslateModule
    ],
    exports: [
        PopupComponent,
        PopupContentComponent,
        PopupControlsComponent,
        PopupHeaderComponent,
        ConfirmBoxComponent
    ]
})
export class PopupModule {
}
