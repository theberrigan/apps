import {Injectable} from '@angular/core';
import {catchError, map, take} from 'rxjs/operators';
import {Observable, throwError} from 'rxjs';
import {HttpService} from './http.service';
import {Base64Service} from './base64.service';

export interface TAListItem {
    id : number;
    display_name : string;
    phone : string;
    enabled : boolean;
}

export interface CreateTARequestData {
    name : string;
}

export interface CreateTAResponseData {
    id : number;
}

export interface TAProp {
    name : string;
    description : string;
    category : string;
    type : string;
    value : string;
    display_name : string;
    supported_values : string[];
}

export interface TACategory {
    name : string;
    properties : TAProp[];
}

export interface TAPropData {
    name : string;
    value : string;
}

@Injectable({
    providedIn: 'root'
})
export class TAService {
    loader : Promise<any> = null;

    constructor (
        private http : HttpService,
        private base64Service : Base64Service
    ) {}

    fetchTAs () : Observable<TAListItem[]> {
        return this.http.get('endpoint://ta.getAll').pipe(
            take(1),
            map(response => response?.toll_authorities || []),
            catchError(error => {
                console.warn('fetchTAs error:', error);
                return throwError(error);
            })
        );
    }

    createTA (data : CreateTARequestData) : Observable<CreateTAResponseData> {
        return this.http.post('endpoint://ta.create', {
            body: data
        }).pipe(
            take(1),
            catchError(error => {
                console.warn('createTA error:', error);
                return throwError(error);
            })
        );
    }

    fetchTAProps (id : number) : Observable<TACategory[]> {
        return this.http.get('endpoint://ta.getProps', {
            urlParams: { id }
        }).pipe(
            take(1),
            map(response => this.decodeCategories(response?.categories || [])),
            catchError(error => {
                console.warn('fetchTAProps error:', error);
                return throwError(error);
            })
        );
    }

    updateTAProps (id : number, properties : TAPropData[]) : Observable<TACategory[]> {
        properties.forEach(prop => {
            if (typeof prop.value === 'string') {
                prop.value = this.base64Service.encode(prop.value.trim());
            }
        });

        return this.http.put('endpoint://ta.updateProps', {
            urlParams: { id },
            body: { properties }
        }).pipe(
            take(1),
            map(response => this.decodeCategories(response?.categories || [])),
            catchError(error => {
                console.warn('updateTAProps error:', error);
                return throwError(error);
            })
        );
    }

    decodeCategories (categories : TACategory[]) : TACategory[] {
        if (!categories) {
            return null;
        }

        categories.forEach(category => {
            category.properties.forEach(prop => {
                if (typeof prop.value === 'string') {
                    prop.value = this.base64Service.decode(prop.value);
                }
            });
        });

        return categories;
    }
}
