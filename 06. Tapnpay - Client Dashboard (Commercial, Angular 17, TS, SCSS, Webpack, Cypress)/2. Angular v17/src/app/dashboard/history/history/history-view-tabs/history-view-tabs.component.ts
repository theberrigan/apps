import {Component, EventEmitter, Input, Output, ViewEncapsulation} from '@angular/core';

type ActiveTab = 'invoices' | 'transactions' | 'disputes';

@Component({
    selector: 'app-history-view-tabs',
    templateUrl: './history-view-tabs.component.html',
    styleUrls: ['./history-view-tabs.component.scss'],
    encapsulation: ViewEncapsulation.None,
})
export class HistoryViewTabsComponent {
    @Input() activeTab: ActiveTab = 'invoices';
    @Output() setActiveTab: EventEmitter<ActiveTab> = new EventEmitter<ActiveTab>();

    onSwitchTab(tabName: ActiveTab): void {
        this.activeTab = tabName;
        this.setActiveTab.emit(tabName);
    }
}
