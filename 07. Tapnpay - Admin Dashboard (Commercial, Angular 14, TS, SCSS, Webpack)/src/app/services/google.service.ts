import {Injectable} from '@angular/core';
import {catchError, map, take} from 'rxjs/operators';
import {Observable, throwError} from 'rxjs';
import { Loader as GoogleLoader } from '@googlemaps/js-api-loader';
import {HttpService} from './http.service';
import { CONFIG } from '../../../config/app/dev';

@Injectable({
    providedIn: 'root'
})
export class GoogleService {
    loader : Promise<any> = null;

    constructor (
        private http : HttpService
    ) {

    }

    // https://developers.google.com/maps/documentation/javascript/examples/
    // https://developers.google.com/maps/documentation/javascript/reference/
    async loadGoogleMaps () : Promise<boolean> {
        return this.loader || (this.loader = new Promise((resolve) => {
            const loader = new GoogleLoader({
                apiKey: CONFIG.google.apiKey,
                version: 'weekly',
                libraries: [ 'places', 'geometry' ]
            });

            loader.load().then(() => {
                resolve(!!google.maps);
            }).catch((e) => {
                console.warn('Failed to load Google:', e);
                resolve(false);
            });
        }));
    }
}
