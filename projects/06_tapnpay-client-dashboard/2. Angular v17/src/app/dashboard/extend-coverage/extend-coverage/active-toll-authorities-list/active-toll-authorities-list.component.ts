import {Component, Input, OnInit} from '@angular/core';

@Component({
    selector: 'app-active-toll-authorities-list',
    templateUrl: './active-toll-authorities-list.component.html',
    styleUrls: ['./active-toll-authorities-list.component.scss']
})
export class ActiveTollAuthoritiesListComponent implements OnInit {

    @Input() activeList: any;

    constructor() {
    }

    ngOnInit(): void {
    }

}
