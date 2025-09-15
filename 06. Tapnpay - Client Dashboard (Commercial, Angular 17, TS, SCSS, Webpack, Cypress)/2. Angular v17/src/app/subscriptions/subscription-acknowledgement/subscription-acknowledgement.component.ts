import {Component, Inject, OnInit} from '@angular/core';
import {FlowGlobalStateService} from "../_services/flow-global-state.service";
import {LicensePlatesService} from "../../services/license-plates.service";
import {DIALOG_DATA, DialogRef} from "@angular/cdk/dialog";
import {
    SetSubscriptionPlanResponse,
    SubscriptionUpdateType, SubscriptionUpdateTypeEnum
} from "../_models/subscription.models";
import {forkJoin} from "rxjs";
import {SubscriptionApiService} from "../_services/subscription-api.service";
import { UserService } from 'src/app/services/user.service';

export interface SubscriptionAcknowledgementDialogData {
    response: SetSubscriptionPlanResponse;
    acknowledgementType: SubscriptionUpdateType;
}

@Component({
    selector: 'app-subscription-acknowledgement',
    templateUrl: './subscription-acknowledgement.component.html',
    styleUrls: ['./subscription-acknowledgement.component.css']
})
export class SubscriptionAcknowledgementComponent implements OnInit {

    public acknowledgementType: SubscriptionUpdateType;
    private pendingLpsExist: boolean;
    public maxLP: number;
    public activeUntil: Date;
    SubscriptionUpdateTypeEnum = SubscriptionUpdateTypeEnum;
    private isMembershipUpdate: boolean = false;

    constructor(
        @Inject(DIALOG_DATA) public dialogData: SubscriptionAcknowledgementDialogData,
        private dialogRef: DialogRef<string>,
        private flowGlobalStateService: FlowGlobalStateService,
        private licensePlatesService: LicensePlatesService,
        private usetService: UserService,
        private subscriptionApiService: SubscriptionApiService) {
    }

    ngOnInit(): void {
        this.acknowledgementType = this.dialogData.acknowledgementType;

        forkJoin({
            pendingLPs: this.licensePlatesService.getPendingLPNs(),
            currentSubscription: this.subscriptionApiService.getCurrentSubscription()
        }).subscribe(({pendingLPs, currentSubscription}) => {

            this.pendingLpsExist = pendingLPs.plates?.length > 0;
            this.maxLP = currentSubscription.max_lp;
            this.activeUntil = currentSubscription.active_until_date;

            switch (this.acknowledgementType) {
                case SubscriptionUpdateTypeEnum.NEW:
                    {
                      this.usetService.setUserActive();
                      this.usetService.initUser().then(() => {
                        this.navigateFlow();    // on new subscription show no ACK
                      });
                      break;
                    }
                case SubscriptionUpdateTypeEnum.UPGRADE:   // show popup
                case SubscriptionUpdateTypeEnum.DOWNGRADE:
                case SubscriptionUpdateTypeEnum.NO_CHANGE:
                    this.isMembershipUpdate = true;
                    break;
                default:
                    console.log("Cannot handle acknowledgement type " + this.acknowledgementType);
                    this.navigateFlow();
            }

        })

    }

    onOK() {
        this.navigateFlow(this.isMembershipUpdate)
    }

    private navigateFlow(isUpdateMembership = false) {
        this.dialogRef.close();
        if (this.pendingLpsExist) {
            this.flowGlobalStateService.navigatePendingLicensePlates();
        } else {
            isUpdateMembership ? this.flowGlobalStateService.navigateMembership() : this.flowGlobalStateService.navigateVehicles();
        }
    }
}
