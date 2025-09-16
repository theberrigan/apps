import {ChangeDetectionStrategy, Component, Input, OnChanges, OnInit, SimpleChanges} from '@angular/core';
import {InvoiceHistoryItem} from "../history.service";
import {TitleService} from "../../../services/title.service";
import {ListState} from "../history/history.component";

@Component({
    selector: 'app-invoices',
    templateUrl: './invoices.component.html',
    styleUrls: ['./invoices.component.scss'],
    changeDetection: ChangeDetectionStrategy.OnPush,
})
export class InvoicesComponent implements OnInit, OnChanges {
    @Input() listState: ListState;
    @Input() isLoadingPage: boolean = false;
    @Input() invoices: InvoiceHistoryItem[];
    invoicesByDate: Array<{ date: string, invoices: InvoiceHistoryItem[] }> = [];

    constructor(private titleService: TitleService) {
    }

    ngOnInit(): void {
        this.titleService.setTitle('history.invoice.page_title');
    }

    ngOnChanges(changes: SimpleChanges) {
        if (changes.invoices && changes.invoices.currentValue) {
            this.invoicesByDate = this.groupByDateTimePerMinutes(changes.invoices.currentValue);
        }
    }

    groupByDateTimePerMinutes(items: InvoiceHistoryItem[]): Array<{ date: string, invoices: InvoiceHistoryItem[] }> {
        const groupedByDateTime: { [key: string]: InvoiceHistoryItem[] } = {};

        // Grouping invoices by date and time with difference less than 2 seconds
        items.forEach(item => {
            const dateTimeKey = new Date(item.payment_date).toISOString().slice(0, 19); // Considering date and time up to seconds
            if (!groupedByDateTime[dateTimeKey]) {
                groupedByDateTime[dateTimeKey] = [];
            }
            groupedByDateTime[dateTimeKey].push(item);
        });

        // Converting groupedByDateTime object to the desired array format
        return Object.keys(groupedByDateTime).map(dateTimeKey => ({
            date: dateTimeKey,
            invoices: groupedByDateTime[dateTimeKey]
        }));
    }

}
