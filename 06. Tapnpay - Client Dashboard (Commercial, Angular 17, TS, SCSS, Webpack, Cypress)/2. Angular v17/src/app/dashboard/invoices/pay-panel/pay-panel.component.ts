import {Component, EventEmitter, Input, OnInit, Output} from '@angular/core';
import {AutopaymentService} from "../../../services/autopayment.service";
import {concatMap, take} from "rxjs/operators";
import {PaymentMethodType, PaymentService} from "../../../services/payment.service";
import {tap} from "rxjs";

@Component({
    selector: 'app-pay-panel',
    templateUrl: './pay-panel.component.html',
    styleUrls: ['./pay-panel.component.scss'],
})
export class PayPanelComponent implements OnInit {
    @Input() isLoading: boolean = false;
    @Input() checkedInvoiceAmountSum: number;
    @Input() surchargeSum: number;
    @Input() isShowDetailsLink: boolean = true;
    activePaymentMethod: PaymentMethodType;

    @Output() showDetails: EventEmitter<boolean> = new EventEmitter(true);
    @Output() makePayment: EventEmitter<{ autoPayControlIsShown: boolean, isAutoPaymentEnabled: boolean }> = new EventEmitter(true);
    isAutopayControlModel: boolean = false;
    isAutoPayEnabled: boolean = true;


    constructor(private autopaymentService: AutopaymentService,
                private paymentService: PaymentService) {
    }


    ngOnInit() {
        this.paymentService.fetchPaymentConfig().pipe(
            take(1),
            tap(res => {
                this.activePaymentMethod = res.payment_method_type;
            }),
            concatMap(() => this.autopaymentService.checkAutopaymentStatus().pipe(
                take(1),
                tap(res => {
                    this.isAutoPayEnabled = res.approvalStatus;
                    this.isAutopayControlModel = this.isAutoPayEnabled;
                })
            ))
        ).subscribe();
    }

    isShowAutopayControl(): boolean {
        return !this.isLoading && !this.isAutoPayEnabled && this.activePaymentMethod
            && !this.autopaymentService.disabledPaymentMethods.includes(this.activePaymentMethod);
    }

    emmitShowDetails() {
        this.showDetails.emit(true);
    }

    emmitMakePayment() {
        const autoPayControlIsShown = this.isShowAutopayControl();
        this.isAutoPayEnabled = this.isAutopayControlModel;
        const payload = {
            autoPayControlIsShown,
            isAutoPaymentEnabled: this.isAutopayControlModel
        }
        this.makePayment.emit(payload);
    }
}
