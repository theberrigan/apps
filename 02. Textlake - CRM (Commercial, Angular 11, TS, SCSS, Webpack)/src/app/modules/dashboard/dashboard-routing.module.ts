import { NgModule } from '@angular/core';
import { Routes, RouterModule } from '@angular/router';
import {ExperimentsComponent} from './experiments/experiments.component';
import {DashboardComponent} from './dashboard.component';
import {OffersComponent} from './offers/offers.component';
import {ProjectsComponent} from './projects/projects.component';
import {MailboxComponent} from './mailbox/mailbox.component';
import {ClientsComponent} from './clients/clients.component';
import {TranslatorsComponent} from './translators/translators.component';
import {ReportsComponent} from './reports/reports.component';
import {SettingsComponent} from './settings/settings.component';
import {AuthGuard} from '../../guards/auth.guard';
import {NavGuard} from '../../guards/nav.guard';
import {OfferComponent} from './offers/offer.component';
import {DiscardGuard} from '../../guards/discard.guard';
import {ClientComponent} from './clients/client.component';
import {ProjectEditorComponent} from './projects/project.component';
import {TranslatorEditorComponent} from './translators/translator.component';
import {ClientStatementsComponent} from './reports/client-statements.component';
import {CoordinatorStatementsComponent} from './reports/coordinator-statements.component';
import {ProjectStatementsComponent} from './reports/project-statements.component';
import {TranslatorStatementsComponent} from './reports/translator-statements.component';
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
import {CalculationRulesComponent} from './settings/calculation-rules/calculation-rules.component';

const routes : Routes = [
    {
        path: '',
        component: DashboardComponent,
        canActivate: [
            AuthGuard
        ],
        canActivateChild: [
            AuthGuard
        ],
        children: [
            {
                path: 'plan',
                component: PlanComponent
            },
            {
                path: 'offers',
                component: OffersComponent,
                canActivate: [
                    NavGuard
                ]
            },
            {
                path: 'offer/:key',
                component: OfferComponent,
                canDeactivate: [
                    DiscardGuard
                ]
            },
            {
                path: 'offers/:key',
                redirectTo: 'offer/:key',
                pathMatch: 'full'
            },
            {
                path: 'projects',
                component: ProjectsComponent,
                canActivate: [
                    NavGuard
                ]
            },
            {
                path: 'project/:key',
                component: ProjectEditorComponent,
                canDeactivate: [
                    DiscardGuard
                ]
            },
            {
                path: 'projects/:key',
                redirectTo: 'project/:key',
                pathMatch: 'full'
            },
            {
                path: 'mailbox',
                component: MailboxComponent,
                canActivate: [
                    NavGuard
                ]
            },
            {
                path: 'clients',
                component: ClientsComponent,
                canActivate: [
                    NavGuard
                ]
            },
            {
                path: 'client/:key',
                component: ClientComponent,
                canDeactivate: [
                    DiscardGuard
                ]
            },
            {
                path: 'clients/:key',
                redirectTo: 'client/:key',
                pathMatch: 'full'
            },
            {
                path: 'translators',
                component: TranslatorsComponent,
                canActivate: [
                    NavGuard
                ]
            },
            {
                path: 'translator/:key',
                component: TranslatorEditorComponent,
                canDeactivate: [
                    DiscardGuard
                ]
            },
            {
                path: 'translators/:key',
                redirectTo: 'translator/:key',
                pathMatch: 'full'
            },
            {
                path: 'reports/translator-statements',
                component: TranslatorStatementsComponent,
                canDeactivate: [
                    DiscardGuard
                ]
            },
            {
                path: 'reports/project-statements',
                component: ProjectStatementsComponent,
                canDeactivate: [
                    DiscardGuard
                ]
            },
            {
                path: 'reports/coordinator-statements',
                component: CoordinatorStatementsComponent
            },
            {
                path: 'reports/client-statements',
                component: ClientStatementsComponent,
                canDeactivate: [
                    DiscardGuard
                ]
            },
            {
                path: 'reports',
                component: ReportsComponent,
                canActivate: [
                    NavGuard
                ]
            },
            {
                path: 'billing/:key',
                redirectTo: 'reports/:key',
                pathMatch: 'full'
            },
            {
                path: 'settings',
                canActivate: [
                    NavGuard
                ],
                children: [
                    {
                        path: '',
                        component: SettingsComponent,
                    },
                    {
                        path: 'mailbox',
                        component: MailboxSettingsComponent,
                    },
                    {
                        path: 'roles',
                        component: RolesSettingsComponent,
                    },
                    {
                        path: 'currencies',
                        component: CurrenciesSettingsComponent,
                        canDeactivate: [
                            DiscardGuard
                        ],
                    },
                    {
                        path: 'company',
                        component: CompanySettingsComponent,
                        canDeactivate: [
                            DiscardGuard
                        ],
                    },
                    {
                        path: 'services',
                        component: ServicesSettingsComponent,
                    },
                    {
                        path: 'rates',
                        component: RatesSettingsComponent,
                    },
                    {
                        path: 'taxes',
                        component: TaxesSettingsComponent,
                    },
                    {
                        path: 'invitations',
                        component: InvitationsSettingsComponent,
                    },
                    {
                        path: 'payment-providers',
                        component: PaymentProvidersSettingsComponent,
                        canDeactivate: [
                            DiscardGuard
                        ],
                    },
                    {
                        path: 'subscriptions',
                        component: SubscriptionsSettingsComponent,
                        canDeactivate: [
                            DiscardGuard
                        ],
                    },
                    {
                        path: 'calculation-rules',
                        component: CalculationRulesComponent,
                        canDeactivate: [
                            DiscardGuard
                        ],
                    },
                ]
            },
            {
                path: 'experiments',
                component: ExperimentsComponent
            },
        ]
    }
];

@NgModule({
    imports: [
        RouterModule.forChild(routes)
    ],
    exports: [
        RouterModule
    ]
})
export class DashboardRoutingModule {}
