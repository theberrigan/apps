import {NgModule} from '@angular/core';
import {CommonModule} from '@angular/common';
import {RouterModule} from '@angular/router';
import {FormsModule, ReactiveFormsModule} from '@angular/forms';
import {TranslateModule} from '@ngx-translate/core';

// import {DropdownComponent} from '../widgets/dropdown/dropdown.component';
// import {DropdownGroupComponent} from '../widgets/dropdown/dropdown-group.component';
// import {DropdownItemComponent} from '../widgets/dropdown/dropdown-item.component';
// import {DropdownLabelComponent} from '../widgets/dropdown/dropdown-label.component';
import {MenuComponent} from '../widgets/menu/menu.component';
import {HttpClientModule} from '@angular/common/http';
import {PopupComponent} from '../widgets/popup/popup.component';
import {PopupManagerComponent} from '../widgets/popup/popup-manager.component';
import {PopupBoxComponent} from '../widgets/popup/popup-box.component';
import {PopupHeaderComponent} from '../widgets/popup/popup-header.component';
import {PopupContentComponent} from '../widgets/popup/popup-content.component';
import {PopupControlsComponent} from '../widgets/popup/popup-controls.component';
import {ConfirmComponent} from '../widgets/popup/confirm/confirm.component';
import {AlertComponent} from '../widgets/popup/alert/alert.component';
import {CheckboxComponent} from '../widgets/checkbox/checkbox.component';
import {TermsComponent} from '../widgets/terms/terms.component';
import {SpinnerComponent} from '../widgets/spinner/spinner.component';
import {ButtonComponent} from '../widgets/button/button.component';
import {BrowserAnimationsModule} from '@angular/platform-browser/animations';
import {ScrollbarDirective} from '../directives/scrollbar.directive';
import {DatepickerComponent} from '../widgets/datepicker/datepicker.component';
import {InputDirective} from '../widgets/input.directive';
import {DatetimePipe} from '../pipes/datetime.pipe';
import {PaginationComponent} from '../widgets/pagination/pagination.component';
import {SortSelectComponent} from './shared/sort-select/sort-select.component';
import {ListViewComponent} from './shared/list-view/list-view.component';
import {NumberMaskDirective} from '../directives/number-mask.directive';
import {TranslatorsColorPickerComponent} from './dashboard/translators/translators-color-picker.component';
import {ToastManagerComponent} from '../widgets/toast/toast-manager.component';
import {ToastComponent} from '../widgets/toast/toast.component';
import {TooltipModule} from 'ng2-tooltip-directive';
import {SafeStylePipe} from '../pipes/safe-style.pipe';


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
        // Components
        // DropdownComponent,
        // DropdownGroupComponent,
        // DropdownLabelComponent,
        // DropdownItemComponent,
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
        TranslatorsColorPickerComponent,
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
        // Modules
        CommonModule,
        RouterModule,
        ReactiveFormsModule,
        HttpClientModule,
        FormsModule,
        TranslateModule,
        TooltipModule,
        // BrowserAnimationsModule,

        // Components
        // DropdownComponent,
        // DropdownGroupComponent,
        // DropdownLabelComponent,
        // DropdownItemComponent,
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
        TranslatorsColorPickerComponent,
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
    entryComponents: [

    ],
    providers: []
})
export class SharedModule {}
