import { Injectable } from '@angular/core';
import { TranslateService } from '@ngx-translate/core';
import {Observable, throwError} from 'rxjs';
import {CONFIG} from '../../../config/app/dev';
import {catchError, map, retry, take} from 'rxjs/operators';

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
        // private http : HttpService,
        private translateService : TranslateService,
        // private datetimeService : DatetimeService2
    ) {}

    public setDefaultLang (code : string) : void {
        // this.datetimeService.setLocale(code);
        return this.translateService.setDefaultLang(code);
    }

    public use (code : string) : Observable<any> {
        // this.datetimeService.setLocale(code);
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
}
