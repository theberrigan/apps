import { ComponentFixture, TestBed } from '@angular/core/testing';

import { HistoryDateFilterComponent } from './history-date-filter.component';

describe('HistoryDateFilterComponent', () => {
  let component: HistoryDateFilterComponent;
  let fixture: ComponentFixture<HistoryDateFilterComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      declarations: [ HistoryDateFilterComponent ]
    })
    .compileComponents();

    fixture = TestBed.createComponent(HistoryDateFilterComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
