import {
    ChangeDetectionStrategy,
    Component, EventEmitter, Input,
    OnDestroy,
    OnInit, Output,
    ViewEncapsulation
} from '@angular/core';
import {Subscription} from 'rxjs';
import * as copyToClipboard from 'copy-to-clipboard';
import {
    AccountService,
    SMS_LOG_FETCH_COUNT, SmsLogFilters, SmsLogItem, SmsLogRequestData, SmsLogResponse
} from '../../../../../../services/account.service';
import {ToastService} from '../../../../../../services/toast.service';
import {defer} from '../../../../../../lib/utils';
import {DatetimeService} from '../../../../../../services/datetime.service';
import {AccountEditorData} from '../account-editor.component';
import {animate, style, transition, trigger} from '@angular/animations';

type ListState = 'loading' | 'list' | 'empty' | 'error';
type SubmitBy = null | 'page' | 'submit' | 'reset';

@Component({
    selector: 'account-editor-sms-log',
    templateUrl: './account-editor-sms-log.component.html',
    styleUrls: [ './account-editor-sms-log.component.scss' ],
    changeDetection: ChangeDetectionStrategy.Default,
    encapsulation: ViewEncapsulation.None,
    host: {
        'class': 'account-editor-sms-log',
    },
    animations: [
        trigger('smsItemAppear', [
            transition(':enter', [
                style({ transform: 'translateY(15px)' }),
                animate('0.15s cubic-bezier(0.5, 1, 0.89, 1)', style({ transform: 'translateY(0px)' }))
            ])
        ]),
    ],
})
export class AccountEditorSmsLogComponent implements OnInit, OnDestroy {
    subs : Subscription[] = [];

    submitBy : SubmitBy = null;

    fetchSub : Subscription = null;

    filters : SmsLogFilters;

    items : SmsLogItem[];

    nextPageKey : string;

    listState : ListState;

    isDataSet : boolean = false;

    @Input()
    accountId : string;

    @Input()
    set data (data : SmsLogResponse) {
        if (!this.isDataSet) {
            this.filters = data.filters;
            this.items = data.items || [];
            this.nextPageKey = data.exclusive_start_key;
            this.listState = this.items.length > 0 ? 'list' : 'empty';

            this.isDataSet = true;
        }
    }

    @Output()
    dataChange = new EventEmitter<SmsLogResponse>();

    isDateChanged : boolean = false;

    isLoadedMore : boolean = false;

    constructor (
        private accountService : AccountService,
        private datetimeService : DatetimeService,
        private toastService : ToastService
    ) {}

    ngOnInit () {

    }

    ngOnDestroy () : void {
        this.subs.forEach(sub => sub.unsubscribe());
    }

    resetFetchSub () {
        if (this.fetchSub) {
            this.fetchSub.unsubscribe();
            this.fetchSub = null;
        }
    }

    fetchItems () {
        if (this.submitBy === 'submit' || this.submitBy === 'reset') {
            this.items = [];
            this.listState = 'loading';
        }

        this.resetFetchSub();

        if (this.isDateChanged) {
            this.isDateChanged = false;
            this.nextPageKey = null;
        }

        let { from, to } = this.filters;

        if (from && to && new Date(to) < new Date(from)) {
            this.filters.to = from;
        }

        const requestData : SmsLogRequestData = {
            exclusive_start_key: this.nextPageKey,
            page_size: SMS_LOG_FETCH_COUNT,
            from_date: this.filters.from,
            to_date: this.filters.to,
        };

        this.fetchSub = this.accountService.fetchSmsLog(this.accountId, requestData).subscribe(
            ({ exclusive_start_key, items }) => {
                this.nextPageKey = exclusive_start_key;
                this.isLoadedMore = (this.items || []).length > 0;
                this.items = [
                    ...(this.items || []),
                    ...(items || [])
                ];
                this.listState = this.items.length > 0 ? 'list' : 'empty';
                this.submitBy = null;

                this.notifyDataUpdate();
            },
            () => {
                this.nextPageKey = null;
                this.items = [];
                this.listState = 'error';
                this.submitBy = null;

                this.notifyDataUpdate();
            }
        );
    }

    onSubmitFilters () {
        this.nextPageKey = null;
        this.submitBy = 'submit';
        this.fetchItems();
    }

    onResetFilters () {
        this.filters = {
            from: null,
            to: null
        };

        this.submitBy = 'reset';

        defer(() => {
            this.isDateChanged = false;
            this.nextPageKey = null;
            this.fetchItems();
        });
    }

    onNextPage () {
        this.submitBy = 'page';
        this.fetchItems();
    }

    onDateChange () {
        this.isDateChanged = true;
    }

    onCopyItem (item : SmsLogItem) {
        const date = this.datetimeService.format(item.date, 'display.datetime');
        const text = `${ date || '' }\n\n${ item.text || '' }`;

        if (copyToClipboard(text)) {
            this.toastService.create({
                message: [ 'accounts.sms_log.copied' ]
            });
        }
    }

    notifyDataUpdate () {
        this.dataChange.emit({
            filters: this.filters,
            items: this.items,
            exclusive_start_key: this.nextPageKey,
        });
    }
}
