import {NgModule} from '@angular/core';
import {CommonModule} from '@angular/common';
import {CheckboxStaticComponent} from "./checkbox-static/checkbox-static.component";


@NgModule({
    declarations: [CheckboxStaticComponent],
    imports: [
        CommonModule
    ],
    exports: [CheckboxStaticComponent]
})
export class CheckboxStaticModule {
}
