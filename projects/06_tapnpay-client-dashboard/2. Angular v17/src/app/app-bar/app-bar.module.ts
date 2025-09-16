import {NgModule} from '@angular/core';
import {CommonModule} from '@angular/common';
import {AppBarComponent} from "./app-bar.component";
import {LogoNeorideModule} from "../logo-neoride/logo-neoride.module";


@NgModule({
    declarations: [AppBarComponent],
    imports: [
        CommonModule,
        LogoNeorideModule
    ],
    exports: [AppBarComponent]
})
export class AppBarModule {
}
