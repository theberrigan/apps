import {Component, OnDestroy, ViewChild, ViewEncapsulation} from '@angular/core';
import {CanDeactivate, Router} from '@angular/router';
import {Subscription, zip} from 'rxjs';
import {DeviceService, ViewportBreakpoint} from '../../../../services/device.service';
import {TitleService} from '../../../../services/title.service';
import {UserData, UserService} from '../../../../services/user.service';
import {UiService} from '../../../../services/ui.service';
import {
    CurrenciesService,
    Currency,
    GetCurrencyHistoryResponse,
    UpdateCurrencyRatesRequest
} from '../../../../services/currencies.service';
import {PopupService} from '../../../../services/popup.service';
import {deleteFromArray} from '../../../../lib/utils';
import {cloneDeep, shuffle} from 'lodash';
import {LangService} from '../../../../services/lang.service';
import {PopupComponent} from '../../../../widgets/popup/popup.component';
import {ToastService} from '../../../../services/toast.service';

type State = 'loading' | 'error' | 'empty' | 'list';

class EditorCurrency {
    key : string = null;
    name : string = '';
    rate : number = null;
    isPrimary : boolean = false;
    isActive : boolean = false;
}

@Component({
    selector: 'currencies',
    templateUrl: './currencies.component.html',
    styleUrls: [ './currencies.component.scss' ],
    encapsulation: ViewEncapsulation.None,
    host: {
        'class': 'currencies-editor',
    }
})
export class CurrenciesSettingsComponent implements OnDestroy, CanDeactivate<boolean | Promise<boolean>> {
    public subs : Subscription[] = [];

    public viewportBreakpoint : ViewportBreakpoint;

    public datetimeDisplayFormat : string;

    public isSaving : boolean = false;

    public isLoadingHistory : boolean = false;

    public state : State;

    public canEdit : boolean;

    public currencies : EditorCurrency[];

    public isChanged : boolean = false;

    @ViewChild('historyPopup')
    public historyPopup : PopupComponent;

    public history : GetCurrencyHistoryResponse;

    constructor (
        private router : Router,
        private titleService : TitleService,
        private userService : UserService,
        private deviceService : DeviceService,
        private uiService : UiService,
        private langService : LangService,
        private popupService : PopupService,
        private currenciesService : CurrenciesService,
        private toastService : ToastService,
    ) {
        this.state = 'loading';
        this.viewportBreakpoint = this.deviceService.viewportBreakpoint;
        this.titleService.setTitle('settings.currencies.page_title');

        this.applyUserData(this.userService.getUserData());
        this.addSub(this.userService.onUserDataUpdated.subscribe(userData => this.applyUserData(userData)));
        this.addSub(this.uiService.activateBackButton().subscribe(() => this.goBack()));

        this.addSub(this.deviceService.onResize.subscribe(message => {
            if (message.breakpointChange) {
                this.viewportBreakpoint = this.deviceService.viewportBreakpoint;
            }
        }));

        this.addSub(zip(
            this.currenciesService.fetchCurrencies(),
            this.currenciesService.fetchCurrenciesRates(),
        ).subscribe(
            ([ currencies, rates ]) => {
                const primaryCurrencyKey = rates.primaryCurrency.key;

                const ratesMap = rates.rates.reduce((acc, rate) => {
                    acc[rate.key] = rate;
                    return acc;
                }, {});

                const editorCurrencies : EditorCurrency[] = [];

                (<Currency[]>currencies).forEach(currency => {
                    const currencyRate = ratesMap[currency.key];

                    const editorCurrency = new EditorCurrency();
                    editorCurrency.key = currency.key;
                    editorCurrency.name = currency.name;
                    editorCurrency.isPrimary = currency.key === primaryCurrencyKey;

                    if (currencyRate) {
                        editorCurrency.rate = currencyRate.rate;
                        editorCurrency.isActive = true;
                    } else {
                        editorCurrency.rate = 0;
                        editorCurrency.isActive = false;
                    }

                    editorCurrencies.push(editorCurrency);
                });

                this.currencies = this.sortCurrencies(editorCurrencies);
                this.state = editorCurrencies.length ? 'list' : 'empty';
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
            if (!this.canEdit || !this.isChanged) {
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
        this.datetimeDisplayFormat = userData.settings.formats.datetime.display;
        this.canEdit = userData.features.can('edit:currencies');
    }

    public sortCurrencies (currencies : EditorCurrency[]) : EditorCurrency[] {
        return currencies.sort((a, b) => {
            return (Number(b.isPrimary) - Number(a.isPrimary)) || a.name.localeCompare(b.name);
        });
    }

    public makePrimary (currency : Currency) : void {
        if (!this.canEdit) {
            return;
        }

        this.popupService.confirm({
            message: [ 'settings.currencies.make_primary__message', { currencyKey: currency.name } ],
        }).subscribe(({ isOk }) => {
            if (!isOk) {
                return;
            }

            this.currencies.forEach(c => {
                c.isActive = c.isPrimary = c.key === currency.key;
                c.rate = 0;
            });

            this.currencies = this.sortCurrencies(this.currencies);
        });

        this.onChange();
    }

    public viewHistory (currency : Currency) : void {
        if (this.isSaving || this.isLoadingHistory) {
            return;
        }

        this.isLoadingHistory = true;
        this.historyPopup.showSpinner();
        this.historyPopup.activate();

        this.addSub(this.currenciesService.fetchCurrenciesRatesHistory(this.currencies[0].key, currency.key).subscribe(
            (history : GetCurrencyHistoryResponse) => {
                this.history = history;
                this.historyPopup.showBox();
            },
            () => {

            },
            () => this.isLoadingHistory = false
        ));
    }

    public onHistoryPopupDeactivated () : void {
        this.history = null;
    }

    public onChange () : void {
        this.isChanged = true;
    }

    public onSave () : void {
        if (!this.canEdit || this.isSaving || this.isLoadingHistory) {
            return;
        }

        this.isSaving = true;

        const ratesData : UpdateCurrencyRatesRequest = {
            primaryCurrency: this.currencies[0].isPrimary ? this.currencies[0].key : null,
            rates: this.currencies.map(currency => ({
                key: currency.key,
                rate: currency.rate
            }))
        };

        this.addSub(this.currenciesService.updateCurrenciesRates(ratesData).subscribe(
            () => {
                this.isChanged = false;
                this.toastService.create({
                    message: [ 'settings.currencies.save_success__message' ]
                });
            },
            () => {
                this.toastService.create({
                    message: [ 'settings.currencies.save_error__message' ]
                });
            },
            () => this.isSaving = false
        ));
    }

    public goBack () : void {
        this.router.navigateByUrl('/dashboard/settings');
    }
}

