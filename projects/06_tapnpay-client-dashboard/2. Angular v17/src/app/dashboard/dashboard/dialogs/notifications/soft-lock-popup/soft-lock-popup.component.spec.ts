import { ComponentFixture, TestBed } from '@angular/core/testing';

import { SoftLockPopupComponent } from './soft-lock-popup.component';

describe('SoftLockPopupComponent', () => {
  let component: SoftLockPopupComponent;
  let fixture: ComponentFixture<SoftLockPopupComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      declarations: [ SoftLockPopupComponent ]
    })
    .compileComponents();

    fixture = TestBed.createComponent(SoftLockPopupComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
