import {
    ChangeDetectionStrategy,
    Component, EventEmitter, Input,
    OnDestroy,
    OnInit, Output,
    ViewEncapsulation
} from '@angular/core';
import {Subscription} from 'rxjs';
import {AccountService, OutstandingInvoice} from '../../../../../../services/account.service';

@Component({
    selector: 'account-editor-invoice-details',
    templateUrl: './account-editor-invoice-details.component.html',
    styleUrls: [ './account-editor-invoice-details.component.scss' ],
    changeDetection: ChangeDetectionStrategy.Default,
    encapsulation: ViewEncapsulation.None,
    host: {
        'class': 'account-editor-invoice-details',
    }
})
export class AccountEditorInvoiceDetailsComponent implements OnInit, OnDestroy {
    subs : Subscription[] = [];

    @Input()
    popupTitle : string = null;

    @Input()
    accountId : string = null;

    @Input()
    invoices : OutstandingInvoice[] = null;

    @Input()
    invoicesToLoad : string[] = null;

    @Output()
    onClose = new EventEmitter<void>();

    constructor (
        private accountService : AccountService
    ) {}

    ngOnInit () {
        this.init();
    }

    ngOnDestroy () : void {
        this.subs.forEach(sub => sub.unsubscribe());
    }

    async init () {
        if (this.invoicesToLoad) {
            await this.fetchInvoices();
        }
    }

    async fetchInvoices () {
        Promise.all(
            this.invoicesToLoad.map(invoiceId => {
                return this.accountService.fetchInvoiceDetails(this.accountId, invoiceId).toPromise()
            })
        ).then((invoices : OutstandingInvoice[]) => {
            this.invoices = invoices;
        });
    }
}
