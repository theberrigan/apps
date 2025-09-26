import {
    Component,
    input,
    OnInit,
    ViewEncapsulation,
    Renderer2,
    inject,
    OnDestroy,
    output,
    signal, WritableSignal, InputSignal, AnimationCallbackEvent,
} from '@angular/core';
import { MoviesService } from '../../services/movies';
import { LoadingState } from '../../types/common';
import { MovieItem } from '../../types/movies';
import { CurrencyPipe, DatePipe, DecimalPipe, I18nPluralPipe, NgOptimizedImage } from '@angular/common';

@Component({
    selector: 'movie-popup',
    imports: [
        DatePipe,
        CurrencyPipe,
        DecimalPipe,
    ],
    templateUrl: './movie-popup.html',
    styleUrl: './movie-popup.scss',
    encapsulation: ViewEncapsulation.None,
    host: {
        class: 'movie-popup',
        'animate.enter': 'movie-popup_appear',
    }
})
export class MoviePopup implements OnInit, OnDestroy {
    movieId : InputSignal<number> = input<number>(0);

    onClosePopup = output<boolean>();

    protected readonly LoadingState = LoadingState;

    protected renderer = inject(Renderer2);

    protected moviesService = inject(MoviesService);

    protected loadingState = signal(LoadingState.Loading);

    protected movie : WritableSignal<MovieItem | null> = signal(null);

    ngOnInit () {
        // console.log(this.movieId);
        // setTimeout(() => this.onClosePopup.emit(), 3000);
        this.renderer.addClass(document.documentElement, 'movie-popup-no-scroll');
        this.loadMovie();
    }

    ngOnDestroy () {
        this.renderer.removeClass(document.documentElement, 'movie-popup-no-scroll');
    }

    protected loadMovie () {
        this.moviesService.fetchMovie(this.movieId()).subscribe({
            next: (movie : MovieItem) => {
                this.movie.set(movie);
                this.loadingState.set(LoadingState.Ready);
            },
            error: () => {
                this.movie.set(null);
                this.loadingState.set(LoadingState.Error);
                this.onClosePopup.emit(true);
            }
        });
    }
}
