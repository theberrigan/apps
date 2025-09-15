import {
    Component, EventEmitter, HostBinding, HostListener, Input, OnDestroy, OnInit, Output,
    ViewEncapsulation
} from '@angular/core';
import {DomService} from '../../../../services/dom.service';

@Component({
    selector: 'context-menu',
    exportAs: 'contextMenu',
    templateUrl: './context-menu.component.html',
    styleUrls: [ './context-menu.component.scss' ],
    encapsulation: ViewEncapsulation.None,
    host: {
        'class': 'context-menu',
    }
})
export class ContextMenuComponent implements OnInit, OnDestroy {
    @Input()
    @HostBinding('style.left.px')
    posX : number = 0;

    @Input()
    @HostBinding('style.top.px')
    posY : number = 0;

    @Output()
    onClose = new EventEmitter<void>();

    constructor (
        private domService : DomService
    ) {}

    ngOnInit () {

    }

    ngOnDestroy () {

    }

    @HostListener('document:click', [ '$event' ])
    onDocClick (e : MouseEvent) {
        if (!this.domService.hasEventMark(e, 'contextMenuClick')) {
            this.onClose.emit();
        }
    }

    @HostListener('click', [ '$event' ])
    onHostClick (e : MouseEvent) {
        this.domService.markEvent(e, 'contextMenuClick');
    }
}
