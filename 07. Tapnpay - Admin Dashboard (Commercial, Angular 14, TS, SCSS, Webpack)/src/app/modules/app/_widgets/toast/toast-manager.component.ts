import {Component, OnDestroy, OnInit, ViewEncapsulation} from '@angular/core';
import {Toast, ToastNavState, ToastService} from '../../../../services/toast.service';
import {Subscription} from 'rxjs';
import {deleteFromArray} from '../../../../lib/utils';


@Component({
    selector: 'toast-manager',
    templateUrl: './toast-manager.component.html',
    styleUrls: [ './toast-manager.component.scss' ],
    encapsulation: ViewEncapsulation.None,
    host: {
        class: 'toast-manager',
        '[class.toast-manager_nav_absent]': `navState === 'nav_absent'`,
        '[class.toast-manager_nav_collapsed]': `navState === 'nav_collapsed'`,
        '[class.toast-manager_nav_expanded]': `navState === 'nav_expanded'`,
    }
})
export class ToastManagerComponent implements OnInit, OnDestroy {
    public subs : Subscription[] = [];

    public toasts : any[] = [];

    public navState : ToastNavState;

    public constructor (
        private toastService : ToastService
    ) {

    }

    public ngOnInit () : void {
        this.addSub(this.toastService.actionEmitter.asObservable().subscribe((toast : Toast) => {
            this.toasts = [ toast, ...this.toasts ];
        }));

        this.addSub(this.toastService.onNavToggle.asObservable().subscribe((navState : ToastNavState) => {
            this.navState = navState;
        }));
    }

    public ngOnDestroy () : void {
        this.subs.forEach(sub => sub.unsubscribe());
        this.toasts = [];
    }

    public addSub (sub : Subscription) : void {
        this.subs = [ ...this.subs, sub ];
    }

    public onHideToast (toast : Toast) : void {
        this.toasts = [ ...deleteFromArray(this.toasts, toast) ];
    }
}
