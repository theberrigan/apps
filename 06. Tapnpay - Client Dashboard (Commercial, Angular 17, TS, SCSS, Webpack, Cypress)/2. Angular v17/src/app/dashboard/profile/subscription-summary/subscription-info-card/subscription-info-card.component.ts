import {Component, Input, OnInit} from '@angular/core';
import {
    SubscriptionStatus,
    SubscriptionToShow
} from "../../../../subscriptions/_models/subscription.models";
import {isNil} from "lodash-es";

interface PropsVisibility {
    status: boolean;
    renewalDate: boolean;
    fee: boolean;
    vehicleLimit: boolean;
    activeUntil: boolean;
    expiredOn: boolean;
    nextActivationDate?: boolean; // added this as it's in your initial structure but not in the function
}


@Component({
    selector: 'app-subscription-info-card',
    templateUrl: './subscription-info-card.component.html',
    styleUrls: ['./subscription-info-card.component.scss']
})

export class SubscriptionInfoCardComponent implements OnInit {

    propsVisibility: PropsVisibility = {
        status: true,
        renewalDate: false,
        fee: false,
        vehicleLimit: false,
        activeUntil: false,
        expiredOn: false,
        nextActivationDate: false,
    };

    private readonly STATUS_VISIBILITY_MAP: Record<SubscriptionStatus, PropsVisibility> = {
        [SubscriptionStatus.ACTIVE]: {
            status: true,
            renewalDate: true,
            fee: true,
            vehicleLimit: true,
            activeUntil: true,
            expiredOn: false,
        },
        [SubscriptionStatus.ACTIVE_UNTIL_EXPIRATION]: {
            status: true,
            renewalDate: false,
            fee: true,
            vehicleLimit: true,
            activeUntil: true,
            expiredOn: false,
        },
        [SubscriptionStatus.EXPIRED]: {
            status: true,
            renewalDate: false,
            fee: false,
            vehicleLimit: false,
            activeUntil: false,
            expiredOn: true,
        },
        [SubscriptionStatus.NO_SUBSCRIPTION]: {
            status: true,
            renewalDate: false,
            fee: false,
            vehicleLimit: false,
            activeUntil: false,
            expiredOn: false,
        },
        [SubscriptionStatus.NEXT_TO_ACTIVE]: {
            status: false,
            renewalDate: true,
            fee: true,
            vehicleLimit: true,
            activeUntil: false,
            expiredOn: false,
        },
    };

    @Input() subscriptionToShow: SubscriptionToShow;

    subscriptionStatus: SubscriptionStatus = SubscriptionStatus.NO_SUBSCRIPTION;

    ngOnInit(): void {
        this.subscriptionStatus = this.getSubscriptionStatus();
        this.setSubscriptionFieldsVisibilityByStatus(this.subscriptionStatus);
    }

    getStatusMessage(): string {
        return "subscription_summary.status_enum." + this.subscriptionStatus.toLowerCase();
    }

    public isStatusActiveUntilExpiration(): boolean {
        return this.subscriptionStatus === SubscriptionStatus.ACTIVE_UNTIL_EXPIRATION;
    }

    public isStatusActive(): boolean {
        return this.subscriptionStatus === SubscriptionStatus.ACTIVE;
    }

    getRenewalDate(): Date {
        return this.subscriptionToShow?.next_billing_date;
    }


    getFee(): number {
        let fee = this.subscriptionToShow?.price;
        return isNil(fee) ? 0 : fee;
    }

    getVehicleLimit(): number {
        let limit = this.subscriptionToShow?.max_lp;
        return isNil(limit) ? 0 : limit;
    }

    getActiveUntilDate(): Date {
        return this.subscriptionToShow?.active_until_date;
    }

    getExpiredOnDate(): Date {
        return this.subscriptionToShow?.expired_date;
    }

    setSubscriptionFieldsVisibilityByStatus(status: SubscriptionStatus): void {
        this.propsVisibility = this.STATUS_VISIBILITY_MAP[status];
    }


    private getSubscriptionStatus() {
        return this.subscriptionToShow?.status;
    }
}
