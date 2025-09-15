import { NgModule } from '@angular/core';
import { Routes, RouterModule } from '@angular/router';
import { NotFoundComponent } from './not-found/not-found.component';
import {TermsComponent} from './terms/terms.component';
import {FaqComponent} from './faq/faq.component';
import {ContactUsComponent} from './contact-us/contact-us.component';
import {AuthComponent} from './auth/auth.component';
import {DashboardComponent} from './dashboard/dashboard.component';
import {InvoicesComponent} from './dashboard/invoices/invoices.component';
import {ProfileComponent} from './dashboard/profile/profile.component';
import {HistoryComponent} from './dashboard/history/history.component';
import {AuthGuard} from '../../guards/auth.guard';
import {FaqDashboardComponent} from './dashboard/faq-dashboard/faq-dashboard.component';
import {ContactUsDashboardComponent} from './dashboard/contact-us-dashboard/contact-us-dashboard.component';
import {TermsDashboardComponent} from './dashboard/terms-dashboard/terms-dashboard.component';
import {VehiclesComponent} from './dashboard/profile/vehicles/vehicles.component';
import {InvoiceHistoryComponent} from './dashboard/history/invoice-history/invoice-history.component';
import {AutoAuthComponent} from './auth/auto-auth/auto-auth.component';
import {CanDeactivateGuard} from '../../guards/can-deactivate.guard';
import {CoverageComponent} from './dashboard/coverage/coverage.component';
import {CoverageGuard} from '../../guards/coverage.guard';

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
        path: 'login/:token',
        redirectTo: '/auth/:token',
        pathMatch: 'full'
    },
    {
        path: 'sign-in/:token',
        redirectTo: '/auth/:token',
        pathMatch: 'full'
    },
    {
        path: 'sign-up/:token',
        redirectTo: '/auth/:token',
        pathMatch: 'full'
    },
    {
        path: 'register/:token',
        redirectTo: '/auth/:token',
        pathMatch: 'full'
    },
    {
        path: 'dashboard',
        redirectTo: '/dashboard/invoices',
        pathMatch: 'full'
    },
    {
        path: 'terms',
        component: TermsComponent,
        canActivate: [
            AuthGuard
        ],
    },
    {
        path: 'terms/:phone',
        component: TermsComponent,
    },
    {
        path: 'faq/:id',
        component: FaqComponent,
    },
    {
        path: 'faq',
        component: FaqComponent,
    },
    {
        path: 'contact-us',
        component: ContactUsComponent,
    },
    {
        path: 'not-found',
        component: NotFoundComponent
    },
    {
        path: 'auth/:token',
        component: AutoAuthComponent
    },
    {
        path: 'auth',
        component: AuthComponent
    },
    {
        path: 'dashboard',
        component: DashboardComponent,
        canActivate: [
            AuthGuard
        ],
        canActivateChild: [
            AuthGuard
        ],
        children: [
            {
                path: 'profile/vehicles',
                component: VehiclesComponent,
            },
            {
                path: 'profile',
                component: ProfileComponent,
            },
            {
                path: 'invoices',
                component: InvoicesComponent,
                canDeactivate: [
                    CanDeactivateGuard
                ]
            },
            {
                path: 'history/invoice/:id',
                component: InvoiceHistoryComponent,
            },
            {
                path: 'history',
                component: HistoryComponent,
            },
            {
                path: 'faq/:id',
                component: FaqDashboardComponent,
            },
            {
                path: 'faq',
                component: FaqDashboardComponent,
            },
            {
                path: 'contact-us',
                component: ContactUsDashboardComponent,
            },
            {
                path: 'terms',
                component: TermsDashboardComponent,
            },
            {
                path: 'coverage',
                component: CoverageComponent,
                canActivate: [
                    CoverageGuard
                ],
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
