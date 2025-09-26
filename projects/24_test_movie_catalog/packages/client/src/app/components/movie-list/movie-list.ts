import { Component, signal, ViewEncapsulation, WritableSignal } from '@angular/core';
import { MovieListSearch } from '../movie-list-search/movie-list-search';
import { LoadingState } from '../../types/common';
import { SearchResultEvent } from '../../types/movies';
import { MoviePopup } from '../movie-popup/movie-popup';
import { NgOptimizedImage } from '@angular/common';

@Component({
    selector: 'movie-list',
    imports: [
        MovieListSearch,
        MoviePopup,
    ],
    templateUrl: './movie-list.html',
    styleUrl: './movie-list.scss',
    encapsulation: ViewEncapsulation.None,
    host: {
        class: 'movie-list'
    }
})
export class MovieList {
    protected readonly LoadingState = LoadingState;

    protected readonly skeletonItems = Array(20).fill(0).map((_, i) => i);

    protected activeMovieId : number | null = null;

    protected state : WritableSignal<SearchResultEvent> = signal({
        state: LoadingState.Loading,
        movies: [],
        error: null
    });

    onStateChange (state : SearchResultEvent) {
        this.state.set(state);
    }

    handleMovieCardClick (movieId : number) {
        this.activeMovieId = movieId;
    }

    handleClosePopup (hasError : boolean) {
        this.activeMovieId = null;

        if (hasError) {
            this.state.set({
                state: LoadingState.Error,
                movies: [],
                error: null
            });
        }
    }
}
