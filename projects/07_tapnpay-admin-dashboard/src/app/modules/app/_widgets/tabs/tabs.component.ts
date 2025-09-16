import {
    AfterContentInit,
    ChangeDetectionStrategy,
    Component, ContentChildren, ElementRef, HostBinding, Input,
    OnDestroy,
    OnInit, QueryList,
    ViewChild,
    ViewEncapsulation
} from '@angular/core';
import {Subject, Subscription} from 'rxjs';
import {DeviceService} from '../../../../services/device.service';
import {TabComponent} from './tab/tab.component';
import {startWith, takeUntil} from 'rxjs/operators';


@Component({
    selector: 'tabs',
    templateUrl: './tabs.component.html',
    styleUrls: [ './tabs.component.scss' ],
    changeDetection: ChangeDetectionStrategy.Default,
    encapsulation: ViewEncapsulation.None,
    host: {
        'class': 'tabs'
    },
})
export class TabsComponent implements OnInit, OnDestroy {
    subs : Subscription[] = [];

    contentMarginBottom : number = -17;

    @Input()
    @HostBinding('class.tabs_full-width')
    isFullWidth : boolean = false;

    @Input()
    @HostBinding('class.tabs_center')
    isCentered : boolean = false;

    @ViewChild('contentEl')
    contentEl : ElementRef;

    constructor (
        private deviceService : DeviceService,
    ) {
        this.contentMarginBottom = -1 * this.deviceService.getScrollbarWidth();
    }

    ngOnInit () : void {

    }

    ngOnDestroy () : void {
        this.subs.forEach(sub => sub.unsubscribe());
    }

    onMouseWheel (e : WheelEvent) {
        if (!this.contentEl) {
            return;
        }

        const el : HTMLElement = this.contentEl.nativeElement;

        if (el.scrollWidth <= el.clientWidth) {
            return;
        }

        e.preventDefault();

        const delta : number = e.deltaY || e.deltaX;

        if (delta === 0) {
            return;
        }

        el.scrollLeft += delta;
    }
}

