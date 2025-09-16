import {
    Component, ElementRef, HostListener,
    OnChanges, OnDestroy, OnInit,
    SimpleChanges, ViewChild,
    ViewEncapsulation
} from '@angular/core';
import { Location} from '@angular/common';
import {FileUploader} from '../../../widgets/file-uploader/file-uploader.class';
import {
    Attachment, ClientCompany,
    CompanyServiceItem,
    Contact, Offer,
    OfferServiceItem,
    OffersService, ShippingAddress
} from '../../../services/offers.service';
import {ActivatedRoute, Router} from '@angular/router';
import {UiService} from '../../../services/ui.service';
import {cloneDeep} from 'lodash';
import {PopupComponent} from '../../../widgets/popup/popup.component';
import {DeviceService, ViewportBreakpoint} from '../../../services/device.service';
import {UserData, UserService} from '../../../services/user.service';
import {TitleService} from '../../../services/title.service';
import {Subscription, zip} from 'rxjs';
import {LangService} from '../../../services/lang.service';
import {
    defer,
    deleteFromArray,
    divFloat,
    isCopyingSupported, isEmailValid,
    mulFloat,
    setSelectionRange,
    str2regexp, trimProperties
} from '../../../lib/utils';
import {ConfirmDiscard} from '../../../guards/discard.guard';
import {PopupService} from '../../../services/popup.service';
import {FilesService} from '../../../services/file.service';
import {Rate, RatesService} from '../../../services/rates.service';
import {FormBuilder, FormGroup} from '@angular/forms';
import {SidebarComponent} from '../../shared/sidebar/sidebar.component';
import {Company, CompanyService, Coordinator} from '../../../services/company.service';
import {Client, ClientsService} from '../../../services/client.service';
import {ProjectsService} from '../../../services/projects.service';
import {OfferCurrency} from '../../../services/currencies.service';
import {ClientComponent} from '../clients/client.component';
import {ToastService} from '../../../services/toast.service';
import {CalcService, RoundingRule} from '../../../services/calc.service';

type Tab = 'details' | 'services' | 'documents' | 'shipping' | 'transactions' | 'history';
type Layout = 'editor' | 'company-selector' | 'service-selector' | 'client-editor';




@Component({
    selector: 'offer-editor',
    templateUrl: './offer.component.html',
    styleUrls: [ './offer.component.scss' ],
    encapsulation: ViewEncapsulation.None,
    // changeDetection: ChangeDetectionStrategy.OnPush,
    host: {
        'class': 'offer-editor',
        '[class.offer-editor_has-tabs]': "layout === 'editor'"
    }
})
export class OfferComponent implements OnInit, OnDestroy, OnChanges, ConfirmDiscard {
    public uploader : FileUploader = null;

    public uploadErrors : string[] = [];

    public uploadQueueSize : number = 0;

    public uploadedFilesCount : number = 0;

    public uploadingProgress : number = 0;

    public areUploadingErrorsVisible : boolean = false;

    public isDropzoneOver : boolean = false;

    public uploaded : string[] = [];

    // -------------------------

    public viewportBreakpoint : ViewportBreakpoint = null;

    public offerToLoad : string = null;

    public unbillableServicesStates : Map<OfferServiceItem, any> = null;

    public editorState : 'loading' | 'error' | 'editor' = 'loading';

    public editorMode : 'create' | 'edit' = 'create';

    public canEdit : boolean = false;

    public canCreateService : boolean = false;

    public canCreateClient : boolean = false;

    public dateDisplayFormat : string = 'd MMM y HH:mm';

    public coordinatorOptions : any[] = null;

    public statusOptions : any[] = null;

    public priorityOptions : any[] = null;

    public deliveryTypeOptions : any[] = null;

    public subjectAreaOptions : any[] = null;

    public translationTypeOptions : any[] = null;

    // Always must be non-null
    public currencyOptions : any[] = null;

    public currencies : OfferCurrency[] = null;

    public taxOptions : any[] = null;

    public taxes : any[] = null;

    public directionOptions : any[] = [
        {
            display: 'filters.any',
            value: null
        }
    ];

    public rateOptions : any[] = [
        {
            display: 'filters.any',
            value: null
        }
    ];

    public unitOptions : any[] = [
        {
            display: 'filters.any',
            value: null
        }
    ];

    public currentDate : Date = null;

    public attachedEmailFrom : string = null;

    public offer : Offer = null;

    public currency : OfferCurrency = null;

    public totalNet : number = 0;

    public totalGross : number = 0;

    public contacts : Contact[] = null;

    public subs : Subscription[] = [];

    // attachmentUuid -> presignedUrl
    public attachmentsUrls : any = {};

    // serviceId -> Attachment[]
    public attachmentsMap : any = {};

    public linkableAttachments : any[] = [];

    public serviceToLink : OfferServiceItem = null;

    public emailPreviewHTML : string = null;

    public emailPreviewState : 'empty' | 'contain' | 'error' = 'empty';

    public emailIframeHeight : number = 150;

    public IsInstructionsEditorEnabled : boolean = false;

    public instructionsEditorHeight : number = 0;

    public fileToEditComment : any = null;

    public fileCommentTypeToEdit : any = null;

    // ------------------

    public transactionsTotalAmount : number = null;
    public transactionsTotalAmountCurrency : string = null;
    public transaction : any = null;
    public transactions : any[] = [];
    public transactionsState : 'loading' | 'empty' | 'error' | 'ready' = 'loading';

    public canViewHistory : boolean = false;
    public isHistoryTabHintVisible : boolean = false;
    public isHistoryActual : boolean = false;
    public historyRecords : any[] = [];
    public historyState : 'loading' | 'empty' | 'error' | 'ready' = 'loading';

    public networkProcess : 'loading-company-profile' | 'saving-offer' | 'project-popup-loading' | 'create-project' | 'create-transaction' = null;

    public personPrefixOptions : any[] = [
        {
            display: '',
            value: ''
        },
        {
            display: 'offers.editor.prefix_mr__select_option',
            value: 'offers.editor.prefix_mr__select_option'
        },
        {
            display: 'offers.editor.prefix_mrs__select_option',
            value: 'offers.editor.prefix_mrs__select_option'
        },
        {
            display: 'offers.editor.prefix_dr__select_option',
            value: 'offers.editor.prefix_dr__select_option'
        },
        {
            display: 'offers.editor.prefix_sir__select_option',
            value: 'offers.editor.prefix_sir__select_option'
        }
    ];

    public IsChanged : boolean = false;

    public set isChanged (isChanged : boolean) {
        this.IsChanged = this.canEdit && isChanged;
    }

    public get isChanged () : boolean {
        return this.IsChanged;
    }

    public IsPublicFieldsHighlighted : boolean = null;

    public set isPublicFieldsHighlighted (isHighlighted : boolean) {
        localStorage.setItem(
            'isOfferPublicFieldsHighlighted',
            String(this.IsPublicFieldsHighlighted = isHighlighted)
        );
    }

    public get isPublicFieldsHighlighted () : boolean {
        return (
            this.IsPublicFieldsHighlighted == null ?
                (this.IsPublicFieldsHighlighted = localStorage.getItem('isOfferPublicFieldsHighlighted') === 'true') :
                this.IsPublicFieldsHighlighted
        );
    }

    public Layout : Layout = 'editor';

    public set layout (layout : Layout) {
        if (!this.canEdit) {
            return;
        }

        this.Layout = layout;

        if (layout == 'company-selector') {
            this.onCompanySelectorActivated();
        } else if (layout == 'service-selector') {
            this.onServiceSelectorActivated();
        }

        this.scrollToTop();
    }

    public get layout () : Layout {
        return this.Layout;
    }


    // ViewChild
    // --------------------------------------------

    public _sidebarEl : SidebarComponent = null;

    @ViewChild('sidebar')
    public set sidebarEl (sidebarEl : SidebarComponent) {
        defer(() => this._sidebarEl = sidebarEl);
    }

    public get sidebarEl () : SidebarComponent {
        return this._sidebarEl;
    }

    @ViewChild('uploaderInput')
    public uploaderInput : ElementRef = null;

    @ViewChild('instructionsText')
    public instructionsText = null;

    @ViewChild('instructionsEditor')
    public instructionsEditor = null;

    @ViewChild('fileCommentEditor')
    public fileCommentEditor : any = null;

    @ViewChild('settingsPopup')
    public settingsPopup : PopupComponent;

    @ViewChild('emailPopup')
    public emailPopup : PopupComponent;

    @ViewChild('projectPopup')
    public projectPopup : PopupComponent;

    @ViewChild('attachmentsPopup')
    public attachmentsPopup : PopupComponent;

    @ViewChild('quotePopup')
    public quotePopup : PopupComponent;

    @ViewChild('billingPopup')
    public billingPopup : PopupComponent;

    @ViewChild('transactionPopup')
    public transactionPopup : PopupComponent;

    @ViewChild('billingFormMessage')
    public billingFormMessageRef : ElementRef = null;

    @ViewChild('quotePreview')
    public quotePreviewRef : ElementRef = null;

    @ViewChild('emailPreviewIframe')
    public emailPreviewIframe : ElementRef = null;

    @ViewChild('clientEditor')
    public clientEditor : ClientComponent = null;

    // ----------------------------------

    public billingForm : any = null;

    public billingFormErrors : any = {};

    public sendingBillingError : string = null;

    public isEmailVerificationCodeSent : boolean = false;

    // ----------------------------------

    public companyProfile : Company = null;

    public clientProfile : Client = null;

    public isCopyingSupported : boolean = false;

    // ----------------------------------

    public projectCoordinatorOptions : any[] = null;

    public projectCoordinatorParams : any = null;

    // ----------------------------------

    public isActionsMenuActive : boolean = false;

    public roundingRule : RoundingRule;

    public isClientSelected : boolean = false;

    constructor (
        private formBuilder : FormBuilder,
        private location : Location,
        private route : ActivatedRoute,
        private router : Router,
        private deviceService : DeviceService,
        private companyService : CompanyService,
        private clientsService : ClientsService,
        private uiService : UiService,
        private offersService : OffersService,
        private projectsService : ProjectsService,
        private titleService : TitleService,
        private userService : UserService,
        private langService : LangService,
        private popupService : PopupService,
        private filesService : FilesService,
        private toastService : ToastService,
        private calcService : CalcService,
        private ratesService : RatesService
    ) {}

    public ngOnInit () : void {
        this.route.params.subscribe((params) => {
            if (params.key) {
                this.cleanup();
                this.init(params.key);
            }
        });
    }

    public init (offerKey : string) : void {
        this.uploader = null;
        this.uploadErrors = [];
        this.uploadQueueSize = 0;
        this.uploadedFilesCount = 0;
        this.uploadingProgress = 0;
        this.areUploadingErrorsVisible = false;
        this.isDropzoneOver = false;
        this.uploaded = [];
        this.viewportBreakpoint = null;
        this.offerToLoad = null;
        this.unbillableServicesStates = null;
        this.editorState = 'loading';
        this.editorMode = 'create';
        this.canEdit = false;
        this.canCreateService = false;
        this.canCreateClient = false;
        this.dateDisplayFormat = 'd MMM y HH:mm';
        this.coordinatorOptions = null;
        this.statusOptions = null;
        this.priorityOptions = null;
        this.deliveryTypeOptions = null;
        this.subjectAreaOptions = null;
        this.translationTypeOptions = null;
        this.currencyOptions = null;
        this.currencies = null;
        this.taxOptions = null;
        this.taxes = null;
        this.currentDate = null;
        this.attachedEmailFrom = null;
        this.offer = null;
        this.currency = null;
        this.totalNet = 0;
        this.totalGross = 0;
        this.contacts = null;
        this.subs = [];
        this.attachmentsUrls = {};
        this.attachmentsMap = {};
        this.linkableAttachments = [];
        this.serviceToLink = null;
        this.emailPreviewHTML = null;
        this.emailPreviewState = 'empty';
        this.emailIframeHeight = 150;
        this.IsInstructionsEditorEnabled = false;
        this.instructionsEditorHeight = 0;
        this.fileToEditComment = null;
        this.fileCommentTypeToEdit = null;
        this.transactionsTotalAmount = null;
        this.transactionsTotalAmountCurrency = null;
        this.transaction = null;
        this.transactions = [];
        this.transactionsState = 'loading';
        this.canViewHistory = false;
        this.isHistoryTabHintVisible = false;
        this.isHistoryActual = false;
        this.historyRecords = [];
        this.historyState = 'loading';
        this.networkProcess = null;
        this.IsChanged = false;
        this.IsPublicFieldsHighlighted = null;
        this.Layout = 'editor';
        this.billingForm = null;
        this.billingFormErrors = {};
        this.sendingBillingError = null;
        this.isEmailVerificationCodeSent = false;
        this.companyProfile = null;
        this.clientProfile = null;
        this.isCopyingSupported = false;
        this.projectCoordinatorOptions = null;
        this.projectCoordinatorParams = null;
        this.isActionsMenuActive = false;
        this.roundingRule = null;
        this.isClientSelected = false;

        this.directionOptions = [
            {
                display: 'filters.any',
                value: null
            }
        ];

        this.rateOptions = [
            {
                display: 'filters.any',
                value: null
            }
        ];

        this.unitOptions = [
            {
                display: 'filters.any',
                value: null
            }
        ];

        // -------------------------------------------------------------------

        this.currentDate = new Date();
        this.unbillableServicesStates = new Map<OfferServiceItem, any>();
        this.viewportBreakpoint = this.deviceService.viewportBreakpoint;

        this.addSub(
            this.deviceService.onResize.subscribe((message) => {
                if (message.breakpointChange) {
                    this.viewportBreakpoint = this.deviceService.viewportBreakpoint;
                }

                this.isActionsMenuActive = false;
                // this.updateEmailPopupSize();
            })
        );

        this.addSub(
            this.uiService.activateBackButton().subscribe(() => {
                switch (this.layout) {
                    case 'service-selector':
                        this.onServiceSelectorSubmit(false);
                        break;
                    case 'client-editor':
                        // TODO:
                        this.clientEditor.canDeactivate().then(isOk => {
                            if (isOk) {
                                this.clientEditor.goBack();
                            }
                        });
                        break;
                    case 'company-selector':
                        this.layout = 'editor';
                        break;
                    case 'editor':
                        this.goBack();
                        break;
                }
            })
        );

        // const offerKey : string = this.offerToLoad = (this.route.snapshot.params['key'] || '').trim() || null;
        this.offerToLoad = offerKey;

        if (!offerKey) {
            this.editorState = 'error';
            return;
        }

        let offerizeData : any = this.offersService.offerizeData;

        if (offerizeData && offerizeData.offerKey != offerKey) {
            offerizeData = null;
        }

        const fromAddress : string = offerizeData && offerizeData.fromAddress || null;

        if (offerKey == 'create') {
            this.editorMode = 'create';
            this.titleService.setTitle('offers.editor.page_title_create');
        } else {
            this.editorMode = 'edit';
            this.titleService.setTitle('offers.editor.page_title_edit', { offerKey });
        }

        this.applyUserData(this.userService.getUserData());
        this.isCopyingSupported = isCopyingSupported();

        this.addSub(zip(
            this.offersService.fetchOffer(offerKey, fromAddress),
            this.langService.fetchLanguages(),
            this.companyService.fetchCalcRule()
        ).subscribe(
            ([ editorData, langs, roundingRule ]) => {
                this.roundingRule = <RoundingRule>roundingRule;

                // Coordinators
                this.coordinatorOptions = editorData.coordinators.reduce((acc, coordinator) => {
                    if (coordinator.active || editorData.offer?.coordinatorId === coordinator.id) {
                        acc.push({
                            value: coordinator.id,
                            display: [
                                coordinator.firstName,
                                coordinator.lastName
                            ].join(' '),
                            isActive: coordinator.active
                        });
                    }
                    return acc;
                }, []);

                // Statuses
                this.statusOptions = editorData.statuses.map(status => {
                    return {
                        key: status.key,
                        value: status.id,
                        display: 'offers.statuses.' + status.key
                    };
                });

                // Priorities
                this.priorityOptions = editorData.priorities.map(priority => {
                    let display = priority.name;

                    if (priority.key) {
                        const key = 'priority.' + priority.key.replace(/\./g, '_');
                        const message = this.langService.translate(key);
                        display = message === key ? priority.key : message;
                    }

                    return {
                        value: priority.id,
                        display
                    };
                });

                // Delivery Type
                this.deliveryTypeOptions = editorData.deliveryTypes.map(deliveryType => {
                    let display = deliveryType.name;

                    if (deliveryType.key) {
                        const key = 'delivery_type.' + deliveryType.key.replace(/\./g, '_');
                        const message = this.langService.translate(key);
                        display = message === key ? deliveryType.key : message;
                    }

                    return {
                        value: deliveryType.id,
                        display
                    };
                });

                // Subject Areas
                this.subjectAreaOptions = editorData.fields.map(subjectArea => {
                    let display = subjectArea.name;

                    if (subjectArea.key) {
                        const key = 'subject_area.' + subjectArea.key.replace(/\./g, '_');
                        const message = this.langService.translate(key);
                        display = message === key ? subjectArea.key : message;
                    }

                    return {
                        value: subjectArea.id,
                        display
                    };
                });

                // Translation Types
                this.translationTypeOptions = editorData.translationTypes.map(translationType => {
                    let display = translationType.name;

                    if (translationType.key) {
                        const key = 'translation_type.' + translationType.key.replace(/\./g, '_');
                        const message = this.langService.translate(key);
                        display = message === key ? translationType.key : message;
                    }

                    return {
                        value: translationType.id,
                        display
                    };
                });

                // Currencies
                this.currencyOptions = editorData.currencies.map(currency => {
                    return {
                        value: currency.key,
                        display: currency.name
                    };
                });

                this.currencies = editorData.currencies.map(currency => new OfferCurrency(currency));

                // Taxes
                this.taxOptions = editorData.taxes.map(tax => {
                    return {
                        value: tax.id,
                        display: tax.name
                    };
                });

                this.taxes = editorData.taxes;

                // Languages
                this.directionOptions = [
                    ...this.directionOptions,
                    ...langs
                ];

                this.attachedEmailFrom = editorData.origin && editorData.origin.from || null;

                this.offer = this.getOfferInstance(editorData.offer);
                this.isClientSelected = !!(this.offer.client && this.offer.client.id);

                this.calculateServicesValues();

                // Contacts
                this.contacts = [
                    new Contact({
                        id: 0,
                        fullName: '',
                        title: '',
                        email: fromAddress || '',
                        phone: '',
                        fax: '',
                        position: '',
                        notes: '',
                        primary: false,
                        inactive: false
                    })
                ];

                // after getOfferInstance
                this.updateContacts(editorData.contacts, 'current');

                // Attachments
                this.offerizeAttachments(offerizeData && offerizeData.attachments || []);

                // [async] fetch attachments urls on the documents tab
                // after offerizeAttachments
                this.fetchAttachmentsUrls();

                // Attachments to service
                // after offerizeAttachments
                this.createAttachmentsMap();

                // [async] fetch email preview HTML
                this.fetchEmailHtml(offerKey)
                    .then(html => {
                        this.emailPreviewHTML = html;
                        this.emailPreviewState = html ? 'contain' : 'empty';
                    }).catch((reason : any) => {
                        console.warn(`Can't load email preview:`, reason);
                        this.emailPreviewHTML = null;
                        this.emailPreviewState = 'error';
                    });/*.then(() => {
                        this.emailPreviewHTML = `<div class="m_7374478547067792330clean-body" style="margin:0;padding:0;background-color:#ffffff"><div id="m_7374478547067792330emailPreHeader" style="opacity:0;color:transparent;line-height:0;font-size:0px;overflow:hidden;border-width:0;display:none!important"><span style="font-size:11pt;font-family:Arial;color:#000000;font-weight:400">Check out all the latest features and download today.</span>‌&nbsp;‌&nbsp;‌&nbsp;‌&nbsp;‌&nbsp;‌&nbsp;‌&nbsp;‌&nbsp;‌&nbsp;‌&nbsp;‌&nbsp;‌&nbsp;‌<wbr>&nbsp;‌&nbsp;‌&nbsp;‌&nbsp;‌&nbsp;‌&nbsp;‌&nbsp;‌&nbsp;‌&nbsp;‌&nbsp;‌&nbsp;‌&nbsp;‌&nbsp;‌&nbsp;‌&nbsp;‌<wbr>&nbsp;‌&nbsp;‌&nbsp;‌&nbsp;‌&nbsp;‌&nbsp;‌&nbsp;‌&nbsp;‌&nbsp;‌&nbsp;‌&nbsp;‌&nbsp;‌&nbsp;‌&nbsp;‌&nbsp;‌<wbr>&nbsp;‌&nbsp;‌&nbsp;‌&nbsp;‌&nbsp;‌&nbsp;‌&nbsp;‌&nbsp;‌&nbsp;‌&nbsp;‌&nbsp;‌&nbsp;‌&nbsp;‌&nbsp;‌&nbsp;‌<wbr>&nbsp;‌&nbsp;‌&nbsp;‌&nbsp;‌&nbsp;‌&nbsp;‌&nbsp;‌&nbsp;‌&nbsp; ‌&nbsp;‌&nbsp;‌&nbsp;‌&nbsp;‌&nbsp;‌&nbsp;‌&nbsp;‌&nbsp;‌&nbsp;‌&nbsp;‌&nbsp;‌&nbsp;</div>  <table class="m_7374478547067792330nl-container" style="table-layout:fixed;vertical-align:top;min-width:320px;Margin:0 auto;border-spacing:0;border-collapse:collapse;background-color:#ffffff;width:100%" cellpadding="0" cellspacing="0" role="presentation" width="100%" bgcolor="#FFFFFF" valign="top"> <tbody> <tr style="vertical-align:top" valign="top"> <td style="word-break:break-word;vertical-align:top" valign="top">  <div style="background-color:transparent"> <div class="m_7374478547067792330mktEditable" id="m_7374478547067792330knak-block-0-5d6fc7564c6af"> <div class="m_7374478547067792330block-grid" style="Margin:0 auto;min-width:320px;max-width:600px;word-wrap:break-word;word-break:break-word;background-color:#ffffff"> <div style="border-collapse:collapse;display:table;width:100%;background-color:#ffffff">   <div class="m_7374478547067792330col m_7374478547067792330num12" style="min-width:320px;max-width:600px;display:table-cell;vertical-align:top;width:598px"> <div style="width:100%!important">  <div style="border-top:0px solid transparent;border-left:1px solid #555555;border-bottom:1px solid #555555;border-right:1px solid #555555;padding-top:0px;padding-bottom:0px;padding-right:0px;padding-left:0px">  <div class="m_7374478547067792330img-container m_7374478547067792330center m_7374478547067792330autowidth m_7374478547067792330fullwidth" align="center" style="padding-right:0px;padding-left:0px"> <a href="https://info.unrealengine.com/JF3JDE0w4T0kfCQ0aS001f0" target="_blank" data-saferedirecturl="https://www.google.com/url?q=https://info.unrealengine.com/JF3JDE0w4T0kfCQ0aS001f0&amp;source=gmail&amp;ust=1568554142210000&amp;usg=AFQjCNF3VaKNk6oA7KwkB63utovneDli5A"> <img class="m_7374478547067792330center m_7374478547067792330autowidth m_7374478547067792330fullwidth CToWUd" align="center" border="0" src="https://ci4.googleusercontent.com/proxy/lArYQVBgLTDQMRkXj7SisSXnrDYps5qCfwnHY1JazB7BElnAj28tejFea_DitPs-fVxM1BaUU_ls5Cmtsq20Mao7tYy5_KlAxV3c9UMLM8LnWnoaxc2-B0at2YJd4uHHQ2Up3yb9BGsjrSreAwIvPUe6h7yShJiV8nNj0Hmpx7pKjFS3g0-C_lPwhVdZZk8oad4=s0-d-e1-ft#https://s3.amazonaws.com/client-data.knak.io/production/email_assets/5b0ee08673f01/d1KwppANDkW7UzrEQQb6IJDh9IvzMRpJZrZxv28F.gif" alt="Unreal Engine Logo" title="Unreal Engine Logo" style="text-decoration:none;height:auto;border:none;width:100%;max-width:598px;display:block" width="598"></a>  </div> <div class="m_7374478547067792330img-container m_7374478547067792330center m_7374478547067792330autowidth m_7374478547067792330fullwidth" align="center" style="padding-right:0px;padding-left:0px"> <a href="https://info.unrealengine.com/JF3JDE0w4T0kfCQ0aS001f0" target="_blank" data-saferedirecturl="https://www.google.com/url?q=https://info.unrealengine.com/JF3JDE0w4T0kfCQ0aS001f0&amp;source=gmail&amp;ust=1568554142210000&amp;usg=AFQjCNF3VaKNk6oA7KwkB63utovneDli5A"> <img class="m_7374478547067792330center m_7374478547067792330autowidth m_7374478547067792330fullwidth CToWUd" align="center" border="0" src="https://ci6.googleusercontent.com/proxy/PkP0mWt56vXxAO4E8ry2wiE6QNoNH3LXbtG4RLkBOyjG-RwY3EFgTqdIqAp86cKoMoHwjUBQOv7ZBJ4Y0frtnUWgjWI5j5OFNXfwllms2lj7GXJa0pYz7beYI7u3wOEZ59dM7w=s0-d-e1-ft#https://ue.unrealengine.com/rs/754-DFT-709/images/Engine_Email_4.23_Emergence.jpg" alt="Unreal Engine 4.23" title="Unreal Engine 4.23" style="text-decoration:none;height:auto;border:none;width:100%;max-width:598px;display:block" width="598"></a>  </div>  <div style="color:#555555;font-family:'Roboto',Tahoma,Verdana,Segoe,sans-serif;line-height:150%;padding-top:15px;padding-right:45px;padding-bottom:10px;padding-left:45px"> <div style="font-size:12px;line-height:18px;font-family:'Roboto',Tahoma,Verdana,Segoe,sans-serif;color:#555555"> <p style="font-size:14px;line-height:22px;margin:0"><span style="font-size:15px;color:#333333">We’re pleased to announce that Unreal Engine 4.23 is now available for download, with a host of new features for game development, film and television production, live entertainment events, visualization, and more. Here’s a taste of what’s in store.</span></p> </div> </div>   <div style="color:#555555;font-family:'Roboto',Tahoma,Verdana,Segoe,sans-serif;line-height:150%;padding-top:15px;padding-right:45px;padding-bottom:10px;padding-left:45px"> <div style="font-family:'Roboto',Tahoma,Verdana,Segoe,sans-serif;font-size:12px;line-height:18px;color:#555555"> <p style="font-size:14px;line-height:21px;margin:0"><strong><span style="color:#333333;font-size:14px;line-height:21px"><span style="font-size:14px;line-height:21px"><span style="font-size:18px;line-height:27px">Enhanced ray tracin</span></span><span style="font-size:14px;line-height:21px"><span style="font-size:14px;line-height:21px"><span style="font-size:18px;line-height:27px">g</span></span></span></span></strong></p> <p style="font-size:12px;line-height:22px;margin:0"><span style="font-size:15px;color:#333333">First introduced in UE 4.22, ray tracing has received numerous enhancements to improve stability and performance, and to support additional materials and geometry types including landscape geometry, instanced static meshes, procedural meshes, and Niagara sprite particles.</span></p> </div> </div>   <div style="color:#555555;font-family:'Roboto',Tahoma,Verdana,Segoe,sans-serif;line-height:150%;padding-top:15px;padding-right:45px;padding-bottom:15px;padding-left:45px"> <div style="font-family:'Roboto',Tahoma,Verdana,Segoe,sans-serif;font-size:12px;line-height:18px;color:#555555"> <p style="font-size:14px;line-height:21px;margin:0"><span style="color:#333333;font-size:14px;line-height:21px"><strong><span style="font-size:14px;line-height:21px"><span style="font-size:18px;line-height:27px">Chaos physics and destruction</span></span></strong></span></p> <p style="font-size:12px;line-height:22px;margin:0"><span style="font-size:15px;color:#333333">Fracture, shatter, and demolish massive-scale scenes at cinematic quality with unprecedented levels of artistic control! Simulate in real time, or pre-cache larger sims for real-time playback. The Chaos system is integrated with the Niagara VFX system for secondary effects such as dust and smoke.</span></p> </div> </div>  <div class="m_7374478547067792330img-container m_7374478547067792330center m_7374478547067792330autowidth m_7374478547067792330fullwidth" align="center" style="padding-right:0px;padding-left:0px"> <a href="https://info.unrealengine.com/JF3JDE0w4T0kfCQ0aS001f0" target="_blank" data-saferedirecturl="https://www.google.com/url?q=https://info.unrealengine.com/JF3JDE0w4T0kfCQ0aS001f0&amp;source=gmail&amp;ust=1568554142210000&amp;usg=AFQjCNF3VaKNk6oA7KwkB63utovneDli5A"> <img class="m_7374478547067792330center m_7374478547067792330autowidth m_7374478547067792330fullwidth CToWUd" align="center" border="0" src="https://ci3.googleusercontent.com/proxy/ctaYkq85ATe8w_S4SFWGWeQitOCmuTBv57FIzdUZK75fnq3xLJYQhH8JGO4qOjAc4UHwlHI8jvFMerByGBglzoJZw7L2trq8Z35rgnTRouAlBSraWHSISZa4jfrFqcSU=s0-d-e1-ft#https://ue.unrealengine.com/rs/754-DFT-709/images/Engine_Email_4.23_Chaos.jpg" alt="Unreal Engine Chaos System" title="Unreal Engine Chaos System" style="text-decoration:none;height:auto;border:none;width:100%;max-width:598px;display:block" width="598"></a>  </div>  <div style="color:#555555;font-family:'Roboto',Tahoma,Verdana,Segoe,sans-serif;line-height:150%;padding-top:15px;padding-right:45px;padding-bottom:10px;padding-left:45px"> <div style="font-family:'Roboto',Tahoma,Verdana,Segoe,sans-serif;font-size:12px;line-height:18px;color:#555555"> <p style="font-size:14px;line-height:27px;margin:0"><span style="font-size:18px;color:#333333"><strong><span style="font-size:18px;line-height:27px">Virtual texturing</span></strong></span></p> <p style="font-size:12px;line-height:22px;margin:0"><span style="font-size:15px;color:#333333">Unreal Engine 4.23 introduces both Streaming and Runtime Virtual Texturing—where large textures are tiled and only the visible tiles loaded—respectively reducing texture memory overhead for light maps and detailed artist-created textures, and improving rendering performance for procedural and layered materials.&nbsp;</span></p> </div> </div>   <div style="color:#555555;font-family:'Roboto',Tahoma,Verdana,Segoe,sans-serif;line-height:150%;padding-top:15px;padding-right:45px;padding-bottom:10px;padding-left:45px"> <div style="font-size:12px;line-height:18px;font-family:'Roboto',Tahoma,Verdana,Segoe,sans-serif;color:#555555"> <p style="font-size:14px;line-height:21px;margin:0"><strong><span style="font-size:14px;line-height:21px;color:#333333"><span style="font-size:14px;line-height:21px"><span style="font-size:18px;line-height:27px">Next-gen virtual production tools</span></span></span></strong></p> <p style="font-size:14px;line-height:22px;margin:0"><span style="font-size:15px;color:#333333">Now you can achieve final shots live on set, with LED walls powered by nDisplay that not only place real-world actors and props within UE4 environments, but also light and cast reflections onto them. We’ve also added VR scouting tools, enhanced Live Link real-time data streaming, and the ability to remotely control UE4 from an iPad or other device.</span></p> </div> </div>  <div class="m_7374478547067792330img-container m_7374478547067792330center m_7374478547067792330autowidth m_7374478547067792330fullwidth" align="center" style="padding-right:0px;padding-left:0px"> <a href="https://info.unrealengine.com/JF3JDE0w4T0kfCQ0aS001f0" target="_blank" data-saferedirecturl="https://www.google.com/url?q=https://info.unrealengine.com/JF3JDE0w4T0kfCQ0aS001f0&amp;source=gmail&amp;ust=1568554142211000&amp;usg=AFQjCNHKUd3tzMeI7UOQiSGdeizPB-o8Yw"> <img class="m_7374478547067792330center m_7374478547067792330autowidth m_7374478547067792330fullwidth CToWUd" align="center" border="0" src="https://ci3.googleusercontent.com/proxy/WjoPyswo57STTAiDY2d3BgKjYB08LVKx7aHuEaPzYir5t5LGXstMugjwXQ0riYl8xIitHpF8NYDckOijEUeYQJsHrZSHM51cHs9wCZMWasJYP-FcvBXh0_QSA8VoEHSzy2VthfH22rCVtMuV=s0-d-e1-ft#https://ue.unrealengine.com/rs/754-DFT-709/images/Engine_Email_4.23_VirtualProduction.jpg" alt="Next-Gen Virtual Production" title="Next-Gen Virtual Production" style="text-decoration:none;height:auto;border:none;width:100%;max-width:598px;display:block" width="598"></a>  </div>  <div style="color:#555555;font-family:'Roboto',Tahoma,Verdana,Segoe,sans-serif;line-height:150%;padding-top:15px;padding-right:45px;padding-bottom:10px;padding-left:45px"> <div style="font-family:'Roboto',Tahoma,Verdana,Segoe,sans-serif;font-size:12px;line-height:18px;color:#555555"> <p style="font-size:14px;line-height:27px;margin:0"><span style="font-size:18px;color:#333333"><strong><span style="font-size:18px;line-height:27px">Unreal Insights</span></strong></span></p> <p style="font-size:12px;line-height:22px;margin:0"><span style="font-size:15px;color:#333333">The Unreal Insights system collects, analyzes, and visualizes data on UE4 behavior for profiling, helping you understand engine performance either live or from pre-recorded sessions. As well as tracking various default sub-systems and events, you can also add your own code annotations to generate trace events.</span></p> </div> </div>   <div style="color:#555555;font-family:'Roboto',Tahoma,Verdana,Segoe,sans-serif;line-height:150%;padding-top:15px;padding-right:45px;padding-bottom:10px;padding-left:45px"> <div style="font-family:'Roboto',Tahoma,Verdana,Segoe,sans-serif;font-size:12px;line-height:18px;color:#555555"> <p style="font-size:14px;line-height:21px;margin:0"><strong><span style="font-size:14px;line-height:21px;color:#333333"><span style="font-size:18px;line-height:27px">HoloLens 2 support</span></span></strong></p> <p style="font-size:12px;line-height:22px;margin:0"><span style="font-size:15px;color:#333333">Support for HoloLens 2, initially released as Beta in May, is now production-ready. Features include streaming and native deployment, emulator support, finger tracking, gesture recognition, meshing, voice input, spatial anchor pinning, and more.&nbsp;</span></p> </div> </div>   <div style="color:#555555;font-family:'Roboto',Tahoma,Verdana,Segoe,sans-serif;line-height:150%;padding-top:15px;padding-right:45px;padding-bottom:10px;padding-left:45px"> <div style="font-family:'Roboto',Tahoma,Verdana,Segoe,sans-serif;font-size:12px;line-height:18px;color:#555555"> <p style="font-size:12px;line-height:22px;margin:0"><span style="font-size:15px;color:#333333">You can see all of the new features in the <a style="text-decoration:underline;color:#0068a5" href="https://info.unrealengine.com/gx0QfkJ0E304FT0aD100gCS" rel="noopener" target="_blank" data-saferedirecturl="https://www.google.com/url?q=https://info.unrealengine.com/gx0QfkJ0E304FT0aD100gCS&amp;source=gmail&amp;ust=1568554142211000&amp;usg=AFQjCNHEKWewUB7kr5S-Es3G0OaW8i9ZDg">release notes</a>. If you’re an existing Unreal Engine user, you can download UE 4.23 from the Launcher. If you’ve yet to get your feet wet, there’s never been a better time to start your journey; click the link below to get started. Either way, we hope you enjoy our latest version!&nbsp;</span></p> </div> </div>  <div class="m_7374478547067792330button-container" align="center" style="padding-top:10px;padding-right:10px;padding-bottom:10px;padding-left:10px"> <a href="https://info.unrealengine.com/HD0030E0kShQCTf1J4F00ya" style="text-decoration:none;display:inline-block;color:#ffffff;background-color:#3aaee0;border-radius:4px;width:auto;width:auto;border-top:1px solid #3aaee0;border-right:1px solid #3aaee0;border-bottom:1px solid #3aaee0;border-left:1px solid #3aaee0;padding-top:5px;padding-bottom:5px;font-family:Arial,sans-serif;text-align:center;word-break:keep-all" target="_blank" data-saferedirecturl="https://www.google.com/url?q=https://info.unrealengine.com/HD0030E0kShQCTf1J4F00ya&amp;source=gmail&amp;ust=1568554142211000&amp;usg=AFQjCNFOsnODTgN_gHO7iLV5Ghru6h37kA"><span style="padding-left:20px;padding-right:20px;font-size:16px;display:inline-block"> <span style="font-size:16px;line-height:32px"><strong>GET STARTED</strong></span> </span></a>  </div> <table class="m_7374478547067792330divider" border="0" cellpadding="0" cellspacing="0" width="100%" style="table-layout:fixed;vertical-align:top;border-spacing:0;border-collapse:collapse;min-width:100%" role="presentation" valign="top"> <tbody> <tr style="vertical-align:top" valign="top"> <td class="m_7374478547067792330divider_inner" style="word-break:break-word;vertical-align:top;min-width:100%;padding-top:10px;padding-right:10px;padding-bottom:10px;padding-left:10px" valign="top"> <table class="m_7374478547067792330divider_content" border="0" cellpadding="0" cellspacing="0" width="100%" style="table-layout:fixed;vertical-align:top;border-spacing:0;border-collapse:collapse;border-top:1px solid #bbbbbb;width:100%" align="center" role="presentation" valign="top"> <tbody> <tr style="vertical-align:top" valign="top"> <td style="word-break:break-word;vertical-align:top" valign="top"><span></span> </td> </tr> </tbody> </table> </td> </tr> </tbody> </table>  <div style="color:#ffffff;font-family:Arial,sans-serif;line-height:120%;padding-top:10px;padding-right:10px;padding-bottom:10px;padding-left:10px"> <div style="font-family:Arial,sans-serif;font-size:12px;line-height:14px;color:#ffffff"> <p style="font-size:12px;line-height:13px;text-align:center;margin:0"><span style="color:#808080;font-size:11px">Some features are Beta, and should not be considered production-ready. Check the <a style="text-decoration:underline;color:#0068a5" href="https://info.unrealengine.com/gx0QfkJ0E304FT0aD100gCS" rel="noopener" target="_blank" data-saferedirecturl="https://www.google.com/url?q=https://info.unrealengine.com/gx0QfkJ0E304FT0aD100gCS&amp;source=gmail&amp;ust=1568554142211000&amp;usg=AFQjCNHEKWewUB7kr5S-Es3G0OaW8i9ZDg">release notes</a> for details.</span></p> <p style="font-size:12px;line-height:14px;text-align:center;margin:0">&nbsp;</p> <p style="font-size:12px;line-height:14px;text-align:center;margin:0"><span style="color:#333333;font-size:12px;line-height:14px"></span></p><div style="text-align:center"><span style="font-size:9px;color:#333333">© 2004-2019, Epic Games, Inc. All rights reserved.&nbsp;<strong>Epic, Epic Games, Unreal, Unreal Engine, UE4</strong>&nbsp;and their respective logos are Epic's trademarks or registered trademarks in the United States of America and elsewhere.&nbsp;Box 254, 2474 Walnut Street, Cary, North Carolina, 27518 USA</span></div> <div style="text-align:center"><span style="font-size:9px"><a href="https://info.unrealengine.com/NF00zDEa0014SCT0ikf0Q3J" rel="noopener" style="text-decoration:underline;color:#0068a5" target="_blank" data-saferedirecturl="https://www.google.com/url?q=https://info.unrealengine.com/NF00zDEa0014SCT0ikf0Q3J&amp;source=gmail&amp;ust=1568554142211000&amp;usg=AFQjCNGW4erEG8vq5p1TfZ9lXNWgz8kQAA">Manage Preferences</a>&nbsp; |&nbsp;<a href="https://info.unrealengine.com/uAk100QFfJ0a0j03CSEDT40" rel="noopener" style="text-decoration:underline;color:#0068a5" target="_blank" data-saferedirecturl="https://www.google.com/url?q=https://info.unrealengine.com/uAk100QFfJ0a0j03CSEDT40&amp;source=gmail&amp;ust=1568554142211000&amp;usg=AFQjCNE1bVP1UHbzZsn6QZHjUvl4RbZBrg">Unsubscribe</a>&nbsp; |&nbsp;<a href="https://info.unrealengine.com/taTS3E1CDQ0Jk00kFf0004B" rel="noopener" style="text-decoration:underline;color:#0068a5" target="_blank" data-saferedirecturl="https://www.google.com/url?q=https://info.unrealengine.com/taTS3E1CDQ0Jk00kFf0004B&amp;source=gmail&amp;ust=1568554142211000&amp;usg=AFQjCNGt1iVHtr6iZC6qR5RHo1rCYQV61A">Terms of Service</a>&nbsp;&nbsp; |&nbsp;&nbsp;<a href="https://info.unrealengine.com/ZFkfS04la0001E0QC30JTDC" rel="noopener" style="text-decoration:underline;color:#0068a5" target="_blank" data-saferedirecturl="https://www.google.com/url?q=https://info.unrealengine.com/ZFkfS04la0001E0QC30JTDC&amp;source=gmail&amp;ust=1568554142211000&amp;usg=AFQjCNEjElnPMx0EcSUljqwLbSRm7cBJAg">Privacy Policy</a></span></div> <div style="text-align:center">&nbsp;</div><p></p> </div> </div>   </div>  </div> </div>   </div> </div> </div> </div>  </td> </tr> </tbody> </table>   <img src="https://ci3.googleusercontent.com/proxy/UeNn2ZSkikZlRW6Yr_76mtBAYeoGBwR9LLUYp8cV47UE1oxWpxOeLxuNkzm-f7xy-ZMVR6F6qB1YP7TtofLOt7kdEqKHlogp015gdyAHi0-I-Mzae5a9H0d0lCQ0NDOfzi-vLPi2A1YP6poB_8liJjGP1NnoP-yR7McWlRSDOZrUI6c0dPPVALKDb--st6xBJA0VsUySjg3-8U5J9do=s0-d-e1-ft#https://info.unrealengine.com/trk?t=1&amp;mid=NzU0LURGVC03MDk6MzAxNDoyMTM1OjU4MTQ6MDozNzU5Ojk6MjkwNToxODUwODI5NDp2YWx2ZXVuaW9uNzZAZ21haWwuY29t" width="1" height="1" style="display:none!important" alt="" class="CToWUd"><div class="yj6qo"></div><div class="adL"></div></div>`;
                        this.emailPreviewState = 'contain';
                    });*/

                this.initFileUploader();

                this.editorState = 'editor';
            },
            reason => {
                console.warn('Failed to load offer editor data:', reason);
                this.editorState = 'error';
            }
        ));
    }

    public ngOnDestroy () : void {
        this.uiService.deactivateBackButton();
        this.cleanup();
    }

    public cleanup () : void {
        this.subs.forEach(sub => sub.unsubscribe());
    }

    public goBack () : void {
        this.router.navigateByUrl('/dashboard/offers');
    }

    public addSub (sub : Subscription) : void {
        this.subs = [ ...this.subs, sub ];
    }

    public ngOnChanges (changes: SimpleChanges) : void {

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

    public applyUserData (userData : UserData) : void {
        this.canViewHistory = userData.features.can('view:changelog');
        this.canEdit = userData.features.can('edit:offers');
        this.canCreateService = userData.features.can('settings:services');
        this.canCreateClient = userData.features.can('edit:clients');
        this.dateDisplayFormat = userData.settings.formats.datetime.display;
    }

    public onContactChanged (contactId : number) : void {
        this.offer.contact = this.contacts.find(contact => contact.id === contactId);
        this.isChanged = true;
    }

    public isStatus (statusKey : string) {
        return (this.statusOptions.find(s => s.value == this.offer.statusId) || { key: null }).key == statusKey;
    }

    public canEditClient () : boolean {
        return !!(this.canEdit && this.offer && this.offer.client && this.offer.client.id);
    }

    public onClientEdited (data : any) : void {
        if (data) {
            this.offer.client.name = data.client.name;
            this.updateContacts(data.contacts, 'current');
            this.isChanged = true;
        }

        this.layout = 'editor';
    }

    public getOfferInstance (source : any) : Offer {
        const offer : Offer = new Offer(source);

        offer.statusId = offer.statusId || this.statusOptions[0]?.value || 0;

        offer.coordinatorId = offer.coordinatorId || this.coordinatorOptions[0]?.value || 0;

        offer.client = offer.client || new ClientCompany();

        offer.contact = offer.contact || new Contact();

        offer.priorityId = offer.priorityId || this.priorityOptions[0]?.value || 0;

        offer.deliveryTypeId = offer.deliveryTypeId || this.deliveryTypeOptions[0]?.value || 0;

        offer.fieldId = offer.fieldId || this.subjectAreaOptions[0]?.value || 0;

        offer.translationTypeId = offer.translationTypeId || this.translationTypeOptions[0]?.value || 0;

        offer.tax = offer.tax || this.taxes[0];

        offer.shippingAddress = offer.shippingAddress || new ShippingAddress();

        offer.services = offer.services || [];

        offer.attachments = offer.attachments || [];

        offer.currency = offer.currency || this.currencyOptions[0]?.value;

        this.currency = this.currencies.find(currency => currency.key == offer.currency) || this.currencies[0] || new OfferCurrency();

        return offer;
    }

    // Fetch all attachments' urls
    public fetchAttachmentsUrls () : void {
        if (!this.attachmentsUrls) {
            this.attachmentsUrls = {};
        }

        this.offer.attachments.forEach(attachment => this.fetchAttachmentUrl(attachment));
    }

    // Fetch attachment's url
    public fetchAttachmentUrl (attachmentId : string | Attachment) : void {
        if (typeof(attachmentId) === 'object') {
            attachmentId = attachmentId.uuid;
        }

        if (!attachmentId || attachmentId in this.attachmentsUrls) {
            return;
        }

        this.attachmentsUrls[attachmentId] = '#';

        this.addSub(this.filesService.fetchFileUrl(attachmentId).subscribe(url => {
            if (attachmentId in this.attachmentsUrls) {
                this.attachmentsUrls[<string>attachmentId] = url;
            }
        }));
    }

    public offerizeAttachments (attachments : Attachment[]) : void {
        if (!this.canEdit) {
            return;
        }

        attachments.forEach(attachment => {
            if (!this.offer.attachments.find(a => a.uuid == attachment.uuid)) {
                this.offer.attachments.push(attachment);
                this.isChanged = true;
            }
        });
    }

    public createAttachmentsMap () : void {
        this.attachmentsMap = this.offer.services.reduce((acc : any, service : OfferServiceItem) => {
            acc[service.serviceId] = this.offer.attachments.filter((attachment : Attachment) => {
                return service.attachments.indexOf(attachment.uuid) !== -1;
            });

            return acc;
        }, {});
    }

    public fetchEmailHtml (offerKey : string) : Promise<string> {
        return new Promise((resolve, reject) => {
            if (offerKey != 'create') {
                this.addSub(this.offersService.fetchOfferEmail(offerKey).subscribe(
                    html => resolve((html || '').trim()),
                    () => reject()
                ));
            } else if (this.offer.attachments) {
                const emailAttachment = this.offer.attachments.find(a => a.type == 'EMAIL_CONTENT');

                if (!emailAttachment) {
                    resolve('');
                    return;
                }

                this.addSub(this.offersService.fetchOfferEmailContent(emailAttachment.uuid).subscribe(
                    html => resolve((html || '').trim()),
                    () => reject()
                ));
            }
        });
    }

    public fetchHistory () : void {
        if (this.isHistoryActual) {
            return;
        }

        this.historyRecords = [];

        if (!this.offer.key || !this.canViewHistory) {
            this.historyState = 'error';
            return;
        }

        this.historyState = 'loading';

        this.addSub(this.offersService.fetchOfferHistory(this.offer.key).subscribe(
            records => {
                this.historyRecords = records || [];
                this.historyRecords.forEach(record => {
                    record.items.forEach(item => {
                        for (let key in item) {
                            let value = (item[key] || '').trim();

                            if (!value) {
                                continue;
                            }

                            const match = value.match(/^([A-z\d_]+\.[A-z\d_]+\.)([A-z\d._]+)$/i);

                            if (!match) {
                                continue;
                            }

                            const transKey = match[1] + match[2].replace(/\./g, '_');
                            const transValue = this.langService.translate(transKey);

                            if (transKey !== transValue) {
                                item[key] = transValue;
                            }

                            console.log(transKey);
                        }
                    });
                });
                this.historyState = this.historyRecords.length ? 'ready' : 'empty';
                this.isHistoryActual = true;
                console.log('records', records);
            },
            reason => {
                console.warn('Can`t load history:', reason);
                this.historyState = 'error';
            }
        ));
    }

    public unlockCurrency () : void {
        if (!this.canEdit || !this.isCurrencyLocked) {
            return;
        }

        this.popupService.confirm({
            title: [ 'offers.editor.unlock_currency_title__button' ],
            message: [ 'offers.editor.unlock_currency_body__button' ],
        }).subscribe(({ isOk }) => {
            if (isOk) {
                this.offer.currencyRate = 0;
                this.offer.updateCurrencyRate = true;
                this.calculateServicesValues();
                this.isChanged = true;
            }
        });
    }

    public onCurrencyChanged (currencyKey : string) : void {
        // When currency has changed, we need to update
        // this.currency == Currency{ key, name, rate } and this.offer.currency == String "EUR".
        console.log('onCurrencyChanged', currencyKey);
        this.currency = this.currencies.find((currency : OfferCurrency) => currency.key === currencyKey);
        this.calculateServicesValues();
        this.isChanged = true;
    }

    public onTaxChanged (taxId : number) : void {
        console.log('onTaxChanged', taxId);
        this.offer.tax = this.taxes.find((t : any) => t.id === taxId);
        this.calculateServicesValues();
        this.isChanged = true;
    }

    public get isCurrencyLocked () : boolean {
        return this.offer.currencyRate > 0;
    }

    public getServiceBasePrice (service : any) : number {
        const ratio : number = (this.isCurrencyLocked ? this.offer.currencyRate : this.currency.rate) / 10000 || 1;
        return service.basePrice * ratio;
    }

    public calculateServicesValues () : void {
        let totalNet : number = 0;
        let totalGross : number = 0;

        this.offer.services.forEach((service : OfferServiceItem) => {
            if (!service.billable) {
                service.ratio = 0;
                service.price = 0;
                service.discount = 0;
                service.net = 0;
                service.gross = 0;

                return;
            }

            const ratio : number = divFloat(service.ratio || 0, 10000); // 1.0

            const quantity : number = divFloat(service.outRounded, 100); // 5.0

            const price : number = this.calcService.round(mulFloat(mulFloat(this.getServiceBasePrice(service), quantity), ratio), this.roundingRule);

            const net : number = Math.max(0, price - service.discount);

            const taxAmount = this.calcService.round(mulFloat(net, divFloat(this.offer.tax.value, 1000000)), this.roundingRule);

            const gross : number = net + taxAmount;

            console.log(
                `calculateServicesValues (${ service.serviceId }: ${ service.name || service.shortName }):`,
                '\n\tratio:', ratio,
                '\n\tquantity:', quantity,
                '\n\tprice:', price,
                '\n\tnet:', net,
                '\n\tgross:', gross,
            );

            service.price = price;
            service.net = net;
            service.gross = gross;

            totalNet += net;
            totalGross += gross;
        });

        this.totalNet = totalNet;
        this.totalGross = totalGross;
    }

    public onServiceValueChanged (service : OfferServiceItem, prop : string, value : string) {
        console.log(
            `onServiceValueChanged (${ service.serviceId }: ${ service.name || service.shortName }):`,
            '\n\tValue:', value,
            `\n\tService.${ prop }:`, service[prop]
        );

        this.calculateServicesValues();
        this.isChanged = true;
    }

    public onServiceBillableChanged (service : OfferServiceItem) {
        if (service.billable) {
            const values : any = this.unbillableServicesStates.get(service);

            if (values) {
                Object.keys(values).forEach((key : string) => service[key] = values[key]);
                this.unbillableServicesStates.delete(service);
            }
        } else {
            this.unbillableServicesStates.set(service, {
                ratio: service.ratio,
                price: service.price,
                discount: service.discount,
                net: service.net,
                gross: service.gross
            });

            service.ratio = 0;
            service.price = 0;
            service.discount = 0;
            service.net = 0;
            service.gross = 0;
        }

        this.calculateServicesValues();
        this.isChanged = true;
    }

    public updateContacts (contacts : Contact[], select : 'current' | 'primary') : void {
        console.log('updateContacts', select, contacts);

        this.contacts = [ this.contacts[0], ...(contacts || []) ];

        // --------------

        // Use on init
        if (select === 'current') {
            const contactId : number = this.offer && this.offer.contact && this.offer.contact.id || 0;

            this.offer.contact = (
                contactId &&
                this.contacts.find((contact : Contact) => contact.id == contactId) ||
                this.contacts[0]
            );

            this.offer.contact.id !== contactId && (this.isChanged = true);

        // Use on company selection
        } else if (select === 'primary') {
            const currentContactId : number = this.offer && this.offer.contact && this.offer.contact.id || null;

            this.offer.contact = (
                this.contacts.find((contact : Contact) => !contact.inactive && contact.primary) ||
                this.contacts[0]
            );

            this.offer.contact.id !== currentContactId && (this.isChanged = true);
        }
    }

    public removeService (service : OfferServiceItem) : void {
        if (!this.canEdit) {
            return;
        }

        this.popupService.confirm({
            title: [ 'offers.editor.service_remove_title__button' ],
            message: [ 'offers.editor.service_remove_body__button', { itemName: service.name } ],
        }).subscribe(({ isOk }) => {
            if (isOk) {
                this.offer.services.splice(this.offer.services.indexOf(service), 1);
                delete this.attachmentsMap[service.serviceId];
                this.unbillableServicesStates.delete(service);
                this.calculateServicesValues();
                this.isChanged = true;
            }
        });
    }

    public onUnlinkAttachment (service : OfferServiceItem, attachment : Attachment) : void {
        if (!this.canEdit) {
            return;
        }

        this.popupService.confirm({
            title: [ 'offers.editor.service_remove_title__button' ],
            message: [ 'offers.editor.confirm_unlink_attachment', { fileName: attachment.name } ],
        }).subscribe(({ isOk }) => {
            if (isOk) {
                this.unlinkAttachment(attachment, service);
            }
        });
    }
    // Unlink attachment from service(s)
    public unlinkAttachment (attachment : string | Attachment, service : number | OfferServiceItem = null) : void {
        if (!this.canEdit) {
            return;
        }

        if (typeof(attachment) == 'string') {
            attachment = this.offer.attachments.find((a : Attachment) => a.uuid === attachment);
        }

        if (!attachment) return;

        let services : OfferServiceItem[];

        if (!service) {
            services = this.offer.services;
        } else {
            if (typeof(service) == 'number') {
                service = <OfferServiceItem>this.offer.services.find((s : OfferServiceItem) => s.serviceId === <any>service);
                if (!service) return;
            }

            services = [ service ];
        }

        services.forEach((service : OfferServiceItem) => {
            deleteFromArray(this.attachmentsMap[service.serviceId], attachment);
            deleteFromArray(service.attachments, (<Attachment>attachment).uuid);
        });

        this.isChanged = true;
    }

    public hasLinkableAttachments (service : OfferServiceItem) : boolean {
        return this.offer.attachments.some(attachment => service.attachments.indexOf(attachment.uuid) === -1);
    }

    public showAttachmentsPopup (service : OfferServiceItem) : void {
        if (!this.canEdit) {
            return;
        }

        this.linkableAttachments = this.offer.attachments.reduce((acc : Attachment[], attachment : Attachment) => {
            if (service.attachments.indexOf(attachment.uuid) === -1) {
                acc.push(attachment);
            }

            return acc;
        }, []);

        if (!this.linkableAttachments.length) {
            return;
        }

        this.serviceToLink = service;
        this.attachmentsPopup.activate();
    }

    public hideAttachmentsPopup () : void {
        this.attachmentsPopup.deactivate().then(() => {
            this.linkableAttachments = [];
            this.serviceToLink = null;
        });
    }

    public onLinkAttachment (attachment : Attachment) : void {
        if (!this.canEdit) {
            return;
        }

        this.linkAttachment(attachment, this.serviceToLink);
        deleteFromArray(this.linkableAttachments, attachment);

        if (!this.linkableAttachments.length) {
            this.hideAttachmentsPopup();
        }
    }

    // Link attachment to service
    public linkAttachment (attachment : string | Attachment, service : number | OfferServiceItem) : void {
        if (!this.canEdit) {
            return;
        }

        if (typeof(attachment) == 'string') {
            attachment = this.offer.attachments.find((a : Attachment) => a.uuid === attachment);
        }

        if (typeof(service) == 'number') {
            service = <OfferServiceItem>this.offer.services.find((s : OfferServiceItem) => s.serviceId === service);
        }

        if (!service || service.attachments.indexOf(attachment.uuid) > -1) return;

        service.attachments.push(attachment.uuid);
        this.attachmentsMap[service.serviceId].push(attachment);

        this.isChanged = true;
    }

    // ----------------------------

    public set isInstructionsEditorEnabled (enableEditor : boolean) {
        if (!this.canEdit) {
            return;
        }

        if (enableEditor) {
            this.instructionsEditorHeight = this.instructionsText.nativeElement.getBoundingClientRect().height;
            console.log(this.instructionsEditorHeight);
        }

        this.IsInstructionsEditorEnabled = enableEditor;

        if (enableEditor) {
            window.requestAnimationFrame(() => {
                setSelectionRange(this.instructionsEditor.nativeElement, (this.offer.instruction || '').length);
                this.instructionsEditor.nativeElement.focus();
            });
        }
    }

    public get isInstructionsEditorEnabled () : boolean {
        return this.IsInstructionsEditorEnabled;
    }

    public onInstructionsEditorKeyUp (event : any) : void {
        if (event.keyCode == 27 || event.keyCode == 13 && event.ctrlKey) {
            event.stopPropagation();
            this.isInstructionsEditorEnabled = false;
        } else {
            this.isChanged = true;
        }
    }

    // ----------------------------

    public onDeleteAttachment (attachment : string | Attachment) : void {
        if (!this.canEdit) {
            return;
        }

        if (typeof(attachment) == 'string') {
            attachment = this.offer.attachments.find((a : Attachment) => a.uuid === attachment);
        }

        if (!attachment)  {
            return;
        }

        this.popupService.confirm({
            message: [ 'offers.editor.confirm_unlink_attachment', { fileName: attachment.name } ],
        }).subscribe(({ isOk }) => {
            if (isOk) {
                if (isOk) {
                    this.deleteAttachment(attachment);
                }
            }
        });
    }

    // Add attachment to offer after upload
    public addAttachment (attachment : Attachment) : void {
        if (!this.canEdit) {
            return;
        }

        this.fetchAttachmentUrl(attachment.uuid);
        this.offer.attachments.push(attachment);

        this.isChanged = true;
    }

    public deleteAttachment (attachment : string | Attachment) : void {
        if (!this.canEdit) {
            return;
        }

        if (typeof(attachment) == 'string') {
            attachment = this.offer.attachments.find((a : Attachment) => a.uuid === attachment);
        }

        if (!attachment) {
            return;
        }

        this.unlinkAttachment(attachment);
        deleteFromArray(this.offer.attachments, attachment);
        delete this.attachmentsUrls[attachment.uuid];

        this.isChanged = true;
    }

    // ----------------------------

    public isEditingFileComment (file : Attachment, commentType : string) : boolean {
        return this.fileToEditComment == file && this.fileCommentTypeToEdit == commentType;
    }

    public getFileCommentText (file : Attachment, commentType : string) : string {
        return (file[commentType] || '').trim();
    }

    public enableFileCommentEditor (file : Attachment, commentType : string) : void {
        if (!this.canEdit) {
            return;
        }

        this.fileToEditComment = file;
        this.fileCommentTypeToEdit = commentType;

        window.requestAnimationFrame(() => {
            setSelectionRange(this.fileCommentEditor.nativeElement, (file[commentType] || '').length);
            this.fileCommentEditor.nativeElement.focus();
        });
    }

    public disableFileCommentEditor () : void {
        this.fileToEditComment = null;
        this.fileCommentTypeToEdit = null;
    }

    public onFileCommentEditorKeyUp (event : any) : void {
        if (event.keyCode == 27 || event.keyCode == 13 && event.ctrlKey) {
            event.stopPropagation();
            this.disableFileCommentEditor();
        } else {
            this.isChanged = true;
        }
    }

    // ----------------------------

    public getInstructionsText () : string {
        return this.offer && (this.offer.instruction || '').trim();
    }

    public initFileUploader () : void {
        // Init file uploader
        this.uploader = new FileUploader({
            autoUpload: false,     // manual upload
            disableMultipart: true // switch POST to PUT
        });

        // Set PUT method for each file
        this.uploader.onAfterAddingFile = (file : any) => {
            file.method = 'PUT';
        };

        // Reset uploader and presign all files
        this.uploader.onAfterAddingAll = () => {
            //! this.hideUploadsError();
            this.areUploadingErrorsVisible = false;
            this.uploadErrors = [];

            this.presignFiles(this.uploader.queue)
                .then((files : any[]) => {
                    files.forEach((file : any) => {
                        if (!file.presignedFile) {
                            file.cancel();
                        }
                    });

                    this.uploadQueueSize = this.uploader.queue.length;
                    this.uploadedFilesCount = 0;
                    this.uploader.uploadAll();
                });
        };

        // Set unique upload url for every file
        this.uploader.onBeforeUploadItem = (file : any) => {
            this.uploader.setOptions({
                url: file.presignedFile.url
            });

            file.withCredentials = false;
        };

        // Increment upload counter on file uploaded (it doesn't matter success or not)
        this.uploader.onCompleteItem = () => {
            this.uploadedFilesCount++;
        };

        // Add file to attachments array if it was uploaded successfully
        this.uploader.onSuccessItem = (file : any) => {
            let attachment : Attachment = new Attachment();

            attachment.name = file.file.name;
            attachment.uuid = file.presignedFile.uuid;

            this.addAttachment(attachment);
        };

        // Add error message to array if file uploading failed
        this.uploader.onErrorItem = (file : any) => {
            this.uploadErrors.push(file.file.name);
            this.areUploadingErrorsVisible = true;
        };

        // Update uploading progress
        this.uploader.onProgressAll = (progress : any) => {
            this.uploadingProgress = Math.round((this.uploadedFilesCount + progress / 100) / this.uploadQueueSize * 100);
        };

        // Reset uploader after uploading
        this.uploader.onCompleteAll = () => {
            this.uploadingProgress = 0;
            this.uploader.clearQueue();
        };
    }

    public onDropzoneClick () : void {
        if (this.uploader.isUploading || !this.uploaderInput) {
            return;
        }

        this.uploaderInput.nativeElement.click();
    }

    public onDropzoneOver (isDropzoneOver : boolean) : void {
        this.isDropzoneOver = isDropzoneOver;
    }


    public presignFiles (files : any[]) : Promise<any[]> {
        return new Promise((resolve) => {
            let requestsCount : number = 0;

            const promises : Promise<any[]>[] = files.map((file : any) => {
                requestsCount++;
                return this.offersService.presignFile(file.file.name);
            });

            promises.forEach((promise : Promise<any[]>, index : number) => {
                promise
                    .catch((reason : any) => {
                        console.warn('Can`t presign file:', reason);
                        return null;
                    })
                    .then((presignedFile : any) => {
                        files[index].presignedFile = presignedFile;

                        if (!--requestsCount) {
                            resolve(files);
                        }
                    });
            });
        });
    }

    // -----------------------

    public activeTab : Tab = 'details';

    public switchTab (tab : Tab) : void {
        if (tab === 'transactions' && !this.isClientSelected) {
            return;
        }

        if (tab === 'history' && !this.canViewHistory) {
            if (this.deviceService.device.touch) {
                this.popupService.alert({
                    message: [ 'log.history_tab_alert__message' ]
                });
            }
            return;
        }

        this.activeTab = tab;

        if (tab === 'transactions') {
            this.transactionsState = 'loading';
            this.fetchTransactions();
        } else if (tab === 'history') {
            this.fetchHistory();
        }

        this.scrollToTop();
    }

    public getLangName (code : string) : string {
        return (this.directionOptions.find(d => d.value == code) || { display: code }).display;
    }

    // -----------------------

    public showSettingsPopup () : void {
        this.settingsPopup.activate();
    }

    public hideSettingsPopup () : void {
        this.settingsPopup.deactivate();
    }

    // ------------------------

    /*
    public showEmailPopup () : void {
        if (!this.emailPreviewIframe) {
            console.warn('Can\'t find emailPreviewIframe');
            return;
        }

        this.emailPreviewIframe.nativeElement.contentWindow.document.open();
        this.emailPreviewIframe.nativeElement.contentWindow.document.write(this.emailPreviewHTML);
        this.emailPreviewIframe.nativeElement.contentWindow.document.close();

        this.emailPreviewIframe.nativeElement.contentWindow.document.body.style.overflowX = 'visible';
        this.emailPreviewIframe.nativeElement.contentWindow.document.body.style.overflowY = 'hidden';
        this.emailPreviewIframe.nativeElement.contentWindow.document.body.style.margin = '0';

        defer(() => {
            this.emailPopup.activate().then(() => this.updateEmailPopupSize());
        });
    }

    public updateEmailPopupSize () : void {
        if (!this.emailPopup || !this.emailPopup.isActive || !this.emailPreviewIframe) {
            return;
        }

        requestAnimationFrame(() => {
            this.emailIframeHeight = this.emailPreviewIframe.nativeElement.contentWindow.document.documentElement.scrollHeight;
        });
    }
     */

    public showEmailPopup () : void {
        this.emailPopup.activate();
    }

    public hideEmailPopup () : void {
        this.emailPopup.deactivate();
    }

    // -----------------------

    public scrollToTop () : void {
        window.scrollTo(0, 0);
    }

    // ----------------------------
    // Service Selector
    // ----------------------------

    public serviceSelectorState : 'init' | 'empty' | 'error' | 'ready' = 'init';

    public serviceSelectorFilters : any = null;

    public serviceSelectorFiltersForm : FormGroup;

    public serviceSelectorServices : any = null;

    public serviceSelectorSort : any = {
        by: 'name',
        direction: 1
    };

    public serviceSelectorSortOptions : any[] = [];

    public serviceSelectorFilterTimeout : any = null;

    public isServiceSelectorSidebarActive : boolean = true;

    // ----------------------------

    public onServiceSelectorActivated () : void {
        if (!this.canEdit) {
            return;
        }

        this.serviceSelectorState = 'init';
        this.serviceSelectorSort = {
            by: 'name',
            direction: 1
        };
        this.serviceSelectorSortOptions = [
            {
                display: this.langService.translate('offers.service.service_name__table_th'),
                value: 'name'
            },
            {
                display: this.langService.translate('offers.service.service_short_name__table_th'),
                value: 'shortName'
            },
            {
                display: this.langService.translate('offers.service.service_from__table_th'),
                value: 'from'
            },
            {
                display: this.langService.translate('offers.service.service_to__table_th'),
                value: 'to'
            },
            {
                display: this.langService.translate('offers.service.service_price__table_th'),
                value: 'price'
            },
            {
                display: this.langService.translate('offers.service.service_unit__table_th'),
                value: 'unit'
            },
            {
                display: this.langService.translate('offers.service.service_rate__table_th'),
                value: 'rate'
            }
        ];
        this.serviceSelectorFilterTimeout = null;

        this.serviceSelectorFiltersForm = this.formBuilder.group({
            from: [ this.directionOptions[0].value ],  // ''
            to: [ this.directionOptions[0].value ],  // ''
            rate: [ this.rateOptions[0].value ],  // null
            name: [ '' ],
            shortName: [ '' ],
            unit: [ this.unitOptions[0].value ]  // null
        });

        this.serviceSelectorFiltersForm.valueChanges.subscribe(val => {
            this.onServiceSelectorFiltersChanged(true);
        });

        const clientId : number = this.offer.client && this.offer.client.id || null;

        this.addSub(zip(
            this.ratesService.loadAvailableRates(clientId),
            this.offersService.fetchCompanyServices(clientId)
        ).subscribe(
            ([ rates, services ] : [ Rate[], any ]) => {
                // Rates
                this.rateOptions = [
                    ...this.rateOptions,
                    ...rates.map((rate : Rate) => ({
                        value: rate.id,
                        display: rate.name
                    }))
                ];

                // Services
                const usedServices : number[] = (this.offer.services || []).map(s => s.serviceId);

                this.serviceSelectorServices = (
                    services
                        .services
                        .map(service => {
                            return {
                                service,
                                isSelected: false,
                                isVisible : true,
                                isUsed: usedServices.indexOf(service.id) > -1
                            };
                        })
                );

                this.serviceSelectorFilterServices();
                this.serviceSelectorSortServices();

                this.serviceSelectorServices
                    .reduce((units, service) => {
                        if (units.indexOf(service.service.unit) == -1) {
                            units.push(service.service.unit);
                        }

                        return units;
                    }, [])
                    .sort()
                    .forEach(unit => {
                        this.unitOptions.push({
                            display: String(unit),
                            value: unit
                        });
                    });

                this.serviceSelectorState = 'ready';
            },
            (reason : any) => {
                console.warn('Failed to load services selector data:', reason);
                this.serviceSelectorState = 'error';
            }
        ));
    }

    public serviceSelectorFilterServices () : void {
        const
            filters : any = this.serviceSelectorFiltersForm.getRawValue(),
            name : string = filters.name.trim(),
            shortName : string = filters.shortName.trim(),
            nameRegexp : any = name ? new RegExp(str2regexp(name), 'i') : null,
            shortNameRegexp : any = shortName ? new RegExp(str2regexp(shortName), 'i') : null;

        let visibleCount : number = 0;

        this.serviceSelectorServices
            .forEach((item : any) => {
                item.isVisible = (
                    visibleCount < 50 &&
                    (filters.from === this.directionOptions[0].value || filters.from === item.service.from) &&
                    (filters.to === this.directionOptions[0].value || filters.to === item.service.to) &&
                    (filters.rate === this.rateOptions[0].value || filters.rate === item.service.rate) &&
                    (!nameRegexp || nameRegexp.test(item.service.name || '')) &&
                    (!shortNameRegexp || shortNameRegexp.test(item.service.shortName || '')) &&
                    (filters.unit === this.unitOptions[0].value || filters.unit === item.service.unit)
                );

                item.isVisible && visibleCount++;
            });

        if (this.serviceSelectorState === 'empty' || this.serviceSelectorState === 'ready') {
            this.serviceSelectorState = visibleCount ? 'ready' : 'empty';
        }
    }

    public getLanguageNameByCode (code : string) : string {
        return (this.directionOptions.find(d => d.value == code) || { display: code }).display;
    }

    public getRateNameById (rateId : any) : string {
        return (this.rateOptions.find(r => r.value == Number(rateId)) || { display: '' }).display;
    }

    public serviceSelectorSortServices () : void {
        const { by, direction } = this.serviceSelectorSort;

        this.serviceSelectorServices = (
            this.serviceSelectorServices.sort(
                (s1 : any, s2 : any) => {
                    s1 = s1.service;
                    s2 = s2.service;

                    let a : any = s1[by],
                        b : any = s2[by];

                    if (by == 'rate' || by == 'price') {
                        return (((a || 0) - (b || 0)) || (s1.id - s2.id)) * direction;
                    } else if (by == 'from' || by == 'to') {
                        a && (a = this.getLanguageNameByCode(a));
                        b && (b = this.getLanguageNameByCode(b));
                    } else {
                        a = a || '';
                        b = b || '';
                    }

                    return ((a || '').localeCompare(b || '') || (s1.id - s2.id)) * direction;
                }
            )
        );
    }

    public onServiceSelectorFiltersChanged (useTimeout : boolean = false) : void {
        if (this.serviceSelectorFilterTimeout != null) {
            clearTimeout(this.serviceSelectorFilterTimeout);
            this.serviceSelectorFilterTimeout = null;
        }

        this.serviceSelectorFilterTimeout = setTimeout(() => {
            this.serviceSelectorFilterServices();
            this.serviceSelectorSortServices();
            this.serviceSelectorFilterTimeout = null;
        }, useTimeout ? 350 : 0);
    }

    public onServiceSelectorSortChanged () : void {
        // if (this.serviceSelectorOrderBy == orderBy) {
        //     this.serviceSelectorOrderDirection *= -1;
        // } else {
        //     this.serviceSelectorOrderBy = orderBy;
        //     this.serviceSelectorOrderDirection = 1;
        // }

        this.serviceSelectorSortServices();
    }

    public isServiceSelectorSelectionEmpty () : boolean {
        return !this.serviceSelectorServices || !this.serviceSelectorServices.some(s => s.isSelected);
    }

    public onServiceSelectorSubmit (submit : boolean = true) : void {
        if (!this.canEdit) {
            return;
        }

        if (submit) {
            const services : CompanyServiceItem[] = (
                this.serviceSelectorServices.reduce((acc : any[], item : any) => {
                    item.isSelected && acc.push(item.service);
                    return acc;
                }, [])
            );

            if (services.length) {
                services.forEach((companyService : CompanyServiceItem) => {
                    const offerService : OfferServiceItem = new OfferServiceItem();

                    offerService.serviceId = companyService.id;
                    offerService.name = companyService.name;
                    offerService.shortName = companyService.shortName;
                    offerService.from = companyService.from;
                    offerService.to = companyService.to;
                    offerService.basePrice = companyService.price;
                    offerService.unit = companyService.unit;
                    offerService.price = offerService.basePrice;
                    offerService.in = 0;
                    offerService.outRounded = offerService.in;

                    this.attachmentsMap[offerService.serviceId] = [];
                    this.offer.services.push(offerService);
                });

                this.calculateServicesValues();
                this.isChanged = true;
            }
        }

        this.layout = 'editor';
    }


    // ----------------------------
    // Company Selector
    // ----------------------------

    public companySelectorState : 'initial' | 'searching' | 'empty' | 'list' | 'error' = 'initial';

    public companySelectorAction : 'idle' | 'create' | 'submit' = 'idle';

    public companySelectorValue : string = '';

    public companySelectorTimeout : any = null;

    public companySelectorCompanies : ClientCompany[] = [];

    public companySelectorRequest : Promise<any> = null;

    public selectedCompany : ClientCompany = null;

    // ----------------------------

    public onCompanySelectorActivated () : void {
        if (!this.canEdit) {
            return;
        }

        this.companySelectorAction = 'idle';
        this.companySelectorTimeout = null;
        this.companySelectorCompanies = [];
        this.companySelectorRequest = null;
        this.companySelectorValue = this.companySelectorValue || this.offer.client && this.offer.client.name || '';
        this.onCompanySearch(true);
    }

    public onCompanySearch (isInitial : boolean = false) : void {
        this.companySelectorRequest = null;

        if (this.companySelectorTimeout) {
            clearTimeout(this.companySelectorTimeout);
            this.companySelectorTimeout = null;
        }

        const value : string = this.companySelectorValue.replace(/\s+/g, ' ').trim();

        if (isInitial) {
            this.companySelectorValue = value;
        }

        if (value.length < 3) {
            this.selectedCompany = null;
            this.companySelectorState = 'initial';
            return;
        }

        this.companySelectorState = 'searching';

        this.companySelectorTimeout = setTimeout(() => {
            const promise : Promise<any> = this.companySelectorRequest = (
                this.clientsService
                    .fetchClientCompanies(value)
                    .toPromise()
                    .then((response : any) => response.clients || [])
                    .catch((reason : any) => {
                        console.warn('onCompanySearch error:', reason);
                        return null;
                    })
                    .then((companies : ClientCompany[]) => {
                        if (this.companySelectorRequest !== promise) {
                            return;
                        }

                        if (!companies) {
                            this.companySelectorCompanies = [];
                            this.selectedCompany = null;
                            this.companySelectorState = 'error';
                            return;
                        }

                        this.companySelectorCompanies = companies;

                        const currentCompanyId = this.offer.client && this.offer.client.id || null;

                        this.selectedCompany = companies.find((company : ClientCompany) => company.id === currentCompanyId) || null;

                        this.companySelectorState = this.companySelectorCompanies.length ? 'list' : 'empty';

                        this.companySelectorRequest = null;
                    })
            );
        }, isInitial ? 0 : 600);
    }

    public onCompanySelect (company : ClientCompany, submit : boolean = false) : void {
        if (this.companySelectorAction != 'idle') {
            return;
        }

        this.selectedCompany = company;
        submit && this.onSubmitCompany();
    }

    public onSubmitCompany (selectedCompany : ClientCompany = null) : void {
        selectedCompany = selectedCompany || this.selectedCompany;

        if (this.offer.client && this.offer.client.id == selectedCompany.id) {
            this.layout = 'editor';
            return;
        }

        if (this.companySelectorAction != 'create') {
            this.companySelectorAction = 'submit';
        }

        const company : ClientCompany = new ClientCompany();

        company.id = selectedCompany.id;
        company.name = selectedCompany.name;

        this.offer.client = company;

        this.addSub(this.clientsService.fetchClientCompanyContacts(company.id).subscribe((response : any) => {
            this.updateContacts(response.contacts, 'primary');
            this.layout = 'editor';
            this.isChanged = true;
        }));
    }

    public onCreateCompany () : void {
        const companyName : string = this.companySelectorValue.replace(/\s+/g, ' ').trim();

        this.popupService.confirm({
            message: [ 'offers.company.confirmation__message', { companyName } ],
        }).subscribe(({ isOk }) => {
            if (isOk) {
                this.companySelectorAction = 'create';

                this.addSub(this.clientsService.createClientCompany(companyName).subscribe((company : ClientCompany) => {
                    this.onSubmitCompany(company);
                }));
            }
        });
    }

    public canCreateCompany () : boolean {
        if (!this.canCreateClient || this.companySelectorState === 'searching') {
            return false;
        }

        const name : string = this.companySelectorValue.replace(/\s+/g, ' ').trim();

        if (name.length < 3) {
            return false;
        }

        const nameLowerCase : string = name.toLowerCase();

        for (let i = 0, len = this.companySelectorCompanies.length; i < len; i++) {
            if (this.companySelectorCompanies[i].name.toLowerCase() == nameLowerCase) {
                return false;
            }
        }

        return true;
    }

    // Transaction Popup
    // --------------------------------

    public fetchTransactions () : Promise<void> {
        return new Promise((resolve) => {
            if (!this.offer.key) {
                this.transactions = [];
                this.transactionsState = 'empty';
                resolve();
                return;
            }

            this.addSub(this.offersService.fetchOfferTransactions(this.offer.key).subscribe(
                response => {
                    this.transactions = response.transactions || [];

                    if ('totalAmount' in response && 'currency' in response) {
                        this.transactionsTotalAmount = response.totalAmount;
                        this.transactionsTotalAmountCurrency = response.currency;
                    }

                    this.transactionsState = this.transactions.length ? 'ready' : 'empty';

                    resolve();
                },
                reason => {
                    console.warn('Can`t load transactions:', reason);

                    this.transactions = [];
                    this.transactionsState = 'error';

                    resolve();
                }
            ));
        });
    }

    public showTransactionPopup () : void {
        if (!this.canEdit) {
            return;
        }

        this.transaction = {
            amount: 0,
            comment: '',
            currency: this.currencyOptions[0].value,
            offerKey: this.offer.key
        };

        this.transactionPopup.activate();
    }

    public hideTransactionPopup (byOverlay : boolean = false) : void {
        if (byOverlay || this.networkProcess) {
            return;
        }

        this.transactionPopup.deactivate().then(() => {
            this.transaction = null;
        });
    }

    public submitTransactionPopup () : void {
        if (!this.canEdit) {
            return;
        }

        this.networkProcess = 'create-transaction';

        this.addSub(
            this.offersService
                .saveTransaction(cloneDeep(this.transaction))
                .subscribe(
                    (transaction : any) => {
                        console.log('Transaction saved:', transaction);
                        if (this.activeTab === 'transactions') {
                            this.fetchTransactions().then(() => {
                                this.networkProcess = null;
                                this.hideTransactionPopup();
                            });
                        } else {
                            this.networkProcess = null;
                            this.hideTransactionPopup();
                            this.switchTab('transactions');
                        }
                    },
                    (reason : any) => {
                        console.warn('Can`t create transaction:', reason);
                        this.toastService.create({
                            message: [ 'offers.editor.cash_payment_save_failed' ]
                        });
                        this.networkProcess = null;
                        // this.hideTransactionPopup();
                    }
                )
        );
    }

    public isTransactionValid () : boolean {
        return !!(this.transaction && this.transaction.currency);
    }

    // Billing Popup
    // -----------------------------

    public showBillingPopup () : void {
        if (!this.canEdit) {
            return;
        }

        this.billingForm = {
            to: (this.offer && this.offer.contact && this.offer.contact.email || '').trim(),
            cc: '',
            bcc: '',
            message: ''
        };

        this.validateBillingForm();
        this.sendingBillingError = null;
        this.isEmailVerificationCodeSent = false;
        this.billingPopup.activate().then(() => {
            window.requestAnimationFrame(() => this.billingFormMessageRef.nativeElement.focus());
        });
    }

    public hideBillingPopup () : void {
        if (this.networkProcess) {
            return;
        }

        this.billingPopup.deactivate().then(() => {
            this.billingForm = null;
        });
    }

    public submitBillingPopup () : void {
        if (!this.canEdit || !this.isBillingFormValid()) {
            return;
        }

        this.networkProcess = 'saving-offer';

        this.saveOffer()
            .then(() => {
                this.offersService.sendQuote(this.offer.key, this.billingForm).subscribe(
                    (error : any) => {
                        if (error) {
                            this.sendingBillingError = error;
                        } else {
                            this.networkProcess = null;
                            this.hideBillingPopup();
                            this.showSavingMessage(true);
                        }
                    },
                    (reason : any) => {
                        this.networkProcess = null;
                        this.showSavingMessage(false);
                        console.warn('Can`t send billing:', reason);
                    }
                );
            }).catch(() => {
                this.showSavingMessage(false);
                this.networkProcess = null;
            });
    }

    public isBillingFormValid () : boolean {
        if (this.billingForm) {
            for (let key in this.billingFormErrors) {
                if (this.billingFormErrors[key]) {
                    return false;
                }
            }
        }

        return true;
    }

    public validateBillingForm (fieldName : string = null) : void {
        if (!this.billingFormErrors) {
            this.billingFormErrors = {};
        }

        const fields : string[] = fieldName ? [ fieldName ] : [ 'to', 'cc', 'bcc' ];

        fields.forEach((fieldName : string) => {
            if (fieldName == 'to') {
                this.billingFormErrors.to = !(
                    this.billingForm.to
                        .replace(/[\s\r\n\t;,]+/g, ' ')
                        .trim()
                        .split(' ')
                        .every((email : string) => isEmailValid(email))
                );
            } else if (fieldName == 'cc') {
                this.billingFormErrors.cc = !(
                    !this.billingForm.cc.replace(/[\s\t\r\n;,]/g, '') ||
                    this.billingForm.cc
                        .replace(/[\s\r\n\t;,]+/g, ' ')
                        .trim()
                        .split(' ')
                        .every((email : string) => isEmailValid(email))
                );
            } else if (fieldName == 'bcc') {
                this.billingFormErrors.bcc = !(
                    !this.billingForm.bcc.replace(/[\s\t\r\n;,]/g, '') ||
                    this.billingForm.bcc
                        .replace(/[\s\r\n\t;,]+/g, ' ')
                        .trim()
                        .split(' ')
                        .every((email : string) => isEmailValid(email))
                );
            }
        });
    }

    public sendEmailVerificationCode () : void {
        if (this.isEmailVerificationCodeSent) {
            return;
        }

        this.isEmailVerificationCodeSent = true;

        this.addSub(this.userService.verifyEmail().subscribe(
            () => {
                this.sendingBillingError = null;
                this.toastService.create({
                    message: [ 'offers.editor.quote_details.link_sent' ]
                });
            },
            () => {
                this.toastService.create({
                    message: [ 'offers.editor.quote_details.link_error' ]
                });
            }
        ));
    }

    public saveOffer () : Promise<void> {
        return new Promise<void>((resolve, reject) => {
            if (!this.canEdit) {
                reject();
                return;
            }

            trimProperties(this.offer, true);

            this.addSub(this.offersService.saveOffer(this.offer).subscribe(
                (response : any) => {
                    this.offer = this.getOfferInstance(response.offer);
                    this.isClientSelected = !!(this.offer.client && this.offer.client.id);

                    if (this.offer.contact && !this.contacts.find((c : Contact) => c.id === this.offer.contact.id)) {
                        this.updateContacts(
                            this.contacts.slice(1).concat([ this.offer.contact ]),
                            'current'
                        );
                    }

                    this.calculateServicesValues();
                    this.fetchAttachmentsUrls();
                    this.createAttachmentsMap();

                    this.isChanged = false;
                    this.isHistoryActual = false;

                    if (this.editorMode === 'create') {
                        this.editorMode = 'edit';
                        this.location.replaceState(`/dashboard/offer/${ this.offer.key }`);
                    }

                    if (this.activeTab === 'history') {
                        this.fetchHistory();
                    }

                    resolve();
                },
                (reason : any) => {
                    console.warn('Can`t save offer:', reason);
                    reject();
                }
            ));
        });
    }

    public onSaveOffer () : void {
        if (!this.canEdit) {
            return;
        }

        this.networkProcess = 'saving-offer';

        this.saveOffer()
            .then(() => this.showSavingMessage(true))
            .catch(() => this.showSavingMessage(false))
            .then(() => this.networkProcess = null);
    }

    public showSavingMessage (isOk : boolean) : void {
        const status : string = isOk ? 'success' : 'error';
        this.toastService.create({
            message: [ `offers.editor.save_${ status }__message` ]
        });
    }

    // Quote popup
    // -------------------------------

    public fetchCompanyProfile () : Promise<void> {
        return new Promise((resolve, reject) => {
            if (this.companyProfile !== null) {
                resolve();
                return;
            }

            this.addSub(this.companyService.getCompany().subscribe(
                (company : Company) => {
                    this.companyProfile = company;
                    resolve();
                },
                (reason : any) => {
                    console.warn('Can`t load company profile:', reason);
                    reject();
                }
            ));
        });
    }

    public fetchClientProfile () : Promise<void> {
        return new Promise((resolve, reject) => {
            // Reset clientProfile if user selected other client
            if (this.offer.client && this.clientProfile && this.clientProfile.id != this.offer.client.id) {
                this.clientProfile = null;
            }

            if (!this.offer || !this.offer.client || !this.offer.client.id || (this.clientProfile && this.clientProfile.id === this.offer.client.id)) {
                resolve();
                return;
            }

            this.addSub(this.clientsService.loadClient(this.offer.client.id).subscribe(
                (client : Client) => {
                    this.clientProfile = client;
                    resolve();
                },
                (reason : any) => {
                    console.warn('Can`t load client profile:', reason);
                    reject();
                }
            ));
        });
    }

    public showQuote () : void {
        this.networkProcess = 'loading-company-profile';

        Promise.all([
            this.fetchCompanyProfile(),
            this.fetchClientProfile()
        ])
        .then(() => this.showQuotePopup())
        .catch(() => {
            this.toastService.create({
                message: [ `offers.editor.quote_preview.loading_error` ]
            });
        })
        .then(() => this.networkProcess = null);
    }

    public showQuotePopup () : void {
        this.quotePopup.activate();
    }

    public hideQuotePopup () : void {
        this.quotePopup.deactivate();
    }

    public copyQuoteText () : void {
        const node = this.quotePreviewRef.nativeElement;

        node.focus();
        window.getSelection().removeAllRanges();

        let range : any = document.createRange();
        range.selectNode(node);
        window.getSelection().addRange(range);

        const status : string = document.execCommand('copy') ? 'success' : 'error';
        window.getSelection().removeAllRanges();

        this.toastService.create({
            message: [ `offers.editor.quote_preview.copy_result_${ status }__message` ]
        });
    }

    public calcTotalServicesNet () : number {
        if (!this.offer.services || !this.offer.services.length) {
            return 0;
        }

        return this.offer.services.reduce((total, service) => total + (service.billable ? service.net : 0), 0);
    }

    public calcTotalServicesTax () : number {
        if (!this.offer.services || !this.offer.services.length) {
            return 0;
        }

        return this.offer.services.reduce((total, service) => total + (service.billable ? (service.gross - service.net) : 0), 0);
    }

    public calcTotalServicesGross () : number {
        if (!this.offer.services || !this.offer.services.length) {
            return 0;
        }

        return this.offer.services.reduce((total, service) => total + (service.billable ? service.gross : 0), 0);
    }

    // ----------------------------

    public fetchCompanyCoordinators () : Promise<any> {
        return new Promise((resolve, reject) => {
            if (this.projectCoordinatorOptions) {
                resolve();
                return;
            }

            this.addSub(this.companyService.fetchCoordinators().subscribe(
                (coordinators : Coordinator[]) => {
                    this.projectCoordinatorOptions = coordinators.map((coordinator : Coordinator) => {
                        return {
                            display: [ coordinator.firstName, coordinator.lastName ].join(' '),
                            value: coordinator.id
                        };
                    });

                    resolve();
                },
                (reason : any) => {
                    console.log('Can`t load projectCoordinatorOptions:', reason);
                    reject();
                }
            ));
        });
    }

    public fetchMemorizedCompanyCoordinator () : Promise<any> {
        return new Promise((resolve, reject) => {
            if (this.projectCoordinatorParams) {
                resolve();
                return;
            }

            this.addSub(this.userService.fetchFromStorage('offerProjectCoordinator').subscribe(
                (params : any) => {
                    this.projectCoordinatorParams = (params || {
                        rememberCoordinator: false,
                        coordinatorId: 0
                    });

                    resolve();
                },
                (reason : any) => {
                    console.log('Can`t load projectCoordinatorParams', reason);
                    reject();
                }
            ));
        });
    }

    public showProjectPopup () : void {
        if (!this.canEdit) {
            return;
        }

        this.networkProcess = 'project-popup-loading';

        Promise.all([
            this.fetchCompanyCoordinators(),
            this.fetchMemorizedCompanyCoordinator()
        ])
        .then(() => {
            if (
                !this.projectCoordinatorParams.rememberCoordinator ||
                !this.projectCoordinatorParams.coordinatorId ||
                !this.projectCoordinatorOptions.find(c => c.value == this.projectCoordinatorParams.coordinatorId)
            ) {
                const userId = this.userService.getUserData().profile.user.id;

                this.projectCoordinatorParams.rememberCoordinator = false;
                this.projectCoordinatorParams.coordinatorId = this.projectCoordinatorOptions.find(c => c.value == userId) && userId || 0;
            }

            this.projectPopup.activate();
        })
        .catch((reason : any) => console.warn('showProjectPopup promises error:', reason))
        .then(() => this.networkProcess = null);
    }

    public hideProjectPopup () : void {
        if (this.networkProcess) {
            return;
        }

        this.projectPopup.deactivate();
    }

    public submitProjectPopup () : void {
        if (!this.canEdit) {
            return;
        }

        this.networkProcess = 'create-project';

        Promise.all([
            this.projectsService.createProject(this.offer.key, this.projectCoordinatorParams.coordinatorId).toPromise(),
            this.userService.saveToStorage('offerProjectCoordinator', this.projectCoordinatorParams)
        ])
        .then(([ project, _ ] : [ any, any ]) => {
            this.router.navigate([ `/dashboard/project/${ project.projectKey }` ]);
        })
        .catch((reason : any) => console.warn('submitProjectPopup promises error:', reason))
        .then(() => {
            this.networkProcess = null;
            this.hideProjectPopup();
        });
    }

    // ------------

    @HostListener('document:click', [ '$event' ])
    public onDocumentClick (e : any) : void {
        if (this.viewportBreakpoint === 'desktop') {
            return;
        }

        let target = e.target;

        while (target) {
            const actionsMenu = target.dataset.actionsMenu;

            if (actionsMenu) {
                this.isActionsMenuActive = (
                    actionsMenu === 'item' ? false :
                    actionsMenu === 'trigger' ? !this.isActionsMenuActive : this.isActionsMenuActive
                );
                return;
            }

            target = target.parentElement;
        }

        this.isActionsMenuActive = false;
    }

    public onHistoryTabMouseEvent (isVisible : boolean) : void {
        this.isHistoryTabHintVisible = !this.canViewHistory && !this.deviceService.device.touch && isVisible;
    }
}
