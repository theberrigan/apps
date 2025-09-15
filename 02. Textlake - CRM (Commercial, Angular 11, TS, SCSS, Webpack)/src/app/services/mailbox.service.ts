import { Injectable } from '@angular/core';
import {Observable, throwError} from 'rxjs';
import {catchError, map, retry, take} from 'rxjs/operators';
import {HttpService} from './http.service';
import {UserService} from './user.service';

export class Mailbox {
    email : string = '';
    host : string = '';
    key : string = '';
    password : string = '';
    port : number = null;
    protocol : string = null;
    securedConnection : boolean = false;
}

export interface MailboxFolder {
    displayNameKey : string;
    fullName : string;
    mailboxKey : string;
    messagesCount : number;
    name : string;
}

export interface MailboxMessage {
    attachmentNames : string[];
    color : string;
    decodedAttachmentNames : string[];
    from : string;
    fromPerson : string;
    hasAttachment : boolean;
    messageId : string;
    messageNumber : number;
    messageUID : number;
    receivedDate : string;
    subject : string;
    tag : string;
    tagType : 'OFFER' | 'PROJECT';
}

@Injectable({
    providedIn: 'root'
})
export class MailboxService {
    constructor (
        private http : HttpService,
        private userService : UserService
    ) {}

    public fetchMailboxes () : Observable<Mailbox[]> {
        return this.http.get('endpoint://mailboxes.getMailboxes').pipe(
            take(1),
            map(response => response.mailboxes as Mailbox[]),
            catchError(error => {
                console.warn('fetchMailboxes error:', error);
                return throwError(error);
            })
        );
    }

    public fetchMailboxFolders (mailboxKey : string) : Observable<MailboxFolder[]> {
        return this.http.get('endpoint://mailboxes.getMailboxFolders', {
            urlParams: { mailboxKey }
        }).pipe(
            take(1),
            map(response => response.folders as MailboxFolder[]),
            catchError(error => {
                console.warn('fetchMailboxFolders error:', error);
                return throwError(error);
            })
        );
    }

    public fetchMessages (mailboxKey : string, folderName : string, startIndex : number, endIndex : number) : Observable<{
        messageCount : number,
        messages : MailboxMessage[]
    }> {
        return this.http.get('endpoint://mailboxes.getMessages', {
            urlParams: {
                mailboxKey,
                folderName,
                startIndex,
                endIndex
            }
        }).pipe(
            take(1),
            catchError(error => {
                console.warn('fetchMessages error:', error);
                return throwError(error);
            })
        );
    }

    public saveColor (messageId : string, color : string) : Observable<any> {
        return this.http.put('endpoint://mailboxes.saveColor', {
            body: {
                messageId,
                color
            }
        }).pipe(
            take(1),
            map(response => response),
            catchError(error => {
                console.warn('saveColor error:', error);
                return throwError(error);
            })
        );
    }

    public fetchMessage (mailboxKey : string, folderKey : string, mailUID : number) : Observable<string> {
        return this.http.get('endpoint://mailboxes.getMessage', {
            urlParams: {
                mailboxKey,
                folderKey,
                mailUID
            }
        }).pipe(
            take(1),
            catchError(error => {
                console.warn('fetchMessage error:', error);
                return throwError(error);
            })
        );
    }

    public storeAttachments (body : any) : Observable<any> {
        return this.http.post('endpoint://mailboxes.storeAttachments', { body }).pipe(
            take(1),
            catchError(error => {
                console.warn('storeAttachments error:', error);
                return throwError(error);
            })
        );
    }

    public deleteMailbox (mailboxKey : string) : Observable<void> {
        return this.http.delete('endpoint://mailboxes.delete', {
            urlParams: { mailboxKey }
        }).pipe(
            take(1),
            catchError(error => {
                console.warn('deleteMailbox error:', error);
                return throwError(error);
            })
        );
    }

    public updateMailbox (mailbox : Mailbox) : Observable<void> {
        return this.http.put('endpoint://mailboxes.save', {
            body: mailbox,
            urlParams: {
                mailboxKey: mailbox.key
            }
        }).pipe(
            take(1),
            catchError(error => {
                console.warn('updateMailbox error:', error);
                return throwError(error);
            })
        );
    }

    public createMailbox (mailbox : Mailbox) : Observable<Mailbox> {
        return this.http.post('endpoint://mailboxes.create', {
            body: mailbox
        }).pipe(
            take(1),
            catchError(error => {
                console.warn('createMailbox error:', error);
                return throwError(error);
            })
        );
    }

    public testMailbox (mailbox : Mailbox) : Observable<boolean> {
        return this.http.post('endpoint://mailboxes.test', {
            body: mailbox
        }).pipe(
            take(1),
            map(response => response.status === 'SUCCESS'),
            catchError(error => {
                console.warn('testMailbox error:', error);
                return throwError(error);
            })
        );
    }
}
