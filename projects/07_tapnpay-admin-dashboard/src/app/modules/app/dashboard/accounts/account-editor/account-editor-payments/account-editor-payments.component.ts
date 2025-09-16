import {
    ChangeDetectionStrategy,
    Component, EventEmitter, Input,
    OnDestroy,
    OnInit, Output,
    ViewEncapsulation
} from '@angular/core';
import {Subscription} from 'rxjs';
import {AccountEditorData} from '../account-editor.component';
import {
    AccountService,
    ResponsePagination,
    Transaction, TRANSACTION_FETCH_COUNT,
    TransactionFilters,
    TransactionResponse, TransactionsRequestData
} from '../../../../../../services/account.service';
import {PaginationLoadEvent} from '../../../../_widgets/pagination/pagination.component';
import {defer} from '../../../../../../lib/utils';

type ListState = 'loading' | 'list' | 'empty' | 'error';

@Component({
    selector: 'account-editor-payments',
    templateUrl: './account-editor-payments.component.html',
    styleUrls: [ './account-editor-payments.component.scss' ],
    changeDetection: ChangeDetectionStrategy.Default,
    encapsulation: ViewEncapsulation.None,
    host: {
        'class': 'account-editor-payments',
    }
})
export class AccountEditorPaymentsComponent implements OnInit, OnDestroy {
    subs : Subscription[] = [];

    fetchSub : Subscription = null;

    filters : TransactionFilters;

    transactions : Transaction[];

    paginationData : ResponsePagination;

    listState : ListState;

    isDataSet : boolean = false;

    @Input()
    accountId : string;

    @Input()
    set data (data : TransactionResponse) {
        if (!this.isDataSet) {
            this.filters = data.filters;
            this.transactions = data.transactions || [];
            this.paginationData = data.page;
            this.listState = this.transactions.length > 0 ? 'list' : 'empty';

            this.isDataSet = true;
        }
    }

    @Output()
    dataChange = new EventEmitter<TransactionResponse>();

    invoicesToInspect : string[] = null;

    constructor (
        private accountService : AccountService
    ) {}

    ngOnInit () {

    }

    ngOnDestroy () : void {
        this.resetFetchSub();
        this.subs.forEach(sub => sub.unsubscribe());
    }

    onVisibilityChange () {
        defer(() => this.fetchTransactions());
    }

    resetFetchSub () {
        if (this.fetchSub) {
            this.fetchSub.unsubscribe();
            this.fetchSub = null;
        }
    }

    fetchTransactions (page : number = 0) {
        this.listState = 'loading';

        this.resetFetchSub();

        const visibility = this.filters.visibility;

        const requestData : TransactionsRequestData = {
            page,
            page_size: TRANSACTION_FETCH_COUNT,
            include_succeeded: visibility == 0 || visibility == 1,
            include_failed: visibility == 0 || visibility == 2,
        };

        this.fetchSub = this.accountService.fetchTransactions(this.accountId, requestData).subscribe(
            ({ page, transactions }) => {
                this.paginationData = page;
                this.transactions = transactions || [];
                this.listState = this.transactions.length > 0 ? 'list' : 'empty';

                this.notifyDataUpdate();
            },
            () => {
                this.paginationData = null;
                this.transactions = [];
                this.listState = 'error';

                this.notifyDataUpdate();
            }
        );
    }

    onSwitchPage (data : PaginationLoadEvent) {
        this.fetchTransactions(data.page);
    }

    onTransactionClick (transaction : Transaction) {
        if (!transaction.invoices || transaction.invoices.length === 0) {
            return;
        }

        this.invoicesToInspect = transaction.invoices.map(invoice => invoice.invoice_id);
    }

    onCloseInvoicePopup () {
        this.invoicesToInspect = null;
    }

    notifyDataUpdate () {
        this.dataChange.emit({
            filters: this.filters,
            transactions: this.transactions,
            page: this.paginationData,
        });
    }
}
