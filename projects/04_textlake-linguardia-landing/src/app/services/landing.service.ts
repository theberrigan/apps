import { Injectable } from '@angular/core';
import {HttpClient} from '@angular/common/http';
import { CONFIG } from '../../../config/app/dev';
import {Observable} from 'rxjs';

@Injectable({
    providedIn: 'root'
})
export class LandingService {
    public serverAPI : string = null;

    constructor (
        public http : HttpClient
    ) {
        this.serverAPI = (CONFIG.server || '').replace(/\/+$/, '');
    }

    public presignFile (fileName : string, recaptchaToken : string) : Observable<any> {
        return this.http.post(this.serverAPI + '/presign', { fileName }, {
            headers: {
                'Linguardia-Recaptcha-Token': recaptchaToken
            }
        });
    }

    public sendRequest (data : any, recaptchaToken : string) : Observable<any> {
        return this.http.post(this.serverAPI + '/submit', data, {
            headers: {
                'Linguardia-Recaptcha-Token': recaptchaToken
            }
        });
    }
}
