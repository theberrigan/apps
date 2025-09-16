import {Component, EventEmitter, Input, Output} from '@angular/core';
import {LicensePlateItem} from "../../../../services/license-plates.service";

@Component({
    selector: 'app-lpn-list-card',
    templateUrl: './lpn-list-card.component.html',
    styleUrls: ['./lpn-list-card.component.scss']
})
export class LpnListCardComponent {
    @Input() licensePlate: LicensePlateItem;

    @Output() showLicensePlateStatusHistory: EventEmitter<any> = new EventEmitter<any>();
    @Output() unregisterLicensePlate: EventEmitter<any> = new EventEmitter<any>()
    @Output() extendLicensePlateRentalPeriod: EventEmitter<LicensePlateItem> = new EventEmitter<LicensePlateItem>();

    onUnregisterClick(licensePlate: LicensePlateItem) {
        this.unregisterLicensePlate.emit(licensePlate);
    }

    onExtendLPNRentalPeriod(licensePlate: LicensePlateItem) {
        this.extendLicensePlateRentalPeriod.emit(licensePlate);
    }

    isRental(lpn: LicensePlateItem) {
        return lpn.type === 'RENTAL';
    }

    onHistoryClick(licensePlate: LicensePlateItem) {
        this.showLicensePlateStatusHistory.emit(licensePlate);
    }
}
