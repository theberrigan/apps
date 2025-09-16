import { Injectable } from '@angular/core';
import {Observable, throwError} from 'rxjs';
import {forIn, isArray} from 'lodash';
import {catchError, map, retry, take} from 'rxjs/operators';
import {HttpService} from './http.service';
import {Coordinator} from './company.service';
import {isSameObjectsLayout, updateObject} from '../lib/utils';
import {UserService} from './user.service';
import {Attachment, Contact, ShippingAddress} from './offers.service';
import {Translator} from './translators.service';
import {Client} from './client.service';

export class ProjectStatus {
    id : number;  // -1 == any
    key : string;
    display : string;
}

class ProjectsStatusColor {
    bg : string;
    text : string;
}

// TODO: select default colors
class ProjectsStatusesColors {
    new : ProjectsStatusColor = {
        bg: '#5b7cd2',
        text: '#fff'
    };

    confirmation : ProjectsStatusColor = {
        bg: '#9059bd',
        text: '#fff'
    };

    inprogress : ProjectsStatusColor = {
        bg: '#3daf9d',
        text: '#fff'
    };

    correction : ProjectsStatusColor = {
        bg: '#de804d',
        text: '#fff'
    };

    complete : ProjectsStatusColor = {
        bg: '#499036',
        text: '#fff'
    };

    ready : ProjectsStatusColor = {
        bg: '#37b791',
        text: '#fff'
    };

    closed : ProjectsStatusColor = {
        bg: '#9a7777',
        text: '#fff'
    };

    complaint : ProjectsStatusColor = {
        bg: '#aa43c7',
        text: '#fff'
    };

    cancelled : ProjectsStatusColor = {
        bg: '#c14848',
        text: '#fff'
    };
}

export class ProjectColumn {
    display : string;
    key : string;
    isVisible : boolean;
    isSortable : boolean;
    sortDirection? : number;
}

export class ProjectInfoColumn {
    display : string;
    key : string;
    isVisible : boolean;
}

export class ProjectsSettings {
    statusesColors : ProjectsStatusesColors = new ProjectsStatusesColors();
    colorizeEntireRow : boolean = false;
    columns : ProjectColumn[] = [
        {
            display: 'projects.list.statusColumn',
            key: 'statusKey',
            isVisible: true,
            isSortable: true,
            sortDirection: 1
        },
        {
            display: 'projects.list.projectColumn',
            key: 'projectKey',
            isVisible: true,
            isSortable: true,
            sortDirection: 1
        },
        {
            display: 'projects.list.offerColumn',
            key: 'offerKey',
            isVisible: true,
            isSortable: true,
            sortDirection: 1
        },
        {
            display: 'projects.list.companyColumn',
            key: 'company',
            isVisible: true,
            isSortable: true,
            sortDirection: 1
        },
        {
            display: 'projects.list.revenueColumn',
            key: 'revenue',
            isVisible: true,
            isSortable: false,
            sortDirection: 1
        },
        {
            display: 'projects.list.expensesColumn',
            key: 'expenses',
            isVisible: true,
            isSortable: false,
            sortDirection: 1
        },
        {
            display: 'projects.list.profitColumn',
            key: 'profit',
            isVisible: true,
            isSortable: false,
            sortDirection: 1
        },
        {
            display: 'projects.list.currencyColumn',
            key: 'currency',
            isVisible: true,
            isSortable: false,
            sortDirection: 1
        },
        {
            display: 'projects.list.marginColumn',
            key: 'margin',
            isVisible: true,
            isSortable: false,
            sortDirection: 1
        },
        {
            display: 'projects.list.deadlineColumn',
            key: 'deadline',
            isVisible: true,
            isSortable: true,
            sortDirection: 1
        },
        {
            display: 'projects.list.descriptionColumn',
            key: 'description',
            isVisible: true,
            isSortable: true,
            sortDirection: 1
        },
        {
            display: 'projects.list.externalNumberColumn',
            key: 'externalNumber',
            isVisible: true,
            isSortable: true,
            sortDirection: 1
        },
        {
            display: 'projects.list.contactColumn',
            key: 'contact',
            isVisible: true,
            isSortable: true,
            sortDirection: 1
        },
        {
            display: 'projects.list.phoneColumn',
            key: 'phone',
            isVisible: true,
            isSortable: false,
            sortDirection: 1
        },
        {
            display: 'projects.list.emailColumn',
            key: 'email',
            isVisible: true,
            isSortable: true,
            sortDirection: 1
        },
        {
            display: 'projects.list.invoiceColumn',
            key: 'invoiceSent',
            isVisible: true,
            isSortable: true,
            sortDirection: 1
        },
        {
            display: 'projects.list.coordinatorColumn',
            key: 'coordinator',
            isVisible: true,
            isSortable: true,
            sortDirection: 1
        }
    ];
    infoColumns : ProjectInfoColumn[] = [
        {
            display: 'projects.list.summary.service_name',
            key: 'name',
            isVisible: true,
        },
        {
            display: 'projects.list.summary.direction',
            key: 'language',
            isVisible: true,
        },
        {
            display: 'projects.list.summary.last_name',
            key: 'lastName',
            isVisible: true,
        },
        {
            display: 'projects.list.summary.first_name',
            key: 'firstName',
            isVisible: true,
        },
        {
            display: 'projects.list.summary.legal_name',
            key: 'legalName',
            isVisible: true,
        },
        {
            display: 'projects.list.summary.phone',
            key: 'phone',
            isVisible: true,
        },
        {
            display: 'projects.list.summary.email',
            key: 'email',
            isVisible: true,
        },
        {
            display: 'projects.list.summary.accepted',
            key: 'accepted',
            isVisible: true,
        },
    ]
}

export interface ProjectsListItem {
    company : string;
    contact : string;
    coordinator : string;
    currency : string;
    deadline : string;
    description : string;
    email : string;
    expenses : number;
    externalNumber : string;
    invoice : string;
    invoiceSent : boolean;
    margin : number;
    offerKey : string;
    phone : string;
    profit : number;
    projectId : number;
    projectKey : string;
    revenue : number;
    statusKey : string;
}

export class ProjectServiceItem {
    attachments : string[] = [];
    basePrice : number = 0;
    billable : boolean = true;
    discount : number = 0;
    from : string = '';
    gross : number = 0;
    id : number = 0;
    in : number = 0;
    name : string = '';
    net : number = 0;
    outPrecise : number = 0;
    outRounded : number = 0;
    price : number = 0;
    rate : number = 0;
    ratio : number = 0;
    serviceId : number = 0;
    shortName : string = '';
    to : string = '';
    unit : string = '';
}

export class Project {
    constructor (init? : Project) {
        if (init) {
            forIn(init, (value, key) => {
                this[key] = value;
            });
        }

        if (!this.shippingAddress) {
            this.shippingAddress = new ShippingAddress();
        }

        if (!this.services) {
            this.services = [];
        }

        if (!this.attachments) {
            this.attachments = [];
        }
    }

    attachments : Attachment[] = [];
    client : Client = null;
    contact : Contact = null;
    coordinator : Coordinator = null;
    created : string = '';
    currency : string = '';
    currencyRate : number = 0;
    company : string = '';
    deadline : string = '';
    deliveryType : {
        id : number,
        key : string
        name : string
    } = null;
    description : string = '';
    externalId : string = '';
    field : {
        id : number,
        key : string
        name : string
    } = null;
    instruction : string = '';
    key : string = '';
    notary : boolean = false;
    offerKey : string = '';
    priority : {
        id : number,
        key : string
        name : string
    } = null;
    services : ProjectServiceItem[] = [];
    shippingAddress : ShippingAddress = null;
    status : {
        id : number,
        key : string,
        name : string
    } = null;
    tax : number = 0;
    translationType : {
        id : number,
        key : string
        name : string
    } = null;
}

export class ProjectServiceProvider {
    color : string;
    email : string;
    estimatedFee : number;
    extraService: boolean;
    feePerUnit : number;
    firstName : string;
    lastName : string;
    middleName : string;
    phone : string;
    translatorId : number;
    translatorServiceId : number;
}

export class ProjectServiceAssignment {
    constructor (init? : any) {
        if (init) {
            forIn(init, (value, key) => {
                this[key] = value;
            });
        }
    }

    accepted : string;
    attachmentId : string;
    begin : string;
    comment : string;
    created : string;
    end : string;
    id : number;
    internalDeadline : string;
    outcomeUuid : string;
    pricePerUnit : number;
    reclaimedAmount : number;
    reclamationComment : string;
    serviceItemId : number;
    translator : Translator = new Translator();
    translatorServiceId : number;
    units : number;
}

export interface HistoryRecordItem {
    isEven : boolean;
    action : string;
    item : string;
    newValue : string;
    oldValue : string;
}

export interface HistoryRecord {
    entityId : string;
    id : string;
    timestamp : string;
    updatedBy : string;
    items : HistoryRecordItem[];
}

@Injectable({
    providedIn: 'root'
})
export class ProjectsService {
    constructor (
        private http : HttpService,
        private userService : UserService
    ) {}

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

    public fetchProjectCoordinators (projectKey : string) : Observable<Coordinator[]> {
        return this.http.get('endpoint://projects.getProjectCoordinators', {
            urlParams: { projectKey }
        }).pipe(
            take(1),
            map(response => response.coordinators as Coordinator[]),
            catchError(error => {
                console.warn('fetchProjectCoordinators error:', error);
                return throwError(error);
            })
        );
    }

    public fetchProjectServiceProviders (projectServiceId : number) : Observable<ProjectServiceProvider[]> {
        return this.http.get('endpoint://projects.getProjectServiceProviders', {
            urlParams: { projectServiceId }
        }).pipe(
            take(1),
            map(response => response.providers as ProjectServiceProvider[]),
            catchError(error => {
                console.warn('fetchProjectServiceProviders error:', error);
                return throwError(error);
            })
        );
    }

    public fetchProjectServiceAssignments (projectServiceId : number) : Observable<ProjectServiceAssignment[]> {
        return this.http.get('endpoint://projects.getProjectServiceAssignments', {
            urlParams: { projectServiceId }
        }).pipe(
            take(1),
            map(response => response.assignments as ProjectServiceAssignment[]),
            catchError(error => {
                console.warn('fetchProjectServiceAssignments error:', error);
                return throwError(error);
            })
        );
    }

    public fetchProjects (filters : any = {}) : Observable<any[]> {
        return this.http.get('endpoint://projects.getMultiple', {
            params: filters
        }).pipe(
            take(1),
            catchError(error => {
                console.warn('fetchProjects error:', error);
                return throwError(error);
            })
        );
    }

    public fetchProjectSummary (projectKey : string) : Observable<any[]> {
        return this.http.get('endpoint://projects.getProjectSummary', {
            urlParams: { projectKey }
        }).pipe(
            take(1),
            map(response => response.items),
            catchError(error => {
                console.warn('fetchProjectSummary error:', error);
                return throwError(error);
            })
        );
    }

    public fetchProjectsStatuses (addAny : boolean = false) : Observable<ProjectStatus[]> {
        return this.http.get('endpoint://projects.getStatuses').pipe(
            retry(1),
            take(1),
            map(response => {
                const statuses = response.statuses.map(status => ({
                    id: status.id,
                    key: status.key,
                    display: ('projects.statuses.' + status.key.toLowerCase().replace(/\./g, '_'))
                }));

                if (addAny) {
                    statuses.unshift({
                        id: -1,
                        key: 'any',
                        display: 'projects.statuses.any'
                    });
                }

                return statuses;
            }),
            catchError(error => {
                console.warn('fetchProjectsStatuses error:', error);
                return throwError(error);
            })
        );
    }

    public fetchProjectsSettings () : Observable<ProjectsSettings> {
        return this.userService.fetchFromStorage('projects_settings').pipe(
            retry(1),
            take(1),
            map((settings : ProjectsSettings) => updateObject(new ProjectsSettings(), settings || {})),
            catchError(error => {
                console.warn('fetchProjectsSettings error:', error);
                return throwError(error);
            })
        );
    }

    public saveProjectsSettings (settings : any) : Promise<boolean> {
        return this.userService.saveToStorage('projects_settings', settings);
    }

    public fetchProjectsListState () : Observable<any> {
        return this.userService.fetchFromStorage('projects_list_state').pipe(
            retry(1),
            take(1),
            catchError(error => {
                console.warn('fetchProjectsListState error:', error);
                return throwError(error);
            })
        );
    }

    public saveProjectsListState (state : any) : Promise<boolean> {
        return this.userService.saveToStorage('projects_list_state', state);
    }

    public fetchProjectHistory (projectKey : string) : Observable<HistoryRecord[]> {
        return this.http.get('endpoint://projects.getHistory', {
            urlParams: { projectKey }
        }).pipe(
            retry(1),
            take(1),
            map(response => response.records),
            catchError(error => {
                console.warn('fetchProjectHistory error:', error);
                return throwError(error);
            })
        );
    }

    public createAssignment (projectServiceId : number, assignmentData : any) : Observable<ProjectServiceAssignment> {
        return this.http.post('endpoint://projects.createAssignment', {
            urlParams: { projectServiceId },
            body: assignmentData
        }).pipe(
            take(1),
            map(response => response.assignment as ProjectServiceAssignment),
            catchError(error => {
                console.warn('createAssignment error:', error);
                return throwError(error);
            })
        );
    }

    public updateAssignment (projectServiceId : number, assignmentId : number, assignmentData : any) : Observable<ProjectServiceAssignment> {
        return this.http.put('endpoint://projects.updateAssignment', {
            urlParams: { projectServiceId, assignmentId },
            body: assignmentData
        }).pipe(
            take(1),
            map(response => response.assignment as ProjectServiceAssignment),
            catchError(error => {
                console.warn('updateAssignment error:', error);
                return throwError(error);
            })
        );
    }

    public deleteAssignment (projectServiceId : number, assignmentId : number) : Observable<ProjectServiceAssignment> {
        return this.http.delete('endpoint://projects.deleteAssignment', {
            urlParams: { projectServiceId, assignmentId },
        }).pipe(
            take(1),
            catchError(error => {
                console.warn('deleteAssignment error:', error);
                return throwError(error);
            })
        );
    }

    public updateDeadline (projectKey : string, deadline : number) : Observable<boolean> {
        return this.http.put('endpoint://projects.updateDeadline', {
            urlParams: { projectKey },
            body: { deadline }
        }).pipe(
            take(1),
            map(response => response === 'SUCCESS'),
            catchError(error => {
                console.warn('updateDeadline error:', error);
                return throwError(error);
            })
        );
    }

    public updateProject (projectKey : string, project : Project) : Observable<Project> {
        return this.http.put('endpoint://projects.updateProject', {
            urlParams: { projectKey },
            body: project
        }).pipe(
            take(1),
            map(response => response.project as Project),
            catchError(error => {
                console.warn('updateProject error:', error);
                return throwError(error);
            })
        );
    }
}
