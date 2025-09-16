import {Component, Inject, Input, OnInit} from '@angular/core';
import {
    SubscriptionListItem, SubscriptionStatus
} from "../_models/subscription.models";
import {DIALOG_DATA, DialogRef} from "@angular/cdk/dialog";
import {FlowGlobalStateService} from "../_services/flow-global-state.service";
import {FlowNavigationService} from "../../services/flow-navigation.service";
import {SubscriptionApiService} from "../_services/subscription-api.service";
import {forkJoin} from "rxjs";
import {LicensePlatesService} from "../../services/license-plates.service";


export interface SubscriptionSelectionDialogData {
    selectedPlanId: string
}

@Component({
    selector: 'app-subscription-select',
    templateUrl: './subscription-select.component.html',
    styleUrls: ['./subscription-select.component.scss']
})
export class SubscriptionSelectComponent implements OnInit {
    @Input() listOfSubscriptions: SubscriptionListItem[] = [];

    plans: SubscriptionListItem[];
    selectedSubscription: SubscriptionListItem;
    subscriptionStatus: SubscriptionStatus;
    private currentPlanId: string;
    private nextPlanId: string;

    public isShowCancel: boolean;
    public isLoaded: boolean = false;
    public activeLicensePlatesCount: number = 0;

    constructor(@Inject(DIALOG_DATA) public dialogData: SubscriptionSelectionDialogData,
                private flowGlobalState: FlowGlobalStateService,
                private flowNavigationService: FlowNavigationService,
                private subscriptionApiService: SubscriptionApiService,
                private licensePlateService: LicensePlatesService,
                public dialogRef: DialogRef<string>) {
    }

    ngOnInit(): void {
        forkJoin({
            subscriptionResp: this.subscriptionApiService.getCurrentSubscription(),
            plansResp: this.subscriptionApiService.getSubscriptionsPlans(),
            activeLicensePlatesResp: this.licensePlateService.getCountOfActiveLPNs()
        })
            .subscribe((
                {
                    subscriptionResp,
                    plansResp,
                    activeLicensePlatesResp
                }) => {
                this.plans = plansResp.plans;
                this.subscriptionStatus = subscriptionResp.status;
                this.currentPlanId = subscriptionResp.subscription_plan_id;
                this.nextPlanId = subscriptionResp.next_subscription_plan_id;
                this.preselectItem();
                this.isShowCancel = this.subscriptionStatus != SubscriptionStatus.NO_SUBSCRIPTION;
                this.activeLicensePlatesCount = activeLicensePlatesResp.active;
                this.isLoaded = true;
            });
    }

    private preselectItem(): void {
        if (this.plans?.length > 0) {
            // pre-select if the id was passed as a parameter of the dialog
            if (this.dialogData.selectedPlanId != null) {
                this.selectedSubscription = this.findPlanById(this.dialogData.selectedPlanId);
            }
            // pre-select if next plan is available
            else if (this.nextPlanId != null) {
                this.selectedSubscription = this.findPlanById(this.nextPlanId);
            }
            // pre-select if a current plan is available
            else if (this.currentPlanId != null) {
                this.selectedSubscription = this.findPlanById(this.currentPlanId);
            }
            // default to the first in the list
            else {
                this.selectedSubscription = this.plans[0];
            }
        }
    }

    private findPlanById(id: string): SubscriptionListItem | null {
        return this.plans.find(item => item.id == id) || null;
    }

    closePopup() {
        this.dialogRef.close();
    }

    setSelectedSubscription(plan: SubscriptionListItem) {
        this.selectedSubscription = plan;
    }

    isSelectedSubscription(plan: SubscriptionListItem): boolean {
        return this.selectedSubscription?.id === plan.id;
    }

    onSubmit() {
        this.flowGlobalState.setSelectedSubscription(this.selectedSubscription);
        // TODO navigation has to be done by parent. Does modal dialog support call backs?
        this.closePopup();
        this.flowNavigationService.onSubscriptionSelectionSuccess();
    }

    // TODO add button
    onCancel() {
        // TODO navigation has to be done by parent
        this.closePopup();
        this.flowNavigationService.onSubscriptionSelectionCancel();
    }

    public isDisabledSubscription(plan: SubscriptionListItem): boolean {
        return plan.max_license_plates < this.activeLicensePlatesCount;
    }
}
