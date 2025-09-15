import {
    Component, EventEmitter, HostListener,
    Input, OnInit, Output,
    ViewEncapsulation
} from '@angular/core';
import {ReplaySubject} from 'rxjs';

@Component({
    selector: '.sidebar__label',
    exportAs: 'sidebarLabel',
    templateUrl: './sidebar-label.component.html',
    encapsulation: ViewEncapsulation.None
})
export class SidebarLabelComponent implements OnInit {
    @Input()
    public canCollapse : boolean = false;

    @Input()
    public isCollapsed : boolean = false;

    @Output()
    public isCollapsedChange = new EventEmitter<boolean>();

    public onCollapse = new ReplaySubject<boolean>();

    public ngOnInit () : void {
        this.onCollapse.next(this.isCollapsed);
    }

    @HostListener('click')
    public onClick () : void {
        if (!this.canCollapse) {
            return;
        }

        this.isCollapsed = !this.isCollapsed;
        this.isCollapsedChange.emit(this.isCollapsed);  // for two-ways binding
        this.onCollapse.next(this.isCollapsed);  // for parent sidebar-section
    }
}
