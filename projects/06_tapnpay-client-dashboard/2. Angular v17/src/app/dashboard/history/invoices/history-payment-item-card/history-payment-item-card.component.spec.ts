import { ComponentFixture, TestBed } from '@angular/core/testing';

import { HistoryPaymentItemCardComponent } from './history-payment-item-card.component';

describe('HistoryPaymentItemCardComponent', () => {
  let component: HistoryPaymentItemCardComponent;
  let fixture: ComponentFixture<HistoryPaymentItemCardComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      declarations: [ HistoryPaymentItemCardComponent ]
    })
    .compileComponents();

    fixture = TestBed.createComponent(HistoryPaymentItemCardComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
