import {Component, OnDestroy, OnInit} from '@angular/core';
import {FormBuilder, FormGroup} from "@angular/forms";
import {AutopaymentService} from "../../../../services/autopayment.service";
import {of, skip, Subscription, switchMap, tap, throwError} from "rxjs";
import {catchError} from "rxjs/operators";
import {ToastService} from "../../../../services/toast.service";
import {deburr} from "lodash-es";

@Component({
    selector: 'app-auto-payment-card',
    templateUrl: './auto-payment-card.component.html',
    styleUrls: ['./auto-payment-card.component.scss']
})
export class AutoPaymentCardComponent implements OnInit, OnDestroy {
    isShowAutoPayments: boolean = true;
    form: FormGroup;
    subscriptions: Subscription[] = [];
    private isProgrammaticChange: boolean;

    constructor(private fb: FormBuilder,
                private autopaymentsService: AutopaymentService,
                private toaster: ToastService) {
        this.form = this.fb.group({
            switch: [false]
        });
    }

    ngOnInit(): void {
        this.subscriptions.push(this.autopaymentsService.checkAutopaymentStatus().subscribe((status) => {
            this.setSwitchValue(status.approvalStatus);
        }));


        this.subscriptions.push(
            this.form.get('switch').valueChanges.pipe(
                tap(value => {
                    if (this.isProgrammaticChange) {
                        this.isProgrammaticChange = false;
                    } else {
                        const serviceCall = value
                            ? this.autopaymentsService.enableAutopayment()
                            : this.autopaymentsService.disableAutopayment();

                        serviceCall.pipe(
                            switchMap(() => this.autopaymentsService.checkAutopaymentStatus()),
                            tap(status => {
                                this.setSwitchValue(status.approvalStatus);
                                this.toaster.create({
                                    message: value ? 'invoices_auto_payment.auto_payment_enabled' : 'invoices_auto_payment.auto_payment_disabled',
                                    type: 'success'
                                });
                            }),
                            catchError(error => {
                                console.error('Autopayment action failed', error);
                                this.setSwitchValue(!value);
                                this.toaster.create({
                                    message: value ? 'invoices_auto_payment.auto_payment_enable_error' : 'invoices_auto_payment.auto_payment_disable_error',
                                    type: 'error'
                                });
                                return of(null);
                            })
                        ).subscribe();
                    }
                })
            ).subscribe()
        );

        this.subscriptions.push(
            this.autopaymentsService.isAutoPaymentValueChanges$.subscribe(
                (value) => {
                    this.setSwitchValue(value);
                }
            ));

    }

    ngOnDestroy(): void {
        this.subscriptions.forEach(sub => sub.unsubscribe());
    }

    setSwitchValue(value: boolean): void {
        this.isProgrammaticChange = true;
        this.form.get('switch').setValue(value);
    }

}
