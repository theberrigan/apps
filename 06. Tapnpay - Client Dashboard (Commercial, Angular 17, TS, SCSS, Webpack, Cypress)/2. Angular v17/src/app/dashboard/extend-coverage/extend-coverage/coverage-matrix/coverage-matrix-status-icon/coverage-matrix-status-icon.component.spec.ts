import { ComponentFixture, TestBed } from '@angular/core/testing';

import { CoverageMatrixStatusIconComponent } from './coverage-matrix-status-icon.component';

describe('CoverageMatrixStatusIconComponent', () => {
  let component: CoverageMatrixStatusIconComponent;
  let fixture: ComponentFixture<CoverageMatrixStatusIconComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      declarations: [ CoverageMatrixStatusIconComponent ]
    })
    .compileComponents();
  });

  beforeEach(() => {
    fixture = TestBed.createComponent(CoverageMatrixStatusIconComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
