import {Injectable} from '@angular/core';
import {catchError, map, take} from 'rxjs/operators';
import {Observable, throwError} from 'rxjs';
import {HttpService} from './http.service';
import {CarrierContractResponseData} from './contracts.service';

export interface PreSignResponse {
    url : string;
    document_id : string;
}

export interface PreSignRequest {
    document_name : string;
}

@Injectable({
    providedIn: 'root'
})
export class DocumentsService {
    constructor (
        private http : HttpService
    ) {}

    fetchDownloadUrl (documentId : string) : Observable<null | string> {
        return this.http.get('endpoint://documents.getDownUrl', {
            urlParams: { documentId }
        }).pipe(
            take(1),
            map(response => response?.url),
            catchError(error => {
                console.warn('fetchDownloadUrl error:', error);
                return throwError(error);
            })
        );
    }

    fetchUploadUrl (data : PreSignRequest) : Observable<PreSignResponse> {
        return this.http.post('endpoint://documents.getUpUrl', {
            body: data
        }).pipe(
            take(1),
            catchError(error => {
                console.warn('fetchUploadUrl error:', error);
                return throwError(error);
            })
        );
    }

    uploadFile (url : string, file : File) : Promise<boolean> {
        return fetch(url, {
            method: 'PUT',
            headers: {
                // 'Content-Type': 'application/octet-stream'
            },
            body: file
        }).then(() => {
            return true;
        }).catch((error) => {
            console.warn('uploadFile error:', error);
            return false;
        });

        /*
        const formData = new FormData();
        formData.append('file', file);

        return this.http.post(url, {
            body: formData,
            reportProgress: false,
        }).pipe(
            take(1),
            // map(response => response.status === 'OK'),
            catchError(error => {
                console.warn('uploadFile error:', error);
                return throwError(error);
            })
        );
         */
    }
}
