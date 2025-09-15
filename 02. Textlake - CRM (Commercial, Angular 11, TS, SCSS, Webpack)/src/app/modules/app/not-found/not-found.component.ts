import { Component, OnInit, NgZone, ViewEncapsulation }      from '@angular/core';
import { Router, ActivatedRoute } from '@angular/router';
import {TitleService} from '../../../services/title.service';

@Component({
    selector: 'not-found',
    templateUrl: './not-found.component.html',
    styleUrls: [ './not-found.component.scss' ],
    encapsulation: ViewEncapsulation.None
})
export class NotFoundComponent implements OnInit {
    public isNotFound : boolean = false;

    constructor (
        public router : Router, 
        public route : ActivatedRoute,
        public zone : NgZone,
        private titleService : TitleService,
    ) {}

    public ngOnInit () : void {
        // /?route=/auth/handle-token?code=1&state=2
        // http://localhost:81/auth/handle-token?code=3054be92-bf1a-462c-b424-ff9e5dd79877&state=vsoPYsgRtJkXEMK8NBTiVJTgovuvgv52#_=_
        const query : any = (
            ((<any>window).initialQueryParams || '')
                .split(/[?&]/g)
                .reduce((acc : any, param : any) => {
                    if (param) {
                        const [ key, value = '' ] : [ string, string ] = param.split('=');
                        acc[key] = decodeURIComponent(value);
                    }
                    return acc;
                }, {})
        );

        if (query.route) {
            let route : string = query.route;

            for (let key in query) {
                if (key != 'route' && query.hasOwnProperty(key)) {
                    route += (route.indexOf('?') > -1 ? '&' : '?') + key + '=' + encodeURIComponent(query[key]);
                }
            }

            console.warn(route);

            // this do not work due to bug in Angular 5.x
            // see https://github.com/angular/angular/issues/18254
            //this.router.navigate([ route ]);

            this.zone.run(() =>  this.router.navigateByUrl(route));
        } else {
            if (!this.route.snapshot.url.length) {
                this.router.navigate([ '/dashboard/offers' ]);
            } else {
                this.isNotFound = true;
                this.titleService.setTitle('not_found.page_title');
                return;
            }
        }
    }
}
