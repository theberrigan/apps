import { ComponentFixture, TestBed } from '@angular/core/testing';

import { PaymentIconLogoPaypalComponent } from './payment-icon-logo-paypal.component';

describe('PaymentIconLogoPaypalComponent', () => {
  let component: PaymentIconLogoPaypalComponent;
  let fixture: ComponentFixture<PaymentIconLogoPaypalComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      declarations: [ PaymentIconLogoPaypalComponent ]
    })
    .compileComponents();

    fixture = TestBed.createComponent(PaymentIconLogoPaypalComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
