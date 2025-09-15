import {Component, Input, OnDestroy, OnInit, ViewEncapsulation} from '@angular/core';
import {DeviceService} from "../../services/device.service";
import {AccountUserData, UserData, UserService} from "../../services/user.service";
import {Observable, Subscription} from "rxjs";
import { NEO_RIDE_LOGO_URL } from '../../constants/logo.constants';

@Component({
    selector: 'app-dashboard-sidebar',
    templateUrl: './dashboard-sidebar.component.html',
    styleUrls: ['./dashboard-sidebar.component.scss'],
    encapsulation: ViewEncapsulation.None
})
export class DashboardSidebarComponent implements OnInit, OnDestroy {

    readonly sidebarScrollAreaMarginRight: number = -17;

    @Input() isCoverageVisible: () => boolean;
    currentYear: any;
    currentUser: UserData = null;
    public NEO_RIDE_LOGO_URL = NEO_RIDE_LOGO_URL;

    private userDataSubscription : Subscription;

    constructor(private deviceService: DeviceService, private userService: UserService) {
        this.sidebarScrollAreaMarginRight = -1 * this.deviceService.getScrollbarWidth();
        this.currentYear = new Date().getFullYear();
    }

    ngOnInit(): void {
        this.userDataSubscription = this.userService.userData$.subscribe(userData => this.currentUser = userData);
    }

    ngOnDestroy() {
        this.userDataSubscription.unsubscribe();
    }

    isExtendCoverageVisible() {
        const tollAuthority = this.currentUser.account.tollAuthority;
        return this.currentUser && tollAuthority && tollAuthority !== 'NTTA';
    }
}
