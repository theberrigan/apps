import { Injectable } from '@angular/core';
import { TranslateService } from '@ngx-translate/core';
import {Observable, throwError} from 'rxjs';
import {CONFIG} from '../../../config/app/dev';
import {DatetimeService} from './datetime.service';
import {HttpService} from './http.service';
import {catchError, map, retry, take} from 'rxjs/operators';
import {forOwn} from 'lodash';
import {Currency} from './currencies.service';

export interface ILang {
    code : string;
    name : string;
    nameKey? : string;
    isDefault? : boolean;
}

interface Option {
    value : string;
    display : string;
}

export const LANGS : ILang[] = CONFIG.locales.map((locale : ILang) => {
    locale.nameKey = 'lang.langs.' + locale.code;
    return locale;
});

export const DEFAULT_LANG : ILang = LANGS.find(l => l.isDefault);

@Injectable({
    providedIn: 'root'
})
export class LangService {
    constructor (
        private http : HttpService,
        private translateService : TranslateService,
        private datetimeService : DatetimeService
    ) {}

    public setDefaultLang (code : string) : void {
        this.datetimeService.setLocale(code);
        return this.translateService.setDefaultLang(code);
    }

    public use (code : string) : Observable<any> {
        this.datetimeService.setLocale(code);
        return this.translateService.use(code);
    }

    public getLangByCode (code : string) : ILang {
        return LANGS.find(l => l.code === code);
    }

    public translate (key : string | Array<string>, interpolateParams? : Object) : string | any {
        return this.translateService.instant(key, interpolateParams);
    }

    public translateAsync (key : string | Array<string>, interpolateParams? : Object) : Observable<string | any> {
        return this.translateService.get(key, interpolateParams);
    }

    public fetchLanguages (options : {
        preferredOnly? : boolean,
        addDefault? : boolean,
    } = {
        preferredOnly: false,
        addDefault: false,
    }) : Observable<Option[]> {
        const endpoint = (
            options.preferredOnly === true ?
            'endpoint://languages.getPreferred' :
            'endpoint://languages.getAll'
        );

        return this.http.get(endpoint).pipe(
            retry(1),
            take(1),
            map(response => {
                return [
                    ...(options.addDefault ? [{
                        value: null,
                        display: ''
                    }] : []),
                    ...response.codes.map(code => ({
                        value: code,
                        display: 'langs.' + code.toLowerCase()
                    }))
                ];
            }),
            catchError(error => {
                console.warn('fetchLanguages error:', error);
                return throwError(error);
            })
        );
    }
}
