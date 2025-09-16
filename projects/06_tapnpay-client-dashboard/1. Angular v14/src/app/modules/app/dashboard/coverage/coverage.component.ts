import {
    ChangeDetectionStrategy,
    Component,
    ElementRef, HostListener, NgZone,
    OnDestroy,
    OnInit,
    Renderer2,
    ViewChild,
    ViewEncapsulation
} from '@angular/core';
import {Router} from '@angular/router';
import {TitleService} from '../../../../services/title.service';
import {DeviceService, ViewportBreakpoint} from '../../../../services/device.service';
import {Subscription} from 'rxjs';
import {AccountPaymentModel, AccountTollAuthority, UserService} from '../../../../services/user.service';
import {ToastService} from '../../../../services/toast.service';
import {GoogleService} from '../../../../services/google.service';
import {
    Coverage,
    CoverageGantry,
    CoverageGroup,
    CoverageRoute,
    CoverageService
} from '../../../../services/coverage.service';
import {defer} from '../../../../lib/utils';
import {cloneDeep} from 'lodash-es';
import {animate, animateChild, group, query, style, transition, trigger} from '@angular/animations';


type State = 'loading' | 'ready' | 'error';


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
        trigger('sidebar', [
            transition(':enter, :leave', [
                group([
                    query('@sidebarOverlay', animateChild()),
                    query('@sidebarPopup', animateChild()),
                ])
            ]),
        ]),
        trigger('sidebarOverlay', [
            transition(':enter', [
                style({ opacity: 0 }),
                animate('0.15s cubic-bezier(0.5, 1, 0.89, 1)', style({ opacity: '*' })),
            ]),
            transition(':leave', [
                style({ opacity: '*' }),
                animate('0.15s cubic-bezier(0.5, 1, 0.89, 1)', style({ opacity: 0 })),
            ])
        ]),
        trigger('sidebarPopup', [
            transition(':enter', [
                style({ transform: 'translateX(100%)' }),
                animate('0.15s cubic-bezier(0.5, 1, 0.89, 1)', style({ transform: '*' }))
            ]),
            transition(':leave', [
                style({ transform: '*' }),
                animate('0.15s cubic-bezier(0.5, 1, 0.89, 1)', style({ transform: 'translateX(100%)' }))
            ])
        ]),
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
    ]
})
export class CoverageComponent implements OnInit, OnDestroy {
    viewportBreakpoint : ViewportBreakpoint;

    subs : Subscription[] = [];

    state : State = 'loading';

    bounds : google.maps.LatLngBoundsLiteral;

    coverageRoutes : CoverageRoute[];

    visibleCoverageRoutes : CoverageRoute[];

    @ViewChild('mapEl')
    mapEl : ElementRef<HTMLDivElement>;

    map : google.maps.Map;

    @ViewChild('searchInputEl')
    searchInputEl : ElementRef;

    searchValue : string = '';

    searchTimeout : any = null;

    isClearVisible : boolean = false;

    isSidebarActive : boolean = false;

    activeRouteId : string = null;

    activeGantryId : string = null;

    paymentModel : AccountPaymentModel = null;

    tollAuthority : AccountTollAuthority = null;

    constructor (
        private hostEl : ElementRef,
        private renderer : Renderer2,
        private router : Router,
        private zone : NgZone,
        private titleService : TitleService,
        private deviceService : DeviceService,
        private googleService : GoogleService,
        private userService : UserService,
        private coverageService : CoverageService,
    ) {
        window.scroll(0, 0);

        this.state = 'loading';

        const { account } = this.userService.getUserData();

        this.paymentModel = account.paymentModel;
        this.tollAuthority = account.tollAuthority;

        this.viewportBreakpoint = this.deviceService.viewportBreakpoint;
        this.subs.push(this.deviceService.onResize.subscribe((message) => {
            if (message.breakpointChange) {
                this.viewportBreakpoint = message.breakpointChange.current;
                this.onSidebarStateChange(false);
            }
        }));
    }

    async ngOnInit () {
        this.titleService.setTitle('coverage.page_title');

        const [ serializedCoverage, isMapLoaded ] : [ Coverage, boolean ] = await Promise.all([
            this.coverageService.fetchCoverage().toPromise(),
            this.initMap()
        ]).catch(() => [ null, false ]);

        if (!serializedCoverage || !isMapLoaded) {
            this.state = 'error';
            return;
        }

        console.log(this.tollAuthority);

        const group = this.getGroupByTA(serializedCoverage.groups, this.tollAuthority);

        if (!group) {
            this.state = 'error';
            return;
        }

        const { routes } = await this.coverageService.deserializeCoverage(serializedCoverage);

        this.coverageRoutes = routes.filter(route => route.groupId === group.id);
        this.bounds = group.bounds;

        this.coverageRoutes.forEach((route) => {
            const { routePolyline, gantries } = route;

            routePolyline.setVisible(false);
            routePolyline.setMap(this.map);

            google.maps.event.addListener(routePolyline, 'click', () => this.onRouteClick(route));

            gantries.forEach((gantry) => {
                const { marker } = gantry;

                marker.setVisible(false);
                marker.setMap(this.map);
            });
        });

        this.setCoverageRoutes(this.coverageRoutes);
        this.updateMap();

        if (this.bounds) {
            this.fitBounds(this.bounds);
        }

        this.state = 'ready';
    }

    ngOnDestroy () : void {
        this.subs.forEach(sub => sub.unsubscribe());
    }

    getGroupByTA (groups : CoverageGroup[], tollAuthority : AccountTollAuthority) : null | CoverageGroup {
        return groups.find(group => group.name.toUpperCase() === tollAuthority.toUpperCase()) || null;
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
            fullscreenControl: false,
            streetViewControl: false,
            mapTypeControl: false,
            draggableCursor: 'default',
            disableDoubleClickZoom: false,
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

        return true;
    }

    setCoverageRoutes (coverageRoutes : null | CoverageRoute[]) {
        this.visibleCoverageRoutes = coverageRoutes || [];
    }

    onSidebarStateChange (isActive : boolean) {
        this.isSidebarActive = isActive;
    }

    // --------------------------------------------------

    resetSearchTimeout () {
        if (this.searchTimeout !== null) {
            clearTimeout(this.searchTimeout);
            this.searchTimeout = null;
        }
    }

    onSearch () {
        this.resetSearchTimeout();

        const value : string = (this.searchValue || '').trim();

        this.isClearVisible = !!this.searchValue;

        if (value.length < 3) {
            this.setCoverageRoutes(this.coverageRoutes);
            return;
        }

        this.searchTimeout = setTimeout(() => {
            this.zone.run(() => {
                this.resetSearchTimeout();
                this.doSearch(value);
            });
        }, 250);
    }

    doSearch (value : string) {
        const regexPattern = (
            value
                .trim()
                .replace(/\s+/, ' ')
                .split('')
                .map(char => char === ' ' ? '\\s' : ('\\u' + char.charCodeAt(0).toString(16).padStart(4, '0')))
                .join('')
        );

        let regex : RegExp = null;

        try {
            regex = RegExp(`(${ regexPattern })`, 'ig');
        } catch (e) {
            console.warn(`Failed to compile regex for value '${ value }'`);
            return;
        }

        this.visibleCoverageRoutes = this.coverageRoutes.reduce((routeAcc : CoverageRoute[], route : CoverageRoute) => {
            const gantries = route.gantries.reduce((gantryAcc : CoverageGantry[], gantry : CoverageGantry) => {
                const newName = gantry.name.replace(regex, '<span class="coverage__ui-search-highlight">$1</span>');
                const newCode = gantry.code.replace(regex, '<span class="coverage__ui-search-highlight">$1</span>');

                if (newName !== gantry.name || newCode !== gantry.code) {
                    const foundGantry = Object.assign({}, gantry);  // shallow copy

                    foundGantry.name = newName;
                    foundGantry.code = newCode;

                    gantryAcc.push(foundGantry);
                }

                return gantryAcc;
            }, []);

            const newName = route.name.replace(regex, '<span class="coverage__ui-search-highlight">$1</span>');

            if (newName !== route.name || gantries.length) {
                const foundRoute = Object.assign({}, route);  // shallow copy

                foundRoute.name = newName;
                foundRoute.gantries = gantries;
                foundRoute.isExpanded = foundRoute.gantries.length > 0;

                routeAcc.push(foundRoute);
            }

            return routeAcc;
        }, []);
    }

    resetSearch () {
        this.resetSearchTimeout();
        this.searchValue = '';
        this.setCoverageRoutes(this.coverageRoutes);
        this.isClearVisible = false;
    }

    onClearSearchClick () {
        this.resetSearch();

        if (!this.deviceService.device.touch) {
            this.focusOnSearchInput();
        }
    }

    onSearchKeyDown (e : KeyboardEvent) {
        if (e.code === 'Escape') {
            e.preventDefault();
            this.resetSearch();
            this.searchInputEl.nativeElement?.blur();
        }
    }

    focusOnSearchInput () {
        defer(() => this.searchInputEl?.nativeElement.focus());
    }

    @HostListener('document:keydown', [ '$event' ])
    onDocKeyDown (e : KeyboardEvent) {
        if (e.ctrlKey && e.code === 'KeyF') {
            const inputEl = this.searchInputEl.nativeElement || null;

            if (inputEl && !inputEl.matches(':focus')) {
                e.preventDefault();
                inputEl.focus();
            }
        }
    }

    // -----------------------------------------------

    trackRouteBy (index, route : CoverageRoute) : string {
        return route.id;
    }

    trackGantryBy (index, gantry : CoverageGantry) : string {
        return gantry.id;
    }

    onRouteClick (route : CoverageRoute) {
        if (this.activeRouteId === route.id) {
            return;
        }

        this.onRouteEyeClick(route);

        if (this.activeRouteId) {
            const selector = `.coverage__route[data-route-id='${ route.id }']`;
            const routeEl = this.hostEl?.nativeElement.querySelector(selector);

            if (routeEl) {
                routeEl.scrollIntoView({
                    behavior: 'smooth'
                });
            }
        }
    }

    onRouteExpandClick (route : CoverageRoute) {
        if (!route.gantries.length) {
            return;
        }

        if (route.isExpanded) {
            route.isExpanded = false;
        } else {
            this.visibleCoverageRoutes.forEach(item => {
                item.isExpanded = item.id === route.id;
            });
        }
    }

    onRouteEyeClick (route : CoverageRoute) {
        this.activeRouteId = this.activeRouteId === route.id ? null : route.id;
        this.activeGantryId = null;

        this.onSidebarStateChange(false);
        this.updateMap();

        if (this.activeRouteId) {
            this.fitBounds(this.getRouteBounds(route));
        } else if (this.bounds) {
            this.fitBounds(this.bounds);
        }
    }

    onToggleGantry (route : CoverageRoute, gantry : CoverageGantry) {
        const isRouteChanged = this.activeRouteId !== route.id;

        if (this.activeGantryId === gantry.id) {
            this.activeGantryId = null;
        } else {
            this.activeRouteId = route.id;
            this.activeGantryId = gantry.id;
        }

        this.onSidebarStateChange(false);
        this.updateMap();

        if (isRouteChanged && this.activeGantryId) {
            this.fitBounds(this.getRouteBounds(route));
        }
    }

    updateMap () {
        this.coverageRoutes.forEach((route) => {
            const isActiveRoute = route.id === this.activeRouteId;

            if (!this.activeRouteId || isActiveRoute) {
                route.routePolyline.set('strokeColor', route.routeColor);
                route.routePolyline.set('strokeOpacity', route.routeOpacity);
                route.routePolyline.setVisible(true);
            } else {
                route.routePolyline.set('strokeColor', '#000');
                route.routePolyline.set('strokeOpacity', 0.35);
                route.routePolyline.setVisible(true);
            }

            route.gantries.forEach((gantry) => {
                if (isActiveRoute) {
                    if (gantry.id === this.activeGantryId) {
                        gantry.marker.setIcon(null);
                    } else {
                        gantry.marker.setIcon({
                            path: google.maps.SymbolPath.CIRCLE,
                            fillColor: '#fff',
                            fillOpacity: 1,
                            strokeWeight: 2,
                            strokeColor: route.routeColor,
                            scale: route.routeWeight
                        });
                    }

                    gantry.marker.setVisible(true);
                } else {
                    gantry.marker.setVisible(false);
                }
            });
        });
    }

    fitBounds (bounds : null | google.maps.LatLngBounds | google.maps.LatLngBoundsLiteral) {
        if (!bounds) {
            return;
        }

        if (this.viewportBreakpoint === 'desktop') {
            this.map.fitBounds(bounds, {
                top: 0,
                left: 20 + 360,
                bottom: 0,
                right: 0
            });
        } else {
            this.map.fitBounds(bounds);
        }
    }

    getRouteBounds (route : CoverageRoute) : null | google.maps.LatLngBounds {
        const path = route.routePolyline.getPath().getArray();

        if (!path.length) {
            return null;
        }

        const bounds = new google.maps.LatLngBounds();

        path.forEach(point => bounds.extend(point));

        return bounds;
    }
}
