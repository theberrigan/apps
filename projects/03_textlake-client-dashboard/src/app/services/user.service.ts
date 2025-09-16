import { Injectable }  from '@angular/core';
import { merge } from 'lodash';
import { HttpService } from './http.service';
import {DEFAULT_LANG, LangService} from './lang.service';
import {empty, Observable, Subject, throwError} from 'rxjs';
import {catchError, map, retry, take} from 'rxjs/operators';

export type PostAuthAction = null | 'TERMS';

class UserProfile {
    primaryEmailVerified : boolean = false;
    alternativeUsers : any[] = [];
    user = {
        email: 'some-user@email.com'
    };
}

class UserSettings {
    panel = {
        notifications: {
            markType: 'counter'
        }
    };
}

class LocalUserData {
    language : string = DEFAULT_LANG.code;
    updateRemoteLangAfterSignIn : boolean = false;
}


export class UserFeatures {
    public features : any;

    constructor (features : any[]) {
        this.features = features.reduce((acc : any, feature : any) => {
            acc[feature.name] = {   // {name: "menu:offers", visible: true, result: null}
                data: feature.result,
                can: feature.visible
            };

            return acc;
        }, {});
    }

    public can (featureName : string) : boolean {
        return featureName in this.features && this.features[featureName].can;
    }

    public getData (featureName : string) : any {
        return featureName in this.features && this.features[featureName].data;
    }
}

export class UserData {
    profile : UserProfile = new UserProfile();
    settings : UserSettings = new UserSettings();
    local : LocalUserData = new LocalUserData();
    features : UserFeatures = new UserFeatures([]);
}

export enum MqttMessageType {
    Notification = 1,
    Profile = 3
}

const isUndefined = (x) => !!x;

@Injectable({
    providedIn: 'root',
})
export class UserService {
    public userData : UserData;

    public onUserDataUpdated = new Subject<UserData>();

    public routerData : { [ key : string ] : any } = {};

    public onAuthMessage = new Subject<any>();

    public onForceSignOut = new Subject<void>();

    private _postAuthAction : PostAuthAction = null;

    public set postAuthAction (action : PostAuthAction) {
        this._postAuthAction = action;
    }

    public userPool : any = {};
    public userSession : any = {};

    public get postAuthAction () : PostAuthAction {
        const action = this._postAuthAction;
        this._postAuthAction = null;
        return action;
    }

    constructor (
        private httpService : HttpService,
        private langService : LangService
    ) {}

    public restoreUser () : Promise<any> {
        return new Promise(resolve => {
            const localData = window.localStorage.getItem('localUserData');

            this.userData = new UserData();
            this.userData.local = merge({}, new LocalUserData(), localData ? JSON.parse(localData) : {});

            this.useLang().then(() => {
                resolve();
            });
        });
    }

    public getUserData () : any {
        return this.userData;
    }

    public getRouterData (key : string) : any {
        const data : any = key in this.routerData ? this.routerData[key] : null;
        delete this.routerData[key];
        return data;
    }

    public setRouterData (key : string, data : any) : void {
        this.routerData[key] = data;
    }

    public signOut () : Promise<void> {
        return new Promise((resolve) => {
            this.onForceSignOut.next();
            resolve();
        });
    }

    public useLang () : Promise<void> {
        return this.langService.use(this.userData.local.language).toPromise();
    }

    public checkVerificationCode (code : string) : Observable<any> {
        return empty();
    }

    public saveUserData (userData : UserData) : Promise<void> {
        return new Promise((resolve) => {
            const { local, settings, profile } = userData;

            if (local) {
                window.localStorage.setItem('localUserData', JSON.stringify(local));
            }

            resolve();
        });
    }

    public sendVerificationCode () : Observable<any> {
        return empty();
    }

    public updateUser (user : any) : Observable<any> {
        return this.httpService.put('endpoint://users.updateUser', {
            urlParams: {
                userId: user.id,
            },
            body: {
                active: user.active
            }
        }).pipe(
            retry(1),
            take(1),
            map((response : any) => response.user),
            catchError(error => {
                console.warn('updateUser error:', error);
                return throwError(error.error || null);
            })
        );
    }
    public signIn (signInData : {
        email : string,
        password : string,
        remember : boolean,
    }) : Promise<any> {
        return new Promise((resolve, reject) => {
            setTimeout(() => resolve({ action: 'COMPLETE' }), 1500);
        });
    }

    private updateToken () : void {
        /*
        this.resetTokenUpdateTimer();

        this.user.refreshSession(this.refreshToken, (err, session) => {
            if (err) {
                console.warn('Token refresh error (sign out):', err);
                // TODO: make force logout user-friendly
                this.signOut().then(() => {
                    this.drainTokenWaitQueue();
                    this.onForceSignOut.next();
                });
                return;
            }

            this.userSession = session;
            this.setTokenUpdateTimer();
            this.drainTokenWaitQueue();

            console.warn('Token is updated');
        });
         */
    }

    public checkLogout () : void {
        setTimeout(() => {
            new Promise(resolve => {
                const user = this.userPool.getCurrentUser();

                if (!user) {
                    return resolve(null);
                }

                user.getSession((err, session) => {
                    if (!err && session.isValid()) {
                        return resolve(session.getAccessToken().getJwtToken() || null);
                    }

                    resolve(null);
                });
            }).then(storageToken => {
                const memoryToken = this.userSession && this.userSession.getAccessToken().getJwtToken() || null;

                if (
                    storageToken && !this.userSession ||                          // user is logged in but current tab is logged out
                    !storageToken && this.userSession ||                          // user is logged out but current tab is logged in
                    storageToken && memoryToken && storageToken !== memoryToken   // in-memory session is outdated
                ) {
                    window.location.reload();
                }

                this.checkLogout();
            });
        }, 3500);
    }

    public updateUserData (options : {
        data : UserData,
        save? : boolean,
        notify? : boolean
    }) : Promise<void> {
        return new Promise((resolve) => {
            this.userData = options.data;

            Promise.all([
                this.useLang(),
                this.saveUserData(this.userData)
            ]).then(() => {
                resolve();
            });
        });
    }

    public fetchFromStorage2 (key : string) : Promise<any> {
        return this.httpService.get2('endpoint://userStorage', { urlParams: { key } })
            .then((response : any) => {
                const data = response.data;

                if (!data) {
                    return;
                }

                try {
                    return JSON.parse(data);
                } catch (e) {
                    console.warn(`Can't parse remote storage value:`, data);
                    return;
                }
            });
    }

    public saveToStorage (key : string, data : any) : Promise<boolean> {
        return new Promise((resolve) => {
            try {
                data = JSON.stringify(data);
            } catch (e) {
                console.warn(`Can't stringify data to save to remote storage:`, data);
                resolve(false);
                return;
            }

            this.fetchFromStorage2(key)
                .then((currentValue : any) => {
                    const requestOptions = {
                        body: { data },
                        urlParams: { key }
                    };

                    (
                        isUndefined(currentValue) ?
                            this.httpService.post2('endpoint://userStorage', requestOptions) :
                            this.httpService.put2('endpoint://userStorage', requestOptions)
                    )
                        .then(() => resolve(true))
                        .catch(() => resolve(false));
                });
        });
    }

    public deleteFromStorage (key : string) : Promise<any> {
        return this.httpService.delete2('endpoint://userStorage', { urlParams: { key } })
            .then(() => true)
            .catch(() => false);
    }

    public fetchFromStorage (key : string) : Observable<any> {
        return this.httpService.get('endpoint://userStorage', { urlParams: { key } }).pipe(
            retry(1),
            map((response : any) => {
                const data = response.data;

                if (!data) {
                    return;
                }

                try {
                    return JSON.parse(data);
                } catch (e) {
                    console.warn(`Can't parse remote storage value:`, data);
                    return;
                }
            })
        );
    }
}
