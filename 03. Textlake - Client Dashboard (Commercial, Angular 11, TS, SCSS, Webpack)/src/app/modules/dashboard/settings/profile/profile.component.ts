import {AfterViewInit, Component, EventEmitter, NgZone, OnDestroy, OnInit, Output, ViewChild, ViewEncapsulation} from '@angular/core';
import {ActivatedRoute, Router} from '@angular/router';
import {RouterService} from '../../../../services/router.service';
import {PopupService} from '../../../../services/popup.service';
import {PopupComponent} from '../../../../widgets/popup/popup.component';
import {UserData, UserService} from '../../../../services/user.service';
import {from, Subscription, zip} from 'rxjs';
import {FormBuilder, FormGroup} from '@angular/forms';
import {first} from 'rxjs/operators';
import {ToastService} from '../../../../services/toast.service';
import {DeviceService, ViewportBreakpoint} from '../../../../services/device.service';

type State = 'loading' | 'ready' | 'error';

@Component({
    selector: 'profile',
    templateUrl: './profile.component.html',
    styleUrls: [ './profile.component.scss' ],
    encapsulation: ViewEncapsulation.None,
    host: {
        'class': 'profile',
    }
})
export class ProfileComponent implements AfterViewInit, OnDestroy {
    public subs : Subscription[] = [];

    public viewportBreakpoint : ViewportBreakpoint;

    public isActive : boolean = false;

    public isSaving : boolean = false;

    public state : State;

    @ViewChild('popup')
    public popup : PopupComponent;

    public reqSub : Subscription;

    public form : FormGroup;

    constructor (
        private router : Router,
        private route : ActivatedRoute,
        private routerService : RouterService,
        private formBuilder : FormBuilder,
        private popupService : PopupService,
        private deviceService : DeviceService,
        private userService : UserService,
        private zone : NgZone,
        private toastService : ToastService,
    ) {
    }

    public ngAfterViewInit () : void {
        this.zone.onStable.pipe(first()).subscribe(() => {
            this.route.queryParams.subscribe((queryParams) => {
                this.isActive = queryParams.z === 'profile';

                if (this.isActive) {
                    this.showPopup();
                } else {
                    this.hidePopup();
                }
            });
        });
    }

    public ngOnDestroy () : void {
        this.subs.forEach(sub => sub.unsubscribe());
    }

    public addSub (sub : Subscription) : void {
        this.subs = [ ...this.subs, sub ];
    }

    public showPopup () : void {
        if (this.state === 'loading') {
            return;
        }

        this.state = 'loading';
        this.popup.showSpinner();
        this.popup.activate();

        this.viewportBreakpoint = this.deviceService.viewportBreakpoint;
        this.addSub(this.deviceService.onResize.subscribe((message) => {
            if (message.breakpointChange) {
                this.viewportBreakpoint = message.breakpointChange.current;
            }
        }));

        setTimeout(() => {
            this.popup.showBox();
            this.state = 'ready';
        }, 1000);
    }

    public hidePopup () : void {
        if (this.reqSub) {
            this.reqSub.unsubscribe();
        }

        this.popup.deactivate().then(() => {
            this.form = null;
        });
    }

    public onSave () : void {
        if (this.isSaving) {
            return;
        }

        this.isSaving = true;
        this.form.disable();

        setTimeout(() => {
            this.form.markAsPristine();
            this.form.enable();
            this.isSaving = false;
        }, 1500);
    }

    public onCloseRequest (byOverlay? : boolean) : void {
        if (this.isSaving || byOverlay) {
            return;
        }

        if (!this.form || this.form.pristine) {
            this.routerService.unsetQueryZ();
            return;
        }

        this.popupService.confirm({
            message: [ 'settings.profile.confirm_discard__message' ],
        }).subscribe(({ isOk }) => {
            if (isOk) {
                this.routerService.unsetQueryZ();
            }
        });
    }
}
