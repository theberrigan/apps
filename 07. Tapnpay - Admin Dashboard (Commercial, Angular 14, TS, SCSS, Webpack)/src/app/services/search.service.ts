import { Injectable } from '@angular/core';
import {HttpService} from './http.service';
import {catchError, map, take} from 'rxjs/operators';
import {Observable, throwError} from 'rxjs';

export interface AccountSearchResult {
    account_id : string;
    account_status : string;
    phone : string;
    lp : string;
    bpm : string;
}

export const SEARCH_MIN_TERM_LENGTH = 3;
export const SEARCH_MAX_TERM_LENGTH = 15;

@Injectable({
    providedIn: 'root'
})
export class SearchService {
    constructor (
        private httpService : HttpService
    ) {}

    // Term length: 3-15
    search (term : string) : Observable<AccountSearchResult[]> {
        return this.httpService.post('endpoint://search.get', {
            body: { value: term }
        }).pipe(
            take(1),
            map(response => response.accounts),
            catchError(error => {
                console.warn('search error:', error);
                return throwError(error);
            })
        )
    }
}
