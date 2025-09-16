import { ComponentFixture, TestBed } from '@angular/core/testing';

import { SubscriptionPaymentPreviewComponent } from './subscription-payment-preview.component';

describe('SubscriptionPaymentPreviewComponent', () => {
  let component: SubscriptionPaymentPreviewComponent;
  let fixture: ComponentFixture<SubscriptionPaymentPreviewComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      declarations: [ SubscriptionPaymentPreviewComponent ]
    })
    .compileComponents();

    fixture = TestBed.createComponent(SubscriptionPaymentPreviewComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
