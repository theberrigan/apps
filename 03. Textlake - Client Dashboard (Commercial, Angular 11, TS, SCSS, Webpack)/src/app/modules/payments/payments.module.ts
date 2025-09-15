import { NgModule }                from '@angular/core';
import { CommonModule  }           from '@angular/common';
import { RouterModule }            from '@angular/router';
import { PaymentsRoutes }          from './payments.routes';
import { PaymentsComponent }       from './payments.component';
import { PaymentsResultComponent } from './payments-result.component';
import { SharedModule }            from '../shared.module';
import {FormsModule, ReactiveFormsModule} from '@angular/forms';

@NgModule({
    imports: [
        SharedModule,
        PaymentsRoutes
    ],
    exports: [],
    declarations: [
        PaymentsComponent,
        PaymentsResultComponent
    ],
    providers: []
})
export class PaymentsModule {}
