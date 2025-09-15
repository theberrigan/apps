import { ComponentFixture, TestBed } from '@angular/core/testing';

import { UserMainInfoComponent } from './user-main-info.component';

describe('UserMainInfoComponent', () => {
  let component: UserMainInfoComponent;
  let fixture: ComponentFixture<UserMainInfoComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      declarations: [ UserMainInfoComponent ]
    })
    .compileComponents();

    fixture = TestBed.createComponent(UserMainInfoComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
