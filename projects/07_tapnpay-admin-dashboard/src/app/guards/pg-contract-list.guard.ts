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
export class PGContractListGuard implements CanActivate, CanActivateChild {
    constructor (
        private router : Router,
        private userService : UserService
    ) {}

    public canActivate (route : ActivatedRouteSnapshot, state : RouterStateSnapshot) : boolean | UrlTree {
        return this.hasAccess();
    }

    public canActivateChild (childRoute : ActivatedRouteSnapshot, state : RouterStateSnapshot) : boolean | UrlTree {
        return this.hasAccess();
    }

    hasAccess () : boolean {
        return this.userService.checkPermission('CONTRACT_PAYMENT_GATEWAY_VIEW');
    }
}
