import {
    Component, ElementRef,
    EventEmitter,
    HostBinding,
    HostListener,
    Input,
    OnDestroy,
    OnInit,
    Output, Renderer2,
    ViewEncapsulation
} from '@angular/core';
import {DeviceService} from '../../services/device.service';
import {DomService} from '../../services/dom.service';

@Component({
    selector: 'menu',
    exportAs: 'menu',
    templateUrl: './menu.component.html',
    styleUrls: [ './menu.component.scss' ],
    encapsulation: ViewEncapsulation.None,
    host: {
        'class': 'menu'
    }
})
export class MenuComponent implements OnInit, OnDestroy {
    @HostBinding('class.menu_visible')
    public _isActive : boolean = false;

    @Input()
    public get isActive () : boolean {
        return this._isActive;
    }

    public set isActive (value : boolean) {
        this.isActiveChange.emit(this._isActive = !!value);
    };

    @Output()
    public isActiveChange : EventEmitter<boolean> = new EventEmitter<boolean>();

    public id : string = null;

    public maxContentHeight : number = null;

    constructor (
        private el : ElementRef,
        private renderer : Renderer2,
        private deviceService : DeviceService,
        private domService : DomService,
    ) {}

    public ngOnInit () : void {
        this.id = (Math.random()).toString();
        this.updateContentMaxHeight();
    }

    public ngOnDestroy () : void {

    }

    @HostListener('click', [ '$event' ])
    public onClick (e : any) : void {
        const menuEl = this.el.nativeElement;

        let target = e.target;

        while (target && target !== menuEl) {
            if ('toggle' in target.dataset) {
                return;
            }

            target = target.parentNode;
        }

        this.domService.markEvent(e, 'persistentMenuId', this.id);
    }

    @HostListener('document:click', [ '$event' ])
    public onDocumentClick (e : any) : void {
        if (
            this.isActive &&
            this.domService.getEventMark(e, 'persistentMenuId') !== this.id &&
            this.domService.getEventMark(e, 'menuToggle') !== this.id
        ) {
            this.isActive = false;
        }
    }

    @HostListener('window:resize')
    public updateContentMaxHeight () : void {
        this.maxContentHeight = this.deviceService.viewportClientSize.y - 40 - 8 - 1 - 8 - 8 - 1 - 40;
    }

    public toggle (e : any) : void {
        this.domService.markEvent(e, 'menuToggle', this.id);
        this.isActive = !this.isActive;
    }
}
