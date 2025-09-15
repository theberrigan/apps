import { ComponentFixture, TestBed } from '@angular/core/testing';

import { PaypalRedirectComponent } from './paypal-redirect.component';

describe('PaypalRedirectComponent', () => {
  let component: PaypalRedirectComponent;
  let fixture: ComponentFixture<PaypalRedirectComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      declarations: [ PaypalRedirectComponent ]
    })
    .compileComponents();

    fixture = TestBed.createComponent(PaypalRedirectComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
