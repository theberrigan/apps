import { Injectable } from '@angular/core';
import {ReplaySubject} from 'rxjs';

@Injectable({
    providedIn: 'root'
})
export class DomService {
    constructor () {}

    public markEvent (e : any, propKey : string, propValue : any = true) : any {
        Object.defineProperty(e, `__${ propKey }`, { value: propValue, configurable: true });
        return e;
    }

    public hasEventMark (e : any, propKey : string, propValue : any = true) : boolean {
        return e[`__${ propKey }`] === propValue;
    }

    public getEventMark (e : any, propKey : string) : any {
        return e[`__${ propKey }`];
    }
}
