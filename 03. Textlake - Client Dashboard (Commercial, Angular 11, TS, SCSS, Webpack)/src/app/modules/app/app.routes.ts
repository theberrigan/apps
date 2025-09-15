import { NgModule }             from '@angular/core';
import { CommonModule  }        from '@angular/common';
import { Routes, RouterModule } from '@angular/router';
import { NotFoundComponent }    from './not-found/not-found.component';

export const routes : Routes = [
    {
        path: 'dashboard',
        redirectTo: '/dashboard/orders',
        pathMatch: 'full'
    },
    {
        path: 'payments',
        loadChildren: () => import('../payments/payments.module').then(m => m.PaymentsModule)
    },
    {
        path: 'auth',
        loadChildren: () => import('../auth/auth.module').then(m => m.AuthModule)
    },
    {
        path: 'dashboard',
        loadChildren: () => import('../dashboard/dashboard.module').then(m => m.DashboardModule)
    },
    {
        path: '**',
        component: NotFoundComponent
    }
];

@NgModule({
    imports: [
        CommonModule,
        RouterModule.forRoot(routes)
    ],
    exports: [
        RouterModule
    ]
})
export class AppRoutes {}
