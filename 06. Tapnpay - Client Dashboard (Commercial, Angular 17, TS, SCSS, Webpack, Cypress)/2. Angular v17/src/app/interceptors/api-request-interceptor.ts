import {Injectable} from '@angular/core';
import { HttpErrorResponse, HttpEvent, HttpHandler, HttpInterceptor, HttpRequest } from '@angular/common/http';
import {UserService} from '../services/user.service';
import {API_TOKEN_HEADER_KEY, InterceptorHttpParams, InterceptorOptions} from '../services/http.service';
import {Observable, throwError} from 'rxjs';
import {catchError} from 'rxjs/operators';
import {Router} from '@angular/router';
import {CONFIG} from '../../../config/app/dev';
import {LangService} from '../services/lang.service';

@Injectable()
export class ApiRequestInterceptor implements HttpInterceptor {
    constructor(
        private router: Router,
        private userService: UserService,
        private langService: LangService,
    ) {
    }

    public intercept(req: HttpRequest<any>, next: HttpHandler): Observable<HttpEvent<any>> {
        const interceptorOptions = (<InterceptorHttpParams>req.params).interceptorOptions || new InterceptorOptions();
        let headers = req.headers;
        let checkAuthError = false;

        if (CONFIG.env && !req.url.includes('neoride')) {
            headers = headers.set('X-TNP-ENV', CONFIG.env);
        }

        const langCode = this.langService.getCurrentLangCode();

        if (langCode && !req.url.includes('neoride')) {
            headers = headers.set('X-TNP-APP-LANG', langCode);
        }

        if (interceptorOptions.useAccessToken) {
            const accessToken = this.userService.getAuthToken();

            if (accessToken) {
                checkAuthError = true;
                headers = headers.set(API_TOKEN_HEADER_KEY, accessToken);
            }
        }

        req = req.clone({headers});

        if (checkAuthError) {
            return next.handle(req).pipe(
                catchError((error: HttpErrorResponse) => {
                    if (error.error.status_code === 101 && this.userService.getAuthToken()) {
                        this.userService.validateAuthData({ token: this.userService.getAuthToken() }).then(authData => {
                            if (!authData.token) {
                                this.userService.logout();
                                this.router.navigateByUrl('/auth');
                            }
                        });
                    }
                    return throwError(error);
                })
            );
        }

        return next.handle(req);
    }
}
