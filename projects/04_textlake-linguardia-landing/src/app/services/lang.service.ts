import { Injectable } from '@angular/core';
import { TranslateService } from '@ngx-translate/core';
import {Observable, throwError} from 'rxjs';
import {catchError, map, retry, take} from 'rxjs/operators';
import {forOwn} from 'lodash';
import {CONFIG} from '../../../config/app/dev';

export interface ILang {
    code : string;
    name : string;
    nameKey? : string;
    isDefault? : boolean;
}

export const LANGS : ILang[] = CONFIG.locales.map((locale : ILang) => {
    locale.nameKey = 'langs.' + locale.code;
    return locale;
});

export const DEFAULT_LANG : ILang = LANGS.find(l => l.isDefault);

@Injectable({
    providedIn: 'root'
})
export class LangService {
    constructor (
        private translateService : TranslateService
    ) {}

    public setDefaultLang (code : string) : void {
        return this.translateService.setDefaultLang(code);
    }

    public use (code : string) : Observable<any> {
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
