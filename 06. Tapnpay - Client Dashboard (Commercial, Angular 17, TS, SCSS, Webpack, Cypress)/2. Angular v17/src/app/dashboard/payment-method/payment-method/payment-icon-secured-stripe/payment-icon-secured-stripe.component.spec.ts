import { ComponentFixture, TestBed } from '@angular/core/testing';

import { PaymentIconSecuredStripeComponent } from './payment-icon-secured-stripe.component';

describe('PaymentIconSecuredStripeComponent', () => {
  let component: PaymentIconSecuredStripeComponent;
  let fixture: ComponentFixture<PaymentIconSecuredStripeComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      declarations: [ PaymentIconSecuredStripeComponent ]
    })
    .compileComponents();

    fixture = TestBed.createComponent(PaymentIconSecuredStripeComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
