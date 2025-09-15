import {Injectable} from '@angular/core';
import {HttpService} from '../../services/http.service';
import {Observable} from "rxjs";
import {
    AllSubscriptionPlansResponse,
    CheckSubscriptionActionsResponse,
    CompareSubscriptionPlanResponse,
    CurrentSubscriptionResponse,
    SetSubscriptionPlanOptions,
    SetSubscriptionPlanResponse
} from "../_models/subscription.models";

@Injectable({
    providedIn: 'root'
})
export class SubscriptionApiService {

    constructor(private httpService: HttpService) {
    }


    public getSubscriptionsPlans(): Observable<AllSubscriptionPlansResponse> {
        return this.httpService.get('endpoint://subscription.getAll');
    }

    public getCurrentSubscription(): Observable<CurrentSubscriptionResponse> {
        return this.httpService.get('endpoint://subscription.getCurrent');
    }

    public setSubscriptionPlan(options: SetSubscriptionPlanOptions): Observable<SetSubscriptionPlanResponse> {
        return this.httpService.put('endpoint://subscription.set', {
            body: options
        });
    }

    cancelSubscription(): Observable<any> {
        return this.httpService.delete('endpoint://subscription.cancel');
    }

    compareSubscriptionPlans(planId: string): Observable<CompareSubscriptionPlanResponse> {
        return this.httpService.get('endpoint://subscription.compare', {
            urlParams: {planId}
        });
    }

    public checkSubscriptionActions(): Observable<CheckSubscriptionActionsResponse> {
        return this.httpService.get('endpoint://subscription.actions');
    }

    public sendCancelReason(data: { source: string, feedback: string }): Observable<any> {
        return this.httpService.put('endpoint://feedback.set', {
            body: data
        });
    }
}
