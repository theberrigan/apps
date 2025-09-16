import { Injectable }  from '@angular/core';
import { Title }       from '@angular/platform-browser';
import { LangService } from './lang.service';
import {ReplaySubject, Subject} from 'rxjs';

@Injectable({
    providedIn: 'root'
})
export class TitleService {
    constructor (
        private title : Title,
        private langService : LangService
    ) {}

    public setRawTitle (title : string, concatTNP : boolean = false) : void {
        this.title.setTitle(title + (concatTNP ? ' | tapNpay Console' : ''));
    }

    public setTitle (titleKey : string, titleData? : any, concatTNP : boolean = false) : void {
        this.langService
            .translateAsync(titleKey, titleData)
            .subscribe(title => this.title.setTitle(title + (concatTNP ? ' | tapNpay Console' : '')));
    }
}
