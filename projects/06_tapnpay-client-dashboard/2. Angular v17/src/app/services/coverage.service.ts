import {Injectable} from '@angular/core';
import {catchError, map, take} from 'rxjs/operators';
import {Observable, of, throwError} from 'rxjs';
import {HttpService} from './http.service';
import {GoogleService} from './google.service';
import {AccountTollAuthority} from './user.service';


export interface Coverage {
    groups: CoverageGroup[];
    routes: CoverageRouteSerialized[];
    bounds: null | google.maps.LatLngBoundsLiteral;
    settings: CoverageSettings;
    version: number;
}

export interface CoverageRouteSerialized {
    id: string;                // uuid4
    name: string;
    groupId: string;
    protoPath: null | string;  // google encoded proto polyline-path
    routePath: null | string;  // google encoded calculated polyline-path
    routeColor: string;        // calculated polyline-path color
    routeWeight: number;
    routeOpacity: number;
    gantries: CoverageGantrySerialized[];
}

export interface CoverageRoute {
    id: string;
    name: string;
    groupId: string;
    routePolyline: google.maps.Polyline;
    routeColor: string;
    routeWeight: number;
    routeOpacity: number;
    gantries: CoverageGantry[];
    isExpanded: boolean;
}

export interface CoverageSettings {
    routeColor: string;
    routeWeight: number;
    routeOpacity: number;
}

export interface CoverageGroup {
    id: string;    // uuid4
    name: string;
    bounds: null | google.maps.LatLngBoundsLiteral;
    isDeactivated: boolean;
    includeToFocus: boolean;
}

export interface CoverageGantry {
    id: string;
    name: string;
    code: string;
    marker: google.maps.Marker;
}

export interface CoverageGantrySerialized {
    id: string;
    name: string;
    code: string;
    position: google.maps.LatLngLiteral;
}

export interface CoverageLocationRoute {
    id: string;
    routePath: google.maps.LatLng[];
    routeColor: string;
    routeWeight: number;
    routeOpacity: number;
}

export interface CoverageLocationGantry {
    id: string;
    name: string;
    code: string;
    fullName: string;
    position: google.maps.LatLngLiteral;
}

export interface CoverageLocation {
    route: CoverageLocationRoute;
    gantry: CoverageLocationGantry;
}

export interface CoverageLocationMap {
    [key: string]: CoverageLocation;
}

export const COVERAGE_CURRENT_VERSION = 3;

type CacheKey = string;


@Injectable({
    providedIn: 'root'
})
export class CoverageService {
    loader: Promise<any> = null;

    coverage: Coverage;
    coverageLocationCache: Map<CacheKey, Promise<null | CoverageLocation[]>> = new Map();

    constructor(
        private http: HttpService,
        private googleService: GoogleService,
    ) {
    }

    getMapCoverageFullData(): Observable<null | Coverage> {
        if (this.coverage) {
            return of(this.coverage);
        }

        this.coverage = null;

        return this.http.get('endpoint://coverage.get').pipe(
            take(1),
            map((coverage: Coverage) => {
                if (coverage && !coverage.version) {
                    coverage.version = 1;
                }

                this.coverage = Object.assign({
                    groups: [],
                    routes: [],
                    bounds: null,
                    settings: null,
                    version: COVERAGE_CURRENT_VERSION
                }, coverage || {});

                /*this.coverage = Object.assign({
                    groups: [],
                    routes: [],
                    bounds: null,
                    settings: null,
                    version: COVERAGE_CURRENT_VERSION
                }, {});*/

                return this.coverage;
            }),
            catchError(error => {
                console.warn('fetchCoverage error:', error);
                return throwError(error);
            })
        );
    }

    async coverageToLocations(coverage: null | Coverage, tollAuthority: AccountTollAuthority, isFilterRoutesByTa: boolean = true): Promise<null | CoverageLocation[]> {

        const cacheKey: CacheKey = `${tollAuthority}-${isFilterRoutesByTa}`;

        if (this.coverageLocationCache.has(cacheKey)) {
            return this.coverageLocationCache.get(cacheKey)!;
        }

        const resultPromise = (async () => {
            if (!coverage) {
                return null;
            }

            await this.googleService.loadGoogleMaps();

            const locations: CoverageLocation[] = [];

            const userTACoverageGroup: CoverageGroup = this.findCoverageGroupByName(coverage.groups, tollAuthority);

            if (!userTACoverageGroup || userTACoverageGroup.isDeactivated) {
                return null;
            }

            coverage.routes.forEach((routeSerialized: CoverageRouteSerialized) => {
                const isNotRoutePath = !!routeSerialized.routePath;
                const isRouteNotFromUserTACoverageGroup = routeSerialized.groupId !== userTACoverageGroup.id;

                if (isFilterRoutesByTa && (isNotRoutePath || isRouteNotFromUserTACoverageGroup)) {
                    return;
                }

                if (this.isAllPropertiesNotNullOrUndefined(routeSerialized)) {
                    const route: CoverageLocationRoute = {
                        id: routeSerialized.id,
                        routePath: google.maps.geometry.encoding.decodePath(routeSerialized.routePath),
                        routeColor: routeSerialized.routeColor,
                        routeWeight: routeSerialized.routeWeight,
                        routeOpacity: routeSerialized.routeOpacity
                    };

                    for (const gantry of routeSerialized.gantries) {
                        const {id, name, code, position} = gantry;
                        const fullName = name && code && name !== code ? `${name} (${code})` : name ?? code ?? '';

                        locations.push({
                            route,
                            gantry: {id, name, fullName, code, position},
                        });
                    }
                }
            });

            return locations;
        })();

        this.coverageLocationCache.set(cacheKey, resultPromise);

        return resultPromise;
    }

    private findCoverageGroupByName(coverageGroups: CoverageGroup[], taName: string): CoverageGroup {
        if (!coverageGroups || !taName) {
            return null;
        }
        return coverageGroups.find(group => group?.name?.toUpperCase() === taName.toUpperCase());
    }

    private isAllPropertiesNotNullOrUndefined(obj: Record<string, any>): boolean {
        return Object.values(obj).every(value => value != null);
    }


    async deserializeCoverage(coverage: null | Coverage): Promise<null | {
        listOfAllTollAuthoritiesRoads: CoverageRoute[];
        bounds: google.maps.LatLngBoundsLiteral;
    }> {
        if (!coverage) {
            return null;
        }

        await this.googleService.loadGoogleMaps();

        const inactiveGroupIds: string[] = coverage.groups.reduce((acc: string[], group: CoverageGroup) => {
            if (group.isDeactivated) {
                acc.push(group.id);
            }

            return acc;
        }, []);

        const routes: CoverageRoute[] = coverage.routes.map((route) => {
            const {id, name, groupId, routePath, routeColor, routeWeight, routeOpacity, gantries} = route;

            if (!routePath || !gantries || (groupId && inactiveGroupIds.includes(groupId))) {
                return;
            }

            const routePolyline = new google.maps.Polyline({
                path: google.maps.geometry.encoding.decodePath(routePath),
                editable: false,
                strokeColor: routeColor,
                strokeOpacity: routeOpacity,
                strokeWeight: routeWeight,
            });

            const deserializedGantries: CoverageGantry[] = gantries.map(({id, name, code, position}) => {
                let fullName: string = '';

                if (name && code && name !== code) {
                    fullName = `${name} (${code})`;
                } else if (name) {
                    fullName = name;
                } else if (code) {
                    fullName = code;
                }

                return {
                    id,
                    name,
                    code,
                    marker: new google.maps.Marker({
                        position,
                        title: fullName,
                        draggable: false,
                        clickable: false,
                        optimized: true,
                        cursor: 'default'
                    })
                };
            });

            return {
                id,
                name,
                groupId,
                routePolyline,
                routeColor,
                routeWeight,
                routeOpacity,
                gantries: deserializedGantries,
                isExpanded: false
            };
        });

        return {listOfAllTollAuthoritiesRoads: routes, bounds: coverage.bounds};
    }
}
