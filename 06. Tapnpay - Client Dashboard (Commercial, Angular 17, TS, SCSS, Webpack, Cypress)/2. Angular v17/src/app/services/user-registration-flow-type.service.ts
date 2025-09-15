import {Injectable, OnDestroy} from "@angular/core";
import {SubscriptionApiService} from "../subscriptions/_services/subscription-api.service";
import {CurrentSubscriptionResponse, SubscriptionType} from "../subscriptions/_models/subscription.models";
import {firstValueFrom} from "rxjs";

export enum userRegistrationFlowType {
    NO_PAY_CAR,
    PAY_PER_CAR,
    PAY_PER_BUNDLE
}

@Injectable({
    providedIn: 'root'
})
export class UserRegistrationFlowTypeService implements OnDestroy {
    private flowType: userRegistrationFlowType;

    constructor(
        private subscriptionApiService: SubscriptionApiService) {
    }

    ngOnDestroy() {
        this.flowType = null;
        console.log('FlowService is destroyed');
    }

    public async setFlowType(): Promise<userRegistrationFlowType> {
        const response: CurrentSubscriptionResponse = await firstValueFrom(this.subscriptionApiService.getCurrentSubscription()).catch(() => null);
        this.flowType = response?.type ? userRegistrationFlowType[response.type] : userRegistrationFlowType.PAY_PER_BUNDLE;
        return this.flowType;
    }

    public getFlowType(): Promise<userRegistrationFlowType> {
        if (!this.flowType) {
            return this.setFlowType();
        }
        return Promise.resolve(this.flowType);
    }

}
