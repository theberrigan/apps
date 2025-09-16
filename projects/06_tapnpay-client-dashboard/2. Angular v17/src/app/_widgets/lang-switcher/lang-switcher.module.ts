import {NgModule} from '@angular/core';
import {CommonModule} from '@angular/common';
import {LangSwitcherComponent} from "./lang-switcher/lang-switcher.component";


@NgModule({
    declarations: [LangSwitcherComponent],
    exports: [
        LangSwitcherComponent
    ],
    imports: [
        CommonModule
    ]
})
export class LangSwitcherModule {
}
