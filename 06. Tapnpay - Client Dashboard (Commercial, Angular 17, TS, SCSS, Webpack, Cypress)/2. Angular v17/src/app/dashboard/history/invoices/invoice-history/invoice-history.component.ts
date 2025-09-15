import {
    ChangeDetectionStrategy,
    Component,
    HostListener,
    OnDestroy,
    OnInit,
    Renderer2,
    ViewEncapsulation
} from '@angular/core';
import {ActivatedRoute, Router} from '@angular/router';
import {TitleService} from '../../../../services/title.service';
import {DeviceService, ViewportBreakpoint} from '../../../../services/device.service';
import {firstValueFrom, Subscription} from 'rxjs';
import {animateChild, query, transition, trigger} from '@angular/animations';
import {
    HistoryService,
    SpecificInvoiceHistory, SpecificInvoiceHistoryInvoice, SpecificInvoiceHistoryPBM,
    SpecificInvoiceHistoryToll, TransactionHistoryItem
} from '../../history.service';
import {DisputeReason, DisputeReasonOption, InvoicesService} from '../../../invoices/invoices.service';
import {CoverageLocation, CoverageLocationMap, CoverageService} from '../../../../services/coverage.service';
import {AccountPaymentModel, AccountTollAuthority, UserService} from '../../../../services/user.service';

type ListState = 'loading' | 'list' | 'empty' | 'error';

type DisputeReasonMap = { [key in DisputeReason]: string };

@Component({
    selector: 'invoice-history',
    templateUrl: './invoice-history.component.html',
    styleUrls: ['./invoice-history.component.scss'],
    changeDetection: ChangeDetectionStrategy.Default,
    encapsulation: ViewEncapsulation.None,
    host: {
        'class': 'invoice-history',
        '[@invoiceHistoryHost]': 'true'
    },
    animations: [
        trigger('invoiceHistoryHost', [
            transition(':enter', [
                query('@*', animateChild(), {optional: true}),
            ]),
        ]),
    ]
})
export class InvoiceHistoryComponent implements OnInit, OnDestroy {
    viewportBreakpoint: ViewportBreakpoint;

    subs: Subscription[] = [];

    listState: ListState;

    history: SpecificInvoiceHistory;

    hasTolls: boolean;

    hasPBM: boolean;

    hasFee: boolean;
    hasSubscription: boolean;

    disputeReasonMap: DisputeReasonMap;

    printDate: Date = new Date();

    coverageLocations: CoverageLocation[];

    coverageLocationMap: CoverageLocationMap;

    activeCoverageLocation: CoverageLocation;

    isMapAvailable: boolean;

    paymentModel: AccountPaymentModel = null;

    tollAuthority: AccountTollAuthority = null;

    constructor(
        private renderer: Renderer2,
        private router: Router,
        private route: ActivatedRoute,
        private titleService: TitleService,
        private deviceService: DeviceService,
        private historyService: HistoryService,
        private invoicesService: InvoicesService,
        private userService: UserService,
        private coverageService: CoverageService,
    ) {
        window.scroll(0, 0);

        this.isMapAvailable = true;  // this.userService.getUserData().account.paymentModel !== 'FLEET';

        const {account} = this.userService.getUserData();

        this.paymentModel = account.paymentModel;
        this.tollAuthority = account.tollAuthority;

        this.viewportBreakpoint = this.deviceService.viewportBreakpoint;
        this.subs.push(this.deviceService.onResize.subscribe((message) => {
            if (message.breakpointChange) {
                this.viewportBreakpoint = message.breakpointChange.current;
            }
        }));
    }

    ngOnInit() {

        this.listState = 'loading';

        const disputeReasons = this.invoicesService.getDisputeReasonOptions();

        this.disputeReasonMap = disputeReasons.reduce((map: DisputeReasonMap, disputeReasonOption: DisputeReasonOption) => {
            map['DISPUTE_' + disputeReasonOption.value] = disputeReasonOption.display;
            return map;
        }, {} as DisputeReasonMap);

        const invoiceId: string = this.route.snapshot.params['id'] || null;

        this.historyService.fetchSpecificInvoiceHistory(invoiceId).subscribe(
            async (response: SpecificInvoiceHistory) => {
                this.history = response;
                this.coverageLocationMap = await this.createLocationMap(this.history?.tolls);
                // this.history.pbm = <any>Object.assign({}, this.history.fee);
                // this.history.pbm.pay_by_name = 'Some name';
                this.hasTolls = (this.history?.tolls || []).length > 0;
                this.hasPBM = !!this.history.pbm;
                this.hasFee = !!this.history.fee;
                this.hasSubscription = !!this.history.subscription;
                this.listState = this.hasTolls || this.hasPBM || this.hasFee || this.hasSubscription ? 'list' : 'empty';
                this.titleService.setTitle('history.invoice.page_title_specific', {
                    invoice: this.history.invoice.invoice_name
                });
            },
            () => {
                this.history = null;
                this.listState = 'error';
            },
        );
    }

    ngOnDestroy(): void {
        this.subs.forEach(sub => sub.unsubscribe());
    }

    async createLocationMap(invoiceHistoryTolls: SpecificInvoiceHistoryToll[]): Promise<CoverageLocationMap> {
        const tollsPositionsByName: CoverageLocationMap = {};

        if (!this.isMapAvailable || !invoiceHistoryTolls) {
            return tollsPositionsByName;
        }

        if (!this.coverageLocations) {
            const coverage = await firstValueFrom(this.coverageService.getMapCoverageFullData());
            this.coverageLocations = await this.coverageService.coverageToLocations(coverage, this.tollAuthority, false);
        }

        if (!this.coverageLocations) {
            return tollsPositionsByName;
        }

        invoiceHistoryTolls.forEach(({location}) => {
            location = location.trim().toUpperCase();

            tollsPositionsByName[location] = this.coverageLocations.find(item => {
                return location.startsWith(item.gantry.code.trim().toUpperCase());
            });
        });

        return tollsPositionsByName;
    }

    hasLocationRoute(location: string): boolean {
        console.log(location);
        return !!(this.isMapAvailable && this.coverageLocationMap && this.coverageLocationMap[location]);
    }

    onShowLocationMap(location: string) {
        if (!this.isMapAvailable || !this.hasLocationRoute(location)) {
            return;
        }

        this.activeCoverageLocation = this.coverageLocationMap[location];
    }

    onMapClose() {
        this.activeCoverageLocation = null;
    }

    onGoBack() {
        this.router.navigateByUrl('/dashboard/history');
    }

    @HostListener('window:beforeprint')
    onBeforePrint() {
        this.printDate = new Date();
    }

    onPrint() {
        window.print();
    }
}
