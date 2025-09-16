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
import {deleteFromArray} from '../../../lib/utils';

type Tab = 'documents' | 'details' | 'shipping' | 'services' | 'invoices' | 'transactions';
const _TRANSACTIONS = [
    {
        "transactionId": "TEST-TRANSACTION-ID1",
        "paymentProvider": "SOFORT",
        "created": 1492402570000,
        "updated": 1492402570000,
        "amount": 100,
        "fees": 5,
        "received": 95,
        "currency": "USD",
        "exchangeRate": 0,
        "status": "INITIATED",
        "comment": null
    },
    {
        "transactionId": "TEST-TRANSACTION-ID2",
        "paymentProvider": "SOFORT",
        "created": 1492402571000,
        "updated": 1492402571000,
        "amount": 200,
        "fees": 25,
        "received": 175,
        "currency": "USD",
        "exchangeRate": 0,
        "status": "RECEIVED",
        "comment": null
    },
    {
        "transactionId": "TEST-TRANSACTION-ID3",
        "paymentProvider": "SOFORT",
        "created": 1492402571000,
        "updated": 1492402571000,
        "amount": 5000,
        "fees": 100,
        "received": 4900,
        "currency": "PLN",
        "exchangeRate": 0,
        "status": "UNTRACEABLE",
        "comment": null
    },
    {
        "transactionId": "143523-318860-5910AF47-0287",
        "paymentProvider": "SOFORT",
        "created": 1494265671000,
        "updated": 1494265671000,
        "amount": 5412,
        "fees": 0,
        "received": 0,
        "currency": "PLN",
        "exchangeRate": 0,
        "status": "INITIATED",
        "comment": null
    },
    {
        "transactionId": "143523-318860-5910B0DF-4D1A",
        "paymentProvider": "SOFORT",
        "created": 1494266079000,
        "updated": 1494266079000,
        "amount": 5412,
        "fees": 0,
        "received": 0,
        "currency": "PLN",
        "exchangeRate": 0,
        "status": "INITIATED",
        "comment": null
    },
    {
        "transactionId": "d8083b95-1882-4beb-8794-b99c7414aa58",
        "paymentProvider": "CASH",
        "created": 1495234763000,
        "updated": 1495234763000,
        "amount": 100,
        "fees": 0,
        "received": 0,
        "currency": "USD",
        "exchangeRate": 0,
        "status": "RECEIVED",
        "comment": "Integration test transaction"
    },
    {
        "transactionId": "7c303f92-24ea-40bc-849b-21c41c3b05a4",
        "paymentProvider": "CASH",
        "created": 1496871108000,
        "updated": 1496871108000,
        "amount": 100,
        "fees": 0,
        "received": 0,
        "currency": "USD",
        "exchangeRate": 0,
        "status": "RECEIVED",
        "comment": "Integration test transaction"
    },
    {
        "transactionId": "745b98ea-83e8-44d2-abe4-66675ffd2801",
        "paymentProvider": "CASH",
        "created": 1496871448000,
        "updated": 1496871448000,
        "amount": 100,
        "fees": 0,
        "received": 0,
        "currency": "USD",
        "exchangeRate": 2300,
        "status": "RECEIVED",
        "comment": "Integration test transaction"
    },
    {
        "transactionId": "725e75f9-8221-4bda-b986-e850108fce3d",
        "paymentProvider": "CASH",
        "created": 1515215659000,
        "updated": 1515215659000,
        "amount": 123,
        "fees": 0,
        "received": 0,
        "currency": "EUR",
        "exchangeRate": 2300,
        "status": "RECEIVED",
        "comment": "Small comment"
    },
    {
        "transactionId": "24da478a-ecc7-41cf-b682-a2be8831165b",
        "paymentProvider": "CASH",
        "created": 1515350964000,
        "updated": 1515350964000,
        "amount": 50000,
        "fees": 0,
        "received": 0,
        "currency": "PLN",
        "exchangeRate": 10000,
        "status": "RECEIVED",
        "comment": "comm"
    },
    {
        "transactionId": "17057b3b-d8b4-464f-92b0-193b7a3a593d",
        "paymentProvider": "CASH",
        "created": 1515350984000,
        "updated": 1515350984000,
        "amount": 80000,
        "fees": 0,
        "received": 0,
        "currency": "USD",
        "exchangeRate": 3500,
        "status": "RECEIVED",
        "comment": "adad"
    },
    {
        "transactionId": "fd96e829-8487-4487-85a1-2b14ef62c589",
        "paymentProvider": "CASH",
        "created": 1515351077000,
        "updated": 1515351077000,
        "amount": 30000,
        "fees": 0,
        "received": 0,
        "currency": "USD",
        "exchangeRate": 3500,
        "status": "RECEIVED",
        "comment": "aaa"
    },
    {
        "transactionId": "1903ba9b-ee1c-4daf-92e9-b5c44550bb15",
        "paymentProvider": "CASH",
        "created": 1515351162000,
        "updated": 1515351162000,
        "amount": 566,
        "fees": 0,
        "received": 0,
        "currency": "RUB",
        "exchangeRate": 20000,
        "status": "RECEIVED",
        "comment": "Ruble is the weakest currency in the world"
    },
    {
        "transactionId": "143523-318860-587AE242-276C",
        "paymentProvider": "SOFORT",
        "created": 1515798117000,
        "updated": 1515798119000,
        "amount": 100,
        "fees": 0,
        "received": 0,
        "currency": "PLN",
        "exchangeRate": 10000,
        "status": "UNTRACEABLE",
        "comment": null
    },
    {
        "transactionId": "143523-318860-587AE242-276C",
        "paymentProvider": "SOFORT",
        "created": 1515798409000,
        "updated": 1515798409000,
        "amount": 100,
        "fees": 0,
        "received": 0,
        "currency": "PLN",
        "exchangeRate": 10000,
        "status": "INITIATED",
        "comment": null
    },
    {
        "transactionId": "143523-318860-5B706302-BE08",
        "paymentProvider": "SOFORT",
        "created": 1534092035000,
        "updated": 1534092035000,
        "amount": 12915,
        "fees": 0,
        "received": 0,
        "currency": "PLN",
        "exchangeRate": 10000,
        "status": "INITIATED",
        "comment": null
    }
];

const _INVOICES = [
    {
        "invoiceId": "in_1GkFMwARJzhi6jTRM0OUqoA1",
        "total": 7996,
        "number": "A8B634B-0035",
        "paid": false,
        "periodStart": 1587240917,
        "periodEnd": 1589832917,
        "currency": "usd",
        "date": 1589832926
    },
    {
        "invoiceId": "in_1GZN4NARJzhi6jTRwahxPSwo",
        "total": 7996,
        "number": "A8B634B-0034",
        "paid": true,
        "periodStart": 1584562517,
        "periodEnd": 1587240917,
        "currency": "usd",
        "date": 1587240919
    },
    {
        "invoiceId": "in_1GO8IPARJzhi6jTRX0ojzmqm",
        "total": 7996,
        "number": "A8B634B-0033",
        "paid": false,
        "periodStart": 1582056917,
        "periodEnd": 1584562517,
        "currency": "usd",
        "date": 1584562521
    },
    {
        "invoiceId": "in_1GDcTjARJzhi6jTRgX385NnP",
        "total": 9386,
        "number": "A8B634B-0032",
        "paid": false,
        "periodStart": 1579378517,
        "periodEnd": 1582056917,
        "currency": "usd",
        "date": 1582056935
    },
    {
        "invoiceId": "in_1G2NhRARJzhi6jTR24s41utY",
        "total": 5997,
        "number": "A8B634B-0031",
        "paid": true,
        "periodStart": 1579378517,
        "periodEnd": 1579378517,
        "currency": "usd",
        "date": 1579378517
    },
    {
        "invoiceId": "in_1G2MbRARJzhi6jTRxglGUFex",
        "total": 5997,
        "number": "A8B634B-0030",
        "paid": true,
        "periodStart": 1579374301,
        "periodEnd": 1579374301,
        "currency": "usd",
        "date": 1579374301
    },
    {
        "invoiceId": "in_1G2MawARJzhi6jTREItegWg8",
        "total": 0,
        "number": "A8B634B-0029",
        "paid": true,
        "periodStart": 1579374270,
        "periodEnd": 1579374270,
        "currency": "usd",
        "date": 1579374270
    },
    {
        "invoiceId": "in_1G2BWwARJzhi6jTR7NlVeH1L",
        "total": 5997,
        "number": "A8B634B-0028",
        "paid": true,
        "periodStart": 1579331738,
        "periodEnd": 1579331738,
        "currency": "usd",
        "date": 1579331738
    },
    {
        "invoiceId": "in_1G2BWVARJzhi6jTRAOdZbC1t",
        "total": 0,
        "number": "A8B634B-0027",
        "paid": true,
        "periodStart": 1579331711,
        "periodEnd": 1579331711,
        "currency": "usd",
        "date": 1579331711
    },
    {
        "invoiceId": "in_1G2BUyARJzhi6jTRfYyp9bnp",
        "total": 0,
        "number": "A8B634B-0026",
        "paid": false,
        "periodStart": 1579331616,
        "periodEnd": 1579331616,
        "currency": "usd",
        "date": 1579331616
    },
    {
        "invoiceId": "in_1G2B4FARJzhi6jTR0gLK9gXt",
        "total": 25987,
        "number": "A8B634B-0025",
        "paid": true,
        "periodStart": 1579329959,
        "periodEnd": 1579329959,
        "currency": "usd",
        "date": 1579329959
    },
    {
        "invoiceId": "in_1G250cARJzhi6jTRBHIlAESW",
        "total": 0,
        "number": "A8B634B-0024",
        "paid": true,
        "periodStart": 1579306670,
        "periodEnd": 1579306670,
        "currency": "usd",
        "date": 1579306670
    },
    {
        "invoiceId": "in_1G24aMARJzhi6jTRelDdQYya",
        "total": 29985,
        "number": "A8B634B-0023",
        "paid": true,
        "periodStart": 1579305042,
        "periodEnd": 1579305042,
        "currency": "usd",
        "date": 1579305042
    },
    {
        "invoiceId": "in_1G24YtARJzhi6jTRU1dXOVe3",
        "total": 0,
        "number": "A8B634B-0022",
        "paid": true,
        "periodStart": 1579304951,
        "periodEnd": 1579304951,
        "currency": "usd",
        "date": 1579304951
    },
    {
        "invoiceId": "in_1G24WFARJzhi6jTRJJpdkR7M",
        "total": 0,
        "number": "A8B634B-0021",
        "paid": true,
        "periodStart": 1579304787,
        "periodEnd": 1579304787,
        "currency": "usd",
        "date": 1579304787
    },
    {
        "invoiceId": "in_1G24V4ARJzhi6jTRoySktuFo",
        "total": 5997,
        "number": "A8B634B-0020",
        "paid": true,
        "periodStart": 1579304713,
        "periodEnd": 1579304713,
        "currency": "usd",
        "date": 1579304714
    },
    {
        "invoiceId": "in_1G1xsMARJzhi6jTRLQYZPkXN",
        "total": 0,
        "number": "A8B634B-0019",
        "paid": true,
        "periodStart": 1579279250,
        "periodEnd": 1579279250,
        "currency": "usd",
        "date": 1579279250
    },
    {
        "invoiceId": "in_1FsLBSARJzhi6jTRzajukCAv",
        "total": 16520,
        "number": "A8B634B-0018",
        "paid": true,
        "periodStart": 1574393491,
        "periodEnd": 1576985491,
        "currency": "usd",
        "date": 1576985566
    },
    {
        "invoiceId": "in_1FhSseARJzhi6jTR4bcagJYz",
        "total": 13993,
        "number": "A8B634B-0017",
        "paid": true,
        "periodStart": 1571715091,
        "periodEnd": 1574393491,
        "currency": "usd",
        "date": 1574393544
    },
    {
        "invoiceId": "in_1FWE5pARJzhi6jTR2Sbjz6FW",
        "total": 13993,
        "number": "A8B634B-0016",
        "paid": true,
        "periodStart": 1569123091,
        "periodEnd": 1571715091,
        "currency": "usd",
        "date": 1571715093
    },
    {
        "invoiceId": "in_1FLLnTARJzhi6jTRZKUUNukM",
        "total": 13993,
        "number": "A8B634B-0015",
        "paid": true,
        "periodStart": 1566444691,
        "periodEnd": 1569123091,
        "currency": "usd",
        "date": 1569123099
    },
    {
        "invoiceId": "in_1FA71UARJzhi6jTRcPFhEfKz",
        "total": 13993,
        "number": "A8B634B-0014",
        "paid": true,
        "periodStart": 1563766291,
        "periodEnd": 1566444691,
        "currency": "usd",
        "date": 1566444700
    },
    {
        "invoiceId": "in_1EysFNARJzhi6jTRB9Dl5EEs",
        "total": 13993,
        "number": "A8B634B-0013",
        "paid": true,
        "periodStart": 1561174291,
        "periodEnd": 1563766291,
        "currency": "usd",
        "date": 1563766291
    },
    {
        "invoiceId": "in_1Enzx1ARJzhi6jTR7gZ5ZviT",
        "total": 13993,
        "number": "A8B634B-0012",
        "paid": true,
        "periodStart": 1558495891,
        "periodEnd": 1561174291,
        "currency": "usd",
        "date": 1561174291
    }
];

const _ATTACHMENTS = [
    {
        "name": "22.jpg",
        "comment": "Public comment Description of the work to be done with document #1 Description of the work to be done with document #1",
        "isChecked": false,
        "to": null,
        "from": null
    },
    {
        "name": "26344_comics_transmetropolitan.jpg",
        "comment": "Public comment",
        "isChecked": false,
        "to": null,
        "from": null
    },
    {
        "name": "24129569.jpg",
        "comment": "Public comment",
        "isChecked": false,
        "to": null,
        "from": null
    },
    {
        "name": "20160913153956_1.jpg",
        "comment": "Public comment",
        "isChecked": false,
        "to": null,
        "from": null
    },
    {
        "name": "DWTD-art.jpg",
        "comment": "Public comment",
        "isChecked": false,
        "to": null,
        "from": null
    },
    {
        "name": "il_fullxfull.449031682_3mby.jpg",
        "comment": "Public comment",
        "isChecked": false,
        "to": null,
        "from": null
    },
    {
        "name": "XdTtW0SN_GI.jpg",
        "comment": "111111",
        "isChecked": false,
        "to": null,
        "from": null
    },
    {
        "name": "screenshot_file_with_a_very_long_name_(created_by_fast_stone_screen_capture).png",
        "comment": "",
        "isChecked": false,
        "to": null,
        "from": null
    },
    {
        "name": "1520886649193495984.jpg",
        "comment": "file 9",
        "isChecked": false,
        "to": null,
        "from": null
    },
    {
        "name": "Screen Shot 2018-03-08 at 8.07.33 PM.png",
        "comment": "",
        "isChecked": false,
        "to": null,
        "from": null
    },
    {
        "name": "Screen Shot 2018-03-08 at 8.34.32 PM.png",
        "comment": "",
        "isChecked": false,
        "to": null,
        "from": null
    },
    {
        "name": "Screen Shot 2018-03-08 at 8.36.10 PM.png",
        "comment": "",
        "isChecked": false,
        "to": null,
        "from": null
    },
    {
        "name": "Screen Shot 2018-03-08 at 9.03.54 PM.png",
        "comment": "",
        "isChecked": false,
        "to": null,
        "from": null
    },
    {
        "name": "Screen Shot 2018-03-08 at 8.07.33 PM.png",
        "comment": "",
        "isChecked": false,
        "to": null,
        "from": null
    },
    {
        "name": "Screen Shot 2018-03-08 at 8.34.32 PM.png",
        "comment": "",
        "isChecked": false,
        "to": null,
        "from": null
    },
    {
        "name": "Screen Shot 2018-03-08 at 8.36.10 PM.png",
        "comment": "",
        "isChecked": false,
        "to": null,
        "from": null
    },
    {
        "name": "Screen Shot 2018-03-08 at 9.03.54 PM.png",
        "comment": "",
        "isChecked": false,
        "to": null,
        "from": null
    },
    {
        "name": "Screen Shot 2018-03-08 at 8.07.33 PM.png",
        "comment": "",
        "isChecked": false,
        "to": null,
        "from": null
    },
    {
        "name": "Screen Shot 2018-03-08 at 8.34.32 PM.png",
        "comment": "",
        "isChecked": false,
        "to": null,
        "from": null
    },
    {
        "name": "Screen Shot 2018-03-08 at 8.36.10 PM.png",
        "comment": "",
        "isChecked": false,
        "to": null,
        "from": null
    },
    {
        "name": "Screen Shot 2018-03-08 at 9.03.54 PM.png",
        "comment": "",
        "isChecked": false,
        "to": null,
        "from": null
    },
    {
        "name": "Screen Shot 2018-03-08 at 8.07.33 PM.png",
        "comment": "",
        "isChecked": false,
        "to": null,
        "from": null
    },
    {
        "name": "Screen Shot 2018-03-08 at 8.34.32 PM.png",
        "comment": "",
        "isChecked": false,
        "to": null,
        "from": null
    },
    {
        "name": "Screen Shot 2018-03-08 at 8.36.10 PM.png",
        "comment": "",
        "isChecked": false,
        "to": null,
        "from": null
    },
    {
        "name": "Screen Shot 2018-03-08 at 9.03.54 PM.png",
        "comment": "",
        "isChecked": false,
        "to": null,
        "from": null
    }
];

const _SERVICES = [
    {
        "name": "Korekta tekstu (pierwsza) HIS --> PL",
        "attachments": [
            "screenshot_file_with_a_very_long_name_(created_by_fast_stone_screen_capture).png",
            "DWTD-art.jpg",
            "il_fullxfull.449031682_3mby.jpg",
            "20160913153956_1.jpg",
            "XdTtW0SN_GI.jpg",
            "24129569.jpg",
            "1520886649193495984.jpg",
            "26344_comics_transmetropolitan.jpg"
        ]
    },
    {
        "name": "Korekta tekstu (pierwsza) CZ --> PL",
        "attachments": [
            "il_fullxfull.449031682_3mby.jpg",
            "24129569.jpg",
            "20160913153956_1.jpg",
            "DWTD-art.jpg",
            "XdTtW0SN_GI.jpg",
            "1520886649193495984.jpg",
            "screenshot_file_with_a_very_long_name_(created_by_fast_stone_screen_capture).png",
            "26344_comics_transmetropolitan.jpg"
        ]
    },
    {
        "name": "Tłum. pisemne ANG --> ARAB",
        "attachments": [
            "XdTtW0SN_GI.jpg"
        ]
    },
    {
        "name": "Korekta tekstu (pierwsza) NATIVE PL --> FR",
        "attachments": [
            "1520886649193495984.jpg",
            "20160913153956_1.jpg",
            "DWTD-art.jpg",
            "il_fullxfull.449031682_3mby.jpg",
            "XdTtW0SN_GI.jpg",
            "26344_comics_transmetropolitan.jpg",
            "screenshot_file_with_a_very_long_name_(created_by_fast_stone_screen_capture).png",
            "24129569.jpg"
        ]
    },
    {
        "name": "Korekta tekstu (pierwsza) LT --> PL",
        "attachments": [
            "XdTtW0SN_GI.jpg",
            "1520886649193495984.jpg",
            "il_fullxfull.449031682_3mby.jpg",
            "24129569.jpg",
            "DWTD-art.jpg",
            "screenshot_file_with_a_very_long_name_(created_by_fast_stone_screen_capture).png",
            "20160913153956_1.jpg",
            "26344_comics_transmetropolitan.jpg"
        ]
    },
    {
        "name": "Korekta tekstu (pierwsza) AUS --> PL",
        "attachments": [
            "XdTtW0SN_GI.jpg",
            "DWTD-art.jpg",
            "1520886649193495984.jpg",
            "screenshot_file_with_a_very_long_name_(created_by_fast_stone_screen_capture).png",
            "il_fullxfull.449031682_3mby.jpg",
            "24129569.jpg",
            "26344_comics_transmetropolitan.jpg",
            "20160913153956_1.jpg"
        ]
    },
    {
        "name": "Korekta tekstu (pierwsza) NATIVE PL --> AUS",
        "attachments": [
            "screenshot_file_with_a_very_long_name_(created_by_fast_stone_screen_capture).png",
            "24129569.jpg",
            "1520886649193495984.jpg"
        ]
    },
    {
        "name": "Tłum. pisemne BY --> POL",
        "attachments": [
            "DWTD-art.jpg"
        ]
    },
    {
        "name": "Tłum. pisemne przysięgłe BY --> PL",
        "attachments": [
            "screenshot_file_with_a_very_long_name_(created_by_fast_stone_screen_capture).png",
            "il_fullxfull.449031682_3mby.jpg",
            "DWTD-art.jpg",
            "1520886649193495984.jpg",
            "20160913153956_1.jpg",
            "XdTtW0SN_GI.jpg",
            "24129569.jpg",
            "26344_comics_transmetropolitan.jpg"
        ]
    },
    {
        "name": "Tłum. pisemne ORM --> PL",
        "attachments": [
            "24129569.jpg",
            "DWTD-art.jpg",
            "screenshot_file_with_a_very_long_name_(created_by_fast_stone_screen_capture).png",
            "il_fullxfull.449031682_3mby.jpg",
            "1520886649193495984.jpg",
            "20160913153956_1.jpg",
            "XdTtW0SN_GI.jpg",
            "26344_comics_transmetropolitan.jpg"
        ]
    },
    {
        "name": "Tłum. pisemne NATIVE ORM --> PL",
        "attachments": [
            "24129569.jpg",
            "XdTtW0SN_GI.jpg",
            "screenshot_file_with_a_very_long_name_(created_by_fast_stone_screen_capture).png",
            "il_fullxfull.449031682_3mby.jpg"
        ]
    },
    {
        "name": "Tłum. pisemne przysięgłe ORM --> PL",
        "attachments": [
            "DWTD-art.jpg",
            "20160913153956_1.jpg",
            "il_fullxfull.449031682_3mby.jpg",
            "26344_comics_transmetropolitan.jpg",
            "screenshot_file_with_a_very_long_name_(created_by_fast_stone_screen_capture).png",
            "24129569.jpg",
            "XdTtW0SN_GI.jpg",
            "1520886649193495984.jpg"
        ]
    },
    {
        "name": "Poświadczenie tlumaczenia BY --> PL",
        "attachments": [
            "screenshot_file_with_a_very_long_name_(created_by_fast_stone_screen_capture).png",
            "24129569.jpg",
            "il_fullxfull.449031682_3mby.jpg",
            "XdTtW0SN_GI.jpg",
            "DWTD-art.jpg",
            "20160913153956_1.jpg",
            "26344_comics_transmetropolitan.jpg",
            "1520886649193495984.jpg"
        ]
    },
    {
        "name": "Poświadczenie tlumaczenia ORM --> PL",
        "attachments": [
            "1520886649193495984.jpg",
            "20160913153956_1.jpg",
            "24129569.jpg",
            "il_fullxfull.449031682_3mby.jpg",
            "26344_comics_transmetropolitan.jpg",
            "XdTtW0SN_GI.jpg",
            "DWTD-art.jpg",
            "screenshot_file_with_a_very_long_name_(created_by_fast_stone_screen_capture).png"
        ]
    }
];

@Component({
    selector: 'order',
    exportAs: 'order',
    templateUrl: './order.component.html',
    styleUrls: [ './order.component.scss' ],
    encapsulation: ViewEncapsulation.None,
    host: {
        'class': 'order',
    }
})
export class OrderComponent implements OnInit, OnDestroy, AfterViewInit {
    public viewportBreakpoint : ViewportBreakpoint;

    public subs : Subscription[] = [];

    public listeners : any[] = [];

    public tab : Tab = 'documents';

    public transactions = _TRANSACTIONS;

    public invoices = _INVOICES;

    public attachments = _ATTACHMENTS;

    public langOptions = [
        {
            display: '',
            value: null
        },
        {
            display: 'English',
            value: 'en'
        },
        {
            display: 'Russian',
            value: 'ru'
        },
        {
            display: 'Polish',
            value: 'pl'
        },
        {
            display: 'Spanish',
            value: 'es'
        },
    ];

    public isCheckedAll : boolean = false;

    public langs = {
        from: null,
        to: null
    };

    public services = _SERVICES;

    constructor (
        private router : Router,
        private route : ActivatedRoute,
        private location : Location,
        private deviceService : DeviceService,
        private popupService : PopupService,
        private titleService : TitleService
    ) {}

    public ngOnInit () : void {
        this.titleService.setTitle('orders.editor.page_title');

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

    public addSub (sub : Subscription) : void {
        this.subs = [ ...this.subs, sub ];
    }

    public addListener (listener : any) : void {
        this.listeners = [ ...this.listeners, listener ];
    }

    public switchTab (tab : Tab) : void {
        this.tab = tab;
    }

    public onPay (invoice : any) : void {
        this.popupService.alert({
            message: 'Make requests and show payment popup'
        });
    }

    public onCheckAll () : void {
        this.attachments.forEach(a => a.isChecked = this.isCheckedAll);
    }

    public onCheckOne () : void {
        this.isCheckedAll = this.attachments.every(a => a.isChecked);
    }

    public onChangeLangAll (key : string, value : any) : void {
        this.attachments.forEach(a => {
            if (a.isChecked) {
                a[key] = value;
            }
        });

        this.attachments = [ ...this.attachments ];
        console.log(this.attachments);
    }

    public onDeleteDocument (attachment) : void {
        deleteFromArray(this.attachments, attachment);
        this.onCheckOne();
    }

    public onDownload (service) : void {
        this.popupService.alert({
            message: 'Download request'
        });
    }

    public onReclamation (service) : void {
        this.popupService.alert({
            message: 'Show reclamation popup'
        });
    }

    public onChangeLang (attachment) : void {
        attachment.isChecked = false;
        this.onCheckOne();
    }
}
