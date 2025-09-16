import {Injectable, TemplateRef} from '@angular/core';
import {PopupComponent} from '../widgets/popup/popup.component';
import {Observable, ReplaySubject, Subject} from 'rxjs';
import {last, without} from 'lodash';
import {DomService} from './dom.service';
import {take} from 'rxjs/operators';

/*

// Confirmation
// -----------------------------------

this.popupService.confirm({
    title? : 'Custom title' | [ 'key.to.translate', { dataToTranslate: '1' }? ],  // default 'Confirm your action'
    message: 'My message' | [ 'key.to.translate', { dataToTranslate: '1' }? ],
    okButtonCaption? : 'Custom ok caption' | [ 'key.to.translate', { dataToTranslate: '1' }? ],  // default 'Ok'
    cancelButtonCaption? : 'Custom cancel caption' | [ 'key.to.translate', { dataToTranslate: '1' }? ],  // default 'Cancel'
    showRemember : boolean // default false
}).subscribe(({ isOk, remember }) => {  // <-- Pay attention: destructuration!
    // if 'showRemember' === true -> 'remember' will be true or false
    console.log(isOk, remember);
});


// Alert
// -----------------------------------

this.popupService.alert({
    title? : 'Custom title' | [ 'key.to.translate', { dataToTranslate: '1' }? ],  // default 'Notification'
    message: 'My message' | [ 'key.to.translate', { dataToTranslate: '1' }? ],
    buttonCaption? : 'Custom ok caption' | [ 'key.to.translate', { dataToTranslate: '1' }? ],  // default 'Ok'
    showRemember : boolean // default false
}).subscribe(({ remember }) => {  // <-- Pay attention: destructuration!
    // if 'showRemember' === true -> 'remember' will be true or false
    console.log(remember);
});


// Custom popup schema
// -----------------------------------

<popup [options]="PopupOptions">
    <popup-box>
        <popup-header>Confirm your action</popup-header>
        <popup-content>Do you want to leave this page and discard unsaved changes?</popup-content>
        <popup-controls>
            <div class="popup__controls-buttons">
                <button type="button" class="button button_blue">Save</button>
                <button type="button" class="button button_red">Cancel</button>
            </div>
        </popup-controls>
    </popup-box>
</popup>

// API
// --------------------------

Методы:
    redraw
    activate
    deactivate

    ! show и hide использовать не нужно

События:
    onActivate - показать существующий попап (добавить в стек попапов)
    onDeactivate - полностью скрыть попап (убрать из стека попапов)

    Используются менеджером попапов:
    onShow - показать ранее скрытый попап
    onHide - временно скрыть попап

*/

export class PopupOptions {
    isActive? : boolean = false;
    closeBy? : 'cross-overlay' | 'cross' | 'overlay' | 'manual' = 'cross-overlay';
    showCross? : boolean = true;
    canBeClosed? : boolean = true;
    stickyHeader? : boolean = false;
    stickyControls? : boolean = false;
}

export type PopupType = 'alert' | 'confirm';

export interface ICreatePopupEvent {
    type : PopupType;
    options : ConfirmOptions | AlertOptions;
}

export class ConfirmOptions {
    showRemember? : boolean;
    title? : string | any[];
    message : string | any[];
    okButtonCaption? : string | any[];
    cancelButtonCaption? : string | any[];
    responseSubject? : Subject<IConfirmResponse>;
}

export interface IConfirmResponse {
    isOk : boolean;
    remember? : boolean;
}

export class AlertOptions {
    showRemember? : boolean;
    title? : string | any[];
    message : string | any[];
    buttonCaption? : string | any[];
    responseSubject? : Subject<IAlertResponse>;
}

export interface IAlertResponse {
    remember : boolean;
}

@Injectable({
    providedIn: 'root'
})
export class PopupService {
    // Only for popup manager
    public onCreatePopup = new ReplaySubject<ICreatePopupEvent>();
    public onPopupTemplate = new ReplaySubject<any>();

    // Queue of active/inactive popups
    public popupStack : PopupComponent[] = [];

    constructor (
        private domService : DomService
    ) {}

    private createPopup (type : PopupType, options : ConfirmOptions | AlertOptions) : Observable<any> {
        const responseSubject = new Subject<any>();

        this.onCreatePopup.next({
            type,
            options: {
                ...options,
                responseSubject
            }
        });

        return responseSubject.asObservable();
    }

    public confirm (options : ConfirmOptions) : Observable<IConfirmResponse> {
        return this.createPopup('confirm', options).pipe(take(1));
    }

    public alert (options : AlertOptions) : Observable<IAlertResponse> {
        return this.createPopup('alert', options).pipe(take(1));
    }

    public activatePopup (popupToActivate : PopupComponent) : Promise<void> {
        const popupToHide : PopupComponent = last(this.popupStack);
        this.popupStack = [ ...this.popupStack, popupToActivate ];

        popupToHide && popupToHide.hide();
        const result = popupToActivate.show();

        this.checkPageScroll();

        return result;
    }

    public deactivatePopup (popupToDeactivate : PopupComponent) : Promise<void> {
        this.popupStack = without(this.popupStack, popupToDeactivate);
        const popupToShow : PopupComponent = last(this.popupStack);

        const result = popupToDeactivate.hide();
        popupToShow && popupToShow.show();

        this.checkPageScroll();

        return result;
    }

    public checkPageScroll () : void {
        this.domService.togglePageScroll(!this.popupStack.length);
    }

    public createPopupFromTemplate (popupTpl : TemplateRef<any>) : Observable<void> {
        const responseSubject = new ReplaySubject<void>();

        this.onPopupTemplate.next({
            isCreate: true,
            popupTpl,
            responseSubject
        });

        return responseSubject.asObservable();
    }

    public removePopupTemplate (popupTpl : TemplateRef<any>) : void {
        this.onPopupTemplate.next({
            isCreate: false,
            popupTpl
        });
    }
}
