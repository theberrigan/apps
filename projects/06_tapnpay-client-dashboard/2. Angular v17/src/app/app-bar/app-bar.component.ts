import {
    ChangeDetectionStrategy,
    Component, HostBinding,
    Input,
    OnDestroy,
    OnInit, Output,
    Renderer2,
    ViewEncapsulation,
    EventEmitter
} from '@angular/core';
import {Router} from '@angular/router';
import {Subscription} from 'rxjs';
import {TermsService} from '../services/terms.service';
import {NavService} from '../services/nav.service';
import { NEO_RIDE_LOGO_URL } from '../constants/logo.constants';

@Component({
    selector: 'app-bar',
    templateUrl: './app-bar.component.html',
    styleUrls: [ './app-bar.component.scss' ],
    changeDetection: ChangeDetectionStrategy.Default,
    encapsulation: ViewEncapsulation.None,
    host: {
        'class': 'app-bar'
    }
})
export class AppBarComponent implements OnInit, OnDestroy {
    subs : Subscription[] = [];

    hasTermsDot : boolean = false;

    isMobile: boolean = false;
    resizeListener: any;

    @Input()
    showBackButton : boolean = false;

    @Input()
    @HostBinding('class.app-bar_has-border')
    hasBorder : boolean = true;

    @Output()
    onBack = new EventEmitter<void>();

    public NEO_RIDE_LOGO_URL = NEO_RIDE_LOGO_URL;

    constructor (
        private renderer : Renderer2,
        private router : Router,
        private termsService : TermsService,
        private navService : NavService,
    ) {
        this.subs.push(this.termsService.onTermsSessionChange.subscribe(({ hasDot }) => {
            this.hasTermsDot = hasDot;
        }));
    }

    public ngOnInit () {
        this.checkIsMobile();
        this.resizeListener = () => this.checkIsMobile();
        window.addEventListener('resize', this.resizeListener);
    }

    public ngOnDestroy () {
        this.subs.forEach(sub => sub.unsubscribe());
        window.removeEventListener('resize', this.resizeListener);
    }

    checkIsMobile() {
        this.isMobile = window.innerWidth <= 768;
    }

    onTriggerClick () {
        this.navService.navMessagePipe.next({ action: 'toggle' });
    }

    onBackClick () {
        this.onBack.emit()
    }
}
