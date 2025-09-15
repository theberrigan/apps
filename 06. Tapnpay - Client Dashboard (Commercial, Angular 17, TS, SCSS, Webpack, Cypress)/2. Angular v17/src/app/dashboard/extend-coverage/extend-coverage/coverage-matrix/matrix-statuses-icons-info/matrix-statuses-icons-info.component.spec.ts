import { ComponentFixture, TestBed } from '@angular/core/testing';

import { MatrixStatusesIconsInfoComponent } from './matrix-statuses-icons-info.component';

describe('MatrixStatusesIconsInfoComponent', () => {
  let component: MatrixStatusesIconsInfoComponent;
  let fixture: ComponentFixture<MatrixStatusesIconsInfoComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      declarations: [ MatrixStatusesIconsInfoComponent ]
    })
    .compileComponents();
  });

  beforeEach(() => {
    fixture = TestBed.createComponent(MatrixStatusesIconsInfoComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
