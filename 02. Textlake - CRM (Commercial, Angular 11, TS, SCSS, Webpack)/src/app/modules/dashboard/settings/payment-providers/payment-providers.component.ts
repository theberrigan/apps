import {Component, OnDestroy, ViewChild, ViewEncapsulation} from '@angular/core';
import {ActivatedRoute, CanDeactivate, Router} from '@angular/router';
import {Location} from '@angular/common';
import {Observable, Subscription, zip} from 'rxjs';
import {DeviceService, ViewportBreakpoint} from '../../../../services/device.service';
import {TitleService} from '../../../../services/title.service';
import {UserData, UserService} from '../../../../services/user.service';
import {UiService} from '../../../../services/ui.service';
import {
    PaymentProvidersService,
    SofortPaymentProvider,
    StripePaymentProvider
} from '../../../../services/payment-providers.service';
import {LangService} from '../../../../services/lang.service';
import {PopupService} from '../../../../services/popup.service';
import {ToastService} from '../../../../services/toast.service';

type State = 'loading' | 'error' | 'editor';
type Tab = 'sofort' | 'stripe';

interface PaymentProviders {
    sofort : SofortPaymentProvider;
    stripe : StripePaymentProvider
}

@Component({
    selector: 'payment-providers',
    templateUrl: './payment-providers.component.html',
    styleUrls: [ './payment-providers.component.scss' ],
    encapsulation: ViewEncapsulation.None,
    host: {
        'class': 'payment-providers-editor',
    }
})
export class PaymentProvidersSettingsComponent implements OnDestroy, CanDeactivate<boolean | Promise<boolean>> {
    public subs : Subscription[] = [];

    public viewportBreakpoint : ViewportBreakpoint;

    public state : State;

    public activeTab : Tab;

    public isSaving : boolean = false;

    public isChanged : boolean = false;

    public canUseSofort : boolean = false;

    public providers : PaymentProviders = {
        sofort: null,
        stripe: null
    };

    public isSofortTabHintVisible : boolean = false;

    constructor (
        private router : Router,
        private route : ActivatedRoute,
        private location : Location,
        private titleService : TitleService,
        private userService : UserService,
        private deviceService : DeviceService,
        private langService : LangService,
        private popupService : PopupService,
        private uiService : UiService,
        private paymentProvidersService : PaymentProvidersService,
        private toastService : ToastService,
    ) {
        this.state = 'loading';
        this.viewportBreakpoint = this.deviceService.viewportBreakpoint;
        this.titleService.setTitle('settings.payment_providers.page_title');

        this.applyUserData(this.userService.getUserData());
        this.addSub(this.userService.onUserDataUpdated.subscribe(userData => this.applyUserData(userData)));
        this.addSub(this.uiService.activateBackButton().subscribe(() => this.goBack()));

        this.addSub(this.deviceService.onResize.subscribe(message => {
            if (message.breakpointChange) {
                this.viewportBreakpoint = this.deviceService.viewportBreakpoint;
            }
        }));

        this.addSub(zip(
            this.paymentProvidersService.fetchSofort(),
            this.paymentProvidersService.fetchStripe(),
        ).subscribe(
            ([ sofort, stripe ]) => {
                this.providers.sofort = sofort;
                this.providers.stripe = stripe;
                this.onSwitchTab(this.canUseSofort ? 'sofort' : 'stripe');

                const messageKey : string = this.route.snapshot.params['m'];

                switch (messageKey) {
                    case 'stripe-connected':
                        this.toastService.create({
                            message: [ `settings.payment_providers.${ messageKey }__message` ]
                        });
                        this.location.replaceState(window.location.pathname);
                        break;
                }

                this.state = 'editor';
            },
            () => this.state = 'error'
        ));
    }

    public ngOnDestroy () : void {
        this.subs.forEach(sub => sub.unsubscribe());
        this.uiService.deactivateBackButton();
    }

    public canDeactivate () : Promise<boolean> {
        return new Promise<boolean>((resolve) => {
            if (!this.isChanged) {
                resolve(true);
                return;
            }

            this.popupService.confirm({
                message: [ 'guards.discard' ],
            }).subscribe(({ isOk }) => resolve(isOk));
        });
    }

    public addSub (sub : Subscription) : void {
        this.subs = [ ...this.subs, sub ];
    }

    public applyUserData (userData : UserData) : void {
        this.canUseSofort = userData.features.can('settings:sofort');
    }

    public onSofortTabMouseEvent (isVisible : boolean) : void {
        this.isSofortTabHintVisible = !this.canUseSofort && !this.deviceService.device.touch && isVisible;
    }

    public onSwitchTab (tab : Tab) : void {
        if (tab === 'sofort' && !this.canUseSofort) {
            if (this.deviceService.device.touch) {
                this.popupService.alert({
                    message: [ 'settings.payment_providers.sofort_tab_alert__message' ]
                });
            }
            return;
        }

        this.activeTab = tab;
    }

    public onChange () : void {
        this.isChanged = true;
    }

    public onSave () : void {
        if (this.isSaving) {
            return;
        }

        this.isSaving = true;

        const requests : Observable<any>[] = [
            this.paymentProvidersService.updateStripe(this.providers.stripe)
        ];

        if (this.canUseSofort) {
            requests.push(this.paymentProvidersService.updateSofort(this.providers.sofort));
        }

        this.addSub(zip(...requests).subscribe(([ stripe, sofort ]) => {
            this.providers.stripe = stripe;
            this.providers.sofort = sofort || null;
            this.isChanged = false;
            this.isSaving = false;
            this.toastService.create({
                message: [ `settings.payment_providers.save_success__message` ]
            });
        }, () => {
            this.toastService.create({
                message: [ `settings.payment_providers.save_error__message` ]
            });
            this.isSaving = false;
        }));
    }

    public goBack () : void {
        this.router.navigateByUrl('/dashboard/settings');
    }
}

