import {NgModule} from '@angular/core';
import {CommonModule} from '@angular/common';
import {PagePanelComponent} from "./page-panel/page-panel.component";
import {TranslateModule} from "@ngx-translate/core";
import {RouterModule} from "@angular/router";
import {UserMainInfoModule} from "../user-main-info/user-main-info.module";


@NgModule({
    declarations: [PagePanelComponent],
    imports: [
        CommonModule,
        TranslateModule,
        RouterModule,
        UserMainInfoModule
    ],
    exports: [
        PagePanelComponent
    ]
})
export class PagePanelModule {
}
