import { ComponentFixture, TestBed } from '@angular/core/testing';

import { TodayDateSelectComponent } from './today-date-select.component';

describe('TodayDateSelectComponent', () => {
  let component: TodayDateSelectComponent;
  let fixture: ComponentFixture<TodayDateSelectComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      declarations: [ TodayDateSelectComponent ]
    })
    .compileComponents();
  });

  beforeEach(() => {
    fixture = TestBed.createComponent(TodayDateSelectComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
