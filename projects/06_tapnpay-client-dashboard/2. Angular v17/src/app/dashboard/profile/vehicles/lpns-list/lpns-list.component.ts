import {
    ChangeDetectionStrategy,
    ChangeDetectorRef,
    Component,
    EventEmitter,
    Input,
    OnInit,
    Output
} from '@angular/core';
import {LicensePlateItem, LicensePlatesService} from "../../../../services/license-plates.service";

@Component({
    selector: 'app-lpns-list',
    templateUrl: './lpns-list.component.html',
    styleUrls: ['./lpns-list.component.scss'],
    changeDetection: ChangeDetectionStrategy.OnPush
})
export class LpnsListComponent implements OnInit {

    @Input() lpnsList: LicensePlateItem[];
    @Input() listTitle: string = '';
    @Input() isRental: boolean = false;
    @Output() onLpnSelectedToUnregister: any = new EventEmitter();
    @Output() onLpnSelectedToRentalExtend: any = new EventEmitter();

    historyItems : LicensePlateItem[];

    constructor(
        private licensePlatesService : LicensePlatesService,
        private changeDetectorRef: ChangeDetectorRef) {
    }

    ngOnInit(): void {
    }

    onUnregisterClick(licensePlate: LicensePlateItem) {
        this.onLpnSelectedToUnregister.emit(licensePlate);
    }

    onRentalExtendClick(licensePlate: LicensePlateItem) {
        this.onLpnSelectedToRentalExtend.emit(licensePlate);
    }

    onHistoryClick(licensePlate: LicensePlateItem) {
        this.licensePlatesService.getAllLicensePlatesHistory(licensePlate.id).subscribe(resp => {
            this.historyItems = resp.items;
            this.changeDetectorRef.detectChanges();
        })
    }

    onHistoryClose() {
        this.historyItems = null;
    }

    isLicensePlateExpired(licensePlate: LicensePlateItem) {
        return licensePlate.end_date && new Date(licensePlate.end_date) < new Date();
    }
}
