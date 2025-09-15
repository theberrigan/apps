import { NgModule } from '@angular/core';
import { Routes, RouterModule } from '@angular/router';
import { NotFoundComponent } from './not-found/not-found.component';

const routes: Routes = [
    // {
    //     path: '',
    //     redirectTo: '/auth/sign-in',
    //     pathMatch: 'full'
    // },
    {
        path: 'auth',
        redirectTo: '/auth/sign-in',
        pathMatch: 'full'
    },
    {
        path: 'auth/login',
        redirectTo: '/auth/sign-in',
        pathMatch: 'full'
    },
    {
        path: 'login',
        redirectTo: '/auth/sign-in',
        pathMatch: 'full'
    },
    {
        path: 'auth/register',
        redirectTo: '/auth/sign-up',
        pathMatch: 'full'
    },
    {
        path: 'auth/reg',
        redirectTo: '/auth/sign-up',
        pathMatch: 'full'
    },
    {
        path: 'register',
        redirectTo: '/auth/sign-up',
        pathMatch: 'full'
    },
    {
        path: 'reg',
        redirectTo: '/auth/sign-up',
        pathMatch: 'full'
    },
    {
        path: 'dashboard',
        redirectTo: '/dashboard/offers',
        pathMatch: 'full'
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
        path: 'not-found',
        component: NotFoundComponent
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
