import { Injectable } from '@angular/core';
import {LangService} from './lang.service';
import {includes} from 'lodash';
import {HttpErrorResponse} from '@angular/common/http';
import {throwError} from 'rxjs';

export const REQUEST_ERRORS = {
    common: [
        'UNKNOWN_ERROR'
    ],
    api: [

    ],
    aws: [

    ],
};

export const DEFAULT_ERROR_KEY = 'errors.common.UNKNOWN_ERROR';

@Injectable({
    providedIn: 'root'
})
export class ErrorsService {
    constructor () {}

    normalizeErrorKey (errorKey : string) : string {
        return errorKey;
    }

    getErrorKey (errorKey : string, sectionKey? : string) : string {
        errorKey = this.normalizeErrorKey(errorKey);

        if (sectionKey && !REQUEST_ERRORS[sectionKey]) {
            return DEFAULT_ERROR_KEY;
        }

        sectionKey = sectionKey || 'common';

        const section = REQUEST_ERRORS[sectionKey];

        return includes(section, errorKey) ? `errors.${ sectionKey }.${ section[errorKey] }` : DEFAULT_ERROR_KEY;
    }

    normalizeRequestError (error : HttpErrorResponse) : any {
        if (error.error instanceof ErrorEvent) {
            // A client-side or network error occurred. Handle it accordingly.
            console.error('Common error occurred:', error.error.message);

            return throwError({
                error,
                code: DEFAULT_ERROR_KEY,
            });
        }

        // The backend returned an unsuccessful response code.
        // The response body may contain clues as to what went wrong,
        console.error(
            `Backend returned code ${error.status}, ` +
            `body was: ${error.error}`);

        return throwError({
            error,
            code: DEFAULT_ERROR_KEY,  // TODO: change to custom
        });
    }
}
