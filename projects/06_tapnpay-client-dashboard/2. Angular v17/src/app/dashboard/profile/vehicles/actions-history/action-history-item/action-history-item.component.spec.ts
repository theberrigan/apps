import { ComponentFixture, TestBed } from '@angular/core/testing';

import { ActionHistoryItemComponent } from './action-history-item.component';

describe('ActionHistoryItemComponent', () => {
  let component: ActionHistoryItemComponent;
  let fixture: ComponentFixture<ActionHistoryItemComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      declarations: [ ActionHistoryItemComponent ]
    })
    .compileComponents();

    fixture = TestBed.createComponent(ActionHistoryItemComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
