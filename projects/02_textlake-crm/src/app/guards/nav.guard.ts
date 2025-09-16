import { ActivatedRouteSnapshot, CanActivate, Router, RouterStateSnapshot, UrlTree } from '@angular/router';
import { Injectable } from '@angular/core';
import { UserService } from '../services/user.service';
import {startsWith} from 'lodash';


const ROUTE_FEATURES = [
    { url: 'offers',      feature: 'menu:offers'      },
    { url: 'projects',    feature: 'menu:projects'    },
    { url: 'mailbox',     feature: 'menu:mailbox'     },
    { url: 'clients',     feature: 'menu:clients'     },
    { url: 'translators', feature: 'menu:translators' },
    { url: 'reports',     feature: 'menu:billings'    },
    { url: 'settings',    feature: 'menu:settings'    },
];


@Injectable({
    providedIn: 'root'
})
export class NavGuard implements CanActivate {
    constructor (
        private router : Router,
        private userService : UserService
    ) {}

    public canActivate (route : ActivatedRouteSnapshot, state : RouterStateSnapshot) : boolean | UrlTree {
        const userData = this.userService.getUserData();

        if (!userData || !userData.features) {
            return false;
        }

        //const [ path ] = state.url.split(/[?#]/);
        //console.warn('NAV GUARD:', path, route.routeConfig.path);
        const item = ROUTE_FEATURES.find(item => item.url === route.routeConfig.path);

        if (!item) {
            return false;
        }

        return userData.features.can(item.feature);
    }
}
