import {Injectable} from '@angular/core';
import {HttpService} from "./http.service";
import {Observable, Subject} from "rxjs";
import paymentMethodType = stripe.paymentMethod.paymentMethodType;
import {PaymentMethodType} from "./payment.service";

@Injectable({
    providedIn: 'root'
})
export class AutopaymentService {

    public isAutoPaymentValueChanges$: Subject<boolean> = new Subject<boolean>();
    public disabledPaymentMethods: PaymentMethodType[] = ['PAYPAL'];

    constructor(private http: HttpService) {
    }

    enableAutopayment(): Observable<{ isAutoPaymentAprrovedStatus: 'OK' }> {
        this.emmitStateChanges(true);
        return this.http.put('endpoint://autopayment.set', {
            body: {
                is_autopayment_approved: true
            }
        });
    }

    disableAutopayment(): Observable<{ isAutoPaymentAprrovedStatus: 'OK' }> {
        this.emmitStateChanges(false);
        return this.http.put('endpoint://autopayment.set', {
            body: {
                is_autopayment_approved: false
            }
        });
    }

    checkAutopaymentStatus(): Observable<{ approvalStatus: boolean }> {
        return this.http.get('endpoint://autopayment.check');
    }

    emmitStateChanges(state: boolean) {
        this.isAutoPaymentValueChanges$.next(state);
    }
}
