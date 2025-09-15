import { ComponentFixture, TestBed } from '@angular/core/testing';

import { ExtendCoverageNotificationMessageComponent } from './extend-coverage-notification-message.component';

describe('ExtendCoverageNotificationMessageComponent', () => {
  let component: ExtendCoverageNotificationMessageComponent;
  let fixture: ComponentFixture<ExtendCoverageNotificationMessageComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      declarations: [ ExtendCoverageNotificationMessageComponent ]
    })
    .compileComponents();
  });

  beforeEach(() => {
    fixture = TestBed.createComponent(ExtendCoverageNotificationMessageComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
