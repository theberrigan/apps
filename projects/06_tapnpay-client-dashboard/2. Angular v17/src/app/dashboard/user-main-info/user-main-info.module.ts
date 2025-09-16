import {NgModule} from '@angular/core';
import {CommonModule} from '@angular/common';
import {UserMainInfoComponent} from "./user-main-info.component";
import {RouterLink} from "@angular/router";
import {TranslateModule} from "@ngx-translate/core";


@NgModule({
    declarations: [UserMainInfoComponent],
    imports: [
        CommonModule,
        RouterLink,
        TranslateModule
    ],
    exports: [UserMainInfoComponent]
})
export class UserMainInfoModule {
}
