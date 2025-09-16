import {
    ChangeDetectionStrategy,
    Component,
    OnDestroy,
    OnInit,
    Renderer2,
    ViewChild,
    ViewEncapsulation
} from '@angular/core';
import {CanDeactivate, Router} from '@angular/router';
import {TitleService} from '../../../../services/title.service';
import {DeviceService, ViewportBreakpoint} from '../../../../services/device.service';
import {Subscription} from 'rxjs';
import {InvoiceItem, InvoicesService,} from '../../../../services/invoices.service';
import {DomService} from '../../../../services/dom.service';
import {animateChild, query, transition, trigger} from '@angular/animations';
import {InvoicesListComponent, OnInvoicesListInitedEvent} from './invoices-list/invoices-list.component';
import {InvoiceDetailComponent} from './invoice-detail/invoice-detail.component';
import {Coverage, CoverageLocation} from '../../../../services/coverage.service';

type Layout = 'invoice-list' | 'invoice-detail';

@Component({
    selector: 'invoices',
    templateUrl: './invoices.component.html',
    styleUrls: [ './invoices.component.scss' ],
    changeDetection: ChangeDetectionStrategy.Default,
    encapsulation: ViewEncapsulation.None,
    host: {
        'class': 'invoices',
        '[@invoicesHost]': 'true'
    },
    animations: [
        trigger('invoicesHost', [
            transition(':enter', [
                query('@*', animateChild(), { optional: true }),
            ]),
        ]),
    ]
})
export class InvoicesComponent implements OnInit, OnDestroy, CanDeactivate<boolean | Promise<boolean>> {
    viewportBreakpoint : ViewportBreakpoint;

    subs : Subscription[] = [];

    layout : Layout = 'invoice-list';

    invoiceItems : InvoiceItem[] = null;

    coverageLocations : CoverageLocation[] = null;

    invoiceItemsForPayment : InvoiceItem[] = null;

    @ViewChild('listComponent', { read: InvoicesListComponent })
    listComponent : InvoicesListComponent;

    @ViewChild('detailComponent', { read: InvoiceDetailComponent })
    detailComponent : InvoiceDetailComponent;

    constructor (
        private renderer : Renderer2,
        private router : Router,
        private titleService : TitleService,
        private deviceService : DeviceService,
        private domService : DomService,
        private invoicesService : InvoicesService,
    ) {
        window.scroll(0, 0);

        this.viewportBreakpoint = this.deviceService.viewportBreakpoint;
        this.subs.push(this.deviceService.onResize.subscribe((message) => {
            if (message.breakpointChange) {
                this.viewportBreakpoint = message.breakpointChange.current;
            }
        }));
    }

    ngOnInit () {
        this.titleService.setTitle('invoices.page_title');

        this.layout = 'invoice-list';
    }

    ngOnDestroy () : void {
        this.subs.forEach(sub => sub.unsubscribe());
    }

    canDeactivate () : boolean {
        return (
            this.listComponent ?
            !this.listComponent.isSubmitting :
            this.detailComponent ?
            !this.detailComponent.isSubmitting :
            true
        );
    }

    onInvoicesListInited ({ invoiceItems, coverageLocations } : OnInvoicesListInitedEvent) {
        this.invoiceItems = invoiceItems;
        this.coverageLocations = coverageLocations;
    }

    onShowInvoiceDetails (invoiceItems : InvoiceItem[]) {
        this.invoiceItemsForPayment = invoiceItems;
        this.layout = 'invoice-detail';
    }

    onCloseInvoicePayment () {
        this.layout = 'invoice-list';
    }

    onPaymentSuccess (paidInvoiceIds : string[]) {
        this.invoiceItems = this.invoiceItems.filter((invoiceItem : InvoiceItem) => {
            return !paidInvoiceIds.includes(invoiceItem.id);
        });
        this.layout = 'invoice-list';
    }
}
