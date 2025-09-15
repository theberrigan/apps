import { NgModule }                from '@angular/core';
import { CommonModule  }           from '@angular/common';
import { Routes, RouterModule }    from '@angular/router';
import { PaymentsComponent }       from './payments.component';
import { PaymentsResultComponent } from './payments-result.component';

export const routes : Routes = [
    {
        path: 'result/:status',
        component: PaymentsResultComponent
    },
    {
        path: ':quoteId',
        component: PaymentsComponent
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
export class PaymentsRoutes {}