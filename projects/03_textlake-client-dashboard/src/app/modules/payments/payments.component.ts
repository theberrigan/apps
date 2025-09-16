import {
    AfterViewChecked,
    AfterViewInit,
    ChangeDetectorRef,
    Component,
    ElementRef,
    HostListener,
    OnDestroy,
    OnInit,
    Renderer2,
    ViewChild, ViewEncapsulation
} from '@angular/core';
import { animate, state, style, transition, trigger } from '@angular/animations';
import { Subscription} from 'rxjs';
import { TranslateService } from '@ngx-translate/core';
import {ActivatedRoute, Router} from '@angular/router';
import { PaymentsService } from '../../services/payments.service';
import { QuoteService } from '../../services/quote.service';
import { CyPipe } from '../../pipes/cy.pipe';
import { CONFIG } from '../../../../config/app/dev';
import {UserService} from '../../services/user.service';
import {defer} from '../../lib/utils';
import {DeviceService, ViewportBreakpoint} from '../../services/device.service';

// http://localhost:9557/payments/W8WYKW
// http://localhost:9557/payments/9CQ3MF

@Component({
    templateUrl: './payments.component.html',
    encapsulation: ViewEncapsulation.None,
    animations: [
        trigger('showWindow', [
            state('false', style({ opacity: 0 })),
            state('true', style({ opacity: 1 })),
            transition('false => true', animate('0.4s ease-out'))
        ]),
        trigger('showPanel', [
            state('false', style({ transform: 'translateY(-100%)' })),
            state('true', style({ transform: 'translateY(0%)' })),
            transition('false => true', animate('0.4s ease-out'))
        ]),
        trigger('expandService', [
            state('false', style({ height: '0px' })),
            state('true', style({ height: '*' })),
            transition('false => true', animate('0.15s ease-out'))
        ])
    ]
})
export class PaymentsComponent implements OnInit, OnDestroy, AfterViewInit, AfterViewChecked {
    public isReady : boolean = false;

    public isLangSwitcherActive : boolean = false;

    public currentLang : string = 'en';

    public langs : any[] = [
        {
            locale: 'en',
            name: 'English'
        },
        {
            locale: 'ru',
            name: 'Russian'
        },
        {
            locale: 'pl',
            name: 'Polish'
        },
        {
            locale: 'es',
            name: 'Spanish'
        },
        {
            locale: 'uk',
            name: 'Ukrainian'
        },
    ];

    public quoteId : string = null;

    public quote : any = null;

    public paymentMethods : any = {};

    // @ViewChild('totalDueEl')
    // public totalDueEl : ElementRef;

    @ViewChild('sectionPayContent')
    public sectionPayContent : ElementRef;

    public sectionPayWidth : number = null;

    public sectionPayContentTop : number = null;

    @ViewChild('paymentWindow')
    public paymentWindow : ElementRef;

    public totalDue : string = '0';

    public totalDuePartial : number = 0;

    public totalDueCurrency : string = '';

    public isTotalDueScaled : boolean = false;

    public serviceExpanded : any = null;

    public subscriptions : Subscription[] = [];

    public breakpoint : number = 0;

    public viewportBreakpoint : ViewportBreakpoint;

    public paymentState : 'ready' | 'paid' | 'processing' | 'popup' | 'unavailable' = null;

    public constructor (
        private renderer : Renderer2,
        private route : ActivatedRoute,
        private router : Router,
        private translate : TranslateService,
        private paymentsService : PaymentsService,
        private quoteService : QuoteService,
        private currencyPipe : CyPipe,
        private deviceService : DeviceService,
        private userService : UserService
    ) {
        this.viewportBreakpoint = this.deviceService.viewportBreakpoint;
    }

    public ngAfterViewInit () {
        defer(() => {
            this.currentLang = this.userService.getUserData().local.language;
            this.quoteId = this.route.snapshot.params['quoteId'];

            Promise.all([
                this.paymentsService.getPaymentMethods(this.quoteId),
                this.quoteService.getQuoteSummary(this.quoteId)
            ])
            .then((responses : any[]) => {
                [ this.paymentMethods, this.quote ] = responses;

                if (this.quote) {
                    // this.quote.quote.fullPaymentRequired = true;

                    this.subscriptions.push(
                        this.deviceService.onResize.subscribe(message => {
                            if (message.breakpointChange) {
                                this.viewportBreakpoint = this.deviceService.viewportBreakpoint;
                                this.redraw();
                            }
                        })
                    );

                    // this.quote.quote.totalDue = 12345;

                    this.setPaymentsState(
                        !Object.keys(this.paymentMethods).some((k) => this.paymentMethods[k]) ? 'unavailable' :
                        this.quote.quote.totalDue <= 0 ? 'paid' : 'ready'
                    );

                    this.totalDuePartial = this.quote.quote.totalDue / 100;
                    this.totalDue = this.totalDuePartial.toFixed(2);

                    this.totalDueCurrency = ({
                        'USD': '$',
                        'EUR': '€',
                        'GBP': '£',
                        'JPY': '¥',
                        'PLN': 'zł',
                        'RUB': '₽'
                    })[ this.quote.quote.currency.toUpperCase() ] || this.quote.quote.currency.toUpperCase();

                    // this.quote.quote.items.forEach((item : any) => {
                    //     item.fromLanguage = 'POL';
                    //     item.toLanguage = 'RUS';
                    // });

                    // quote.email
                    // quote.phone
                    // quote.fax
                }

                requestAnimationFrame(() => {
                    this.isReady = true;
                });

                console.log(this.quote);
            });
        });
    }

    public ngAfterViewChecked () : void {
        this.redraw();
    }

    public ngOnInit () : void {
        requestAnimationFrame(() => this.redraw());
    }

    public ngOnDestroy () : void {
        this.subscriptions.forEach((e) => e.unsubscribe());
    }

    @HostListener('window:scroll')
    @HostListener('window:resize')
    public redraw () : void {
        if (!this.quote) {
            return;
        }

        requestAnimationFrame(() => {
            if (this.viewportBreakpoint === 'desktop' && this.sectionPayContent && this.paymentWindow) {
                const
                    pwRect : any = this.paymentWindow.nativeElement.getBoundingClientRect(),
                    spRect : any  = this.sectionPayContent.nativeElement.getBoundingClientRect(),
                    bottomBound : number = Math.min(window.innerHeight, pwRect.bottom);

                let top : number = Math.max(0, pwRect.top) + (pwRect.height - spRect.height) / 2;

                this.sectionPayWidth = Math.ceil(spRect.width);
                this.sectionPayContentTop = Math.ceil(Math.max(pwRect.top, top + spRect.height > bottomBound ? (top - Math.abs(top + spRect.height - bottomBound)) : top));
            } else {
                this.sectionPayWidth = null;
                this.sectionPayContentTop = null;
            }
        });
    }

    public onPartialAmountChanged (e : any) : void {
        const
            max : number = this.quote.quote.totalDue / 100,
            value : number = Number(e.target.value.replace(/,/g, '.').replace(/[\r\s\n\t]+/g, ''));

        this.totalDuePartial = Math.floor((Number.isFinite(value) && value > 0 && value <= max && value || max) * 100) / 100;
        e.target.value = this.totalDuePartial;  // change detector fix
    }

    public pay (provider : string) : void {
        this.setPaymentsState('processing');

        switch (provider) {
            case 'sofort':
                this.paymentsService
                    .paySofort(this.quoteId, this.totalDuePartial * 100)
                    .then((response : any) => {
                        if (!response) {
                            this.setPaymentsState('ready');
                            alert('Something went wrong.');
                            return;
                        }

                        if (response.redirectURL) {
                            window.location.href = response.redirectURL;
                        }
                    });
                break;
            case 'stripe':
                this.showStripeWidget();
                break;
            case 'paypal':
                alert(`'${ provider }' is not implemented`);
                break;
            default:
                alert(`Unknown payment provider '${ provider }'`);
        }
    }

    public getLanguage (langCode : string) : string {
        const
            key : string = `langs.${ langCode.toLowerCase() }`,
            lang : string = this.translate.instant(key);

        return key != lang ? lang : langCode;
    }

    public markLangSwitcherEvent (event : any) {
        event.isLangSwitcherEvent = true;
    }

    public setPaymentsState (state : 'ready' | 'paid' | 'processing' | 'popup' | 'unavailable') : void {
        this.paymentState = state;
        requestAnimationFrame(() => this.redraw());
    }

    public toggleLangSwitcher () {
        this.isLangSwitcherActive = !this.isLangSwitcherActive;
    }

    @HostListener('click', [ '$event.isLangSwitcherEvent' ])
    public onComponentClick (isLangSwitcherEvent : boolean = false) {
        !isLangSwitcherEvent && (this.isLangSwitcherActive = false);
    }

    public onLangSwitch (lang : any) {
        this.currentLang = lang.locale;
        const userData = this.userService.getUserData();
        userData.local.language = this.currentLang;
        this.userService.updateUserData(userData);
        // window.localStorage.setItem('userLang', this.currentLang);
        // this.translate.use(this.currentLang);
        this.isLangSwitcherActive = false;
    }

    public expandService (service : any) : void {
        this.serviceExpanded = service != this.serviceExpanded ? service : null;
    }

    public showStripeWidget () : void {
        new Promise((resolve) => {
            if ('StripeCheckout' in window) {
                resolve((<any>window).StripeCheckout);
                return;
            }

            const script : any = document.createElement('script');
            script.addEventListener('load', () => resolve((<any>window).StripeCheckout));
            script.src = 'https://checkout.stripe.com/checkout.js';
            document.head.appendChild(script);
        }).then((StripeCheckout : any) => {
            let isTokenCreated : boolean = false;

            const amount : number = Number((this.totalDuePartial * 100).toPrecision(15));

            this.translate
                .get('payments.pay_with_card')
                .subscribe((name : string) => {
                    StripeCheckout.configure({
                        key: CONFIG.payments.stripe.apiKey,
                        name,
                        // description: `Offer: ${ this.quote.quote.name }`,
                        locale: (() => {
                            const langs : string[] = [ 'zh', 'da', 'nl', 'en', 'fi', 'fr', 'de', 'it', 'ja', 'no', 'es', 'sv' ];
                            return ~langs.indexOf(this.currentLang) ? this.currentLang : 'auto';
                        })(),
                        token: (token) => {
                            isTokenCreated = true;
                            console.warn('Token', token);

                            this.paymentsService
                                .saveStripeToken(this.quoteId, token.id, amount)
                                .then((isOk : boolean) => {
                                    this.router.navigate([
                                        isOk ?
                                        '/payments/result/success' :
                                        '/payments/result/failed'
                                    ]);
                                });
                        },
                        opened: () => {
                            this.setPaymentsState('popup');
                        },
                        closed: () => {
                            this.setPaymentsState(isTokenCreated ? 'processing' : 'ready');
                        }
                    }).open({
                        amount,
                        currency: this.quote.quote.currency
                    });
                });
        });
    }
}
