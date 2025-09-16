import { Component, EventEmitter, Input, Output, ViewEncapsulation } from '@angular/core';
import { isArray, isUndefined, merge } from 'lodash';
import { Subject } from 'rxjs';
import { ConfirmOptions, IConfirmResponse } from '../../../services/popup.service';

@Component({
    selector: 'confirm',
    templateUrl: './confirm.component.html',
    styleUrls: [ './confirm.component.scss' ],
    encapsulation: ViewEncapsulation.None,
    host: {
        class: 'confirm'
    }
})
export class ConfirmComponent {
    @Output()
    public onClose = new EventEmitter<void>();

    @Input()
    public set options (options : ConfirmOptions) {
        options = merge({}, new ConfirmOptions(), options);

        this.showRemember = !!options.showRemember;
        this.responseSubject = options.responseSubject;

        if (isArray(options.title)) {
            [ this.title, this.titleData ] = options.title;
            this.translateTitle = true;
        } else if (!isUndefined(options.title)) {
            this.title = options.title || '';
            this.translateTitle = false;
            this.titleData = undefined;
        } else {
            this.title = 'popups.confirm.title';
            this.translateTitle = true;
            this.titleData = undefined;
        }

        if (isArray(options.message)) {
            [ this.message, this.messageData ] = options.message;
            this.translateMessage = true;
        } else {
            this.message = options.message;
            this.translateMessage = false;
            this.messageData = undefined;
        }

        if (isArray(options.okButtonCaption)) {
            [ this.okButtonCaption, this.okButtonCaptionData ] = options.okButtonCaption;
            this.translateOkButtonCaption = true;
        } else if (options.okButtonCaption) {
            this.okButtonCaption = options.okButtonCaption;
            this.translateOkButtonCaption = false;
        } else {
            this.okButtonCaption = 'popups.confirm.ok__button';
            this.translateOkButtonCaption = true;
        }

        if (isArray(options.cancelButtonCaption)) {
            [ this.cancelButtonCaption, this.cancelButtonCaptionData ] = options.cancelButtonCaption;
            this.translateCancelButtonCaption = true;
        } else if (options.cancelButtonCaption) {
            this.cancelButtonCaption = options.cancelButtonCaption;
            this.translateCancelButtonCaption = false;
        } else {
            this.cancelButtonCaption = 'popups.confirm.cancel__button';
            this.translateCancelButtonCaption = true;
        }
    }

    public showRemember : boolean;

    public translateTitle : boolean;

    public title : string;

    public titleData : any;

    public translateMessage : boolean;

    public message : string;

    public messageData : any;

    public translateOkButtonCaption : boolean;

    public okButtonCaption : string;

    public okButtonCaptionData : any;

    public translateCancelButtonCaption : boolean;

    public cancelButtonCaption : string;

    public cancelButtonCaptionData : any;

    public responseSubject : Subject<IConfirmResponse>;

    public remember : boolean = false;

    constructor () {}

    public onConfirm (closeByOverlay : boolean, isConfirmed : boolean) : void {
        if (closeByOverlay) {
            return;
        }

        this.responseSubject.next({
            isOk: isConfirmed,
            remember: this.showRemember ? this.remember : undefined
        });

        this.onClose.emit();
    }
}
