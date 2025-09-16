import {
    AfterViewInit,
    Component, EventEmitter, HostListener, Input,
    OnDestroy, OnInit, Output, Renderer2, ViewChild,
    ViewEncapsulation
} from '@angular/core';
import {ActivatedRoute, CanDeactivate, Router} from '@angular/router';
import {TitleService} from '../../../services/title.service';
import {forkJoin, Observable, of, Subscription, zip} from 'rxjs';
import {LangService} from '../../../services/lang.service';
import {UserData, UserService} from '../../../services/user.service';
import {UiService} from '../../../services/ui.service';
import {PopupService} from '../../../services/popup.service';
import {FormBuilder} from '@angular/forms';
import {DeviceService, ViewportBreakpoint} from '../../../services/device.service';
import {Plan, PlanPromo, PlansService} from '../../../services/plans.service';
import {SubscriptionService} from '../../../services/subscription.service';
import {DomService} from '../../../services/dom.service';
import {PopupComponent} from '../../../widgets/popup/popup.component';
import {defer} from '../../../lib/utils';
import {FundingSourceComponent} from '../../../widgets/funding-source/funding-source.component';

type State = 'loading' | 'error' | 'ready';

@Component({
    selector: 'plan',
    templateUrl: './plan.component.html',
    styleUrls: [ './plan.component.scss' ],
    encapsulation: ViewEncapsulation.None,
    host: {
        'class': 'plan',
    }
})
export class PlanComponent implements OnInit, AfterViewInit, OnDestroy, CanDeactivate<boolean | Promise<boolean>> {
    public subs : Subscription[] = [];

    public viewportBreakpoint : ViewportBreakpoint;

    @Output()
    public onSubscribed : EventEmitter<any> = new EventEmitter<any>();

    @Input()
    public isStandalone : boolean = true;

    @ViewChild('fundingSource')
    public fundingSource : FundingSourceComponent;

    @ViewChild('paymentsPopup')
    public paymentsPopup : PopupComponent;

    public state : State = 'loading';

    public isSubscribed : boolean = false;

    public plans : PlanPromo[];

    public activePlan : PlanPromo;

    public featureHint : any = null;

    public pricePerUser : number;

    public usersNumber : number;

    public isFundingSourcePopupVisible : boolean = false;

    public isSubmitting : boolean = false;

    public usersBounds = {
        min: 3,
        max: 15
    };

    public usersOptions : any[] = [];

    public features : any[] = [
        {
            name: "subs.plans.unlimited_oap",
            BASIC: true,
            PREMIER: true,
            hint: null
        },
        {
            name: "subs.plans.storage",
            BASIC: "subs.plans.storage_BASIC",
            PREMIER: "subs.plans.storage_PREMIER",
            hint: null
        },
        {
            name: "subs.plans.currencies",
            BASIC: true,
            PREMIER: true,
            hint: null
        },
        {
            name: "subs.plans.customer_profiles",
            BASIC: "subs.plans.customer_profiles_BASIC",
            PREMIER: "subs.plans.customer_profiles_PREMIER",
            hint: null
        },
        {
            name: "subs.plans.translator_profiles",
            BASIC: "subs.plans.translator_profiles_BASIC",
            PREMIER: "subs.plans.translator_profiles_PREMIER",
            hint: null
        },
        {
            name: "subs.plans.reports",
            BASIC: true,
            PREMIER: true,
            hint: null
        },
        {
            name: "subs.plans.max_users",
            BASIC: "subs.plans.max_users_BASIC",
            PREMIER: "subs.plans.max_users_PREMIER",
            hint: null
        },
        {
            name: "subs.plans.mailboxes",
            BASIC: "subs.plans.mailboxes_BASIC",
            PREMIER: "subs.plans.mailboxes_PREMIER",
            hint: null
        },
        {
            name: "subs.plans.fee",
            BASIC: "subs.plans.fee_BASIC",
            PREMIER: "subs.plans.fee_PREMIER",
            hint: "subs.plans.fee_hint"
        },
        {
            name: "subs.plans.sofort",
            BASIC: false,
            PREMIER: true,
            hint: null
        }
    ];

    public featuresSeparate : any[] = [
        {
            BASIC: [ 'yes', 'subs.plans.separate.unlimited_oap', null ],
            PREMIER: [ 'yes', 'subs.plans.separate.unlimited_oap', null ],
        },
        {
            BASIC: [ 'yes', 'subs.plans.separate.unlimited_storage', null ],
            PREMIER: [ 'yes', 'subs.plans.separate.unlimited_storage', null ],
        },
        {
            BASIC: [ 'yes', 'subs.plans.separate.multiple_currencies', null ],
            PREMIER: [ 'yes', 'subs.plans.separate.multiple_currencies', null ],
        },
        {
            BASIC: [ 'yes', 'subs.plans.separate.customer_profiles_BASIC', null ],
            PREMIER: [ 'yes', 'subs.plans.separate.customer_profiles_PREMIER', null ],
        },
        {
            BASIC: [ 'yes', 'subs.plans.separate.translator_profiles_BASIC', null ],
            PREMIER: [ 'yes', 'subs.plans.separate.translator_profiles_PREMIER', null ],
        },
        {
            BASIC: [ 'yes', 'subs.plans.separate.reports', null ],
            PREMIER: [ 'yes', 'subs.plans.separate.reports', null ],
        },
        {
            BASIC: [ 'limited', 'subs.plans.separate.max_users_BASIC', null ],
            PREMIER: [ 'yes', 'subs.plans.separate.max_users_PREMIER', null ],
        },
        {
            BASIC: [ 'limited', 'subs.plans.separate.mailboxes_BASIC', null ],
            PREMIER: [ 'yes', 'subs.plans.separate.mailboxes_PREMIER', null ],
        },
        {
            BASIC: [ 'limited', 'subs.plans.separate.fee_BASIC', 'subs.plans.fee_hint' ],
            PREMIER: [ 'yes', 'subs.plans.separate.fee_PREMIER', null ],
        },
        {
            BASIC: [ 'no', 'subs.plans.separate.sofort_BASIC', null ],
            PREMIER: [ 'yes', 'subs.plans.separate.sofort_PREMIER', null ],
        }
    ];

    public constructor (
        private renderer : Renderer2,
        private router : Router,
        private route : ActivatedRoute,
        private formBuilder : FormBuilder,
        private titleService : TitleService,
        private domService : DomService,
        private langService : LangService,
        private userService : UserService,
        private uiService : UiService,
        private deviceService : DeviceService,
        private popupService : PopupService,
        private subscriptionService : SubscriptionService,
        private plansService : PlansService,
    ) {
        if (this.isStandalone) {
            this.titleService.setTitle('subs.plans.page_title');
        }

        this.usersNumber = this.usersBounds.min;

        for (let i = this.usersBounds.min; i <= this.usersBounds.max; i++) {
            this.usersOptions.push(i);
        }

        this.viewportBreakpoint = this.deviceService.viewportBreakpoint;
        this.addSub(this.deviceService.onResize.subscribe((message) => {
            if (message.breakpointChange) {
                this.viewportBreakpoint = message.breakpointChange.current;
            }
        }));

        this.addSub(zip(
            this.subscriptionService.fetchSubscription(),
            this.plansService.fetchPlans(),
        ).subscribe(
            ([ subscription, plans ]) => {
                if (!plans.length && this.isStandalone) {
                    this.isSubscribed = true;
                    this.router.navigateByUrl('/dashboard');
                    return;
                }

                this.plans = plans;
                this.isSubscribed = Boolean(subscription && subscription.plan && subscription.plan.name);

                this.state = 'ready';
            },
            () => this.state = 'error'
        ));
    }

    public ngOnInit () : void {

    }

    public ngAfterViewInit () : void {
        window.scrollTo(0, 0);
    }

    public ngOnDestroy () : void {
        this.subs.forEach(sub => sub.unsubscribe());
    }

    public canDeactivate () : Promise<boolean> {
        return new Promise<boolean>((resolve) => {
            resolve(!this.isStandalone || this.isSubscribed || !this.userService.isSignedIn);
        });
    }

    public addSub (sub : Subscription) : void {
        this.subs = [ ...this.subs, sub ];
    }

    @HostListener('document:click', [ '$event' ])
    public onDocumentClick (e : any) : void {
        if (!this.domService.hasEventMark(e, 'featureHintButtonClick') && this.deviceService.device.touch) {
            this.featureHint = null;
        }
    }

    public toggleHint (e : any, feature : any = null) : void {
        if (this.deviceService.device.touch) {
            if (e.type === 'click') {
                this.featureHint = this.featureHint === feature ? null : feature;
                this.domService.markEvent(e, 'featureHintButtonClick');
            }
        } else {
            if (e.type === 'mouseenter') {
                this.featureHint = feature;
            } else if (e.type === 'mouseleave') {
                this.featureHint = null;
            }
        }
    }

    public onChoosePlan (plan : PlanPromo) : void {
        this.activePlan = plan;

        if (plan.price > 0) {  // not free
            this.pricePerUser = plan.price / 100;
            this.isFundingSourcePopupVisible = true;
            defer(() => this.paymentsPopup.activate());
        } else {  // free
            this.isSubmitting = true;

            this.addSub(this.subscriptionService.subscribe({
                fundingSource: null,
                plan: plan.plan,
                quantity: this.usersNumber
            }).subscribe(subscription => {
                console.warn('subscription', subscription);
                this.userService.updateFeatures().then(() => {
                    this.isSubmitting = false;
                    this.isSubscribed = true;
                    this.onSubscribed.emit();
                    if (this.isStandalone) {
                        this.router.navigateByUrl('/dashboard');
                    }
                });
            }, () => {
                this.isSubmitting = false;
            }));
        }
    }

    public onHidePaymentsPopup (byOverlay : boolean = false) : void {
        if (byOverlay) {
            return;
        }

        this.paymentsPopup.deactivate().then(() => {
            this.isFundingSourcePopupVisible = false;
        });
    }

    public onSubmitPayments () : void {
        this.isSubmitting = true;
        this.fundingSource.submitCard();
    }

    public isCardValid () : boolean {
        return !!this.fundingSource && this.fundingSource.isCardValid();
    }

    public onFundingSourceSubmitted (response : any) : void {
        if (!response.isOk) {
            this.isSubmitting = false;
            return;
        }

        this.addSub(this.subscriptionService.subscribe({
            fundingSource: response.token.id,
            plan: this.activePlan.plan,
            quantity: this.usersNumber
        }).subscribe(subscription => {
            console.warn('subscription', subscription);
            this.userService.updateFeatures().then(() => {
                this.isSubmitting = false;
                this.isSubscribed = true;
                this.onSubscribed.emit();
                if (this.isStandalone) {
                    this.router.navigateByUrl('/dashboard');
                }
            });
        }, () => {
            this.isSubmitting = false;
        }));
    }
}
