import {NgModule} from '@angular/core';
import {CommonModule} from '@angular/common';
import {CurrencyFormatPipe} from "../../pipes/currencyFormat.pipe";
import {DatetimePipe} from "../../pipes/datetime.pipe";


@NgModule({
    declarations: [
        CurrencyFormatPipe,
        DatetimePipe,
    ],
    imports: [
        CommonModule
    ],
    exports: [
        CurrencyFormatPipe,
        DatetimePipe,
    ]
})
export class MainPipesModule {
}
