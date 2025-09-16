import { ComponentFixture, TestBed } from '@angular/core/testing';

import { DebtLockPopupComponent } from './debt-lock-popup.component';

describe('DebtLockPopupComponent', () => {
  let component: DebtLockPopupComponent;
  let fixture: ComponentFixture<DebtLockPopupComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      declarations: [ DebtLockPopupComponent ]
    })
    .compileComponents();

    fixture = TestBed.createComponent(DebtLockPopupComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
