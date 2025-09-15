import { Injectable }  from '@angular/core';
import { Title }       from '@angular/platform-browser';
import { LangService } from './lang.service';

@Injectable({
    providedIn: 'root'
})
export class TitleService {
    constructor (
        private title : Title,
        private langService : LangService
    ) {}

    public setRawTitle (title : string, concatTextlake : boolean = true) : void {
        this.title.setTitle(title + (concatTextlake ? ' | Textlake' : ''));
    }

    public setTitle (titleKey : string, titleData? : any, concatTextlake : boolean = true) : void {
        this.langService
            .translateAsync(titleKey, titleData)
            .subscribe(title => this.title.setTitle(title + (concatTextlake ? ' | Textlake' : '')));
    }
}
