import { Injectable } from '@angular/core';
import {Observable, ReplaySubject} from 'rxjs';
import {HttpService} from './http.service';

export class Terms {
    id : number;
    textEng? : string;
}

export interface IShowTermsEvent {
    // terms : Terms;
    endpoint : string;
    isAcceptRequired? : boolean;
    responseSubject : ReplaySubject<IShowTermsResponseEvent>;
}

export interface IShowTermsResponseEvent {
    status : 'loading' | 'empty' | 'error' | 'shown' | 'accepted' | 'close' | 'complete';
}

@Injectable({
    providedIn: 'root'
})
export class TermsService {
    // /rest/v1/terms - last accepted private terms
    // /rest/v1/terms/{termsId} - accept new private terms
    // /rest/v1/terms/eligible - new private terms to accept
    // /rest/v1/terms/unauthenticated - public terms
    public onShowTerms = new ReplaySubject<IShowTermsEvent>();

    constructor (
        private http : HttpService
    ) {}

    public showPublicTerms () : Observable<IShowTermsResponseEvent> {
        return this.showTerms('terms.getPublic', false);
    }

    public showAcceptedTerms () : Observable<IShowTermsResponseEvent> {
        return this.showTerms('terms.getAccepted', false);

    }

    public showEligibleTerms () : Observable<IShowTermsResponseEvent> {
        return this.showTerms('terms.getEligible', true);
    }

    // 'terms.getPublic'
    // 'terms.getAccepted'
    // 'terms.getEligible'
    private showTerms (endpoint : string, isAcceptRequired : boolean) : Observable<IShowTermsResponseEvent> {
        const responseSubject = new ReplaySubject<IShowTermsResponseEvent>();

        responseSubject.next({ status: 'loading' });

        this.onShowTerms.next({
            endpoint,
            isAcceptRequired,
            responseSubject
        });

        return responseSubject.asObservable();
    }

    public fetchTerms (endpoint : string) : Promise<Terms> {
        return new Promise((resolve, reject) => {
            this.http.get2('endpoint://' + endpoint)
                .then(({ terms }) => resolve(terms))
                .catch(reason => {
                    console.warn(`Terms fetch error:`, reason);
                    reject();
                });
        });
    }

    public acceptTerms (termsId : number) : Promise<void> {
        return new Promise((resolve, reject) => {
            this.http.post2('endpoint://terms.accept', { urlParams: { termsId } })
                .then(() => resolve())
                .catch(reason => {
                    console.warn(`Terms accept error:`, reason);
                    reject();
                });
        });
    }
}
