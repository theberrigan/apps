import {ChangeDetectionStrategy, Component, EventEmitter, Input, Output} from '@angular/core';

@Component({
    selector: 'app-transactions',
    templateUrl: './transactions.component.html',
    styleUrls: ['./transactions.component.css'],
    changeDetection: ChangeDetectionStrategy.OnPush,
})
export class TransactionsComponent {
    @Input() isLoadingPage: boolean = false;
    @Input() viewportBreakpoint: any;
    @Input() transactionItems: any;
    @Input() isMapAvailable: any;
    @Input() coverageLocationMap: any;
    @Input() listState: any;

    @Output() showLocationMap: EventEmitter<any> = new EventEmitter<any>;


    hasLocationRoute(location: string): boolean {
        return !!(this.isMapAvailable && this.coverageLocationMap && this.coverageLocationMap[location]);
    }

    onShowLocationMap(location) {
        this.showLocationMap.emit(location);
    }
}
