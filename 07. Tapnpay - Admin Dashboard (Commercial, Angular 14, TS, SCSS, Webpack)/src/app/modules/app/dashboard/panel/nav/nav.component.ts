import {
    ChangeDetectionStrategy,
    Component,
    OnDestroy,
    OnInit,
    ViewEncapsulation
} from '@angular/core';
import {Subscription} from 'rxjs';
import {UserService} from '../../../../../services/user.service';
import {DomService} from '../../../../../services/dom.service';
import {NavigationEnd, Router} from '@angular/router';


@Component({
    selector: 'nav',
    templateUrl: './nav.component.html',
    styleUrls: [ './nav.component.scss' ],
    changeDetection: ChangeDetectionStrategy.Default,
    encapsulation: ViewEncapsulation.None,
    host: {
        'class': 'nav'
    },
})
export class NavComponent implements OnInit, OnDestroy {
    subs : Subscription[] = [];

    isAccountsVisible : boolean = false;

    isDisputesVisible : boolean = false;

    isFAQVisible : boolean = false;

    isCoverageVisible : boolean = false;

    isTAsVisible : boolean = false;

    isContractsActive : boolean = false;

    isCarrierContractsVisible : boolean = false;

    isTAContractsVisible : boolean = false;

    isPGContractsVisible : boolean = false;

    isContractsVisible : boolean = false;
    /*
    [
        {
            type : 'action' | 'link' | 'menu' | 'etc',
            display : 'i18n.key',
            isActive : boolean,

            url? : string,

            action? : string;

            isOpen? : boolean,
            children? : [

            ]
            permissions : {}
        }
    ]

    */

    constructor (
        private router : Router,
        private domService : DomService,
        private userService : UserService
    ) {
        this.isAccountsVisible = (
            this.userService.checkPermission('ACCOUNT_VIEW_SUMMARY') ||
            this.userService.checkPermission('ACCOUNT_VIEW_OUTSTANDING_INVOICES') ||
            this.userService.checkPermission('ACCOUNT_VIEW_TRANSACTIONS') ||
            this.userService.checkPermission('ACCOUNT_VIEW_SMS') ||
            this.userService.checkPermission('ACCOUNT_VIEW_ACTIONS') ||
            this.userService.checkPermission('ACCOUNT_CLOSE')
        );

        this.isDisputesVisible = this.userService.checkPermission('DISPUTES_UPLOAD');
        this.isFAQVisible = this.userService.checkPermission('FAQ_UPDATE');
        this.isCoverageVisible = this.userService.checkPermission('MAP_EDIT');

        this.isTAsVisible = (
            this.userService.checkPermission('TOLL_AUTHORITY_LIST') ||
            this.userService.checkPermission('TOLL_AUTHORITY_CREATE') ||
            this.userService.checkPermission('TOLL_AUTHORITY_VIEW') ||
            this.userService.checkPermission('TOLL_AUTHORITY_EDIT')
        );

        this.isCarrierContractsVisible = this.userService.checkPermission('CONTRACT_CARRIER_VIEW');
        this.isTAContractsVisible = this.userService.checkPermission('CONTRACT_TOLL_AUTHORITY_VIEW');
        this.isPGContractsVisible = this.userService.checkPermission('CONTRACT_PAYMENT_GATEWAY_VIEW');

        this.isContractsVisible = (
            this.isCarrierContractsVisible ||
            this.isTAContractsVisible ||
            this.isPGContractsVisible
        );
    }

    ngOnInit () : void {
        this.updateActive();

        this.router.events.subscribe((e) => {
            if (e instanceof NavigationEnd) {
                this.updateActive();
            }
        });
    }

    ngOnDestroy () : void {
        this.subs.forEach(sub => sub.unsubscribe());
    }

    updateActive () {
        const routeUrl = this.router.url;

        this.isContractsActive = routeUrl.startsWith('/dashboard/contracts');
    }
}

