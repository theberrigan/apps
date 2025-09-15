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
import {TermsService} from '../../../services/terms.service';
import {NavService} from '../../../services/nav.service';

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

    @Input()
    showBackButton : boolean = false;

    @Input()
    @HostBinding('class.app-bar_has-border')
    hasBorder : boolean = true;

    @Output()
    onBack = new EventEmitter<void>();

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

    }

    public ngOnDestroy () {
        this.subs.forEach(sub => sub.unsubscribe());
    }

    onTriggerClick () {
        this.navService.navMessagePipe.next({ action: 'toggle' });
    }

    onBackClick () {
        this.onBack.emit()
    }
}
