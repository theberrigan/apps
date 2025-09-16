import { ComponentFixture, TestBed } from '@angular/core/testing';

import { PaymentIconLogoGooglePlayComponent } from './payment-icon-logo-google-play.component';

describe('PaymentIconLogoGooglePlayComponent', () => {
  let component: PaymentIconLogoGooglePlayComponent;
  let fixture: ComponentFixture<PaymentIconLogoGooglePlayComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      declarations: [ PaymentIconLogoGooglePlayComponent ]
    })
    .compileComponents();

    fixture = TestBed.createComponent(PaymentIconLogoGooglePlayComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
