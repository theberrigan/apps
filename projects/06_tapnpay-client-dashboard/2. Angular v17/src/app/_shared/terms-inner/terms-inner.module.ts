import {NgModule} from '@angular/core';
import {CommonModule} from '@angular/common';
import {TermsInnerComponent} from "./terms-inner.component";
import {TranslateModule} from "@ngx-translate/core";
import {SharedModule} from "../shared.module";
import {ButtonModule} from "../../_widgets/button/button.module";
import {LoaderModule} from "../../_widgets/loader/loader.module";
import {CheckboxModule} from "../../_widgets/checkbox/checkbox.module";


@NgModule({
    declarations: [TermsInnerComponent],
    imports: [
        CommonModule,
        TranslateModule,
        SharedModule,
        ButtonModule,
        LoaderModule,
        CheckboxModule
    ],
    exports: [TermsInnerComponent]
})
export class TermsInnerModule {
}
