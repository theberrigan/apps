import {ChangeDetectionStrategy, Component, OnInit, Renderer2, ViewEncapsulation} from '@angular/core';
import {Router} from '@angular/router';
import {TitleService} from '../../../services/title.service';
import {FormBuilder, FormGroup} from '@angular/forms';

@Component({
    selector: 'contact-us',
    templateUrl: './contact-us.component.html',
    styleUrls: [ './contact-us.component.scss' ],
    changeDetection: ChangeDetectionStrategy.Default,
    encapsulation: ViewEncapsulation.None,
    host: {
        'class': 'contact-us'
    }
})
export class ContactUsComponent implements OnInit {
    constructor (
        private renderer : Renderer2,
        private router : Router,
        private formBuilder : FormBuilder,
        private titleService : TitleService,
    ) {
        window.scroll(0, 0);
    }

    public ngOnInit () {
        this.titleService.setTitle('contact_us.page_title');
    }
}
