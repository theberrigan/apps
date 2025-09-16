import { ComponentFixture, TestBed } from '@angular/core/testing';

import { SubscriptionSelectComponent } from './subscription-select.component';

describe('SubscriptionSelectComponent', () => {
  let component: SubscriptionSelectComponent;
  let fixture: ComponentFixture<SubscriptionSelectComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      declarations: [ SubscriptionSelectComponent ]
    })
    .compileComponents();

    fixture = TestBed.createComponent(SubscriptionSelectComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
