import {
    AfterViewInit,
    Component, ElementRef,
    EventEmitter, HostListener, OnDestroy,
    OnInit,
    Output, Renderer2,
    ViewChild,
    ViewEncapsulation
} from '@angular/core';
import {DeviceService, ViewportBreakpoint} from '../../../services/device.service';
import {MqttMessageType, UserData, UserService} from '../../../services/user.service';
import {ActivatedRoute, Router} from '@angular/router';
import {Paginator, UiService} from '../../../services/ui.service';
import {Subject, Subscription} from 'rxjs';
import {includes, isArray, mapKeys, merge, remove, some} from 'lodash';
import {DomService} from '../../../services/dom.service';
import {animate, style, transition, trigger} from '@angular/animations';
import {debounceTime, tap} from 'rxjs/operators';
import {RouterService} from '../../../services/router.service';
import {NotificationsState, PanelButtonMarkType, TasksPagingState, TasksState, TaskStatus} from './panel.types';
import {getTaskStatuses, NOTIFICATIONS_TO_LOAD, NOTIFICATIONS_VISIBLE_MAX, TASKS_TO_LOAD} from './panel.statics';
import {PanelService} from './panel.service';
import {defer} from '../../../lib/utils';

// TODO(router:offers,translators,clients,invites): Add links to quick menu
// TODO(laziness): add screen-anti-click for onSignOut method


@Component({
    selector: 'panel',
    exportAs: 'panel',
    templateUrl: './panel.component.html',
    styleUrls: [ './panel.component.scss' ],
    encapsulation: ViewEncapsulation.None,
    host: {
        'class': 'panel',
    },
    animations: [
        trigger('showTaskItem', [
            transition(':enter', [
                style({ 'background-color': '#dee6f1' }),
                animate('1s ease-out', style({ 'background-color': '#fff' }))
            ])
        ])
    ]
})
export class PanelComponent implements OnInit, OnDestroy, AfterViewInit {
    @ViewChild('userMenu')
    public userMenu : any;

    public plusMenuButtonsVisibility : any;

    public isCreateMenuActive : boolean = false;

    public viewportBreakpoint : ViewportBreakpoint = null;

    @Output()
    public onNavToggle = new EventEmitter<void>();

    @Output()
    public onShowEmailVerificationPopup : EventEmitter<void> = new EventEmitter<void>();

    public isBackButtonActive : boolean = false;

    public userData : UserData;

    public altAccounts : any[];

    public subs : Subscription[] = [];

    public listeners : any[] = [];

    // Tasks
    // ---------------------

    @ViewChild('tasksContentEl')
    public tasksContentEl : ElementRef;

    @ViewChild('tasksContinueEl')
    public tasksContinueEl : ElementRef;

    public tasksRequestSub : Subscription;

    public tasksPaginator : Paginator;

    public isTasksIconAnimated : boolean = false;

    public tasksMarkType : PanelButtonMarkType = null;

    public tasksState : TasksState = 'loading';

    public tasksPagingState : TasksPagingState = 'hidden';

    public unviewedTasks : number = 0;

    public tasks : any[] = [];  // defer(() => this.recountTasks());

    public tasksStatuses : TaskStatus[];

    public onTasksStatusChecked = new Subject<void>();

    public _isTasksActive : boolean = false;

    public set isTasksActive (isActive : boolean) {
        if ((this._isTasksActive = isActive)) {
            this.markTasksAsViewed();
        }
    }

    public get isTasksActive () : boolean {
        return this._isTasksActive;
    }

    // Notifications
    // ----------------------

    @ViewChild('notificationsMenu')
    public notificationsMenu : any;

    public notificationsRequestSub : Subscription;

    public isNotificationsIconAnimated : boolean = false;

    public notificationsMarkType : PanelButtonMarkType = null;

    public notificationsState : NotificationsState = 'loading';

    public unviewedNotifications : number = 0;

    public notifications : any[] = [];

    public _isNotificationsMenuActive : boolean = false;

    public set isNotificationsMenuActive (isActive : boolean) {
        if (this.viewportBreakpoint === 'mobile' && this._isNotificationsMenuActive !== isActive) {
            this.setPageScroll(!isActive);
        }

        if ((this._isNotificationsMenuActive = isActive)) {
            this.markNotificationsAsViewed();
        }
    }

    public get isNotificationsMenuActive () : boolean {
        return this._isNotificationsMenuActive;
    }

    public setPageScroll (isActive : boolean) : void {
        if (isActive) {
            this.renderer.removeClass(document.body, 'tasks_scroll_disabled');
        } else {
            this.renderer.addClass(document.body, 'tasks_scroll_disabled');
        }
    }

    constructor (
        private router : Router,
        private route : ActivatedRoute,
        private routerService : RouterService,
        private renderer : Renderer2,
        private deviceService : DeviceService,
        private userService : UserService,
        private uiService : UiService,
        private domService : DomService,
        private panelService : PanelService
    ) {
        this.viewportBreakpoint = this.deviceService.viewportBreakpoint;

        this.userService.fetchFromStorage('tasksCheckedStatusesIds').subscribe((checkedStatusesIds : number[]) => {
            this.tasksStatuses = !checkedStatusesIds ? getTaskStatuses() : getTaskStatuses().map(status => {
                status.isChecked = includes(checkedStatusesIds, status.id);
                return status;
            });

            if (!checkedStatusesIds) {
                this.saveCheckedTasksStatuses();
            }

            this.addSub(
                this.onTasksStatusChecked.pipe(
                    tap(() => this.onTaskStatusChangeDebounce()),
                    debounceTime(800)
                ).subscribe(() => this.onTasksReload())
            );

            this.loadTasks('reload', 0, TASKS_TO_LOAD);
        });

        this.loadNotification();
        this.subscribeToMqttMessages();

        this.applyUserData(this.userService.getUserData());
        this.addSub(this.userService.onUserDataUpdated.subscribe(userData => this.applyUserData(userData)));

        this.addSub(
            this.deviceService.onResize.subscribe((message) => {
                if (message.breakpointChange) {
                    this.viewportBreakpoint = this.deviceService.viewportBreakpoint;
                }

                this.deactivateNotifications();
            })
        );

        this.addSub(
            this.uiService.onSetupBackButton.subscribe((isActive) => {
                this.isBackButtonActive = isActive;
            })
        );

        // Use it in other components to show and listen back button <-
        // this.uiService.activateBackButton().subscribe(() => {
        //     this.uiService.deactivateBackButton();
        //     console.log('Go back');
        // });
    }

    public ngOnInit () : void {
        // this.setupTasksScrollListener();
    }

    public ngAfterViewInit () : void {
        defer(() => this.setupTasksScrollListener());
    }

    public ngOnDestroy () : void {
        this.subs.forEach(sub => sub.unsubscribe());
        this.listeners.forEach(unlisten => unlisten());
    }

    public addSub (sub : Subscription) : void {
        this.subs = [ ...this.subs, sub ];
    }

    public addListener (listener : any) : void {
        this.listeners = [ ...this.listeners, listener ];
    }

    public subscribeToMqttMessages () : void {
        this.addSub(
            this.userService.onMqttMessage.subscribe((message) => {
                // TODO(question): why 'user'?
                if (message.topic === 'user') {
                    this.processMqttMessage(message.message);
                }
            })
        );
    }

    public processMqttMessage (message : any) : void {
        switch (message.type) {
            case MqttMessageType.Notification:
            case MqttMessageType.Profile:
                if (this.processNotifications(message) && !this.isNotificationsMenuActive) {
                    this.animateNotificationsIcon();
                }

                if (message.type === MqttMessageType.Profile) {
                    // TODO(ToastService):
                    // this.toastService.create({
                    //     type: 'success',
                    //     message: message.message
                    // });
                }

                break;
            case MqttMessageType.Task:
                if (this.processTasks(message, false) && !this.isTasksActive) {
                    this.animateTasksIcon();
                }

                break;
            default:
                console.warn('Unknown MQTT message type:', message);
        }
    }


    /** NOTIFICATIONS
     * ----------------------------- **/

    public loadNotification () : void {
        if (this.notificationsRequestSub) {
            this.notificationsRequestSub.unsubscribe();
        }

        this.notificationsState = 'loading';
        this.notifications = [];
        this.recountNotifications();

        this.notificationsRequestSub = (
            this.panelService
                .fetchNotifications(NOTIFICATIONS_TO_LOAD)
                .subscribe((notifications : any[]) => {
                    console.log('Notifications:', notifications);
                    // TODO: delete ---------------
                    // notifications.push({
                    //     id: 301,
                    //     type: 3,
                    //     message: "Thank you for joining TEXTLAKE translation manager! Please update your Profile and select the language you would like to use.",
                    //     params: null,
                    //     link: "/settings/user",
                    //     displayed: true
                    // });
                    // ----------------------
                    this.notificationsState = 'ok';
                    this.processNotifications(notifications || []);
                }, () => {
                    this.notificationsState = 'error';
                    this.notifications = [];
                    this.recountNotifications();
                }, () => {
                    this.notificationsRequestSub = null;
                })
        );
    }

    public processNotifications (notifications : any | any[]) : boolean {
        if (!notifications) {
            return false;
        } else if (!isArray(notifications)) {
            notifications = [ notifications ];
        }

        if (!notifications.length) {
            return false;
        }

        // TODO(server): when server will send message as i18n, use 'notification.message | translate : notification.messageData'
        notifications = notifications.map((notification) => {
            return {
                message: notification.message,
                messageData: PanelComponent.parseNotificationMessageData(notification.params),
                link: notification.link ? ('/dashboard' + notification.link) : null,
                displayed: notification.displayed !== false,
                id: notification.id
            };
        });

        this.notifications = [
            ...notifications,
            ...this.notifications
        ].slice(0, NOTIFICATIONS_VISIBLE_MAX);

        if (this.isNotificationsMenuActive) {
            this.markNotificationsAsViewed();
        } else {
            this.recountNotifications();
        }

        return true;
    }

    public recountNotifications () : void {
        this.unviewedNotifications = this.notifications.filter(n => !n.displayed).length;
    }

    public animateNotificationsIcon () : void {
        this.isNotificationsIconAnimated = true;
    }

    public markNotificationsAsViewed () : void {
        this.markAsViewed(this.notifications);
        this.recountNotifications();
    }

    public deactivateNotifications () : void {
        if (this.viewportBreakpoint === 'mobile') {
            this.isNotificationsMenuActive = false;
        } else if (this.notificationsMenu) {
            this.notificationsMenu.isActive = false;
        }
    }

    public toggleNotifications (e : any) : void {
        if (this.viewportBreakpoint === 'mobile') {
            this.isNotificationsMenuActive = !this.isNotificationsMenuActive;
        } else if (this.notificationsMenu) {
            this.notificationsMenu.toggle(e);
        }
    }

    public onNotificationsToggle (isActive : boolean) : void {
        this.isNotificationsMenuActive = isActive;
    }


    /** TASKS
     * ----------------------------- **/

    public get checkedTaskStatusesIds () : number[] {
        return (this.tasksStatuses || []).filter(status => status.isChecked).map(status => status.id);
    }

    public setupTasksScrollListener () : void {
        if (!this.tasksContentEl) {
            console.warn('Tasks content element not found');
            return;
        }

        const tasksContentEl = this.tasksContentEl.nativeElement;

        this.addListener(
            this.renderer.listen(tasksContentEl, 'scroll', () => {
                if (this.tasksPagingState !== 'button') {
                    return;
                }

                const spaceLeft = (
                    tasksContentEl.scrollHeight -
                    tasksContentEl.scrollTop -
                    tasksContentEl.clientHeight -
                    (this.tasksContinueEl && this.tasksContinueEl.nativeElement.clientHeight || 0)
                );

                if (spaceLeft < 100) {
                    this.continueLoadTasks();
                }
            })
        );
    }

    public continueLoadTasks () : void {
        // tasksPagingState === 'button' - the most important sign we can continue loading
        if (this.tasksPagingState !== 'button') {
            return;
        }

        console.warn('CONTINUE LOADING');
        this.loadTasks('continue', this.tasksPaginator.number + 1, this.tasksPaginator.size);
    }

    public onTaskStatusChangeDebounce () : void {
        this.tasksState = 'loading';
        this.tasksPagingState = 'hidden';
    }

    public onTasksReload () : void {
        this.saveCheckedTasksStatuses();
        this.loadTasks('reload', 0, TASKS_TO_LOAD);
    }

    public saveCheckedTasksStatuses () : void {
        this.userService.saveToStorage('tasksCheckedStatusesIds', this.checkedTaskStatusesIds);
    }

    public loadTasks (mode : 'reload' | 'continue', page : number, size : number) : void {
        if (this.tasksRequestSub) {
            this.tasksRequestSub.unsubscribe();
        }

        if (mode === 'reload') {
            this.tasksState = 'loading';
            this.tasksPagingState = 'hidden';
            this.tasks = [];
            this.recountTasks();
        } else if (mode === 'continue') {
            this.tasksState = 'ok';
            this.tasksPagingState = 'loading';
        }

        this.tasksRequestSub = (
            this.panelService
                .fetchTasks(page, size, this.checkedTaskStatusesIds)
                .subscribe((response : any) => {
                    if (!response) {
                        this.tasksState = 'error';
                        this.tasksPagingState = 'hidden';
                        this.tasks = [];
                        this.recountTasks();
                        return;
                    }

                    console.log('Tasks:', response.tasks);

                    this.tasksPaginator = new Paginator(response);
                    this.processTasks(response.tasks || [], true);
                    this.tasksPagingState = this.tasks.length && this.tasksPaginator.next ? 'button' : 'hidden';
                    this.tasksState = 'ok';
                }, () => {
                    this.tasksState = 'error';
                    this.tasksPagingState = 'hidden';
                    this.tasks = [];
                    this.recountTasks();
                }, () => {
                    this.tasksRequestSub = null;
                })
        );
    }

    public processTasks (newTasks : any | any[], toEnd : boolean) : boolean {
        if (!newTasks) {
            return false;
        } else if (!isArray(newTasks)) {
            newTasks = [ newTasks ];
        }

        // Two effect:
        // 1. Filter out broken tasks without status
        // 2. Filter out tasks not corresponding to status filter
        newTasks = newTasks.filter(task => includes(this.checkedTaskStatusesIds, task.status));

        if (!newTasks.length) {
            return false;
        }

        newTasks = newTasks.map((task) => {
            // If tasks with task.id already exists in this.tasks then we must eject
            // it from this.tasks, modify and insert it back on the top of this.tasks
            const existingTask = remove(this.tasks, oldTask => oldTask.id === task.id)[0] || {};

            task = merge(existingTask, task);

            let link = null;

            // TODO(server): add offers, etc.
            switch (task.group) {
                case 'project':
                    link = '/dashboard/project/' + task.link;
                    break;
            }

            return {
                priority: task.priority,
                status: this.tasksStatuses.find(status => status.id == task.status),
                message: 'panel.tasks.messages.' + task.message.replace(/\./g, '_') + '__message',
                messageData: PanelComponent.parseNotificationMessageData(task.params),
                user: task.user || null,
                updated: task.updated,
                displayed: task.displayed !== false,
                id: task.id,
                link
            };
        });

        this.tasks = toEnd ? [ ...this.tasks, ...newTasks ] : [ ...newTasks, ...this.tasks ];

        if (this.isTasksActive) {
            this.markTasksAsViewed();
        } else {
            this.recountTasks();
        }

        return true;
    }

    public recountTasks () : void {
        this.unviewedTasks = this.tasks.filter(t => !t.displayed).length;
    }

    public animateTasksIcon () : void {
        this.isTasksIconAnimated = true;
    }


    /** TASKS & NOTIFICATIONS COMMON
     * ----------------------------- **/

    public markTasksAsViewed () : void {
        this.markAsViewed(this.tasks);
        this.recountTasks();
    }

    public static parseNotificationMessageData (data : any) : any {
        return mapKeys(data ? data.split(';') : {}, (_, key) => 'p' + key);
    }

    public markAsViewed (entities : any[]) : void {
        const ids : number[] = entities.filter(e => !e.displayed).map(e => (e.displayed = true) && e.id);

        if (ids.length) {
            this.panelService.markAsViewed(ids).toPromise();  // toPromise() to trigger non-eager Observable
        }
    }

    public toggleTasks () : void {
        this.isTasksActive = !this.isTasksActive;
        this.setPageScroll(!this.isTasksActive);
    }

    public deactivateTasks () : void {
        this.isTasksActive = false;
        this.setPageScroll(true);
    }


    /** PANEL
     * ----------------------------- **/

    @HostListener('animationend', [ '$event' ])
    public onAnimationEnd (e : any) {
        switch (e.target.getAttribute('data-icon')) {
            case 'notifications':
                this.isNotificationsIconAnimated = false;
                break;
            case 'tasks':
                this.isTasksIconAnimated = false;
                break;
        }

        console.log('Animation end:', e.target.getAttribute('data-icon'));
    }

    public applyUserData (userData : UserData) : void {
        console.log('APPLY USER SETTINGS', userData);
        const { profile, settings, features } = this.userData = userData;

        if (profile.alternativeUsers && profile.alternativeUsers.length > 1) {
            const accounts = profile.alternativeUsers;
            const haveSameCompany = accounts.every((account) => account.companyName === accounts[0].companyName);

            this.altAccounts = accounts.map((account : any) => {
                const userName = [ account.firstName, account.lastName ].join(' ').trim();

                return {
                    id: account.id,
                    name: haveSameCompany ? userName : (account.companyName + (userName ? (': ' + userName) : ''))
                }
            });
        } else {
            this.altAccounts = null;
        }

        this.tasksMarkType = settings.panel.tasks.markType as PanelButtonMarkType;
        this.notificationsMarkType = settings.panel.notifications.markType as PanelButtonMarkType;

        const plusItems = {
            offer:      features.can('edit:offers'),
            translator: features.can('edit:translators'),
            client:     features.can('edit:clients'),
            invite:     features.can('settings:invitations')
        };

        this.plusMenuButtonsVisibility = some(plusItems, value => !!value) ? plusItems : null;
    }

    public onSignOut () : void {
        this.userService.signOut().then(() => {
            this.router.navigateByUrl('/auth/sign-in');
        });
    }

    public onGoBack () : void {
        this.uiService.onGoBack.next();
    }

    public onVerifyEmail () : void {
        this.onShowEmailVerificationPopup.emit();
    }

    public onShowSettings () : void {
        this.routerService.setQueryZ('profile');
    }

    public onSwitchAccount (account : any) : void {
        this.userService.switchAccount(account.id).subscribe(
            () => window.location.reload(),
            (error : any) => {
                console.warn('onSwitchAccount error:', error);

                // TODO(ToastService):
                // this.toastService.create({
                //     type: 'error',
                //     message: '...'
                // });
            }
        );
    }

    // <div style="position: fixed; bottom: 30%; left: 0; z-index: 1000000;" (click)="$event.preventDefault(); $event.stopPropagation();">
    //     <button type="button" style="padding: 10px 20px; margin: 5px;" (click)="userService.createNotification()">Notif</button>
    //     <button type="button" style="padding: 10px 20px; margin: 5px;" (click)="__createFakeTask()">Task</button>
    // </div>

    // public __createFakeTask () {
    //     this.processTasks({
    //         "id": Math.ceil(Math.random() * 10000),
    //         "priority": 2,
    //         "message": "task.project.deadline.2",
    //         "params": "P-2017-91",
    //         "status": 0,
    //         "user": null,
    //         "created": "2019-02-05T09:58:01.000+0000",
    //         "updated": "2019-02-06T07:58:01.000+0000",
    //         "link": "P-2017-91",
    //         "group": "project",
    //         "displayed": false
    //     }, false);
    //
    //     if (!this.isTasksActive) {
    //         this.animateTasksIcon();
    //     }
    // }
}
