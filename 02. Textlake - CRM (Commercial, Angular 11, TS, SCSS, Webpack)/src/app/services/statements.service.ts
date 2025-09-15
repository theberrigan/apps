import { Injectable } from '@angular/core';
import {HttpService} from './http.service';
import {UserService} from './user.service';
import {Observable, throwError} from 'rxjs';
import {Pagination} from '../widgets/pagination/pagination.component';
import {Address} from '../types/address.type';
import {catchError, map, retry, take} from 'rxjs/operators';

export class ClientStatementItem {
    comment : string;
    completed : string;
    created : string;
    currency : string;
    description : string;
    externalId : string;
    gross : number;
    invoice : string;
    invoiceSent : boolean;
    net : number;
    offer : string;
    project : string;
    projectId : number;
    status : string;
}

export class ClientStatement {
    address : Address;
    bankAccount : string;
    bankName : string;
    clientId : number;
    clientName : string;
    items : ClientStatementItem[];
    legalName : string;
    tax : number;
    tin : string;
    total : any;
}

export class GetClientStatementsResponse extends Pagination {
    statements : ClientStatement[];
}

export class CoordinatorStatementItem {
    expenses : number;
    gross : number;
    margin : number;
    net : number;
    offer : string;
    offerCoordinator : string;
    offerCreated : string;
    offerStatus : string;
    project : string;
    projectCompleted : string;
    projectCoordinator : string;
    projectCreated : string;
    projectStatus : string;
}

export class CoordinatorStatement {
    email : string;
    items : CoordinatorStatementItem[];
    totalGross : number;
    totalNet : number;
}

export class GetCoordinatorStatementResponse extends Pagination {
    statement : CoordinatorStatement;
}

export class GetTranslatorStatementResponse extends Pagination {
    statements : TranslatorStatement[];
}

export class ProjectStatementItem {
    comment : string;
    debited : boolean;
    fee : number;
    firstName : string;
    lastName : string;
    translatorDebitId : number;
    translatorId : number;
}

export class ProjectStatement {
    items : ProjectStatementItem[];
    projectCreated : number;
    projectId : number;
    projectKey : string;
    projectStatusKey : string;
    total : number;
}

export class TranslatorStatementItem {
    comment : string;
    debited : boolean;
    fee : number;
    projectId : number;
    projectKey : string;
    projectStatusKey : string;
    translatorDebitId : number;
}

export class TranslatorStatement {
    firstName : string;
    items : TranslatorStatementItem[];
    lastName : string;
    translatorId : number;
    total : number;
}

@Injectable({
    providedIn: 'root'
})
export class StatementsService {
    constructor (
        private http : HttpService,
        private userService : UserService
    ) {}

    public fetchClientsStatements (params : any) : Observable<GetClientStatementsResponse> {
        return this.http.get('endpoint://statements.getClientsStatements', { params }).pipe(
            take(1),
            catchError(error => {
                console.warn('fetchClientsStatements error:', error);
                return throwError(error);
            })
        );
    }

    public saveClientStatementItem (statementItemData : any) : Observable<any> {
        return this.http.put('endpoint://statements.saveClientStatementItem', {
            body: statementItemData
        }).pipe(
            take(1),
            map(response => response.invoice),
            catchError(error => {
                console.warn('saveClientStatementItem error:', error);
                return throwError(error);
            })
        );
    }

    public fetchClientsStatementsState () : Observable<any> {
        return this.userService.fetchFromStorage('clients_statements_state').pipe(
            retry(1),
            take(1),
            catchError(error => {
                console.warn('fetchClientsStatementsState error:', error);
                return throwError(error);
            })
        );
    }

    public saveClientsStatementsState (state : any) : Promise<boolean> {
        return this.userService.saveToStorage('clients_statements_state', state);
    }


    public fetchCoordinatorsStatements (params : any) : Observable<GetCoordinatorStatementResponse> {
        return this.http.get('endpoint://statements.getCoordinatorsStatements', { params }).pipe(
            take(1),
            catchError(error => {
                console.warn('fetchCoordinatorsStatements error:', error);
                return throwError(error);
            })
        );
    }

    public fetchCoordinatorsStatementsState () : Observable<any> {
        return this.userService.fetchFromStorage('coordinators_statements_state').pipe(
            retry(1),
            take(1),
            catchError(error => {
                console.warn('fetchCoordinatorsStatements error:', error);
                return throwError(error);
            })
        );
    }

    public saveCoordinatorsStatementsState (state : any) : Promise<boolean> {
        return this.userService.saveToStorage('coordinators_statements_state', state);
    }


    public fetchProjectsStatements (params : any) : Observable<ProjectStatement[]> {
        return this.http.get('endpoint://statements.getProjectsStatements', { params }).pipe(
            take(1),
            map(response => response.statements as ProjectStatement[]),
            catchError(error => {
                console.warn('fetchProjectsStatements error:', error);
                return throwError(error);
            })
        );
    }

    public fetchProjectsStatementsState () : Observable<any> {
        return this.userService.fetchFromStorage('projects_statements_state').pipe(
            retry(1),
            take(1),
            catchError(error => {
                console.warn('fetchProjectsStatements error:', error);
                return throwError(error);
            })
        );
    }

    public saveProjectsStatementsState (state : any) : Promise<boolean> {
        return this.userService.saveToStorage('projects_statements_state', state);
    }


    public fetchTranslatorsStatements (params : any) : Observable<GetTranslatorStatementResponse> {
        return this.http.get('endpoint://statements.getTranslatorsStatements', { params }).pipe(
            take(1),
            // map(response => response.statements as TranslatorStatement[]),
            catchError(error => {
                console.warn('fetchTranslatorsStatements error:', error);
                return throwError(error);
            })
        );
    }

    public fetchTranslatorsStatementsState () : Observable<any> {
        return this.userService.fetchFromStorage('translators_statements_state').pipe(
            retry(1),
            take(1),
            catchError(error => {
                console.warn('fetchTranslatorsStatements error:', error);
                return throwError(error);
            })
        );
    }

    public saveTranslatorsStatementsState (state : any) : Promise<boolean> {
        return this.userService.saveToStorage('translators_statements_state', state);
    }

    public saveStatementItem (statementItemData : any) : Observable<any> {
        return this.http.put('endpoint://statements.saveStatementItem', {
            body: {
                item: statementItemData
            }
        }).pipe(
            take(1),
            catchError(error => {
                console.warn('saveStatementItem error:', error);
                return throwError(error);
            })
        );
    }

    /*
    public createProject (offerKey : string, coordinatorId : number) : Observable<any> {
        return this.http.post('endpoint://projects.create', {
            urlParams: { offerKey },
            body: {
                offerKey,
                coordinatorId
            }
        }).pipe(
            take(1),
            catchError(error => {
                console.warn('createProject error:', error);
                return throwError(error);
            })
        );
    }

    public presignOutcome (assignmentId : number, fileName : string) : Observable<any> {
        return this.http.put('endpoint://projects.presignOutcome', {
            urlParams: { assignmentId },
            body: {
                assignmentId,
                fileName
            }
        }).pipe(
            take(1),
            catchError(error => {
                console.warn('presignOutcome error:', error);
                return throwError(error);
            })
        );
    }

    public fetchProject (projectKey : string) : Observable<Project> {
        return this.http.get('endpoint://projects.getOne', {
            urlParams: { projectKey }
        }).pipe(
            take(1),
            map(response => response.project as Project),
            catchError(error => {
                console.warn('fetchProject error:', error);
                return throwError(error);
            })
        );
    }
    */
}
