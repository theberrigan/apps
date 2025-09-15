import {NgModule} from '@angular/core';
import {CommonModule} from '@angular/common';
import {DatepickerComponent} from "./datepicker.component";
import {TodayDateSelectComponent} from "./today-date-select/today-date-select.component";
import {TranslateModule} from "@ngx-translate/core";
import {FormsModule} from "@angular/forms";
import {ButtonModule} from "../button/button.module";


@NgModule({
    declarations: [DatepickerComponent, TodayDateSelectComponent],
    imports: [
        CommonModule,
        TranslateModule,
        FormsModule,
        ButtonModule
    ],
    exports: [
        DatepickerComponent]
})
export class DatepickerModule {
}
