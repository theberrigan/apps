import {NgModule} from '@angular/core';
import {Routes, RouterModule} from '@angular/router';
import {NotFoundComponent} from './not-found/not-found.component';
import {TermsComponent} from './terms/terms.component';
import {AuthComponent} from './auth/auth.component';
import {AuthGuard} from './guards/auth.guard';
import {AutoAuthComponent} from './auth/auto-auth/auto-auth.component';
import { NavMobileLogoutConfirmComponent } from './nav-mobile-logout-confirm/nav-mobile-logout-confirm.component';
import { EmailVerificationComponent } from './email-verification/email-verification.component';

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
        path: 'faq',
        loadChildren: () => import('./faq/faq.module').then(m => m.FaqModule),
    },
    {
        path: 'contact-us',
        loadChildren: () => import('./contact-us/contact-us.module').then(m => m.ContactUsModule),
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
        loadChildren: () => import('./dashboard/dashboard.module').then(m => m.DashboardModule),
    },
    {
        path: 'dashboard/logout-confirm',
        component: NavMobileLogoutConfirmComponent
    },
    {
        path: 'email-verification/confirm-verify-email/:token',
        component: EmailVerificationComponent
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
export class AppRoutingModule {
}
