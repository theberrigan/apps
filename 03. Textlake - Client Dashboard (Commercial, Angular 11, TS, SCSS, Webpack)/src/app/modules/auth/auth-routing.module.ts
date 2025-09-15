import { NgModule } from '@angular/core';
import { Routes, RouterModule } from '@angular/router';
import {AuthComponent} from './auth.component';
// import {AuthGuard} from '../../guards/auth.guard';

const routes : Routes = [
    {
        path: ':action',
        component: AuthComponent,
        // canActivate: [
        //     AuthGuard
        // ],
        // canActivateChild: [
        //     AuthGuard
        // ]
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
export class AuthRoutingModule {}
