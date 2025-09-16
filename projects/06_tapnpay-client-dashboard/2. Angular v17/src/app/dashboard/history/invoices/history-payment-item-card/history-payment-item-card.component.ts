import {ChangeDetectionStrategy, Component, HostBinding, Input, OnInit} from '@angular/core';
import {InvoiceHistoryItem, InvoiceHistoryPaymentMethod} from "../../history.service";
import {Router} from "@angular/router";
import {animate, state, style, transition, trigger} from "@angular/animations";

@Component({
    selector: 'app-history-payment-item-card',
    templateUrl: './history-payment-item-card.component.html',
    styleUrls: ['./history-payment-item-card.component.scss'],
    changeDetection: ChangeDetectionStrategy.OnPush,
})
export class HistoryPaymentItemCardComponent implements OnInit {
    readonly paymentMethodNames: { [key in InvoiceHistoryPaymentMethod]: string } = {
        DCB: 'payment_methods.dcb',
        PAYPAL: 'payment_methods.paypal',
        CREDIT_CARD: 'payment_methods.credit_card',
        DEBIT_CARD: 'payment_methods.debit_card',
        WALLET: 'payment_methods.wallet',
        GOOGLEPAY: 'payment_methods.google_pay',
        APPLEPAY: 'payment_methods.apple_pay',
    };

    @Input() dateInvoices: { date: string, invoices: InvoiceHistoryItem[] } = null;
    public isOpened: boolean = false;
    public firstInvoice: InvoiceHistoryItem = null;
    public totalFee: number = 0;
    public processingFee: number = 0;

    constructor(private router: Router) {
    }

    ngOnInit(): void {
        this.firstInvoice = this.dateInvoices.invoices[0];
        this.setFee();
    }

    getTotalFeeWithProcessingFee(invoices: InvoiceHistoryItem[]) {
        this.totalFee = this.getTotalFee(invoices);
        this.processingFee = this.getProcessingFee(invoices);
        return this.totalFee + this.processingFee;
    }

    private getTotalFee(invoices: InvoiceHistoryItem[]) {
        return invoices.reduce((acc, invoice) => acc + invoice.payment_amount, 0);
    }

    private getProcessingFee(invoices: InvoiceHistoryItem[]) {
        return invoices[0].surcharge;
    }

    private setFee() {
        this.processingFee = this.getProcessingFee(this.dateInvoices.invoices);
        this.totalFee = this.getTotalFeeWithProcessingFee(this.dateInvoices.invoices);
    }

    public toggleCollapse(): boolean {
        return this.isOpened = !this.isOpened;
    }

    public goToInvoice(invoiceId: string) {
        this.router.navigateByUrl(`/dashboard/history/invoice/${invoiceId}`);
    }
}
