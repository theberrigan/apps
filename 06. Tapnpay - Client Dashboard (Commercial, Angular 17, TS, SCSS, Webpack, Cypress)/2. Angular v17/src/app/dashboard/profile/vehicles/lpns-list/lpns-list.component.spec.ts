import { ComponentFixture, TestBed } from '@angular/core/testing';

import { LpnsListComponent } from './lpns-list.component';

describe('LpnsListComponent', () => {
  let component: LpnsListComponent;
  let fixture: ComponentFixture<LpnsListComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      declarations: [ LpnsListComponent ]
    })
    .compileComponents();
  });

  beforeEach(() => {
    fixture = TestBed.createComponent(LpnsListComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
