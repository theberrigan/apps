import { Injectable } from '@angular/core';
import { TranslateService } from '@ngx-translate/core';
import {Observable, throwError} from 'rxjs';
import {CONFIG} from '../../../config/app/dev';
import {HttpService} from './http.service';
import {DebugService} from './debug.service';

export interface ILangFormat {
    input : {
        date : string;
        time : string;
        datetime : string;
    };
    display : {
        date : string;
        time : string;
        datetime : string;
    }
}

export interface ILang {
    code : string;
    name : string;
    isDefault? : boolean;
    format : ILangFormat;
}

export const LANGS : ILang[] = CONFIG.locales;

export const LOCALES : string[] = LANGS.map(lang => lang.code);

export const DEFAULT_LANG : ILang = LANGS.find(l => l.isDefault);

// https://github.com/lephyrus/ngx-translate-messageformat-compiler
@Injectable({
    providedIn: 'root'
})
export class LangService {
    constructor (
        private http : HttpService,
        private translateService : TranslateService,
    ) {
    }

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

    public getCurrentLangCode () : string {
        return this.translateService.currentLang;
    }

    public onLangChange (callback) {
        return this.translateService.onLangChange.subscribe(callback);
    }
}
