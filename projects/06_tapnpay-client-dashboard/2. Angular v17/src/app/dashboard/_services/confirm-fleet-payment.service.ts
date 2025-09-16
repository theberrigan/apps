import {Injectable} from '@angular/core';
import {StripeService} from "../../services/stripe.service";
import {PaymentService} from "../../services/payment.service";
import {PendingLPN} from "../../services/license-plates.service";
import {BehaviorSubject, Subject} from "rxjs";
import {PendingPlateCreateModel} from "../dashboard/dashboard.component";

export type LPNType = 'RENTAL' | 'REGULAR';

export interface EmmitNewPendingLicensePlatesListToPayParams {
    listOfLPns: PendingPlateCreateModel[];
    lpnNames: string[];
}

@Injectable({
    providedIn: 'root'
})
export class ConfirmFleetPaymentService {
    public newPendingLicensePlatesListToPay$: Subject<EmmitNewPendingLicensePlatesListToPayParams> = new Subject<EmmitNewPendingLicensePlatesListToPayParams>();
    constructor(private stripeService: StripeService,
                private paymentService: PaymentService,
    ) {
    }


    public async initPaymentConfig() {
        const [stripe, paymentConfig, hoursToPay] = await Promise.all([
            this.stripeService.getStripeInstance(),
            this.paymentService.fetchPaymentConfig().toPromise(),
            this.paymentService.fetchHoursToPay().toPromise()
        ]).catch(() => [null, null]);
        return {stripe, paymentConfig, hoursToPay};
    }

    public getPLateType(plate: PendingLPN): LPNType {
        return plate.rental ? 'RENTAL' : 'REGULAR';
    }

    public getEndDateForRentalLPN(plate: PendingLPN, pendingFormValue): string {
        const endDate = new Date(pendingFormValue?.rental_period.endDate);
        const endTime = new Date(pendingFormValue?.rental_period.endTime);

        return this.getMixedDateTimeFromTwoDates(endDate, endTime);
    }

    private getMixedDateTimeFromTwoDates(dateForDate: Date, DateForTime: Date): string | null {
        const mixedDate = new Date(
            dateForDate.getFullYear(),
            dateForDate.getMonth(),
            dateForDate.getDate(),
            DateForTime.getHours(),
            DateForTime.getMinutes()
        );
        return mixedDate.toISOString() || null;
    }

    public emmitNewPendingLicensePlatesListToPay(data: EmmitNewPendingLicensePlatesListToPayParams) {
        this.newPendingLicensePlatesListToPay$.next(data);
    }
}
