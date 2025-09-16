import { ComponentFixture, TestBed } from '@angular/core/testing';

import { SubscriptionLimitComponent } from './subscription-limit.component';

describe('SubscriptionLimitComponent', () => {
  let component: SubscriptionLimitComponent;
  let fixture: ComponentFixture<SubscriptionLimitComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      declarations: [ SubscriptionLimitComponent ]
    })
    .compileComponents();

    fixture = TestBed.createComponent(SubscriptionLimitComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
