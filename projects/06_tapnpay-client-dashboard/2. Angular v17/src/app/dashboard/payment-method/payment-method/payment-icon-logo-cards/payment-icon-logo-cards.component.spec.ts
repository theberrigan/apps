import { ComponentFixture, TestBed } from '@angular/core/testing';

import { PaymentIconLogoCardsComponent } from './payment-icon-logo-cards.component';

describe('PaymentIconLogoCardsComponent', () => {
  let component: PaymentIconLogoCardsComponent;
  let fixture: ComponentFixture<PaymentIconLogoCardsComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      declarations: [ PaymentIconLogoCardsComponent ]
    })
    .compileComponents();

    fixture = TestBed.createComponent(PaymentIconLogoCardsComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
