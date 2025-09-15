import {Component, Input} from '@angular/core';

@Component({
    selector: 'app-actions-history',
    templateUrl: './actions-history.component.html',
    styleUrls: ['./actions-history.component.scss']
})
export class ActionsHistoryComponent {
    @Input() historyItems: any;

}
