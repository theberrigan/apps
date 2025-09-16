import {Injectable} from '@angular/core';
import {catchError, map, take} from 'rxjs/operators';
import {Observable, throwError} from 'rxjs';
import {HttpService} from './http.service';
import { CONFIG } from '../../../config/app/dev';

export interface CoverageRouteSerialized {
    id : string;                // uuid4
    name : string;
    groupId : string;
    protoPath : null | string;  // google encoded proto polyline-path
    routePath : null | string;  // google encoded calculated polyline-path
    routeColor : string;        // calculated polyline-path color
    routeWeight : number;
    routeOpacity : number;
    gantries : CoverageGantrySerialized[];
}

export interface CoverageSettings {
    routeColor : string;
    routeWeight : number;
    routeOpacity : number;
}

export interface CoverageGroup {
    id : string;    // uuid4
    name : string;
    bounds : null | google.maps.LatLngBoundsLiteral;
    isDeactivated : boolean;
    includeToFocus : boolean;
}

export interface CoverageGantry {
    id : string;    // uuid4
    name : string;
    code : string;  // PGBT-LAKPY
    marker : google.maps.Marker;
    onDragListener : google.maps.MapsEventListener;
}

export interface CoverageGantrySerialized {
    id : string;    // uuid4
    name : string;
    code : string;  // PGBT-LAKPY
    position : google.maps.LatLngLiteral;
}

export interface Coverage {
    groups : CoverageGroup[];
    routes : CoverageRouteSerialized[];
    bounds : null | google.maps.LatLngBoundsLiteral;
    settings : CoverageSettings;
    version : number;
}

export const COVERAGE_CURRENT_VERSION = 3;

@Injectable({
    providedIn: 'root'
})
export class CoverageService {
    loader : Promise<any> = null;

    constructor (
        private http : HttpService
    ) {}

    fetchCoverage () : Observable<null | Coverage> {
        return this.http.get('endpoint://coverage.get').pipe(
            take(1),
            map((response : Coverage) => {
                if (response && !response.version) {
                    response.version = 1;
                }

                response = Object.assign({
                    groups: null,
                    routes: null,
                    bounds: null,
                    settings: null,
                    version: COVERAGE_CURRENT_VERSION
                }, response || {});

                return this.upgradeCoverage(response);
            }),
            catchError(error => {
                console.warn('fetchCoverage error:', error);
                return throwError(error);
            })
        );
    }

    saveCoverage (coverage : Coverage) : Observable<boolean> {
        return this.http.put('endpoint://coverage.set', {
            body: {
                json: JSON.stringify(coverage)
            }
        }).pipe(
            take(1),
            map(response => response.status === 'OK'),
            catchError(error => {
                console.warn('saveCoverage error:', error);
                return throwError(error);
            })
        );
    }

    upgradeCoverage (coverage : Coverage) : Coverage {
        if (!coverage) {
            return null;
        }

        while (coverage.version < COVERAGE_CURRENT_VERSION) {
            switch (coverage.version) {
                case 1:
                    // In v1 there was no field for the code, so it was used as a name.
                    // In v2 there is field for the code, so just copy name to code.
                    coverage.routes?.forEach(route => {
                        route.gantries?.forEach(gantry => {
                            gantry.code = gantry.name;
                        });
                    });
                    break;
                case 2:
                    // Added bounds to each group
                    coverage.groups?.forEach(group => {
                        group.bounds = null;
                    });
            }

            coverage.version += 1;
        }

        return coverage;
    }
}
