import {Component, OnDestroy, OnInit, Renderer2, ViewEncapsulation} from '@angular/core';
import { DeviceService } from '../../../services/device.service';

@Component({
    selector: 'action-panel',
    templateUrl: './action-panel.component.html',
    styleUrls: [ './action-panel.component.scss' ],
    encapsulation: ViewEncapsulation.None,
    host: {
        'class': 'action-panel',
    }
})
export class ActionPanelComponent implements OnInit, OnDestroy {
    public isActive : true;

    public dashboardEl : any;

    constructor (
        private renderer : Renderer2,
    ) {
        this.dashboardEl = document.querySelector('dashboard.dashboard');
    }

    public ngOnInit () : void {
        this.renderer.addClass(this.dashboardEl, 'dashboard_action-panel-active');
    }

    public ngOnDestroy () : void {
        this.renderer.removeClass(this.dashboardEl, 'dashboard_action-panel-active');
    }
}
