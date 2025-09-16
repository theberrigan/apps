import {Injectable, NgZone} from '@angular/core';
import {Subject} from 'rxjs';
import {take} from 'rxjs/operators';
import {defer} from '../lib/utils';

export type ToastNavState = 'nav_absent' | 'nav_collapsed' | 'nav_expanded';

export type ToastType = 'error' | 'success' | 'default';

export class Toast {
    message : string | any[];
    type? : ToastType;
    timeout? : number | null;
}

@Injectable({
    providedIn: 'root'
})
export class ToastService {
    public actionEmitter = new Subject<Toast>();
    public onNavToggle = new Subject<ToastNavState>();

    public create (toast : Toast) : void {
        defer(() => this.actionEmitter.next(toast));
    }
}
