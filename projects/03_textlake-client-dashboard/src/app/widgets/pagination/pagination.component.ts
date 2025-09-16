import {
    Component, EventEmitter, Input,
    OnDestroy,
    OnInit, Output,
    Renderer2,
    ViewEncapsulation
} from '@angular/core';
import { isFinite } from '../../lib/utils';

export class Pagination {
    first : boolean;        // это первая страница страница?
    previous : boolean;     // есть ли предыдущая страница, противоположно first
    last : boolean;         // это последняя страница?
    next : boolean;         // есть ли следующая страница, противоположно last
    number : number;        // какая страница запрошена
    size : number;          // сколько запрошено
    totalElements : number; // сколько всего элементов с учётом использованных фильтров
    totalPages : number;    // сколько всего страниц с учётом использованных фильтров
}

export class PaginationLoadEvent {
    page : number;
    size : number;
    isContinue : boolean;
}

@Component({
    selector: 'pagination',
    exportAs: 'pagination',
    templateUrl: './pagination.component.html',
    styleUrls: [ './pagination.component.scss' ],
    encapsulation: ViewEncapsulation.None,
    host: {
        'class': 'pagination',
    }
})
export class PaginationComponent implements OnInit, OnDestroy {
    @Output()
    public onLoad = new EventEmitter<PaginationLoadEvent>();

    @Input()
    public isLoading : boolean = false;

    public _data : Pagination;

    @Input()
    public set data (pagination : Pagination) {
        if (pagination) {
            const buttons = [];

            const leftGapFrom = 1;
            const leftGapTo = pagination.number - 2;
            const rightGapFrom = pagination.number + 2;
            const rightGapTo = pagination.totalPages - 2;

            let isPrevGap = false;

            for (let page = 0, max = pagination.totalPages; page < max; page++) {
                const isActive = pagination.number === page;
                const isGap = page >= leftGapFrom && page <= leftGapTo || page >= rightGapFrom && page <= rightGapTo;

                if (isGap && isPrevGap) {
                    continue;
                }

                isPrevGap = isGap;

                buttons.push({
                    page,
                    isGap,
                    isActive,
                    isDisabled: isGap || isActive
                });
            }

            this._data = pagination;
            this.buttons = buttons;
            this.isFirst = pagination.first;
            this.isLast = pagination.last;
            this.page = pagination.number;
            this.size = pagination.size;
            this.totalPages = pagination.totalPages;
        } else {
            this._data = null;
            this.buttons = null;
            this.isFirst = false;
            this.isLast = false;
            this.page = null;
            this.size = null;
            this.totalPages = null;
        }
    }

    public get data () : Pagination {
        return this._data;
    }

    public buttons : any[];

    public isFirst : boolean = false;

    public isLast : boolean = false;

    public page : number;

    public size : number;

    public totalPages : number;

    constructor () {}

    public ngOnInit () : void {

    }

    public ngOnDestroy () : void {

    }

    public onClickLoadMore () : void {
        if (this.isLoading || this.isLast || !isFinite(this.page) || !isFinite(this.size)) {
            return;
        }

        this.onLoad.emit({
            page: this.page + 1,
            size: this.size,
            isContinue: true
        });
    }

    public onClickSpecific (page : number) : void {
        if (this.isLoading || !isFinite(this.size) || !isFinite(page) || !isFinite(this.totalPages) || page < 0 || page >= this.totalPages) {
            return;
        }

        this.onLoad.emit({
            page,
            size: this.size,
            isContinue: false
        });
    }

}
