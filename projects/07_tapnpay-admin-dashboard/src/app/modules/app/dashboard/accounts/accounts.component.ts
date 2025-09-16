import {
    ChangeDetectionStrategy,
    Component,
    OnDestroy,
    OnInit,
    Renderer2,
    ViewEncapsulation
} from '@angular/core';
import {ActivatedRoute, Router} from '@angular/router';
import {Subscription} from 'rxjs';
import {TitleService} from '../../../../services/title.service';
import {defer } from '../../../../lib/utils';
import {
    AccountEditorData, AccountEditorTab,
} from './account-editor/account-editor.component';
import {AccountService} from '../../../../services/account.service';
import {UserService} from '../../../../services/user.service';

type State = 'empty' | 'ready';

interface TabContextMenu {
    posX : number;
    posY : number;
    accountId : string;
}

@Component({
    selector: 'accounts',
    templateUrl: './accounts.component.html',
    styleUrls: [ './accounts.component.scss' ],
    changeDetection: ChangeDetectionStrategy.Default,
    encapsulation: ViewEncapsulation.None,
    host: {
        'class': 'accounts',
    }
})
export class AccountsComponent implements OnInit, OnDestroy {
    subs : Subscription[] = [];

    canViewSummary : boolean = false;

    canViewInvoices : boolean = false;

    canViewTransactions : boolean = false;

    canViewSmsLog : boolean = false;

    canViewActions : boolean = false;

    state : State;

    activeAccountId : string;

    accounts : AccountEditorData[] = null;  // null ony for first init, otherwise []

    tabContextMenu : TabContextMenu = null;

    constructor (
        private renderer : Renderer2,
        private router : Router,
        private route : ActivatedRoute,
        private titleService : TitleService,
        private accountService : AccountService,
        private userService : UserService
    ) {
        window.scroll(0, 0);

        this.canViewSummary = this.userService.checkPermission('ACCOUNT_VIEW_SUMMARY');
        this.canViewInvoices = this.userService.checkPermission('ACCOUNT_VIEW_OUTSTANDING_INVOICES');
        this.canViewTransactions = this.userService.checkPermission('ACCOUNT_VIEW_TRANSACTIONS');
        this.canViewSmsLog = this.userService.checkPermission('ACCOUNT_VIEW_SMS');
        this.canViewActions = this.userService.checkPermission('ACCOUNT_VIEW_ACTIONS');
    }

    ngOnInit () {
        this.titleService.setTitle('accounts.page_title');
        this.route.params.subscribe(params => this.init((params || {}).accountId || null));
        console.warn('Init accounts');
    }

    ngOnDestroy () : void {
        this.subs.forEach(sub => sub.unsubscribe());
    }

    init (accountId : string) {
        let activeAccountId : string = null;

        if (this.accounts === null) {
            const data = this.accountService.restoreAccountsFromLocalStorage();

            this.accounts = data.accounts || [];

            this.accounts.forEach(account => {
                // account.accountId
                // account.activeTab
                account.accountData = null;
            });

            if (this.accounts.some(acc => acc.accountId === data.activeAccountId)) {
                activeAccountId = data.activeAccountId;
            } else if (this.accounts.length > 0) {
                activeAccountId = this.accounts[0].accountId;
            } else {
                activeAccountId = null;
            }
        }

        if (accountId) {
            if (this.accounts.some(acc => acc.accountId === accountId) === false) {
                const activeTab : AccountEditorTab = (
                    this.canViewSummary ? 'summary' :
                    this.canViewInvoices ? 'invoices' :
                    this.canViewTransactions ? 'payments' :
                    this.canViewSmsLog ? 'sms_log' :
                    this.canViewActions ? 'actions' : null
                );

                this.accounts.push({
                    accountId,
                    accountPhone: accountId,
                    activeTab,
                    accountData: null,
                });
            }

            activeAccountId = accountId;
        }

        if (this.accounts.length === 0) {
            this.state = 'empty';
            this.activeAccountId = null;
        } else {
            this.state = 'ready';
            this.activeAccountId = activeAccountId;
        }

        this.saveEditorData();
    }

    onSwitchTab (accountId : string) {
        if (accountId) {
            this.router.navigate([ '/dashboard/accounts/', accountId ]);
        } else {
            this.router.navigateByUrl('/dashboard/accounts');
        }
    }

    onEditorChange (data : AccountEditorData) {
        const accountIndex = this.accounts.findIndex(account => account.accountId === data.accountId);

        if (accountIndex >= 0) {
            this.accounts[accountIndex] = data;
            this.saveEditorData();
        }
    }

    onCloseTab (accountId : string) {
        this.tabContextMenu = null;

        if (accountId === this.activeAccountId) {
            const accountIndex = this.accounts.findIndex(account => account.accountId === accountId);

            this.accounts = this.accounts.filter(account => account.accountId !== accountId);

            const newAccountCount = this.accounts.length;

            if (newAccountCount === 0) {
                this.state = 'empty';
                this.saveEditorData();
                this.onSwitchTab(null);
            } else {
                const newAccountIndex = Math.max(0, Math.min(newAccountCount - 1, accountIndex));
                const newAccountId = this.accounts[newAccountIndex].accountId;
                this.saveEditorData();
                this.onSwitchTab(newAccountId);
            }
        } else {
            this.accounts = this.accounts.filter(account => account.accountId !== accountId);
            this.saveEditorData();
        }
    }

    onCloseOtherTabs (accountId : string) {
        this.tabContextMenu = null;
        const accountIndex = this.accounts.findIndex(account => account.accountId === accountId);
        this.accounts = [ this.accounts[accountIndex] ];
        this.saveEditorData();
        this.onSwitchTab(accountId);
    }

    onCloseAllTabs () {
        this.tabContextMenu = null;
        this.accounts = [];
        this.state = 'empty';
        this.saveEditorData();
        this.onSwitchTab(null);
    }

    onCloseTabContextMenu () {
        this.tabContextMenu = null;
    }

    saveEditorData () {
        if (this.accounts.length === 0) {
            this.deleteEditorData();
            return;
        }

        const accounts = this.accounts.map(account => ({
            accountId: account.accountId,
            accountPhone: account.accountPhone,
            activeTab: account.activeTab,
        }));

        this.accountService.saveAccountsToLocalStorage({
            accounts,
            activeAccountId: this.activeAccountId
        });
    }

    deleteEditorData () {
        this.accountService.deleteAccountsFromLocalStorage();
    }

    accountTrackBy (index, item : AccountEditorData) : string {
        return item.accountId;
    }

    onOpenTabContextMenu (e : MouseEvent, account : AccountEditorData) {
        if (e.button !== 2) {  // RMB
            return;
        }

        e.preventDefault();

        this.tabContextMenu = {
            posX: e.clientX,
            posY: e.clientY,
            accountId: account.accountId
        };
    }
}
