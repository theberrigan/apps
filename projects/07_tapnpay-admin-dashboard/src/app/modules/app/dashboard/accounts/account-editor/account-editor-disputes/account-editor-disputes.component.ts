import {
    ChangeDetectionStrategy,
    Component, EventEmitter, Input,
    OnDestroy,
    OnInit, Output,
    ViewEncapsulation
} from '@angular/core';
import {Subscription} from 'rxjs';
import { AccountService, Dispute } from '../../../../../../services/account.service';
import {defer} from '../../../../../../lib/utils';

type ListState = 'loading' | 'list' | 'empty' | 'error';
type SubmitBy = null | 'page' | 'submit' | 'reset';

interface DisputesTabData {
    disputes : Dispute[];
}

@Component({
    selector: 'account-editor-disputes',
    templateUrl: './account-editor-disputes.component.html',
    styleUrls: [ './account-editor-disputes.component.scss' ],
    changeDetection: ChangeDetectionStrategy.Default,
    encapsulation: ViewEncapsulation.None,
    host: {
        'class': 'account-editor-disputes',
    },
})
export class AccountEditorDisputesComponent implements OnInit, OnDestroy {
    subs : Subscription[] = [];

    fetchSub : Subscription = null;

    disputes : Dispute[];

    listState : ListState;

    isDataSet : boolean = false;

    @Input()
    accountId : string;

    @Input()
    set data (data : DisputesTabData) {
        if (!this.isDataSet) {
            this.disputes = data.disputes || [];
            this.listState = this.disputes.length > 0 ? 'list' : 'empty';
            this.isDataSet = true;
        }
    }

    @Output()
    dataChange = new EventEmitter<DisputesTabData>();

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

    fetchTransactions () {
        this.listState = 'loading';

        this.resetFetchSub();

        this.fetchSub = this.accountService.fetchDisputes(this.accountId).subscribe(
            (disputes : Dispute[]) => {
                this.disputes = disputes || [];
                this.listState = this.disputes.length > 0 ? 'list' : 'empty';

                this.notifyDataUpdate();
            },
            () => {
                this.disputes = [];
                this.listState = 'error';

                this.notifyDataUpdate();
            }
        );
    }

    onDisputeClick (dispute : Dispute) {
        if (!dispute?.invoice_id) {
            return;
        }

        this.invoicesToInspect = [ dispute?.invoice_id ];
    }

    onCloseInvoicePopup () {
        this.invoicesToInspect = null;
    }

    notifyDataUpdate () {
        this.dataChange.emit({
            disputes: this.disputes,
        });
    }
}
