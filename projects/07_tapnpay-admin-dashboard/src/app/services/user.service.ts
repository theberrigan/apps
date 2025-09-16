import {Injectable, NgZone} from '@angular/core';
import {API_TOKEN_HEADER_KEY, HttpService} from './http.service';
import {take} from 'rxjs/operators';
import { ReplaySubject} from 'rxjs';
import {DEFAULT_LANG, ILang, LangService} from './lang.service';
import {CONFIG} from '../../../config/app/dev';
import {cloneDeep} from 'lodash-es';
import {deleteJsonFromLocalStorage, readJsonFromLocalStorage, saveJsonToLocalStorage} from '../lib/utils';
import {DebugService} from './debug.service';
import {StorageService} from './storage.service';
import {HttpErrorResponse} from '@angular/common/http';
import {ACCOUNT_LOCAL_STORAGE_KEY} from './account.service';


export interface LocalUserData {
    lang : string;
    shouldUpdateRemoteLang : boolean;
}

export interface RemoteUserData {
    lang : string;
    firstLoginDate : string;
    permissions : Permissions;
}

export interface AuthUserData {
    token : string;
}

export interface UserData {
    auth : AuthUserData;
    local : LocalUserData;
    remote : RemoteUserData;
}

interface GetTokenResponse {
    token : string;
    permissions : string[];
}

export type Permission = (
    'ACCOUNT_SEARCH' |
    'ACCOUNT_VIEW_SUMMARY' |
    'ACCOUNT_VIEW_OUTSTANDING_INVOICES' |
    'ACCOUNT_VIEW_TRANSACTIONS' |
    'ACCOUNT_VIEW_SMS' |
    'ACCOUNT_VIEW_ACTIONS' |
    'ACCOUNT_ACTIONS_SEND_PIN' |
    'ACCOUNT_ACTIONS_SEND_SMS' |
    'ACCOUNT_ACTIONS_UPDATE_DUE_DATE' |
    'FAQ_UPDATE' |
    'TOLL_AUTHORITY_LIST' |
    'TOLL_AUTHORITY_CREATE' |
    'TOLL_AUTHORITY_VIEW' |
    'TOLL_AUTHORITY_EDIT' |
    'MAP_EDIT' |
    'ACCOUNT_CLOSE' |
    'ACCOUNT_VIEW_DISPUTES' |
    'CONTRACT_CARRIER_EDIT' |
    'CONTRACT_CARRIER_VIEW' |
    'CONTRACT_PAYMENT_GATEWAY_EDIT' |
    'CONTRACT_PAYMENT_GATEWAY_VIEW' |
    'CONTRACT_TOLL_AUTHORITY_EDIT' |
    'CONTRACT_TOLL_AUTHORITY_VIEW' |
    'DISPUTES_UPLOAD'
);

export type Permissions = {
    [ key in Permission ] : boolean;
}

@Injectable({
    providedIn: 'root'
})
export class UserService {
    readonly supportedLangs : ILang[] = CONFIG.locales;

    readonly defaultLocalUserData : LocalUserData;

    readonly defaultRemoteUserData : RemoteUserData;

    readonly defaultAuthUserData : AuthUserData;

    userData : UserData;

    onUserChanged = new ReplaySubject<UserData>();

    onLoginStateChange = new ReplaySubject<boolean>();

    shouldRemoteSaveAfterUserInit : boolean = false;

    shouldSaveAuthDataAfterUserInit : boolean = false;

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
            firstLoginDate: new Date().toISOString(),
            permissions: <Permissions>{}
        };
    }

    createDefaultAuthUserData () : AuthUserData {
        return {
            token: null
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
                ]);
            }).then(([
                authData,
                remoteUserData,
                localUserData
            ] : [
                AuthUserData,
                RemoteUserData,
                LocalUserData
            ]) => {
                this.userData = {
                    auth: authData,
                    local: localUserData,
                    remote: remoteUserData
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

                console.log(this.userData);

                resolve(this.userData);
            });
        });
    }

    getLocalUserData () : Promise<LocalUserData> {
        return new Promise(resolve => {
            resolve(readJsonFromLocalStorage('localUserData', cloneDeep(this.defaultLocalUserData)));
        });
    }

    // TODO: debounce
    saveLocalUserData () {
        saveJsonToLocalStorage('localUserData', this.userData.local);
    }

    getRemoteUserData (token : string) : Promise<RemoteUserData> {
        return new Promise(resolve => {
            if (token) {
                Promise.all([
                    this.storageService.get('user_data', token).toPromise(),
                    this.fetchPermissions(token)
                ]).then(([ userData, permissions ] : [ RemoteUserData, string[] ]) => {
                    if (!userData) {
                        userData = cloneDeep(this.defaultRemoteUserData);
                        this.shouldRemoteSaveAfterUserInit = true;
                    }

                    userData.permissions = this.convertPermissions(permissions);

                    resolve(userData);
                }).catch(() => {
                    resolve(cloneDeep(this.defaultRemoteUserData))
                });
            } else {
                resolve(cloneDeep(this.defaultRemoteUserData));
            }
        });
    }

    // TODO: debounce
    saveRemoteUserData () {
        if (this.isLoggedIn()) {
            const remoteData = cloneDeep(this.userData.remote);

            // Do not send permissions
            delete remoteData['permissions'];

            this.storageService.create('user_data', remoteData).subscribe(isOk => {
                console.log('Remote user data update:', isOk);
            });
        }
    }

    getUserAuthData () : Promise<AuthUserData> {
        const rawAuthData = readJsonFromLocalStorage('authUserData', cloneDeep(this.defaultAuthUserData));
        return this.validateAuthData(rawAuthData);
    }

    // TODO: debounce
    saveUserAuthData () {
        if (!this.userData.auth.token) {
            deleteJsonFromLocalStorage(ACCOUNT_LOCAL_STORAGE_KEY);
        }

        saveJsonToLocalStorage('authUserData', this.userData.auth);
    }

    validateAuthData (authUserData : AuthUserData) : Promise<AuthUserData> {
        return new Promise(resolve => {
            if (!authUserData.token) {
                return resolve(authUserData);
            }

            this.http.options('endpoint://auth.validateToken', {
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

    fetchPermissions (token : string) : Promise<string[]> {
        return this.http.get('endpoint://auth.getPermissions', {
            headers: {
                [ API_TOKEN_HEADER_KEY ]: token
            }
        })
            .pipe(take(1))
            .toPromise()
            .then(({ permissions }) => permissions)
            .catch((error : HttpErrorResponse) => {
                console.warn('fetchPermissions error:', error);
                return [];
            });
    }

    // -----------------------------------------------------------------------

    getFirstLoginDate () : string {
        return this.userData?.remote?.firstLoginDate;
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

    checkPermission (permission : Permission) : boolean {
        return this.getPermissions()[permission] === true;
    }

    getPermissions () : Permissions {
        return this.userData?.remote?.permissions || <Permissions>{};
    }

    setPermissions (permissions : string[]) {
        if (!this.userData || !this.userData.remote) {
            return;
        }

        this.userData.remote.permissions = this.convertPermissions(permissions || []);
    }

    convertPermissions (permissions : string[]) : Permissions {
        return permissions.reduce((acc : any, permission : string) => {
            acc[permission] = true;
            return acc;
        }, {});
    }

    // -----------------------------------------------------------------------

    getUserData () : UserData {
        return this.userData;
    }

    isLoggedIn () : boolean {
        return !!(this.userData?.auth?.token);
    }

    fetchAuthUrl () : Promise<string> {
        return this.http.get('endpoint://auth.get-url', {
            urlParams: {
                brand: CONFIG.authBrand
            }
        })
            .pipe(take(1))
            .toPromise()
            .then(response => response && response.url || null)
            .catch((error : HttpErrorResponse) => {
                console.warn('fetchLoginUrl error:', error);
                return null;
            });
    }

    auth (code : string) : Promise<boolean> {
        return this.http.post('endpoint://auth.get-token', {
            body: {
                code,
                brand: CONFIG.authBrand
            }
        })
            .pipe(take(1))
            .toPromise()
            .then(({ token, permissions } : GetTokenResponse) => {
                return this.storageService.get('user_data', token)
                    .toPromise()
                    .then((remoteUserData : RemoteUserData) => {
                        if (!remoteUserData) {
                            remoteUserData = cloneDeep(this.defaultRemoteUserData);
                            this.shouldRemoteSaveAfterUserInit = true;
                        }

                        this.userData.remote = remoteUserData;

                        this.setAuthToken(token);
                        this.setPermissions(permissions);

                        // TODO: saved twice
                        if (this.userData.local?.shouldUpdateRemoteLang) {
                            this.userData.remote.lang = this.userData.local.lang;
                            this.userData.local.shouldUpdateRemoteLang = false;
                            this.shouldRemoteSaveAfterUserInit = true;
                            this.saveLocalUserData();
                        }

                        // TODO: saved twice
                        if (this.shouldRemoteSaveAfterUserInit) {
                            this.shouldRemoteSaveAfterUserInit = false;
                            this.saveRemoteUserData();
                        }

                        this.notifyUserChanged();
                        this.notifyLoginStateChanged();

                        return true;
                    })
                    .catch((error) => {
                        console.warn('error:', error);
                        return false;
                    });
            })
            .catch((error : HttpErrorResponse) => {
                console.warn('auth error:', error);
                return false;
            });
    }

    /*
    applyToken (token : string | null) : Promise<boolean> {
        return new Promise((resolve) => {
            this.getRemoteUserData(token).then((remoteUserData : RemoteUserData) => {
                if (!token) {
                    return resolve(false);
                }

                this.setAuthToken(token);
                this.userData.remote = remoteUserData;

                // TODO: saved twice
                if (this.userData.local?.shouldUpdateRemoteLang) {
                    this.userData.remote.lang = this.userData.local.lang;
                    this.userData.local.shouldUpdateRemoteLang = false;
                    this.shouldRemoteSaveAfterUserInit = true;
                    this.saveLocalUserData();
                }

                // TODO: saved twice
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
     */

    logout () {
        this.userData.auth.token = null;
        this.userData.remote = cloneDeep(this.defaultRemoteUserData);
        this.saveUserAuthData();
        this.notifyUserChanged();
        this.notifyLoginStateChanged();
    }
}
