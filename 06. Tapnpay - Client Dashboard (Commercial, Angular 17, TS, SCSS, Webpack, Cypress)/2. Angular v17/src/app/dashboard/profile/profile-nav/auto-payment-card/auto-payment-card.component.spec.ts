import { ComponentFixture, TestBed } from '@angular/core/testing';

import { AutoPaymentCardComponent } from './auto-payment-card.component';

describe('AutoPaymentCardComponent', () => {
  let component: AutoPaymentCardComponent;
  let fixture: ComponentFixture<AutoPaymentCardComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      declarations: [ AutoPaymentCardComponent ]
    })
    .compileComponents();

    fixture = TestBed.createComponent(AutoPaymentCardComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
