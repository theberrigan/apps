import {Injectable, OnDestroy} from "@angular/core";
import {PaymentConfig, PaymentService} from "./payment.service";
import {userRegistrationFlowType} from "./user-registration-flow-type.service";
import {FlowGlobalStateService} from "../subscriptions/_services/flow-global-state.service";
import {SubscriptionApiService} from "../subscriptions/_services/subscription-api.service";
import {CurrentSubscriptionResponse, SubscriptionStatus} from "../subscriptions/_models/subscription.models";
import {Router} from "@angular/router";

@Injectable({
    providedIn: 'root'
})
export class FlowNavigationService {

    constructor(
        private paymentService: PaymentService,
        private flowGlobalState: FlowGlobalStateService,
        private subscriptionApiService: SubscriptionApiService,
        private router: Router) {
    }

    onSubscriptionSelectionSuccess() : void {
        switch (this.flowGlobalState.flowType) {
            case userRegistrationFlowType.PAY_PER_BUNDLE:
                this.paymentService.fetchPaymentConfig().subscribe((conf: PaymentConfig) => {
                    if (conf.setup_complete) {
                        this.flowGlobalState.navigateSubscriptionConfirmation();
                    } else {
                        this.flowGlobalState.navigatePaymentMethodSelection()
                    }
                })
                break;
            default:
                console.log("onSubscriptionSelectionSuccess is not defined for the flow");
                break;
        }
    }

    onSubscriptionSelectionCancel() {
        this.subscriptionApiService.getCurrentSubscription().subscribe((response : CurrentSubscriptionResponse) => {
            if (response.status != SubscriptionStatus.NO_SUBSCRIPTION) {
                this.router.navigateByUrl('/dashboard/profile/subscription');
            }
        })
    }
}
