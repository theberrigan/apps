import {Injectable} from '@angular/core';
import {HttpService} from './http.service';
import {catchError, map, take} from 'rxjs/operators';
import {Observable, throwError} from 'rxjs';

@Injectable({
    providedIn: 'root'
})
export class GraphService {
    constructor (
        private http : HttpService
    ) {}

    fetchGraph (nodeId : string) : Observable<string> {
        return this.http.get('endpoint://graph.getOne', {
            urlParams: { nodeId },
            responseType: 'text'
        }).pipe(
            take(1),
            catchError(error => {
                console.warn('fetchGraph error:', error);
                return throwError(error);
            })
        );
    }
}
