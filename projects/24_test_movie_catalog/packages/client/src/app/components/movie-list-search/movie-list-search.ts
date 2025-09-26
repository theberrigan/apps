import { Component, inject, OnInit, output, ViewEncapsulation } from '@angular/core';
import { ReactiveFormsModule, FormsModule, FormControl } from '@angular/forms';
import {
    debounceTime,
    distinctUntilChanged,
    switchMap,
    tap,
} from 'rxjs';
import { MoviesService } from '../../services/movies';
import { MovieListError, MovieListResponse, SearchResultEvent } from '../../types/movies';
import { LoadingState } from '../../types/common';


@Component({
    selector: 'movie-list-search',
    imports: [
        ReactiveFormsModule,
        FormsModule,
    ],
    templateUrl: './movie-list-search.html',
    styleUrl: './movie-list-search.scss',
    encapsulation: ViewEncapsulation.None,
    host: {
        class: 'movie-list-search'
    }
})
export class MovieListSearch implements OnInit {
    protected searchControl = new FormControl('');

    protected moviesService = inject(MoviesService);

    protected stateChange = output<SearchResultEvent>();

    protected state : LoadingState = LoadingState.None;

    async ngOnInit () : Promise<void> {
        this.searchControl.valueChanges
            .pipe(
                tap(() => {
                    this.setState(LoadingState.Loading, [], null);
                }),
                debounceTime(500),
                distinctUntilChanged(),
                switchMap((query : string | null) => {
                    return this.moviesService.fetchMovies(query);
                }),
            ).subscribe({
                next: (movies : MovieListResponse) => {
                    this.setState(LoadingState.Ready, movies, null);
                },
                error: (error : MovieListError) => {
                    this.setState(LoadingState.Error, [], error);
                }
            });

        this.searchControl.reset();
    };

    setState (
        state : LoadingState,
        movies : MovieListResponse,
        error : MovieListError | null
    ) {
        if (this.state !== state) {
            this.state = state;
            this.stateChange.emit({ state, movies, error });
        }
    }
}
