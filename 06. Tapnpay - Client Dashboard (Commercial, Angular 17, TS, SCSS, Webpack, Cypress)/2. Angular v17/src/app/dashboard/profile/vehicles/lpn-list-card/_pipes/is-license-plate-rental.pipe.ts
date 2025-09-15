import {Pipe, PipeTransform} from '@angular/core';
import {LicensePlateItem} from "../../../../../services/license-plates.service";

@Pipe({
    name: 'isLicensePlateRental'
})
export class IsLicensePlateRentalPipe implements PipeTransform {

    transform(lpn: LicensePlateItem): boolean {
        return lpn.type === 'RENTAL';
    }
}
