import {Injectable} from '@angular/core';
import {HttpErrorResponse, HttpEvent, HttpHandler, HttpInterceptor, HttpRequest} from '@angular/common/http';
import {UserService} from '../services/user.service';
import {API_TOKEN_HEADER_KEY, InterceptorHttpParams, InterceptorOptions} from '../services/http.service';
import {Observable, throwError} from 'rxjs';
import {switchMap} from 'rxjs/operators';

@Injectable()
export class ApiRequestInterceptor implements HttpInterceptor {
    constructor (
        private userService : UserService
    ) {}

    public intercept (req : HttpRequest<any>, next : HttpHandler) : Observable<HttpEvent<any>> {
        const interceptorOptions = (<InterceptorHttpParams>req.params).interceptorOptions || new InterceptorOptions();

        return (
            interceptorOptions.useAccessToken ?
            this.userService.waitForAccessToken().pipe(switchMap(accessToken => {
                if (accessToken) {
                    req = req.clone({
                        headers: req.headers.set(API_TOKEN_HEADER_KEY, accessToken)
                    });

                    return next.handle(req);
                }

                return throwError(new HttpErrorResponse({
                    error: new Error('User is not authorized.'),
                }));
            })) :
            next.handle(req)
        );
    }
}
