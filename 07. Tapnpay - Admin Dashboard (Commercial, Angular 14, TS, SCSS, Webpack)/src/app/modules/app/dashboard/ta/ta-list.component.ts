import {
    ChangeDetectionStrategy,
    Component, ElementRef, HostListener, Input,
    OnDestroy,
    OnInit, ViewChild,
    ViewEncapsulation
} from '@angular/core';
import {Subscription} from 'rxjs';
import {TitleService} from '../../../../services/title.service';
import {ToastService} from '../../../../services/toast.service';
import {TAListItem, TAService} from '../../../../services/ta.service';
import {Router} from '@angular/router';

type ListState = 'loading' | 'ready' | 'empty' | 'error';

@Component({
    selector: 'ta-list',
    templateUrl: './ta-list.component.html',
    styleUrls: [ './ta-list.component.scss' ],
    changeDetection: ChangeDetectionStrategy.Default,
    encapsulation: ViewEncapsulation.None,
    host: {
        'class': 'ta-list'
    },
})
export class TAListComponent implements OnInit, OnDestroy {
    subs : Subscription[] = [];

    authorities : TAListItem[];

    listState : ListState = 'loading';

    isCreatePopupVisible : boolean = false;

    isTANameValid : boolean = false;

    taName : string = '';

    isSubmitting : boolean = false;

    constructor (
        private router : Router,
        private titleService : TitleService,
        private taService : TAService,
        private toastService : ToastService,
    ) {
        this.titleService.setTitle('ta.list.page_title');
        this.listState = 'loading';
    }

    ngOnInit () : void {
        this.loadTAs();
    }

    ngOnDestroy () : void {
        this.subs.forEach(sub => sub.unsubscribe());
    }

    async loadTAs () {
        this.authorities = await this.taService.fetchTAs().toPromise().catch(() => null);

        if (!this.authorities) {
            this.listState = 'error';
        } else if (this.authorities.length) {
            this.listState = 'ready';
        } else {
            this.listState = 'empty';
        }
    }

    onEditTA (authority : TAListItem) {
        this.router.navigate([ '/dashboard/toll-authorities', authority.id ]);
    }

    onCreateTA (e? : MouseEvent) {
        e?.preventDefault();

        this.taName = '';
        this.isTANameValid = false;
        this.isCreatePopupVisible = true;
    }

    onCancelCreate () {
        this.hideCreatePopup();
    }

    async onConfirmCreate () {
        if (this.isSubmitting || !this.isTANameValid) {
            return;
        }

        this.isSubmitting = true;

        const name = (this.taName || '').trim();
        const result = await this.taService.createTA({ name }).toPromise().catch(() => null);

        this.isSubmitting = false;

        if (result) {
            this.hideCreatePopup();
            this.router.navigate([ '/dashboard/toll-authorities', result.id ]);
        } else {
            this.toastService.create({
                message: [ 'ta.list.create_error' ],
                timeout: 9000
            });
        }
    }

    hideCreatePopup () {
        this.isCreatePopupVisible = false;
    }

    validateTAName () {
        this.isTANameValid = !!(this.taName || '').trim();
    }
}
