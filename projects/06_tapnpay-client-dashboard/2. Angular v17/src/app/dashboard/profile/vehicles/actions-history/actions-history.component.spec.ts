import { ComponentFixture, TestBed } from '@angular/core/testing';

import { ActionsHistoryComponent } from './actions-history.component';

describe('ActionsHistoryComponent', () => {
  let component: ActionsHistoryComponent;
  let fixture: ComponentFixture<ActionsHistoryComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      declarations: [ ActionsHistoryComponent ]
    })
    .compileComponents();

    fixture = TestBed.createComponent(ActionsHistoryComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
