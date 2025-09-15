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
import {NotificationsState, PanelButtonMarkType} from './panel.types';
import {NOTIFICATIONS_TO_LOAD, NOTIFICATIONS_VISIBLE_MAX} from './panel.statics';
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

        this.loadNotification();
        this.subscribeToMqttMessages();

        this.applyUserData(this.userService.getUserData());
        // this.addSub(this.userService.onUserDataUpdated.subscribe(userData => this.applyUserData(userData)));

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

    }

    public ngAfterViewInit () : void {

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
        // this.addSub(
        //     this.userService.onMqttMessage.subscribe((message) => {
        //         // TODO(question): why 'user'?
        //         if (message.topic === 'user') {
        //             this.processMqttMessage(message.message);
        //         }
        //     })
        // );
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


    /** TASKS & NOTIFICATIONS COMMON
     * ----------------------------- **/

    public static parseNotificationMessageData (data : any) : any {
        return mapKeys(data ? data.split(';') : {}, (_, key) => 'p' + key);
    }

    public markAsViewed (entities : any[]) : void {
        const ids : number[] = entities.filter(e => !e.displayed).map(e => (e.displayed = true) && e.id);

        if (ids.length) {
            this.panelService.markAsViewed(ids).toPromise();  // toPromise() to trigger non-eager Observable
        }
    }


    /** PANEL
     * ----------------------------- **/

    @HostListener('animationend', [ '$event' ])
    public onAnimationEnd (e : any) {
        if (e.target.getAttribute('data-icon') === 'notifications') {
            this.isNotificationsIconAnimated = false;
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

        this.notificationsMarkType = settings.panel.notifications.markType as PanelButtonMarkType;
    }

    public onSignOut () : void {
        this.userService.signOut().then(() => {
            this.router.navigateByUrl('/auth/sign-in');
        });
    }

    public onShowSettings () : void {
        this.routerService.setQueryZ('profile');
    }

    public onVerifyEmail () : void {
        this.onShowEmailVerificationPopup.emit();
    }

    public onSwitchAccount (account : any) : void {
        // this.userService.switchAccount(account.id).subscribe(
        //     () => window.location.reload(),
        //     (error : any) => {
        //         console.warn('onSwitchAccount error:', error);
        //
        //         // TODO(ToastService):
        //         // this.toastService.create({
        //         //     type: 'error',
        //         //     message: '...'
        //         // });
        //     }
        // );
    }

    public onGoBack () : void {
        this.uiService.onGoBack.next();
    }
}
