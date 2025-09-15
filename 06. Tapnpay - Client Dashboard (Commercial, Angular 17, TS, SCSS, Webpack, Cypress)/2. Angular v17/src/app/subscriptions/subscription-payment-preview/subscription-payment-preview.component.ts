import {Component, Inject, OnDestroy, OnInit} from '@angular/core';
import {DIALOG_DATA, DialogRef} from "@angular/cdk/dialog";
import {FlowGlobalStateService} from "../_services/flow-global-state.service";
import {PaymentConfig, PaymentService} from "../../services/payment.service";
import {
    SetSubscriptionPlanResponse,
    SubscriptionListItem, SubscriptionUpdateType, SubscriptionUpdateTypeEnum
} from "../_models/subscription.models";
import {SubscriptionApiService} from "../_services/subscription-api.service";
import {firstValueFrom, Subscription, switchMap, throwError} from "rxjs";
import {SubscriptionPaymentService} from "../_services/subscription-payment.service";
import {catchError} from "rxjs/operators";
import {
    SubscriptionAcknowledgementDialogData
} from "../subscription-acknowledgement/subscription-acknowledgement.component";
import { HttpClient } from "@angular/common/http";


@Component({
    selector: 'app-subscription-payment-preview',
    templateUrl: './subscription-payment-preview.component.html',
    styleUrls: ['./subscription-payment-preview.component.scss']
})
export class SubscriptionPaymentPreviewComponent implements OnInit, OnDestroy {

    constructor(@Inject(DIALOG_DATA) public dialogData: any,
                private dialogRef: DialogRef<string>,
                private flowGlobalState: FlowGlobalStateService,
                private subscriptionApi: SubscriptionApiService,
                private paymentService: PaymentService,
                private subscriptionPaymentService: SubscriptionPaymentService,
                private httpClient: HttpClient) {
    }

    selectedSubscription: SubscriptionListItem;
    selectedPaymentMethod: PaymentConfig;

    public priceDifference: number = 0
    public currentVehicles: number;
    public currentActiveUntil: Date;
    public additionalVehicles: number;
    public futureMaxLp: number;
    public futureInvoiceAmount: number;
    public futureInvoiceDate: Date;

    public subscriptionConfirmationType: SubscriptionUpdateType;

    private subscriptionItem: Subscription;
    SubscriptionUpdateTypeEnum = SubscriptionUpdateTypeEnum;

    isPaymentProcessing = false;

    ngOnInit(): void {
        this.subscriptionItem = this.flowGlobalState.selectedNewSubscription$
            .pipe(
                switchMap((subscription) => {
                    this.selectedSubscription = subscription;
                    return this.subscriptionApi.compareSubscriptionPlans(subscription.id);
                })
            )
            .subscribe((comparePlannsResponse) => {
                this.priceDifference = comparePlannsResponse.billing_amount;
                this.currentVehicles = comparePlannsResponse.current_max_lp;
                this.additionalVehicles = comparePlannsResponse.current_max_lp > 0 ? comparePlannsResponse.next_max_lp - comparePlannsResponse.current_max_lp : comparePlannsResponse.next_max_lp;
                this.futureInvoiceAmount = comparePlannsResponse.next_billing_amount;
                this.futureInvoiceDate = comparePlannsResponse.next_billing_date;
                this.currentActiveUntil = comparePlannsResponse.current_active_until;
                this.futureMaxLp = comparePlannsResponse.next_max_lp;
                this.subscriptionConfirmationType = comparePlannsResponse.update_type;
            });


        this.flowGlobalState.selectedPaymentMethod$.subscribe((paymentMethod) => {
            this.selectedPaymentMethod = paymentMethod;
            // if the browser is refreshed flowGlobalState has no data about payment method, do the fetch directly
            if (paymentMethod == null) {
                this.paymentService.fetchPaymentConfig().subscribe((resp: PaymentConfig) => {
                    this.selectedPaymentMethod = resp;
                });
            }
        });
    }

    ngOnDestroy(): void {
        this.subscriptionItem?.unsubscribe();
    }


    submitUpdateSubscriptionPayment() {
        if (this.selectedPaymentMethod !== null) {
            this.isPaymentProcessing = true;
            this.payBySubscriptionUpdate();
        } else {
            this.paymentService.fetchPaymentConfig().subscribe((resp) => {
                this.selectedPaymentMethod = resp;
                this.isPaymentProcessing = true;
                this.payBySubscriptionUpdate();
            })
        }
    }

    private async payBySubscriptionUpdate() {
        try {
            const response: SetSubscriptionPlanResponse = await firstValueFrom(
                this.subscriptionPaymentService.paySubscription(
                    this.selectedPaymentMethod,
                    this.selectedSubscription,
                    this.subscriptionConfirmationType
                )
            );

            if (response.payment_complete) {
                this.handleCompletePaymentResponse(response);
                return;
            }

            const paymentType = this.selectedPaymentMethod.payment_method_type;
            const isPaymentMadeByWallets = ['APPLEPAY', 'GOOGLEPAY'].includes(paymentType);
            if (isPaymentMadeByWallets) {
                try {
                    await this.subscriptionPaymentService.completeWalletPayment(response);
                    this.handleCompletePaymentResponse(response);
                } catch (error) {
                    this.handleErrorPaymentResponse(error);
                }
                return;
            }

            if (paymentType === 'PAYPAL' && response?.payment_intent?.approve_payment_url) {
                this.redirectToPaymentUrl(response.payment_intent.approve_payment_url);
                return;
            }

            this.handleErrorPaymentResponse(response);
        } catch (error) {
            this.isPaymentProcessing = false;
            this.handleErrorPaymentResponse(error);
        }
    }


    public getPaymentMethodTranslationKey(): string {
        switch (this.selectedPaymentMethod?.payment_method_type) {
            case "APPLEPAY":
                return "apple_pay";
            case "GOOGLEPAY":
                return "google_pay";
            case "CREDIT_CARD":
                return "credit_card";
            case "DEBIT_CARD":
                return "debit_card";
            case "DCB":
                return "dcb";
            case "PAYPAL":
                return "paypal";
            case "VENMO":
                return "venmo";
        }
    }

    private handleErrorPaymentResponse(response: any) {
        this.dialogRef.close();
        this.flowGlobalState.navigatePaymentMethodSelectionWithData({subscriptionPaymentError: true, error: response});
    }

    private handleCompletePaymentResponse(subsResponse: SetSubscriptionPlanResponse) {

        this.sendMarketingData();

        this.isPaymentProcessing = false;
        const data: SubscriptionAcknowledgementDialogData = {
            response: subsResponse,
            acknowledgementType: this.subscriptionConfirmationType
        }
        this.dialogRef.close();
        if (this.subscriptionConfirmationType != SubscriptionUpdateTypeEnum.NO_CHANGE) {
            this.flowGlobalState.navigateSubscriptionAcknowledgement(data);
        }
    }

    private redirectToPaymentUrl(url: string): void {
        window.location.assign(url);
    }

    onBackClick(): void {
        this.dialogRef.close();
        this.flowGlobalState.navigateSubscriptionSelection();
    }

    onPaymentChangeClick(): void {
        this.dialogRef.close();
        this.flowGlobalState.navigatePaymentMethodSelection();
    }

    public isSubscriptionUpdateType(type: SubscriptionUpdateType): boolean {
        return this.subscriptionConfirmationType === type;
    }

    protected readonly Math = Math;

    private sendMarketingData() {
        this.httpClient.get(
            'https://insight.adsrvr.org/track/pxl/?adv=dywlzhl&ct=0:0co2ta8&fmt=3'
        ).subscribe(
            () => {
                console.log('Marketing data sent');
            },
            (error) => {
                console.error('Marketing data error', error);
            }
        )
    }
}
