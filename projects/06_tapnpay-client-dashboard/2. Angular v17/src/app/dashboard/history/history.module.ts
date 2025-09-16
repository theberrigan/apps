import {NgModule} from '@angular/core';
import {CommonModule} from '@angular/common';
import {HistoryComponent} from "./history/history.component";
import {InvoiceHistoryComponent} from "./invoices/invoice-history/invoice-history.component";
import {RouterModule, Routes} from "@angular/router";
import {GoogleMapModule} from "../../_widgets/google-map/google-map.module";
import {TranslateModule} from "@ngx-translate/core";
import {MainPipesModule} from "../../_shared/main-pipes/main-pipes.module";
import {PagePanelModule} from "../page-panel/page-panel.module";
import {AppBarModule} from "../../app-bar/app-bar.module";
import {LoaderModule} from "../../_widgets/loader/loader.module";
import {DatepickerModule} from "../../_widgets/datepicker/datepicker.module";
import {FormsModule} from "@angular/forms";
import {PaginationComponent} from "./history/pagination/pagination.component";
import {ButtonModule} from "../../_widgets/button/button.module";
import {HistoryViewTabsComponent} from './history/history-view-tabs/history-view-tabs.component';
import {
    HistoryPaymentItemCardComponent
} from './invoices/history-payment-item-card/history-payment-item-card.component';
import {CollapseAnimatedDirective} from './invoices/history-payment-item-card/collapse-animated.directive';
import {InvoicesComponent} from './invoices/invoices.component';
import {TransactionsComponent} from './transactions/transactions.component';
import {DisputesComponent} from './disputes/disputes.component';
import {HistoryDateFilterComponent} from './history/history-date-filter/history-date-filter.component';

const routes: Routes = [
    {
        path: '',
        component: HistoryComponent,
        children: [
            {path: '', redirectTo: 'invoices', pathMatch: 'full'},
            {
                path: 'invoices',
                component: InvoicesComponent
            },
            {
                path: 'transactions',
                component: TransactionsComponent
            },
            {
                path: 'disputes',
                component: DisputesComponent
            }
        ]
    },
    {
        path: 'invoice/:id',
        component: InvoiceHistoryComponent
    }
];

@NgModule({
    declarations: [HistoryComponent,
        InvoiceHistoryComponent,
        PaginationComponent,
        HistoryViewTabsComponent,
        HistoryPaymentItemCardComponent,
        CollapseAnimatedDirective,
        InvoicesComponent,
        TransactionsComponent,
        DisputesComponent,
        HistoryDateFilterComponent],
    imports: [
        CommonModule,
        RouterModule.forChild(routes),
        GoogleMapModule,
        TranslateModule,
        MainPipesModule,
        PagePanelModule,
        AppBarModule,
        LoaderModule,
        DatepickerModule,
        FormsModule,
        ButtonModule
    ]
})
export class HistoryModule {
}
