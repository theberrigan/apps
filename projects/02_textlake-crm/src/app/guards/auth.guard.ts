import {UserService} from '../services/user.service';
import {
    ActivatedRouteSnapshot,
    CanActivate,
    CanActivateChild,
    Router,
    RouterStateSnapshot,
    UrlTree
} from '@angular/router';
import {Injectable} from '@angular/core';
import {startsWith} from 'lodash';

@Injectable({
    providedIn: 'root'
})
export class AuthGuard implements CanActivate, CanActivateChild {
    constructor (
        private router : Router,
        private userService : UserService
    ) {}

    private checkUrl (url : string) : boolean | UrlTree {
        const isAuth = startsWith(url, '/auth');
        const isSignedIn = this.userService.isSignedIn;

        if (isAuth && isSignedIn) {
            return this.router.createUrlTree([ '/dashboard' ]);
        } else if (!isAuth && !isSignedIn) {
            return this.router.createUrlTree([ '/auth' ]);
        }

        return true;
    }

    public canActivate (route : ActivatedRouteSnapshot, state : RouterStateSnapshot) : boolean | UrlTree {
        return this.checkUrl(state.url);
    }

    public canActivateChild (childRoute : ActivatedRouteSnapshot, state : RouterStateSnapshot) : boolean | UrlTree {
        return this.checkUrl(state.url);
    }
}
