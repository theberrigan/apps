import {Component, OnDestroy, ViewChild, ViewEncapsulation} from '@angular/core';
import {Router} from '@angular/router';
import {Subscription} from 'rxjs';
import {DeviceService, ViewportBreakpoint} from '../../../../services/device.service';
import {TitleService} from '../../../../services/title.service';
import {User, UserData, UserRole, UserService} from '../../../../services/user.service';
import {UiService} from '../../../../services/ui.service';
import {zip} from 'rxjs';
import {DomService} from '../../../../services/dom.service';
import {PopupService} from '../../../../services/popup.service';
import {defer, deleteFromArray} from '../../../../lib/utils';
import {PopupComponent} from '../../../../widgets/popup/popup.component';

type State = 'loading' | 'error' | 'empty' | 'list';

interface UserWithRoles {
    user : User;
    roles : {
        key : string,
        display : string,
        isActive : boolean,
        isActiveOnInit : boolean
    }[],
    activityRequest : Subscription,
    isMe : boolean;
}

interface EditorRoles {
    key : string,
    display : string,
}

@Component({
    selector: 'roles',
    templateUrl: './roles.component.html',
    styleUrls: [ './roles.component.scss' ],
    encapsulation: ViewEncapsulation.None,
    host: {
        'class': 'roles-editor',
    }
})
export class RolesSettingsComponent implements OnDestroy {
    public subs : Subscription[] = [];

    public viewportBreakpoint : ViewportBreakpoint;

    public state : State;

    public usersWithRoles : UserWithRoles[];

    public roles : EditorRoles[];

    public userWithRolesToEdit : UserWithRoles;

    @ViewChild('editor')
    public editor : PopupComponent;

    public isSaving : boolean = false;

    constructor (
        private router : Router,
        private titleService : TitleService,
        private userService : UserService,
        private deviceService : DeviceService,
        private uiService : UiService,
        private domService : DomService,
        private popupService : PopupService
    ) {
        this.state = 'loading';
        this.viewportBreakpoint = this.deviceService.viewportBreakpoint;
        this.titleService.setTitle('settings.roles.page_title');

        this.addSub(this.userService.onUserDataUpdated.subscribe(userData => this.applyUserData(userData)));
        this.addSub(this.uiService.activateBackButton().subscribe(() => this.goBack()));

        this.addSub(this.deviceService.onResize.subscribe(message => {
            if (message.breakpointChange) {
                this.viewportBreakpoint = this.deviceService.viewportBreakpoint;
            }
        }));

        this.addSub(zip(
            this.userService.fetchUsers(),
            this.userService.fetchRoles(),
        ).subscribe(
            ([ users, roles ] : [ User[], UserRole[] ]) => {
                const currentUserData = this.userService.getUserData();

                this.roles = roles.map(role => ({
                    key: role.key,
                    display: ('settings.roles.names.' + role.key)
                })).sort((a, b) => a.key.localeCompare(b.key));

                this.usersWithRoles = users.reduce((acc, user) => {
                    const userWithRoles : UserWithRoles = {
                        user,
                        roles: null,
                        activityRequest: null,
                        isMe: user.id === currentUserData.profile.user.id
                    };
                    userWithRoles.isMe ? acc.unshift(userWithRoles) : acc.push(userWithRoles);
                    return acc;
                }, []);

                this.state = this.usersWithRoles.length ? 'list' : 'empty';
            },
            () => this.state = 'error'
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

    public onUserClick (userWithRoles : UserWithRoles, e : any) : void {
        if (this.domService.hasEventMark(e, 'roleSwitchClick')) {
            return;
        }

        this.userWithRolesToEdit = userWithRoles;

        defer(() => {
            if (userWithRoles.roles) {
                this.editor.showBox();
                this.editor.activate();
                return;
            }

            this.editor.showSpinner();
            this.editor.activate();

            this.addSub(this.userService.fetchUserRoles(userWithRoles.user.id).subscribe(
                (userRoles : UserRole[]) => {
                    const userRolesKeys = userRoles.map(role => role.key);

                    this.userWithRolesToEdit.roles = this.roles.map(role => {
                        const isActive = userRolesKeys.indexOf(role.key) !== -1;

                        return {
                            key: role.key,
                            display: role.display,
                            isActive,
                            isActiveOnInit: isActive
                        }
                    });

                    this.editor.showBox();
                },
                () => {
                    this.onHideEditor();
                }
            ));
        });
    }

    public onSwitchActivity (userWithRoles : UserWithRoles, e : any) : void {
        this.domService.markEvent(e, 'roleSwitchClick');

        if (userWithRoles.activityRequest) {
            userWithRoles.activityRequest.unsubscribe();
        }

        const wasActive = userWithRoles.user.active;
        userWithRoles.user.active = !userWithRoles.user.active;

        const request = userWithRoles.activityRequest = this.userService.updateUser(userWithRoles.user).subscribe(
            (user : User) => {
                if (userWithRoles.activityRequest === request) {
                    userWithRoles.activityRequest = null;
                    userWithRoles.user = user;
                }

                request.unsubscribe();
            },
            (error) => {
                if (userWithRoles.activityRequest === request) {
                    userWithRoles.activityRequest = null;
                    userWithRoles.user.active = wasActive;
                }

                if (error.messageKey === 'error.subscription.limit') {
                    this.popupService.confirm({
                        message: [ 'settings.roles.update_subscription.message' ],
                        okButtonCaption: [ 'settings.roles.update_subscription.trueLabel' ],
                        cancelButtonCaption: [ 'settings.roles.update_subscription.falseLabel' ]
                    }).subscribe(({ isOk }) => {
                        if (isOk) {
                            this.router.navigateByUrl('/dashboard/settings/subscriptions');
                        }
                    });
                }

                request.unsubscribe();
            }
        );
    }

    public onHideEditor (byOverlay : boolean = false) : void {
        if (byOverlay) {
            return;
        }

        this.editor.deactivate().then(() => {
            this.userWithRolesToEdit = null;
        });
    }

    public onSave () : void {
        if (this.isSaving || !this.userWithRolesToEdit) {
            return;
        }

        this.isSaving = true;

        const userId = this.userWithRolesToEdit.user.id;

        const requests = this.userWithRolesToEdit.roles.reduce((acc, role) => {
            if (role.isActive !== role.isActiveOnInit) {
                acc.push(
                    role.isActive ?
                    this.userService.setUserRole(userId, role.key) :
                    this.userService.deleteUserRole(userId, role.key)
                );
            }
            return acc;
        }, []);

        if (!requests.length) {
            this.isSaving = false;
            this.onHideEditor();
            return;
        }

        this.addSub(zip(...requests).subscribe(
            () => {
                this.userWithRolesToEdit.roles.forEach(role => {
                    role.isActiveOnInit = role.isActive;
                });
                this.onHideEditor();
                this.isSaving = false;
            },
            () => {
                // TODO: show error toast
                this.isSaving = false
            }
        ));
    }

    public goBack () : void {
        this.router.navigateByUrl('/dashboard/settings');
    }
}

