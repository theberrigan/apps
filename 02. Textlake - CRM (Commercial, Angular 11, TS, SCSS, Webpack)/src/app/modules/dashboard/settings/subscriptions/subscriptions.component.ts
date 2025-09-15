import {Component, OnDestroy, ViewChild, ViewEncapsulation} from '@angular/core';
import {CanDeactivate, Router} from '@angular/router';
import {Subscription, zip} from 'rxjs';
import {DeviceService, ViewportBreakpoint} from '../../../../services/device.service';
import {TitleService} from '../../../../services/title.service';
import {UserData, UserService} from '../../../../services/user.service';
import {UiService} from '../../../../services/ui.service';
import {
    SubscriptionDetails,
    SubscriptionInvoice,
    SubscriptionService,
    UpcomingInvoice
} from '../../../../services/subscription.service';
import {PlanPromo, PlansService} from '../../../../services/plans.service';
import {PopupService} from '../../../../services/popup.service';
import {mergeMap} from 'rxjs/operators';
import {PopupComponent} from '../../../../widgets/popup/popup.component';
import {defer} from '../../../../lib/utils';
import {FundingSourceComponent} from '../../../../widgets/funding-source/funding-source.component';
import {ToastService} from '../../../../services/toast.service';

type State = 'loading' | 'error' | 'editor';
type Tab = 'general' | 'invoices';
type Layout = 'main' | 'plans';

@Component({
    selector: 'subscriptions',
    templateUrl: './subscriptions.component.html',
    styleUrls: [ './subscriptions.component.scss' ],
    encapsulation: ViewEncapsulation.None,
    host: {
        'class': 'subscriptions-editor',
    }
})
export class SubscriptionsSettingsComponent implements OnDestroy, CanDeactivate<boolean | Promise<boolean>> {
    public subs : Subscription[] = [];

    public viewportBreakpoint : ViewportBreakpoint;

    public isSaving : boolean = false;

    public isChanged : boolean = false;

    public state : State;

    public activeTab : Tab;

    public layout : Layout;

    public subscription : SubscriptionDetails;

    public availablePlans : PlanPromo[];

    public invoices : SubscriptionInvoice[];

    public nextBill : UpcomingInvoice;

    public usersNumber : number;

    public canChangePlan : boolean;

    public hasUnpaidInvoices : boolean;

    public datetimeDisplayFormat : string;

    public usersOptions : number[] = [];

    public isFundingSourceExists : boolean = false;

    @ViewChild('fundingSourcePopup')
    public fundingSourcePopup : PopupComponent;

    @ViewChild('fundingSource')
    public fundingSource : FundingSourceComponent;

    public isFundingSourcePopupVisible : boolean = false;

    public isSubmittingFundingSource : boolean = false;

    @ViewChild('paymentPopup')
    public paymentPopup : PopupComponent;

    @ViewChild('paymentFundingSource')
    public paymentFundingSource : FundingSourceComponent;

    public isPaymentPopupVisible : boolean = false;

    public isSubmittingPayment : boolean = false;

    public invoiceToPay : SubscriptionInvoice;

    public isPaymentWithExistingFundingSource : boolean;

    constructor (
        private router : Router,
        private titleService : TitleService,
        private userService : UserService,
        private deviceService : DeviceService,
        private popupService : PopupService,
        private uiService : UiService,
        private subscriptionService : SubscriptionService,
        private plansService : PlansService,
        private toastService : ToastService,
    ) {
        this.state = 'loading';
        this.layout = 'main';
        this.viewportBreakpoint = this.deviceService.viewportBreakpoint;
        this.titleService.setTitle('subs.page__title');

        this.applyUserData(this.userService.getUserData());
        this.addSub(this.userService.onUserDataUpdated.subscribe(userData => this.applyUserData(userData)));
        this.addSub(this.uiService.activateBackButton().subscribe(() => this.goBack()));

        this.addSub(this.deviceService.onResize.subscribe(message => {
            if (message.breakpointChange) {
                this.viewportBreakpoint = this.deviceService.viewportBreakpoint;
            }
        }));

        for (let i = 3; i <= 15; i++) {
            this.usersOptions.push(i);
        }

        this.fetchData();
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

    public fetchData () : Promise<boolean> {
        return new Promise((resolve) => {
            this.state = 'loading';

            this.addSub(zip(
                this.subscriptionService.fetchSubscription(),
                this.subscriptionService.fetchInvoices(),
                this.subscriptionService.fetchNextBill(),
                this.plansService.fetchPlans(),
            ).subscribe(
                ([ subscription, invoices, nextBill, plans ]) => {
                    // invoices.forEach(i => i.paid = false);
                    this.subscription = subscription;
                    this.invoices = invoices;
                    this.nextBill = nextBill;
                    this.availablePlans = plans;

                    this.updateCommonData(subscription, plans);
                    this.hasUnpaidInvoices = !invoices.every(i => i.paid);

                    this.onSwitchTab('general');
                    this.state = 'editor';
                    resolve(true);
                },
                () => {
                    this.state = 'error';
                    resolve(false);
                }
            ));
        });
    }

    public updateCommonData (subscription : SubscriptionDetails, plans? : PlanPromo[]) : void {
        plans = plans || this.availablePlans || [];

        this.usersNumber = subscription ? subscription.quantity : 0;
        this.canChangePlan = (plans.length > 0 && (!subscription || !subscription.plan || !subscription.plan.name || plans.some(p => p.name !== subscription.plan.name)));
        this.isFundingSourceExists = !!(subscription && subscription.fundingSource);
    }

    public addSub (sub : Subscription) : void {
        this.subs = [ ...this.subs, sub ];
    }

    public applyUserData (userData : UserData) : void {
        this.datetimeDisplayFormat = userData.settings.formats.date.display;
    }

    public onSwitchTab (tab : Tab) : void {
        this.activeTab = tab;
    }

    public onChange () : void {
        this.isChanged = true;
    }

    public onChangeFundingSource () : void {
        if (this.isSaving) {
            return;
        }

        this.isFundingSourcePopupVisible = true;
        defer(() => this.fundingSourcePopup.activate());
    }

    public onChangePlan () : void {
        if (this.isSaving || !this.canChangePlan) {
            return;
        }

        this.layout = 'plans';
    }

    public onPay (invoice : SubscriptionInvoice) : void {
        if (this.isSaving) {
            return;
        }

        this.invoiceToPay = invoice;
        this.isPaymentPopupVisible = true;
        defer(() => this.paymentPopup.activate());
    }

    public onSave () : void {
        if (this.isSaving || !this.subscription || this.subscription.quantity === this.usersNumber) {
            return;
        }

        this.popupService.confirm({
            message: [ 'subs.confirm_users_change' ],
        }).subscribe(({ isOk }) => {
            if (!isOk) {
                return;
            }

            this.isSaving = true;

            this.addSub(this.subscriptionService.updateSubscription({
                quantity: this.usersNumber,
                fundingSource: null
            }).pipe(
                mergeMap(subscription => {
                    this.subscription = subscription;
                    this.usersNumber = subscription.quantity;
                    return this.subscriptionService.fetchNextBill();
                })
            ).subscribe(
                nextBill => {
                    this.nextBill = nextBill;
                    this.isChanged = false;
                    this.isSaving = false;
                    this.toastService.create({
                        message: [ 'subs.save_success' ]
                    });
                },
                () => {
                    this.isSaving = false;
                    this.toastService.create({
                        message: [ 'subs.save_error' ]
                    });
                }
            ));
        });
    }

    public onPlanChanged () : void {
        this.layout = 'main';

        this.fetchData().then(isOk => {
            if (isOk) {
                this.toastService.create({
                    message: [ 'subs.plan_success_change__toast' ]
                });
            }
        });
    }

    public onSubmitFundingSource () : void {
        this.isSubmittingFundingSource = true;
        this.fundingSource.submitCard();
    }

    public isCardValid () : boolean {
        return !!this.fundingSource && this.fundingSource.isCardValid();
    }

    public onHideFundingSourcePopup (byOverlay : boolean = false) : void {
        if (byOverlay) {
            return;
        }

        this.fundingSourcePopup.deactivate().then(() => {
            this.isFundingSourcePopupVisible = false;
        });
    }

    public onFundingSourceSubmitted (response : any) : void {
        if (!response.isOk) {
            this.isSubmittingFundingSource = false;
            return;
        }

        this.addSub(this.subscriptionService.updateSubscription({
            fundingSource: response.token.id,
            quantity: this.usersNumber
        }).subscribe(subscription => {
            console.warn('subscription', subscription);
            this.isSubmittingFundingSource = false;
            this.subscription = subscription;
            this.updateCommonData(subscription);
            this.onHideFundingSourcePopup();
            this.toastService.create({
                message: [ 'subs.funding_source_updated__toast' ]
            });
        }, () => {
            this.isSubmittingFundingSource = false;
            this.toastService.create({
                message: [ 'subs.subs_error__toast' ]
            });
        }));
    }

    public onSubmitPayment (useExistingFundingSource : boolean) : void {
        this.isPaymentWithExistingFundingSource = useExistingFundingSource;
        this.isSubmittingPayment = true;

        if (useExistingFundingSource) {
            this.payInvoiceWithToken();
        } else {
            this.paymentFundingSource.submitCard();
        }
    }

    public onPaymentFundingSourceSubmitted (response : any) : void {
        if (!response.isOk) {
            this.isSubmittingPayment = false;
            return;
        }

        this.payInvoiceWithToken(response.token.id);
    }

    public payInvoiceWithToken (token : string = null) : void {
        this.addSub(this.subscriptionService.payTheInvoice(this.invoiceToPay.invoiceId, token).subscribe(
            invoice => {
                this.invoices.splice(this.invoices.indexOf(this.invoiceToPay), 1, invoice);
                this.hasUnpaidInvoices = !this.invoices.every(i => i.paid);
                this.isSubmittingPayment = false;
                this.onHidePaymentPopup();
                this.toastService.create({
                    message: [ 'subs.invoice_paid__toast' ]
                });
            },
            () => {
                this.isSubmittingPayment = false;
                this.toastService.create({
                    message: [ 'subs.invoice_pay_error__toast' ]
                });
            }
        ));
    }

    public isPaymentCardValid () : boolean {
        return !!this.paymentFundingSource && this.paymentFundingSource.isCardValid();
    }

    public onHidePaymentPopup (byOverlay : boolean = false) : void {
        if (byOverlay) {
            return;
        }

        this.paymentPopup.deactivate().then(() => {
            this.isPaymentPopupVisible = false;
            this.invoiceToPay = null;
        });
    }

    public goBack () : void {
        switch (this.layout) {
            case 'main':
                this.router.navigateByUrl('/dashboard/settings');
                break;
            case 'plans':
                this.layout = 'main';
                break;
        }
    }
}

