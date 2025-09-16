import {
    ChangeDetectionStrategy,
    Component, HostListener,
    OnDestroy,
    OnInit,
    Renderer2,
    ViewEncapsulation
} from '@angular/core';
import {Router} from '@angular/router';
import {TitleService} from '../../../services/title.service';
import {Subscription} from 'rxjs';


@Component({
    selector: 'dashboard',
    templateUrl: './dashboard.component.html',
    styleUrls: [ './dashboard.component.scss' ],
    changeDetection: ChangeDetectionStrategy.Default,
    encapsulation: ViewEncapsulation.None,
    host: {
        'class': 'dashboard',
        '[attr.data-bounding]': 'true'
    }
})
export class DashboardComponent implements OnInit, OnDestroy {
    subs : Subscription[] = [];

    constructor (
        private renderer : Renderer2,
        private router : Router,
        private titleService : TitleService,

    ) {
        window.scroll(0, 0);
        this.titleService.setTitle('dashboard.page_title');
    }

    ngOnInit () {
        this.renderer.addClass(document.body, 'dashboard-scroll-y');
    }

    ngOnDestroy () : void {
        this.subs.forEach(sub => sub.unsubscribe());
        this.renderer.removeClass(document.body, 'dashboard-scroll-y');
    }
}
