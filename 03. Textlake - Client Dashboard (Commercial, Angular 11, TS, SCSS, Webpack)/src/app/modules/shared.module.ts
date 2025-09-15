import { NgModule, ModuleWithProviders } from '@angular/core';
import { TranslateModule }               from '@ngx-translate/core';
import { CyPipe }                        from '../pipes/cy.pipe';
import { MaximizeDirective } from '../directives/maximize.directive';
import {FormsModule, ReactiveFormsModule} from '@angular/forms';
import {DatetimeService2} from '../services/datetime-service2.service';
import {DatetimeService} from '../services/datetime.service';
import {FormatDatePipe} from '../pipes/fdate.pipe';
import {CommonModule} from '@angular/common';
import {RouterModule} from '@angular/router';
import {HttpClientModule} from '@angular/common/http';
import {MenuComponent} from '../widgets/menu/menu.component';
import {PopupManagerComponent} from '../widgets/popup/popup-manager.component';
import {PopupComponent} from '../widgets/popup/popup.component';
import {PopupBoxComponent} from '../widgets/popup/popup-box.component';
import {PopupHeaderComponent} from '../widgets/popup/popup-header.component';
import {PopupContentComponent} from '../widgets/popup/popup-content.component';
import {PopupControlsComponent} from '../widgets/popup/popup-controls.component';
import {ConfirmComponent} from '../widgets/popup/confirm/confirm.component';
import {AlertComponent} from '../widgets/popup/alert/alert.component';
import {TermsComponent} from '../widgets/terms/terms.component';
import {CheckboxComponent} from '../widgets/checkbox/checkbox.component';
import {SpinnerComponent} from '../widgets/spinner/spinner.component';
import {ButtonComponent} from '../widgets/button/button.component';
import {DatepickerComponent} from '../widgets/datepicker/datepicker.component';
import {PaginationComponent} from '../widgets/pagination/pagination.component';
import {SortSelectComponent} from './shared/sort-select/sort-select.component';
import {ListViewComponent} from './shared/list-view/list-view.component';
import {ToastManagerComponent} from '../widgets/toast/toast-manager.component';
import {ToastComponent} from '../widgets/toast/toast.component';
import {InputDirective} from '../widgets/input.directive';
import {ScrollbarDirective} from '../directives/scrollbar.directive';
import {NumberMaskDirective} from '../directives/number-mask.directive';
import {DatetimePipe} from '../pipes/datetime.pipe';
import {SafeStylePipe} from '../pipes/safe-style.pipe';
import {TooltipModule} from 'ng2-tooltip-directive';

@NgModule({
    imports: [
        CommonModule,
        RouterModule,
        FormsModule,
        ReactiveFormsModule,
        HttpClientModule,
        TranslateModule,
        TooltipModule
    ],
    declarations: [
        MaximizeDirective,
        CyPipe,
        FormatDatePipe,

        MenuComponent,
        PopupComponent,
        PopupManagerComponent,
        PopupBoxComponent,
        PopupHeaderComponent,
        PopupContentComponent,
        PopupControlsComponent,
        ConfirmComponent,
        AlertComponent,
        TermsComponent,
        CheckboxComponent,
        SpinnerComponent,
        ButtonComponent,
        DatepickerComponent,
        PaginationComponent,
        SortSelectComponent,
        ListViewComponent,
        ToastManagerComponent,
        ToastComponent,

        // Directives
        InputDirective,
        ScrollbarDirective,
        NumberMaskDirective,

        // Pipes
        DatetimePipe,
        SafeStylePipe
    ],
    exports: [
        CommonModule,
        RouterModule,
        FormsModule,
        ReactiveFormsModule,
        HttpClientModule,
        MaximizeDirective,
        TranslateModule,
        CyPipe,
        FormatDatePipe,
        TooltipModule,

        MenuComponent,
        PopupComponent,
        PopupManagerComponent,
        PopupBoxComponent,
        PopupHeaderComponent,
        PopupContentComponent,
        PopupControlsComponent,
        ConfirmComponent,
        AlertComponent,
        TermsComponent,
        CheckboxComponent,
        SpinnerComponent,
        ButtonComponent,
        DatepickerComponent,
        PaginationComponent,
        SortSelectComponent,
        ListViewComponent,
        ToastManagerComponent,
        ToastComponent,

        // Directives
        InputDirective,
        ScrollbarDirective,
        NumberMaskDirective,

        // Pipes
        DatetimePipe,
        SafeStylePipe
    ],
    providers: [
        CyPipe,
        DatetimeService2,
        DatetimeService
    ]
})
export class SharedModule {
    static forRoot () : ModuleWithProviders<any> {
        return {
            ngModule: SharedModule,
            providers: []
        };
    }
}
