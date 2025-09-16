import { Injectable }  from '@angular/core';
import { HttpService2 } from './http2.service';

@Injectable({
    providedIn: 'root',
})
export class QuoteService {
    constructor (
        private http : HttpService2
    ) {}

    public getQuoteSummary (quoteCode : string) : Promise<any> {
        return this.http.get({
            url: 'endpoint://quote.get_quote_summary',
            params: { quoteCode }
        })
        .toPromise()
        .then((response : any) => response)
        .catch((reason : any) => {
            console.warn(`[PaymentsService.getQuoteSummary] Error:`, reason);
            return null;
        });
    }


    /*
    getProjectCoordinators (projectKey : string) {
        return this.http.get(
            this.getApiUrl('get_project_coordinator', { projectKey }),
            this.buildOptions(null, 'json', {}, this.userService.getAccessToken())
        )
            .toPromise()
            .then((response : any) => response.json().coordinators as Coordinator[])
            .catch((response : any) => Promise.reject(this.parsePromiseError(response)));
    }

    getProjectSummary (projectKey : string) {
        return this.http.get(
            this.getApiUrl('get_project_summary', { projectKey }),
            this.buildOptions(null, 'json', {}, this.userService.getAccessToken())
        )
            .toPromise()
            .then(response => response.json().items)
            .catch(response => Promise.reject(this.parsePromiseError(response)));
    }

    getStatusesColors () {
        return new Promise((resolve, reject) => {
            this.userService
                .getFromStorage('statusesColors')
                .then((statuses : any) => resolve(statuses && statuses.projects || {}))
                .catch(() => reject());
        });
    }

    getStatuses () : Promise<any[]> {
        return new Promise((resolve, reject) => {
            this.http.get(
                this.getApiUrl('get_project_statuses'),
                this.buildOptions(null, 'json', {}, this.userService.getAccessToken())
            )
                .toPromise()
                .then((response) => {
                    const statuses : any[] = response.json().statuses;

                    this.translate
                        .get(statuses.map((status : any) => `projects.statuses.${ status.key }`))
                        .subscribe((messages : any) => {
                            statuses.forEach((status : any) => {
                                const key : string = `projects.statuses.${ status.key }`;
                                messages[key] != key && (status.name = messages[key]);
                            });
                        });

                    resolve(statuses);
                })
                .catch((reason : any) => reject(reason));
        });
    }

    getProjects (filters : any = {}) {
        const options : RequestOptions = new RequestOptions();

        options.params = new URLSearchParams();

        Object.keys(filters).forEach((key : string) => options.params.set(key, filters[key]));

        return this.http.get(
            this.getApiUrl('get_projects'),
            this.buildOptions(null, 'json', options, this.userService.getAccessToken())
        )
            .toPromise()
            .then(response => response.json())
            .catch(response => Promise.reject(this.parsePromiseError(response)));
    }

    createProject (offerKey : string, coordinatorId : number) {
        return this.http.post(
            this.getApiUrl('create_project', { offerKey }),
            {
                offerKey,
                coordinatorId
            },
            this.buildOptions(null, 'json', {}, this.userService.getAccessToken())
        )
            .toPromise()
            .then(response => response.json())
            .catch(response => Promise.reject(this.parsePromiseError(response)));
    }

    loadProject (projectKey : string) {
        return this.http.get(
            this.getApiUrl('load_project', { projectKey }),
            this.buildOptions(null, 'json', {}, this.userService.getAccessToken())
        )
            .toPromise()
            .then(response => response.json().project)
            .catch(response => Promise.reject(this.parsePromiseError(response)));
    }

    getTransactions (offerKey : string) {
        return this.http.get(
            this.getApiUrl('get_project_transactions', { offerKey }),
            this.buildOptions(null, 'json', {}, this.userService.getAccessToken())
        )
            .toPromise()
            .then(response => response.json())
            .catch(this.handleError);
    }

    saveProject (projectKey : string, project : any) {
        return this.http.put(
            this.getApiUrl('update_project', { key: projectKey }),
            JSON.stringify(project),
            this.buildOptions('json', 'json', {}, this.userService.getAccessToken())
        )
            .toPromise()
            .then(response => response.json().project)
            .catch(response => Promise.reject(this.parsePromiseError(response)));
    }

    loadAssignments (serviceId) {
        return this.http.get(
            this.getApiUrl('get_project_assignments', { serviceId }),
            this.buildOptions(null, 'json', {}, this.userService.getAccessToken())
        )
            .toPromise()
            .then(response => response.json().assignments)
            .catch(this.handleError);
    }

    createAssignment (projectServiceId : number, assignmentData : any) {
        return this.http.post(
            this.getApiUrl('create_project_assignment', { projectServiceId }),
            JSON.stringify(assignmentData),
            this.buildOptions('json', 'json', {}, this.userService.getAccessToken())
        )
            .toPromise()
            .then(response => response.json().assignment)
            .catch(response => Promise.reject(this.parsePromiseError(response)));
    }

    updateAssignment (projectServiceId : number, assignmentId : number, assignmentData : any) {
        return this.http.put(
            this.getApiUrl('update_project_assignment', { projectServiceId, assignmentId }),
            JSON.stringify(assignmentData),
            this.buildOptions('json', 'json', {}, this.userService.getAccessToken())
        )
            .toPromise()
            .then(response => response.json().assignment)
            .catch(response => Promise.reject(this.parsePromiseError(response)));
    }

    deleteAssignment (projectServiceId : number, assignmentId : number) {
        return this.http.delete(
            this.getApiUrl('delete_project_assignment', { projectServiceId, assignmentId }),
            this.buildOptions(null, 'json', {}, this.userService.getAccessToken())
        )
            .toPromise()
            .then(response => response)
            .catch(response => Promise.reject(this.parsePromiseError(response)));
    }

    loadProviders (projectServiceId) {
        return this.http.get(
            this.getApiUrl('get_service_providers', { projectServiceId }),
            this.buildOptions(null, 'json', {}, this.userService.getAccessToken())
        )
            .toPromise()
            .then(response => response.json().providers)
            .catch(this.handleError);
    }

    updateDeadline (projectKey : string, deadline : number) {
        return this.http.put(
            this.getApiUrl('update_project_deadline', { projectKey }),
            JSON.stringify({ deadline }),
            this.buildOptions('json', 'json', {}, this.userService.getAccessToken())
        )
            .toPromise()
            .then(response => response.json())
            .catch(response => Promise.reject(this.parsePromiseError(response)));
    }

    presignOutcome (assignmentId : number, fileName : string) {
        return this.http.put(
            this.getApiUrl('presign_outcome', { assignmentId }),
            JSON.stringify({ assignmentId, fileName }),
            this.buildOptions('json', 'json', {}, this.userService.getAccessToken())
        )
            .toPromise()
            .then(response => response.json())
            .catch(response => Promise.reject(this.parsePromiseError(response)));
    }
    */
}
