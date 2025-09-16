import {NgModule} from '@angular/core';
import {CommonModule} from '@angular/common';
import {FaqComponent} from "./faq/faq.component";
import {RouterModule, Routes} from "@angular/router";
import {TranslateModule} from "@ngx-translate/core";
import {HelpPageModule} from "../help-page/help-page.module";
import {FaqInnerModule} from "../_shared/faq-inner/faq-inner.module";

const routes: Routes = [
    {
        path: '',
        component: FaqComponent,
    },
    {
        path: ':id',
        component: FaqComponent,
    }
];

@NgModule({
    declarations: [FaqComponent],
    imports: [
        CommonModule,
        RouterModule.forChild(routes),
        TranslateModule,
        HelpPageModule,
        FaqInnerModule
    ]
})
export class FaqModule {
}
