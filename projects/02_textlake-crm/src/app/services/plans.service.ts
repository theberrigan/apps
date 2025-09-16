import { Injectable } from '@angular/core';
import {HttpService} from './http.service';
import {catchError, map, retry, take} from 'rxjs/operators';
import {Observable, throwError} from 'rxjs';
import {UserService} from './user.service';


export interface Plan {
    id : number;
    name : string;
    plan : string;
    tier : string;
}

export interface PlanPromo {
    name : string;
    plan : string;
    price : number;
    tier : string;
}


@Injectable({
    providedIn: 'root'
})
export class PlansService {
    constructor (
        private http : HttpService,
        private userService : UserService,
    ) {}

    public fetchPlans () : Observable<PlanPromo[]> {
        return this.http.get('endpoint://plans.getPlans').pipe(
            retry(1),
            take(1),
            map(response => response.plans),
            catchError(error => {
                console.warn('fetchPlans error:', error);
                return throwError(error);
            })
        );
    }
}
