import { NgModule }      from '@angular/core';

import {ExperimentsComponent} from './experiments/experiments.component';
import {DashboardRoutingModule} from './dashboard-routing.module';
import {DashboardComponent} from './dashboard.component';
import {SharedModule} from '../shared.module';
import {OffersComponent} from './offers/offers.component';
import {ProjectsComponent} from './projects/projects.component';
import {MailboxComponent} from './mailbox/mailbox.component';
import {TranslatorsComponent} from './translators/translators.component';
import {ReportsComponent} from './reports/reports.component';
import {ClientsComponent} from './clients/clients.component';
import {SettingsComponent} from './settings/settings.component';
import {ActionPanelComponent} from '../shared/action-panel/action-panel.component';
import {NavigationComponent} from './navigation/navigation.component';
import {PanelComponent} from './panel/panel.component';
import {ProfileComponent} from './settings/profile/profile.component';
import { SidebarComponent } from '../shared/sidebar/sidebar.component';
import { SidebarTriggerComponent } from '../shared/sidebar/trigger/sidebar-trigger.component';
import { SidebarLabelComponent } from '../shared/sidebar/label/sidebar-label.component';
import {SidebarSectionComponent} from '../shared/sidebar/section/sidebar-section.component';
import {OfferComponent} from './offers/offer.component';

import { FileUploadModule } from '../../widgets/file-uploader/file-upload.module';
import {DiscardGuard} from '../../guards/discard.guard';
import {ClientComponent} from './clients/client.component';
import {ProjectEditorComponent} from './projects/project.component';
import {TranslatorEditorComponent} from './translators/translator.component';
import {TranslatorStatementsComponent} from './reports/translator-statements.component';
import {ProjectStatementsComponent} from './reports/project-statements.component';
import {CoordinatorStatementsComponent} from './reports/coordinator-statements.component';
import {ClientStatementsComponent} from './reports/client-statements.component';
import {MailboxSettingsComponent} from './settings/mailbox/mailbox.component';
import {RolesSettingsComponent} from './settings/roles/roles.component';
import {CurrenciesSettingsComponent} from './settings/currencies/currencies.component';
import {CompanySettingsComponent} from './settings/company/company.component';
import {ServicesSettingsComponent} from './settings/services/services.component';
import {RatesSettingsComponent} from './settings/rates/rates.component';
import {TaxesSettingsComponent} from './settings/taxes/taxes.component';
import {InvitationsSettingsComponent} from './settings/invitations/invitations.component';
import {PaymentProvidersSettingsComponent} from './settings/payment-providers/payment-providers.component';
import {SubscriptionsSettingsComponent} from './settings/subscriptions/subscriptions.component';
import {PlanComponent} from './plan/plan.component';
import {FundingSourceComponent} from '../../widgets/funding-source/funding-source.component';
import {ColorPickerComponent} from '../../widgets/color-picker/color-picker.component';
import {IsolatedViewComponent} from '../../widgets/isolated-view/isolated-view.component';
import {CalculationRulesComponent} from './settings/calculation-rules/calculation-rules.component';

@NgModule({
    imports: [
        SharedModule,
        DashboardRoutingModule,
        FileUploadModule
    ],
    exports: [],
    declarations: [
        DashboardComponent,
        NavigationComponent,
        PanelComponent,
        ActionPanelComponent,
        OffersComponent,
        OfferComponent,
        ProjectsComponent,
        ProjectEditorComponent,
        MailboxComponent,
        ClientsComponent,
        ClientComponent,
        TranslatorsComponent,
        TranslatorEditorComponent,
        ReportsComponent,
        TranslatorStatementsComponent,
        ProjectStatementsComponent,
        CoordinatorStatementsComponent,
        ClientStatementsComponent,
        ExperimentsComponent,
        ProfileComponent,
        SidebarComponent,
        SidebarSectionComponent,
        SidebarLabelComponent,
        SidebarTriggerComponent,
        SettingsComponent,
        MailboxSettingsComponent,
        RolesSettingsComponent,
        CurrenciesSettingsComponent,
        CompanySettingsComponent,
        CalculationRulesComponent,
        ServicesSettingsComponent,
        RatesSettingsComponent,
        TaxesSettingsComponent,
        InvitationsSettingsComponent,
        PaymentProvidersSettingsComponent,
        SubscriptionsSettingsComponent,
        PlanComponent,
        FundingSourceComponent,
        ColorPickerComponent,
        IsolatedViewComponent
    ],
    providers: [
        DiscardGuard
    ]
})
export class DashboardModule {}
