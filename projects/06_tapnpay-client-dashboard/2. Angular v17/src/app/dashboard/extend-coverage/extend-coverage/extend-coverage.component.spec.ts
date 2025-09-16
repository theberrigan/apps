import { ComponentFixture, TestBed } from '@angular/core/testing';

import { ExtendCoverageComponent } from './extend-coverage.component';

describe('ExtendCoverageComponent', () => {
  let component: ExtendCoverageComponent;
  let fixture: ComponentFixture<ExtendCoverageComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      declarations: [ ExtendCoverageComponent ]
    })
    .compileComponents();
  });

  beforeEach(() => {
    fixture = TestBed.createComponent(ExtendCoverageComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
