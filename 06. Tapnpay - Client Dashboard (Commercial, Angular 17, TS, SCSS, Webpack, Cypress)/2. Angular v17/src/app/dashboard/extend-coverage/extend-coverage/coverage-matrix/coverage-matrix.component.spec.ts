import { ComponentFixture, TestBed } from '@angular/core/testing';

import { CoverageMatrixComponent } from './coverage-matrix.component';

describe('CoverageMatrixComponent', () => {
  let component: CoverageMatrixComponent;
  let fixture: ComponentFixture<CoverageMatrixComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      declarations: [ CoverageMatrixComponent ]
    })
    .compileComponents();
  });

  beforeEach(() => {
    fixture = TestBed.createComponent(CoverageMatrixComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
