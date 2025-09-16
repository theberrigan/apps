import {Injectable} from '@angular/core';
import {HttpService} from './http.service';
import {catchError, map, take} from 'rxjs/operators';
import {Observable, throwError} from 'rxjs';

export interface FaqCategoryItem {
    id: string;
    question: string;
    answer: string;
}

export interface FaqCategory {
    id: string;
    name: string;
    items: FaqCategoryItem[];
}

@Injectable({
    providedIn: 'root'
})
export class FaqService {
    constructor(
        private http: HttpService,
    ) {
    }

    fetchFAQ(lang: string): Observable<FaqCategory[]> {
        return this.http.get('endpoint://faq.get', {
            params: {lang}
        }).pipe(
            take(1),
            map(response => response.categories || []),
            catchError(error => {
                console.warn('fetchFAQ error:', error);
                return throwError(error);
            })
        );
    }
}
