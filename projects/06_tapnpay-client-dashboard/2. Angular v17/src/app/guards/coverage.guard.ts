import {UserService} from '../services/user.service';
import { ActivatedRouteSnapshot, Router, RouterStateSnapshot, UrlTree } from '@angular/router';
import {Injectable} from '@angular/core';

@Injectable({
    providedIn: 'root'
})
export class CoverageGuard  {
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
        return true;  // this.userService.getUserData().account.paymentModel !== 'FLEET';
    }
}
