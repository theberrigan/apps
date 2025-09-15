import { Injectable } from '@angular/core';
import {HttpService} from './http.service';
import {catchError, map, retry, take} from 'rxjs/operators';
import {Observable, ReplaySubject, Subject, throwError} from 'rxjs';
import {DomSanitizer} from '@angular/platform-browser';
import {UserData, UserService} from './user.service';
import {DashboardService} from './dashboard.service';
import {cloneDeep} from 'lodash-es';
import {readJsonFromLocalStorage, saveJsonToLocalStorage} from '../lib/utils';
import {DebugService} from './debug.service';
import {LOCALES} from './lang.service';

export interface TermsSession {
    hasDot : boolean;
    phone : string;
    link : string;
}

export interface AcceptTermsResponse {
    isOk : boolean;
    token : string | null;
}

export interface AcceptedTermsResponse {
    status : 'OK' | 'ERROR';
    accepted : string;
    terms_name : string;
}

export interface TermsData {
    phone : string;
    name? : string;
}

@Injectable({
    providedIn: 'root'
})
export class TermsService {
    termsCache : any = {};

    termsSession : TermsSession;

    onTermsSessionChange = new ReplaySubject<TermsSession>();

    isInDashboard : boolean = false;

    readonly defaultTermsData : TermsData;

    termsData : TermsData;

    regLang : string | null = null;

    constructor (
        private http : HttpService,
        private sanitizer : DomSanitizer,
        private userService : UserService,
        private debugService : DebugService,
        private dashboardService : DashboardService,
    ) {
        this.defaultTermsData = this.createDefaultTermsData();

        this.dashboardService.onDashboardStateChange.subscribe(isInDashboard => {
            this.isInDashboard = isInDashboard;
            this.updateTermsSession();
        });

        this.debugService.register('createTestPBM', () => {
            this.createTestPBM().subscribe(data => {
                // console.warn(`PBM data: ${ JSON.stringify(data) }`);
                window.location.href = `/terms/${ data.phone }`;
            });
        }, { help: 'Create pay-by-mail/reg-n-pay test data' });

        this.debugService.register('createTestFleetPBM', () => {
            this.createTestFleetPBM().subscribe(data => {
                window.location.href = `/terms/${ data.phone }`;
            });
        }, { help: 'Create pay-by-mail/reg-n-pay fleet test data' });
    }

    initTerms () : Promise<void> {
        const lastTermsData = this.getLastTermsData();

        return this.validateTermsData(lastTermsData)
            .then(termsData => this.setTermsData(termsData));
    }

    createDefaultTermsData () : TermsData {
        return {
            phone: null,
            name: null
        };
    }

    getLastTermsData () : TermsData {
        return readJsonFromLocalStorage('lastTermsData', cloneDeep(this.defaultTermsData));
    }

    saveLastTermsData () {
        saveJsonToLocalStorage('lastTermsData', this.termsData);
    }

    validateTermsData (termsData : TermsData, rememberRegLang : boolean = false) : Promise<TermsData> {
        if (!termsData.phone) {
            return Promise.resolve(cloneDeep(this.defaultTermsData));
        }

        return this.http.post('endpoint://terms.verify', {
            body: {
                phone: String(termsData.phone).trim()
            }
        })
            .pipe(take(1))
            .toPromise()
            .then(({ status, acceptable, terms_name, registration_language } : {
                status : 'OK' | 'ERROR',
                acceptable : boolean,
                terms_name : string,
                registration_language : string,
            }) => {
                if (status === 'OK' && acceptable) {
                    termsData.name = terms_name;
                } else {
                    termsData = cloneDeep(this.defaultTermsData);
                }

                registration_language = (registration_language || 'en').toLowerCase();

                if (rememberRegLang && LOCALES.includes(registration_language)) {
                    this.regLang = registration_language;
                }

                return termsData;
            })
            .catch(error => {
                console.warn('validateTermsData error:', error);
                return cloneDeep(this.defaultTermsData);
            });
    }

    getTermsPhone () : string | null {
        return this.termsData?.phone || this.defaultTermsData.phone;
    }

    updateTermsSession () {
        const phone = this.getTermsPhone();
        const hasDot = !!phone && !this.isInDashboard;

        this.termsSession = {
            hasDot,
            phone,
            link: hasDot ? `/terms/${ phone }` : '/terms'
        };

        this.onTermsSessionChange.next(this.termsSession);
    }

    getTermsSession () : TermsSession {
        return this.termsSession;
    }

    setTermsData (termsData : TermsData) {
        this.termsData = termsData;
        this.saveLastTermsData();
        this.updateTermsSession();
    }

    fetchTerms (name : string, langCode : string) {
        const cacheKey = `${ name }:${ langCode }`;

        // console.log(this.termsCache[cacheKey]);

        if (this.termsCache[cacheKey]) {
            return new Observable(subscriber => {
                subscriber.next(this.termsCache[cacheKey]);
            }).pipe(take(1));
        }

        return this.http.get(`/assets/locale/terms/${ name }.${ langCode }.html`, {
            responseType: 'text'
        }).pipe(
            retry(1),
            take(1),
            map((html : any) => {
                html = this.sanitizer.bypassSecurityTrustHtml(html);
                this.termsCache[cacheKey] = html;
                return html;
            }),
            catchError(error => {
                console.warn('fetchTerms error:', error);
                return throwError(error);
            })
        );
    }

    fetchAcceptedTerms () : Observable<AcceptedTermsResponse> {
        return this.http.get('endpoint://terms.getAccepted').pipe(
            take(1),
            catchError(error => {
                console.warn('fetchAcceptedTerms error:', error);
                return throwError('error');
            })
        );
    }

    acceptTerms (termsId : string) : Observable<AcceptTermsResponse> {
        return this.http.post('endpoint://terms.accept', {
            body: {
                phone: termsId,
                accepted: true
            }
        }).pipe(
            take(1),
            map(response => {
                if (response.status === 'OK') {
                    this.setTermsData(cloneDeep(this.defaultTermsData));

                    return {
                        isOk: true,
                        token: response.token
                    };
                }

                return {
                    isOk: false,
                    token: null
                };
            }),
            catchError(error => {
                console.warn('acceptTerms error:', error);
                return throwError('error');
            })
        );
    }

    createTestPBM () : Observable<{ phone : string, url : string }> {
        return this.http.get('endpoint://test.create-pbm').pipe(
            take(1),
            catchError(error => {
                console.warn('createTestPBM error:', error);
                return throwError('error');
            })
        );
    }

    createTestFleetPBM () : Observable<{ phone : string }> {
        return this.http.get('endpoint://fleet.feeReg').pipe(
            take(1),
            catchError(error => {
                console.warn('createTestFleetPBM error:', error);
                return throwError('error');
            })
        );
    }
}
