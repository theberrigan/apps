import {
    Component,
    EventEmitter,
    HostBinding,
    Input,
    OnDestroy, OnInit,
    Output,
    ViewChild,
    ViewEncapsulation
} from '@angular/core';
import {ActivatedRoute, CanDeactivate, Router} from '@angular/router';
import {Location} from '@angular/common';
import {
    Client,
    ClientBalance,
    ClientBalanceRecord,
    ClientsService,
    Transaction
} from '../../../services/client.service';
import {TitleService} from '../../../services/title.service';
import {Observable, Subscription, zip} from 'rxjs';
import {LangService} from '../../../services/lang.service';
import {UserData, UserService} from '../../../services/user.service';
import {CurrenciesService, Currency, OfferCurrency} from '../../../services/currencies.service';
import {UiService} from '../../../services/ui.service';
import {cloneDeep, forOwn, merge} from 'lodash';
import {PopupService} from '../../../services/popup.service';
import {FormBuilder, FormGroup} from '@angular/forms';
import {defer, float, int, isInt} from '../../../lib/utils';
import {isNumber} from 'util';
import {Rate} from '../../../services/rates.service';
import {PopupComponent} from '../../../widgets/popup/popup.component';
import {DeviceService, ViewportBreakpoint} from '../../../services/device.service';
import {Contact} from '../../../services/offers.service';
import {ToastService} from '../../../services/toast.service';

type Tab = 'general' | 'billing' | 'contacts' | 'rates' | 'balance';
type Mode = 'standalone' | 'embedded';
type EditorMode = 'edit' | 'create';
type NetworkProcess = 'deleting' | 'saving';
type BalanceFilter = 'all' | 'credit' | 'debit';

interface ContactWrap {
    isOpened : boolean,
    isChanged : boolean,
    contact : Contact
}

interface BalanceRecordWrap {
    isVisible : boolean,
    record : ClientBalanceRecord
}


// TODO: can deactivate
@Component({
    selector: 'client-editor',
    templateUrl: './client.component.html',
    styleUrls: [ './client.component.scss' ],
    encapsulation: ViewEncapsulation.None,
    host: {
        'class': 'client-editor',
    }
})
export class ClientComponent implements OnInit, OnDestroy, CanDeactivate<boolean | Promise<boolean>> {
    @Input()
    public mode : Mode = 'standalone';

    @Input()
    public clientId : number = null;

    @Output()
    public onHideEditor = new EventEmitter<{
        client : Client,
        contacts : Contact[]
    }>();

    @ViewChild('contactEditor')
    public contactEditor : PopupComponent;

    public activeTab : Tab = 'general';

    public client : Client = null;

    public editorState : 'init' | 'ready' | 'error';

    public _editorMode : EditorMode;

    public set editorMode (editorMode : EditorMode) {
        this._editorMode = editorMode;

        if (this.mode === 'standalone') {
            this.titleService.setTitle('clients.editor.page_title_' + editorMode);
        }
    }

    public get editorMode () : EditorMode {
        return this._editorMode;
    }

    public viewportBreakpoint : ViewportBreakpoint;

    public networkProcess : NetworkProcess;

    public canEdit : boolean = false;

    public editorForm : FormGroup;

    public dateDisplayFormat : string = 'd MMM y HH:mm';

    public currencyOptions : any[];

    public titleOptions : any[];

    public langsOptions : any[];

    public paymentTypeOptions : any[] = [
        {
            value: 'CASH',
            display: 'CASH'
        },
        {
            value: 'WIRE3DAYS',
            display: 'WIRE3DAYS'
        },
        {
            value: 'WIRE7DAYS',
            display: 'WIRE7DAYS'
        },
        {
            value: 'WIRE14DAYS',
            display: 'WIRE14DAYS'
        },
        {
            value: 'WIRE21DAYS',
            display: 'WIRE21DAYS'
        }
    ];

    public subs : Subscription[] = [];

    // -----------------------

    public rates : { isChanged : boolean, rate : Rate }[];

    public ratesState : 'loading' | 'error' | 'empty' | 'list';

    // -----------------------

    public contacts : ContactWrap[];

    public contactsState : 'loading' | 'error' | 'empty' | 'list';

    public hasOpenedContacts : boolean = false;

    public contactWrapToEdit : ContactWrap;

    public contactEditorMode : 'edit' | 'create';

    // -----------------------

    @ViewChild('transactionEditor')
    public transactionEditor : PopupComponent;

    public isTransactionSaving : boolean = false;

    public transaction : Transaction;

    public balance : number;

    public balanceRecords : BalanceRecordWrap[];

    public balanceState : 'loading' | 'error' | 'empty' | 'list';

    public balanceFilter : BalanceFilter;

    public balanceOrder : any;

    public balanceFilterOptions : any[] = [
        {
            value: 'all',
            display: 'clients.editor.balance_all'
        },
        {
            value: 'credit',
            display: 'clients.editor.balance_credit'
        },
        {
            value: 'debit',
            display: 'clients.editor.balance_debit'
        }
    ];

    public balanceSortOptions : any[] = [
        {
            value: 'created',
            display: 'clients.editor.balance_date'
        },
        {
            value: 'offerKey',
            display: 'clients.editor.balance_offer'
        },
        {
            value: 'projectKey',
            display: 'clients.editor.balance_project'
        },
        {
            value: 'amount',
            display: 'clients.editor.balance_amount'
        },
        {
            value: 'currency',
            display: 'clients.editor.balance_currency'
        },
        {
            value: 'exchangeRate',
            display: 'clients.editor.balance_exchange_rate'
        },
        {
            value: 'credited',
            display: 'clients.editor.balance_credited'
        },
        {
            value: 'balance',
            display: 'clients.editor.balance_balance'
        },
        {
            value: 'comment',
            display: 'clients.editor.balance_comment'
        }
    ];

    public constructor (
        private router : Router,
        private route : ActivatedRoute,
        private location : Location,
        private formBuilder : FormBuilder,
        private titleService : TitleService,
        private langService : LangService,
        private clientsService : ClientsService,
        private currenciesService : CurrenciesService,
        private userService : UserService,
        private uiService : UiService,
        private deviceService : DeviceService,
        private popupService : PopupService,
        private toastService : ToastService
    ) {
        this.editorState = 'init';

        this.viewportBreakpoint = this.deviceService.viewportBreakpoint;

        this.addSub(
            this.deviceService.onResize.subscribe(message => {
                if (message.breakpointChange) {
                    this.viewportBreakpoint = this.deviceService.viewportBreakpoint;
                }
            })
        );

        this.applyUserData(this.userService.getUserData());
        this.addSub(this.userService.onUserDataUpdated.subscribe(userData => this.applyUserData(userData)));

        if (this.mode === 'standalone') {
            this.addSub(this.uiService.activateBackButton().subscribe(() => this.goBack()));
        }

        this.editorForm = this.formBuilder.group({
            preferredLanguage: [ '' ],
            name: [ '' ],
            legalName: [ '' ],
            email: [ '' ],
            email2: [ '' ],
            phone: [ '' ],
            phone2: [ '' ],
            fax: [ '' ],
            zip: [ '' ],
            country: [ '' ],
            state: [ '' ],
            city: [ '' ],
            addressLine: [ '' ],
            addressLine2: [ '' ],
            note: [ '' ],
            tin: [ '' ],
            tax: [ 0 ],
            paymentType: [ '' ],
            currency: [ '' ],
            bankName: [ '' ],
            bankAccount: [ '' ],
        });
    }

    public ngOnInit () : void {

        let clientToLoad = this.mode === 'standalone' ? this.route.snapshot.params['key'] : this.clientId;
        this.editorMode = clientToLoad === 'create' ? 'create' : 'edit';

        this.addSub(zip(
            this.fetchClient(clientToLoad),
            this.langService.fetchLanguages({
                preferredOnly: true,
                addDefault: true
            }),
            this.currenciesService.fetchCurrencies({
                activeOnly: true,
                asOptions: true
            })
        ).subscribe(([ client, langs, currencies ] : [ Client, any[], Currency[] ]) => {
            this.updateClientModel(client);

            this.langsOptions = langs;

            this.currencyOptions = currencies;

            this.titleOptions = [
                {
                    value: '',
                    display: ''
                },
                ...([
                    'offers.editor.prefix_mr__select_option',
                    'offers.editor.prefix_mrs__select_option',
                    'offers.editor.prefix_dr__select_option',
                    'offers.editor.prefix_sir__select_option'
                ].map(transKey => {
                    const translated = this.langService.translate(transKey);

                    return {
                        value: translated,
                        display: translated
                    }
                }))
            ];

            console.warn(this.editorMode, clientToLoad, client, langs);

            this.editorState = 'ready';
        }, () => {
            this.editorState = 'error';
        }));
    }

    public ngOnDestroy () : void {
        this.subs.forEach(sub => sub.unsubscribe());
    }

    public addSub (sub : Subscription) : void {
        this.subs = [ ...this.subs, sub ];
    }

    public canDeactivate () : Promise<boolean> {
        return new Promise<boolean>((resolve) => {
            const hasChanges = !!(
                this.rates && this.rates.some(rateWrap => rateWrap.isChanged) &&
                this.contacts && this.contacts.some(contactWrap => contactWrap.isChanged)
            );

            if (!this.canEdit || !this.editorForm || this.editorForm.pristine && !hasChanges) {
                resolve(true);
                return;
            }

            this.popupService.confirm({
                message: [ 'guards.discard' ],
            }).subscribe(({ isOk }) => resolve(isOk));
        });
    }

    public updateClientModel (client : Client) : void {
        this.client = client;

        Object.keys(this.editorForm.getRawValue()).forEach(key => {
            this.editorForm.controls[key].setValue(client[key]);
        });

        client.deleted ? this.editorForm.disable() : this.editorForm.enable();
    }

    public applyUserData (userData : UserData) : void {
        this.canEdit = userData.features.can('edit:clients');
        this.dateDisplayFormat = userData.settings.formats.datetime.display;
    }

    public fetchClient (key : string) : Observable<Client> {
        return Observable.create(observer => {
            if (key === 'create') {
                observer.next(new Client());
            } else {
                this.addSub(this.clientsService.loadClient(Number(key)).subscribe(
                    (client : Client) => observer.next(client),
                    () => observer.error()
                ));
            }
        });
    }

    public switchTab (tab : Tab) : void {
        this.activeTab = tab;

        switch (tab) {
            case 'contacts':
                this.fetchContacts();
                break;
            case 'rates':
                this.fetchRates();
                break;
            case 'balance':
                this.fetchBalance();
                break;
        }
    }

    public onToggleActivity () : void {
        if (this.client.deleted) {
            this.onSave(true);
        } else {
            this.popupService.confirm({
                message: [ 'clients.editor.confirm_delete__message' ],
            }).subscribe(({ isOk }) => {
                isOk && this.onSave(true);
            });
        }
    }

    public onSave (toggleActivity : boolean = false) : void {
        if (
            this.editorState !== 'ready' || this.networkProcess || !this.client ||
            (toggleActivity ? this.editorMode === 'create' : this.client.deleted)
        ) {
            return;
        }

        this.networkProcess = toggleActivity ? 'deleting' : 'saving';

        const client : Client = merge({}, this.client, this.editorForm.getRawValue());

        const tax = Number(client.tax);
        client.tax = isNumber(tax) ? tax : 0;

        if (toggleActivity) {
            client.deleted = !client.deleted;
        }

        (this.editorMode === 'create' ? this.createClient(client) : this.saveClient(client)).then(() => {
            this.networkProcess = null;
            this.editorForm.markAsPristine();

            if (this.mode === 'standalone') {
                if (this.editorMode === 'create') {
                    this.editorMode = 'edit';
                    this.location.replaceState('/dashboard/client/' + this.client.id);
                }
            } else {
                if (!toggleActivity) {
                    this.onHideEditor.emit({
                        client: this.client,
                        contacts: (this.contacts || []).map(contactWrap => contactWrap.contact)
                    });
                }
            }
        }).catch(() => {
            this.networkProcess = null;
            this.toastService.create({
                message: [ 'clients.editor.save_failed' ]
            });
        })
    }

    public createClient (client : Client) : Promise<void> {
        return new Promise((resolve, reject) => {
            this.addSub(this.clientsService.createClient(client).subscribe(
                (client : Client) => {
                    this.updateClientModel(client);
                    resolve();
                },
                () => reject()
            ));
        });
    }

    public saveClient (client : Client) : Promise<void> {
        return new Promise((resolve, reject) => {
            const requests = [];

            // -------------------

            requests.push(this.clientsService.saveClient(client));

            // --------------------

            const changedContactsIndexes : number[] = [];

            if (this.contacts) {
                this.contacts.forEach((contactWrap, i) => {
                    if (contactWrap.isChanged) {
                        if (contactWrap.contact.id === 0) {
                            requests.push(this.clientsService.createContact(this.client.id, contactWrap.contact));
                        } else {
                            requests.push(this.clientsService.saveContact(this.client.id, contactWrap.contact));
                        }
                        changedContactsIndexes.push(i);
                    }
                });
            }

            // --------------------

            this.addSub(
                zip(...requests).subscribe(
                    (responses : any[]) => {
                        this.updateClientModel(responses.shift());

                        changedContactsIndexes.forEach(i => {
                            const contactWrap = this.contacts[i];
                            contactWrap.contact = responses.shift();
                            contactWrap.isChanged = false;
                        });

                        this.toastService.create({
                            message: [ 'clients.editor.save_success' ]
                        });

                        resolve();
                    },
                    () => reject()
                )
            );
        });
    }

    public fetchRates () : void {
        if (
            this.ratesState === 'loading' || this.ratesState === 'empty' || this.ratesState === 'list' ||
            this.editorMode === 'create' || !this.client
        ) {
            return;
        }

        this.ratesState = 'loading';

        this.addSub(
            this.clientsService.fetchRates(this.client.id).subscribe(
                (rates : Rate[]) => {
                    if (rates.length) {
                        this.rates = rates.map(rate => {
                            rate.selected = rate.selected || rate.global;

                            return {
                                isChanged: false,
                                rate
                            };
                        });

                        this.ratesState = 'list';
                    } else {
                        this.ratesState = 'empty';
                    }
                },
                () => {
                    this.ratesState = 'error';
                }
            )
        );
    }

    public fetchContacts () : void {
        if (
            this.contactsState === 'loading' || this.contactsState === 'empty' || this.contactsState === 'list' ||
            this.editorMode === 'create' || !this.client
        ) {
            return;
        }

        this.contactsState = 'loading';

        this.addSub(
            this.clientsService.fetchContacts(this.client.id).subscribe(
                (contacts : Contact[]) => {
                    // contacts = [];
                    if (contacts.length) {
                        this.contacts = contacts.map(contact => {
                            return {
                                isOpened: false,
                                isChanged: false,
                                contact
                            };
                        });

                        this.contactsState = 'list';
                    } else {
                        this.contacts = [];
                        this.contactsState = 'empty';
                    }
                },
                () => {
                    this.contacts = [];
                    this.contactsState = 'error';
                }
            )
        );
    }

    public toggleContactDetails (contactWrap : ContactWrap) : void {
        contactWrap.isOpened = !contactWrap.isOpened;
        this.hasOpenedContacts = this.contacts.some(cw => cw.isOpened);
    }

    public toggleAllContactsDetails () : void {
        const hasOpened = this.hasOpenedContacts;
        this.contacts.forEach(cw => cw.isOpened = !hasOpened);
        this.hasOpenedContacts = !hasOpened;
    }

    public showContactEditor (contactWrap : ContactWrap = null) : void {
        if (!this.canEdit || this.networkProcess || this.contactsState === 'loading' || this.contactsState === 'error') {
            return;
        }

        if (contactWrap) {
            this.contactWrapToEdit = <ContactWrap>cloneDeep(contactWrap);
            this.contactEditorMode = 'edit';
        } else {
            this.contactWrapToEdit = {
                isChanged: true,
                isOpened: false,
                contact: new Contact({ id: 0 })
            };
            this.contactEditorMode = 'create';
        }

        this.contactEditor.activate();
    }

    public hideContactEditor (byOverlay : boolean = false) : void {
        if (byOverlay) {
            return;
        }

        this.contactEditor.deactivate().then(() => {
            this.contactWrapToEdit = null;
            this.contactEditorMode = null;
        });
    }

    public submitContact () : void {
        const contactWrap : ContactWrap = this.contactWrapToEdit;
        contactWrap.isChanged = true;

        if (contactWrap.contact.primary) {
            this.contacts.forEach(cw => {
                if (cw.contact.primary) {
                    cw.contact.primary = false;
                    cw.isChanged = true;
                }
            });
        }

        if (this.contactEditorMode === 'create') {
            this.contacts.push(contactWrap);
        } else {
            const wrapIndex = this.contacts.indexOf(this.contacts.find(cw => cw.contact.id === contactWrap.contact.id));
            this.contacts[wrapIndex] = contactWrap;
        }

        if (this.contactsState === 'empty') {
            this.contactsState = 'list';
        }

        this.hideContactEditor();
    }

    public isContactValid () : boolean {
        const contact : Contact = this.contactWrapToEdit && this.contactWrapToEdit.contact;

        return !!(
            contact &&
            (
                (contact.fullName || '').trim() ||
                (contact.email || '').trim() ||
                (contact.phone || '').trim() ||
                (contact.fax || '').trim() ||
                (contact.position || '').trim() ||
                (contact.notes || '').trim()
            )
        );
    }

    public fetchBalance (isReload : boolean = false) : Promise<any> {
        return new Promise((resolve) => {
            if (!isReload && (
                this.balanceState === 'loading' ||
                this.balanceState === 'empty' ||
                this.balanceState === 'list' ||
                this.editorMode === 'create' ||
                !this.client
            )) {
                resolve();
                return;
            }

            if (!isReload) {
                this.balanceState = 'loading';
            }

            if (!this.balanceFilter) {
                this.balanceFilter = 'all';
            }

            if (!this.balanceOrder) {
                this.balanceOrder = {
                    by: this.balanceSortOptions[0].value,
                    direction: -1
                };
            }

            this.addSub(
                this.clientsService.fetchBalance(this.client.id).subscribe(
                    (response : ClientBalance) => {
                        this.balance = response.balance;

                        if (response.items.length) {
                            this.balanceRecords = response.items.map(record => {
                                return {
                                    isVisible: true,
                                    record
                                };
                            });

                            this.filterBalanceRecords();
                            this.sortBalanceRecords();
                            this.balanceState = 'list';
                        } else {
                            this.balanceRecords = [];
                            this.balanceState = 'empty';
                        }

                        resolve();
                    },
                    () => {
                        this.balance = 0;
                        this.balanceRecords = [];
                        this.balanceState = 'error';
                        resolve();
                    }
                )
            );
        });
    }

    public filterBalanceRecords () : void {
        this.balanceRecords.forEach(recordWrap => {
            recordWrap.isVisible = (
                this.balanceFilter == 'all' ||
                this.balanceFilter == 'credit' && recordWrap.record.credited > 0 ||
                this.balanceFilter == 'debit' && recordWrap.record.credited < 0
            );
        });
    }

    public sortBalanceRecords () : void {
        if (!this.balanceRecords) {
            return;
        }

        const { by, direction } = this.balanceOrder;

        this.balanceRecords.sort((rw1, rw2) => {
            const
                a = rw1.record[by] === null ? '' : String(rw1.record[by]),
                b = rw2.record[by] === null ? '' : String(rw2.record[by]),
                c1 = rw1.record.created,
                c2 = rw2.record.created;

            return (a.localeCompare(b) || (c2 < c2 ? -1 : c2 > c2 ? 1 : 0)) * direction;
        });
    }

    public onBalanceFilter () : void {
        defer(() => this.filterBalanceRecords());
    }

    public onBalanceSort () : void {
        defer(() => this.sortBalanceRecords());
    }

    public showTransactionEditor () : void {
        if (!this.canEdit || this.networkProcess || this.balanceState === 'loading' || this.balanceState === 'error') {
            return;
        }

        this.transaction = {
            amount: 0,
            comment: '',
            currency: this.currencyOptions[0].value,
        };

        this.transactionEditor.activate();
    }

    public hideTransactionEditor (byOverlay : boolean = false) : void {
        if (byOverlay || this.isTransactionSaving) {
            return;
        }

        this.transactionEditor.deactivate().then(() => {
            this.transaction = null;
        });
    }

    public isTransactionValid () : boolean {
        return !!(this.transaction && isNumber(Number(this.transaction.amount)) && Number(this.transaction.amount) > 0 && this.transaction.currency);
    }

    public saveTransaction () : void {
        if (!this.canEdit || this.networkProcess || !this.isTransactionValid() || this.isTransactionSaving) {
            return;
        }

        this.isTransactionSaving = true;

        const transaction : Transaction = cloneDeep(this.transaction);

        transaction.amount = float(transaction.amount);

        this.clientsService.saveTransaction(this.client.id, transaction).subscribe(
            () => {
                this.fetchBalance(true).then(() => {
                    this.isTransactionSaving = false;
                    this.hideTransactionEditor();
                });
            },
            () => {
                this.isTransactionSaving = false;
                this.toastService.create({
                    message: [ 'clients.editor.transaction_not_saved' ]
                });
            }
        );
    }

    public goBack () : void {
        if (this.mode == 'standalone') {
            this.uiService.deactivateBackButton();
            this.router.navigateByUrl('/dashboard/clients');
        } else {
            this.onHideEditor.emit();
        }
    }
}
