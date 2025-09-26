import { LoadingState } from './common';
import { HttpErrorResponse } from '@angular/common/http';


export interface MovieSearchItem {
    id        : number;
    title     : string;
    age       : number | null;
    year      : number | null;
    posterUrl : string;
    genre     : string | null;
    country   : string | null;
}

interface Person {
    id : number;
    name : {
        russian : string | null;
        foreign : string | null;
    };
}

export interface MovieItem {
    id    : number;
    kpId  : number;
    kpUrl : string;
    title : {
        russian : string | null;
        foreign : string | null;
    };
    description : {
        short : string | null;
        full : string | null;
    };
    slogan         : string | null;
    age            : number | null;
    duration       : number | null;
    productionYear : number | null;
    premiereDate   : string | null;
    budget : {
        amount   : number | null;
        currency : string | null;
    };
    boxOffice : {
        amount   : number | null;
        currency : string | null;
    };
    rating: {
        value          : number | null;
        voteCount      : number | null;
        top250Position : number | null;
    };
    posterUrl : string;
    genres : {
        id : number;
        title : string;
    }[];
    countries : {
        id : number;
        title : string;
    }[];
    actors      : Person[];
    voiceActors : Person[];
    directors   : Person[];
    writers     : Person[];
    producers   : Person[];
    composers   : Person[];
    designers   : Person[];
    editors     : Person[];
    awards : {
        id               : number;
        year             : number | null;
        awardTitle       : string | null;
        nominationTitle  : string | null;
        win              : boolean;
    }[];
    platforms : {
        id            : number;
        platformTitle : string;
        watchUrl      : string;
        logoUrl       : string;
    }[];
    releases : {
        id            : number;
        releaserTitle : string;
        type          : string;
        date          : string;
    }[];
    audience : {
        id           : number;
        countryId    : number;
        countryTitle : string;
        count        : number;
    }[];
}

export type MovieListResponse = MovieSearchItem[];

export type MovieListError = HttpErrorResponse;

export interface SearchResultEvent {
    state : LoadingState;
    movies : MovieListResponse;
    error : HttpErrorResponse | null;
}
