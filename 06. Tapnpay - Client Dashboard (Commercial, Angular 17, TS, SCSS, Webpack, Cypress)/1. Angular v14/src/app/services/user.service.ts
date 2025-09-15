import {ApplicationRef, Injectable, NgZone} from '@angular/core';
import {API_TOKEN_HEADER_KEY, HttpService} from './http.service';
import {catchError, map, retry, switchMap, take} from 'rxjs/operators';
import {Observable, ReplaySubject, throwError} from 'rxjs';
import {DEFAULT_LANG, ILang, LangService} from './lang.service';
import {CONFIG} from '../../../config/app/dev';
import {cloneDeep} from 'lodash-es';
import {readJsonFromLocalStorage, saveJsonToLocalStorage} from '../lib/utils';
import {DebugService} from './debug.service';
import {StorageService} from './storage.service';
import {HttpErrorResponse} from '@angular/common/http';

export type AccountPaymentModel = 'UNKNOWN' | 'POSTPAID' | 'FLEET';
export type AccountTollAuthority = string;
export type AccountStatus = 'ACTIVE' | 'ACCOUNT_DEBT_LOCK' | 'OTHER';

export interface LocalUserData {
    lang : string;
    shouldUpdateRemoteLang : boolean;
}

export interface RemoteUserData {
    lang : string;
    firstLoginDate : string;
}

export interface AuthUserData {
    token : string;
}

export interface AccountUserData {
    tollAuthority : AccountTollAuthority;
    paymentModel : AccountPaymentModel;
    accountStatus : AccountStatus;
}

export interface UserData {
    auth : AuthUserData;
    local : LocalUserData;
    remote : RemoteUserData;
    account : AccountUserData;
}

export const DEV_PHONE = 'ta-sunpass-phone';
export const DEV_PHONE_NTTA = '18554827672';
export const DEV_PHONE_SUNPASS = '18555172507';
export const DEV_PHONE_FASTRAK = '18555172927';

@Injectable({
    providedIn: 'root'
})
export class UserService {
    readonly supportedLangs : ILang[] = CONFIG.locales;

    readonly defaultLocalUserData : LocalUserData;

    readonly defaultRemoteUserData : RemoteUserData;

    readonly defaultAuthUserData : AuthUserData;

    readonly defaultAccountUserData : AccountUserData;

    // User is new if no more than 24 hours have passed since the first login
    readonly isNewUserMaxTime : number = 24 * 60 * 60 * 1000;

    userData : UserData;

    onUserChanged = new ReplaySubject<UserData>();

    onLoginStateChange = new ReplaySubject<boolean>();

    _isRegNPay : boolean = false;

    shouldRemoteSaveAfterUserInit : boolean = false;

    shouldSaveAuthDataAfterUserInit : boolean = false;

    _testFleetUserPhone : string = null;

    constructor (
        private http : HttpService,
        private langService : LangService,
        private debugService : DebugService,
        private storageService : StorageService,
        private zone : NgZone
    ) {
        this.defaultLocalUserData = this.createDefaultLocalUserData();
        this.defaultRemoteUserData = this.createDefaultRemoteUserData(this.defaultLocalUserData);
        this.defaultAuthUserData = this.createDefaultAuthUserData();
        this.defaultAccountUserData = this.createDefaultAccountUserData();

        this.debugService.register('setLang', (lang : string) => {
            return this.zone.run(() => this.setLang(lang));
        }, { help: `Change application language (${ this.supportedLangs.map(lang => JSON.stringify(lang.code)).join(', ') })` });
    }

    createDefaultLocalUserData () : LocalUserData {
        const data : LocalUserData = {
            lang: DEFAULT_LANG.code,
            shouldUpdateRemoteLang: false
        };

        const browserLocales = [
            navigator.language,
            ...navigator.languages
        ].reduce((acc : string[], lang : string) => {
            if (lang) {
                lang = lang.toLowerCase().split('-')[0];

                if (!acc.includes(lang)) {
                    acc.push(lang);
                }
            }

            return acc;
        }, []);

        const preferredLocale = browserLocales.find(locale => {
            for (let supportedLang of this.supportedLangs) {
                if (locale === supportedLang.code) {
                    return true;
                }
            }

            return false;
        });

        data.lang = preferredLocale || DEFAULT_LANG.code;

        return data;
    }

    createDefaultRemoteUserData (defaultLocalUserData : LocalUserData) : RemoteUserData {
        return {
            lang: defaultLocalUserData.lang,
            firstLoginDate: new Date().toISOString()
        };
    }

    createDefaultAuthUserData () : AuthUserData {
        return {
            token: null
        };
    }

    createDefaultAccountUserData () : AccountUserData {
        return {
            tollAuthority: 'UNKNOWN',
            paymentModel: 'UNKNOWN',
            accountStatus: 'ACTIVE',
        };
    }

    initUser () : Promise<UserData> {
        return new Promise(resolve => {
            Promise.all([
                this.getUserAuthData(),
            ]).then(([
                authData,
            ] : [
                AuthUserData
            ]) => {
                return Promise.all([
                    Promise.resolve(authData),
                    this.getRemoteUserData(authData.token),
                    this.getLocalUserData(),
                    this.getAccountUserData(authData.token),
                ]);
            }).then(([
                authData,
                remoteUserData,
                localUserData,
                accountUserData,
            ] : [
                AuthUserData,
                RemoteUserData,
                LocalUserData,
                AccountUserData
            ]) => {
                this.userData = {
                    auth: authData,
                    local: localUserData,
                    remote: remoteUserData,
                    account: accountUserData
                };

                if (this.shouldRemoteSaveAfterUserInit) {
                    this.shouldRemoteSaveAfterUserInit = false;
                    this.saveRemoteUserData();
                }

                if (this.shouldSaveAuthDataAfterUserInit) {
                    this.shouldSaveAuthDataAfterUserInit = false;
                    this.saveUserAuthData();
                }

                this.notifyUserChanged();
                this.notifyLoginStateChanged();

                resolve(this.userData);
            });
        });
    }

    getLocalUserData () : Promise<LocalUserData> {
        return new Promise(resolve => {
            resolve(readJsonFromLocalStorage('localUserData', cloneDeep(this.defaultLocalUserData)));
        });
    }

    async getAccountUserData (token : string) : Promise<AccountUserData> {
        if (!token) {
            return Promise.resolve(cloneDeep(this.defaultAccountUserData));
        }

        return this.http.get('endpoint://account.getUserData', {
            headers: {
                [ API_TOKEN_HEADER_KEY ]: token
            }
        }).pipe(
            take(1),
            map((response : {
                status : 'OK' | 'ERROR';
                toll_authority_model : 'POSTPAID' | 'FLEET';
                toll_authority : string;
                account_status : AccountStatus;
            }) => {
                let accountData : AccountUserData = cloneDeep(this.defaultAccountUserData);

                if (response.status === 'OK') {
                    accountData = <AccountUserData>{
                        tollAuthority: response.toll_authority,
                        paymentModel: response.toll_authority_model,
                        accountStatus: response.account_status,
                    };
                }

                // TODO: remove later
                if (!accountData.tollAuthority) {
                    accountData.tollAuthority = accountData.paymentModel === 'POSTPAID' ? 'NTTA' : 'SUNPASS';
                }

                if (this.userData) {
                    this.userData.account = accountData;
                }

                return accountData;
            }),
            catchError((error : HttpErrorResponse) => {
                console.warn('getAccountUserData error:', error);
                return throwError(error.error.status_code || error.error.status);
            })
        ).toPromise().catch(() => {
            return cloneDeep(this.defaultAccountUserData);
        });
    }

    // TODO: debounce
    saveLocalUserData () {
        saveJsonToLocalStorage('localUserData', this.userData.local);
    }

    getRemoteUserData (token : string) : Promise<RemoteUserData> {
        return new Promise(resolve => {
            if (token) {
                this.storageService.get('user_data', token).subscribe(
                    (userData : RemoteUserData) => {
                        if (!userData) {
                            userData = cloneDeep(this.defaultRemoteUserData);
                            this.shouldRemoteSaveAfterUserInit = true;
                            console.warn('Def user data', userData);
                        }

                        // Replace deprecated isFirstLogin flag with firstLoginDate
                        // -----------------------------------------------------------------

                        const isFirstLogin = userData['isFirstLogin'];

                        if (isFirstLogin === true) {
                            userData.firstLoginDate = new Date().toISOString();
                        } else if (isFirstLogin === false || !userData['firstLoginDate']) {
                            userData.firstLoginDate = new Date(0).toISOString();
                        }

                        if (userData.hasOwnProperty('isFirstLogin')) {
                            delete userData['isFirstLogin'];
                            this.shouldRemoteSaveAfterUserInit = true;
                        }

                        // -----------------------------------------------------------------

                        resolve(userData);
                    },
                    () => resolve(cloneDeep(this.defaultRemoteUserData))
                );
            } else {
                resolve(cloneDeep(this.defaultRemoteUserData));
            }
        });
    }

    // TODO: debounce
    saveRemoteUserData () {
        if (this.isLoggedIn()) {
            this.storageService.create('user_data', this.userData.remote).subscribe(isOk => {
                console.log('Remote user data update:', isOk);
            });
        }
    }

    getUserAuthData () : Promise<AuthUserData> {
        const authUserData = readJsonFromLocalStorage('authUserData', cloneDeep(this.defaultAuthUserData));
        return this.validateAuthData(authUserData);
    }

    // TODO: debounce
    saveUserAuthData () {
        saveJsonToLocalStorage('authUserData', this.userData.auth);
    }

    // TODO: remote token validation
    validateAuthData (authUserData : AuthUserData) : Promise<AuthUserData> {
        return new Promise(resolve => {
            if (!authUserData.token) {
                return resolve(authUserData);
            }

            this.http.options('endpoint://auth.validate-token', {
                headers: {
                    [ API_TOKEN_HEADER_KEY ]: authUserData.token
                }
            })
                .pipe(take(1))
                .toPromise()
                .then(({ status }) => status === 'OK')
                .catch(() => false)
                .then((isTokenValid : boolean) => {
                    if (!isTokenValid) {
                        authUserData.token = null;
                        this.shouldSaveAuthDataAfterUserInit = true;
                    }

                    resolve(authUserData);
                });
        });
    }

    notifyUserChanged () {
        this.onUserChanged.next(this.userData);
    }

    notifyLoginStateChanged () {
        this.onLoginStateChange.next(this.isLoggedIn());
    }

    // -----------------------------------------------------------------------

    isNewUser () : boolean {
        const firstLoginDate = this.getFirstLoginDate();

        if (!firstLoginDate) {
            return false;
        }

        const msFromFirstLogin = new Date().getTime() - new Date(firstLoginDate).getTime();

        return (msFromFirstLogin < this.isNewUserMaxTime);
    }

    getFirstLoginDate () : string {
        return this.userData?.remote?.firstLoginDate;
    }

    isRegNPay () {
        return this._isRegNPay;
    }

    setIsRegNPay (isRegNPay : boolean) {
        this._isRegNPay = isRegNPay;
    }

    getLang () : string {
        if (this.isLoggedIn()) {
            return this.userData?.remote?.lang || this.defaultRemoteUserData.lang;
        } else {
            return this.userData?.local?.lang || this.defaultLocalUserData.lang;
        }
    }

    setLang (lang : string) {
        if (!this.userData) {
            return;
        }

        if (this.userData.remote) {
            this.userData.remote.lang = lang;
            this.saveRemoteUserData();
        }

        if (this.userData.local) {
            this.userData.local.lang = lang;
            this.userData.local.shouldUpdateRemoteLang = !this.isLoggedIn();
            this.saveLocalUserData();
        }

        this.langService.use(lang);
        this.notifyUserChanged();
    }

    getAuthToken () : string {
        return this.userData?.auth?.token || this.defaultAuthUserData.token;
    }

    setAuthToken (token : string) {
        if (!this.userData || !this.userData.auth) {
            return;
        }

        this.userData.auth.token = token;
        this.saveUserAuthData();
        this.notifyUserChanged();
    }

    // -----------------------------------------------------------------------

    getUserData () : UserData {
        return this.userData;
    }

    isLoggedIn () : boolean {
        return !!(this.userData?.auth?.token);
    }

    getTestAccountPin (phone : string) : Observable<string> {
        return this.http.get('endpoint://test.get-account-pin', {
            urlParams: { phone },
            responseType: 'text'
        }).pipe(
            take(1),
            catchError(error => {
                this.debugService.logNetworkError(error, 'getTestAccountPin');
                return throwError(error);
            })
        );
    }

    createTestAccount () {
        return this.http.get('endpoint://test.create-account').pipe(
            take(1),
            map((credentials : { phone : string, pin : string }) => {
                return credentials;
            }),
            catchError(error => {
                this.debugService.logNetworkError(error, 'createTestUser');
                return throwError(error);
            })
        );
    }

    createTestFleetAccount (phone : string = DEV_PHONE) {
        return this.http.get('endpoint://fleet.createTestAcc', {
            urlParams: { phone }
        }).pipe(
            take(1),
            map((credentials : { phone : string, pin : string, token : string }) => {
                this._testFleetUserPhone = credentials.phone;
                return credentials;
            }),
            catchError(error => {
                this.debugService.logNetworkError(error, 'createTestFleetAccount');
                return throwError(error);
            })
        );
    }

    generateInvoices (phone : string = null) {
        return this.http.get('endpoint://fleet.generateInvoices', {
            urlParams: {
                phone: phone || this._testFleetUserPhone
            }
        }).pipe(
            take(1),
            catchError(error => {
                this.debugService.logNetworkError(error, 'generateInvoices');
                return throwError(error);
            })
        );
    }

    sendPhone (phone : string) : Observable<boolean> {
        return this.http.post('endpoint://auth.send-phone', {
            body: {
                phone: String(phone).trim()
            }
        }).pipe(
            take(1),
            map(response => response.status === 'OK'),
            catchError(error => {
                this.debugService.logNetworkError(error, 'sendPhone');
                return throwError(error);
            })
        );
    }

    applyToken (token : string | null, isRegNPay : boolean = false) : Promise<boolean> {
        return new Promise((resolve) => {
            Promise.all([
                this.getRemoteUserData(token),
                this.getAccountUserData(token)
            ]).then(([
                remoteUserData,
                accountUserData,
            ] : [
                RemoteUserData,
                AccountUserData
            ]) => {
                if (!token) {
                    return resolve(false);
                }

                this.setIsRegNPay(isRegNPay);
                this.setAuthToken(token);
                this.userData.account = accountUserData;
                this.userData.remote = remoteUserData; // TODO: update remote lang

                if (this.userData.local?.shouldUpdateRemoteLang) {
                    this.userData.remote.lang = this.userData.local.lang;
                    this.userData.local.shouldUpdateRemoteLang = false;
                    this.shouldRemoteSaveAfterUserInit = true;
                    this.saveLocalUserData();
                }

                if (this.shouldRemoteSaveAfterUserInit) {
                    this.shouldRemoteSaveAfterUserInit = false;
                    this.saveRemoteUserData();
                }

                this.notifyUserChanged();
                this.notifyLoginStateChanged();

                return resolve(true);
            });
        });
    }

    validateToken (token : string) : Observable<boolean> {
        return this.http.options('endpoint://auth.validate-token', {
            headers: {
                [ API_TOKEN_HEADER_KEY ]: token
            }
        }).pipe(
            take(1),
            map(response => response.status === 'OK'),
            catchError(error => {
                console.warn('validateToken error:', error);
                return throwError(error);
            })
        );
    }

    login (credentials : { phone : string, pin : string }) : Promise<{
        isOk : boolean;
        errorCode : number;
    }> {
        return this.http.post('endpoint://auth.send-pin', {
            body: credentials
        })
            .pipe(take(1))
            .toPromise()
            .then(response => {
                if (!response || response.status !== 'OK' || !response.token) {
                    return Promise.resolve({
                        isOk: false,
                        errorCode: 0
                    });
                }

                return this.applyToken(response.token).then(isOk => ({
                    isOk,
                    errorCode: 0
                }));
            }).catch((error : HttpErrorResponse) => {
                console.warn('login error:', error);
                return {
                    isOk: false,
                    errorCode: error.error.status_code
                };
            });
    }

    logout () {
        this.userData.auth.token = null;
        this.userData.remote = cloneDeep(this.defaultRemoteUserData);
        this.userData.account = cloneDeep(this.defaultAccountUserData);
        this.saveUserAuthData();
        this.notifyUserChanged();
        this.notifyLoginStateChanged();
    }

    deactivateAccount () {
        return this.http.delete('endpoint://account.deactivate').pipe(
            take(1),
            map(response => response === 'OK'),
            catchError(error => {
                console.warn('deactivateAccount error:', error);
                return throwError(error.error.status_code);
            })
        );
    }

    lockAccount (phone : string, status : string = 'ACCOUNT_DEBT_LOCK') {
        return this.http.get('endpoint://account.lock', {
            urlParams: {
                phone,
                lock_type: status
            }
        }).pipe(
            take(1),
            map(response => response === 'OK'),
            catchError(error => {
                console.warn('lockAccount error:', error);
                return throwError(error.error.status_code);
            })
        );
    }
}
