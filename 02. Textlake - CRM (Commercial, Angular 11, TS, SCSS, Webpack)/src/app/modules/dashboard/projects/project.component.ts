import {
    AfterViewInit,
    Component, ElementRef,
    OnDestroy, OnInit, Renderer2, ViewChild,
    ViewEncapsulation
} from '@angular/core';
import {ActivatedRoute, CanDeactivate, Router} from '@angular/router';
import {
    ClientsService
} from '../../../services/client.service';
import {TitleService} from '../../../services/title.service';
import {forkJoin, Observable, of, Subscription, zip} from 'rxjs';
import * as copyToClipboard from 'copy-to-clipboard';
import {LangService} from '../../../services/lang.service';
import {UserData, UserService} from '../../../services/user.service';
import {CurrenciesService} from '../../../services/currencies.service';
import {UiService} from '../../../services/ui.service';
import {PopupService} from '../../../services/popup.service';
import {AbstractControl, FormArray, FormBuilder, FormControl, FormGroup} from '@angular/forms';
import {DeviceService, ViewportBreakpoint} from '../../../services/device.service';
import {
    HistoryRecord,
    Project,
    ProjectServiceAssignment, ProjectServiceItem,
    ProjectServiceProvider,
    ProjectsService
} from '../../../services/projects.service';
import {CompanyService, Coordinator} from '../../../services/company.service';
import {mergeMap, tap} from 'rxjs/operators';
import {defer, divFloat, mulFloat, setSelectionRange, str2regexp} from '../../../lib/utils';
import {Attachment, OffersService, OfferTransactionsResponse} from '../../../services/offers.service';
import {FilesService} from '../../../services/file.service';
import {FileUploader} from '../../../widgets/file-uploader/file-uploader.class';
import {cloneDeep, values} from 'lodash';
import {ToastService} from '../../../services/toast.service';
import {CalcService, RoundingRule} from '../../../services/calc.service';

type Tab = 'details' | 'services' | 'documents' | 'shipping' | 'transactions' | 'history';
type State = 'loading' | 'error' | 'ready';
type CommentField = 'publicComment' | 'privateComment';
type HistoryState = 'awaiting' | 'loading' | 'empty' | 'error' | 'ready';
type TransactionsState = 'awaiting' | 'loading' | 'empty' | 'error' | 'ready';

interface DatetimeFormats {
    select : string;
    display : string;
}

interface SelectOption {
    display : string;
    value : any;
}

interface StatusSelectOption {
    display : string;
    key : string;
    id : number;
}

interface ServiceProviderWrap {
    projectServiceId : number;
    providers : ProjectServiceProvider[];
}

interface AssignmentWrap {
    assignment : ProjectServiceAssignment;
    service : ProjectServiceItem;
    serviceProvider : ProjectServiceProvider;
    isUploading : boolean;
}

interface AttachmentCommentToEdit {
    uuid : string;
    commentField : CommentField;
}

interface FileCache {
    [ uuid : string ] : {
        state : 'awaiting' | 'loading' | 'error' | 'ready',
        url : string
    }
}

/*
* TODO:
*  - 'Services' tab hint + disable tab
*  - mobile tabs icons
*  - mobile layouts for transactions and history tabs
*  - test mobile back button
*  - как себя ведёт вкладка Docs, когда загружен новый документ
*  - учесть canEdit и canViewHisotry, и задисейблить сю форму, если !canEdit
*  - After save: realod history & transactions
*
* load/save project -> create this.attachments -> buildForm
* upload file -> add to this.attachments -> add to form
* */

@Component({
    selector: 'project-editor',
    templateUrl: './project.component.html',
    styleUrls: [ './project.component.scss' ],
    encapsulation: ViewEncapsulation.None,
    host: {
        'class': 'project-editor',
        '[class.project-editor_tabs-compensate]': "layout === 'editor'"
    }
})
export class ProjectEditorComponent implements OnInit, AfterViewInit, OnDestroy, CanDeactivate<boolean | Promise<boolean>> {
    public viewportBreakpoint : ViewportBreakpoint;

    public canEdit : boolean;

    public canReadHistory : boolean;

    public isHistoryTabHintVisible : boolean = false;

    public datetimeFormats : DatetimeFormats;

    public subs : Subscription[] = [];

    public isSaving : boolean = false;

    public hasChanges : boolean;

    public activeTab : Tab;

    public state : State;

    public layout : 'editor' | 'assignment-editor';

    public editorForm : FormGroup;

    public roFields : any;

    public projectKey : string;

    public project : Project;

    public serviceProviders : ServiceProviderWrap[];

    public assignments : AssignmentWrap[];

    public coordinatorOptions : {
        display : string,
        value : number
    }[];

    public langs : any;

    public statusOptions : StatusSelectOption[];

    // -------------------

    public assignmentEditorMode : 'create' | 'edit';

    // -------------------

    @ViewChild('instructionText')
    public instructionText : ElementRef;

    @ViewChild('instructionEditor')
    public instructionEditor : ElementRef;

    public isInstructionEditorEnabled : boolean = false;

    public instructionEditorHeight : number;

    // -----------------

    @ViewChild('documentCommentEditor')
    public documentCommentEditor : ElementRef;

    public attachmentCommentToEdit : AttachmentCommentToEdit;

    // ----------------

    public transactionsState : TransactionsState;

    public transactions : OfferTransactionsResponse;

    // ----------------

    public historyState : HistoryState;

    public history : HistoryRecord[];

    // -----------------

    @ViewChild('uploaderInput')
    public uploaderInput : ElementRef;

    public uploader : FileUploader;

    public assignmentToUploadOutcome : AssignmentWrap;

    // ------------------------

    public assignmentEditorServicesOrder = {
        by: 'name',
        direction: 1
    };

    public assignmentEditorServices : ProjectServiceProvider[];

    public assignmentEditorFilteredServices : ProjectServiceProvider[];

    public assignmentEditorOpenedServices : any;

    public assignmentEditorFilterDebounceTimer : any = null;

    public assignmentEditorFilterText : string;

    public assignmentToEdit : AssignmentWrap;

    public assignmentToEditIndex : number;

    public scrollY : number;

    public assignmentEditorSortOptions = [
        {
            display: 'projects.editor.translator_name__table_th',
            value: 'name'
        },
        {
            display: 'projects.editor.translator_cpu__table_th',
            value: 'feePerUnit'
        },
        {
            display: 'projects.editor.translator_email__table_th',
            value: 'email'
        },
        {
            display: 'projects.editor.translator_phone__table_th',
            value: 'phone'
        },
        {
            display: 'projects.editor.translator_extra__table_th',
            value: 'extraService'
        }
    ];

    // ----------------

    public assignmentsToDelete : AssignmentWrap[];

    public roundingRule : RoundingRule;

    public constructor (
        private renderer : Renderer2,
        private router : Router,
        private route : ActivatedRoute,
        private formBuilder : FormBuilder,
        private titleService : TitleService,
        private langService : LangService,
        private clientsService : ClientsService,
        private currenciesService : CurrenciesService,
        private userService : UserService,
        private uiService : UiService,
        private deviceService : DeviceService,
        private popupService : PopupService,
        private projectsService : ProjectsService,
        private offersService : OffersService,
        private filesService : FilesService,
        private companyService : CompanyService,
        private calcService : CalcService,
        private toastService : ToastService
    ) {

    }

    public ngOnInit () : void {
        this.route.params.subscribe((params) => {
            if (params.key) {
                this.cleanup();
                this.init(params.key);
            }
        });
    }

    public ngAfterViewInit () : void {
        window.scrollTo(0, 0);
    }

    public ngOnDestroy () : void {
        this.cleanup();
        this.uiService.deactivateBackButton();
    }

    public init (projectKey : string) : void {
        this.layout = 'editor';
        this.activeTab = 'details';
        this.state = 'loading';
        this.historyState = 'awaiting';
        this.isSaving = false;
        this.hasChanges = false;
        this.assignments = null;
        this.assignmentsToDelete = [];
        this.project = null;
        this.editorForm = null;
        this.statusOptions = null;
        this.langs = null;
        this.coordinatorOptions = null;
        this.serviceProviders = null;
        this.roFields = null;
        this.assignmentEditorMode = null;
        this.isInstructionEditorEnabled = false;
        this.instructionEditorHeight = null;
        this.attachmentCommentToEdit = null;
        this.transactionsState = null;
        this.transactions = null;
        this.historyState = null;
        this.history = null;
        this.uploader = null;
        this.assignmentToUploadOutcome = null;
        this.assignmentEditorServicesOrder = {
            by: 'name',
            direction: 1
        };
        this.assignmentEditorServices = null;
        this.assignmentEditorFilteredServices = null;
        this.assignmentEditorOpenedServices = null;
        this.assignmentEditorFilterDebounceTimer = null;
        this.assignmentEditorFilterText = null;
        this.assignmentToEdit = null;
        this.assignmentToEditIndex = null;
        this.scrollY = null;
        this.roundingRule = null;

        // const projectKey : string = this.projectKey = this.route.snapshot.params['key'];
        this.projectKey = projectKey;

        this.titleService.setTitle('projects.editor.page_title', { projectKey });

        this.applyUserData(this.userService.getUserData());
        this.addSub(this.userService.onUserDataUpdated.subscribe(userData => this.applyUserData(userData)));

        this.viewportBreakpoint = this.deviceService.viewportBreakpoint;
        this.addSub(this.deviceService.onResize.subscribe((message) => {
            if (message.breakpointChange) {
                this.viewportBreakpoint = message.breakpointChange.current;
            }
        }));

        this.addSub(this.uiService.activateBackButton().subscribe(() => this.goBack()));

        this.buildEditorForm();

        this.addSub(zip(
            this.projectsService.fetchProject(projectKey),
            this.projectsService.fetchProjectCoordinators(projectKey),
            this.projectsService.fetchProjectsStatuses(),
            this.langService.fetchLanguages(),
            this.companyService.fetchCalcRule(),
        ).pipe(
            mergeMap(([ project, coordinators, statuses, langs, roundingRule ]) => {
                this.roundingRule = <RoundingRule>roundingRule;

                this.project = new Project(project);  // TODO: prepareProject()
                this.statusOptions = statuses;
                this.langs = langs.reduce((acc : any, { value, display }) => {
                    acc[value] = display;
                    return acc
                }, {});

                this.coordinatorOptions = coordinators.map(coordinator => ({
                    value: coordinator.id,
                    display: [ coordinator.firstName, coordinator.lastName ].join(' ')
                }));

                const services = this.project.services;

                return services.length ? forkJoin(
                    of(services),
                    zip(...services.map(s => this.projectsService.fetchProjectServiceProviders(s.id)))
                ) : of([ services, [] ]);
            }),
            mergeMap(([ services, responses ] : [ ProjectServiceItem[], any[] ]) => {
                const providersMap = {};

                this.serviceProviders = responses.map((providers, i) => {
                    const projectServiceId = services[i].id;
                    providersMap[projectServiceId] = providers;
                    return { providers, projectServiceId };
                });

                return services.length ? forkJoin(
                    of(services),
                    of(providersMap),
                    zip(...services.map(s => this.projectsService.fetchProjectServiceAssignments(s.id)))
                ) : of([ services, providersMap, [] ]);
            })
        ).subscribe(([ services, providers, responses ] : [ ProjectServiceItem[], any, any[] ]) => {
            this.assignments = responses.reduce((acc, assignments, i) => {
                const service = services[i];

                assignments.forEach(assignment => {
                    const serviceProvider = providers[service.id].find(p => p.translatorId === assignment.translator.id);
                    acc.push({
                        assignment,
                        service,
                        serviceProvider,
                        isUploading: false
                    });
                });

                return acc;
            }, [] as AssignmentWrap[]);

            // (this.project, this.assignments, this.serviceProviders);

            this.updateForm();
            this.state = 'ready';
        }, () => this.state = 'error'));
    }

    public cleanup () : void {
        this.subs.forEach(sub => sub.unsubscribe());
        this.subs = [];
    }

    public addSub (sub : Subscription) : void {
        this.subs = [ ...this.subs, sub ];
    }

    public canDeactivate () : Promise<boolean> {
        return new Promise<boolean>((resolve) => {
            if (!this.canEdit || this.editorForm.pristine && !this.hasChanges) {
                resolve(true);
                return;
            }

            this.popupService.confirm({
                message: [ 'guards.discard' ],
            }).subscribe(({ isOk }) => resolve(isOk));
        });
    }

    public applyUserData (userData : UserData) : void {
        this.canEdit = userData.features.can('edit:projects');
        this.canReadHistory = userData.features.can('view:changelog');
        this.datetimeFormats = <DatetimeFormats><any>userData.settings.formats.datetime;

        if (this.editorForm) {
            if (this.canEdit && !this.isSaving) {
                this.editorForm.enable();
            } else {
                this.editorForm.disable();
            }
        }
    }

    public switchTab (tab : Tab) : void {
        if (tab === 'history' && !this.canReadHistory) {
            if (this.deviceService.device.touch) {
                this.popupService.alert({
                    message: [ 'log.history_tab_alert__message' ]
                });
            }
            return;
        }

        this.activeTab = tab;

        switch (tab) {
            case 'transactions':
                this.fetchTransactions();
                break;
            case 'history':
                this.fetchHistory();
                break;
        }
    }

    public buildEditorForm () : void {
        const project = this.project;

        this.editorForm = this.formBuilder.group({
            details: this.formBuilder.group({
                status: [ project && project.status ? project.status.id : 0 ],
                coordinator: [ project && project.coordinator ? project.coordinator.id : -1 ],
                deadline: [ project && project.deadline ],
            }),
            documents: this.formBuilder.group({
                instruction: [ project && (project.instruction || '').trim() || '' ],
                items: this.formBuilder.group({})
            }),
            shipping: this.formBuilder.group({
                companyName: [ project && project.shippingAddress.companyName || '' ],
                firstName: [ project && project.shippingAddress.firstName || '' ],
                lastName: [ project && project.shippingAddress.lastName || '' ],
                street: [ project && project.shippingAddress.street || '' ],
                suite: [ project && project.shippingAddress.suite || '' ],
                zipCode: [ project && project.shippingAddress.zipCode || '' ],
                state: [ project && project.shippingAddress.state || '' ],
                country: [ project && project.shippingAddress.country || '' ],
                city: [ project && project.shippingAddress.city || '' ],
            })
        });

        const formItems = (<FormGroup>this.editorForm.get('documents.items'));

        (project && project.attachments || []).forEach(attachment => {
            formItems.addControl(attachment.uuid, this.formBuilder.group({
                publicComment: this.formBuilder.control(attachment.publicComment),
                privateComment: this.formBuilder.control(attachment.privateComment)
            }));
        });

        //this.canEdit ? this.editorForm.enable() : this.editorForm.disable();
    }

    public updateForm () : void {
        const project = this.project;

        this.buildEditorForm();

        const fields : any = {
            projectKey: (project.key || '').toUpperCase(),
            created: project.created,
            client: project.client && project.client.name || '',
            contact: project.contact ? [ project.contact.title, project.contact.fullName ].join(' ') : '',
            email: project.contact && project.contact.email || '',
            phone: project.contact && project.contact.phone || '',
            fax: project.contact && project.contact.fax || '',
            externalId: project.externalId || '',
            notary: !!project.notary,
            description: project.description || ''
        };

        [
            [ 'priority', 'priority' ],
            [ 'deliveryType', 'delivery_type' ],
            [ 'field', 'subject_area' ],
            [ 'translationType', 'translation_type' ]
        ].forEach(([ projectProp, i18nProp ]) => {
            let value = project[projectProp];

            if (value) {
                const key = i18nProp + '.' + value.key.replace(/\./g, '_');
                const message = this.langService.translate(key);
                value = message === key ? value.name : message;
            }

            fields[projectProp] = value;
        });

        this.roFields = fields;
    }

    public fetchTransactions () : void {
        if (this.transactionsState === 'empty' || this.transactionsState === 'ready') {
            return;
        }

        this.transactionsState = 'loading';

        this.addSub(this.offersService.fetchOfferTransactions(this.project.offerKey).subscribe((transactions : OfferTransactionsResponse) => {
            this.transactions = transactions;
            this.transactionsState = transactions.transactions.length ? 'ready' : 'empty';
        }, () => {
            this.transactionsState = 'error';
        }));
    }

    public fetchHistory () : void {
        if (!this.canReadHistory || this.historyState === 'empty' || this.historyState === 'ready') {
            return;
        }

        this.historyState = 'loading';

        this.addSub(this.projectsService.fetchProjectHistory(this.project.key).subscribe((records : HistoryRecord[]) => {
            let itemsCount = 0;
            records = records || [];

            records.forEach(record => {
                record.items.forEach(item => {
                    [ 'action', 'oldValue', 'newValue' ].forEach(prop => {
                        let matchCount = 0;
                        item[prop] = (item[prop] || '').replace(/\./g, () => matchCount++ >= 2 ? '_' : '.');
                    });
                    item.isEven = itemsCount++ % 2 === 0;
                });
            });

            this.history = records;
            this.historyState = this.history.length ? 'ready' : 'empty';
        }, () => {
            this.historyState = 'error';
        }));
    }

    public onSave () : void {
        if (!this.canEdit || this.state !== 'ready' || this.isSaving) {
            return;
        }

        this.isSaving = true;
        this.editorForm.disable();

        let tasks = [];

        this.assignments.forEach(assignmentWrap => {
            const { assignment, service } = assignmentWrap;

            let request : Observable<any>,
                assignmentData : any = {
                    attachmentId: assignment.attachmentId,
                    begin: assignment.begin,
                    end: assignment.end,
                    units: assignment.units,
                    translatorServiceId: assignment.translatorServiceId,
                    comment: assignment.comment,
                    internalDeadline: assignment.internalDeadline,
                    accepted: assignment.accepted,
                    reclaimedAmount: assignment.reclaimedAmount,
                    reclamationComment: assignment.reclamationComment
                };

            if (assignment.id) {
                request = this.projectsService.updateAssignment(service.id, assignment.id, assignmentData);
            } else {
                assignmentData.attachmentId = assignment.attachmentId;
                request = this.projectsService.createAssignment(service.id, assignmentData);
            }

            tasks.push(request.pipe(tap(assignment => assignmentWrap.assignment = assignment)));
        });

        this.assignmentsToDelete.forEach(aw => {
            tasks.push(this.projectsService.deleteAssignment(aw.service.id, aw.assignment.id));
        });

        this.addSub((tasks.length ? zip(...tasks) : of([])).pipe(mergeMap(() => {
            const { details, documents, shipping } = this.editorForm.getRawValue();

            const projectData : any = {
                assignments: this.assignments.map(aw => aw.assignment),
                instruction: documents.instruction,
                shippingAddress: shipping,
                statusId: details.status,
                coordinatorId: details.coordinator,
                attachments: this.project.attachments.map(attachment => {
                    const comments = documents.items[attachment.uuid];

                    if (comments) {
                        attachment.privateComment = comments.privateComment;
                        attachment.publicComment = comments.publicComment;
                    }

                    return attachment;
                })
            };

            // console.log(JSON.stringify(projectData, null, '    '));

            return zip(
                this.projectsService.updateProject(this.project.key, projectData),
                of(details.deadline),
                this.projectsService.updateDeadline(this.project.key, details.deadline)
            );
        })).subscribe(([ project, deadline, isDeadlineUpdated ] : [ Project, any, boolean ]) => {
            project = this.project = new Project(project);

            if (isDeadlineUpdated) {
                project.deadline = deadline;
            } else {
                console.warn('Can`t save deadline');
            }

            defer(() => this.updateForm());

            this.assignments.forEach(assignmentWrap => {
                assignmentWrap.service = this.project.services.find(s => s.id === assignmentWrap.assignment.serviceItemId);
            });

            this.assignmentsToDelete = [];
            this.isSaving = false;
            this.hasChanges = false;
            this.editorForm.markAsPristine();
            this.canEdit && this.editorForm.enable();

            if (this.activeTab === 'history') {
                this.historyState = 'awaiting';
                this.fetchHistory();
            }

            this.toastService.create({
                message: [ 'projects.editor.save_success__message' ]
            });
        }));
    }

    // ------------------------

    public enableInstructionEditor () : void {
        if (!this.canEdit || this.isSaving) {
            return;
        }

        this.instructionEditorHeight = this.instructionText.nativeElement.getBoundingClientRect().height;
        this.isInstructionEditorEnabled = true;

        window.requestAnimationFrame(() => {
            if (this.isInstructionEditorEnabled) {
                setSelectionRange(this.instructionEditor.nativeElement, this.getInstructionText().length);
                this.instructionEditor.nativeElement.focus();
            }
        });
    }

    public disableInstructionEditor () : void {
        if (!this.canEdit) {
            return;
        }

        this.editorForm.get('documents.instruction').setValue(this.getInstructionText().trim());
        this.isInstructionEditorEnabled = false;
    }

    public onInstructionEditorKeyUp (e : KeyboardEvent) : void {
        if (e.keyCode === 27 || e.keyCode === 13 && e.ctrlKey) {
            this.disableInstructionEditor();
        }
    }

    public getInstructionText () : string {
        return this.editorForm.getRawValue().documents.instruction || '';
    }

    // ------------------------

    public hasAttachments () : boolean {
        return (this.project && this.project.attachments || []).length > 0;
    }

    public fileCache : FileCache;

    public onFileDownload (uuid : string, e? : any) : void {
        if (e) {
            e.preventDefault();
        }

        if (!this.fileCache) {
            this.fileCache = {};
        }

        let cache = this.fileCache[uuid];

        if (!cache) {
            this.fileCache[uuid] = cache = {
                state: 'awaiting',
                url: null
            };
        }

        if (cache.state === 'awaiting' || cache.state === 'error') {
            cache.state = 'loading';

            this.addSub(this.filesService.fetchFileUrl(uuid).subscribe(url => {
                cache.url = url;
                cache.state = 'ready';
                this.downloadFile(url);
            }, () => {
                cache.state = 'error';
            }));
        } else if (cache.state === 'ready') {
            this.downloadFile(cache.url);
        }
    }

    public downloadFile (url : string) : void {
        const anchor = this.renderer.createElement('a');
        this.renderer.setProperty(anchor, 'href', url);
        this.renderer.setProperty(anchor, 'download', '');
        this.renderer.addClass(anchor, 'hidden');
        this.renderer.appendChild(document.body, anchor);
        anchor.click();
        this.renderer.removeChild(this.renderer.parentNode(anchor), anchor);
    }

    public onDocumentCommentKeyUp (e : any) : void {
        if (e.keyCode === 27 || e.keyCode === 13 && e.ctrlKey) {
            this.deactivateDocumentCommentEditor();
        }
    }

    public activateDocumentCommentEditor (attachment : Attachment, commentField : CommentField) : void {
        if (!this.canEdit || this.isSaving) {
            return;
        }

        this.attachmentCommentToEdit = {
            uuid: attachment.uuid,
            commentField
        };

        window.requestAnimationFrame(() => {
            if (this.attachmentCommentToEdit) {
                const comment = this.getDocumentCommentText(attachment.uuid, commentField);
                setSelectionRange(this.documentCommentEditor.nativeElement, comment.length);
                this.documentCommentEditor.nativeElement.focus();
            }
        });
    }

    public deactivateDocumentCommentEditor () : void {
        if (!this.canEdit) {
            return;
        }

        const commentToEdit = this.attachmentCommentToEdit;

        if (commentToEdit) {
            const comment = this.getDocumentCommentText(commentToEdit.uuid, commentToEdit.commentField).trim();
            this.editorForm.get('documents.items.' + commentToEdit.uuid + '.' + commentToEdit.commentField).setValue(comment);
            this.attachmentCommentToEdit = null;
        }
    }

    public getDocumentCommentText (attachmentUuid : string, commentField : CommentField) : string {
        return this.editorForm.getRawValue().documents.items[attachmentUuid][commentField] || '';
    }

    // -------------

    public initFileUploader () : void {
        this.uploader = new FileUploader({
            autoUpload: false,
            disableMultipart: true
        });

        this.uploader.onAfterAddingFile = (file : any) => {
            file.method = 'PUT';
        };

        this.uploader.onAfterAddingAll = (queue : any[]) => {
            const item = queue[0];
            const assignmentWrap = this.assignmentToUploadOutcome;
            assignmentWrap.isUploading = true;
            this.assignmentToUploadOutcome = null;

            this.addSub(this.projectsService.presignOutcome(assignmentWrap.assignment.id, item.file.name).subscribe(
                (presignData : any) => {
                    item.uploadConfig = {
                        assignmentWrap,
                        uploadUrl: presignData.url,
                        fileUuid: presignData.uuid
                    };

                    this.uploader.uploadAll();
                },
                () => {
                    item.cancel();
                    assignmentWrap.isUploading = false;
                }
            ));

            return { fileItems: queue };
        };

        this.uploader.onBeforeUploadItem = (file : any) => {
            this.uploader.setOptions({
                url: file.uploadConfig.uploadUrl
            });

            file.withCredentials = false;
        };

        this.uploader.onSuccessItem = (file : any) => {
            const { assignmentWrap } = file.uploadConfig;
            const fileUuid = assignmentWrap.assignment.outcomeUuid = file.uploadConfig.fileUuid;

            if (this.fileCache) {
                delete this.fileCache[fileUuid];
            }

            assignmentWrap.isUploading = false;
            this.hasChanges = true;
        };

        this.uploader.onErrorItem = (file : any) => {
            console.warn("ERROR", file);
            file.uploadConfig.assignmentWrap.isUploading = false;
            // TODO: show error
        };
    }

    public showOutcomeUploadDialog (assignmentWrap : AssignmentWrap) : void {
        if (!this.uploader) {
            this.initFileUploader();
        }

        this.assignmentToUploadOutcome = assignmentWrap;
        this.uploaderInput.nativeElement.click();
    }

    // ------------------

    public onDeleteAssignment (assignmentWrap : AssignmentWrap) : void {
        if (!this.canEdit) {
            return;
        }

        this.popupService.confirm({
            message: [ 'projects.editor.confirm_assignment__message' ],
        }).subscribe(({ isOk }) => {
            if (isOk) {
                if (assignmentWrap.assignment.id) {
                    this.assignmentsToDelete.push(assignmentWrap);
                }
                this.assignments.splice(this.assignments.indexOf(assignmentWrap), 1);
                this.hasChanges = true;
            }
        });
    }

    public sortAssignmentEditorServices (servicesProviders : ProjectServiceProvider[]) : ProjectServiceProvider[] {
        const servicesToSort = [ ...(servicesProviders || []) ];

        if (!servicesToSort.length) {
            return servicesToSort;
        }

        const { by, direction } = this.assignmentEditorServicesOrder;

        return servicesToSort.sort((s1, s2) => {
            if (by === 'extraService') {
                return ((Number(s1.extraService) - Number(s2.extraService)) || (s1.translatorServiceId - s2.translatorServiceId)) * direction;
            }

            let a : string,
                b : string;

            if (by === 'name') {
                a = [ s1.lastName, s1.firstName, s1.middleName ].join(' ');
                b = [ s2.lastName, s2.firstName, s2.middleName ].join(' ');
            } else {
                a = s1[by] === null ? '' : String(s1[by]);
                b = s2[by] === null ? '' : String(s2[by]);
            }

            return (a.localeCompare(b) || (s1.translatorServiceId - s2.translatorServiceId)) * direction;
        });
    }

    public collectAssignmentEditorServices (projectServiceId : number) : ProjectServiceProvider[] {
        return this.serviceProviders.find(sp => sp.projectServiceId === projectServiceId).providers;
    }

    public addAssignment (service : ProjectServiceItem, attachmentId : string = null) : void {
        if (!this.canEdit) {
            return;
        }

        this.assignmentEditorServices = this.sortAssignmentEditorServices(this.collectAssignmentEditorServices(service.id));
        this.assignmentEditorFilteredServices = this.assignmentEditorServices;
        this.assignmentToEdit = {
            service,
            serviceProvider: null,
            isUploading: false,
            assignment: new ProjectServiceAssignment({
                attachmentId: attachmentId || '',
                units: service.in || 0
            })
        };
        this.assignmentEditorOpenedServices = {};
        this.assignmentToEditIndex = -1;
        this.assignmentEditorMode = 'create';
        this.scrollY = window.scrollY;
        this.layout = 'assignment-editor';
        this.scrollToY(0);
    }

    public editAssignment (service : ProjectServiceItem, assignmentWrap : AssignmentWrap) : void {
        if (!this.canEdit) {
            return;
        }

        this.assignmentEditorServices = this.sortAssignmentEditorServices(this.collectAssignmentEditorServices(service.id));
        this.assignmentEditorFilteredServices = this.assignmentEditorServices;
        this.assignmentToEdit = {
            service,
            serviceProvider: assignmentWrap.serviceProvider,
            isUploading: false,
            assignment: cloneDeep(assignmentWrap.assignment)
        };
        this.assignmentEditorOpenedServices = {};
        this.assignmentToEditIndex = this.assignments.indexOf(assignmentWrap);
        this.assignmentEditorMode = 'edit';
        this.scrollY = window.scrollY;
        this.layout = 'assignment-editor';
        this.scrollToY(0);
    }

    public onCloseAssignmentEditor (confirm : boolean) : void {
        if (confirm) {
            console.log(this.assignmentToEdit, this.assignmentToEdit.assignment.reclaimedAmount);
            if (this.assignmentToEditIndex >= 0) {
                this.assignments[this.assignmentToEditIndex] = this.assignmentToEdit;
            } else {
                this.assignmentToEdit.assignment.pricePerUnit = this.assignmentToEdit.serviceProvider.feePerUnit;
                this.assignments.push(this.assignmentToEdit);
            }

            this.hasChanges = true;
        }

        this.layout = 'editor';
        // TODO: this.clearServiceFilter();
        this.scrollToY(this.scrollY);
        this.scrollY = 0;
        this.assignmentEditorMode = null;
        this.assignmentToEdit = null;
        this.assignmentToEditIndex = null;
        this.assignmentEditorServices = [];
        this.assignmentEditorFilteredServices = [];
        this.assignmentEditorOpenedServices = {};

        if (this.assignmentEditorFilterDebounceTimer) {
            clearTimeout(this.assignmentEditorFilterDebounceTimer);
            this.assignmentEditorFilterDebounceTimer = null;
        }
    }

    public onConfirmAssigmentChanges () : void {
        if (!this.assignmentToEdit.serviceProvider) {
            this.onCloseAssignmentEditor(false);
            return;
        }

        this.popupService.confirm({
            message: [ 'projects.editor.confirm_assignment_popup__message' ],
            okButtonCaption: [ 'projects.editor.confirm_assignment_popup__ok' ],
            cancelButtonCaption: [ 'projects.editor.confirm_assignment_popup__cancel' ]
        }).subscribe(({ isOk }) => this.onCloseAssignmentEditor(isOk));
    }

    public onAssignmentEditorOrderChange () : void {
        defer(() => {
            this.assignmentEditorFilteredServices = this.sortAssignmentEditorServices(this.assignmentEditorFilteredServices);
            this.assignmentEditorOpenedServices = {};
        });
    }

    public onAssignmentEditorFilterKeyUp () : void {
        if (this.assignmentEditorFilterDebounceTimer !== null) {
            clearTimeout(this.assignmentEditorFilterDebounceTimer);
        }

        this.assignmentEditorFilterDebounceTimer = setTimeout(() => {
            this.assignmentEditorFilterDebounceTimer = null;
            this.assignmentEditorOpenedServices = {};

            const filter = (this.assignmentEditorFilterText || '').trim();

            if (filter) {
                const regexp = new RegExp(str2regexp(filter), 'i');
                // console.log(regexp);

                this.assignmentEditorFilteredServices = this.sortAssignmentEditorServices(
                    this.assignmentEditorServices.filter(service => {
                        return regexp.test([ service.lastName, service.firstName, service.middleName ].join(' '));
                    })
                );
            } else {
                this.assignmentEditorFilteredServices = this.sortAssignmentEditorServices(this.assignmentEditorServices);
            }
        }, 300);
    }

    public getAttachmentName (attachmentId : string) : string {
        return (this.project.attachments.find(a => a.uuid === attachmentId) || { name: '' }).name;
    }

    public toggleAssignmentEditorService (index : number) : void {
        this.assignmentEditorOpenedServices[index] = !this.assignmentEditorOpenedServices[index];
    }

    public toggleAssignmentEditorAllServices () : void {
        const targetValue = !this.hasOpenedProviders();
        this.assignmentEditorOpenedServices = {};
        for (let i = 0; i < this.assignmentEditorFilteredServices.length; i++) {
            this.assignmentEditorOpenedServices[i] = targetValue;
        }
    }

    public hasOpenedProviders () : boolean {
        return values(this.assignmentEditorOpenedServices).some(v => v);
    }

    public assignmentEditorProviderChange (serviceProvider : ProjectServiceProvider) : void {
        this.assignmentToEdit.assignment.translator.id = serviceProvider.translatorId;
        this.assignmentToEdit.assignment.translatorServiceId = serviceProvider.translatorServiceId;
        this.assignmentToEdit.serviceProvider = serviceProvider;
    }

    // ------------------------

    public calcServiceCost (targetService : ProjectServiceItem) : number {
        return this.assignments.reduce((sum, assignmentWrap) => {
            const { service, assignment } = assignmentWrap;

            if (service.id === targetService.id) {
                const assignmentFeeBeforeRounding = divFloat(mulFloat(assignment.pricePerUnit, assignment.units), 100) - assignment.reclaimedAmount;
                const assignmentFee = this.calcService.round(assignmentFeeBeforeRounding, this.roundingRule);
                sum += assignmentFee;
            }

            return sum;
        }, 0);
    }

    public calcServiceProfit (targetService : ProjectServiceItem) : number {
        return targetService.net - this.calcServiceCost(targetService);
    }

    public calcServiceMargin (targetService : ProjectServiceItem) : number {
        let net : number = targetService.net,
            expenses : number = this.calcServiceCost(targetService),
            profit = net - expenses;

        const margin : number = this.calcService.round(mulFloat(divFloat(profit, net), 10000), this.roundingRule);
        return Number.isFinite(margin) && margin > 0 ? divFloat(margin, 100) : 0;
    }

    public calcTranslatorMargin (assignmentWrap : AssignmentWrap) : number {
        const { service, assignment } = assignmentWrap;

        const
            expensesBeforeRounding = divFloat(mulFloat(assignment.pricePerUnit, assignment.units), 100) - assignment.reclaimedAmount,
            expenses = this.calcService.round(expensesBeforeRounding, this.roundingRule),
            profit = service.net - expenses,
            margin = this.calcService.round(mulFloat(divFloat(profit, service.net), 10000), this.roundingRule);

        return Number.isFinite(margin) && margin > 0 ? divFloat(margin, 100) : 0;
    }

    public getLanguageName (code : string) : string {
        code = code.toUpperCase();
        return this.langs[code] || code;
    }

    // ------------------------

    public getDeadlineControl () : FormControl {
        return (<FormControl>(<FormGroup>this.editorForm.controls['details']).controls['deadline']);
    }

    public scrollToY (y : number) : void {
        setTimeout(() => window.scrollTo(0, y), 0);
    }

    public goBack () : void {
        switch (this.layout) {
            case 'editor':
                this.router.navigateByUrl('/dashboard/projects');
                break;
            case 'assignment-editor':
                this.onConfirmAssigmentChanges();
                break;
        }
    }

    public onHistoryTabMouseEvent (isVisible : boolean) : void {
        this.isHistoryTabHintVisible = !this.canReadHistory && !this.deviceService.device.touch && isVisible;
    }

    public onCopy (text : string) : void {
        text = (text || '').trim();

        if (text.length === 0) {
            return;
        }

        if (copyToClipboard(text)) {
            this.toastService.create({
                message: [ 'projects.editor.copy_success' ]
            });
        }
    }
}
