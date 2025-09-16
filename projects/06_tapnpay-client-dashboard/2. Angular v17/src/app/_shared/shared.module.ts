import {CommonModule} from '@angular/common';
import {RouterModule} from '@angular/router';
import {NgModule} from "@angular/core";
import {FormsModule, ReactiveFormsModule} from '@angular/forms';
import {TranslateModule} from '@ngx-translate/core';
import {provideHttpClient, withInterceptorsFromDi} from '@angular/common/http';
import {ToastComponent} from '../_widgets/toast/toast.component';
import {ToastManagerComponent} from '../_widgets/toast/toast-manager.component';
import {MainPipesModule} from "./main-pipes/main-pipes.module";


@NgModule({
    declarations: [
        ToastComponent,
        ToastManagerComponent,
        // Directives
    ],
    exports: [
        // Modules
        CommonModule,
        RouterModule,
        ReactiveFormsModule,
        FormsModule,
        TranslateModule,
        // Components
        ToastComponent,
        ToastManagerComponent,
        // Directives
        // Pipes
    ], imports: [CommonModule,
        RouterModule,
        ReactiveFormsModule,
        FormsModule,
        TranslateModule,
        MainPipesModule], providers: [provideHttpClient(withInterceptorsFromDi())]
})
export class SharedModule {
}
