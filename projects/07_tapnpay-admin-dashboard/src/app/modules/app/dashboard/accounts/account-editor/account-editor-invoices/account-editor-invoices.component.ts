import {
    ChangeDetectionStrategy,
    Component, EventEmitter, Input,
    OnDestroy,
    OnInit, Output,
    ViewEncapsulation
} from '@angular/core';
import {Subscription} from 'rxjs';
import {
    AccountService,
    ExtendInvoiceDateRequestData,
    OutstandingInvoice,
    OutstandingInvoiceWithExtension, TransactionResponse
} from '../../../../../../services/account.service';
import {DomService} from '../../../../../../services/dom.service';
import {defer, int} from '../../../../../../lib/utils';
import {ToastService} from '../../../../../../services/toast.service';


@Component({
    selector: 'account-editor-invoices',
    templateUrl: './account-editor-invoices.component.html',
    styleUrls: [ './account-editor-invoices.component.scss' ],
    changeDetection: ChangeDetectionStrategy.Default,
    encapsulation: ViewEncapsulation.None,
    host: {
        'class': 'account-editor-invoices',
    }
})
export class AccountEditorInvoicesComponent implements OnInit, OnDestroy {
    subs : Subscription[] = [];

    invoices : OutstandingInvoiceWithExtension[];

    invoicesToInspect : OutstandingInvoiceWithExtension[] = null;

    @Input()
    accountId : string;

    shouldBeSaved : boolean = false;

    isSaving : boolean = false;

    isDataSet : boolean = false;

    @Input()
    set data (invoices : OutstandingInvoiceWithExtension[]) {
        if (!this.isDataSet) {
            this.invoices = invoices;
            this.isDataSet = true;
        }
    }

    @Output()
    dataChange = new EventEmitter<OutstandingInvoiceWithExtension[]>();

    extendHoursOptions : number[] = [ null, 24, 48, 72 ];

    constructor (
        private accountService : AccountService,
        private toastService : ToastService,
        private domService : DomService,
    ) {}

    ngOnInit () {

    }

    ngOnDestroy () : void {
        this.subs.forEach(sub => sub.unsubscribe());
    }

    onCloseInvoicePopup () {
        this.invoicesToInspect = null;
    }

    onInvoiceClick (invoice : OutstandingInvoiceWithExtension, e : any) {
        if (this.domService.hasEventMark(e, 'extCellClick')) {
            return;
        }

        this.invoicesToInspect = [ invoice ];
    }

    onExtendCellClick (e : any) {
        this.domService.markEvent(e, 'extCellClick');
    }

    onCheckExtensionHours () {
        this.shouldBeSaved = this.invoices.some(invoice => invoice.hours && invoice.hours > 0);
    }

    async onSave () {
        if (this.isSaving) {
            return;
        }

        const invoicesToSave : ExtendInvoiceDateRequestData[] = this.invoices.reduce((acc, invoice) => {
            if (invoice.hours && invoice.hours > 0) {
                acc.push({
                    invoice_id: invoice.invoice_id,
                    hours: invoice.hours
                });
            }
            return acc;
        }, []);

        if (invoicesToSave.length <= 0) {
            return;
        }

        this.isSaving = true;

        const isExtended = await Promise.all(
            invoicesToSave.map(invoice => this.accountService.saveInvoiceExtension(this.accountId, invoice).toPromise())
        ).catch(() => false);

        this.invoices = await this.accountService.fetchExtendedInvoices(this.accountId).catch(() => null);
        this.onCheckExtensionHours();
        this.notifyDataUpdate();

        this.isSaving = false;

        if (isExtended) {
            this.toastService.create({
                message: [ 'accounts.invoices.extend_success' ],
                timeout: 5000
            });
        } else {
            this.toastService.create({
                message: [ 'accounts.invoices.extend_error' ],
                timeout: 5000
            });
        }
    }

    notifyDataUpdate () {
        this.dataChange.emit(this.invoices);
    }
}
