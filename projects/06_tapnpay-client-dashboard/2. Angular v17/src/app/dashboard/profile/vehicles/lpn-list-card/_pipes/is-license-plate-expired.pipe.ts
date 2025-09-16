import {Pipe, PipeTransform} from '@angular/core';
import {LicensePlateItem} from "../../../../../services/license-plates.service";

@Pipe({
    name: 'isLicensePlateExpired'
})
export class IsLicensePlateExpiredPipe implements PipeTransform {

    transform(licensePlate: LicensePlateItem): boolean {
        if (!licensePlate.end_date) {
            return false;
        }

        const endDate: Date = new Date(licensePlate.end_date);
        if (isNaN(endDate.getTime())) {
            throw new Error('Invalid LPN end_date format');
        }
        return endDate < new Date();
    }
}
