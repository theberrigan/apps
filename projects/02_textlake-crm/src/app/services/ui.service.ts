import { Injectable } from '@angular/core';
import {Subject} from 'rxjs';

export class Paginator {
    // ---------------------------
    first : boolean;        // это первая страница страница?
    previous : boolean;     // есть ли предыдущая страница, противоположно first
    last : boolean;         // это последняя страница?
    next : boolean;         // есть ли следующая страница, противоположно last
    number : number;        // какая страница запрошена
    size : number;          // сколько запрошено
    totalElements : number; // сколько всего элементов с учётом использованных фильтров
    totalPages : number;    // сколько всего страниц с учётом использованных фильтров

    constructor (init : Partial<Paginator> = {}) {
        Object.assign(this, init);
    }
}

@Injectable({
    providedIn: 'root'
})
export class UiService {
    public onGoBack = new Subject<void>();

    public onSetupBackButton = new Subject<boolean>();

    constructor () {}

    public activateBackButton () : Subject<void> {
        this.onSetupBackButton.next(true);
        return this.onGoBack;
    }

    public deactivateBackButton () : void {
        this.onSetupBackButton.next(false);
    }
}
