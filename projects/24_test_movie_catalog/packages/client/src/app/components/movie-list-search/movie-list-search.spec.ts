import { ComponentFixture, TestBed } from '@angular/core/testing';

import { MovieListSearch } from './movie-list-search';

describe('MovieListSearch', () => {
  let component: MovieListSearch;
  let fixture: ComponentFixture<MovieListSearch>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [MovieListSearch]
    })
    .compileComponents();

    fixture = TestBed.createComponent(MovieListSearch);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
