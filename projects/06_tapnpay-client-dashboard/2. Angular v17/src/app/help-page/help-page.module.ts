import {NgModule} from '@angular/core';
import {CommonModule} from '@angular/common';
import {HelpPageComponent} from "./help-page/help-page.component";
import {TranslateModule} from "@ngx-translate/core";
import {RouterLink} from "@angular/router";
import {AppBarModule} from "../app-bar/app-bar.module";
import {LangSwitcherModule} from "../_widgets/lang-switcher/lang-switcher.module";


@NgModule({
    declarations: [HelpPageComponent],
    exports: [
        HelpPageComponent
    ],
    imports: [
        CommonModule,
        TranslateModule,
        RouterLink,
        AppBarModule,
        LangSwitcherModule,
    ]
})
export class HelpPageModule {
}
