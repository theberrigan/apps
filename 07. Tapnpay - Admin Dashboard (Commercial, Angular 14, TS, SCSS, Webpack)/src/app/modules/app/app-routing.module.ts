import { NgModule } from '@angular/core';
import { Routes, RouterModule } from '@angular/router';
import { NotFoundComponent } from './not-found/not-found.component';
import {AuthComponent} from './auth/auth.component';
import {DashboardComponent} from './dashboard/dashboard.component';
import {AuthGuard} from '../../guards/auth.guard';
import {CanDeactivateGuard} from '../../guards/can-deactivate.guard';
import {AccountsComponent} from './dashboard/accounts/accounts.component';
import {AccountsGuard} from '../../guards/accounts.guard';
import {FAQComponent} from './dashboard/faq/faq.component';
import {FaqGuard} from '../../guards/faq.guard';
import {CoverageComponent} from './dashboard/coverage/coverage.component';
import {TAListComponent} from './dashboard/ta/ta-list.component';
import {TAEditorComponent} from './dashboard/ta/ta-editor.component';
import {CoverageGuard} from '../../guards/coverage.guard';
import {TAListGuard} from '../../guards/ta-list.guard';
import {TAEditorGuard} from '../../guards/ta-editor.guard';
import {CarrierContractListComponent} from './dashboard/contracts/carrier-contract-list.component';
import {CarrierContractComponent} from './dashboard/contracts/carrier-contract.component';
import {TAContractListComponent} from './dashboard/contracts/ta-contract-list.component';
import {TAContractComponent} from './dashboard/contracts/ta-contract.component';
import {PGContractListComponent} from './dashboard/contracts/pg-contract-list.component';
import {PGContractComponent} from './dashboard/contracts/pg-contract.component';
import {CarrierContractListGuard} from '../../guards/carrier-contract-list.guard';
import {CarrierContractGuard} from '../../guards/carrier-contract.guard';
import {TAContractListGuard} from '../../guards/ta-contract-list.guard';
import {TAContractGuard} from '../../guards/ta-contract.guard';
import {PGContractListGuard} from '../../guards/pg-contract-list.guard';
import {PGContractGuard} from '../../guards/pg-contract.guard';
import {DisputesComponent} from './dashboard/disputes/disputes.component';
import {DisputesGuard} from '../../guards/disputes.guard';

const routes: Routes = [
    {
        path: '',
        redirectTo: '/auth',
        pathMatch: 'full'
    },
    {
        path: 'login',
        redirectTo: '/auth',
        pathMatch: 'full'
    },
    {
        path: 'sign-in',
        redirectTo: '/auth',
        pathMatch: 'full'
    },
    {
        path: 'sign-up',
        redirectTo: '/auth',
        pathMatch: 'full'
    },
    {
        path: 'register',
        redirectTo: '/auth',
        pathMatch: 'full'
    },
    {
        path: 'dashboard',
        redirectTo: '/dashboard/accounts',
        pathMatch: 'full'
    },
    {
        path: 'not-found',
        component: NotFoundComponent
    },
    {
        path: 'auth',
        component: AuthComponent
    },
    {
        path: 'dashboard',
        component: DashboardComponent,
        canActivate: [ AuthGuard ],
        canActivateChild: [ AuthGuard ],
        children: [
            {
                path: 'accounts/:accountId',
                component: AccountsComponent,
                canActivate: [ AccountsGuard ],
                canActivateChild: [ AccountsGuard ],
            },
            {
                path: 'accounts',
                component: AccountsComponent,
                canActivate: [ AccountsGuard ],
                canActivateChild: [ AccountsGuard ],
            },
            {
                path: 'faq',
                component: FAQComponent,
                canActivate: [ FaqGuard ],
                canActivateChild: [ FaqGuard ],
            },
            {
                path: 'coverage',
                component: CoverageComponent,
                canActivate: [ CoverageGuard ],
                canActivateChild: [ CoverageGuard ],
            },
            {
                path: 'toll-authorities/:id',
                component: TAEditorComponent,
                canActivate: [ TAEditorGuard ],
                canActivateChild: [ TAEditorGuard ],
                canDeactivate: [ CanDeactivateGuard ],
            },
            {
                path: 'toll-authorities',
                component: TAListComponent,
                canActivate: [ TAListGuard ],
                canActivateChild: [ TAListGuard ],
            },

            // -------------------------

            {
                path: 'contracts/carriers',
                component: CarrierContractListComponent,
                canActivate: [ CarrierContractListGuard ],
                canActivateChild: [ CarrierContractListGuard ],
            },
            {
                path: 'contracts/carrier/:id',
                component: CarrierContractComponent,
                canActivate: [ CarrierContractGuard ],
                canActivateChild: [ CarrierContractGuard ],
            },
            {
                path: 'contracts/carrier',
                component: CarrierContractComponent,
                canActivate: [ CarrierContractGuard ],
                canActivateChild: [ CarrierContractGuard ],
            },
            {
                path: 'contracts/toll-authorities',
                component: TAContractListComponent,
                canActivate: [ TAContractListGuard ],
                canActivateChild: [ TAContractListGuard ],
            },
            {
                path: 'contracts/toll-authority/:id',
                component: TAContractComponent,
                canActivate: [ TAContractGuard ],
                canActivateChild: [ TAContractGuard ],
            },
            {
                path: 'contracts/toll-authority',
                component: TAContractComponent,
                canActivate: [ TAContractGuard ],
                canActivateChild: [ TAContractGuard ],
            },
            {
                path: 'contracts/payment-gateways',
                component: PGContractListComponent,
                canActivate: [ PGContractListGuard ],
                canActivateChild: [ PGContractListGuard ],
            },
            {
                path: 'contracts/payment-gateway/:id',
                component: PGContractComponent,
                canActivate: [ PGContractGuard ],
                canActivateChild: [ PGContractGuard ],
            },
            {
                path: 'contracts/payment-gateway',
                component: PGContractComponent,
                canActivate: [ PGContractGuard ],
                canActivateChild: [ PGContractGuard ],
            },

            // -------------------------

            {
                path: 'disputes',
                component: DisputesComponent,
                canActivate: [ DisputesGuard ],
                canActivateChild: [ DisputesGuard ],
            },
        ]
    },
    {
        path: '**',
        component: NotFoundComponent
    }
];

@NgModule({
    imports: [
        RouterModule.forRoot(routes)
    ],
    exports: [
        RouterModule
    ]
})
export class AppRoutingModule {}
