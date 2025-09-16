import {NgModule} from '@angular/core';
import {CommonModule} from '@angular/common';
import {CoverageComponent} from "./coverage/coverage.component";
import {RouterModule} from "@angular/router";
import {FormsModule} from "@angular/forms";
import {PagePanelModule} from "../page-panel/page-panel.module";
import {AppBarModule} from "../../app-bar/app-bar.module";
import {TranslateModule} from "@ngx-translate/core";
import {LoaderModule} from "../../_widgets/loader/loader.module";

const routes = [
    {
        path: '',
        component: CoverageComponent
    }
];

@NgModule({
    declarations: [CoverageComponent],
    imports: [
        CommonModule,
        RouterModule.forChild(routes),
        FormsModule,
        PagePanelModule,
        AppBarModule,
        TranslateModule,
        LoaderModule,
    ]
})
export class CoverageModule {
}
