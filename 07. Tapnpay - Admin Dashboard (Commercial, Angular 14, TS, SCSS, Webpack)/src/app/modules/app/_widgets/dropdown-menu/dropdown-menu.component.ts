import {
    Component, ElementRef, EventEmitter, HostBinding, HostListener, Input, OnDestroy, OnInit, Output, Renderer2,
    ViewEncapsulation
} from '@angular/core';
import {DomService} from '../../../../services/dom.service';

let uniqueMenuId = 0;

@Component({
    selector: 'dropdown-menu',
    exportAs: 'dropdownMenu',
    templateUrl: './dropdown-menu.component.html',
    styleUrls: [ './dropdown-menu.component.scss' ],
    encapsulation: ViewEncapsulation.None,
    host: {
        'class': 'dropdown-menu',
    }
})
export class DropdownMenuComponent implements OnInit, OnDestroy {
    @Output()
    onDeactivateRequest = new EventEmitter<void>();

    @Input()
    isAutoDeactivate : boolean = true;

    @Input()
    set trigger (el : HTMLElement) {
        this.resetTriggerListener();

        this._trigger = el || null;

        if (this._trigger) {
            this.triggerUnlisten = this.renderer.listen(this._trigger, 'click', (e) => this.onTriggerClick(e));
        }
    }

    get trigger () : null | HTMLElement {
        return this._trigger;
    }

    _trigger : HTMLElement = null;

    triggerUnlisten : () => void;

    isActive : boolean = false;

    readonly id : string = String(++uniqueMenuId);

    readonly ignoreEventMark : string;

    constructor (
        private hostEl : ElementRef,
        private renderer : Renderer2,
        private domService : DomService,
    ) {
        this.ignoreEventMark = `cm_1_${ this.id }`;
    }

    ngOnInit () {

    }

    ngOnDestroy () {
        this.resetTriggerListener();
    }

    resetTriggerListener () {
        if (this.triggerUnlisten) {
            this.triggerUnlisten();
            this.triggerUnlisten = null;
        }
    }

    @HostListener('document:click', [ '$event' ])
    onDocClick (e : MouseEvent) {
        if (!this.domService.hasEventMark(e, this.ignoreEventMark)) {
            this.onShouldDeactivate();
        }
    }

    @HostListener('click', [ '$event' ])
    onHostClick (e : MouseEvent) {
        const hostEl = this.hostEl.nativeElement;

        for (let el : HTMLElement = <HTMLElement>e.target; el && el !== hostEl; el = el.parentElement) {
            if (el.classList.contains('dropdown-menu__item') && !el.classList.contains('dropdown-menu__item_disabled')) {
                this.onShouldDeactivate();
                break;
            }
        }

        this.domService.markEvent(e, this.ignoreEventMark);
    }

    onTriggerClick (e : MouseEvent) {
        this.domService.markEvent(e, this.ignoreEventMark);
        this.toggle();
    }

    onShouldDeactivate () {
        if (this.isAutoDeactivate) {
            this.deactivate();
        } else {
            this.onDeactivateRequest.emit();
        }
    }

    toggle () {
        this.isActive = !this.isActive;
    }

    activate () {
        this.isActive = true;
    }

    deactivate () {
        this.isActive = false;
    }
}

// TODO:
// - _disabled
