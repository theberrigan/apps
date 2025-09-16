import { ComponentFixture, TestBed } from '@angular/core/testing';

import { AccountNotificationPopupComponent } from './account-notification-popup.component';

describe('AccountNotificationPopupComponent', () => {
  let component: AccountNotificationPopupComponent;
  let fixture: ComponentFixture<AccountNotificationPopupComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [AccountNotificationPopupComponent]
    })
    .compileComponents();
    
    fixture = TestBed.createComponent(AccountNotificationPopupComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
