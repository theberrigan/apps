import { Injectable } from '@angular/core';
import {API_TOKEN_HEADER_KEY, HttpService} from './http.service';
import {catchError, map, retry, take} from 'rxjs/operators';
import {Observable, throwError} from 'rxjs';

@Injectable({
    providedIn: 'root'
})
export class StorageService {
    constructor (
        private http : HttpService,
    ) {}

    get (key : string, token : string = null) : Observable<any> {
        const headers = {};

        if (token) {
            headers[API_TOKEN_HEADER_KEY] = token;
        }

        return this.http.get('endpoint://storage.get', {
            urlParams: { key },
            headers
        }).pipe(
            retry(1),
            take(1),
            map(({ status, value }) => {
                if (status === 'OK' && value !== null) {
                    return JSON.parse(value);
                }

                return null;
            }),
            catchError(error => {
                console.warn('StorageService.get error:', error);
                return throwError(error);
            })
        );
    }

    create (key : string, value : any) : Observable<boolean> {
        return this.http.post('endpoint://storage.create', {
            urlParams: { key },
            body: {
                value: JSON.stringify(value)
            }
        }).pipe(
            take(1),
            map(({ status }) => status === 'OK'),
            catchError(error => {
                console.warn('StorageService.create error:', error);
                return throwError(error);
            })
        );
    }

    update (key : string, value : any) : Observable<boolean> {
        return this.http.put('endpoint://storage.update', {
            urlParams: { key },
            body: {
                value: JSON.stringify(value)
            }
        }).pipe(
            take(1),
            map(({ status }) => status === 'OK'),
            catchError(error => {
                console.warn('StorageService.update error:', error);
                return throwError(error);
            })
        );
    }

    delete (key : string) : Observable<boolean> {
        return this.http.delete('endpoint://storage.delete', {
            urlParams: { key },
        }).pipe(
            take(1),
            map(({ status }) => status === 'OK'),
            catchError(error => {
                console.warn('StorageService.delete error:', error);
                return throwError(error);
            })
        );
    }
}
