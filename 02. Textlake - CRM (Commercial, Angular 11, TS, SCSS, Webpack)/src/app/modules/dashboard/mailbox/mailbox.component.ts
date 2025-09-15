import {
    Component,
    ElementRef,
    HostListener,
    OnDestroy,
    OnInit,
    Renderer2,
    ViewChild,
    ViewEncapsulation
} from '@angular/core';
import {Router} from '@angular/router';
import {Observable, Subscription} from 'rxjs';
import { CONFIG } from '../../../../../config/app/dev';
import {DeviceService, ViewportBreakpoint} from '../../../services/device.service';
import {Mailbox, MailboxFolder, MailboxMessage, MailboxService} from '../../../services/mailbox.service';
import {TitleService} from '../../../services/title.service';
import {UserData, UserService} from '../../../services/user.service';
import {DomService} from '../../../services/dom.service';
import {PopupComponent} from '../../../widgets/popup/popup.component';
import {OffersService} from '../../../services/offers.service';
import {cloneDeep} from 'lodash';
import {defer} from '../../../lib/utils';

type State = 'loading' | 'empty' | 'error' | 'ready';
type FoldersState = 'loading' | 'error' | 'empty' | 'ready';
type MessagesState = 'loading' | 'error' | 'empty' | 'ready';

@Component({
    selector: 'mailbox',
    templateUrl: './mailbox.component.html',
    styleUrls: [ './mailbox.component.scss' ],
    encapsulation: ViewEncapsulation.None,
    host: {
        'class': 'mailbox',
    }
})
export class MailboxComponent implements OnInit, OnDestroy {
    public viewportBreakpoint : ViewportBreakpoint;

    public subs : Subscription[] = [];

    public state : State;

    public foldersState : FoldersState;

    public messagesState : MessagesState;

    public datetimeDisplayFormat : string;

    public mailboxes : Mailbox[];

    public folders : MailboxFolder[];

    public activeMailbox : Mailbox;

    public activeFolder : MailboxFolder;

    public foldersSub : Subscription;

    public messagesSub : Subscription;

    public messageSub : Subscription;

    public messageCount : number;

    public messages : MailboxMessage[];

    public messagesPerPage : number = 20;

    public isButtonsDisabled : boolean = false;

    public colorPickerMessageId : string;

    public colorCodes : string[] = [
        'F44336', 'E91E63', '9C27B0', '673AB7', '3F51B5',
        '2196F3', '00BCD4', '009688', '4CAF50', '8BC34A',
        'CDDC39', 'FFEB3B', 'FFC107', 'FF9800', 'FF5722',
        '795548', '607D8B', '000000', '1B5E20', '827717'
    ];

    @ViewChild('messagePopup')
    public messagePopup : PopupComponent;

    @ViewChild('messageIframe')
    public messageIframe : ElementRef;

    @ViewChild('messageContent')
    public messageContent : ElementRef;

    public messageIframeHeight : number = 150;

    public messageCache : any = {};

    public activeMessage : MailboxMessage;

    // public iframeSizeUnlisten : any;

    public emailViewMode : 'iframe' | 'shadowDom';

    public offersFilters : any;

    public offerizeMode : string = null;

    public offerizeAttachments : any[] = null;

    public offerizeOffers : any[] = null;

    public offerizeOfferSelected : any = null;

    public offerizeAttachmentsSelected : any[] = null;

    public isOfferizeSubmitting : boolean = false;

    public isOffersLoading : boolean = false;

    @ViewChild('offerizePopup')
    public offerizePopup : PopupComponent;

    public uploadMailContent : boolean = true;

    public emailHtml : string;

    public maxEmailPopupWidth : number = null;

    public activeMenuMessage : MailboxMessage;

    public canConfigureMailboxes : boolean = false;

    constructor(
        private renderer : Renderer2,
        private router : Router,
        private titleService : TitleService,
        private userService : UserService,
        private mailboxService : MailboxService,
        private domService : DomService,
        private deviceService : DeviceService,
        private offerService : OffersService
    ) {
        this.titleService.setTitle('mailbox.page_title');

        this.viewportBreakpoint = this.deviceService.viewportBreakpoint;

        this.offersFilters = {
            status: 'any',
            name: '',
            page: 0,
            size: 10
        };

        this.applyUserData(this.userService.getUserData());
        this.addSub(this.userService.onUserDataUpdated.subscribe(userData => this.applyUserData(userData)));

        this.addSub(this.deviceService.onResize.subscribe(message => {
            if (message.breakpointChange) {
                this.viewportBreakpoint = this.deviceService.viewportBreakpoint;
            }
        }));

        this.fetchMailboxes();
    }

    public ngOnInit () : void {

    }

    public ngOnDestroy () : void {
        this.subs.forEach(sub => sub.unsubscribe());
        // if (this.iframeSizeUnlisten) {
        //     this.iframeSizeUnlisten();
        //     this.iframeSizeUnlisten = null;
        // }
    }

    public addSub (sub : Subscription) : void {
        this.subs = [ ...this.subs, sub ];
    }

    public applyUserData (userData : UserData) : void {
        this.datetimeDisplayFormat = userData.settings.formats.datetime.display;
        this.canConfigureMailboxes = userData.features.can('settings:mailbox');
    }

    public fetchMailboxes() : void {
        this.state = 'loading';

        this.addSub(this.mailboxService.fetchMailboxes().subscribe(
            (mailboxes : Mailbox[]) => {
                this.mailboxes = mailboxes || [];

                if (this.mailboxes.length) {
                    this.onChangeMailbox(this.mailboxes[0]);
                    this.state = 'ready';
                } else {
                    this.state = 'empty';
                    // this.router.navigateByUrl('/dashboard/settings/mailbox');
                }
            },
            () => {
                this.state = 'error';
            }
        ));
    }

    public onChangeMailbox (mailbox : Mailbox) : void {
        if (mailbox === this.activeMailbox) {
            return;
        }

        this.activeMailbox = mailbox;
        this.fetchFolders();
    }

    public fetchFolders() : void {
        if (!this.activeMailbox) {
            console.warn('fetchFolders called, but activeMailbox is empty.');
            return;
        }

        this.foldersState = 'loading';
        this.messagesState = 'loading';

        if (this.messageSub) {
            this.messageSub.unsubscribe();
        }

        if (this.messagesSub) {
            this.messagesSub.unsubscribe();
        }

        if (this.foldersSub) {
            this.foldersSub.unsubscribe();
        }

        this.foldersSub = this.mailboxService.fetchMailboxFolders(this.activeMailbox.key).subscribe(
            (folders : MailboxFolder[]) => {
                this.folders = folders;

                if (this.folders.length) {
                    this.onChangeFolder(this.folders[0]);
                    this.foldersState = 'ready';
                } else {
                    this.foldersState = 'empty';
                    this.messagesState = 'empty';
                }
            },
            () => {
                this.foldersState = 'error';
                this.messagesState = 'error';
            }
        );

        this.addSub(this.foldersSub);
    }

    public onChangeFolder(folder : MailboxFolder) : void {
        if (folder === this.activeFolder) {
            return;
        }

        this.activeFolder = folder;
        this.fetchMessages();
    }

    public fetchMessages(startIndex : number = 0, endIndex : number = 0) {
        if (!this.activeMailbox || !this.activeFolder) {
            console.warn('fetchFolders called, but activeMailbox is empty.');
            return;
        }

        this.messagesState = 'loading';

        if (this.messageSub) {
            this.messageSub.unsubscribe();
        }

        if (this.messagesSub) {
            this.messagesSub.unsubscribe();
        }

        this.messagesSub = this.mailboxService.fetchMessages(this.activeMailbox.key, this.activeFolder.fullName, startIndex, endIndex).subscribe(
            response => {
                this.messageCount = response.messageCount;
                this.messages = response.messages;

                if (this.messages.length) {
                    // this.onChangeFolder(this.folders[0]);
                    this.messagesState = 'ready';
                } else {
                    this.messagesState = 'empty';
                }
            },
            () => {
                this.messagesState = 'error';
            }
        );

        this.addSub(this.messagesSub);
    }

    public isCreateOfferButtonDisabled (message : MailboxMessage) : boolean {
        return this.isButtonsDisabled || !message || !!message.tag;
    }

    public isAddToOfferButtonDisabled (message : MailboxMessage) : boolean {
        return this.isButtonsDisabled || !message || !message.hasAttachment && !!message.tag;
    }

    public isPrevButtonDisabled() : boolean {
        return this.isButtonsDisabled || this.state !== 'ready' || this.foldersState !== 'ready' || this.messagesState !== 'ready' || !this.messageCount || !this.messages || !this.messages.length || this.messages[this.messages.length - 1].messageNumber <= 1;
    }

    public isNextButtonDisabled() : boolean {
        return this.isButtonsDisabled || this.state !== 'ready' || this.foldersState !== 'ready' || this.messagesState !== 'ready' || !this.messageCount || !this.messages || !this.messages.length || this.messages[0].messageNumber >= this.messageCount;
    }

    public prevPage() : void {
        const endIndex = Math.max(1, this.messages[this.messages.length - 1].messageNumber - 1);
        const startIndex = Math.max(1, endIndex - this.messagesPerPage);
        this.fetchMessages(startIndex, endIndex);
    }

    public nextPage() : void {
        const startIndex = Math.min(this.messageCount, this.messages[0].messageNumber + 1);
        const endIndex = Math.min(this.messageCount, startIndex + this.messagesPerPage);
        this.fetchMessages(startIndex, endIndex);
    }

    public isRefreshButtonDisabled() : boolean {
        return this.state !== 'ready' || this.foldersState !== 'ready' || this.messagesState === 'loading';
    }

    public refresh() : void {
        this.fetchMessages();
    }

    public isCurrentColor(currentCode : string, targetCode : string) : boolean {
        return (currentCode || '').toLowerCase() === (targetCode || '000').toLowerCase();
    }

    public onColorPickerTriggerClick(e : any, messageId : string) : void {
        this.domService.markEvent(e, 'colorPickerClick');
        this.colorPickerMessageId = messageId === this.colorPickerMessageId ? null : messageId;
    }

    public onColorCellClick(e : any, message : MailboxMessage, colorCode : string) : void {
        this.domService.markEvent(e, 'colorPickerClick');

        this.colorPickerMessageId = null;

        if (this.isCurrentColor(message.color, colorCode)) {
            return;
        }

        message.color = colorCode;

        this.mailboxService.saveColor(message.messageId, message.color).subscribe((response) => {
            console.log(response);
        });
    }

    public onColorPickerClick(e : any) : void {
        this.domService.markEvent(e, 'colorPickerClick');
    }

    @HostListener('document:click', [ '$event' ])
    public onDocumentClick(e : any) {
        if (!this.domService.hasEventMark(e, 'colorPickerClick')) {
            this.colorPickerMessageId = null;
        }

        if (!this.domService.hasEventMark(e, 'messageMenuToggleClick') && (!this.domService.hasEventMark(e, 'messageMenuClick') || this.domService.hasEventMark(e, 'messageMenuItemClick'))) {
            this.activeMenuMessage = null;
        }
    }

    public onMessageClick(e : any, message : MailboxMessage) : void {
        if (
            this.isButtonsDisabled ||
            this.domService.hasEventMark(e, 'colorPickerClick') ||
            this.domService.hasEventMark(e, 'messageButtonClick') ||
            this.activeMenuMessage
        ) {
            return;
        }

        const cacheKey = `${ this.activeMailbox.key }|${ this.activeFolder.fullName }|${ message.messageUID }`;

        if (this.messageCache[cacheKey]) {
            this.activeMessage = message;
            this.showMessagePopup(this.messageCache[cacheKey]);
            this.messagePopup.activate();
        } else {
            this.messagePopup.showSpinner();
            this.messagePopup.activate();

            this.isButtonsDisabled = true;

            if (this.messageSub) {
                this.messageSub.unsubscribe();
            }

            this.messageSub = this.mailboxService.fetchMessage(
                this.activeMailbox.key,
                this.activeFolder.fullName,
                message.messageUID
            ).subscribe((messageText : string) => {
                this.activeMessage = message;
                this.messageCache[cacheKey] = messageText;
                this.showMessagePopup(messageText);
                this.isButtonsDisabled = false;
            }, () => {
                console.warn('Error');
                this.isButtonsDisabled = false;
                this.onMessagePopupClose();
            });
        }

        this.addSub(this.messageSub);
    }

    public showMessagePopup(messageText : string) : void {
        this.messagePopup.showBox(true);
        this.messagePopup.activate().then(() => {
            this.emailHtml = messageText;
            this.messagePopup.showBox(false);
        });
    }

    public onMessageAction(message : MailboxMessage, action : 'create' | 'add') : void {
        if (this.isButtonsDisabled || action === 'create' && this.isCreateOfferButtonDisabled(message) || action === 'add' && this.isAddToOfferButtonDisabled(message)) {
            return;
        }

        this.onMessagePopupClose();

        this.offerizeMode = action;

        this.activeMessage = message;
        this.offerizeAttachments = this.activeMessage.hasAttachment ? this.activeMessage.attachmentNames : null;
        this.offerizeAttachmentsSelected = this.offerizeAttachments !== null ? [] : null;
        this.offersFilters.name = '';

        if (action === 'create' && !this.activeMessage.hasAttachment) {
            this.onOfferize();
            return;
        }

        this.offerizePopup.showSpinner();
        this.offerizePopup.activate();

        this.getOffers().then(() => {
            this.offerizePopup.showBox();
        }, () => {
            this.offerizePopup.deactivate();
        });
    }

    public getOffers () : Promise<any> {
        return new Promise((resolve, reject) => {
            this.isOffersLoading = true;
            this.offerService.fetchOffers(cloneDeep(this.offersFilters)).subscribe((response : any) => {
                this.offerizeOffers = response.offers;

                // Preselect already linked offer
                if (this.activeMessage.tag) {
                    this.offerizeOfferSelected = this.offerizeOffers.find(offer => offer.offerKey === this.activeMessage.tag) || null;
                }

                // Upload mail content if preselected offer exists. False otherwise
                this.uploadMailContent = !(this.offerizeOfferSelected && this.offerizeOfferSelected.offerKey === this.activeMessage.tag);

                this.isOffersLoading = false;
                resolve();
            }, () => {
                this.isOffersLoading = false;
                reject();
            });
        });
    }

    public onMessagePopupClose() : void {
        if (this.messagePopup) {
            this.messagePopup.deactivate().then(() => {
                this.emailHtml = null;
            });
        }
    }

    public getAttachmentDownloadUrl (attachmentName : string) : string {
        return `${ CONFIG.server.replace(/\/*$/, '') }/rest/v1/mailboxes/${ this.activeMailbox.key }/${ this.activeFolder.fullName }/email/${ this.activeMessage.messageUID }/attachment/${ encodeURIComponent(attachmentName) }`;
    }

    public checkOfferizeButtonsActivity () : boolean {
        return (this.offerizeAttachmentsSelected && this.offerizeAttachmentsSelected.length || this.uploadMailContent) &&
            (this.offerizeMode == 'create' || this.offerizeMode == 'add' && this.offerizeOfferSelected);
    }

    public onOfferize () {
        this.isOfferizeSubmitting = true;

        this.mailboxService .storeAttachments({
                folder: this.activeFolder.fullName,
                mailboxKey: this.activeFolder.mailboxKey,
                messageUID: this.activeMessage.messageUID,
                names: this.offerizeAttachmentsSelected || [],
                includeEmailContent: this.uploadMailContent
            }).subscribe(
                response => {
                    this.offerizePopup.deactivate();
                    this.isOfferizeSubmitting = false;

                    const offerKey : string = this.offerizeMode == 'add' ? this.offerizeOfferSelected.offerKey : 'create';

                    this.offerService.offerizeData = {
                        offerKey,
                        fromAddress: response.fromAddress,
                        attachments: response.files
                    };

                    this.router.navigateByUrl('/dashboard/offer/' + offerKey);
                },
                response => {
                    this.isOfferizeSubmitting = false;
                }
            );
    }

    public onOfferizePopupCloseRequest(byOverlay : boolean = false) : void {
        if (!byOverlay) {
            this.offerizePopup.deactivate();
        }
    }

    public isUploadMailContentDisabled () : boolean {
        return (this.offerizeOfferSelected && this.offerizeOfferSelected.offerKey === this.activeMessage.tag) || !this.offerizeAttachments || !this.offerizeAttachments.length;
    }

    public toggleAttachment (attachment) {
        if (this.offerizeAttachmentsSelected.indexOf(attachment) === -1) {
            this.offerizeAttachmentsSelected.push(attachment);
        } else {
            this.offerizeAttachmentsSelected.splice(this.offerizeAttachmentsSelected.indexOf(attachment), 1);
        }
    }

    public isAttachmentSelected (attachment) {
        return this.offerizeAttachmentsSelected.indexOf(attachment) !== -1;
    }

    public onOfferFilterKeyUp (event : any) : void {
        if (event.keyCode === 13) {
            event.stopPropagation();
            this.getOffers();
        }
    }

    public clearOffersFilter () : void {
        this.offersFilters.name = '';
        this.getOffers();
    }

    public isOfferSelected (offer) {
        return this.offerizeOfferSelected === offer;
    }

    public selectOffer (offer) {
        this.offerizeOfferSelected = offer;
        if (this.offerizeOfferSelected && this.offerizeOfferSelected.offerKey === this.activeMessage.tag) {
            this.uploadMailContent = false;
        }
    }

    public onEmailViewResize (requiredWidth : number) : void {
        this.maxEmailPopupWidth = requiredWidth <= 860 ? 860 : null;
    }

    public onMessageMenuToggle (e : any, message : MailboxMessage) : void {
        this.domService.markEvent(e, 'messageButtonClick');
        this.domService.markEvent(e, 'messageMenuToggleClick');
        this.activeMenuMessage = this.activeMenuMessage === message ? null : message;
    }

    public onTagClick (e : any) {
        this.domService.markEvent(e, 'messageButtonClick');
    }

    public onMessageMenuItemClick (e : any, message : MailboxMessage, action : 'create' | 'add') : void {
        this.domService.markEvent(e, 'messageMenuItemClick');
        this.onMessageAction(message, action);
    }

    public onMessageMenuClick (e : any) : void {
        this.domService.markEvent(e, 'messageMenuClick');
    }
}
