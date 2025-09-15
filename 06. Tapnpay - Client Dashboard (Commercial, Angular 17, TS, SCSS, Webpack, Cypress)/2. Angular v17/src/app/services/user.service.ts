import {Injectable, NgZone} from '@angular/core';
import {API_TOKEN_HEADER_KEY, HttpService} from './http.service';
import {catchError, map, take} from 'rxjs/operators';
import {BehaviorSubject, Observable, throwError} from 'rxjs';
import {DEFAULT_LANG, ILang, LangService} from './lang.service';
import {CONFIG} from '../../../config/app/dev';
import {cloneDeep} from 'lodash-es';
import {readJsonFromLocalStorage, saveJsonToLocalStorage} from '../lib/utils';
import {StorageService} from './storage.service';
import { HttpErrorResponse } from '@angular/common/http';
import {IsShowAddVehicleModalAfterLoginService} from "./is-show-add-vehicle-modal-after-login.service";

export type AccountPaymentModel = 'UNKNOWN' | 'POSTPAID' | 'FLEET';
export type AccountTollAuthority = string;
export type AccountStatus = 'ACTIVE' | 'ACCOUNT_DEBT_LOCK' | 'ACCOUNT_SOFT_LOCK' | 'SUBSCRIPTION_EXPIRED' | 'OTHER' ;

export interface LocalUserData {
    lang: string;
    shouldUpdateRemoteLang: boolean;
}

export interface RemoteUserData {
    lang: string;
    firstLoginDate: string;
}

export interface AuthUserData {
    token: string;
}

export interface AccountUserData {
    tollAuthority: AccountTollAuthority;
    paymentModel: AccountPaymentModel;
    accountStatus: AccountStatus;
}

export interface UserData {
    auth: AuthUserData;
    local: LocalUserData;
    remote: RemoteUserData;
    account: AccountUserData;
}

// Interface for user-details API response
export interface ApiUserDetailsData {
    status: string;
    user_details: {
        account_status: string;
        terms_accepted: string | null;
        first_name: string | null;
        last_name: string | null;
        email: string | null;
        email_verified_at: string | null;
    };
}

export const TEST_ACCOUNT_CREATE_PHONES = {
    DEFAULT: '18555172507',
    NTAA: '18554827672',
    SUNPASS: '18555172507',
    IPASS: '18336440841',
    FASTRAK: '18555172927',
    GOODTOGO: '18553911030',
    TXHUB: '18882066777'
}

interface DefaultUserData {
    local: LocalUserData;
    remote: RemoteUserData;
    auth: AuthUserData;
    account: AccountUserData;
}

@Injectable({
    providedIn: 'root'
})
export class UserService {
    readonly supportedLangs: ILang[] = CONFIG.locales;

    readonly defaultUserData: DefaultUserData = {} as DefaultUserData;


    // User is new if no more than 24 hours have passed since the first login
    readonly isNewUserMaxTime: number = 24 * 60 * 60 * 1000;

    userData: UserData;

    userData$ = new BehaviorSubject<UserData>(null);

    isUserLogin$ = new BehaviorSubject<boolean>(null);

    _isRegNPay: boolean = false;

    shouldRemoteSaveAfterUserInit: boolean = false;

    shouldSaveAuthDataAfterUserInit: boolean = false;

    _testFleetUserPhone: string = null;

    apiUserDetailsData: ApiUserDetailsData = null;

    constructor(
        private http: HttpService,
        private langService: LangService,
        private storageService: StorageService,
        private zone: NgZone,
        private isShowAddVehicleModalAfterLoginService: IsShowAddVehicleModalAfterLoginService
    ) {
        this.defaultUserData.local = this.createDefaultLocalUserData();
        this.defaultUserData.remote = this.createDefaultRemoteUserData(this.defaultUserData.local);
        this.defaultUserData.auth = this.createDefaultAuthUserData();
        this.defaultUserData.account = this.createDefaultAccountUserData();

    }

    public setAppLang(lang: string) {
        this.zone.run(() => this.setLang(lang));
    }

    public getLangNames(): string {
        return this.supportedLangs.map((lang: ILang) => JSON.stringify(lang.code)).join(', ');
    }

    createDefaultLocalUserData(): LocalUserData {
        const data: LocalUserData = {
            lang: DEFAULT_LANG.code,
            shouldUpdateRemoteLang: false
        };

        const browserLocales = [
            navigator.language,
            ...navigator.languages
        ].reduce((acc: string[], lang: string) => {
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

    createDefaultRemoteUserData(defaultLocalUserData: LocalUserData): RemoteUserData {
        return {
            lang: defaultLocalUserData.lang,
            firstLoginDate: new Date().toISOString()
        };
    }

    createDefaultAuthUserData(): AuthUserData {
        return {
            token: null
        };
    }

    createDefaultAccountUserData(): AccountUserData {
        return {
            tollAuthority: null,
            paymentModel: null,
            accountStatus: 'ACTIVE',
        };
    }

    async getUserDetailsFromApi(token: string): Promise<ApiUserDetailsData> {
        if (!token) return null;
        try {
            const response = await this.http.get('endpoint://user.getDetails', {
                headers: {
                    [API_TOKEN_HEADER_KEY]: token
                }
            }).pipe(take(1)).toPromise();
            return response as ApiUserDetailsData;
        } catch (error) {
            console.warn('getUserDetailsFromApi error:', error);
            return null;
        }
    }

    async initUser(): Promise<UserData> {
        const authData = await this.getUserAuthData();
        const [remoteUserData, localUserData, accountUserData, apiUserDetailsData] = await Promise.all([
            this.getRemoteUserData(authData.token),
            this.getLocalUserData(),
            this.getAccountUserData(authData.token),
            this.getUserDetailsFromApi(authData.token)
        ]);
        this.userData = {
            auth: authData,
            local: localUserData,
            remote: remoteUserData,
            account: accountUserData
        };
        this.apiUserDetailsData = apiUserDetailsData;
        if (this.shouldRemoteSaveAfterUserInit) {
            this.shouldRemoteSaveAfterUserInit = false;
            this.saveRemoteUserData();
        }
        if (this.shouldSaveAuthDataAfterUserInit) {
            this.shouldSaveAuthDataAfterUserInit = false;
            this.saveUserAuthData();
        }
        this.notifyUserDataChanged();
        this.notifyLoginStateChanged();
        return this.userData;
    }


    getLocalUserData(): Promise<LocalUserData> {
        return new Promise(resolve => {
            resolve(readJsonFromLocalStorage('localUserData', cloneDeep(this.defaultUserData.local)));
        });
    }

    public refreshAccountStatus() {
        return this.http.get('endpoint://account.getUserData').pipe(
            take(1),
            map((response: {
                    account_status: AccountStatus;
                }) => {
                    if (this.userData) {
                        this.userData.account.accountStatus = response.account_status
                    }
                    return response.account_status
                }
            ));
    }

    async getAccountUserData(token: string): Promise<AccountUserData> {
        if (!token) {
            return Promise.resolve(cloneDeep(this.defaultUserData.account));
        }

        return this.http.get('endpoint://account.getUserData', {
            headers: {
                [API_TOKEN_HEADER_KEY]: token
            }
        }).pipe(
            take(1),
            map((response: {
                status: 'OK' | 'ERROR';
                toll_authority_model: 'POSTPAID' | 'FLEET';
                toll_authority: string;
                account_status: AccountStatus;
            }) => {
                let accountData: AccountUserData = cloneDeep(this.defaultUserData.account);

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
            catchError((error: HttpErrorResponse) => {
                console.warn('getAccountUserData error:', error);
                return throwError(error.error.status_code || error.error.status);
            })
        ).toPromise().catch(() => {
            return cloneDeep(this.defaultUserData.account);
        });
    }

    // TODO: debounce
    saveLocalUserData() {
        saveJsonToLocalStorage('localUserData', this.userData.local);
    }

    getRemoteUserData(token: string): Promise<RemoteUserData> {
        return new Promise(resolve => {
            if (token) {
                this.storageService.get('user_data', token).subscribe(
                    (userData: RemoteUserData) => {
                        if (!userData) {
                            userData = cloneDeep(this.defaultUserData.remote);
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
                    () => resolve(cloneDeep(this.defaultUserData.remote))
                );
            } else {
                console.log('response.token after in storage else:', token);
                resolve(cloneDeep(this.defaultUserData.remote));
            }
        });
    }

    // TODO: debounce
    saveRemoteUserData() {
        if (this.isLoggedIn()) {
            this.storageService.create('user_data', this.userData.remote).subscribe(isOk => {
                console.log('Remote user data update:', isOk);
            });
        }
    }

    getUserAuthData(): Promise<AuthUserData> {
        const authUserData = readJsonFromLocalStorage('authUserData', cloneDeep(this.defaultUserData.auth));
        return this.validateAuthData(authUserData);
    }

    // TODO: debounce
    saveUserAuthData() {
        saveJsonToLocalStorage('authUserData', this.userData.auth);
    }

    // TODO: remote token validation
    validateAuthData(authUserData: AuthUserData): Promise<AuthUserData> {
        return new Promise(resolve => {
            if (!authUserData.token) {
                return resolve(authUserData);
            }

            this.http.options('endpoint://auth.validate-token', {
                headers: {
                    [API_TOKEN_HEADER_KEY]: authUserData.token
                }
            })
                .pipe(take(1))
                .toPromise()
                .then(({status}) => status === 'OK')
                .catch(() => false)
                .then((isTokenValid: boolean) => {
                    if (!isTokenValid) {
                        authUserData.token = null;
                        this.shouldSaveAuthDataAfterUserInit = true;
                    }

                    resolve(authUserData);
                });
        });
    }

    notifyUserDataChanged() {
        this.userData$.next(this.userData);
    }

    notifyLoginStateChanged() {
        this.isUserLogin$.next(this.isLoggedIn());
    }

    // TODO: debounce
    // -----------------------------------------------------------------------

    public isNewUser(): boolean {
        const firstLoginDate = this.getFirstLoginDate();
        console.log('firstLoginDate:', firstLoginDate);
        if (!firstLoginDate) {
            return false;
        }

        const msFromFirstLogin = new Date().getTime() - new Date(firstLoginDate).getTime();

        return (msFromFirstLogin < this.isNewUserMaxTime);
    }

    public isRegNPay() {
        return this._isRegNPay;
    }

    public setUserActive() {
        this.userData.account.accountStatus = "ACTIVE";
    }

    public getLang(): string {
        if (this.isLoggedIn()) {
            return this.userData?.remote?.lang || this.defaultUserData.remote.lang;
        } else {
            return this.userData?.local?.lang || this.defaultUserData.local.lang;
        }
    }

    setLang(lang: string) {
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
        this.notifyUserDataChanged();
    }

    getAuthToken(): string {
        return this.userData?.auth?.token || this.defaultUserData.auth.token;
    }

    setAuthToken(token: string) {
        if (!this.userData || !this.userData.auth) {
            return;
        }

        this.userData.auth.token = token;
        this.saveUserAuthData();
        this.notifyUserDataChanged();
    }

    getUserData(): UserData {
        return this.userData;
    }

    isLoggedIn(): boolean {
        return !!(this.userData?.auth?.token);
    }


    // -----------------------------------------------------------------------

    getTestAccountPin(phone: string): Observable<string> {
        return this.http.get('endpoint://test.get-account-pin', {
            urlParams: {phone},
            responseType: 'text'
        }).pipe(
            take(1),
            catchError(error => {
                this.logNetworkError(error, 'getTestAccountPin');
                return throwError(error);
            })
        );
    }

    createTestAccount() {
        return this.http.get('endpoint://test.create-account').pipe(
            take(1),
            map((credentials: { phone: string, pin: string }) => {
                return credentials;
            }),
            catchError(error => {
                this.logNetworkError(error, 'createTestUser');
                return throwError(error);
            })
        );
    }

    createTestFleetAccount(phone: string = TEST_ACCOUNT_CREATE_PHONES.DEFAULT) {
        return this.http.get('endpoint://fleet.createTestAcc', {
            urlParams: {phone}
        }).pipe(
            take(1),
            map((credentials: { phone: string, pin: string, token: string }) => {
                this._testFleetUserPhone = credentials.phone;
                return credentials;
            }),
            catchError(error => {
                this.logNetworkError(error, 'createTestFleetAccount');
                return throwError(error);
            })
        );
    }

    createTestFleetAccountWithOTFSubscription(phone: string = TEST_ACCOUNT_CREATE_PHONES.DEFAULT) {
        return this.http.get('endpoint://fleet.createTestAccOTF', {
            urlParams: {phone}
        }).pipe(
            take(1),
            map((credentials: { phone: string, pin: string, token: string }) => {
                this._testFleetUserPhone = credentials.phone;
                return credentials;
            }),
            catchError(error => {
                this.logNetworkError(error, 'createTestFleetAccountOTF');
                return throwError(error);
            })
        );
    }

    generateInvoices(phone: string = null) {
        return this.http.get('endpoint://fleet.generateInvoices', {
            urlParams: {
                phone: phone || this._testFleetUserPhone
            }
        }).pipe(
            take(1),
            catchError(error => {
                this.logNetworkError(error, 'generateInvoices');
                return throwError(error);
            })
        );
    }

    sendPhone(phone: string): Observable<boolean> {
        return this.http.post('endpoint://auth.send-phone', {
            body: {
                phone
            }
        }).pipe(
            take(1),
            map(response => response.status === 'OK'),
            catchError(error => {
                this.logNetworkError(error, 'sendPhone');
                return throwError(error);
            })
        );
    }

    // TODO extract to token validation service
    applyToken(token: string | null, isRegNPay: boolean = false): Promise<boolean> {
        return new Promise((resolve) => {
            Promise.all([
                this.getRemoteUserData(token),
                this.getAccountUserData(token),
                this.getUserDetailsFromApi(token)
            ]).then(([
                remoteUserData,
                accountUserData,
                apiUserDetailsData
            ]: [
                RemoteUserData,
                AccountUserData,
                ApiUserDetailsData
            ]) => {
                if (!token) {
                    return resolve(false);
                }
                this.setIsRegNPay(isRegNPay);
                this.setAuthToken(token);
                this.userData.account = accountUserData;
                this.userData.remote = remoteUserData;
                this.apiUserDetailsData = apiUserDetailsData;
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
                this.notifyUserDataChanged();
                this.notifyLoginStateChanged();
                return resolve(true);
            });
        });
    }

    validateToken(token: string): Observable<boolean> {
        return this.http.options('endpoint://auth.validate-token', {
            headers: {
                [API_TOKEN_HEADER_KEY]: token
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

    // TODO extract to auth service
    login(credentials: { phone: string, pin: string }): Promise<{
        isOk: boolean;
        errorCode: number;
    }> {
        return this.http.post('endpoint://auth.send-pin', {
            body: credentials
        })
            .pipe(take(1))
            .toPromise()
            .then(response => {
                const isNotLogin = !response || response.status !== 'OK' || !response.token;
                const loginErrorBaseResolveMessage = {
                    isOk: false,
                    errorCode: 0
                };

                if (isNotLogin) {
                    return Promise.resolve(loginErrorBaseResolveMessage);
                }
                console.log('response.token before:', response.token);
                return this.applyToken(response.token).then(isOk => ({
                    isOk,
                    errorCode: 0
                }));
            }).catch((error: HttpErrorResponse) => {
                console.warn('login error:', error);
                return {
                    isOk: false,
                    errorCode: error.error.status_code
                };
            });
    }

    // TODO extract to token validation service

    logout() {
        this.userData.auth.token = null;
        saveJsonToLocalStorage('showNeorideBanner', null);
        this.userData.remote = cloneDeep(this.defaultUserData.remote);
        this.userData.account = cloneDeep(this.defaultUserData.account);
        this.saveUserAuthData();
        this.notifyUserDataChanged();
        this.notifyLoginStateChanged();
        this.isShowAddVehicleModalAfterLoginService.deleteOption();
    }

    deactivateAccount() {
        return this.http.delete('endpoint://account.deactivate').pipe(
            take(1),
            map(response => response === 'OK'),
            catchError(error => {
                console.warn('deactivateAccount error:', error);
                return throwError(error.error.status_code);
            })
        );
    }

    lockAccount(phone: string, status: string = 'ACCOUNT_DEBT_LOCK') {
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

    logNetworkError(error: HttpErrorResponse, methodName: string = '') {
        if (error.error) {
            console.warn(`${methodName} error:\n\t${error.url}\n\t${error.error.status_code} ${error.error.status} ${error.error.message}\n\tError object:`, error);
        } else {
            console.warn(`${methodName} error:\n\t${error.url}\n\t${error.status} ${error.statusText} ${error.name} ${error.message}\n\tError object:`, error);
        }
    }

    private getFirstLoginDate(): string {
        return this.userData?.remote?.firstLoginDate;
    }

    private setIsRegNPay(isRegNPay: boolean) {
        this._isRegNPay = isRegNPay;
    }

    getToken(): string {
        return this.getAuthToken();
    }

    public isAccountActive(): boolean {
        const accountStatus = this.apiUserDetailsData?.user_details?.account_status;
        console.log('apiUserDetailsData.account_status:', accountStatus);
        return accountStatus === 'ACTIVE' || accountStatus === 'SUSPICIOUS_ACTIVITY' || accountStatus === 'ACCOUNT_DEBT_LOCK' || accountStatus === 'SUBSCRIPTION_EXPIRED';
    }
}
