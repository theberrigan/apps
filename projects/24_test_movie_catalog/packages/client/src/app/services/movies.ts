import { inject, Injectable } from '@angular/core';
import { HttpClient, HttpParams } from '@angular/common/http';
import { Observable, retry, take, timeout } from 'rxjs';
import { MovieItem, MovieListResponse } from '../types/movies';

const API_ORIGIN : string = (() => {
    const url = new URL(window.location.origin);

    url.port = '40451';

    return url.toString();
})();

@Injectable({
    providedIn: 'root'
})
export class MoviesService {
    protected http = inject(HttpClient);

    fetchMovies (query : string | null) : Observable<MovieListResponse> {
        query = (query ?? '').trim();

        const params = new HttpParams({
            fromObject: { query }
        });

        return this.http.get<MovieListResponse>(`${ API_ORIGIN }api/movies/search`, { params }).pipe(
            timeout(5000),
            retry(2),
            take(1)
        );
    }

    fetchMovie (movieId : number) : Observable<MovieItem> {
        return this.http.get<MovieItem>(`${ API_ORIGIN }api/movie/${ movieId }`).pipe(
            timeout(5000),
            retry(2),
            take(1)
        );
    }
}
