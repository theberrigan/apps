import { ComponentFixture, TestBed } from '@angular/core/testing';

import { LpnListCardComponent } from './lpn-list-card.component';

describe('LpnListCardComponent', () => {
  let component: LpnListCardComponent;
  let fixture: ComponentFixture<LpnListCardComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      declarations: [ LpnListCardComponent ]
    })
    .compileComponents();

    fixture = TestBed.createComponent(LpnListCardComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
