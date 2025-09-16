import { Injectable } from '@angular/core';
import { HttpRequest, HttpHandler, HttpEvent, HttpInterceptor } from '@angular/common/http';
import { Observable } from 'rxjs';
import { UserService } from '../services/user.service';
import { RequestFlags } from '../enums/request-flags.enum';
import {HttpService2} from '../services/http2.service';


@Injectable()
export class RequestInterceptor implements HttpInterceptor {
    constructor (
        public userService : UserService
    ) {}

    public intercept (request : HttpRequest<any>, next : HttpHandler): Observable<HttpEvent<any>> {
        const
            requestFlags : number = Number(request.headers.get(HttpService2.REQUEST_FLAGS_HEADER) || 0),  // TODO: delete header from request
            headers : any = {};

        if (requestFlags & RequestFlags.Auth) {
            headers[HttpService2.ACCESS_TOKEN_HEADER] = 'accessToken';
        }

        request = request.clone({
            setHeaders: headers
        });

        return next.handle(request);
    }
}
