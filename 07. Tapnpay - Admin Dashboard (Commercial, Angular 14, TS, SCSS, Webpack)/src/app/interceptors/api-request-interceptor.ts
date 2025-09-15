import {Injectable} from '@angular/core';
import {HttpErrorResponse, HttpEvent, HttpHandler, HttpInterceptor, HttpRequest} from '@angular/common/http';
import {UserService} from '../services/user.service';
import {
    API_REQUEST_HEADER_PREFIX,
    API_TOKEN_HEADER_KEY, AuthType,
    InterceptorHttpParams,
    InterceptorOptions
} from '../services/http.service';
import {Observable, throwError} from 'rxjs';
import {catchError, switchMap} from 'rxjs/operators';
import {Router} from '@angular/router';
import {CONFIG} from '../../../config/app/dev';
import {LangService} from '../services/lang.service';

@Injectable()
export class ApiRequestInterceptor implements HttpInterceptor {
    constructor (
        private router : Router,
        private userService : UserService,
        private langService : LangService,
    ) {}

    public intercept (req : HttpRequest<any>, next : HttpHandler) : Observable<HttpEvent<any>> {
        const interceptorOptions = (<InterceptorHttpParams>req.params).interceptorOptions || new InterceptorOptions();
        let headers = req.headers;
        let checkAuthError = false;

        if (interceptorOptions.authType !== AuthType.External) {
            if (CONFIG.env) {
                headers = headers.set(`${ API_REQUEST_HEADER_PREFIX }-ENV`, CONFIG.env);
            }

            if (APP_VERSION) {
                headers = headers.set(`${ API_REQUEST_HEADER_PREFIX }-APP-VERSION`, APP_VERSION);
            }

            const langCode = this.langService.getCurrentLangCode();

            if (langCode) {
                headers = headers.set(`${ API_REQUEST_HEADER_PREFIX }-APP-LANG`, langCode);
            }

            if (interceptorOptions.useAccessToken) {
                const accessToken = this.userService.getAuthToken();

                if (accessToken) {
                    checkAuthError = true;
                    headers = headers.set(API_TOKEN_HEADER_KEY, accessToken);
                }
            }

            req = req.clone({ headers });

            if (checkAuthError) {
                return next.handle(req).pipe(
                    catchError((error : HttpErrorResponse) => {
                        if (error.error.status_code === 101) {
                            this.userService.logout();
                            this.router.navigateByUrl('/auth');
                        }

                        return throwError(error);
                    })
                );
            }
        }

        return next.handle(req);
    }
}
