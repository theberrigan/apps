import { ComponentFixture, TestBed } from '@angular/core/testing';

import { MoviePopup } from './movie-popup';

describe('MoviePopup', () => {
  let component: MoviePopup;
  let fixture: ComponentFixture<MoviePopup>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [MoviePopup]
    })
    .compileComponents();

    fixture = TestBed.createComponent(MoviePopup);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
