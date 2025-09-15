import { ComponentFixture, TestBed } from '@angular/core/testing';

import { NewTestModalComponent } from './new-test-modal.component';

describe('NewTestModalComponent', () => {
  let component: NewTestModalComponent;
  let fixture: ComponentFixture<NewTestModalComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      declarations: [ NewTestModalComponent ]
    })
    .compileComponents();

    fixture = TestBed.createComponent(NewTestModalComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
