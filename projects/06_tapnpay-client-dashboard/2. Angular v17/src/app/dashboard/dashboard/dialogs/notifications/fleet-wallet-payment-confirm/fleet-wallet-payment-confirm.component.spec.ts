import { ComponentFixture, TestBed } from '@angular/core/testing';

import { FleetWalletPaymentConfirmComponent } from './fleet-wallet-payment-confirm.component';

describe('FleetWalletPaymentConfirmComponent', () => {
  let component: FleetWalletPaymentConfirmComponent;
  let fixture: ComponentFixture<FleetWalletPaymentConfirmComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      declarations: [ FleetWalletPaymentConfirmComponent ]
    })
    .compileComponents();

    fixture = TestBed.createComponent(FleetWalletPaymentConfirmComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
