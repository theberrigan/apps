import {Component, EventEmitter, HostListener, Input, Output, ViewChild} from '@angular/core';
import {DatepickerComponent} from "../../../../_widgets/datepicker/datepicker.component";
import {DomService} from "../../../../services/dom.service";
import {deburr} from "lodash-es";

export interface Filters {
    from: string;
    to: string;
}

@Component({
    selector: 'app-history-date-filter',
    templateUrl: './history-date-filter.component.html',
    styleUrls: ['./history-date-filter.component.css']
})
export class HistoryDateFilterComponent {

    @Output() filtersTriggerClick = new EventEmitter<MouseEvent>();
    @Output() filtersChange = new EventEmitter<Filters>();
    @Output() resetFiltersClick = new EventEmitter<boolean>();
    isFiltersVisible: boolean = false;

    filters: Filters = {
        from: '',
        to: ''
    }

    readonly defaultFilters: Filters = {
        from: '1970-01-01T00:00:00.000Z',
        to: '2030-01-01T00:00:00.000Z'
    };

    constructor(private domService: DomService) {
        const currentTime = new Date();

        this.defaultFilters = {
            from: new Date(currentTime.getTime() - (30 * 24 * 60 * 60 * 1000)).toISOString(),
            to: currentTime.toISOString(),
        };

        this.filters = {
            from: this.defaultFilters.from,
            to: this.defaultFilters.to
        }
    }

    onResetFiltersClick() {
        this.filters = {
            from: this.defaultFilters.from,
            to: this.defaultFilters.to
        }
        this.isFiltersVisible = false;
        this.resetFiltersClick.emit(true);
    }

    onFiltersChange() {
        this.isFiltersVisible = false;
        this.filtersChange.emit(this.filters);
    }

    @ViewChild('dpFrom', {read: DatepickerComponent})
    dpFrom: DatepickerComponent;

    @ViewChild('dpTo', {read: DatepickerComponent})
    dpTo: DatepickerComponent;

    @HostListener('document:click', ['$event'])
    onDocClick(e: Event) {
        console.log(e);
        if (
            !this.domService.isHasEventMark(e, 'filtersTriggerClick') &&
            !this.domService.isHasEventMark(e, 'filtersPopupClick') &&
            !this.domService.isHasEventMark(e, 'datepickerClick')
        ) {
            this.isFiltersVisible = false;
        }
    }

    onFiltersPopupClick($event: MouseEvent) {
        this.domService.markEvent($event, 'filtersPopupClick');
    }

    onFiltersTriggerClick(e: Event) {
        this.isFiltersVisible = !this.isFiltersVisible;
        this.domService.markEvent(e, 'filtersTriggerClick');
    }
}
