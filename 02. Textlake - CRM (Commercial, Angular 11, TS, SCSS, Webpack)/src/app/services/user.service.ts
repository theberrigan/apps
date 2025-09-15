import { Injectable } from '@angular/core';
import {Observable, of, Subject, throwError} from 'rxjs';
import {merge, isUndefined, includes, forOwn, findKey, isFinite} from 'lodash';

import { CognitoUserPool, CognitoUserAttribute, CognitoUser, CognitoUserSession, AuthenticationDetails, CognitoRefreshToken } from 'amazon-cognito-identity-js';
import { CognitoAuth } from 'amazon-cognito-auth-js';
import { default as AWSClient } from 'aws-api-gateway-client';
import * as AWSIoT              from 'aws-iot-device-sdk';

import {CONFIG} from '../../../config/app/dev';
import { SocialAuthProvider } from '../modules/auth/auth.component';
import {DEFAULT_LANG, LangService} from './lang.service';
import { API_TOKEN_HEADER_KEY, HttpService } from './http.service';
import {uniqueId, getTimestamp, isSameObjectsLayout, updateObject} from '../lib/utils';
import {catchError, concatMap, delay, map, retry, retryWhen, take} from 'rxjs/operators';

export type PostAuthAction = null | 'PLAN' | 'TERMS';

export class UserProfile {
    public companyId : number;
    public language : string;
    public primaryEmailVerified : boolean;

    public alternativeUsers : {
        companyId : number;
        companyName : string;
        firstName : string;
        id : number;
        lastName: string;
    }[];

    public user : {
        active : boolean;
        email : string;
        firstName : string;
        id : number;
        lastName : string;
        verifiedEmail : boolean;
    };
}

export class UserLocalData {
    public language : string = DEFAULT_LANG.code;
    public updateRemoteLangAfterSignIn : boolean = false;
}

export class UserSettings {
    public useZebra : boolean = true;

    public formats : { [ key : string ] : { [ key : string ] : string } } = {
        date: {
            display: 'D MMM YY',
            select: 'DD.MM.YY'
        },
        time: {
            display: 'HH:mm',
            select: 'HH:mm'
        },
        datetime: {
            display: 'D MMM YY HH:mm',
            select: 'DD.MM.YY HH:mm'
        }
    };

    public panel = {
        tasks: {
            markType: 'counter'
        },
        notifications: {
            markType: 'counter'
        }
    };
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
    public profile : UserProfile = null;     // profile/me
    public settings : UserSettings = null;   // remote storage
    public local : UserLocalData = null;     // local storage
    public features : UserFeatures = null;   // features

    // constructor (data : any = {}) {
    //     Object.keys(data).forEach((key : string) => {
    //         if (key in this) {
    //             this[key] = data[key];
    //         }
    //     });
    // }
}

export enum MqttMessageType {
    Notification = 1,
    Task = 2,
    Profile = 3
}

export class User {
    id : number = null;
    active : boolean = false;
    email : string = '';
    firstName : string = '';
    lastName : string = '';
    verifiedEmail : boolean = false;
}

export class UserRole {
    description : string = null;
    key : string = null;
}

const USER_FEATURES : string[] = [
    'menu:offers',
    'menu:projects',
    'menu:mailbox',
    'menu:clients',
    'menu:translators',
    'menu:billings',
    'menu:settings',
    'settings:mailbox',
    'settings:roles',
    'settings:currencies',
    'settings:company-profile',
    'settings:services',
    'settings:rates',
    'settings:taxes',
    'settings:invitations',
    'settings:payment-providers',
    'settings:subscriptions',
    'settings:sofort',
    'settings:calculation-rules',
    'edit:offers',
    'edit:projects',
    'edit:clients',
    'edit:translators',
    'edit:currencies',
    'view:changelog',
];

const USER_FRIENDLY_COGNITO_ERRORS : string[] = [
    'UserNotFoundException',
    'PasswordResetRequiredException',
    'CodeMismatchException',
    'ExpiredCodeException',
    'NotAuthorizedException',
    'InvalidPasswordException',
    'UsernameExistsException',
    'InvalidParameterException'
];

@Injectable({
    providedIn: 'root'
})
export class UserService {
    public userPool : CognitoUserPool;

    public user : CognitoUser;

    public userSession : CognitoUserSession;

    public userData : UserData;

    public tokenExpireTimeout : any = null;

    public routerData : { [ key : string ] : any } = {};

    public onAuthMessage = new Subject<any>();

    public onUserDataUpdated = new Subject<UserData>();

    public onMqttMessage = new Subject<{ message : any, topic : string }>();

    public onForceSignOut = new Subject<void>();

    private _postAuthAction : PostAuthAction = null;

    public set postAuthAction (action : PostAuthAction) {
        this._postAuthAction = action;
    }

    public get postAuthAction () : PostAuthAction {
        const action = this._postAuthAction;
        this._postAuthAction = null;
        return action;
    }

    private mqttClient : AWSIoT.Device = null;

    private mqttExpireTimeout : any = null;

    private mqttConnectionId : string = null;

    private tokenWaitQueue : Subject<string>[] = [];

    constructor (
        private http : HttpService,
        private langService : LangService
    ) {
        this.userPool = new CognitoUserPool({
            UserPoolId: CONFIG.aws.cognito.userPoolId,
            ClientId: CONFIG.aws.cognito.clientId
        });

        // this.checkLogout();

        // TODO: remove
        // if (!CONFIG.isProduction) {
        //     (window as any).userService = this;
        // }

        // setTimeout(() => {
        //     console.log(this.tokenWaitQueue);
        // }, 5000)
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

    public waitForAccessToken () : Observable<string> {
        if (this.accessToken) {
            return Observable.create((observer) => observer.next(this.accessToken));
        }

        if (this.userSession) {
            return this.pushToTokenWaitQueue();
        }

        return Observable.create((observer) => observer.next(null));
    }

    public pushToTokenWaitQueue () : Observable<string> {
        const subject = new Subject<string>();
        this.tokenWaitQueue.push(subject);
        return subject.asObservable();
    }

    public drainTokenWaitQueue () : void {
        this.tokenWaitQueue.forEach(subject => subject.next(this.accessToken));
        this.tokenWaitQueue = [];
    }

    public static getCognitoErrorKey (cognitoError : any) : string {
        const errorCode : string = cognitoError.code || cognitoError.name;
        return ('auth.errors.' + (includes(USER_FRIENDLY_COGNITO_ERRORS, errorCode) ? errorCode : 'UnknownError'));
    }

    public setRouterData (key : string, data : any) : void {
        this.routerData[key] = data;
    }

    public getRouterData (key : string) : any {
        const data : any = key in this.routerData ? this.routerData[key] : null;
        delete this.routerData[key];
        return data;
    }

    public restoreLogin () : string {
        return (window.localStorage.getItem('login') || '').trim();
    }

    public saveLogin (remember : boolean, email : string) : void {
        if (remember === true && email) {
            window.localStorage.setItem('login', email);
        } else if (remember === false || remember === true && !email) {
            window.localStorage.removeItem('login');
        }
    }

    public textlakeSignIn (options : {
        user : CognitoUser,
        session : CognitoUserSession,
        remember? : boolean,
        email? : string
    }) : Promise<any> {
        return new Promise((resolve) => {
            this.http.post2('endpoint://challenge.login', {
                headers: {
                    [ API_TOKEN_HEADER_KEY ]: options.session.getAccessToken().getJwtToken()
                }
            })
                .then(data => {
                    return this.setupUser({
                        user: options.user,
                        session: options.session,
                        postAuthAction: data.nextChallenge
                    });
                })
                .then(() => {
                    this.saveLogin(options.remember, options.email);
                    resolve({ action: 'COMPLETE' });
                })
                .catch(reason => {
                    console.warn('textlakeSignIn error:', reason);

                    resolve({
                        action: 'ERROR',
                        error: 'auth.errors.UnknownError'
                    });
                });
        });
    }

    public forgotPassword (restoreData : { email : string }) : Promise<any> {
        return new Promise((resolve) => {
            const user : CognitoUser = new CognitoUser({
                Username: restoreData.email,
                Pool: this.userPool
            });

            user.forgotPassword({
                onSuccess: (data : any) => {
                    resolve({
                        action: 'COMPLETE',
                        extra: {
                            destination: data.CodeDeliveryDetails.Destination,
                            user
                        }
                    });
                },
                onFailure: (err : any) => {
                    console.warn('forgotPassword error:', err);

                    resolve({
                        action: 'ERROR',
                        error: UserService.getCognitoErrorKey(err)
                    });
                }
            });
        });
    }

    public confirmPassword (resetData : {
        code : string,
        newPassword : string,
        email? : string,
        user? : CognitoUser
    }) : Promise<any> {
        return new Promise((resolve) => {
            const user : CognitoUser = resetData.user || (new CognitoUser({
                Username: resetData.email,
                Pool: this.userPool
            }));

            user.confirmPassword(
                resetData.code,
                resetData.newPassword,
                {
                    onSuccess: () => resolve({ action: 'COMPLETE' }),
                    onFailure: (err : any) => {
                        resolve({
                            action: 'ERROR',
                            error: UserService.getCognitoErrorKey(err)
                        });
                    }
                }
            );
        });
    }

    public completeNewPasswordChallenge (newPasswordData : {
        email : string,
        remember : boolean,
        user : CognitoUser,
        userAttributes : any,
        newPassword : string
    }) : Promise<any> {
        return new Promise((resolve) => {
            const user : CognitoUser = newPasswordData.user;

            user.completeNewPasswordChallenge(
                newPasswordData.newPassword,
                newPasswordData.userAttributes,
                {
                    onSuccess: (session : CognitoUserSession, userConfirmationNecessary? : boolean) => {
                        this.textlakeSignIn({
                            user,
                            session,
                            remember: newPasswordData.remember,
                            email: newPasswordData.email
                        })
                        .then(result => resolve(result));
                    },
                    onFailure: (err : any) => {
                        console.warn('Complete new password challenge error:', err);

                        resolve({
                            action: 'ERROR',
                            error: UserService.getCognitoErrorKey(err)
                        });
                    },
                    mfaRequired: (challengeName : any, challengeParameters : any) => {
                        console.warn(`MFA isn't implemented:`, challengeName, challengeParameters);

                        resolve({
                            action: 'ERROR',
                            error: 'auth.errors.UnknownError'
                        });
                    },
                    customChallenge: (challengeParameters : any) => {
                        console.warn(`Custom challenges aren't implemented:`, challengeParameters);

                        resolve({
                            action: 'ERROR',
                            error: 'auth.errors.UnknownError'
                        });
                    }
                }
            );
        });
    }

    public signIn (signInData : {
        email : string,
        password : string,
        remember : boolean,
    }) : Promise<any> {
        return new Promise((resolve, reject) => {
            const user = new CognitoUser({
                Username: signInData.email.toLowerCase(),
                Pool: this.userPool
            });

            user.authenticateUser(
                new AuthenticationDetails({
                    Username: signInData.email.toLowerCase(),
                    Password: signInData.password
                }),
                {
                    onSuccess: (session : CognitoUserSession, userConfirmationNecessary? : boolean) => {
                        this.textlakeSignIn({
                            user,
                            session,
                            remember: signInData.remember,
                            email: signInData.email
                        })
                        .then(result => resolve(result));
                    },
                    onFailure: (err : any) => {
                        console.warn(`signIn error:`, err);

                        resolve({
                            action: 'ERROR',
                            error: UserService.getCognitoErrorKey(err)
                        });
                    },
                    newPasswordRequired: (userAttributes : any, requiredAttributes : any) => {
                        delete userAttributes.email_verified;

                        resolve({
                            action: 'NEW_PASSWORD',
                            extra: {
                                user,
                                userAttributes,
                                email: signInData.email,
                                remember: signInData.remember
                            }
                        });
                    },
                    mfaRequired: (challengeName : any, challengeParameters : any) => {
                        console.warn(`MFA isn't implemented:`, challengeName, challengeParameters);

                        resolve({
                            action: 'ERROR',
                            error: 'auth.errors.UnknownError'
                        });
                    },
                    totpRequired: (challengeName : any, challengeParameters : any) => {
                        console.warn(`TOTP isn't implemented:`, challengeName, challengeParameters);

                        resolve({
                            action: 'ERROR',
                            error: 'auth.errors.UnknownError'
                        });
                    },
                    customChallenge: (challengeParameters : any) => {
                        console.warn(`Custom challenges aren't implemented:`, challengeParameters);

                        resolve({
                            action: 'ERROR',
                            error: 'auth.errors.UnknownError'
                        });
                    }
                    // mfaSetup?: (challengeName: any, challengeParameters: any) => void,
                    // selectMFAType?: (challengeName: any, challengeParameters: any) => void
                }
            );
        });
    }

    public signUp (signUpData : {
        email : string,
        password : string,
    }) : Promise<any> {
        return new Promise((resolve) => {
            this.userPool.signUp(
                signUpData.email.toLowerCase(),
                signUpData.password,
                [
                    new CognitoUserAttribute({
                        Name : 'email',
                        Value : signUpData.email.toLowerCase()
                    })
                ],
                null,  // validationData
                (err, result) => {
                    if (err) {
                        // const user = this.userPool.getCurrentUser();
                        // user && user.signOut();

                        console.warn('signUp error:', err);

                        resolve({
                            action: 'ERROR',
                            error: UserService.getCognitoErrorKey(err)
                        });

                        return;
                    }

                    this.signIn({
                        remember: false,
                        ...signUpData
                    }).then((result : any) => resolve(result));
                }
            );
        });
    }

    // ----------------------------
    // ----------------------------

    public createSocialAuthProvider (providerName? : SocialAuthProvider) : CognitoAuth {
        const provider : CognitoAuth = new CognitoAuth({
            ClientId: CONFIG.aws.cognito.clientId,
            AppWebDomain: CONFIG.aws.cognito.appWebDomain,
            TokenScopesArray: [ 'email', 'openid', 'aws.cognito.signin.user.admin' ],
            RedirectUriSignIn: CONFIG.aws.cognito.signedInRedirectUrl.replace(/{host}/g, window.location.host),
            RedirectUriSignOut: CONFIG.aws.cognito.signedOutRedirectUrl.replace(/{host}/g, window.location.host)
        });

        provider.IdentityProvider = providerName;

        provider.useCodeGrantFlow();

        return provider;
    }

    public createSocialAuthRequest (providerName? : SocialAuthProvider) : [ Promise<any>, CognitoAuth ] {
        const provider : CognitoAuth = this.createSocialAuthProvider(providerName);

        const response : Promise<any> = new Promise((resolve) => {
            const callback = (err? : any) => {
                if (err) {
                    console.warn('Social auth error:', err);

                    resolve({
                        action: 'ERROR',
                        error: 'auth.errors.UnknownError'
                    });

                    return;
                }

                const user = this.userPool.getCurrentUser();

                if (!user) {
                    console.warn('Can`t get current user');

                    resolve({
                        action: 'ERROR',
                        error: 'auth.errors.UnknownError'
                    });

                    return;
                }

                user.getSession((err, session) => {
                    if (err || !session.isValid()) {
                        console.warn(`Can't restore session or session isn't valid:`, err);

                        resolve({
                            action: 'ERROR',
                            error: 'auth.errors.UnknownError'
                        });
                    } else {
                        this.textlakeSignIn({ user, session })
                            .then(result => resolve(result));
                    }
                });
            };

            provider.userhandler = {
                onSuccess: () => callback(),
                onFailure: (err) => callback(err)
            };
        });

        return [ response, provider ];
    }

    // Restore existing session or create new through redirect to Google/Facebook
    public executeSocialAuth (providerName : SocialAuthProvider) : Promise<any> {
        const [ response, provider ] = this.createSocialAuthRequest(providerName);
        provider.getSession();
        return response;
    }

    public exchangeCodeForToken () : Promise<any> {
        const [ response, provider ] = this.createSocialAuthRequest();
        provider.parseCognitoWebResponse(window.location.href);
        return response;
    }

    // вызывается только в APP_INITIALIZER'e
    public restoreUser () : Promise<void> {
        return new Promise((resolve) => {
            const user : CognitoUser = this.userPool.getCurrentUser();

            if (!user) {
                this.setupUser(null).then(() => resolve());
                return;
            }

            user.getSession((err, session) => {
                if (!err && session.isValid()) {
                    console.log('session', user, session);
                    this.textlakeSignIn({ user, session })
                        .then(() => resolve());

                    return;
                }

                this.setupUser(null).then(() => resolve());
            });
        });
    }

    public updateFeatures () : Promise<any> {
        return new Promise(resolve => {
            this.fetchFeatures()
                .then(features => {
                    this.userData.features = features;
                    this.onUserDataUpdated.next(this.userData);
                    resolve();
                });
        });

    }

    public fetchFeatures () : Promise<any> {
        return new Promise(resolve => {
            this.http.put2('endpoint://feature.features', {
                body: {
                    features: USER_FEATURES
                }
            })
                .then(response => resolve(new UserFeatures(response.features)))
                .catch(() => resolve(new UserFeatures([])))
        });
    }

    public setupUser (authAttrs : {
        user : CognitoUser,
        session : CognitoUserSession,
        postAuthAction : PostAuthAction
    }) : Promise<void> {
        return new Promise((resolve) => {
            const userData = new UserData();

            const local = window.localStorage.getItem('localUserData');

            userData.local = merge({}, new UserLocalData(), local ? JSON.parse(local) : {});

            // ------------------

            if (authAttrs && authAttrs.session.isValid()) {
                this.user = authAttrs.user;
                this.userSession = authAttrs.session;
                this.postAuthAction = authAttrs.postAuthAction;

                this.setTokenUpdateTimer();

                let saveUserData : boolean = false;
                let updateEmail : boolean = false;

                Promise.all([
                    this.http.get2('endpoint://profile.userProfile'),
                    this.fetchFromStorage2('user_settings_v2'),  // userSettings in v1.0
                    this.fetchFeatures()
                ]).then(([ profile, settings, features ] : [ UserProfile, UserSettings, UserFeatures ]) => {
                    // profile
                    // ----------------------
                    userData.profile = profile;

                    // TODO: DELETE!!!!!!
                    // userData.profile.primaryEmailVerified = false;
                    //----------------------

                    userData.profile.language = userData.profile.language.toLowerCase();

                    // settings
                    // ----------------------
                    const defaultSettings = new UserSettings();
                    saveUserData = saveUserData || !isSameObjectsLayout(defaultSettings, settings);
                    userData.settings = updateObject(defaultSettings, settings || {});

                    // features
                    // ----------------------
                    userData.features = features;

                    // Update remote language if needed
                    if (userData.local.updateRemoteLangAfterSignIn) {
                        userData.profile.language = userData.local.language;
                        userData.local.updateRemoteLangAfterSignIn = false;
                        saveUserData = true;
                    }

                    if (userData.profile.user.email) {
                        return Promise.resolve(null);
                    } else {
                        updateEmail = true;
                        return this.getUserAttributes();
                    }
                }).then((userAttrs : any) => {
                    if (userAttrs) {
                        if (updateEmail && userAttrs.email) {
                            userData.profile.user.email = userAttrs.email;
                            saveUserData = true;
                        }
                    }

                    this.updateUserData({
                        data: userData,
                        save: saveUserData,
                        notify: false
                    }).then(() => {
                        this.connectMqtt();
                        resolve();
                    });
                });
            } else {
                this.disconnectMqtt();
                this.resetTokenUpdateTimer();

                try {
                    if (this.user) {
                        this.user.signOut();
                    }
                } catch (e) {
                    console.warn('signOut error:', e);
                }

                this.user = null;
                this.userSession = null;
                this.postAuthAction = null;

                this.updateUserData({
                    data: userData,
                    save: false,
                    notify: false
                }).then(() => resolve());
            }
        });
    }

    public getUserAttributes () : Promise<any> {
        return new Promise((resolve) => {
            this.user.getUserAttributes((err : any, attrs : CognitoUserAttribute[]) => {
                if (err) {
                    console.warn(`Can't get user attributes:`, err);
                    resolve(null);
                    return;
                }

                resolve(
                    attrs.reduce((acc, attr) => {
                        acc[ attr.getName() ] = attr.getValue();
                        return acc;
                    }, {})
                );
            });
        });
    }

    public fetchMqttOptions () : Promise<any> {
        return new Promise((resolve) => {
            const apiClient = AWSClient.newClient({
                invokeUrl: CONFIG.aws.apiGateway.server
            });

            apiClient.invokeApi(
                {},
                CONFIG.aws.apiGateway.endpoints.sts,
                'POST',
                {
                    headers: {
                        'Authorization': this.idToken
                    }
                },
                {}
            )
                .then(response => resolve(response.data))
                .catch(reason => {
                    console.warn(`Can't get MQTT options from API Gateway:`, reason);
                    resolve(null);
                });
        });
    }

    public disconnectMqtt () : void {
        if (this.mqttExpireTimeout !== null) {
            clearTimeout(this.mqttExpireTimeout);
            this.mqttExpireTimeout = null;
        }

        if (this.mqttClient) {
            this.mqttClient.end();
            this.mqttClient = null;
        }

        this.mqttConnectionId = null;
    }

    public connectMqtt () : Promise<void> {
        return new Promise((resolve) => {
            if (this.mqttConnectionId) {
                this.disconnectMqtt();
            }

            if (!this.isSignedIn) {
                resolve();
                return;
            }

            const connectionId = this.mqttConnectionId = uniqueId('connection_');

            console.warn('[MQTT] Setup connection with ID:', connectionId);

            this.fetchMqttOptions().then(options => {
                if (!options || !this.isSignedIn || this.mqttConnectionId !== connectionId) {
                    resolve();
                    return;
                }

                const expireIn = options.expireIn;
                const updateTimeout = Math.max(0, expireIn - getTimestamp());
                const topics : { [ key : string ] : string } = {
                    user: CONFIG.aws.iot.topics.user.replace(/{userId}/g, String(this.userData.profile.user.id)),
                    company: CONFIG.aws.iot.topics.company.replace(/{companyId}/g, String(this.userData.profile.companyId)),
                    identity: CONFIG.aws.iot.topics.identity.replace(/{identityId}/g, this.user.getUsername())
                };

                this.mqttClient = AWSIoT.device({
                    region: CONFIG.aws.cognito.region,
                    host: options.iotEndpoint,
                    clientId: uniqueId('client_'),
                    protocol: 'wss',
                    maximumReconnectTimeMs: 8000,
                    debug: CONFIG.aws.iot.debug,
                    accessKeyId: options.accessKey,
                    secretKey: options.secretKey,
                    sessionToken: options.sessionToken
                });

                // Setup listeners
                // -------------------------

                this.mqttClient.on('connect', () => {
                    console.warn(
                        '[MQTT]',
                        '\nConnection established.',
                        '\nConnection ID:', connectionId,
                        '\nExpire in:', Math.floor(updateTimeout / 1000 / 60), 'minutes',
                        '\nUpdate date:', new Date(expireIn),
                        '\nTopics:'
                    );

                    console.table && console.table(topics);

                    if (this.mqttConnectionId === connectionId) {
                        forOwn(topics, (topic : string) => {
                            this.mqttClient.subscribe(topic);
                        });
                    }
                });

                this.mqttClient.on('reconnect', () => console.warn('MQTT reconnecting...'));

                this.mqttClient.on('close', (error) => {
                    error ? console.warn('[MQTT] disconnected with error:', error) : console.warn('MQTT disconnected');
                });

                this.mqttClient.on('error', (error) => console.warn('MQTT error:', error));

                this.mqttClient.on('message', (topic : string, payload : string) => {
                    const message : any = JSON.parse(payload);

                    console.warn('[MQTT] raw message:', topic, message);

                    this.onMqttMessage.next({
                        message,
                        topic: findKey(topics, t => t === topic)
                    });
                });

                // Setup update timeout
                // ------------------------

                this.mqttExpireTimeout = setTimeout(() => this.connectMqtt(), updateTimeout);

                // -------------------------

                resolve();
            });
        });
    }

    // Если в каком-то компоненте нужно обновить данные пользователя, то нужно их обновить,
    // а затем прислать в эту функцию. Она сохранит все изменения и разошлёт обновлённые данные
    // по всем компонентам, которые подписаны на изменения onUserDataUpdated
    public updateUserData (options : {
        data : UserData,
        save? : boolean,
        notify? : boolean
    }) : Promise<void> {
        return new Promise((resolve) => {
            const userData = options.data;
            const promises : Promise<any>[] = [];

            if (userData.profile) {
                userData.local.language = userData.profile.language;
            }

            promises.push(this.langService.use(userData.local.language).toPromise());

            if (options.save !== false) {
                promises.push(this.saveUserData(userData));
            }

            Promise.all(promises).then(() => {
                this.userData = userData;

                console.warn(userData);

                if (options.notify !== false) {
                    this.onUserDataUpdated.next(userData);
                }

                resolve();
            });
        });
    }

    public saveUserData (userData : UserData) : Promise<boolean> {
        return new Promise((resolve) => {
            const { local, settings, profile } = userData;
            const promises : Promise<any>[] = [];

            // save local
            if (local) {
                window.localStorage.setItem('localUserData', JSON.stringify(local));
            }

            // save remote
            if (settings) {
                promises.push(this.saveToStorage('user_settings_v2', settings));
            }

            // save profile/me
            if (profile) {
                promises.push(
                    this.http.put2('endpoint://profile.userProfile', {
                        body: {
                            language: profile.language.toUpperCase(),
                            email: profile.user.email
                        }
                    })
                );
            }

            if (!promises.length) {
                resolve(true);
                return;
            }

            Promise
                .all(promises)
                .then(() => resolve(true))
                .catch(() => resolve(false));
        });
    }

    public getUserData () : UserData {
        return this.userData;
    }

    public signOut () : Promise<void> {
        return this.setupUser(null);
    }

    public get isSignedIn () : boolean {
        // NOTE: if session is invalid, it means accessToken & idToken are expired
        return !!(this.userSession && this.userSession.isValid());
    }

    public get tokenExpiration () : number {
        return this.isSignedIn ? this.userSession.getAccessToken().getExpiration() * 1000 : null;
    }

    public get accessToken () : string {
        return this.isSignedIn ? this.userSession.getAccessToken().getJwtToken() : null;
    }

    public get idToken () : string {
        return this.isSignedIn ? this.userSession.getIdToken().getJwtToken() : null;
    }

    public get refreshToken () : CognitoRefreshToken {
        return this.userSession ? this.userSession.getRefreshToken() : null;
    }

    private resetTokenUpdateTimer () : void {
        if (this.tokenExpireTimeout !== null) {
            clearTimeout(this.tokenExpireTimeout);
            this.tokenExpireTimeout = null;
        }
    }

    private setTokenUpdateTimer () : void {
        this.resetTokenUpdateTimer();

        if (!this.userSession) {
            throw new Error(`Unexpected: setTokenUpdateTimer is called, but session isn't set!`);
        }

        // If session is already invalid (expired), update token right now
        if (!this.userSession.isValid()) {
            this.updateToken();
            return;
        }

        const expireIn = this.tokenExpiration - 60 * 1000;  // -1 min
        const updateTimeout = Math.max(0, expireIn - getTimestamp());

        console.warn(
            'Session token expiration:',
            '\n\tDate:', new Date(expireIn),
            '\n\tMinutes left:', Math.floor(updateTimeout / 1000 / 60)
        );

        this.tokenExpireTimeout = setTimeout(() => this.updateToken(), updateTimeout);
    }

    private updateToken () : void {
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
    }

    public switchAccount (accountId : number) : Observable<any> {
        return this.http.post('endpoint://profile.switchAccount', {
            urlParams: {
                accountId
            }
        }).pipe(
            retry(1)
        );
    }

    public verifyEmail () : Observable<any> {
        return this.http.post('endpoint://profile.verifyEmail', {
            body: {
                language: 'EN'
            }
        }).pipe(
            retry(1),
            take(1),
            map(() => null),
            catchError(error => {
                console.warn('verifyEmail error:', error);
                return throwError(error);
            })
        );
    }

    public sendVerificationCode () : Observable<any> {
        return this.http.post('endpoint://profile.sendVerificationCode').pipe(
            retry(1),
            take(1),
            map(response => response === 'SUCCESS'),
            catchError(error => {
                console.warn('sendVerificationCode error:', error);
                return throwError(error);
            })
        );
    }

    public checkVerificationCode (code : string) : Observable<any> {
        return this.http.post('endpoint://profile.checkVerificationCode', {
            body: { code }
        }).pipe(
            retry(1),
            take(1),
            map(response => response === 'SUCCESS'),
            catchError(error => {
                console.warn('checkVerificationCode error:', error);
                return throwError(error);
            })
        );
    }

    // Roles
    // --------------------------

    public fetchUsers () : Observable<User[]> {
        return this.http.get('endpoint://users.getAllUsers').pipe(
            retry(1),
            take(1),
            map(response => response.users),
            catchError(error => {
                console.warn('fetchUsers error:', error);
                return throwError(error);
            })
        );
    }

    public updateUser (user : User) : Observable<User> {
        return this.http.put('endpoint://users.updateUser', {
            urlParams: {
                userId: user.id,
            },
            body: {
                active: user.active
            }
        }).pipe(
            retry(1),
            take(1),
            map(response => response.user),
            catchError(error => {
                console.warn('updateUser error:', error);
                return throwError(error.error || null);
            })
        );
    }

    public fetchRoles () : Observable<UserRole[]> {
        return this.http.get('endpoint://users.getAllRoles').pipe(
            retry(1),
            take(1),
            map(response => response.roles),
            catchError(error => {
                console.warn('fetchRoles error:', error);
                return throwError(error);
            })
        );
    }

    public fetchUserRoles (userId : number) : Observable<UserRole[]> {
        return this.http.get('endpoint://users.getUserRoles', {
            urlParams: { userId }
        }).pipe(
            retry(1),
            take(1),
            map(response => response.roles),
            catchError(error => {
                console.warn('fetchUserRoles error:', error);
                return throwError(error);
            })
        );
    }

    public setUserRole (userId : number, roleKey : string) : Observable<void> {
        return this.http.put('endpoint://users.setUserRole', {
            urlParams: {
                userId,
                roleKey
            }
        }).pipe(
            retry(1),
            take(1),
            catchError(error => {
                console.warn('setUserRole error:', error);
                return throwError(error);
            })
        );
    }

    public deleteUserRole (userId : number, roleKey : string) : Observable<void> {
        return this.http.delete('endpoint://users.deleteUserRole', {
            urlParams: {
                userId,
                roleKey
            }
        }).pipe(
            retry(1),
            take(1),
            catchError(error => {
                console.warn('deleteUserRole error:', error);
                return throwError(error);
            })
        );
    }


    // Remote Storage
    // --------------------------

    public fetchFromStorage (key : string) : Observable<any> {
        return this.http.get('endpoint://userStorage', { urlParams: { key } }).pipe(
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

    public fetchFromStorage2 (key : string) : Promise<any> {
        return this.http.get2('endpoint://userStorage', { urlParams: { key } })
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
                        this.http.post2('endpoint://userStorage', requestOptions) :
                        this.http.put2('endpoint://userStorage', requestOptions)
                    )
                    .then(() => resolve(true))
                    .catch(() => resolve(false));
                });
        });
    }

    public deleteFromStorage (key : string) : Promise<any> {
        return this.http.delete2('endpoint://userStorage', { urlParams: { key } })
            .then(() => true)
            .catch(() => false);
    }

    // Testings
    // -------------------------

    public createNotification () : Promise<boolean> {
        console.warn('WARN: test function called');

        if (CONFIG.isProduction) {
            return Promise.reject(false);
        }

        return this.http.get2('endpoint://test.createNotification')
            .then(() => true)
            .then(() => false);
    }

    public createTask () : Promise<boolean> {
        console.warn('WARN: test function called');

        if (CONFIG.isProduction) {
            return Promise.reject(false);
        }

        return this.http.get2('endpoint://test.createTask')
            .then(() => true)
            .then(() => false);
    }

    /*
    public testRemoteStorage () : void {
        console.warn('WARN: test function called');

        if (CONFIG.isProduction) {
            return;
        }

        const storageKey = 'test_storage_item';

        this.fetchFromStorage2(storageKey)
            .then(data => {
                console.warn('Fetch (must be empty):', data);
                return this.saveToStorage(storageKey, { value: 'Saturn' });
            })
            .then(isOk => {
                console.warn('Save (create item):', isOk);
                return this.fetchFromStorage2(storageKey)
            })
            .then(data => {
                console.warn('Fetch (must be { value: Saturn }):', data);
                return this.saveToStorage(storageKey, { value: 'Earth' });
            })
            .then(isOk => {
                console.warn('Save (update item):', isOk);
                return this.fetchFromStorage2(storageKey)
            })
            .then(data => {
                console.warn('Fetch (must be { value: Earth }):', data);
                return this.deleteFromStorage(storageKey);
            })
            .then(isOk => {
                console.warn('Delete:', isOk);
                return this.fetchFromStorage2(storageKey)
            })
            .then(data => {
                console.warn('Fetch (must be empty):', data);
            });
    }
    */
}
