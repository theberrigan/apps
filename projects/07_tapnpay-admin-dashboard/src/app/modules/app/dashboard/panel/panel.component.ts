import {
    ChangeDetectionStrategy,
    Component, HostListener,
    OnDestroy,
    OnInit,
    Renderer2,
    ViewEncapsulation
} from '@angular/core';
import {Subscription} from 'rxjs';
import {UserService} from '../../../../services/user.service';
import {DomService} from '../../../../services/dom.service';
import {Router} from '@angular/router';


@Component({
    selector: 'panel',
    templateUrl: './panel.component.html',
    styleUrls: [ './panel.component.scss' ],
    changeDetection: ChangeDetectionStrategy.Default,
    encapsulation: ViewEncapsulation.None,
    host: {
        'class': 'panel'
    },
})
export class PanelComponent implements OnInit, OnDestroy {
    subs : Subscription[] = [];

    isUserMenuActive : boolean = false;

    readonly isSearchVisible : boolean = false;

    constructor (
        private router : Router,
        private renderer : Renderer2,
        private userService : UserService,
        private domService : DomService,
    ) {
        this.isSearchVisible = this.userService.checkPermission('ACCOUNT_SEARCH');
    }

    ngOnInit () : void {

    }

    ngOnDestroy () : void {
        this.subs.forEach(sub => sub.unsubscribe());
    }

    onLogout (e : any) {
        this.onUserMenuItemClick(e);
        this.userService.logout();
        this.router.navigateByUrl('/auth');
    }

    onUserMenuItemClick (e : any) {
        this.domService.markEvent(e, 'userItemClick');
    }

    onUserMenuClick (e : any) {
        this.domService.markEvent(e, 'userMenuClick');
    }

    onUserMenuTriggerClick (e : any) {
        this.domService.markEvent(e, 'userTriggerClick');
    }

    @HostListener('document:click', [ '$event' ])
    onDocClick (e : any) {
        if (this.domService.hasEventMark(e, 'userTriggerClick')) {
            this.isUserMenuActive = !this.isUserMenuActive;
        } else if (!this.domService.hasEventMark(e, 'userMenuClick') || this.domService.hasEventMark(e, 'userItemClick')) {
            this.isUserMenuActive = false;
        }
    }
}

