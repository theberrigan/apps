import {
    Component, ElementRef, Input,
    OnDestroy,
    OnInit, Output, Renderer2, ViewChild,
    ViewEncapsulation,
    EventEmitter
} from '@angular/core';
import {GoogleService} from '../../../services/google.service';
import {CoverageLocation} from '../../../services/coverage.service';

@Component({
    selector: 'google-map',
    exportAs: 'googleMap',
    templateUrl: './google-map.component.html',
    styleUrls: [ './google-map.component.scss' ],
    encapsulation: ViewEncapsulation.None,
    host: {
        'class': 'google-map'
    }
})
export class GoogleMapComponent implements OnInit, OnDestroy {
    @Input()
    data : CoverageLocation;

    @ViewChild('map')
    mapEl : ElementRef;

    map : google.maps.Map;

    title : string;

    @Output()
    onClose = new EventEmitter();

    constructor (
        private hostEl : ElementRef,
        private renderer : Renderer2,
        private googleService : GoogleService,
    ) {}

    async ngOnInit () {
        this.renderer.addClass(document.body, 'google-map-active');

        if (this.data) {
            const { route, gantry } = this.data;

            this.title = gantry.fullName;

            const isMapLoaded = await this.initMap(gantry.position);

            if (isMapLoaded) {
                new google.maps.Polyline({
                    map: this.map,
                    path: route.routePath,
                    editable: false,
                    draggable: false,
                    strokeColor: route.routeColor,
                    strokeOpacity: route.routeOpacity,
                    strokeWeight: route.routeWeight,
                });

                new google.maps.Marker({
                    position: gantry.position,
                    title: gantry.fullName,
                    map: this.map,
                    draggable: false,
                    clickable: false,
                });
            }
        }
    }

    ngOnDestroy () {
        this.renderer.removeClass(document.body, 'google-map-active');
    }

    async initMap (mapCenter : google.maps.LatLngLiteral) : Promise<boolean> {
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
            center: mapCenter,
            zoom: 12,
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

    onCloseClick () {
        this.onClose.emit();
    }
}
