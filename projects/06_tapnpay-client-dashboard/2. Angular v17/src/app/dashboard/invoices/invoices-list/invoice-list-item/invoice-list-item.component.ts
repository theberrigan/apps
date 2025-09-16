import {Component, Input} from '@angular/core';
import {InvoiceItemUIModel} from "../../invoices.service";

@Component({
    selector: 'app-invoice-list-item',
    templateUrl: './invoice-list-item.component.html',
    styleUrls: ['./invoice-list-item.component.scss']
})
export class InvoiceListItemComponent {
    @Input() invoice: InvoiceItemUIModel = null;
    isSubmitting: boolean = false;

    onItemClick(invoice: InvoiceItemUIModel, $event: MouseEvent) {

    }

    onCheckboxCellClick(invoice: InvoiceItemUIModel, $event: MouseEvent) {

    }
}
