import { ComponentFixture, TestBed } from '@angular/core/testing';

import { LpnCardComponent } from './lpn-card.component';

describe('LpnCardComponent', () => {
  let component: LpnCardComponent;
  let fixture: ComponentFixture<LpnCardComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      declarations: [ LpnCardComponent ]
    })
    .compileComponents();
  });

  beforeEach(() => {
    fixture = TestBed.createComponent(LpnCardComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
