import {ChangeDetectionStrategy, Component, Input, ViewEncapsulation} from '@angular/core';
import {InvoiceItemUIModel} from "../../invoices.service";

@Component({
    selector: 'app-subscription-invoice-card',
    templateUrl: './subscription-invoice-card.component.html',
    styleUrls: ['./subscription-invoice-card.component.scss'],
    changeDetection: ChangeDetectionStrategy.OnPush,
    encapsulation: ViewEncapsulation.None
})
export class SubscriptionInvoiceCardComponent {
    @Input() invoiceItem: InvoiceItemUIModel;

}
