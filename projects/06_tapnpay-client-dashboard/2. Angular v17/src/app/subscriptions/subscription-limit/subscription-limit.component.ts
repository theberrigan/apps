import {Component, EventEmitter, OnInit, Output} from '@angular/core';
import {SubscriptionApiService} from "../_services/subscription-api.service";

@Component({
  selector: 'app-subscription-limit',
  exportAs: 'app-subscription-limit',
  templateUrl: './subscription-limit.component.html',
  styleUrls: ['./subscription-limit.component.css']
})
export class SubscriptionLimitComponent implements OnInit {

  public isVisible: boolean = false;
  public maxLicensePlates: number;

  @Output()
  cancel = new EventEmitter<void>();

  @Output()
  update = new EventEmitter<void>();

  constructor(
      private subscriptionApiService : SubscriptionApiService
  ) {

  }

  ngOnInit() {
    this.subscriptionApiService.getCurrentSubscription().subscribe((response) => {
      this.maxLicensePlates = response?.max_lp;
      this.isVisible = true;
    });
  }

  onCancelSubscriptionLimit() {
    this.isVisible = false;
    this.cancel.emit();
  }

  onUpdateSubscriptionLimit() {
    this.isVisible = false;
    this.update.emit();
  }

}
