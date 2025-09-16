import {
    AfterViewInit,
    ChangeDetectionStrategy,
    Component,
    ElementRef,
    HostListener,
    OnDestroy,
    OnInit,
    Renderer2,
    ViewChild,
    ViewEncapsulation
} from '@angular/core';
import {fromEvent, Subject, Subscription} from 'rxjs';
import {TitleService} from '../../../../services/title.service';
import {ToastService} from '../../../../services/toast.service';
import {GoogleService} from '../../../../services/google.service';
import {
    Coverage, COVERAGE_CURRENT_VERSION,
    CoverageGantry,
    CoverageGantrySerialized,
    CoverageGroup,
    CoverageRouteSerialized,
    CoverageService,
    CoverageSettings
} from '../../../../services/coverage.service';
import {defer, getMin, isFinite, truncateFraction, uuid4} from '../../../../lib/utils';
import {animate, style, transition, trigger} from '@angular/animations';
import {cloneDeep} from 'lodash-es';
import {debounceTime, distinctUntilChanged, map} from 'rxjs/operators';
import {DomService} from '../../../../services/dom.service';
import SymbolPath = google.maps.SymbolPath;

type State = 'loading' | 'ready' | 'error' | 'future-version';

type Tab = 'routes' | 'groups';

interface CoverageRouteOptions {
    serializedRoute? : CoverageRouteSerialized;
    startPoint? : google.maps.LatLng;
    map? : google.maps.Map;
    directionsService : google.maps.DirectionsService;
    visibility : RouteVisibility;
    settings : CoverageSettings;
}

enum RouteVisibility {
    Active = 1,
    Inactive = 2,
    Hidden = 3,
    Preview = 4,
}

interface RouteColor {
    code : string;
    isDefault : boolean;
}

const ROUTE_COLORS : RouteColor[] = [
    {
        code: '#fb9902',
        isDefault: false
    },
    {
        code: '#fd5308',
        isDefault: false
    },
    {
        code: '#fe2712',
        isDefault: false
    },
    {
        code: '#a7194b',
        isDefault: false
    },
    {
        code: '#8601af',
        isDefault: false
    },
    {
        code: '#3d01a4',
        isDefault: false
    },
    {
        code: '#0247fe',
        isDefault: false
    },
    {
        code: '#4875e7',
        isDefault: true
    },
    {
        code: '#66b032',
        isDefault: false
    }
];

const ROUTE_COLOR = ROUTE_COLORS.find(color => color.isDefault);

const ROUTE_WEIGHT = {
    min: 1,
    max: 10,
    steps: 10,
    defaultValue: 5,
};

const ROUTE_OPACITY = {
    min: 0.2,
    max: 1.0,
    defaultValue: 0.8,
};

const SETTINGS_DEFAULT : CoverageSettings = {
    routeColor: ROUTE_COLOR.code,
    routeWeight: ROUTE_WEIGHT.defaultValue,
    routeOpacity: ROUTE_OPACITY.defaultValue,
};

const UI_MARGIN = 20;
const UI_WIDTH = 390;
const SEARCH_WIDTH = 640;
const SEARCH_HEIGHT = 48;
const MAP_BASE_PADDING = 50;
const BODY_LOCK_CLASS = 'coverage-lock';

/*
TODO:
- Pan to added Marker
- Add markers to bounding box
- Disable everything when edit marker mode is active
- Save to server!
-
 */
// ('name -11.87, 65.321'.matchAll(/-?\d+(?:\.(?:\d+|\d*e-?\d+))?/ig))
class CoverageRoute {
    id : string;

    name : string;

    groupId : string;

    gantries : CoverageGantry[] = [];

    private protoPolyline : null | google.maps.Polyline;

    private routePolyline : null | google.maps.Polyline;

    private routeTimeout : any;

    private map : google.maps.Map = null;

    private directionsService : google.maps.DirectionsService;

    private onRouteClickSubject = new Subject<CoverageRoute>();

    private onColorChangeSubject = new Subject<string>();

    private onWeightChangeSubject = new Subject<number>();

    private onOpacityChangeSubject = new Subject<number>();

    private visibility : RouteVisibility = RouteVisibility.Inactive;

    private _routeColor : string = '#4875e7';

    set routeColor (color : string) {
        this._routeColor = color;
        this.routePolyline?.set('strokeColor', color);
    }

    get routeColor () : string {
        // Don't get value from polyline, get it from this object instead
        return this._routeColor;
    }

    private _routeOpacity : number = 1.0;

    set routeOpacity (opacity : number) {
        this._routeOpacity = opacity;
        this.routePolyline?.set('strokeOpacity', opacity);
    }

    get routeOpacity () : number {
        // Don't get value from polyline, get it from this object instead
        return this._routeOpacity;
    }

    private _routeWeight : number = 5;

    set routeWeight (weight : number) {
        this._routeWeight = weight;
        this.routePolyline?.set('strokeWeight', weight);
    }

    get routeWeight () : number {
        // Don't get value from polyline, get it from this object instead
        return this._routeWeight;
    }

    activeGantry : CoverageGantry = null;

    activeGantryPosition : string = '';

    constructor (options : CoverageRouteOptions) {
        console.log(google.maps.geometry.encoding.encodePath((new google.maps.Polyline()).getPath()).length);
        const { serializedRoute, startPoint, map, directionsService, visibility, settings } = options;

        this.map = map || null;
        this.directionsService = directionsService;

        if (serializedRoute) {
            const { id, name, groupId, protoPath, routePath, routeColor, routeWeight, routeOpacity, gantries } = serializedRoute;

            this.id = id;
            this.name = name;
            this.groupId = groupId;
            this.protoPolyline = this.createProtoPolyline(this.decodePath(protoPath || ''));
            this.routePolyline = this.createRoutePolyline(this.decodePath(routePath || ''));
            this.routeColor = routeColor ? routeColor.toLowerCase() : settings.routeColor;
            this.routeWeight = routeWeight || settings.routeWeight;
            this.routeOpacity = routeOpacity || settings.routeOpacity;
            this.routeTimeout = null;
            this.gantries = [];

            (gantries || []).forEach(serializedGantry => {
                const gantry = this.deserializeGantry(serializedGantry);
                this.setGentryStyle(gantry, false);
                this.pushGantry(gantry);
            });
        } else {
            this.id = uuid4();
            this.name = '';
            this.groupId = null;
            this.protoPolyline = this.createProtoPolyline(startPoint ? [ startPoint ] : []);
            this.routePolyline = null;
            this.routeColor = settings.routeColor;
            this.routeWeight = settings.routeWeight;
            this.routeOpacity = settings.routeOpacity;
            this.routeTimeout = null;
            this.gantries = [];
        }

        this.setupListeners();
        this.setVisibility(visibility || RouteVisibility.Hidden);
    }

    serialize () : CoverageRouteSerialized {
        return {
            id: this.id,
            name: this.getName(),
            groupId: this.groupId,
            protoPath: this.polylineToPath(this.protoPolyline),
            routePath: this.polylineToPath(this.routePolyline),
            routeColor: this.routeColor,
            routeWeight: this.routeWeight,
            routeOpacity: this.routeOpacity,
            gantries: this.gantries.map(gantry => this.serializeGantry(gantry)),
        };
    }

    serializeGantry (gantry : CoverageGantry) : CoverageGantrySerialized {
        return {
            id: gantry.id,
            name: this.getGantryName(gantry),
            code: this.getGantryCode(gantry),
            position: <google.maps.LatLngLiteral>this.getGantryPosition(gantry),
        };
    }

    deserializeGantry (serializedGantry : CoverageGantrySerialized) : CoverageGantry {
        const { id, name, code, position } = serializedGantry;

        return {
            id,
            name,
            code,
            marker: new google.maps.Marker({
                position,
                title: name,
                map: this.map,
                draggable: false,
                clickable: false
            }),
            onDragListener: null,
        };
    }

    getGantryName (gantry : CoverageGantry) : string {
        return (gantry.name || '').trim();
    }

    getGantryCode (gantry : CoverageGantry) : string {
        return (gantry.code || '').trim();
    }

    getGantryPosition (gantry : CoverageGantry, asString : boolean = false) : null | string | google.maps.LatLngLiteral {
        const position : google.maps.LatLngLiteral = gantry?.marker?.getPosition()?.toJSON() || null;

        if (asString) {
            return position ? this.positionToString(position) : '';
        }

        return position;
    }

    pushPoint (point : google.maps.LatLng) {
        this.protoPolyline?.getPath()?.push(point);
    }

    listenOnRouteClick (fn : (route : CoverageRoute) => void) {
        this.onRouteClickSubject.asObservable().subscribe(fn);
    }

    listenOnColorChange (fn : (routeColor : string) => void) {
        this.onColorChangeSubject.asObservable().subscribe(fn);
    }

    listenOnWeightChange (fn : (routeWeight : number) => void) {
        this.onWeightChangeSubject.asObservable().subscribe(fn);
    }

    listenOnOpacityChange (fn : (routeOpacity : number) => void) {
        this.onOpacityChangeSubject.asObservable().subscribe(fn);
    }

    onColorClick (color : RouteColor) {
        this.routeColor = color.code;
        this.onColorChangeSubject.next(this.routeColor);
    }

    onWeightChange () {
        this.onWeightChangeSubject.next(this.routeWeight);
    }

    onOpacityChange () {
        this.onOpacityChangeSubject.next(this.routeOpacity);
    }

    detach () {
        // TODO: unsub all
        clearTimeout(this.routeTimeout);
        this.onRouteClickSubject.unsubscribe();
        this.onColorChangeSubject.unsubscribe();
        this.onWeightChangeSubject.unsubscribe();
        this.onOpacityChangeSubject.unsubscribe();
        this.protoPolyline?.setMap(null);
        this.routePolyline?.setMap(null);
        this.gantries.forEach(gantry => gantry.marker?.setMap(null));
    }

    setVisibility (visibility : RouteVisibility) {
        this.visibility = visibility;
        this.updateState();
    }

    hasRoutePath () : boolean {
        return this.getRoutePath().length > 1;
    }

    getName () : string {
        return (this.name || '').trim();
    }

    getRoutePath () : google.maps.LatLng[] {
        return this.routePolyline?.getPath()?.getArray() || [];
    }

    getBounds () : null | google.maps.LatLngBounds {
        const path = this.getRoutePath();

        if (!path.length) {
            return null;
        }

        const bounds = new google.maps.LatLngBounds();

        path.forEach(point => bounds.extend(point));

        return bounds;
    }

    private updateState () {
        const hasActiveGantry = !!this.activeGantry;

        switch (this.visibility) {
            case RouteVisibility.Active:
                this.protoPolyline?.setVisible(!hasActiveGantry);

                if (this.routePolyline) {
                    this.routePolyline.set('strokeColor', this.routeColor);
                    this.routePolyline.set('strokeOpacity', this.routeOpacity);
                    this.routePolyline.setVisible(true);
                }

                this.gantries.forEach(gantry => gantry.marker?.setVisible(true));

                break;
            case RouteVisibility.Inactive:
                this.protoPolyline?.setVisible(false);

                if (this.routePolyline) {
                    this.routePolyline.set('strokeColor', '#000');
                    this.routePolyline.set('strokeOpacity', 0.35);
                    this.routePolyline.setVisible(true);
                }

                this.gantries.forEach(gantry => gantry.marker?.setVisible(false));

                break;
            case RouteVisibility.Hidden:
                this.protoPolyline?.setVisible(false);
                this.routePolyline?.setVisible(false);
                this.gantries.forEach(gantry => gantry.marker?.setVisible(false));

                break;
            case RouteVisibility.Preview:
                this.protoPolyline?.setVisible(false);

                if (this.routePolyline) {
                    this.routePolyline.set('strokeColor', this.routeColor);
                    this.routePolyline.set('strokeOpacity', this.routeOpacity);
                    this.routePolyline.setVisible(true);
                }

                this.gantries.forEach(gantry => gantry.marker?.setVisible(false));

                break;
        }
    }

    private getProtoPath () : google.maps.LatLng[] {
        return this.protoPolyline?.getPath()?.getArray() || [];
    }

    private async calcRoute (path : google.maps.LatLng[]) : Promise<null | google.maps.DirectionsResult> {
        if (path.length < 2) {
            return Promise.resolve(null);
        }

        return this.directionsService.route({
            origin: path[0],
            destination: path[path.length - 1],
            waypoints: path.slice(1, -1).map(point => ({
                location: point,
                stopover: false
            })),
            optimizeWaypoints: false,
            travelMode: google.maps.TravelMode.DRIVING,
            provideRouteAlternatives: false,
        }).then(result => {
            return result;
        }).catch(e => {
            console.warn(e.name, e.message);
            return null;
        });
    }

    private removeRoutePolyline () {
        this.routePolyline?.setMap(null);
        this.routePolyline = null;
    }

    // Search || Name Input | Swap Waypoints | Thickness | Color | Opacity | Ok
    private onUpdateRoute () {
        clearTimeout(this.routeTimeout);

        const protoPath = this.getProtoPath();

        if (protoPath.length <= 1) {
            this.removeRoutePolyline();
        } else {
            this.routeTimeout = setTimeout(async () => {
                const responseRoutes : google.maps.DirectionsRoute[] = [
                    await this.calcRoute(protoPath),
                    await this.calcRoute([ ...protoPath ].reverse())
                ].reduce((acc, response) => {
                    if (response?.routes?.length) {
                        acc.push(response.routes[0]);
                    }

                    return acc;
                }, []);

                this.removeRoutePolyline();

                if (responseRoutes.length) {
                    const shortestRoute = getMin(responseRoutes, route => {
                        return route.legs.reduce((sum, leg) => (sum + leg.distance.value), 0);
                    });

                    if (shortestRoute?.overview_polyline) {
                        const path = google.maps.geometry.encoding.decodePath(shortestRoute.overview_polyline);
                        this.routePolyline = this.createRoutePolyline(path);
                    }
                }
            }, 250);
        }
    }

    private setupListeners () {
        const protoPath = this.protoPolyline.getPath();

        google.maps.event.addListener(this.protoPolyline, 'rightclick', (e : google.maps.PolyMouseEvent) => {
            if (e.vertex !== undefined) {
                protoPath.removeAt(e.vertex);
            }
        });

        google.maps.event.addListener(protoPath, 'insert_at', () => this.onUpdateRoute());
        google.maps.event.addListener(protoPath, 'remove_at', () => this.onUpdateRoute());
        google.maps.event.addListener(protoPath, 'set_at', () => this.onUpdateRoute());
    }

    private decodePath (path : string) : google.maps.LatLng[] {
        return path && google.maps.geometry.encoding.decodePath(path) || [];
    }

    private createProtoPolyline (polylinePath : google.maps.LatLng[]) : google.maps.Polyline {
        return new google.maps.Polyline({
            map: this.map,
            path: polylinePath,
            editable: true,
            draggable: false,
            strokeColor: '#FF0000',
            strokeOpacity: 1.0,
            strokeWeight: 1,
        });
    }

    private createRoutePolyline (polylinePath : google.maps.LatLng[]) : google.maps.Polyline {
        const polyline = new google.maps.Polyline({
            map: this.map,
            path: polylinePath,
            editable: false,
            strokeColor: this.routeColor,
            strokeOpacity: this.routeOpacity,
            strokeWeight: this.routeWeight,
        });

        google.maps.event.addListener(polyline, 'click', () => {
            this.onRouteClickSubject.next(this);
        });

        return polyline;
    }

    private polylineToPath (polyline : google.maps.Polyline) : null | string {
        return polyline && google.maps.geometry.encoding.encodePath(polyline.getPath()) || null;
    }

    checkActiveGantry (gantry : CoverageGantry) : boolean {
        if (!gantry) {
            return false;
        }

        return this.activeGantry?.id === gantry.id;
    }

    hasGantries () : boolean {
        return this.gantries?.length > 0 || false;
    }

    onSwitchGantry (gantry : CoverageGantry) {
        this.setActiveGantry(this.checkActiveGantry(gantry) ? null : gantry);
    }

    setActiveGantry (gantry : null | CoverageGantry) {
        if (this.activeGantry) {
            this.setGentryStyle(this.activeGantry, false);
            this.activeGantry.onDragListener?.remove();
            this.activeGantry.onDragListener = null;
        }

        this.activeGantry = gantry;

        if (this.activeGantry) {
            this.setGentryStyle(this.activeGantry, true);

            const { marker } = this.activeGantry;

            this.activeGantry.onDragListener = google.maps.event.addListener(marker, 'dragend', () => {
                this.activeGantryPosition = <string>this.getGantryPosition(this.activeGantry, true);
            });

            this.activeGantryPosition = <string>this.getGantryPosition(this.activeGantry, true);
        }

        this.updateState();
    }

    onRemoveGantry (gantry : CoverageGantry) {
        if (!gantry) {
            return;
        }

        if (this.activeGantry && gantry.id === this.activeGantry.id) {
            this.resetGantryEditor();
        }

        gantry.marker?.setMap(null);

        this.gantries = this.gantries.filter(item => item.id !== gantry.id);
    }

    onAddGantry (position : google.maps.LatLngLiteral = null) {
        const name = '';

        const gantry : CoverageGantry = {
            id: uuid4(),
            name,
            code: '',
            marker: new google.maps.Marker({
                position,
                title: name,
                map: this.map,
                draggable: false,
                clickable: false,
            }),
            onDragListener: null,
        };

        // this.setGentryStyle(gantry, false);
        this.pushGantry(gantry);
        this.setActiveGantry(gantry);
    }

    onGantryNameChange () {
        const name = this.getGantryName(this.activeGantry);
        this.activeGantry.marker?.setTitle(name);
    }

    onGantryPositionChange () {
        const position = this.positionFromString(this.activeGantryPosition);
        this.activeGantry?.marker.setPosition(position);
    }

    setActiveGantryPosition (position : google.maps.LatLng) {
        if (this.activeGantry) {
            this.activeGantry.marker?.setPosition(position);
            this.activeGantryPosition = this.positionToString(position?.toJSON());
        }
    }

    setGentryStyle (gantry : CoverageGantry, isActive : boolean) {
        if (!gantry || !gantry.marker) {
            return;
        }

        const { marker } = gantry;

        if (isActive) {
            marker.setIcon(null);
            marker.setDraggable(true);
        } else {
            marker.setIcon({
                path: google.maps.SymbolPath.CIRCLE,
                fillColor: '#e83f3a',
                fillOpacity: 1,
                strokeWeight: 1,
                strokeColor: '#fff',
                scale: 4
            });
            marker.setDraggable(false);
        }
    }

    pushGantry (gantry : CoverageGantry) {
        if (!gantry) {
            return;
        }

        this.gantries = [ ...this.gantries, gantry ];
    }

    resetGantryEditor () {
        this.setActiveGantry(null);
        this.activeGantryPosition = '';
    }

    onDeactivate () {
        this.resetGantryEditor();
    }

    hasActiveGantry () : boolean {
        return !!this.activeGantry;
    }

    positionToString (position : google.maps.LatLngLiteral | number[]) : null | string {
        if (position) {
            if (Array.isArray(position) && position.length === 2 && position.every(n => isFinite(n))) {
                return position.map(n => truncateFraction(n, 7)).join(', ');
            } else if (('lat' in position) && ('lng' in position)) {
                return `${ truncateFraction(position.lat, 7) }, ${ truncateFraction(position.lng, 7) }`;
            }
        }

        return null;
    }

    positionFromString (position : string) : null | google.maps.LatLngLiteral {
        position = (position || '').trim();

        if (position) {
            const nums : number[] = position.split(/[\s,;]+/).map(val => parseFloat(val.trim()));

            if (nums.length === 2 && nums.every(n => isFinite(n))) {
                return {
                    lat: truncateFraction(nums[0], 7),
                    lng: truncateFraction(nums[1], 7)
                };
            }
        }

        return null;
    }
}

@Component({
    selector: 'coverage',
    templateUrl: './coverage.component.html',
    styleUrls: [ './coverage.component.scss' ],
    changeDetection: ChangeDetectionStrategy.Default,
    encapsulation: ViewEncapsulation.None,
    host: {
        'class': 'coverage'
    },
    animations: [
        trigger('expand', [
            transition(':enter', [
                style({ height: '0px' }),
                animate('0.15s cubic-bezier(0.5, 1, 0.89, 1)', style({ height: '*' }))
            ]),
            transition(':leave', [
                style({ height: '*' }),
                animate('0.15s cubic-bezier(0.5, 1, 0.89, 1)', style({ height: '0px' }))
            ])
        ]),
    ],
})
export class CoverageComponent implements OnInit, OnDestroy, AfterViewInit {
    subs : Subscription[] = [];

    @ViewChild('mapEl')
    mapEl : ElementRef;

    @ViewChild('scrollEl')
    scrollEl : ElementRef;

    state : State = 'loading';

    map : google.maps.Map = null;

    _routes : CoverageRoute[] = [];

    set routes (routes : CoverageRoute[]) {
        this._routes = routes || [];
    }

    get routes () : CoverageRoute[] {
        return this._routes || (this._routes = []);
    }

    groups : CoverageGroup[] = [];

    activeRoute : CoverageRoute = null;

    directionsService : google.maps.DirectionsService = null;

    placesService : google.maps.places.PlacesService = null;

    isPreviewActive : boolean = false;

    isHelpVisible : boolean = false;

    isSaving : boolean = false;

    settings : CoverageSettings = null;

    activeTab : Tab = 'routes';

    readonly strokeWeightOptions = ROUTE_WEIGHT;

    readonly strokeOpacityOptions = ROUTE_OPACITY;

    readonly routeColorOptions = ROUTE_COLORS;

    readonly uiMargin = UI_MARGIN;

    readonly uiWidth = UI_WIDTH;

    readonly searchWidth = SEARCH_WIDTH;

    readonly searchHeight = SEARCH_HEIGHT;

    readonly searchLeft = `calc(50% - ${ (SEARCH_WIDTH + UI_WIDTH + UI_MARGIN) / 2 }px)`;

    activeGroupId : null | string = null;

    appVersion : number = null;

    dataVersion : number = null;

    constructor (
        public renderer : Renderer2,
        public titleService : TitleService,
        public domService : DomService,
        public toastService : ToastService,
        public googleService : GoogleService,
        public coverageService : CoverageService,
    ) {
        this.titleService.setTitle('coverage.page_title');
        this.state = 'loading';
    }

    ngOnInit () {

    }

    ngOnDestroy () {
        this.subs.forEach(sub => sub.unsubscribe());
    }

    async ngAfterViewInit () {
        const [ coverage, isMapLoaded ] : [ Coverage, boolean ] = await Promise.all([
            this.coverageService.fetchCoverage().toPromise(),
            this.initMap()
        ]).catch(() => [ null, false ]);

        console.warn(coverage);

        /*
        const nttaGroup = coverage.groups.find(group => group.name === 'NTTA');
        const sunpassGroup = coverage.groups.find(group => group.name === 'Sunpass');
        const trashGroups = coverage.groups.reduce((acc, group) => {
            if ([ 'TEXPress', 'TXDOT TEXPress' ].includes(group.name)) {
                acc[group.id] = group;
            }

            return acc;
        }, {});
        coverage.groups = coverage.groups.filter(group => !(group.id in trashGroups));
        coverage.routes.forEach((route) => {
            if (route.groupId === nttaGroup.id || (route.groupId in trashGroups)) {
                route.groupId = nttaGroup.id;
                route.routeColor = '#3d01a4';
            } else if (route.groupId === sunpassGroup.id) {
                route.routeColor = '#fe2712';
            }
        });
         */

        if (!coverage || !isMapLoaded) {
            this.state = 'error';
            return;
        }

        if (coverage.version > COVERAGE_CURRENT_VERSION) {
            this.appVersion = COVERAGE_CURRENT_VERSION
            this.dataVersion = coverage.version;
            this.state = 'future-version';
            return;
        }

        this.settings = Object.assign({}, SETTINGS_DEFAULT, coverage.settings || {});
        this.groups = coverage.groups || [];

        (coverage.routes || []).forEach(serializedRoute => {
            const route = new CoverageRoute({
                serializedRoute,
                map: this.map,
                directionsService: this.directionsService,
                visibility: RouteVisibility.Hidden,
                settings: cloneDeep(this.settings)
            });

            this.pushRoute(route);
        });

        this.preview();
        defer(() => this.initSearch());

        this.state = 'ready';
    }

    async initMap () : Promise<boolean> {
        const isGoogleMapsLoaded = await this.googleService.loadGoogleMaps();

        if (!isGoogleMapsLoaded) {
            console.warn('Failed to load Google Maps API');
            return false;
        }

        if (!this.mapEl.nativeElement) {
            console.warn('Map root element not found');
            return false;
        }

        // https://developers.google.com/maps/documentation/javascript/reference/map#Map
        this.map = new google.maps.Map(<HTMLElement>this.mapEl.nativeElement, {
            center: {
                lat: 32.75,
                lng: -96.7
            },
            zoom: 10,
            disableDefaultUI: true,
            draggableCursor: 'default',
            disableDoubleClickZoom: true,
            clickableIcons: false,
            mapTypeId: google.maps.MapTypeId.ROADMAP,
            styles: [
                {
                    featureType: 'poi',
                    elementType: 'all',
                    stylers: [
                        {
                            visibility: 'off'
                        }
                    ]
                }
            ]
        });



        google.maps.event.addListener(this.map, 'click', e => this.onMapClick(e));

        this.directionsService = new google.maps.DirectionsService();
        this.placesService = new google.maps.places.PlacesService(this.map);

        return true;
    }

    hasRoutes () : boolean {
        return this.routes.length > 0;
    }

    hasGroups () : boolean {
        return (this.groups || []).length > 0;
    }

    checkActiveRoute (route : CoverageRoute) : boolean {
        return !!(this.activeRoute && this.activeRoute.id === route.id);
    }

    onSwitchRoute (route : CoverageRoute) {
        this.setActiveRoute(this.checkActiveRoute(route) ? null : route, true);
    }

    onMapClick (e : google.maps.MapMouseEvent) {
        const position = e.latLng;

        if (this.activeRoute?.hasActiveGantry()) {
            this.activeRoute.setActiveGantryPosition(position);
        } else {
            const startNewRoute = (<MouseEvent>e.domEvent).ctrlKey;

            if (!startNewRoute && this.activeRoute) {
                this.activeRoute.pushPoint(position);
            } else {
                const route = new CoverageRoute({
                    startPoint: position,
                    map: this.map,
                    directionsService: this.directionsService,
                    visibility: RouteVisibility.Hidden,
                    settings: cloneDeep(this.settings),
                });

                this.pushRoute(route);
                this.setActiveRoute(route);
            }
        }
    }

    pushRoute (route : CoverageRoute) {
        if (!route) {
            return;
        }

        this.routes = [ ...this.routes, route ];

        route.listenOnRouteClick((route) => {
            this.setActiveRoute(route, true);
            this.scrollToRoute(route);
        });

        route.listenOnColorChange((routeColor : string) => {
            this.settings.routeColor = routeColor;
        });

        route.listenOnWeightChange((routeWeight : number) => {
            this.settings.routeWeight = routeWeight;
        });

        route.listenOnOpacityChange((routeOpacity : number) => {
            this.settings.routeOpacity = routeOpacity;
        });
    }

    preview () {
        const activeRoutes = this.filterRoutes(this.routes, {
            isDeactivated: false,
            hasRoutePath: true,
        });

        this.isPreviewActive = true;
        this.activeRoute?.onDeactivate();
        this.activeRoute = null;

        const activeRoutesIds : string[] = activeRoutes.map(route => route.id);

        this.routes.forEach(route => {
            if (activeRoutesIds.includes(route.id)) {
                route.setVisibility(RouteVisibility.Preview);
            } else {
                route.setVisibility(RouteVisibility.Hidden);
            }
        });

        this.fitBounds(<google.maps.LatLngBounds>this.getBounds(activeRoutes));
    }

    filterRoutes (routes : CoverageRoute[], filter : {
        isDeactivated? : boolean;
        includeToFocus? : boolean;
        hasRoutePath? : boolean;
        groupId? : string;
    }) : CoverageRoute[] {
        const checkIsDeactivated = 'isDeactivated' in filter;
        const checkIncludeToFocus = 'includeToFocus' in filter;
        const checkHasRoutePath = 'hasRoutePath' in filter;
        const checkGroupId = 'groupId' in filter;

        const activeGroupIds : string[] = this.groups.reduce((acc, group) => {
            const isIsDeactivatedOk = !checkIsDeactivated || group.isDeactivated === filter.isDeactivated;
            const isIncludeToFocusOk = !checkIncludeToFocus || group.includeToFocus === filter.includeToFocus;
            const isGroupIdOk = !checkGroupId || group.id === filter.groupId;

            if (isIsDeactivatedOk && isIncludeToFocusOk && isGroupIdOk) {
                acc.push(group.id);
            }

            return acc;
        }, []);

        return routes.filter(route => {
            const isGroupOk = (
                checkGroupId ?
                route.groupId === filter.groupId :
                (!route.groupId || activeGroupIds.includes(route.groupId))
            );

            const isRoutePathOk = !checkHasRoutePath || route.hasRoutePath() === filter.hasRoutePath;

            return isGroupOk && isRoutePathOk;
        });
    }

    getBounds (
        routes : CoverageRoute[],
        asJson : boolean = false
    ) : null | google.maps.LatLngBounds | google.maps.LatLngBoundsLiteral {
        if (!routes || !routes.length) {
            return null;
        }

        const bounds = new google.maps.LatLngBounds();

        routes.forEach(route => {
            route.getRoutePath().forEach(point => bounds.extend(point));
        });

        return asJson ? bounds.toJSON() : bounds;
    }

    onShowHelp () {
        this.isHelpVisible = true;
    }

    onHideHelp () {
        this.isHelpVisible = false;
    }

    setActiveRoute (route : null | CoverageRoute, boundToRoute : boolean = false) {
        if (this.isPreviewActive) {
            this.isPreviewActive = false;
            this.routes.forEach(item => item.setVisibility(RouteVisibility.Inactive));
        } else {
            this.activeRoute?.setVisibility(RouteVisibility.Inactive);
        }

        this.activeRoute?.onDeactivate();
        this.activeRoute = route;

        if (this.activeRoute) {
            this.activeRoute.setVisibility(RouteVisibility.Active);

            if (boundToRoute) {
                this.fitBounds(route.getBounds());
            }
        } else {
            this.isPreviewActive = true;
            this.routes.forEach(item => item.setVisibility(RouteVisibility.Preview));
        }
    }

    fitBounds (bounds : null | google.maps.LatLngBounds) {
        if (bounds) {
            this.map.fitBounds(bounds, {
                top: MAP_BASE_PADDING + SEARCH_HEIGHT + UI_MARGIN,
                left: MAP_BASE_PADDING,
                bottom: MAP_BASE_PADDING,
                right: MAP_BASE_PADDING + UI_WIDTH + UI_MARGIN
            });
        }
    }

    scrollToRoute (route : CoverageRoute) {
        const scrollEl = this.scrollEl?.nativeElement;

        if (!route || !scrollEl) {
            return;
        }

        const routeEl = scrollEl.querySelector(`.coverage__ui-route[data-route-id='${ route.id }']`);

        if (!routeEl) {
            return;
        }

        routeEl.scrollIntoView({
            behavior: 'smooth'
        });
    }

    onRemoveRoute (route : CoverageRoute) {
        if (!route || !this.hasRoutes()) {
            return;
        }

        if (this.checkActiveRoute(route)) {
            this.activeRoute = null;
        }

        route.detach();
        this.routes = this.routes.filter(item => item.id !== route.id);
    }

    async onSave () {
        if (this.isSaving) {
            return;
        }

        this.isSaving = true;
        this.renderer.addClass(document.body, BODY_LOCK_CLASS);
        this.map.set('keyboardShortcuts', false);

        const routes = this.routes;
        const groups = this.groups || [];

        const initialFocusRoutes = this.filterRoutes(routes, {
            isDeactivated: false,
            includeToFocus: true,
            hasRoutePath: true
        });

        const nonEmptyRoutes = this.filterRoutes(routes, {
            hasRoutePath: true
        });

        groups.forEach(group => {
            const groupRoutes = nonEmptyRoutes.filter(route => route.groupId === group.id);

            if (groupRoutes.length > 0) {
                group.bounds = <google.maps.LatLngBoundsLiteral>this.getBounds(groupRoutes, true);
            } else {
                group.bounds = null;
            }
        });

        const isOk = await this.coverageService.saveCoverage({
            groups,
            routes: routes.map(route => route.serialize()),
            bounds: <google.maps.LatLngBoundsLiteral>this.getBounds(initialFocusRoutes, true),
            settings: this.settings,
            version: COVERAGE_CURRENT_VERSION
        }).toPromise().catch(() => false);

        this.map.set('keyboardShortcuts', true);
        this.renderer.removeClass(document.body, BODY_LOCK_CLASS);
        this.isSaving = false;

        this.toastService.create({
            message: [ isOk ? 'coverage.save_success' : 'coverage.save_error' ],
            timeout: 5000
        });
    }

    onSwitchTab (tab : Tab) {
        if (this.activeTab === tab) {
            return;
        }

        this.activeTab = tab;
    }

    trackRouteBy (index, route : CoverageRoute) : string {
        return route.id;
    }

    trackGantryBy (index, gantry : CoverageGantry) : string {
        return gantry.id;
    }

    trackGroupBy (index, group : CoverageGroup) : string {
        return group.id;
    }

    onAddNewGroup () {
        const group : CoverageGroup = {
            id: uuid4(),
            name: '',
            bounds: null,
            isDeactivated: false,
            includeToFocus: true
        };

        this.groups.push(group);
        this.activeGroupId = group.id;
    }

    onSwitchGroup (group : CoverageGroup) {
        this.activeGroupId = this.activeGroupId === group.id ? null : group.id;
    }

    getGroupName (group : CoverageGroup) : string {
        return (group?.name || '').trim();
    }

    onRemoveGroup (group : CoverageGroup) {
        this.routes.forEach(route => {
            if (route.groupId === group.id) {
                route.groupId = null;
            }
        });

        if (this.activeGroupId === group.id) {
            this.activeGroupId = null;
        }

        this.groups = this.groups.filter(item => item.id !== group.id);
    }

    onGroupDeactivatedChange (group : CoverageGroup) {
        if (!this.isPreviewActive) {
            return;
        }

        const groupRoutes = this.filterRoutes(this.routes, {
            hasRoutePath: true,
            groupId: group.id
        });

        groupRoutes.forEach(route => {
            if (group.isDeactivated) {
                route.setVisibility(RouteVisibility.Hidden);
            } else {
                route.setVisibility(RouteVisibility.Preview);
            }
        });
    }

    // --------------------------------------------------------------

    @ViewChild('searchEl')
    searchEl : ElementRef<HTMLInputElement>;

    isSearchSubmitting : boolean = false;

    isSearchPopupVisible : boolean = false;

    searchTerm : string = '';

    searchItems : google.maps.places.PlaceResult[] = null;

    searchRequestId : number = -1;

    get isSearchClearButtonVisible () : boolean {
        return !!this.searchTerm;
    }

    initSearch () {
        this.subs.push(
            fromEvent(this.searchEl.nativeElement, 'input')
                .pipe(
                    map((e : any) => e.target.value.trim()),
                    debounceTime(150),
                    distinctUntilChanged(),
                )
                .subscribe((term : string) => this.onSearchTermChange(term))
        );
    }

    async onSearchTermChange (term : string) {
        this.searchRequestId += 1;

        if (term.length < 3) {
            this.searchItems = null;
            this.isSearchSubmitting = false;
            this.isSearchPopupVisible = false;
            return;
        }

        const currentRequestId = this.searchRequestId;
        this.isSearchSubmitting = true;

        const searchItems = await this.doSearchRequest(term).catch(() => null);

        if (currentRequestId !== this.searchRequestId) {
            return;
        }

        if (searchItems && searchItems.length > 0) {
            this.searchItems = searchItems.slice(0, 10);
        } else {
            this.searchItems = null;
        }

        this.isSearchSubmitting = false;
        this.isSearchPopupVisible = true;
    }

    async doSearchRequest (term : string) : Promise<null | google.maps.places.PlaceResult[]> {
        return new Promise((resolve) => {
            this.placesService.textSearch({
                query: term,
                // fields: [ 'formatted_address', 'geometry.location' ],
            }, (results, status) => {
                resolve(status === google.maps.places.PlacesServiceStatus.OK && results || null);
            });
        });
    }

    onSearchClearClick () {
        this.hideSearchPopup();
        this.resetSearch();

        defer(() => this.searchEl?.nativeElement.focus());
    }

    onSearchItemClick (place : google.maps.places.PlaceResult) {
        this.hideSearchPopup();

        if (this.map) {
            this.map.panTo(place.geometry.location);
            this.map.setZoom(15);
        }
    }

    hideSearchPopup () {
        this.searchRequestId += 1;
        this.isSearchSubmitting = false;
        this.isSearchPopupVisible = false;
    }

    resetSearch () {
        this.searchRequestId += 1;
        this.searchItems = null;
        this.searchTerm = '';
    }

    @HostListener('click', [ '$event' ])
    onHostClick (e : any) {
        this.domService.markEvent(e, 'coverageSearchHostClick');
    }

    @HostListener('document:click', [ '$event' ])
    onDocClick (e : any) {
        if (!this.domService.hasEventMark(e, 'coverageSearchHostClick')) {
            this.hideSearchPopup();
        }
    }

    onSearchInputFocus () {
        if (this.searchItems) {
            this.isSearchPopupVisible = true;
        }
    }
}
