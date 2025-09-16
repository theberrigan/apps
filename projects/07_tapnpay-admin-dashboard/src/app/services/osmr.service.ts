import {Injectable} from '@angular/core';
import {HttpService} from './http.service';
import {catchError, map, take} from 'rxjs/operators';
import {Observable, throwError} from 'rxjs';

@Injectable({
    providedIn: 'root'
})
export class OSMRService {
    constructor (
        private http : HttpService
    ) {}

    createRoute (coords : number[][]) : Observable<boolean> {
        return this.http.get(`endpoint://osmr.getRoute`, {
            urlParams: {
                coords: coords.map(pair => pair.join(',')).join(';')
            }
        }).pipe(
            take(1),
            catchError(error => {
                console.warn('createRoute error:', error);
                return throwError(error);
            })
        );
    }
}
