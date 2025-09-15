import { ComponentFixture, TestBed } from '@angular/core/testing';

import { SubscriptionInfoCardComponent } from './subscription-info-card.component';

describe('SubscriptionInfoCardComponent', () => {
  let component: SubscriptionInfoCardComponent;
  let fixture: ComponentFixture<SubscriptionInfoCardComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      declarations: [ SubscriptionInfoCardComponent ]
    })
    .compileComponents();

    fixture = TestBed.createComponent(SubscriptionInfoCardComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
