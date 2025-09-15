import {Injectable} from '@angular/core';
import {Loader as GoogleLoader} from '@googlemaps/js-api-loader';
import {CONFIG} from '../../../config/app/dev';

@Injectable({
    providedIn: 'root'
})
export class GoogleService {
    loader: Promise<any> = null;

    constructor() {

    }

    // https://developers.google.com/maps/documentation/javascript/examples/
    // https://developers.google.com/maps/documentation/javascript/reference/
    async loadGoogleMaps(): Promise<boolean> {
        if (this.loader) {
            return this.loader;
        }

        this.loader = new Promise<boolean>((resolve) => {
            const googleLoader: GoogleLoader = new GoogleLoader({
                apiKey: CONFIG.google.apiKey,
                version: 'weekly',
                libraries: ['places', 'geometry']
            });

            googleLoader.load().then(() => {
                if (google.maps) {
                    resolve(true);
                } else {
                    console.warn('Google Maps loaded, but "google.maps" is not available.');
                    resolve(false);
                }
            }).catch((error) => {
                console.warn('Failed to load Google Maps:', error);
                resolve(false);
            });
        });

        return this.loader;
    }

}
