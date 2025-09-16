import {Component, OnDestroy, OnInit} from '@angular/core';
import {Router} from '@angular/router';
import {DeviceService, ViewportBreakpoint} from '../../../services/device.service';
import {SubscriptionApiService} from "../../../subscriptions/_services/subscription-api.service";
import {
    CurrentSubscriptionResponse, SetSubscriptionPlanOptions,
    SubscriptionStatus,
    SubscriptionToShow
} from "../../../subscriptions/_models/subscription.models";
import {isNil} from "lodash-es";
import {FlowGlobalStateService} from "../../../subscriptions/_services/flow-global-state.service";
import {delay} from "rxjs";
import {SubscriptionPaymentService} from "../../../subscriptions/_services/subscription-payment.service";
import {take} from "rxjs/operators";

export enum DataState {
    LOADING,
    READY,
    ERROR
}

@Component({
    selector: 'app-subscription-summary',
    templateUrl: './subscription-summary.component.html',
    styleUrls: ['./subscription-summary.component.scss'],
})
export class SubscriptionSummaryComponent implements OnInit, OnDestroy {
    dataStates = DataState
    viewportBreakpoint: ViewportBreakpoint;
    dataState: DataState = DataState.LOADING;
    subscriptionStatus: SubscriptionStatus = SubscriptionStatus.NO_SUBSCRIPTION;

    isShowCancel: boolean = false;
    isShowCancellationConfirmation: boolean = false;

    currentSubscription: CurrentSubscriptionResponse;
    nextDownGradeSubscription: SubscriptionToShow;


    public cancelMembershipState = {
        isCancelStarted: false,
        activeCancelStep: 1,
        cancelReason: '',
        isProcessing: false,
        otherReasonValue: '',
        isRestoreProcessing: false,
        isShowRestoreConfirmation: false,
    }

    constructor(
        private router: Router,
        private deviceService: DeviceService,
        private subscriptionService: SubscriptionApiService,
        private flowGlobalStateService: FlowGlobalStateService,
        private subscriptionPaymentService: SubscriptionPaymentService
    ) {
        this.viewportBreakpoint = this.deviceService.viewportBreakpoint;
        this.dataState = DataState.LOADING;
    }

    ngOnInit(): void {
        this.refreshSubscription();

        this.flowGlobalStateService.flowEvents$.subscribe((event) => {
            if (event.name === 'membership') {
                this.refreshSubscription();
            }
        });
    }

    ngOnDestroy() {
        console.log('SubscriptionSummaryComponent destroyed');
    }

    private resetCancelReason() {
        this.cancelMembershipState.cancelReason = '';
        this.cancelMembershipState.otherReasonValue = '';
    }

    refreshSubscription(): void {
        this.dataState = DataState.LOADING;
        this.subscriptionService.getCurrentSubscription().pipe(delay(500)).subscribe((subscriptionResponse) => {
            this.subscriptionStatus = subscriptionResponse.status;
            if (this.subscriptionStatus === SubscriptionStatus.ACTIVE) {
                this.isShowCancel = true;
            }
            this.currentSubscription = subscriptionResponse;
            if (this.isHasNextSubscription(subscriptionResponse)) {
                this.nextDownGradeSubscription = this.getNextSubscriptionInstance(subscriptionResponse);
                this.isShowCancel = true;
            }

            this.dataState = DataState.READY;
        });
    }

    public isActiveCancelStep(step: number): boolean {
        return this.cancelMembershipState.isCancelStarted && this.cancelMembershipState.activeCancelStep === step;
    }

    public setActiveCancelStep(step: number): void {
        this.cancelMembershipState.activeCancelStep = step;
    }

    startCancelMembership() {
        this.cancelMembershipState.isCancelStarted = true;
        this.cancelMembershipState.activeCancelStep = 1;
        this.cancelMembershipState.isProcessing = false;
    }

    closeCancelMembership() {
        this.cancelMembershipState.isCancelStarted = false;
        this.cancelMembershipState.activeCancelStep = 1;
        this.resetCancelReason();
    }

    closeRestoreMembership() {
        this.cancelMembershipState.isCancelStarted = false;
        this.cancelMembershipState.activeCancelStep = 1;
        this.resetCancelReason();
        this.cancelMembershipState.isShowRestoreConfirmation = false;
    }

    private getNextSubscriptionInstance(subscriptionResponse: CurrentSubscriptionResponse) {
        return {
            status: SubscriptionStatus.NEXT_TO_ACTIVE,
            next_billing_date: subscriptionResponse.next_billing_date,
            price: subscriptionResponse.next_billing_amount,
            max_lp: subscriptionResponse.next_max_lp,
            active_until_date: new Date(subscriptionResponse.next_billing_date),
            expired_date: null
        };
    }

    onGoBack() {
        this.router.navigateByUrl('/dashboard/profile');
    }

    onUpdateClick(): void {
        this.flowGlobalStateService.navigateSubscriptionSelection();
    }

    cancelMembershipFinally() {
        this.cancelMembershipState.isProcessing = true;
        this.subscriptionService.cancelSubscription().pipe(
            delay(1000)
        ).subscribe(() => {
            this.sendCancelReason();
            this.resetCurrentSubscriptionInfo();
            this.refreshSubscription();
            this.cancelMembershipState.isProcessing = false;
            this.cancelMembershipState.activeCancelStep = 3;
            this.isShowCancel = false;
        })
    }

    private resetCurrentSubscriptionInfo() {
        this.currentSubscription = null;
        this.nextDownGradeSubscription = null;
    }

    getActiveUntilDate(): Date {
        return this.currentSubscription?.active_until_date;
    }

    isHasNextSubscription(subs: CurrentSubscriptionResponse): boolean {
        return (!!subs.subscription_plan_id && !!subs.next_subscription_plan_id)
            && (subs.subscription_plan_id !== subs.next_subscription_plan_id);
    }

    sendCancelReason() {
        const cancelData = {
            source: 'Tapnpay web version',
            feedback: this.getCancelReasonText(),
        }
        this.subscriptionService.sendCancelReason(cancelData).pipe(take(1)).subscribe(() => {

        });
    }

    getUserToken(): string {
        return JSON.parse(localStorage.getItem('authUserData')).token;
    }

    getCancelReasonText(): string {
        return this.cancelMembershipState.cancelReason === 'other' ? 'other ' + this.cancelMembershipState.otherReasonValue : this.cancelMembershipState.cancelReason;
    }


    restoreCurrentSubscription() {
        const data: SetSubscriptionPlanOptions = {
            subscription_plan_id: this.currentSubscription.subscription_plan_id,
            verification_code: null,
            return_url: null,
            cancel_url: null,
            payment_method_id: null,
            payment_method_type: null,
        }
        this.cancelMembershipState.isRestoreProcessing = true;

        this.subscriptionService.setSubscriptionPlan(data).pipe(
            delay(500),
            take(1)
        ).subscribe(() => {
            this.resetCurrentSubscriptionInfo();
            this.refreshSubscription();
            this.cancelMembershipState.isRestoreProcessing = false;
            this.cancelMembershipState.isShowRestoreConfirmation = true;
        });
    }

    isShowRestoreButton() {
        return this.currentSubscription?.status === SubscriptionStatus.ACTIVE_UNTIL_EXPIRATION;
    }

    isShowUpdateButton() {
        return this.currentSubscription?.status === SubscriptionStatus.ACTIVE || this.subscriptionStatus === SubscriptionStatus.NEXT_TO_ACTIVE;
    }
}
