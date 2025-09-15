import {Component, OnDestroy, ViewChild, ViewEncapsulation} from '@angular/core';
import {ActivatedRoute, Router} from '@angular/router';
import {Subscription, zip} from 'rxjs';
import {DeviceService, ViewportBreakpoint} from '../../../../services/device.service';
import {TitleService} from '../../../../services/title.service';
import {UserData, UserRole, UserService} from '../../../../services/user.service';
import {UiService} from '../../../../services/ui.service';
import {PopupComponent} from '../../../../widgets/popup/popup.component';
import {Invitation, InvitationsService} from '../../../../services/invitations.service';
import {PopupService} from '../../../../services/popup.service';
import {cloneDeep} from 'lodash';
import {defer, deleteFromArray, isEmailValid, isSameObjectsLayout, updateObject} from '../../../../lib/utils';
import {LangService} from '../../../../services/lang.service';
import {ToastService} from '../../../../services/toast.service';


type ListState = 'loading' | 'error' | 'empty' | 'list';
type EditorMode = 'create' | 'edit';

interface State {
    sort : {
        by : string;
        direction : number;
    };
}

interface EditorRole {
    key : string;
    displayKey : string;
    isActive : boolean;
}

@Component({
    selector: 'invitations',
    templateUrl: './invitations.component.html',
    styleUrls: [ './invitations.component.scss' ],
    encapsulation: ViewEncapsulation.None,
    host: {
        'class': 'invitations-editor',
    }
})
export class InvitationsSettingsComponent implements OnDestroy {
    public subs : Subscription[] = [];

    public viewportBreakpoint : ViewportBreakpoint;

    public listState : ListState;

    public state : State;

    public stateChangeDebounceTimer : any = null;

    public isSaving : boolean = false;

    public isDeleting : boolean = false;

    public invitations : Invitation[];

    public roles : UserRole[];

    public editorMode : EditorMode;

    @ViewChild('editor')
    public editor : PopupComponent;

    public isEmailValid : boolean = false;

    public isEditorFormValid : boolean = false;

    public invitationToEdit : Invitation;

    public invitationToEditIndex : number;

    public editorRoles : EditorRole[];

    public datetimeDisplayFormat : string;

    public readonly sortOptions : any = [
        {
            value: 'email',
            display: 'settings.invitations.list.email'
        },
        {
            value: 'created',
            display: 'settings.invitations.list.date'
        },
    ];

    public readonly defaultState : State = {
        sort: {
            by: this.sortOptions[0].value,
            direction: 1
        }
    };

    constructor (
        private router : Router,
        private route : ActivatedRoute,
        private titleService : TitleService,
        private userService : UserService,
        private deviceService : DeviceService,
        private uiService : UiService,
        private popupService : PopupService,
        private langService : LangService,
        private invitationsService : InvitationsService,
        private toastService : ToastService,
    ) {
        this.listState = 'loading';
        this.viewportBreakpoint = this.deviceService.viewportBreakpoint;
        this.titleService.setTitle('settings.invitations.list.page_title');
        this.state = cloneDeep(this.defaultState);

        this.applyUserData(this.userService.getUserData());
        this.addSub(this.userService.onUserDataUpdated.subscribe(userData => this.applyUserData(userData)));
        this.addSub(this.uiService.activateBackButton().subscribe(() => this.goBack()));

        this.addSub(this.deviceService.onResize.subscribe(message => {
            if (message.breakpointChange) {
                this.viewportBreakpoint = this.deviceService.viewportBreakpoint;
            }
        }));

        this.addSub(zip(
            this.invitationsService.fetchInvitations(),
            this.invitationsService.fetchInvitationsListState(),
            this.userService.fetchRoles()
        ).subscribe(
            ([ invitations, state, roles ] : [ Invitation[], any, UserRole[] ]) => {
                state = state || {};

                if (isSameObjectsLayout(this.defaultState, state)) {
                    this.state = state;
                } else {
                    this.state = updateObject(this.defaultState, state);
                    this.saveState();
                }

                this.invitations = this.sortInvitations(invitations);
                this.roles = roles.sort((a, b) => a.key.localeCompare(b.key));

                this.listState = this.invitations.length ? 'list' : 'empty';

                this.route.queryParams.subscribe(queryParams => {
                    if (queryParams['action'] === 'create') {
                        this.onCreate();
                    }
                });
            },
            () => {
                this.listState = 'error';
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
        this.datetimeDisplayFormat = userData.settings.formats.datetime.display;
    }

    public sortInvitations (invitation : Invitation[]) : Invitation[] {
        if (!invitation || !invitation.length) {
            return invitation;
        }

        const { by, direction } = this.state.sort;

        return invitation.sort((i1, i2) => {
            let a = i1[by] === null ? '' : String(i1[by]),
                b = i2[by] === null ? '' : String(i2[by]);

            return (a.localeCompare(b) || i1.id.localeCompare(i2.id)) * direction;
        });
    }

    public saveState () : void {
        if (this.stateChangeDebounceTimer !== null) {
            clearTimeout(this.stateChangeDebounceTimer);
        }

        this.stateChangeDebounceTimer = setTimeout(() => {
            this.stateChangeDebounceTimer = null;
            this.invitationsService.saveInvitationsListState(this.state);
        }, 200);
    }

    public onOrderChange () : void {
        this.invitations = this.sortInvitations(this.invitations);
        this.saveState();
    }

    public onDelete (invitation : Invitation) : void {
        this.popupService.confirm({
            message: [ 'settings.invitations.list.confirm_delete', { email: invitation.email } ],
        }).subscribe(({ isOk }) => {
            if (isOk) {
                this.isDeleting = true;

                this.addSub(this.invitationsService.deleteInvitation(invitation.id).subscribe(
                    () => {
                        deleteFromArray(this.invitations, invitation);
                        this.listState = this.invitations.length === 0 ? 'empty' : 'list';
                        this.isDeleting = false;
                        this.toastService.create({
                            message: [ 'settings.invitations.list.delete_ok' ]
                        });
                    },
                    () => {
                        this.toastService.create({
                            message: [ 'settings.invitations.list.delete_error' ]
                        });
                        this.isDeleting = false;
                    }
                ));
            }
        });
    }

    public onEdit (invitation : Invitation) : void {
        this.editorMode = 'edit';
        this.invitationToEdit = cloneDeep(invitation);
        this.invitationToEditIndex = this.invitations.indexOf(invitation);
        this.prepareEditor();
        defer(() => this.editor.activate());
    }

    public onCreate () : void {
        this.editorMode = 'create';
        this.invitationToEdit = new Invitation();
        this.prepareEditor();
        defer(() => this.editor.activate());
    }

    public prepareEditor () : void {
        const invitationRoles = this.invitationToEdit.roles || [];
        this.editorRoles = this.roles.map(role => ({
            key: role.key,
            displayKey: 'settings.roles.names.' + role.key,
            isActive: invitationRoles.indexOf(role.key) !== -1
        }));
        this.isEmailValid = false;
        this.isEditorFormValid = false;
        this.validate();
    }

    public validate () : void {
        defer(() => {
            this.isEmailValid = isEmailValid((this.invitationToEdit.email || '').trim());
            this.isEditorFormValid = this.isEmailValid && this.editorRoles.some(r => r.isActive);
        });
    }

    public onSave () : void {
        if (!this.isEditorFormValid || this.isSaving || this.isDeleting) {
            return;
        }

        this.isSaving = true;
        this.invitationToEdit.roles = this.editorRoles.filter(r => r.isActive).map(r => r.key);

        if (this.editorMode === 'create') {
            this.addSub(this.invitationsService.createInvitation(this.invitationToEdit).subscribe(
                invitation => {
                    this.invitations.push(invitation);
                    this.listState = 'list';
                    this.onHideEditor();
                    this.isSaving = false;
                    this.toastService.create({
                        message: [ 'settings.invitations.editor.saved' ]
                    });
                },
                () => {
                    this.isSaving = false;
                    this.toastService.create({
                        message: [ 'settings.invitations.editor.unknown_error' ]
                    });
                }
            ));
        } else {
            this.addSub(this.invitationsService.updateInvitation(this.invitationToEdit).subscribe(
                invitation => {
                    this.invitations[this.invitationToEditIndex] = invitation;
                    this.onHideEditor();
                    this.isSaving = false;
                    this.toastService.create({
                        message: [ 'settings.invitations.editor.saved' ]
                    });
                },
                () => {
                    this.toastService.create({
                        message: [ 'settings.invitations.editor.unknown_error' ]
                    });
                    this.isSaving = false;
                }
            ));
        }
    }

    public onHideEditor (byOverlay : boolean = false) : void {
        if (byOverlay) {
            return;
        }

        this.invitations = this.sortInvitations(this.invitations);

        this.editor.deactivate().then(() => {
            this.editorMode = null;
            this.editorRoles = null;
            this.invitationToEdit = null;
            this.invitationToEditIndex = null;
            this.router.navigate([], {
                queryParams: {
                    action: null,
                },
                queryParamsHandling: 'merge'
            })
        });
    }

    public goBack () : void {
        this.router.navigateByUrl('/dashboard/settings');
    }
}

