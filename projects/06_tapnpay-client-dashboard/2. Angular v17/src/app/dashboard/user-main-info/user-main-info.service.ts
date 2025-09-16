import {Injectable} from '@angular/core';
import {SubscriptionApiService} from "../../subscriptions/_services/subscription-api.service";
import {AllInvoicesHttpResponseModel, InvoicesService} from "../invoices/invoices.service";
import {
    AllLicensePlatesHttpResponse,
    GetLicensePlatesResponseV2,
    LicensePlatesService
} from "../../services/license-plates.service";
import {BehaviorSubject, forkJoin} from "rxjs";
import {CurrentSubscriptionResponse} from "../../subscriptions/_models/subscription.models";

@Injectable({
    providedIn: 'root'
})
export class UserMainInfoService {

    allDataSubj$ = new BehaviorSubject<{
        subscription: CurrentSubscriptionResponse,
        invoices: AllInvoicesHttpResponseModel,
        vehicles: {active: number}
    } | null>(null);

    constructor(private subscription: SubscriptionApiService,
                private invoices: InvoicesService,
                private licensePlatesService: LicensePlatesService) {
    }

    getAllData() {
        forkJoin([
            this.subscription.getCurrentSubscription(),
            this.invoices.fetchInvoices(),
            this.licensePlatesService.getCountOfActiveLPNs()]).subscribe(
            ([subscription, invoices, vehicles]) => {
                console.log(subscription, invoices, vehicles);
                this.setAllData({subscription, invoices, vehicles});
            });
    }

    private setAllData(data: {
        subscription: CurrentSubscriptionResponse,
        invoices: AllInvoicesHttpResponseModel,
        vehicles: {active: number}
    }) {
        this.allDataSubj$.next(data);
    }
}
