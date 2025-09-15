import {
    ChangeDetectionStrategy,
    Component, HostBinding, HostListener, Input,
    OnDestroy,
    OnInit, Output,
    Renderer2,
    ViewEncapsulation,
    EventEmitter
} from '@angular/core';
import {Subject, Subscription} from 'rxjs';
import {DomService} from '../../../../../services/dom.service';

interface TabOnCloseEvent {
    by : 0 | 1 | 2;  // 0 - LMB, 1 - MMB, 2 - Context Menu
}

@Component({
    selector: 'tab',
    templateUrl: './tab.component.html',
    styleUrls: [ './tab.component.scss' ],
    changeDetection: ChangeDetectionStrategy.Default,
    encapsulation: ViewEncapsulation.None,
    host: {
        'class': 'tab'
    },
})
export class TabComponent implements OnInit, OnDestroy {
    subs : Subscription[] = [];

    @Input()
    @HostBinding('class.tab_active')
    isActive = false;

    @Input()
    @HostBinding('class.tab_can-close')
    canClose : boolean = true;

    @Input()
    @HostBinding('class.tab_fixed-width')
    isFixedWidth : boolean = false;

    @Output()
    onClose = new EventEmitter<TabOnCloseEvent>();

    @Output()
    onActivate = new EventEmitter<void>();

    constructor (
        private domService : DomService
    ) {}

    ngOnInit () : void {

    }

    ngOnDestroy () : void {
        this.subs.forEach(sub => sub.unsubscribe());
    }

    onCloseClick (e : MouseEvent) {
        this.domService.markEvent(e, 'tabCloseClick');

        if (!this.canClose) {
            return;
        }

        if (e.button === 0) {
            this.onClose.emit({
                by: 0,
            });
        }
    }

    @HostListener('click', [ '$event' ])
    onClick (e : MouseEvent) {
        if (this.domService.hasEventMark(e, 'tabCloseClick')) {
            return;
        }

        this.onActivate.emit();
    }
}

