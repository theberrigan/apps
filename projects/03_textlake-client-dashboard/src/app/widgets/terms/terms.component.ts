import {
    Component,
    OnDestroy,
    OnInit, ViewChild,
    ViewEncapsulation
} from '@angular/core';
import {IShowTermsEvent, IShowTermsResponseEvent, Terms, TermsService} from '../../services/terms.service';
import {ReplaySubject} from 'rxjs';
import {PopupComponent} from '../popup/popup.component';

@Component({
    selector: 'terms',
    exportAs: 'terms',
    templateUrl: './terms.component.html',
    styleUrls: [ './terms.component.scss' ],
    encapsulation: ViewEncapsulation.None,
    host: {
        'class': 'terms'
    }
})
export class TermsComponent implements OnInit, OnDestroy {
    public terms : Terms;

    public text : string;

    public isAcceptRequired : boolean;

    public responseSubject : ReplaySubject<IShowTermsResponseEvent>;

    @ViewChild('popup')
    public popup : PopupComponent;

    public isAccepted : boolean = false;

    public isAcceptInProgress : boolean = false;

    constructor (
        public termsService : TermsService
    ) {}

    public ngOnInit () : void {
        this.termsService.onShowTerms.subscribe((e : IShowTermsEvent) => {
            console.log('Loading...');

            this.popup.showSpinner();
            this.popup.activate();
            this.isAcceptRequired = e.isAcceptRequired;
            this.responseSubject = e.responseSubject;

            this.termsService.fetchTerms(e.endpoint)
                .then((terms : Terms) => {
                    if (!terms) {
                        this.responseSubject.next({ status: 'empty' });
                        this.popup.deactivate();
                        return;
                    }

                    this.terms = terms;
                    this.text = terms.textEng; // TODO
                    this.popup.showBox();
                    this.responseSubject.next({ status: 'shown' });

                })
                .catch(() => {
                    this.responseSubject.next({ status: 'error' });
                    this.popup.deactivate();
                });
        });
    }

    public ngOnDestroy () : void {
        this.cleanUp();
    }

    public onAccept () : void {
        if (!this.isAcceptRequired || !this.isAccepted || this.isAcceptInProgress) {
            return;
        }

        this.isAcceptInProgress = true;

        // setTimeout(() => {
        //     this.isAcceptInProgress = false;
        //     this.responseSubject.next({ status: 'close' });
        //     this.popup.deactivate();
        // }, 7000);
        // return;

        this.termsService
            .acceptTerms(this.terms.id)
            .then(() => {
                this.responseSubject.next({ status: 'accepted' });
            })
            .catch(() => {
                this.responseSubject.next({ status: 'error' });
            })
            .then(() => {
                this.isAcceptInProgress = false;
                this.responseSubject.next({ status: 'close' });
                this.popup.deactivate();
            });

    }

    public onCloseRequest (byOverlay? : boolean) : void {
        if (byOverlay || this.isAcceptRequired) {
            return;
        }

        this.responseSubject.next({ status: 'close' });
        this.popup.deactivate();
    }

    public onDeactivate () : void {
        this.responseSubject.next({ status: 'complete' });
        this.cleanUp();
    }

    public cleanUp () : void {
        this.terms = null;
        this.text = null;
        this.responseSubject = null;
        this.isAcceptRequired = false;
        this.isAccepted = false;
        this.isAcceptInProgress = false;
        console.log('Clear');
    }
}
