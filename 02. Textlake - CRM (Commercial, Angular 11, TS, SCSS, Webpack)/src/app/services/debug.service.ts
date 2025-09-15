import { Injectable } from '@angular/core';

@Injectable({
    providedIn: 'root'
})
export class DebugService {

    constructor () {

    }

    public assert (condition : any, falseMessage : string = '') : void {
        condition = !!condition;

        if (console.assert) {
            console.assert(condition, falseMessage);
        } else if (!condition) {
            console.error ? console.error(falseMessage) : console.error('Assertion error:', falseMessage);
        }
    }
}
