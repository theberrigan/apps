import {Component, HostBinding, OnInit, ViewEncapsulation} from '@angular/core';
import {TitleService} from '../../../services/title.service';

@Component({
    selector: 'reports',
    templateUrl: './reports.component.html',
    styleUrls: [ './reports.component.scss' ],
    encapsulation: ViewEncapsulation.None,
    host: {
        'class': 'reports',
    }
})
export class ReportsComponent {
    constructor (
        private titleService : TitleService
    ) {
        this.titleService.setTitle('billing.page_title');
    }
}
