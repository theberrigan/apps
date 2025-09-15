import { Injectable } from '@angular/core';
import { Subject } from 'rxjs';


@Injectable({
    providedIn: 'root'
})
export class NetworkService {
    _isOnline : boolean;

    onNetworkStatusChange = new Subject<boolean>();

    constructor () {
        this._isOnline = navigator.onLine;
        this.onNetworkStatusChange.next(this._isOnline);

        window.addEventListener('online', () => this.onStatusChange(true));
        window.addEventListener('offline', () => this.onStatusChange(false));
    }

    private onStatusChange (isOnline) {
        this._isOnline = isOnline;
        this.onNetworkStatusChange.next(this._isOnline);
    }

    isOnline () : boolean {
        return this._isOnline;
    }
}
