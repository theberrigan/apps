import { Injectable } from '@angular/core';
import {Observable, of, throwError} from 'rxjs';
import { catchError, map, retry, take } from 'rxjs/operators';
import { isArray } from 'lodash';
import { HttpService } from '../../../services/http.service';


@Injectable({
    providedIn: 'root'
})
export class PanelService {
    constructor (
        private http : HttpService
    ) {}

    public fetchNotifications (count : number) : Observable<any> {
        return of([]);
        /*return this.http.get('endpoint://notifications.get', {
            urlParams: { count }
        }).pipe(
            retry(1),
            take(1),
            map(response => response.notifications),
            catchError(error => {
                console.warn('fetchNotifications error:', error);
                return throwError(error);
            })
        );*/
    }

    public markAsViewed (id : number | number[]) : Observable<any> {
        if (typeof(id) === 'number') {
            id = [ id ];
        }

        return this.http.post('endpoint://notifications.markAsViewed', {
            params: { id: id.join(',') }
        }).pipe(
            retry(1),
            take(1),
            catchError(error => {
                console.warn('markAsViewed error:', error);
                return throwError(error);
            })
        );
    }
}
