import {
    ChangeDetectionStrategy,
    Component, EventEmitter, Input,
    OnDestroy,
    OnInit, Output,
    ViewEncapsulation
} from '@angular/core';
import {Subscription} from 'rxjs';
import {
    AccountService, InvoiceExtension, OutstandingInvoice, OutstandingInvoiceWithExtension,
    SMS_LOG_FETCH_COUNT,
    TRANSACTION_FETCH_COUNT,
    TransactionResponse
} from '../../../../../services/account.service';
import {UserService} from '../../../../../services/user.service';

export type AccountEditorTab = 'summary' | 'invoices' | 'payments' | 'disputes' | 'sms_log' | 'actions';
export type AccountEditorState = 'default' | 'init' | 'error' | 'ready';

export interface AccountTabData {
    data : any;
    state : AccountEditorState;
    lastUpdateDate : number;
}

export type AccountData = {
    [ key in AccountEditorTab ] : AccountTabData;
}

export interface AccountEditorData {
    accountId : string;
    accountPhone : string;
    activeTab : AccountEditorTab;
    accountData? : AccountData;
}

const LAST_UPDATE_THRESHOLD = 20 * 60 * 1000;  // 20 min

@Component({
    selector: 'account-editor',
    templateUrl: './account-editor.component.html',
    styleUrls: [ './account-editor.component.scss' ],
    changeDetection: ChangeDetectionStrategy.Default,
    encapsulation: ViewEncapsulation.None,
    host: {
        'class': 'account-editor',
    }
})
export class AccountEditorComponent implements OnInit, OnDestroy {
    subs : Subscription[] = [];

    canViewSummary : boolean = false;

    canViewInvoices : boolean = false;

    canViewTransactions : boolean = false;

    canViewDisputes : boolean = false;

    canViewSmsLog : boolean = false;

    canViewActions : boolean = false;

    editorData : AccountEditorData = null;

    accountId : string;

    accountPhone : string;

    activeTab : AccountEditorTab;

    accountData : AccountData;

    isDataSet : boolean = false;

    @Input()
    set data (data : AccountEditorData) {
        if (!this.isDataSet) {
            this.accountId = data.accountId;
            this.accountPhone = data.accountPhone;
            this.accountData = data.accountData;

            if (!this.accountData) {
                this.accountData = {
                    'summary': {
                        data: null,
                        state: 'default',
                        lastUpdateDate: 0,
                    },
                    'invoices': {
                        data: null,
                        state: 'default',
                        lastUpdateDate: 0,
                    },
                    'payments': {
                        data: null,
                        state: 'default',
                        lastUpdateDate: 0,
                    },
                    'disputes': {
                        data: null,
                        state: 'default',
                        lastUpdateDate: 0,
                    },
                    'sms_log': {
                        data: null,
                        state: 'default',
                        lastUpdateDate: 0,
                    },
                    'actions': {
                        data: {},
                        state: 'ready',
                        lastUpdateDate: 0,
                    },
                };
            }

            this.isDataSet = true;

            this.onSwitchTab(data.activeTab);
        }
    }

    @Output()
    dataChange = new EventEmitter<AccountEditorData>();

    constructor (
        private accountService : AccountService,
        private userService : UserService
    ) {
        this.canViewSummary = this.userService.checkPermission('ACCOUNT_VIEW_SUMMARY');
        this.canViewInvoices = this.userService.checkPermission('ACCOUNT_VIEW_OUTSTANDING_INVOICES');
        this.canViewTransactions = this.userService.checkPermission('ACCOUNT_VIEW_TRANSACTIONS');
        this.canViewDisputes = this.userService.checkPermission('ACCOUNT_VIEW_DISPUTES');
        this.canViewSmsLog = this.userService.checkPermission('ACCOUNT_VIEW_SMS');
        this.canViewActions = (
            this.userService.checkPermission('ACCOUNT_VIEW_ACTIONS') ||
            this.userService.checkPermission('ACCOUNT_CLOSE')
        );
    }

    ngOnInit () {

    }

    ngOnDestroy () : void {
        this.subs.forEach(sub => sub.unsubscribe());
    }

    async fetchSummaryTab () {
        if (this.checkMustReloadTab(this.accountData.summary)) {
            this.accountData.summary.state = 'init';

            const response = await this.accountService.fetchSummary(this.accountId).toPromise().catch(() => null);

            this.accountData.summary.state = response ? 'ready' : 'error';
            this.accountData.summary.data = response;
            this.accountData.summary.lastUpdateDate = Date.now();

            this.notifyDataUpdate();
        }
    }

    async onSwitchTab (tab : AccountEditorTab) {
        if (
            this.activeTab === tab ||
            (tab === 'summary' && !this.canViewSummary) ||
            (tab === 'invoices' && !this.canViewInvoices) ||
            (tab === 'payments' && !this.canViewTransactions) ||
            (tab === 'disputes' && !this.canViewDisputes) ||
            (tab === 'sms_log' && !this.canViewSmsLog) ||
            (tab === 'actions' && !this.canViewActions)
        ) {
            return;
        }

        this.activeTab = tab;

        // Summary tab must always be loaded, phoneNumber required for tab title
        if (this.canViewSummary) {
            this.fetchSummaryTab();
        }

        if (this.activeTab !== 'summary') {
            let tabData = this.accountData[tab];

            if (this.checkMustReloadTab(tabData)) {
                let response = null;

                tabData.state = 'init';

                switch (tab) {
                    case 'invoices':
                        response = await this.accountService.fetchExtendedInvoices(this.accountId).catch(() => null);
                        break;
                    case 'payments':
                        response = await this.accountService.fetchTransactions(this.accountId, {
                            page: 0,
                            page_size: TRANSACTION_FETCH_COUNT,
                            include_succeeded: true,
                            include_failed: true
                        }).toPromise().catch(() => null);

                        if (response) {
                            response.filters = {
                                visibility: 0
                            };
                        }

                        break;
                    case 'disputes':
                        response = await this.accountService.fetchDisputes(this.accountId).toPromise().catch(() => null);
                        break;
                    case 'sms_log':
                        response = await this.accountService.fetchSmsLog(this.accountId, {
                            page_size: SMS_LOG_FETCH_COUNT,
                            exclusive_start_key: null,
                            from_date: null,
                            to_date: null
                        }).toPromise().catch(() => null);

                        if (response) {
                            response.filters = {
                                from: null,
                                to: null,
                            };
                        }

                        break;
                    case 'actions':
                        response = await this.accountService.fetchSummary(this.accountId).toPromise().catch(() => null);

                        if (response) {
                            response = {
                                lastPIN: null,
                                summaryData: response
                            };
                        }
                        break;
                }

                tabData = this.accountData[tab];

                tabData.state = response ? 'ready' : 'error';
                tabData.data = response;
                tabData.lastUpdateDate = Date.now();
            }
        }

        this.notifyDataUpdate();
    }

    checkMustReloadTab (tabData : AccountTabData) {
        const timeFromLastUpdate = Date.now() - tabData.lastUpdateDate;
        const mustReload = tabData.state === 'ready' && timeFromLastUpdate >= LAST_UPDATE_THRESHOLD;

        return tabData.state === 'default' || tabData.state === 'error' || mustReload;
    }

    notifyDataUpdate () {
        this.dataChange.emit({
            accountId: this.accountId,
            accountPhone: this.accountData?.summary?.data?.phone_number || this.accountPhone,
            activeTab: this.activeTab,
            accountData: this.accountData,
        });
    }

    onTabDataChange (tab : AccountEditorTab, data : any) {
        this.accountData[tab].data = data;

        // Actions tab uses same data as Summary tab,
        // so if Actions tab updates data, update it for summary tab too
        if (tab === 'actions') {
            this.accountData.summary.data = data.summaryData;
        }

        this.notifyDataUpdate();
    }
}
