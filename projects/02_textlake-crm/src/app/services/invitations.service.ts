import { Injectable } from '@angular/core';
import {HttpService} from './http.service';
import {catchError, map, retry, take} from 'rxjs/operators';
import {Observable, throwError} from 'rxjs';
import {UserService} from './user.service';

export class Invitation {
    id : string = null;
    created : string = null;
    email : string = '';
    roles : string[] = [];
}

@Injectable({
    providedIn: 'root'
})
export class InvitationsService {
    constructor (
        private http : HttpService,
        private userService : UserService,
    ) {}

    public fetchInvitations () : Observable<Invitation[]> {
        return this.http.get('endpoint://invitations.getInvitations').pipe(
            retry(1),
            take(1),
            map(response => response.invitations),
            catchError(error => {
                console.warn('fetchInvitations error:', error);
                return throwError(error);
            })
        );
    }

    public createInvitation (invitation : Invitation) : Observable<Invitation> {
        return this.http.post('endpoint://invitations.createInvitation', {
            body: { invitation }
        }).pipe(
            retry(1),
            take(1),
            map(response => response.invitation),
            catchError(error => {
                console.warn('createInvitation error:', error);
                return throwError(error);
            })
        );
    }

    public updateInvitation (invitation : Invitation) : Observable<Invitation> {
        return this.http.put('endpoint://invitations.updateInvitation', {
            urlParams: {
                invitationId: invitation.id
            },
            body: { invitation }
        }).pipe(
            retry(1),
            take(1),
            map(response => response.invitation),
            catchError(error => {
                console.warn('updateInvitation error:', error);
                return throwError(error);
            })
        );
    }

    public deleteInvitation (invitationId : string) : Observable<void> {
        return this.http.delete('endpoint://invitations.deleteInvitation', {
            urlParams: { invitationId }
        }).pipe(
            retry(1),
            take(1),
            catchError(error => {
                console.warn('deleteInvitation error:', error);
                return throwError(error);
            })
        );
    }

    public fetchInvitationsListState () : Observable<any> {
        return this.userService.fetchFromStorage('invitations_list_state').pipe(
            retry(1),
            take(1),
            catchError(error => {
                console.warn('fetchInvitationsListState error:', error);
                return throwError(error);
            })
        );
    }

    public saveInvitationsListState (state : any) : Promise<boolean> {
        return this.userService.saveToStorage('invitations_list_state', state);
    }
}
