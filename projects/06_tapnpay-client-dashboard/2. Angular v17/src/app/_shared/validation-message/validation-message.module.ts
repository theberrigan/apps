import {NgModule} from '@angular/core';
import {CommonModule} from '@angular/common';
import {ValidationErrorsComponent} from "./validation-errors.component";
import {TranslateModule} from "@ngx-translate/core";
import {MainPipesModule} from "../main-pipes/main-pipes.module";


@NgModule({
    declarations: [ValidationErrorsComponent],
    imports: [
        CommonModule,
        TranslateModule,
        MainPipesModule,
    ],
    exports: [
        ValidationErrorsComponent
    ]
})
export class ValidationMessageModule {
}
