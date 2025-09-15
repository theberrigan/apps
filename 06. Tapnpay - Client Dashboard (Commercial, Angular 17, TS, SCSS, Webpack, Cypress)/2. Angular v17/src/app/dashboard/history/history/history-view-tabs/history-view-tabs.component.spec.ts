import { ComponentFixture, TestBed } from '@angular/core/testing';

import { HistoryViewTabsComponent } from './history-view-tabs.component';

describe('HistoryViewTabsComponent', () => {
  let component: HistoryViewTabsComponent;
  let fixture: ComponentFixture<HistoryViewTabsComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      declarations: [ HistoryViewTabsComponent ]
    })
    .compileComponents();

    fixture = TestBed.createComponent(HistoryViewTabsComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
