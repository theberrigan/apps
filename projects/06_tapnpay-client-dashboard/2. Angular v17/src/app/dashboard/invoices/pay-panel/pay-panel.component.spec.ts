import { ComponentFixture, TestBed } from '@angular/core/testing';

import { PayPanelComponent } from './pay-panel.component';

describe('PayPanelComponent', () => {
  let component: PayPanelComponent;
  let fixture: ComponentFixture<PayPanelComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      declarations: [ PayPanelComponent ]
    })
    .compileComponents();

    fixture = TestBed.createComponent(PayPanelComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
