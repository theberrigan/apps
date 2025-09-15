import {NgModule} from '@angular/core';
import {CommonModule} from '@angular/common';
import {ContactUsComponent} from "./contact-us/contact-us.component";
import {RouterModule, Routes} from "@angular/router";
import {HelpPageModule} from "../help-page/help-page.module";
import {TranslateModule} from "@ngx-translate/core";
import {ContactUsInnerModule} from "../_shared/contact-us-inner/contact-us-inner.module";

const routes: Routes = [
    {
        path: '',
        component: ContactUsComponent,
    }
];

@NgModule({
    declarations: [ContactUsComponent],
    imports: [
        CommonModule,
        RouterModule.forChild(routes),
        HelpPageModule,
        TranslateModule,
        ContactUsInnerModule
    ]
})
export class ContactUsModule {
}
