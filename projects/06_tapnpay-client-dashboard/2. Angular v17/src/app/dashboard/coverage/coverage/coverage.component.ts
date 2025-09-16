import {
    ChangeDetectionStrategy,
    Component,
    ElementRef,
    HostListener,
    NgZone,
    OnDestroy,
    OnInit,
    Renderer2,
    ViewChild,
    ViewEncapsulation
} from '@angular/core';
import {Router} from '@angular/router';
import {TitleService} from '../../../services/title.service';
import {DeviceService, ViewportBreakpoint} from '../../../services/device.service';
import {firstValueFrom, Subscription} from 'rxjs';
import {AccountPaymentModel, AccountTollAuthority, UserService} from '../../../services/user.service';
import {GoogleService} from '../../../services/google.service';
import {
    Coverage,
    CoverageGantry,
    CoverageGroup,
    CoverageRoute,
    CoverageService
} from '../../../services/coverage.service';
import {defer} from '../../../lib/utils';
import {animate, animateChild, group, query, style, transition, trigger} from '@angular/animations';
import {
    AllLicensePlatesHttpResponse,
    LicensePlateItem,
    LicensePlatesService
} from "../../../services/license-plates.service";
import {map} from "rxjs/operators";


type pageDataLoadState = 'loading' | 'ready' | 'error';


@Component({
    selector: 'coverage',
    templateUrl: './coverage.component.html',
    styleUrls: ['./coverage.component.scss'],
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
                style({opacity: 0}),
                animate('0.15s cubic-bezier(0.5, 1, 0.89, 1)', style({opacity: '*'})),
            ]),
            transition(':leave', [
                style({opacity: '*'}),
                animate('0.15s cubic-bezier(0.5, 1, 0.89, 1)', style({opacity: 0})),
            ])
        ]),
        trigger('sidebarPopup', [
            transition(':enter', [
                style({transform: 'translateX(100%)'}),
                animate('0.15s cubic-bezier(0.5, 1, 0.89, 1)', style({transform: '*'}))
            ]),
            transition(':leave', [
                style({transform: '*'}),
                animate('0.15s cubic-bezier(0.5, 1, 0.89, 1)', style({transform: 'translateX(100%)'}))
            ])
        ]),
        trigger('expand', [
            transition(':enter', [
                style({height: '0px'}),
                animate('0.15s cubic-bezier(0.5, 1, 0.89, 1)', style({height: '*'}))
            ]),
            transition(':leave', [
                style({height: '*'}),
                animate('0.15s cubic-bezier(0.5, 1, 0.89, 1)', style({height: '0px'}))
            ])
        ]),
    ]
})
export class CoverageComponent implements OnInit, OnDestroy {
    viewportBreakpoint: ViewportBreakpoint;

    subs: Subscription[] = [];

    pageLoadState: pageDataLoadState = 'loading';

    tollAuthorityMapBounds: google.maps.LatLngBoundsLiteral;

    listOfSelectedLPNTollAuthorityRoads: CoverageRoute[] = [];

    listOfVisibleTollAuthorityRoads: CoverageRoute[];

    @ViewChild('mapEl')
    mapEl: ElementRef<HTMLDivElement>;

    googleMap: google.maps.Map;

    @ViewChild('searchInputEl')
    searchInputEl: ElementRef;

    searchValue: string = '';

    searchTimeout: any = null;

    isClearVisible: boolean = false;

    isSidebarActive: boolean = false;

    activeRouteId: string = null;

    activeGantryId: string = null;

    paymentModel: AccountPaymentModel = null;

    selectedLPNTollAuthorities: AccountTollAuthority[] = null;

    listOfLicensePlates: LicensePlateItem[] = null;
    selectedLicensePlate: LicensePlateItem | null = null;

    constructor(
        private hostEl: ElementRef,
        private renderer: Renderer2,
        private router: Router,
        private zone: NgZone,
        private titleService: TitleService,
        private deviceService: DeviceService,
        private googleService: GoogleService,
        private userService: UserService,
        private coverageService: CoverageService,
        private licensePlatesService: LicensePlatesService,
    ) {
        window.scroll(0, 0);

        this.setPageDataLoadState('loading');

        const {account} = this.userService.getUserData();

        this.viewportBreakpoint = this.deviceService.viewportBreakpoint;
        this.subs.push(this.deviceService.onResize.subscribe((message) => {
            if (message.breakpointChange) {
                this.viewportBreakpoint = message.breakpointChange.current;
                this.hideSidebar();
            }
        }));
    }

    private setPageDataLoadState(state: pageDataLoadState) {
        this.pageLoadState = state ? state : 'loading';
    }

    async ngOnInit() {
        this.titleService.setTitle('coverage.page_title');
        this.getLicensePlates();
    }


    ngOnDestroy(): void {
        this.subs.forEach(sub => sub.unsubscribe());
    }

    private async initPageData() {
        try {
            const [serializedCoverage, isMapLoaded]: [Coverage, boolean] = await Promise.all([
                firstValueFrom(this.coverageService.getMapCoverageFullData()),
                this.initMap(),
            ]);

            if (!serializedCoverage || !isMapLoaded) {
                this.pageLoadState = 'error';
                return;
            }

            // Retrieve groups for selected toll authorities
            const tollAuthorityMapItemsGroup: CoverageGroup[] = this.selectedLPNTollAuthorities
                .map((tollAuthority) =>
                    this.getMapItemsGroupForTollAuthority(serializedCoverage.groups, tollAuthority)
                )
                .filter((group): group is CoverageGroup => !!group);

            if (tollAuthorityMapItemsGroup.length === 0) {
                this.pageLoadState = 'error';
                return;
            }

            const {listOfAllTollAuthoritiesRoads} = await this.coverageService.deserializeCoverage(
                serializedCoverage
            );

            // Get roads for selected toll authorities
            this.listOfSelectedLPNTollAuthorityRoads = tollAuthorityMapItemsGroup.flatMap((group) =>
                this.getListOfTollAuthorityRoads(listOfAllTollAuthoritiesRoads, group)
            );

            // Set map bounds
            this.tollAuthorityMapBounds = tollAuthorityMapItemsGroup[0]?.bounds || serializedCoverage.bounds;

            // Initialize routes and gantries
            this.listOfSelectedLPNTollAuthorityRoads.forEach((route) => {
                const {routePolyline, gantries} = route;

                routePolyline.setVisible(false);
                routePolyline.setMap(this.googleMap);

                google.maps.event.addListener(routePolyline, 'click', () => this.onRouteClick(route));

                gantries.forEach((gantry) => {
                    const {marker} = gantry;

                    marker.setVisible(false);
                    marker.setMap(this.googleMap);
                });
            });

            this.setCoverageRoutes(this.listOfSelectedLPNTollAuthorityRoads);
            this.updateMap();

            if (this.tollAuthorityMapBounds) {
                this.fitMapBounds(this.tollAuthorityMapBounds);
            }

            this.pageLoadState = 'ready';
        } catch (error) {
            console.error('Error initializing page data:', error);
            this.pageLoadState = 'error';
        }
    }


    private getListOfTollAuthorityRoads(listOfAllTollAuthoritiesRoutes: CoverageRoute[], tollAuthorityMapItemsGroup: CoverageGroup): CoverageRoute[] {
        if (listOfAllTollAuthoritiesRoutes && listOfAllTollAuthoritiesRoutes.length > 0 && tollAuthorityMapItemsGroup) {
            return listOfAllTollAuthoritiesRoutes.filter(route => route.groupId === tollAuthorityMapItemsGroup.id);
        } else {
            return [];
        }
    }

    private getLicensePlates() {
        this.licensePlatesService.getAllLicensePlates().pipe(
            map(
                (res: AllLicensePlatesHttpResponse) => [...res.plates, ...res.rental_plates].sort(this.sortByDate()
                ),
            )).subscribe(
            {
                next: (listOfAllUserLPNs) => {
                    this.listOfLicensePlates = listOfAllUserLPNs;
                    const firstLicensePlateItem = this.listOfLicensePlates[0];
                    this.selectedLicenseId = this.listOfLicensePlates && firstLicensePlateItem ? firstLicensePlateItem.id : null;
                    if (this.selectedLicenseId) {
                        this.setSelectedLicensePlate(this.selectedLicenseId);
                        this.getLicensePlateCoverage(this.selectedLicenseId);
                    } else {
                        this.selectedLPNTollAuthorities = [this.getUserDefaultTollAuthority()];
                        this.initPageData().then(_r => {
                        });
                    }
                },
                error: (err) => {
                    this.pageLoadState = 'error';
                    console.error(err);
                }
            }
        );
    }

    private sortByDate() {
        return (a: LicensePlateItem, b: LicensePlateItem) => {
            if (a.registered > b.registered) {
                return -1;
            }
            if (a.registered < b.registered) {
                return 1;
            }
            return 0;
        };
    }

    private getLicensePlateCoverage(licensePlateId: string) {
        this.licensePlatesService.getLicensePlateCoverage(licensePlateId).subscribe(
            async res => {
                this.selectedLPNTollAuthorities = res.coverage ? res.coverage : null;
                await this.initPageData();
            });
    }

    private getUserDefaultTollAuthority() {
        const {account} = this.userService.getUserData();
        return account.tollAuthority;
    }

    getMapItemsGroupForTollAuthority(groups: CoverageGroup[], tollAuthority: AccountTollAuthority): null | CoverageGroup {
        return groups.find(group => group.name.toUpperCase() === tollAuthority.toUpperCase()) || null;
    }

    async initMap(): Promise<boolean> {
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
        this.googleMap = new google.maps.Map(<HTMLElement>this.mapEl.nativeElement, {
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

    setCoverageRoutes(coverageRoutes: null | CoverageRoute[]) {
        this.listOfVisibleTollAuthorityRoads = coverageRoutes || [];
    }

    onSidebarStateChange(isActive: boolean) {
        this.isSidebarActive = isActive;
    }

    // --------------------------------------------------

    resetSearchTimeout() {
        if (this.searchTimeout !== null) {
            clearTimeout(this.searchTimeout);
            this.searchTimeout = null;
        }
    }

    onSearch() {
        this.resetSearchTimeout();

        const value: string = (this.searchValue || '').trim();

        this.isClearVisible = !!this.searchValue;

        if (value.length < 3) {
            this.setCoverageRoutes(this.listOfSelectedLPNTollAuthorityRoads);
            return;
        }

        this.searchTimeout = setTimeout(() => {
            this.zone.run(() => {
                this.resetSearchTimeout();
                this.makeSearchByText(value);
            });
        }, 250);
    }

    makeSearchByText(value: string) {
        const sanitizedValue = value.trim().replace(/\s+/g, ' ');
        if (!sanitizedValue) {
            this.listOfVisibleTollAuthorityRoads = [];
            return;
        }


        const escapedValue = sanitizedValue.replace(/[.*+?^${}()|[\]\\]/g, '\\$&').replace(/\s/g, '\\s+');
        let regex: RegExp;

        try {
            regex = new RegExp(`(${escapedValue})`, 'ig');
        } catch (e) {
            console.warn(`Failed to compile regex for value '${value}':`, e);
            return;
        }

        this.listOfVisibleTollAuthorityRoads = this.listOfSelectedLPNTollAuthorityRoads
            .map((route) => {
                const matchedGantries = route.gantries
                    .map((gantry) => {
                        const nameMatch = regex.test(gantry.name);
                        const codeMatch = regex.test(gantry.code);

                        if (nameMatch || codeMatch) {
                            return {
                                ...gantry,
                                name: gantry.name.replace(regex, '<span class="coverage__ui-search-highlight">$1</span>'),
                                code: gantry.code.replace(regex, '<span class="coverage__ui-search-highlight">$1</span>'),
                            };
                        }
                        return null;
                    })
                    .filter((gantry) => gantry !== null);

                const routeNameMatch = regex.test(route.name);

                if (routeNameMatch || matchedGantries.length > 0) {
                    return {
                        ...route,
                        name: route.name.replace(regex, '<span class="coverage__ui-search-highlight">$1</span>'),
                        gantries: matchedGantries,
                        isExpanded: matchedGantries.length > 0,
                    };
                }
                return null;
            })
            .filter((route) => route !== null);
    }


    resetSearch() {
        this.resetSearchTimeout();
        this.searchValue = '';
        this.setCoverageRoutes(this.listOfSelectedLPNTollAuthorityRoads);
        this.isClearVisible = false;
    }

    onClearSearchClick() {
        this.resetSearch();

        if (!this.deviceService.device.touch) {
            this.focusOnSearchInput();
        }
    }

    onSearchKeyDown(e: KeyboardEvent) {
        if (e.code === 'Escape') {
            e.preventDefault();
            this.resetSearch();
            this.searchInputEl.nativeElement?.blur();
        }
    }

    focusOnSearchInput() {
        defer(() => this.searchInputEl?.nativeElement.focus());
    }

    @HostListener('document:keydown', ['$event'])
    onDocKeyDown(e: KeyboardEvent) {
        if (e.ctrlKey && e.code === 'KeyF') {
            const inputEl = this.searchInputEl.nativeElement || null;

            if (inputEl && !inputEl.matches(':focus')) {
                e.preventDefault();
                inputEl.focus();
            }
        }
    }

    // -----------------------------------------------
    selectedLicenseId: string | null = null;


    trackRouteBy(index, route: CoverageRoute): string {
        return route.id;
    }

    trackGantryBy(index, gantry: CoverageGantry): string {
        return gantry.id;
    }

    onRouteClick(route: CoverageRoute) {
        if (this.activeRouteId === route.id) {
            return;
        }

        this.showRoadOnMap(route);

        if (this.activeRouteId) {
            const selector = `.coverage__route[data-route-id='${route.id}']`;
            const routeEl = this.hostEl?.nativeElement.querySelector(selector);

            if (routeEl) {
                routeEl.scrollIntoView({
                    behavior: 'smooth'
                });
            }
        }
    }

    onRouteExpandClick(route: CoverageRoute) {
        if (!route.gantries.length) {
            return;
        }

        if (route.isExpanded) {
            route.isExpanded = false;
        } else {
            this.listOfVisibleTollAuthorityRoads.forEach(item => {
                item.isExpanded = item.id === route.id;
            });
        }
    }

    showRoadOnMap(road: CoverageRoute) {
        this.activeRouteId = this.activeRouteId === road.id ? null : road.id;
        this.activeGantryId = null;

        this.hideSidebar();
        this.updateMap();

        if (this.activeRouteId) {
            this.fitMapBounds(this.getRouteBounds(road));
        } else if (this.tollAuthorityMapBounds) {
            this.fitMapBounds(this.tollAuthorityMapBounds);
        }
    }

    private hideSidebar() {
        this.onSidebarStateChange(false);
    }

    onToggleGantry(route: CoverageRoute, gantry: CoverageGantry) {
        const isRouteChanged = this.activeRouteId !== route.id;

        if (this.activeGantryId === gantry.id) {
            this.activeGantryId = null;
        } else {
            this.activeRouteId = route.id;
            this.activeGantryId = gantry.id;
        }

        this.hideSidebar();
        this.updateMap();

        if (isRouteChanged && this.activeGantryId) {
            this.fitMapBounds(this.getRouteBounds(route));
        }
    }

    updateMap() {
        this.listOfSelectedLPNTollAuthorityRoads.forEach((route) => {
            const isActiveRoute = route.id === this.activeRouteId;

            this.updateRoutePolyline(route, isActiveRoute);
            this.updateGantryMarkers(route, isActiveRoute);
        });
    }

    private updateRoutePolyline(route, isActiveRoute: boolean) {
        const strokeColor = !this.activeRouteId || isActiveRoute ? route.routeColor : '#000';
        const strokeOpacity = !this.activeRouteId || isActiveRoute ? route.routeOpacity : 0.35;

        // Update strokeColor if it has changed
        if (route.routePolyline.get('strokeColor') !== strokeColor) {
            route.routePolyline.set('strokeColor', strokeColor);
        }

        // Update strokeOpacity if it has changed
        if (route.routePolyline.get('strokeOpacity') !== strokeOpacity) {
            route.routePolyline.set('strokeOpacity', strokeOpacity);
        }

        // Ensure the polyline is visible
        if (!route.routePolyline.getVisible()) {
            route.routePolyline.setVisible(true);
        }
    }

    private updateGantryMarkers(route: CoverageRoute, isActiveRoute: boolean) {
        route.gantries.forEach((gantry: CoverageGantry) => {
            if (isActiveRoute) {
                this.updateActiveGantryMarker(gantry, route);
            } else {
                this.hideGantryMarker(gantry);
            }
        });
    }

    private updateActiveGantryMarker(gantry: CoverageGantry, route: CoverageRoute) {
        if (gantry.id === this.activeGantryId) {
            if (gantry.marker.getIcon() !== null) {
                gantry.marker.setIcon(null);
            }
        } else {
            const desiredIcon = {
                path: google.maps.SymbolPath.CIRCLE,
                fillColor: '#fff',
                fillOpacity: 1,
                strokeWeight: 2,
                strokeColor: route.routeColor,
                scale: route.routeWeight,
            };

            const currentIcon = gantry.marker.getIcon();


            if (!this.iconsAreEqual(currentIcon, desiredIcon)) {
                gantry.marker.setIcon(desiredIcon);
            }
        }


        if (!gantry.marker.getVisible()) {
            gantry.marker.setVisible(true);
        }
    }

    private hideGantryMarker(gantry: CoverageGantry) {
        if (gantry.marker.getVisible()) {
            gantry.marker.setVisible(false);
        }
    }

    private iconsAreEqual(icon1, icon2): boolean {
        return JSON.stringify(icon1) === JSON.stringify(icon2);
    }


    fitMapBounds(bounds: null | google.maps.LatLngBounds | google.maps.LatLngBoundsLiteral) {
        if (!bounds) {
            return;
        }

        if (this.viewportBreakpoint === 'desktop') {
            this.googleMap.fitBounds(bounds, {
                top: 0,
                left: 20 + 360,
                bottom: 0,
                right: 0
            });
        } else {
            this.googleMap.fitBounds(bounds);
        }
    }

    getRouteBounds(route: CoverageRoute): null | google.maps.LatLngBounds {
        const path = route.routePolyline.getPath().getArray();

        if (!path.length) {
            return null;
        }

        const bounds = new google.maps.LatLngBounds();

        path.forEach(point => bounds.extend(point));

        return bounds;
    }

    setLicensePlateCoverage(id: string) {
        this.setSelectedLicensePlate(id);
        this.getLicensePlateCoverage(id);
    }

    private setSelectedLicensePlate(id: string) {
        this.selectedLicensePlate = this.listOfLicensePlates.find(item => item.id === id) || null;
    }
}
