import { Injectable } from '@angular/core';
import {ActivatedRoute, Router} from '@angular/router';

@Injectable({
    providedIn: 'root'
})
export class RouterService {
    constructor (
        private router : Router,
        private route : ActivatedRoute,
    ) {}

    public setQueryZ (value : string) : Promise<any> {
        return this.setQueryParam('z', value);
    }

    public unsetQueryZ () : Promise<any> {
        return this.setQueryParam('z', null);
    }

    public setQueryParam (key : string, value : any) : Promise<any> {
        return this.router.navigate([], {
            relativeTo: this.route,
            queryParams: { [ key ]: value },
            queryParamsHandling: 'merge',
        });
    }
}
