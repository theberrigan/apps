import {
    AfterViewInit,
    Component, ElementRef, EventEmitter,
    OnDestroy, Output, Renderer2, ViewChild,
    ViewEncapsulation
} from '@angular/core';
import {ActivatedRoute, Router} from '@angular/router';
import {Subscription} from 'rxjs';
import {DeviceService, ViewportBreakpoint} from '../../services/device.service';
import {UserService} from '../../services/user.service';
import {UiService} from '../../services/ui.service';
import {LangService} from '../../services/lang.service';
import {DomService} from '../../services/dom.service';
import {FormBuilder} from '@angular/forms';
import {PopupService} from '../../services/popup.service';
import {SubscriptionService} from '../../services/subscription.service';
import {PlansService} from '../../services/plans.service';
import {StripeService} from '../../services/stripe.service';
import {defer} from '../../lib/utils';

@Component({
    selector: 'funding-source',
    templateUrl: './funding-source.component.html',
    styleUrls: [ './funding-source.component.scss' ],
    encapsulation: ViewEncapsulation.None,
    host: {
        'class': 'funding-source',
    }
})
export class FundingSourceComponent implements AfterViewInit, OnDestroy {
    public subs : Subscription[] = [];

    public viewportBreakpoint : ViewportBreakpoint;

    public stripe : any = null;

    public stripeElements : any = null;

    @Output()
    public onResult : EventEmitter<any> = new EventEmitter<any>();

    public isSubmitting : boolean = false;

    public stripeInputStyle : any = {
        base: {
            iconColor: '#59606b',
            color: '#59606b',
            fontWeight: '500',
            fontFamily: '"Roboto", "Helvetica Neue", Helvetica, sans-serif',
            fontSize: '14px',
            '::placeholder': {
                color: '#99A0AA'
            }
        }
    };

    @ViewChild('cardNumberNest')
    public cardNumberNest : ElementRef = null;

    @ViewChild('cardExpireNest')
    public cardExpireNest : ElementRef = null;

    @ViewChild('cardCVCNest')
    public cardCVCNest : ElementRef = null;

    public cardNumber : any = null;

    public cardNumberState : any = null;

    public cardExpire : any = null;

    public cardExpireState : any = null;

    public cardCVC : any = null;

    public cardCVCState : any = null;

    public cardForm = {
        cardholder: '',
        zip: ''
    };

    public cardErrorMessage : string = null;

    public isCardSubmitted : boolean = false;

    public hasCardNumberFocus : boolean = false;

    public hasCardExpireFocus : boolean = false;

    public hasCardCVCFocus : boolean = false;

    public constructor (
        private renderer : Renderer2,
        private router : Router,
        private route : ActivatedRoute,
        private formBuilder : FormBuilder,
        private domService : DomService,
        private langService : LangService,
        private userService : UserService,
        private uiService : UiService,
        private deviceService : DeviceService,
        private popupService : PopupService,
        private subscriptionService : SubscriptionService,
        private plansService : PlansService,
        private stripeService : StripeService,
    ) {
        this.viewportBreakpoint = this.deviceService.viewportBreakpoint;
        this.addSub(this.deviceService.onResize.subscribe((message) => {
            if (message.breakpointChange) {
                this.viewportBreakpoint = message.breakpointChange.current;
            }
        }));
    }

    public ngAfterViewInit () : void {
        this.stripeService.getInstance().then((stripe : any) => {
            this.stripe = stripe;

            this.stripeElements = stripe.elements({
                locale: this.stripeService.getLocale()
            });

            defer(() => this.initCard());
        });
    }

    public ngOnDestroy () : void {
        this.subs.forEach(sub => sub.unsubscribe());
    }

    public addSub (sub : Subscription) : void {
        this.subs = [ ...this.subs, sub ];
    }

    public initCard () : void {
        Promise.all([
            new Promise((resolve) => {
                this.cardNumber = this.stripeElements.create('cardNumber', { style: this.stripeInputStyle });
                this.cardNumber.on('change', (event : any) => this.cardNumberState = event);
                this.cardNumber.on('ready', () => resolve());
                this.cardNumber.on('focus', () => this.hasCardNumberFocus = true);
                this.cardNumber.on('blur', () => this.hasCardNumberFocus = false);
                this.cardNumber.mount(this.cardNumberNest.nativeElement);
            }),
            new Promise((resolve) => {
                this.cardExpire = this.stripeElements.create('cardExpiry', { style: this.stripeInputStyle });
                this.cardExpire.on('change', (event : any) => this.cardExpireState = event);
                this.cardExpire.on('ready', () => resolve());
                this.cardExpire.on('focus', () => this.hasCardExpireFocus = true);
                this.cardExpire.on('blur', () => this.hasCardExpireFocus = false);
                this.cardExpire.mount(this.cardExpireNest.nativeElement);

            }),
            new Promise((resolve) => {
                this.cardCVC = this.stripeElements.create('cardCvc', { style: this.stripeInputStyle });
                this.cardCVC.on('change', (event : any) => this.cardCVCState = event);
                this.cardCVC.on('ready', () => resolve());
                this.cardCVC.on('focus', () => this.hasCardCVCFocus = true);
                this.cardCVC.on('blur', () => this.hasCardCVCFocus = false);
                this.cardCVC.mount(this.cardCVCNest.nativeElement);
            })
        ]).then(() => this.resetCard());
    }

    public resetCard () : void {
        this.cardForm = {
            cardholder: '',
            zip: ''
        };

        this.cardNumber.clear();
        this.cardExpire.clear();
        this.cardCVC.clear();

        this.isCardSubmitted = false;
    }

    public submitCard () : void {
        if (this.isSubmitting || !this.isCardValid()) {
            return;
        }

        this.isSubmitting = true;
        this.cardErrorMessage = null;

        this.stripe.createToken(this.cardNumber, {
            name: (this.cardForm.cardholder = this.cardForm.cardholder.trim()),
            address_zip: (this.cardForm.zip = this.cardForm.zip.trim())
        }).then((response : any) => {
            if (response.token) {
                // this.resetCard();

                this.onResult.emit({
                    isOk: true,
                    token: response.token
                });
            } else if (response.error) {
                this.cardErrorMessage = response.error.message || response.error;

                this.onResult.emit({
                    isOk: false
                });
            }

            this.isSubmitting = false;
        });
    }

    public isCardValid () : boolean {
        return !!(
            this.cardForm.cardholder.trim() &&
            (
                !this.cardForm.zip.trim() ||
                /^\d+(-\d+)?$/.test(this.cardForm.zip.trim())
            ) &&
            this.cardNumberState &&
            !this.cardNumberState.error &&
            this.cardNumberState.complete &&
            this.cardExpireState &&
            !this.cardExpireState.error &&
            this.cardExpireState.complete &&
            this.cardCVCState &&
            !this.cardCVCState.error &&
            this.cardCVCState.complete
        );
    }
}
