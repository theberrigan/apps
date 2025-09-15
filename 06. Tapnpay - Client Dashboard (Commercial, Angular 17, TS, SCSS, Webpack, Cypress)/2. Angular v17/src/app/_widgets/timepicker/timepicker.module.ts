import {NgModule} from '@angular/core';
import {TimepickerComponent} from './timepicker/timepicker.component';
import {FormsModule} from "@angular/forms";
import {NgClass, NgForOf, NgIf} from "@angular/common";
import {ButtonModule} from "../button/button.module";
import {TranslateModule} from "@ngx-translate/core";


@NgModule({
    declarations: [
        TimepickerComponent
    ],
    exports: [
        TimepickerComponent
    ],
    imports: [
        FormsModule,
        NgIf,
        NgForOf,
        ButtonModule,
        NgClass,
        TranslateModule
    ]
})
export class TimepickerModule {
}
