import {
    AfterViewInit,
    Component, OnDestroy,
    OnInit,
    ViewEncapsulation
} from '@angular/core';
import {ActivatedRoute, Router} from '@angular/router';
import { Location } from '@angular/common';
import {Subscription} from 'rxjs';
import {TitleService} from '../../../services/title.service';
import {DeviceService, ViewportBreakpoint} from '../../../services/device.service';
import {PopupService} from '../../../services/popup.service';
import {Pagination} from '../../../widgets/pagination/pagination.component';

const _ORDERS = {
    "totalPages": 26,
    "totalElements": 257,
    "number": 0,
    "size": 10,
    "offers": [
        {
            "offerId": 1,
            "statusKey": "accepted",
            "statusName": "Accepted",
            "offerKey": "2016-1",
            "client": "China National Petroleum",
            "contact": "John Smith 2",
            "phone": "******7890",
            "email": "v*****2@g***m",
            "net": 195100,
            "gross": 239973,
            "currencyKey": "PLN",
            "currencyName": "PLN - Polish Zloty",
            "coordinator": "Sergey S",
            "created": 1492402570000,
            "description": "Квантовый компьютер — вычислительное устройство, которое использует явления квантовой суперпозиции и квантовой запутанности для передачи и обработки данных. Хотя появление транзисторов, классических компьютеров и множества других электронных устройств связано с развитием квантовой механики и физики конденсированного состояния, информация между элементами таких систем передаётся в виде классических величин обычного электрического напряжения."
        },
        {
            "offerId": 2,
            "statusKey": "accepted",
            "statusName": "Accepted",
            "offerKey": "2016-2",
            "client": "test",
            "contact": "",
            "phone": "",
            "email": "voffka",
            "net": 34600,
            "gross": 42558,
            "currencyKey": "PLN",
            "currencyName": "PLN - Polish Zloty",
            "coordinator": "Sergey S",
            "created": 1492480241000,
            "description": "В повествовательном фольклоре не всегда можно провести чёткую границу между жанрами."
        },
        {
            "offerId": 5,
            "statusKey": "new",
            "statusName": "New",
            "offerKey": "2016-3",
            "client": null,
            "contact": "",
            "phone": "",
            "email": "",
            "net": 0,
            "gross": 0,
            "currencyKey": "PLN",
            "currencyName": "PLN - Polish Zloty",
            "coordinator": "Sergey S",
            "created": 1492631372000,
            "description": null
        },
        {
            "offerId": 6,
            "statusKey": "new",
            "statusName": "New",
            "offerKey": "2016-4",
            "client": "Маша и Медведи",
            "contact": "Михаил Попатыч",
            "phone": "********* 123",
            "email": "v*****5@g***m",
            "net": 37796,
            "gross": 46489,
            "currencyKey": "PLN",
            "currencyName": "PLN - Polish Zloty",
            "coordinator": "Sergey S",
            "created": 1492632412000,
            "description": "Мишки на Сервере"
        },
        {
            "offerId": 7,
            "statusKey": "accepted",
            "statusName": "Accepted",
            "offerKey": "2016-5",
            "client": "Клиент 1",
            "contact": "Александр Петрович",
            "phone": "",
            "email": "voffka",
            "net": 40500,
            "gross": 49815,
            "currencyKey": "PLN",
            "currencyName": "PLN - Polish Zloty",
            "coordinator": "Sergey S",
            "created": 1492667710000,
            "description": "description askhfdalksjdhflkj"
        },
        {
            "offerId": 10,
            "statusKey": "accepted",
            "statusName": "Accepted",
            "offerKey": "2016-6",
            "client": "Client1",
            "contact": "Smitherson",
            "phone": "******3123",
            "email": "v*****1@g***m",
            "net": 10500,
            "gross": 12915,
            "currencyKey": "PLN",
            "currencyName": "PLN - Polish Zloty",
            "coordinator": "Sergey S",
            "created": 1492732679000,
            "description": "This is a test data"
        },
        {
            "offerId": 12,
            "statusKey": "accepted",
            "statusName": "Accepted",
            "offerKey": "2016-7",
            "client": "tedt",
            "contact": "john",
            "phone": "",
            "email": "",
            "net": 26500,
            "gross": 32595,
            "currencyKey": "PLN",
            "currencyName": "PLN - Polish Zloty",
            "coordinator": "Sergey S",
            "created": 1493749176000,
            "description": null
        },
        {
            "offerId": 13,
            "statusKey": "accepted",
            "statusName": "Accepted",
            "offerKey": "2016-8",
            "client": "empty",
            "contact": "",
            "phone": "",
            "email": "",
            "net": 0,
            "gross": 0,
            "currencyKey": "PLN",
            "currencyName": "PLN - Polish Zloty",
            "coordinator": "Sergey S",
            "created": 1493937587000,
            "description": null
        },
        {
            "offerId": 14,
            "statusKey": "accepted",
            "statusName": "Accepted",
            "offerKey": "2016-9",
            "client": "Company 1",
            "contact": "John",
            "phone": "",
            "email": "voffka",
            "net": 383,
            "gross": 471,
            "currencyKey": "USD",
            "currencyName": "USD - United States Dollar",
            "coordinator": "Sergey S",
            "created": 1494014824000,
            "description": null
        },
        {
            "offerId": 15,
            "statusKey": "accepted",
            "statusName": "Accepted",
            "offerKey": "2016-10",
            "client": "China National Petroleum",
            "contact": "John Smith 2",
            "phone": "******7890",
            "email": "v*****2@g***m",
            "net": 0,
            "gross": 0,
            "currencyKey": "EUR",
            "currencyName": "EUR - Euro",
            "coordinator": "Sergey S",
            "created": 1494118061000,
            "description": null
        }
    ],
    "first": true,
    "next": true,
    "last": false,
    "previous": false
};

@Component({
    selector: 'orders',
    exportAs: 'orders',
    templateUrl: './orders.component.html',
    styleUrls: [ './orders.component.scss' ],
    encapsulation: ViewEncapsulation.None,
    host: {
        'class': 'orders',
    }
})
export class OrdersComponent implements OnInit, OnDestroy, AfterViewInit {
    public viewportBreakpoint : ViewportBreakpoint;

    public subs : Subscription[] = [];

    public listeners : any[] = [];

    public sortOptions = [
        {
            display: 'Order ID',
            value: 'id'
        }
    ];

    public sizeOptions = [ 25 ];

    public view : any = 'table';

    public orders = _ORDERS.offers;

    public pagination = _ORDERS;

    constructor (
        private router : Router,
        private route : ActivatedRoute,
        private location : Location,
        private deviceService : DeviceService,
        private popupService : PopupService,
        private titleService : TitleService
    ) {}

    public ngOnInit () : void {
        this.titleService.setTitle('orders.page_title');

        this.viewportBreakpoint = this.deviceService.viewportBreakpoint;
        this.deviceService.onResize.subscribe(message => {
            if (message.breakpointChange) {
                this.viewportBreakpoint = this.deviceService.viewportBreakpoint;
            }
        });
    }

    public ngAfterViewInit () : void {

    }

    public ngOnDestroy () : void {
        this.subs.forEach(sub => sub.unsubscribe());
        this.listeners.forEach(unlisten => unlisten());
    }

    public addListener (listener : any) : void {
        this.listeners = [ ...this.listeners, listener ];
    }

    public addSub (sub : Subscription) : void {
        this.subs = [ ...this.subs, sub ];
    }
}
