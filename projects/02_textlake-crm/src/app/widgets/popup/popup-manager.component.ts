import {
    Component,
    OnDestroy,
    OnInit, TemplateRef,
    ViewEncapsulation
} from '@angular/core';
import {ICreatePopupEvent, PopupService} from '../../services/popup.service';
import {without} from 'lodash';
import {defer} from '../../lib/utils';

@Component({
    selector: 'popup-manager',
    templateUrl: './popup-manager.component.html',
    encapsulation: ViewEncapsulation.None,
    host: {
        'class': 'popup-manager'
    }
})
export class PopupManagerComponent implements OnInit, OnDestroy {
    public popups : ICreatePopupEvent[] = [];
    public popupTemplates : TemplateRef<any>[] = [];

    constructor (
        private popupService : PopupService
    ) {}

    public ngOnInit () : void {
        this.popupService.onCreatePopup.subscribe((popup : ICreatePopupEvent) => {
            this.popups = [ ...this.popups, popup ];
        });

        this.popupService.onPopupTemplate.subscribe((options : any) => {
            if (options.isCreate) {
                this.popupTemplates = [ ...this.popupTemplates, options.popupTpl ];
                defer(() => options.responseSubject.next());
            } else {
                this.popupTemplates = without(this.popupTemplates, options.popupTpl);
            }
        });
    }

    public ngOnDestroy () : void {

    }

    public onClose (popup : ICreatePopupEvent) : void {
        this.popups = without(this.popups, popup);
    }
}
