import {Injectable} from '@angular/core';
import {BehaviorSubject, Subject} from "rxjs";
import {SubscriptionListItem} from "../_models/subscription.models";
import {PaymentConfig} from "../../services/payment.service";
import {userRegistrationFlowType} from "../../services/user-registration-flow-type.service";
import {
    SubscriptionAcknowledgementDialogData
} from "../subscription-acknowledgement/subscription-acknowledgement.component";

export type AddSubscriptionFlowEventsNames =
    | 'subscriptionSelection'
    | 'subscriptionConfirmation'
    | 'paymentMethodSelection'
    | 'subscriptionAcknowledgement'
    | 'licensePlateAddedAcknowledgement'
    | 'licensePlateDeclinedAcknowledgement'
    | 'pendingLicensePlates'
    | 'vehicles'
    | 'membership'
    ;

export interface AddSubscriptionFlowEvent {
    name: AddSubscriptionFlowEventsNames;
    data: any;
}


@Injectable({
    providedIn: 'root'
})
export class FlowGlobalStateService {

    constructor() {
    }

    public flowInitCompleted$: BehaviorSubject<boolean> = new BehaviorSubject<boolean>(false);
    public selectedNewSubscription$: BehaviorSubject<SubscriptionListItem> = new BehaviorSubject(null);
    public selectedPaymentMethod$: BehaviorSubject<PaymentConfig> = new BehaviorSubject(null);

    public flowEvents$: Subject<AddSubscriptionFlowEvent> = new Subject();

    public flowType: userRegistrationFlowType;


    public setFlowInitCompleted() {
        this.flowInitCompleted$.next(true);
    }

    public setSelectedSubscription(plan: SubscriptionListItem) {
        this.selectedNewSubscription$.next(plan);
    }

    public setSelectedPaymentConfig(setElectedPaymentConfig: PaymentConfig) {
        this.selectedPaymentMethod$.next(setElectedPaymentConfig);
    }

    public setFlowType(type: userRegistrationFlowType): void {
        this.flowType = type;
    }

    public emmitSubscriptionFlowEvent(event: AddSubscriptionFlowEvent) {
        this.flowEvents$.next(event);
    }


    public isPayPerBundle(): boolean {
        return this.flowType === userRegistrationFlowType.PAY_PER_BUNDLE;
    }

    public isPayPerCar(): boolean {
        return this.flowType === userRegistrationFlowType.PAY_PER_CAR;
    }


    // ----------------------------------------------------------------------------

    public navigateSubscriptionSelection() {
        this.emmitSubscriptionFlowEvent({
            name: 'subscriptionSelection',
            data: null
        })
    }

    public navigateSubscriptionConfirmation() {
        this.emmitSubscriptionFlowEvent({
            name: 'subscriptionConfirmation',
            data: null
        })
    }


    public navigatePaymentMethodSelection() {
        this.emmitSubscriptionFlowEvent({
            name: 'paymentMethodSelection',
            data: null
        })
    }

    public navigatePaymentMethodSelectionWithData(data: any) {
        this.emmitSubscriptionFlowEvent({
            name: 'paymentMethodSelection',
            data: data
        })
    }

    public navigateSubscriptionAcknowledgement(data: SubscriptionAcknowledgementDialogData) {
        this.emmitSubscriptionFlowEvent({
            name: 'subscriptionAcknowledgement',
            data: data
        })
    }

    public navigateLicensePlateAddedAcknowledgement() {
        this.emmitSubscriptionFlowEvent({
            name: 'licensePlateAddedAcknowledgement',
            data: null
        })
    }

    public navigateLicensePlateDeclinedAcknowledgement() {
        this.emmitSubscriptionFlowEvent({
            name: 'licensePlateDeclinedAcknowledgement',
            data: null
        })
    }

    public navigatePendingLicensePlates() {
        this.emmitSubscriptionFlowEvent({
            name: 'pendingLicensePlates',
            data: null
        })
    }

    public navigateVehicles() {
        this.emmitSubscriptionFlowEvent({
            name: 'vehicles',
            data: null
        })
    }

    public navigateMembership() {
        this.emmitSubscriptionFlowEvent({
            name: 'membership',
            data: null
        })
    }


}
