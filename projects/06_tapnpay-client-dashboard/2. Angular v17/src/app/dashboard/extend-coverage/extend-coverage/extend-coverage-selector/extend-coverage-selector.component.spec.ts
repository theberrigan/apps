import { ComponentFixture, TestBed } from '@angular/core/testing';

import { ExtendCoverageSelectorComponent } from './extend-coverage-selector.component';

describe('ExtendCoverageSelectorComponent', () => {
  let component: ExtendCoverageSelectorComponent;
  let fixture: ComponentFixture<ExtendCoverageSelectorComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      declarations: [ ExtendCoverageSelectorComponent ]
    })
    .compileComponents();
  });

  beforeEach(() => {
    fixture = TestBed.createComponent(ExtendCoverageSelectorComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
