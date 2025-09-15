import { Injectable } from '@angular/core';
import {HttpService} from './http.service';
import {catchError, map, retry, take} from 'rxjs/operators';
import {Observable, ReplaySubject, Subject, throwError} from 'rxjs';
import {DomSanitizer} from '@angular/platform-browser';
import {UserService} from './user.service';


@Injectable({
    providedIn: 'root'
})
export class DashboardService {
    onDashboardStateChange = new ReplaySubject<boolean>();

    isInDashboard : boolean = false;

    constructor (
        private http : HttpService,
        private sanitizer : DomSanitizer,
        private userService : UserService,
    ) {
        this.notifyDashboardStateChange();
    }

    setDashboardState (isInDashboard : boolean) {
        this.isInDashboard = isInDashboard;
        this.notifyDashboardStateChange();
    }

    notifyDashboardStateChange () {
        this.onDashboardStateChange.next(this.isInDashboard);
    }

    getDashboardState () : boolean {
        return this.isInDashboard;
    }
}
