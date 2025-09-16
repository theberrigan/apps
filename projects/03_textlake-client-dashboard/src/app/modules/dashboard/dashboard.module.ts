import { NgModule }           from '@angular/core';
import { CommonModule  }      from '@angular/common';
import { RouterModule }       from '@angular/router';
import { DashboardRoutes }    from './dashboard.routes';
import { DashboardComponent } from './dashboard.component';
import { SharedModule }       from '../shared.module';
import {FormsModule, ReactiveFormsModule} from '@angular/forms';
import {FileUploadModule} from '../../widgets/file-uploader/file-upload.module';
import {DiscardGuard} from '../../guards/discard.guard';
import {IsolatedViewComponent} from '../../widgets/isolated-view/isolated-view.component';
import {SidebarTriggerComponent} from '../shared/sidebar/trigger/sidebar-trigger.component';
import {SidebarLabelComponent} from '../shared/sidebar/label/sidebar-label.component';
import {SidebarSectionComponent} from '../shared/sidebar/section/sidebar-section.component';
import {SidebarComponent} from '../shared/sidebar/sidebar.component';
import {ActionPanelComponent} from '../shared/action-panel/action-panel.component';
import {NavigationComponent} from './navigation/navigation.component';
import {PanelComponent} from './panel/panel.component';
import {BillingComponent} from './billing/billing.component';
import {OrdersComponent} from './orders/orders.component';
import {OrderComponent} from './orders/order.component';
import {ProfileComponent} from './settings/profile/profile.component';

@NgModule({
    imports: [
        SharedModule,
        DashboardRoutes,
        FileUploadModule
    ],
    exports: [],
    declarations: [
        DashboardComponent,
        NavigationComponent,
        PanelComponent,
        ActionPanelComponent,
        ProfileComponent,
        SidebarComponent,
        SidebarSectionComponent,
        SidebarLabelComponent,
        SidebarTriggerComponent,
        IsolatedViewComponent,
        BillingComponent,
        OrdersComponent,
        OrderComponent
    ],
    providers: [
        DiscardGuard
    ]
})
export class DashboardModule {}
