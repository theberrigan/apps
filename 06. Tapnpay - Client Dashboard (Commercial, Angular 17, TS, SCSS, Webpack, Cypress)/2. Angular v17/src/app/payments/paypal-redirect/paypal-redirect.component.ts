import {Component, OnInit} from '@angular/core';
import {ActivatedRoute} from "@angular/router";
import {FlowGlobalStateService} from "../../subscriptions/_services/flow-global-state.service";
import {
    SubscriptionAcknowledgementDialogData
} from "../../subscriptions/subscription-acknowledgement/subscription-acknowledgement.component";
import {SubscriptionUpdateType} from "../../subscriptions/_models/subscription.models";


type PayPalRedirectType =
    | "subscription-cancel"
    | "subscription-confirm";

@Component({
    selector: 'app-paypal-redirect',
    templateUrl: './paypal-redirect.component.html',
    styleUrls: ['./paypal-redirect.component.css']
})
export class PaypalRedirectComponent implements OnInit {
    constructor(
        private route: ActivatedRoute,
        private flowGlobalStateService: FlowGlobalStateService) {
    }

    ngOnInit(): void {
        this.flowGlobalStateService.flowInitCompleted$.subscribe((isFlowReady) => {
            if (isFlowReady === true) {
                const action: PayPalRedirectType = this.route.snapshot.params['action'] || null;
                const confirmationType: SubscriptionUpdateType = this.route.snapshot.queryParams['ackType'];

                switch (action) {
                    case "subscription-cancel":
                        this.flowGlobalStateService.navigateSubscriptionSelection();
                        break;
                    case "subscription-confirm":
                        const data: SubscriptionAcknowledgementDialogData = {
                            response: null,
                            acknowledgementType: confirmationType
                        }
                        this.flowGlobalStateService.navigateSubscriptionAcknowledgement(data);
                        break;
                    default:
                        console.log("Paypal redirect action is not defined: " + action);
                }
                // unsubscribe since the component is no longer needed
                this.flowGlobalStateService.flowInitCompleted$.unsubscribe();
            }
        });
    }
}
