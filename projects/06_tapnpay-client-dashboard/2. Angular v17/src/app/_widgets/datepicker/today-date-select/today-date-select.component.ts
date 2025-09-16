import {Component, EventEmitter, Input, OnInit, Output} from '@angular/core';

@Component({
    selector: 'app-today-date-select',
    templateUrl: './today-date-select.component.html',
    styleUrls: ['./today-date-select.component.css']
})
export class TodayDateSelectComponent implements OnInit {

    @Output() onSelectCurrentDate = new EventEmitter<any>();

    @Input() nowDate: any;

    constructor() {
    }

    ngOnInit(): void {
    }

    emmitCurrentDateSelectEvent() {
        this.onSelectCurrentDate.emit();
    }
}
