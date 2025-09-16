import {ChangeDetectionStrategy, Component, OnInit, Renderer2, ViewEncapsulation} from '@angular/core';
import {Router} from '@angular/router';
import {TitleService} from '../../services/title.service';

@Component({
    selector: 'faq',
    templateUrl: './faq.component.html',
    styleUrls: [ './faq.component.scss' ],
    changeDetection: ChangeDetectionStrategy.Default,
    encapsulation: ViewEncapsulation.None,
    host: {
        'class': 'faq'
    }
})
export class FaqComponent implements OnInit {

    constructor (
        private renderer : Renderer2,
        private router : Router,
        private titleService : TitleService,
    ) {
        window.scroll(0, 0);
    }

    public ngOnInit () {
        this.titleService.setTitle('faq.page_title');
    }
}
