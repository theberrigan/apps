import {NgModule} from '@angular/core';
import {CommonModule} from '@angular/common';
import {RouterModule} from '@angular/router';
import {FormsModule, ReactiveFormsModule} from '@angular/forms';
import {TranslateModule} from '@ngx-translate/core';
import {HttpClientModule} from '@angular/common/http';
import {TooltipModule} from 'ng2-tooltip-directive';
import {CheckboxComponent} from './app/_widgets/checkbox/checkbox.component';
import {ButtonComponent} from './app/_widgets/button/button.component';
import {ToastComponent} from './app/_widgets/toast/toast.component';
import {ToastManagerComponent} from './app/_widgets/toast/toast-manager.component';
import {LoaderComponent} from './app/_widgets/loader/loader.component';
import {CurrencyPipe} from '../pipes/currency.pipe';
import {DatetimePipe} from '../pipes/datetime.pipe';
import {CheckboxStaticComponent} from './app/_widgets/checkbox-static/checkbox-static.component';
import {ContextPanelComponent} from './app/_widgets/context-panel/context-panel.component';
import {PopupComponent} from './app/_widgets/popup/popup.component';
import {PopupHeaderComponent} from './app/_widgets/popup/popup-header.component';
import {PopupContentComponent} from './app/_widgets/popup/popup-content.component';
import {PopupControlsComponent} from './app/_widgets/popup/popup-controls.component';
import {ConfirmBoxComponent} from './app/_widgets/popup/confirm-box/confirm-box.component';


@NgModule({
    imports: [
        CommonModule,
        RouterModule,
        ReactiveFormsModule,
        FormsModule,
        HttpClientModule,
        TranslateModule,
        TooltipModule,
    ],
    declarations: [
        CheckboxComponent,
        CheckboxStaticComponent,
        ButtonComponent,
        ToastComponent,
        ToastManagerComponent,
        LoaderComponent,
        ContextPanelComponent,
        PopupComponent,
        PopupHeaderComponent,
        PopupContentComponent,
        PopupControlsComponent,
        ConfirmBoxComponent,

        // Directives

        // Pipes
        CurrencyPipe,
        DatetimePipe,
    ],
    exports: [
        // Modules
        CommonModule,
        RouterModule,
        ReactiveFormsModule,
        HttpClientModule,
        FormsModule,
        TranslateModule,
        TooltipModule,

        // Components
        CheckboxComponent,
        CheckboxStaticComponent,
        ButtonComponent,
        ToastComponent,
        ToastManagerComponent,
        LoaderComponent,
        ContextPanelComponent,
        PopupComponent,
        PopupHeaderComponent,
        PopupContentComponent,
        PopupControlsComponent,
        ConfirmBoxComponent,

        // Directives

        // Pipes
        CurrencyPipe,
        DatetimePipe,
    ],
    entryComponents: [

    ],
    providers: []
})
export class SharedModule {}
