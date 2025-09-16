import {NgModule} from '@angular/core';
import {CommonModule} from '@angular/common';
import {FaqInnerComponent} from "./faq-inner/faq-inner.component";
import {FormsModule} from "@angular/forms";
import {TranslateModule} from "@ngx-translate/core";
import {LoaderModule} from "../../_widgets/loader/loader.module";


@NgModule({
    declarations: [FaqInnerComponent],
    exports: [
        FaqInnerComponent
    ],
    imports: [
        CommonModule,
        FormsModule,
        TranslateModule,
        LoaderModule
    ]
})
export class FaqInnerModule {
}
