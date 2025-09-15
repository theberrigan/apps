import {ChangeDetectionStrategy, Component, EventEmitter, Input, OnInit, Output} from '@angular/core';
import {TitleService} from "../../../services/title.service";
import {ViewportBreakpoint} from "../../../services/device.service";

@Component({
    selector: 'app-disputes',
    templateUrl: './disputes.component.html',
    styleUrls: ['./disputes.component.css'],
    changeDetection: ChangeDetectionStrategy.OnPush,
})
export class DisputesComponent implements OnInit {
    @Input() disputeItems: any;
    @Input() isLoadingPage: boolean;
    @Input() listState!: "loading" | "list" | "empty" | "error";
    @Input() viewportBreakpoint: ViewportBreakpoint;
    @Input() disputeReasonMap: any;
    @Input() coverageLocationMap: any;
    @Input() isMapAvailable: any;
    @Output() showLocationMap = new EventEmitter<string>();

    constructor(private titleService: TitleService) {
    }

    ngOnInit() {
        this.titleService.setTitle('history.disputes.page_title');
    }

    hasLocationRoute(location: string): boolean {
        return !!(this.isMapAvailable && this.coverageLocationMap && this.coverageLocationMap[location]);
    }

    onShowLocationMap(location) {
        this.showLocationMap.emit(location);
    }
}
