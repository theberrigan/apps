import { bindMethods } from './utils';

export class Subscriber {
    private readonly _listeners : any = {};

    constructor () {
        bindMethods(this);
    }

    public on (eventName : string, listener : Function) : Subscriber {
        (this._listeners[eventName] || (this._listeners[eventName] = [])).push(listener);
        return this;
    }

    public emit (eventName : string, event? : any) : Subscriber {
        (this._listeners[eventName] || []).forEach(listener => listener(event));
        return this;
    }
}