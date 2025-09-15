import { Injectable } from '@angular/core';
import {HttpService} from './http.service';
import {Observable, throwError} from 'rxjs';
import {catchError, map, retry, take} from 'rxjs/operators';

@Injectable({
    providedIn: 'root'
})
export class FilesService {
    constructor (
        private http : HttpService,
    ) {}

    public fetchFileUrl (uuid : string) : Observable<string> {
        return this.http.get('endpoint://files.getParams', {
            urlParams: { uuid }
        }).pipe(
            retry(1),
            take(1),
            map(response => response.url),
            catchError(error => {
                console.warn('fetchFileUrl error:', error);
                return throwError(error);
            })
        );
    }
}
