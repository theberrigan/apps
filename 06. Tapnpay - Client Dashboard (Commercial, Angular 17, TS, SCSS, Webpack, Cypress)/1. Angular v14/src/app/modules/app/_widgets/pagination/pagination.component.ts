import {
    Component, EventEmitter, Input,
    OnDestroy,
    OnInit, Output,
    Renderer2,
    ViewEncapsulation
} from '@angular/core';
import { isFinite } from '../../../../lib/utils';

export class Pagination {
    page_size : number;          // сколько запрошено
    page : number;        // какая страница запрошена
    previous : boolean;     // есть ли предыдущая страница, противоположно first
    next : boolean;         // есть ли следующая страница, противоположно last
    total_elements : number; // сколько всего элементов с учётом использованных фильтров
    total_pages : number;    // сколько всего страниц с учётом использованных фильтров
}

export class PaginationLoadEvent {
    page : number;
    size : number;
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
            const leftGapTo = pagination.page - 2;
            const rightGapFrom = pagination.page + 2;
            const rightGapTo = pagination.total_pages - 2;

            let isPrevGap = false;

            for (let page = 0, max = pagination.total_pages; page < max; page++) {
                const isActive = pagination.page === page;
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
            this.page = pagination.page;
            this.size = pagination.page_size;
            this.totalPages = pagination.total_pages;
            this.isVisible = this.buttons.length > 1;
        } else {
            this._data = null;
            this.buttons = null;
            this.page = null;
            this.size = null;
            this.totalPages = null;
            this.isVisible = false;
        }
    }

    public get data () : Pagination {
        return this._data;
    }

    public buttons : any[];

    public page : number;

    public size : number;

    public totalPages : number;

    public isVisible : boolean = false;

    constructor () {}

    public ngOnInit () : void {

    }

    public ngOnDestroy () : void {

    }

    public onClickSpecific (page : number) : void {
        if (this.isLoading || !isFinite(this.size) || !isFinite(page) || !isFinite(this.totalPages) || page < 0 || page >= this.totalPages) {
            return;
        }

        this.onLoad.emit({
            page,
            size: this.size,
        });
    }

}
