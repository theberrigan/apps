import {Injectable} from '@angular/core';
import {HttpService} from './http.service';
import {catchError, map, take} from 'rxjs/operators';
import {Observable, throwError} from 'rxjs';


@Injectable({
    providedIn: 'root'
})
export class DisputesService {

    constructor (
        private http : HttpService
    ) {}

    uploadFile (file : File) : Observable<string[]> {
        const formData = new FormData();

        formData.append('file', file, file.name);

        return this.http.post('endpoint://disputes.uploadFile', {
            body: formData,
            reportProgress: false
        }).pipe(
            take(1),
            map(response => response.messages),
            catchError(error => {
                console.warn('uploadFile error:', error);
                return throwError(error);
            })
        );
    }
}
