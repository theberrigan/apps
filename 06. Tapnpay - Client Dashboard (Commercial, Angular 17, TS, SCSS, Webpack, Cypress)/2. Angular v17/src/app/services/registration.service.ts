import { Injectable } from '@angular/core';
import { Observable, throwError } from 'rxjs';
import { catchError, map, take } from 'rxjs/operators';
import { UserService } from './user.service';
import { HttpService } from './http.service';

export interface RegistrationData {
    first_name: string;
    last_name: string;
    email: string;
    terms_accepted: string;
    language: string;
}

export interface RegistrationResponse {
    status: string;
    status_code: number;
}

@Injectable({
    providedIn: 'root'
})
export class RegistrationService {
    constructor(
        private http: HttpService,
        private userService: UserService
    ) {}

    registerUser(data: RegistrationData): Observable<RegistrationResponse> {
        const token = this.userService.getToken();
        const headers = {
            'Content-Type': 'application/json',
            'x-tnp-access-token': token
        };

        // Map language code to API format: 'ENG' for English, 'SPA' for Spanish
        let apiLanguage = data.language;
        if (apiLanguage.toLowerCase() === 'en') {
            apiLanguage = 'ENG';
        } else if (apiLanguage.toLowerCase() === 'es') {
            apiLanguage = 'SPA';
        } else {
            apiLanguage = apiLanguage.toUpperCase();
        }

        const apiData = {
            ...data,
            language: apiLanguage,
            terms_accepted: data.terms_accepted.toString()
        };

        return this.http.post('endpoint://account.register-user', {
            body: apiData,
            headers
        }).pipe(
            take(1),
            map(response => ({
                status: response.status,
                status_code: response.status_code
            })),
            catchError(error => {
                console.warn('Registration error:', error);
                return throwError(error);
            })
        );
    }
} 