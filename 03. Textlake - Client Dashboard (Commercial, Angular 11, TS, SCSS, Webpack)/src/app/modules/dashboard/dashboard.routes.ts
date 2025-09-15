import { NgModule }             from '@angular/core';
import { CommonModule  }        from '@angular/common';
import { Routes, RouterModule } from '@angular/router';
import { DashboardComponent }   from './dashboard.component';
import {BillingComponent} from './billing/billing.component';
import {OrdersComponent} from './orders/orders.component';
import {OrderComponent} from './orders/order.component';

export const routes : Routes = [
    {
        path: '',
        component: DashboardComponent,
        children: [
            {
                path: '',
                redirectTo: 'orders',
                pathMatch: 'full'
            },
            {
                path: 'billing',
                redirectTo: 'billing/',
                pathMatch: 'full'
            },
            {
                path: 'billing/:tab',
                component: BillingComponent
            },
            {
                path: 'orders',
                component: OrdersComponent
            },
            {
                path: 'order/:key',
                component: OrderComponent
            }
        ]
    }
];

@NgModule({
    imports: [
        CommonModule,
        RouterModule.forChild(routes)
    ],
    exports: [
        RouterModule
    ]
})
export class DashboardRoutes {}
