import {Component, Input} from '@angular/core';

@Component({
    selector: 'app-action-history-item',
    templateUrl: './action-history-item.component.html',
    styleUrls: ['./action-history-item.component.scss']
})
export class ActionHistoryItemComponent {
    @Input() date: string;
    @Input() type: 'START' | 'END';
    @Input() isPeriodEnded: boolean = false;

}
