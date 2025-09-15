import { ComponentFixture, TestBed } from '@angular/core/testing';

import { SubscriptionInvoiceCardComponent } from './subscription-invoice-card.component';

describe('SubscriptionInvoiceCardComponent', () => {
  let component: SubscriptionInvoiceCardComponent;
  let fixture: ComponentFixture<SubscriptionInvoiceCardComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      declarations: [ SubscriptionInvoiceCardComponent ]
    })
    .compileComponents();

    fixture = TestBed.createComponent(SubscriptionInvoiceCardComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
