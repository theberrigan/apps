import {
    ChangeDetectionStrategy,
    Component,
    OnDestroy,
    OnInit,
    ViewChild,
    ViewEncapsulation
} from '@angular/core';

import {TitleService} from '../../services/title.service';
import {DeviceService, ViewportBreakpoint} from '../../services/device.service';
import {Subscription} from 'rxjs';
import {InvoiceItemUIModel, InvoicesService,} from './invoices.service';
import {animateChild, query, transition, trigger} from '@angular/animations';
import {InvoicesListComponent, OnInvoicesListInitedEvent} from './invoices-list/invoices-list.component';
import {InvoiceDetailComponent} from './invoice-detail/invoice-detail.component';
import {CoverageLocation} from '../../services/coverage.service';

type Layout = 'invoice-list' | 'invoice-detail';

@Component({
    selector: 'invoices',
    templateUrl: './invoices.component.html',
    styleUrls: ['./invoices.component.scss'],
    changeDetection: ChangeDetectionStrategy.Default,
    encapsulation: ViewEncapsulation.None,
    host: {
        'class': 'invoices',
        '[@invoicesHost]': 'true'
    },
    animations: [
        trigger('invoicesHost', [
            transition(':enter', [
                query('@*', animateChild(), {optional: true}),
            ]),
        ]),
    ]
})
export class InvoicesComponent implements OnInit, OnDestroy {
    viewportBreakpoint: ViewportBreakpoint;

    subs: Subscription[] = [];

    layout: Layout = 'invoice-list';

    commonListOfInvoices: { regular: InvoiceItemUIModel[], subscription: InvoiceItemUIModel[] } = {
        regular: [],
        subscription: []
    }

    coverageLocations: CoverageLocation[] = null;

    openedInDetailsInvoice: InvoiceItemUIModel[] = null;

    @ViewChild('listComponent', {read: InvoicesListComponent})
    listComponent: InvoicesListComponent;

    @ViewChild('detailComponent', {read: InvoiceDetailComponent})
    detailComponent: InvoiceDetailComponent;
    public surchargeSum: number = 0;

    constructor(
        private titleService: TitleService,
        private deviceService: DeviceService,
    ) {
        window.scroll(0, 0);

        this.viewportBreakpoint = this.deviceService.viewportBreakpoint;
        this.subs.push(this.deviceService.onResize.subscribe((message) => {
            if (message.breakpointChange) {
                this.viewportBreakpoint = message.breakpointChange.current;
            }
        }));
    }

    ngOnInit() {
        this.titleService.setTitle('invoices.page_title');

        this.layout = 'invoice-list';
    }

    ngOnDestroy(): void {
        this.subs.forEach(sub => sub.unsubscribe());
    }

    canDeactivate(): boolean {
        return (
            this.listComponent ?
                !this.listComponent.isSubmitting :
                this.detailComponent ?
                    !this.detailComponent.isSubmitting :
                    true
        );
    }

    setInvoicesAndCoverageDataToParentComponent({
                                                    invoiceItems,
                                                    coverageLocations,
                                                    surchargeSum
                                                }: OnInvoicesListInitedEvent) {


        this.commonListOfInvoices = invoiceItems;
        this.coverageLocations = coverageLocations;
        this.surchargeSum = surchargeSum;
    }

    switchToInvoiceDetailsView(invoiceItems: InvoiceItemUIModel[]) {
        this.openedInDetailsInvoice = invoiceItems;
        this.layout = 'invoice-detail';
    }

    onCloseInvoicePayment() {
        this.layout = 'invoice-list';
    }

    onPaymentSuccess(paidInvoiceIds: string[]) {
        this.commonListOfInvoices = {
            regular: [],
            subscription: []
        }
        this.layout = 'invoice-list';
    }

}
