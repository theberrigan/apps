import {ChangeDetectionStrategy, Component, EventEmitter, Input, Output} from '@angular/core';
import {SubscriptionListItem} from "../../_models/subscription.models";

@Component({
    selector: 'app-subscription-item',
    templateUrl: './subscription-item.component.html',
    styleUrls: ['./subscription-item.component.scss'],
    changeDetection: ChangeDetectionStrategy.OnPush
})
export class SubscriptionItemComponent {
    @Input() plan: SubscriptionListItem;
    @Input() isSelected: boolean;
    @Input() isDisabled: boolean;
    @Output() selectedNewPlan = new EventEmitter<SubscriptionListItem>();


    setSelectedSubscription(plan: SubscriptionListItem) {
        if (this.isDisabled) {
            return;
        }
        this.selectedNewPlan.emit(plan);
    }
}
