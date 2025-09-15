import { ComponentFixture, TestBed } from '@angular/core/testing';

import { ActiveTollAuthoritiesListComponent } from './active-toll-authorities-list.component';

describe('ActiveTollAuthoritiesListComponent', () => {
  let component: ActiveTollAuthoritiesListComponent;
  let fixture: ComponentFixture<ActiveTollAuthoritiesListComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      declarations: [ ActiveTollAuthoritiesListComponent ]
    })
    .compileComponents();
  });

  beforeEach(() => {
    fixture = TestBed.createComponent(ActiveTollAuthoritiesListComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
