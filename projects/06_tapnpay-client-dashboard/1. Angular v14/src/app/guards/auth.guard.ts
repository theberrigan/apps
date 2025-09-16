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

@Injectable({
    providedIn: 'root'
})
export class AuthGuard implements CanActivate, CanActivateChild {
    constructor (
        private router : Router,
        private userService : UserService
    ) {}

    // {phone: "PT-AG-12684", pin: "7695"}
    public canActivate (route : ActivatedRouteSnapshot, state : RouterStateSnapshot) : boolean | UrlTree {
        return this.hasAccess();
    }

    public canActivateChild (childRoute : ActivatedRouteSnapshot, state : RouterStateSnapshot) : boolean | UrlTree {
        return this.hasAccess();
    }

    hasAccess () : boolean {
        if (this.userService.isLoggedIn()) {
            return true;
        } else {
            this.router.navigateByUrl('/auth');
            return false;
        }
    }
}
