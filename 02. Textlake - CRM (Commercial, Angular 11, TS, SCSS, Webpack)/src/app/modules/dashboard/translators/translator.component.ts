import {Component, OnDestroy, OnInit, ViewChild, ViewEncapsulation} from '@angular/core';
import {Location} from '@angular/common';
import {forkJoin, Observable, of, Subscription, zip} from 'rxjs';
import {DeviceService, ViewportBreakpoint} from '../../../services/device.service';
import {FormBuilder, FormControl, FormGroup} from '@angular/forms';
import {ActivatedRoute, CanDeactivate, Router} from '@angular/router';
import {TitleService} from '../../../services/title.service';
import {UserData, UserService} from '../../../services/user.service';
import {
    Translator,
    TranslatorFinancial,
    TranslatorServiceItem,
    TranslatorsService
} from '../../../services/translators.service';
import {CompanyService, CompanyServiceItem} from '../../../services/company.service';
import {LangService} from '../../../services/lang.service';
import {
    defer,
    deleteFromArray,
    isFloat,
    isFloatString,
    isInt,
    isIntString,
    uniqueId,
    updateObject
} from '../../../lib/utils';
import {CurrenciesService} from '../../../services/currencies.service';
import {mergeMap} from 'rxjs/operators';
import {PopupService} from '../../../services/popup.service';
import {UiService} from '../../../services/ui.service';
import {PopupComponent} from '../../../widgets/popup/popup.component';
import {cloneDeep} from 'lodash';
import {Address} from '../../../types/address.type';
import {ToastService} from '../../../services/toast.service';

type Tab = 'general' | 'services' | 'financial';
type State = 'loading' | 'error' | 'ready';
type SSNState = 'loading' | 'hidden' | 'visible';

class TranslatorServiceWrap {
    id : string;
    service : TranslatorServiceItem;
    isOpen : boolean;
}

@Component({
    selector: 'translator-editor',
    templateUrl: './translator.component.html',
    styleUrls: [ './translator.component.scss' ],
    encapsulation: ViewEncapsulation.None,
    host: {
        'class': 'translator-editor',
    }
})
export class TranslatorEditorComponent implements OnInit, OnDestroy, CanDeactivate<boolean | Promise<boolean>> {
    @ViewChild('serviceEditor')
    public serviceEditor : PopupComponent;

    public state : State;

    public activeTab : Tab;

    public isEditing : boolean;

    public canEdit : boolean;

    public isSaving : boolean;

    public subs : Subscription[] = [];

    public dateSelectFormat : string;

    public viewportBreakpoint : ViewportBreakpoint;

    public translator : Translator;

    public translatorServiceWraps : TranslatorServiceWrap[];

    public translatorFinancial : TranslatorFinancial;

    public ssnState : SSNState;

    public ssnSub : Subscription;

    public form : FormGroup;

    public paymentTypeOptions : any[] = [
        {
            value: null,
            display: ''
        },
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

    public languageOptions : any[];

    public languagesMap : any;

    public currenciesOptions : any[];

    public serviceOptions : any[];

    public filteredServiceOptions : any[];

    public servicesMap : any;

    public subjectAreaOptions : any[];

    public filteredSubjectAreaOptions : any[];

    public subjectAreaMap : any;

    public translationTypeOptions : any[];

    public translationTypesMap : any;

    public serviceEditorMode : 'create' | 'edit';

    public serviceWrapToEdit : TranslatorServiceWrap;

    public serviceEditorFilters : any;

    public saveTasks : any[] = [];

    public subjectAreaModel : any = null;

    public hasOpenedServices : boolean = false;

    constructor (
        private location : Location,
        private route : ActivatedRoute,
        private router : Router,
        private formBuilder : FormBuilder,
        private titleService : TitleService,
        private userService : UserService,
        private deviceService : DeviceService,
        private translatorsService : TranslatorsService,
        private companyService : CompanyService,
        private currenciesService : CurrenciesService,
        private langService : LangService,
        private popupService : PopupService,
        private toastService : ToastService,
        private uiService : UiService
    ) {
        this.state = 'loading';
        this.activeTab = 'general';
        this.isSaving = false;

        const translatorToLoad = (this.route.snapshot.params['key'] || '').toLowerCase();
        this.isEditing = translatorToLoad !== 'create';

        this.updateTitle();

        this.viewportBreakpoint = this.deviceService.viewportBreakpoint;

        this.addSub(this.deviceService.onResize.subscribe(message => {
            if (message.breakpointChange) {
                this.viewportBreakpoint = this.deviceService.viewportBreakpoint;
            }
        }));

        this.applyUserData(this.userService.getUserData());
        this.addSub(this.userService.onUserDataUpdated.subscribe(userData => this.applyUserData(userData)));

        this.addSub(this.uiService.activateBackButton().subscribe(() => this.goBack()));

        this.form = this.formBuilder.group({
            primary: this.formBuilder.group({
                lastName: [ '' ],
                firstName: [ '' ],
                middleName: [ '' ],
                legalName: [ '' ],
                email: [ '' ],
                email2: [ '' ],
                phone: [ '' ],
                phone2: [ '' ],
                fax: [ '' ],
                addressLine: [ '' ],
                addressLine2: [ '' ],
                city: [ '' ],
                state: [ '' ],
                zip: [ '' ],
                country: [ '' ],
                nativeLanguage: [ '' ],
                comment: [ '' ],
                color: [ null ],
                active: [ true ]
            }),
            financial: this.formBuilder.group({
                tin: [ '' ],
                personalNumber: [ '' ],
                currency: [ null ],
                paymentType: [ null ],
                bankName: [ '' ],
                bankAccount: [ '' ],
                dateOfBirth: [ null ],
                placeOfBirth: [ '' ],
                placeOfBirthAddress: this.formBuilder.group({
                    addressLine: [ '' ],
                    addressLine2: [ '' ],
                    city: [ '' ],
                    state: [ '' ],
                    country: [ '' ],
                    zip: [ '' ],
                }),
                taxAgency: [ '' ],
                taxAgencyAddress: this.formBuilder.group({
                    addressLine: [ '' ],
                    addressLine2: [ '' ],
                    city: [ '' ],
                    state: [ '' ],
                    country: [ '' ],
                    zip: [ '' ],
                })
            })
        });

        const requests : Observable<any>[] = [
            this.companyService.fetchBasicServices(),
            this.companyService.fetchSubjectAreas(true),
            this.companyService.fetchTranslationTypes(true),
            this.langService.fetchLanguages({
                addDefault: true
            }),
            this.currenciesService.fetchCurrencies({
                asOptions: true,
                addDefault: true
            }),
        ];

        if (this.isEditing) {
            if (!isIntString(translatorToLoad)) {
                this.state = 'error';
                return;
            }

            const translatorId = Number(translatorToLoad);

            requests.push(
                this.translatorsService.fetchTranslator(translatorId),
                this.translatorsService.fetchTranslatorServices(translatorId),
                this.translatorsService.fetchTranslatorFinancial(translatorId)
            );
        }

        this.addSub(zip(...requests).subscribe(
            ([
                companyServices,
                subjectAreas,
                translationTypes,
                languages,
                currencies,
                ...responses
            ]) => {
                companyServices = companyServices.map(service => {
                    const from = service.from ? this.langService.translate('langs.' + service.from.toLowerCase()) : '';
                    const to = service.to ? this.langService.translate('langs.' + service.to.toLowerCase()) : '';
                    service.name = `${ service.name } (${ from } → ${ to })`;
                    return service;
                });

                this.serviceOptions = [
                    {
                        value: null,
                        display: '',
                        from: null,
                        to: null
                    },
                    ...companyServices.map(service => ({
                        display: service.name,
                        value: service.id,
                        from: service.from,
                        to: service.to
                    }))
                ];

                this.servicesMap = companyServices.reduce((acc, service) => {
                    acc[service.id] = service;
                    return acc;
                }, {});

                this.subjectAreaOptions = [
                    {
                        display: '',
                        value: null
                    },
                    ...subjectAreas
                ];

                this.subjectAreaMap = subjectAreas.reduce((acc, subjectArea) => {
                    acc[subjectArea.value] = subjectArea.display;
                    return acc;
                }, {});

                this.translationTypeOptions = [
                    {
                        display: '',
                        value: null
                    },
                    ...translationTypes
                ];

                this.translationTypesMap = translationTypes.reduce((acc, translationType) => {
                    acc[translationType.value] = translationType.display;
                    return acc;
                }, {});

                this.languageOptions = languages;

                this.languagesMap = languages.reduce((acc, language) => {
                    if (language.value !== null) {
                        acc[language.value] = language.display;
                    }
                    return acc;
                }, {});

                this.currenciesOptions = currencies;

                if (this.isEditing) {
                    this.translator = responses[0];
                    this.updateFinancial(responses[2]);
                    this.translatorServiceWraps = responses[1].map(translatorService => {
                        translatorService.price /= 100;

                        return {
                            id: uniqueId(),
                            service: translatorService,
                            isOpen: false
                        };
                    });
                } else {
                    this.translator = new Translator();
                    this.updateFinancial(new TranslatorFinancial());
                    this.translatorServiceWraps = [];
                }

                this.updateForm();
                this.updateTitle();

                this.state = 'ready';
            },
            () => {
                this.state = 'error';
            }
        ));
    }

    public ngOnInit () : void {

    }

    public ngOnDestroy () : void {
        this.subs.forEach(sub => sub.unsubscribe());
        this.uiService.deactivateBackButton();
    }

    public canDeactivate() : Promise<boolean> {
        return new Promise((resolve) => {
            if (!this.canEdit || this.form.pristine && !this.saveTasks.length) {
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
        this.canEdit = userData.features.can('edit:translators');
        this.dateSelectFormat = userData.settings.formats.date.select;
    }

    public switchTab(tab : Tab) : void {
        this.activeTab = tab;
    }

    public updateFinancial (financial : TranslatorFinancial) : void {
        if (!financial.placeOfBirthAddress) {
            financial.placeOfBirthAddress = new Address();
        }

        if (!financial.taxAgencyAddress) {
            financial.taxAgencyAddress = new Address();
        }

        this.translatorFinancial = financial;
    }

    public updateForm () : void {
        this.form.setValue(updateObject(this.form.getRawValue(), {
            primary: this.translator,
            financial: this.translatorFinancial
        }));

        this.canEdit ? this.form.enable() : this.form.disable();
        this.updateSSNVisibility();
    }

    public updateSSNVisibility () : void {
        const control = <FormControl>this.form.get('financial.personalNumber');
        const isHidden = (this.translatorFinancial.personalNumber || '').trim().slice(0, 3) === '***';

        if (isHidden) {
            this.ssnState = 'hidden';
            control.disable();
        } else {
            this.ssnState = 'visible';
            this.canEdit ? control.enable() : control.disable();
        }
    }

    public onShowSSN () : void {
        if (!this.isEditing || this.isSaving || this.ssnState !== 'hidden') {
            return;
        }

        const control = <FormControl>this.form.get('financial.personalNumber');

        control.disable();
        this.ssnState = 'loading';

        this.ssnSub = this.translatorsService.getTranslatorSSN(this.translator.id).subscribe(
            (ssn : string) => {
                control.setValue(ssn, { emitEvent: false });
                this.canEdit ? control.enable() : control.disable();
                this.ssnState = 'visible';
                this.ssnSub = null;
            },
            () => {
                control.disable();
                this.ssnState = 'hidden';
                this.ssnSub = null;
            }
        );

        this.addSub(this.ssnSub);
    }

    public updateTitle () : void {
        if (this.isEditing) {
            const translatorName = this.translator ? ([
                this.translator.firstName,
                this.translator.middleName,
                this.translator.lastName
            ].join(' ')) : '';

            this.titleService.setTitle('settings.translators.editor.page_title_edit', { translatorName });
        } else {
            this.titleService.setTitle('settings.translators.editor.page_title_create');
        }
    }

    public onSave () : void {
        if (!this.canEdit || this.isSaving || this.state !== 'ready') {
            return;
        }

        this.isSaving = true;

        if (this.ssnSub) {
            this.ssnSub.unsubscribe();
            this.ssnSub = null;
            this.updateSSNVisibility();
        }

        const formValue = this.form.getRawValue();
        this.translator = updateObject(this.translator, formValue.primary);
        this.translatorFinancial = updateObject(this.translatorFinancial, formValue.financial);

        // TODO: before save service * 100

        this.addSub((
            this.isEditing ?
            this.translatorsService.updateTranslator(this.translator) :
            this.translatorsService.createTranslator(this.translator)
        ).pipe(
            mergeMap(translator => {
                this.translator = translator;
                return this.translatorsService.updateFinancial(this.translator.id, this.translatorFinancial);
            }),
            mergeMap(translatorFinancial => {
                this.updateFinancial(translatorFinancial);
                const wrapsToUpdate : TranslatorServiceWrap[] = [];
                const writeRequests : Observable<any>[] = [];
                const deleteRequests : Observable<any>[] = [];

                this.saveTasks.forEach(task => {
                    if (task.action === 'delete') {
                        deleteRequests.push(this.translatorsService.deleteService(this.translator.id, task.serviceId));
                    } else {
                        const serviceWrap = this.translatorServiceWraps.find(tsw => tsw.id === task.serviceWrapId);
                        const service = cloneDeep(serviceWrap.service);
                        service.price = Math.floor(service.price * 100);
                        wrapsToUpdate.push(serviceWrap);
                        writeRequests.push(
                            task.action === 'create' ?
                            this.translatorsService.createService(this.translator.id, service) :
                            this.translatorsService.updateService(this.translator.id, service)
                        );
                    }
                });

                return (writeRequests.length || deleteRequests.length) ? forkJoin(
                    of(wrapsToUpdate),
                    zip(...writeRequests, ...deleteRequests)
                ) : of([ wrapsToUpdate, [] ]);
            }),
        ).subscribe(
            ([ wrapsToUpdate, updatedServices ] : [ TranslatorServiceWrap[], TranslatorServiceItem[] ]) => {
                wrapsToUpdate.forEach((serviceWrap, i) => {
                    const service = updatedServices[i];
                    service.price /= 100;
                    serviceWrap.service = service;
                });

                this.updateForm();
                if (!this.isEditing) {
                    this.updateTitle();
                    this.location.replaceState('/dashboard/translator/' + this.translator.id);
                    this.isEditing = true;
                }
                this.form.markAsPristine();
                this.saveTasks = [];
                this.isSaving = false;
                this.toastService.create({
                    message: [ 'settings.translators.editor.save_success__message' ]
                });
            },
            () => {
                this.isSaving = false;
                this.toastService.create({
                    message: [ 'settings.translators.editor.save_error__message' ]
                });
            }
        ));
    }

    public getCompanyServiceName (companyServiceId : number) : string {
        return (this.servicesMap[companyServiceId] || { name: '' }).name;
    }

    public getSubjectAreasName (subjectAreaId : number) : string {
        return this.langService.translate(this.subjectAreaMap[subjectAreaId]);
    }

    public getSubjectAreasNames (service : TranslatorServiceItem) : string {
        const names = [];

        service.fieldIds.forEach(id => {
            if (id in this.subjectAreaMap) {
                names.push(this.langService.translate(this.subjectAreaMap[id]));
            }
        });

        return names.join(', ');
    }

    public getTranslationTypeName (id : number) : string {
        return this.translationTypesMap[id] || '';
    }

    public getServiceUnit (companyServiceId : number) : string {
        if (!companyServiceId || companyServiceId < 1) {
            return '';
        }

        return (this.servicesMap[companyServiceId] || { unit: '' }).unit;
    }

    public onAddService () : void {
        if (!this.canEdit) {
            return;
        }

        this.serviceEditorMode = 'create';
        this.serviceWrapToEdit = {
            id: uniqueId(),
            service: new TranslatorServiceItem(),
            isOpen: false
        };
        this.onServiceEditorFiltersClear();
        this.filterSubjectArea();
        this.serviceEditor.activate();
    }

    public onEditService (serviceWrap : TranslatorServiceWrap) : void {
        if (!this.canEdit) {
            return;
        }

        this.serviceEditorMode = 'edit';
        this.serviceWrapToEdit = cloneDeep(serviceWrap);
        this.onServiceEditorFiltersClear();
        this.filterSubjectArea();
        this.serviceEditor.activate();
    }

    public onDeleteService (serviceWrap : TranslatorServiceWrap) : void {
        if (!this.canEdit) {
            return;
        }

        this.popupService.confirm({
            message: [ 'settings.translators.editor.delete_service__message' ],
        }).subscribe(({ isOk }) => {
            if (isOk) {
                if (serviceWrap.service.id) {
                    this.saveTasks.push({
                        action: 'delete',
                        serviceId: serviceWrap.service.id
                    });
                }
                deleteFromArray(this.translatorServiceWraps, serviceWrap);
            }
        });
    }

    public hideServiceEditor (byOverlay : boolean = false) : void {
        console.log(byOverlay);
        if (byOverlay) {
            return;
        }

        this.serviceEditor.deactivate().then(() => {
            this.serviceEditorMode = null;
            this.serviceWrapToEdit = null;
            this.serviceEditorFilters = null;
        });
    }

    public onServiceSubmit () : void {
        const serviceWraps = this.translatorServiceWraps;
        const serviceWrap = this.serviceWrapToEdit;

        serviceWrap.service.price = Number(serviceWrap.service.price);
        serviceWrap.service.fieldIds.sort();

        switch (this.serviceEditorMode) {
            case 'create':
                this.translatorServiceWraps.push(serviceWrap);
                break;
            case 'edit':
                const index = serviceWraps.indexOf(serviceWraps.find(sw => sw.id === serviceWrap.id));
                serviceWraps[index] = serviceWrap;
                break;
        }

        const saveTask = {
            action: serviceWrap.service.id ? 'update' : 'create',
            serviceWrapId: serviceWrap.id
        };

        const existingTask = this.saveTasks.find(st => st.serviceWrapId === serviceWrap.id);
        const existingTaskIndex = existingTask ? this.saveTasks.indexOf(existingTask) : -1;

        if (existingTaskIndex === -1) {
            this.saveTasks.push(saveTask);
        } else {
            this.saveTasks[existingTaskIndex] = saveTask;
        }

        this.hideServiceEditor();
    }

    public isServiceValid () : boolean {
        const serviceToEdit = this.serviceWrapToEdit.service;
        return !!(serviceToEdit.fieldIds.length && serviceToEdit.translationTypeId && isFloatString(String(serviceToEdit.price)));
    }

    public onServiceEditorSubjectAreaSelect (value : any) : void {
        if (!value || this.serviceWrapToEdit.service.fieldIds.indexOf(value) !== -1) {
            return;
        }

        this.subjectAreaModel = null;
        this.serviceWrapToEdit.service.fieldIds.push(value);
        this.filterSubjectArea();
    }

    public isServiceEditorClearButtonActive () : boolean {
        return !!(this.serviceEditorFilters && (this.serviceEditorFilters.from || this.serviceEditorFilters.to));
    }

    public onServiceEditorFiltersClear () : void {
        this.serviceEditorFilters = {
            from: null,
            to: null
        };

        this.filteredServiceOptions = this.serviceOptions;
    }

    public onServiceEditorFilterChange () : void {
        defer(() => {
            const { from, to } = (this.serviceEditorFilters || {
                from: null,
                to: null
            });

            console.log(from, to);

            this.filteredServiceOptions = this.serviceOptions.filter(so => {
                return !so.value || (!from || from === so.from) && (!to || to === so.to);
            });
        });
    }

    public filterSubjectArea () : void {
        if (!this.serviceWrapToEdit) {
            this.filteredSubjectAreaOptions = this.subjectAreaOptions;
            return;
        }

        const usedSubjectAreas = this.serviceWrapToEdit.service.fieldIds;

        this.filteredSubjectAreaOptions = this.subjectAreaOptions.filter(sao => {
            return !sao.value || usedSubjectAreas.indexOf(sao.value) === -1;
        });
    }

    public onDeleteSubjectArea (subjectAreaId : number) : void {
        defer(() => {
            deleteFromArray(this.serviceWrapToEdit.service.fieldIds, subjectAreaId);
            this.filterSubjectArea();
        });
    }

    public toggleServiceDetails (serviceWrap : TranslatorServiceWrap) : void {
        serviceWrap.isOpen = !serviceWrap.isOpen;
        this.hasOpenedServices = this.translatorServiceWraps.some(tsw => tsw.isOpen);
    }

    public toggleAllServiceDetails () : void {
        const hasOpened = this.hasOpenedServices;
        this.translatorServiceWraps.forEach(tsw => tsw.isOpen = !hasOpened);
        this.hasOpenedServices = !hasOpened;
    }

    public goBack () : void {
        this.router.navigateByUrl('/dashboard/translators');
    }
}
