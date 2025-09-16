import {Component, OnInit, NgZone, ViewEncapsulation, ChangeDetectionStrategy} from '@angular/core';
import { Router, ActivatedRoute } from '@angular/router';
import {TitleService} from '../../../services/title.service';

@Component({
    selector: 'not-found',
    exportAs: 'notFound',
    templateUrl: './not-found.component.html',
    styleUrls: [ './not-found.component.scss' ],
    changeDetection: ChangeDetectionStrategy.Default,
    encapsulation: ViewEncapsulation.None,
    host: {
        'class': 'not-found'
    }
})
export class NotFoundComponent implements OnInit {
    constructor (
        public router : Router,
        public titleService : TitleService,
    ) {}

    public ngOnInit () : void {
        // /?route=/dashboard/offers?hello=1&hello2=2#hash=1
        // http://localhost:81/auth/handle-token?code=3054be92-bf1a-462c-b424-ff9e5dd79877&state=vsoPYsgRtJkXEMK8NBTiVJTgovuvgv52#_=_
        this.titleService.setTitle('not_found.page_title');
    }
}
