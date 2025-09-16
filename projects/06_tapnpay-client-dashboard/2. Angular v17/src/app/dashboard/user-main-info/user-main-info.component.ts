import {Component} from '@angular/core';
import {UserMainInfoService} from "./user-main-info.service";
import {AllInvoicesHttpResponseModel, InvoiceItemBackendModel} from "../invoices/invoices.service";
import {GetLicensePlatesResponseV2, LicensePlatesService} from "../../services/license-plates.service";
import {CurrentSubscriptionResponse} from "../../subscriptions/_models/subscription.models";
import {BehaviorSubject} from "rxjs";

@Component({
    selector: 'app-user-main-info',
    templateUrl: './user-main-info.component.html',
    styleUrls: ['./user-main-info.component.scss']
})
export class UserMainInfoComponent {
    constructor(private userMainInfoService: UserMainInfoService, private licensePlatesService: LicensePlatesService) {

    }

    isLoaded$ = new BehaviorSubject<boolean>(false);
    dataSubscriptions$ = this.userMainInfoService.allDataSubj$;

    dataState = {
        subscriptionInfo: {
            expirationDate: new Date(),
            isHasRenewal: true,
            isShow: false,
        },
        invoices: {
            all: 0,
        },
        vehicles: {
            all: 0,
        }
    }

    ngOnInit() {
        this.userMainInfoService.getAllData();
        this.dataSubscriptions$.subscribe(data => {
            if (data) {
                this.setDataState(data);
            }
        });
    }

    private setDataState(data: {
        subscription: CurrentSubscriptionResponse;
        invoices: AllInvoicesHttpResponseModel;
        vehicles: { active: number };
    }) {
        this.isLoaded$.next(false);
        let {subscription, invoices, vehicles} = data;
        let invoicesCount = invoices.invoices.length;
        let vehiclesCount = vehicles.active;
        let expirationDate = new Date(subscription.active_until_date);

        this.dataState = {
            subscriptionInfo: {
                expirationDate: expirationDate,
                isHasRenewal: invoices.invoices.some((invoice: InvoiceItemBackendModel) => invoice.invoice_type === "SUBSCRIPTION_RENEWAL"),
                isShow: subscription.type === "PAY_PER_BUNDLE",
            },
            invoices: {
                all: invoicesCount,
            },
            vehicles: {
                all: vehiclesCount,
            }
        }
        this.isLoaded$.next(true);

    }

    ngOnDestroy() {

    }
}
