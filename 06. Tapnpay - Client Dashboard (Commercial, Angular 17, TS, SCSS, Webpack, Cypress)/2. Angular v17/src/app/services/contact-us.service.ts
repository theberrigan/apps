import {Injectable} from '@angular/core';
import {HttpService} from './http.service';
import {catchError, map, take} from 'rxjs/operators';
import {Observable, throwError} from 'rxjs';

export interface ContactUsRequestData {
    brand: string;
    email: string;
    phone: string;
    comment: string;
    first_name: string;
    last_name: string;
}

@Injectable({
    providedIn: 'root'
})
export class ContactUsService {
    constructor(
        private http: HttpService,
    ) {
    }

    sendData(requestData: ContactUsRequestData,token:string): Observable<boolean> {
        return this.http.post('endpoint://contact-us.send', {
            body: requestData,
            headers: {
                'tnp-recaptcha-token': token,
              }
        }).pipe(
            take(1),
            map(response => response === 'OK'),
            catchError(error => {
                console.warn('sendData error:', error);
                return throwError(error);
            })
        );
    }
}
