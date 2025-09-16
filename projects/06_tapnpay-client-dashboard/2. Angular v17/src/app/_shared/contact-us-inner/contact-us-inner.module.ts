import {NgModule} from '@angular/core';
import {CommonModule} from '@angular/common';
import {ContactUsInnerComponent} from "./contact-us-inner/contact-us-inner.component";
import {ReactiveFormsModule} from "@angular/forms";
import {TranslateModule} from "@ngx-translate/core";
import {ButtonModule} from "../../_widgets/button/button.module";


@NgModule({
    declarations: [
        ContactUsInnerComponent
    ],
    exports: [
        ContactUsInnerComponent
    ],
    imports: [
        CommonModule,
        ReactiveFormsModule,
        TranslateModule,
        ButtonModule
    ]
})
export class ContactUsInnerModule {
}
