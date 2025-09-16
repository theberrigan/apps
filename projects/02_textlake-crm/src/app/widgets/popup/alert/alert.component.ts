import { Component, EventEmitter, Input, Output, ViewEncapsulation } from '@angular/core';
import { isArray, isUndefined, merge } from 'lodash';
import { Subject } from 'rxjs';
import { AlertOptions, IAlertResponse } from '../../../services/popup.service';

@Component({
    selector: 'alert',
    templateUrl: './alert.component.html',
    styleUrls: [ './alert.component.scss' ],
    encapsulation: ViewEncapsulation.None,
    host: {
        class: 'alert'
    }
})
export class AlertComponent {
    // This event listened by popup manager
    @Output()
    public onClose = new EventEmitter<void>();

    @Input()
    public set options (options : AlertOptions) {
        options = merge({}, new AlertOptions(), options);

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
            this.title = 'popups.alert.title';
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

        if (isArray(options.buttonCaption)) {
            [ this.buttonCaption, this.buttonCaptionData ] = options.buttonCaption;
            this.translateButtonCaption = true;
        } else if (options.buttonCaption) {
            this.buttonCaption = options.buttonCaption;
            this.translateButtonCaption = false;
        } else {
            this.buttonCaption = 'popups.alert.ok__button';
            this.translateButtonCaption = true;
        }
    }

    public showRemember : boolean;

    public translateTitle : boolean;

    public title : string;

    public titleData : any;

    public translateMessage : boolean;

    public message : string;

    public messageData : any;

    public translateButtonCaption : boolean;

    public buttonCaption : string;

    public buttonCaptionData : any;

    public responseSubject : Subject<IAlertResponse>;

    public remember : boolean = false;

    constructor () {}

    public onOk (closeByOverlay : boolean) : void {
        if (closeByOverlay) {
            return;
        }

        this.responseSubject.next({
            remember: this.showRemember ? this.remember : undefined
        });

        this.onClose.emit();
    }
}
