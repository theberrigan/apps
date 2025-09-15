import { ComponentFixture, TestBed } from '@angular/core/testing';

import { SubscriptionAcknowledgementComponent } from './subscription-acknowledgement.component';

describe('SubscriptionAcknowledgementComponent', () => {
  let component: SubscriptionAcknowledgementComponent;
  let fixture: ComponentFixture<SubscriptionAcknowledgementComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      declarations: [ SubscriptionAcknowledgementComponent ]
    })
    .compileComponents();

    fixture = TestBed.createComponent(SubscriptionAcknowledgementComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
