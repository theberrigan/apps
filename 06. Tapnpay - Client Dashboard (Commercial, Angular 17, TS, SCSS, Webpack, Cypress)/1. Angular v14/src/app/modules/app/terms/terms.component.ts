import {
    ChangeDetectionStrategy,
    Component, ElementRef,
    OnDestroy,
    OnInit,
    Renderer2,
    ViewChild,
    ViewEncapsulation
} from '@angular/core';
import {ActivatedRoute, Router} from '@angular/router';
import { Location} from '@angular/common';
import {TitleService} from '../../../services/title.service';

@Component({
    selector: 'terms',
    templateUrl: './terms.component.html',
    styleUrls: [ './terms.component.scss' ],
    encapsulation: ViewEncapsulation.None,
    changeDetection: ChangeDetectionStrategy.Default,
    host: {
        'class': 'terms'
    }
})
export class TermsComponent implements OnInit, OnDestroy {
    constructor (
        private renderer : Renderer2,
        private router : Router,
        private route : ActivatedRoute,
        private location : Location,
        private titleService : TitleService,
    ) {
        window.scroll(0, 0);
    }

    public ngOnInit () {
        this.titleService.setTitle('terms.page_title');
    }

    public ngOnDestroy () {

    }
}
