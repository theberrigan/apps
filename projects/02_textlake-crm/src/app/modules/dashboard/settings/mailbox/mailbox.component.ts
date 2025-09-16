import {Component, OnDestroy, ViewChild, ViewEncapsulation} from '@angular/core';
import {ActivatedRoute, Router} from '@angular/router';
import {Subscription} from 'rxjs';
import {DeviceService, ViewportBreakpoint} from '../../../../services/device.service';
import {TitleService} from '../../../../services/title.service';
import {UserData, UserService} from '../../../../services/user.service';
import {UiService} from '../../../../services/ui.service';
import {Mailbox, MailboxService} from '../../../../services/mailbox.service';
import {PopupComponent} from '../../../../widgets/popup/popup.component';
import {defer, deleteFromArray, int, isEmailValid, isIntString} from '../../../../lib/utils';
import {cloneDeep, forIn} from 'lodash';
import {LangService} from '../../../../services/lang.service';
import {PopupService} from '../../../../services/popup.service';
import {ToastService} from '../../../../services/toast.service';

type State = 'loading' | 'error' | 'empty' | 'list';
type EditorMode = 'create' | 'edit';

@Component({
    selector: 'mailbox',
    templateUrl: './mailbox.component.html',
    styleUrls: [ './mailbox.component.scss' ],
    encapsulation: ViewEncapsulation.None,
    host: {
        'class': 'mailbox-editor',
    }
})
export class MailboxSettingsComponent implements OnDestroy {
    public subs : Subscription[] = [];

    public viewportBreakpoint : ViewportBreakpoint;

    public state : State;

    public isSaving : boolean = false;

    public isTesting : boolean = false;

    public isDeleting : boolean = false;

    public mailboxes : Mailbox[];

    public editorMode : EditorMode;

    @ViewChild('editor')
    public editor : PopupComponent;

    public isEmailValid : boolean = false;

    public isEditorFormValid : boolean = false;

    public mailboxToEdit : Mailbox;

    public mailboxToEditIndex : number;

    public protocolOptions : any[] = [
        {
            display: 'IMAP',
            value: 'imap'
        }
    ];

    public protocolsMap : any;

    public isProtocolReadOnly : boolean = false;

    constructor (
        private router : Router,
        private route : ActivatedRoute,
        private titleService : TitleService,
        private userService : UserService,
        private langService : LangService,
        private deviceService : DeviceService,
        private uiService : UiService,
        private popupService : PopupService,
        private mailboxService : MailboxService,
        private toastService : ToastService,
    ) {
        this.state = 'loading';
        this.viewportBreakpoint = this.deviceService.viewportBreakpoint;
        this.titleService.setTitle('settings.mailboxes.page_title');

        this.applyUserData(this.userService.getUserData());
        this.addSub(this.userService.onUserDataUpdated.subscribe(userData => this.applyUserData(userData)));
        this.addSub(this.uiService.activateBackButton().subscribe(() => this.goBack()));

        this.addSub(this.deviceService.onResize.subscribe(message => {
            if (message.breakpointChange) {
                this.viewportBreakpoint = this.deviceService.viewportBreakpoint;
            }
        }));

        this.protocolsMap = this.protocolOptions.reduce((acc, protocol) => {
            acc[protocol.value] = protocol.display;
            return acc;
        }, {});

        this.addSub(this.mailboxService.fetchMailboxes().subscribe(
            (mailboxes : Mailbox[]) => {
                this.mailboxes = mailboxes;
                this.state = this.mailboxes.length ? 'list' : 'empty';

                this.route.queryParams.subscribe(queryParams => {
                    if (queryParams['action'] === 'create') {
                        this.onCreate();
                    }
                });
            },
            () => {
                this.state = 'error';
            }
        ));
    }

    public ngOnDestroy () : void {
        this.subs.forEach(sub => sub.unsubscribe());
        this.uiService.deactivateBackButton();
    }

    public addSub (sub : Subscription) : void {
        this.subs = [ ...this.subs, sub ];
    }

    public applyUserData (userData : UserData) : void {

    }

    public onDelete (mailbox : Mailbox) : void {
        this.popupService.confirm({
            message: [ 'settings.mailboxes.mailbox_confirm__message' ],
        }).subscribe(({ isOk }) => {
            if (isOk) {
                this.isDeleting = true;

                this.mailboxService.deleteMailbox(mailbox.key).subscribe(
                    () => {
                        deleteFromArray(this.mailboxes, mailbox);
                        this.toastService.create({
                            message: [ 'settings.mailboxes.delete_success__message' ]
                        });
                    },
                    () => {
                        this.toastService.create({
                            message: [ 'settings.mailboxes.delete_failed__message' ]
                        });
                    },
                    () => this.isDeleting = false
                );
            }
        });
    }

    public onEdit (mailbox : Mailbox) : void {
        this.editorMode = 'edit';
        this.mailboxToEdit = cloneDeep(mailbox);
        this.mailboxToEditIndex = this.mailboxes.indexOf(mailbox);
        this.prepareEditor();
        defer(() => this.editor.activate());
    }

    public onCreate () : void {
        this.editorMode = 'create';
        this.mailboxToEdit = new Mailbox();
        this.mailboxToEdit.protocol = this.protocolOptions[0].value;
        this.prepareEditor();
        defer(() => this.editor.activate());
    }

    public onSave () : void {
        if (!this.isEditorFormValid || this.isSaving || this.isTesting || this.isDeleting) {
            return;
        }

        this.isSaving = true;

        const mailboxToSave = this.getNormalizedMailbox(this.mailboxToEdit);

        if (this.editorMode === 'create') {
            this.mailboxService.createMailbox(mailboxToSave).subscribe(
                mailbox => {
                    this.mailboxes.push(mailbox);
                    this.onHideEditor();
                    this.toastService.create({
                        message: [ 'settings.mailboxes.save_success__message' ]
                    });
                },
                () => {
                    this.toastService.create({
                        message: [ 'settings.mailboxes.save_error__message' ]
                    });
                },
                () => this.isSaving = false
            );
        } else {
            this.mailboxService.updateMailbox(mailboxToSave).subscribe(
                () => {
                    mailboxToSave.password = null;
                    this.mailboxes[this.mailboxToEditIndex] = mailboxToSave;
                    this.onHideEditor();
                    this.toastService.create({
                        message: [ 'settings.mailboxes.save_success__message' ]
                    });
                },
                () => {
                    this.toastService.create({
                        message: [ 'settings.mailboxes.save_error__message' ]
                    });
                },
                () => this.isSaving = false
            );
        }
    }

    public onTest () : void {
        if (!this.editorMode || !this.isEditorFormValid || this.isSaving || this.isTesting || this.isDeleting) {
            return;
        }

        this.isTesting = true;

        this.mailboxService.testMailbox(this.getNormalizedMailbox(this.mailboxToEdit)).subscribe(
            isOk => {
                this.toastService.create({
                    message: [
                        isOk ?
                        'settings.mailboxes.test_success__message' :
                        'settings.mailboxes.test_error__message'
                    ]
                });
            },
            () => {
                this.toastService.create({
                    message: [ 'settings.mailboxes.test_error__message' ]
                });
            },
            () => this.isTesting = false
        );
    }

    public onHideEditor (byOverlay : boolean = false) : void {
        if (byOverlay) {
            return;
        }

        this.editor.deactivate().then(() => {
            this.editorMode = null;
            this.mailboxToEdit = null;
            this.mailboxToEditIndex = null;
            this.router.navigate([], {
                queryParams: {
                    action: null,
                },
                queryParamsHandling: 'merge'
            })
        });
    }

    public prepareEditor () : void {
        this.isEmailValid = false;
        this.isEditorFormValid = false;
        this.isProtocolReadOnly = this.protocolOptions.length <= 1;
        this.validate();
    }

    public validate () : void {
        defer(() => {
            let isValid : boolean = null;

            forIn(this.mailboxToEdit, (value, key) => {
                const valueStr = String(value).trim();

                switch (key) {
                    case 'email':
                        this.isEmailValid = isEmailValid(valueStr);
                        isValid = isValid != false && !!value && this.isEmailValid;
                        break;
                    case 'protocol':
                    case 'password':
                    case 'host':
                        isValid = isValid != false && !!value && !!valueStr;
                        break;
                    case 'port':
                        isValid = isValid != false && isIntString(valueStr);
                        break;
                }
                console.log(key, value, isValid);

                if (isValid === false) {
                    return false;
                }
            });

            this.isEditorFormValid = isValid;
        });
    }

    public getNormalizedMailbox (mailbox : Mailbox) : Mailbox {
        mailbox = cloneDeep(mailbox);

        mailbox.email = mailbox.email.trim();
        mailbox.password = mailbox.password.trim();
        mailbox.host = mailbox.host.trim();
        mailbox.port = int(mailbox.port);
        mailbox.protocol = mailbox.protocol.trim();

        return mailbox;
    }

    public goBack () : void {
        this.router.navigateByUrl('/dashboard/settings');
    }
}

