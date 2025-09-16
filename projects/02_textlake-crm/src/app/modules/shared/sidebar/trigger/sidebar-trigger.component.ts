import {Component, EventEmitter, Input, OnDestroy, OnInit, Output, ViewEncapsulation} from '@angular/core';
import {DeviceService} from '../../../../services/device.service';
import {SidebarComponent} from '../sidebar.component';

@Component({
    selector: 'sidebar-trigger',
    exportAs: 'sidebar-trigger',
    templateUrl: './sidebar-trigger.component.html',
    encapsulation: ViewEncapsulation.None,
    host: {
        'class': 'sidebar-trigger',
    }
})
export class SidebarTriggerComponent implements OnInit, OnDestroy {
    @Output()
    public onClick = new EventEmitter<any>();

    @Input()
    public hasMark : boolean = false;

    @Input()
    public sidebar : SidebarComponent;

    @Input()
    public isDisabled : boolean = false;

    public get isSidebarActive () : boolean {
        return this.sidebar && this.sidebar.isActive;
    }

    constructor (
        private deviceService : DeviceService
    ) {}

    public ngOnInit () : void {

    }

    public ngOnDestroy () : void {

    }
}
