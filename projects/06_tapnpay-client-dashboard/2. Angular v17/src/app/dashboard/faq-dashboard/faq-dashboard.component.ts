import {ChangeDetectionStrategy, Component, OnInit, Renderer2, ViewEncapsulation} from '@angular/core';
import {Router} from '@angular/router';
import {TitleService} from '../../services/title.service';
import {DeviceService, ViewportBreakpoint} from '../../services/device.service';

@Component({
    selector: 'faq-dashboard',
    templateUrl: './faq-dashboard.component.html',
    styleUrls: [ './faq-dashboard.component.scss' ],
    changeDetection: ChangeDetectionStrategy.Default,
    encapsulation: ViewEncapsulation.None,
    host: {
        'class': 'faq-dashboard'
    }
})
export class FaqDashboardComponent implements OnInit {
    viewportBreakpoint : ViewportBreakpoint;

    constructor (
        private renderer : Renderer2,
        private router : Router,
        private titleService : TitleService,
        private deviceService : DeviceService,
    ) {
        window.scroll(0, 0);

        this.viewportBreakpoint = this.deviceService.viewportBreakpoint;
        this.deviceService.onResize.subscribe((message) => {
            if (message.breakpointChange) {
                this.viewportBreakpoint = message.breakpointChange.current;
            }
        });
    }

    public ngOnInit () {
        this.titleService.setTitle('faq.page_title');
    }
}
