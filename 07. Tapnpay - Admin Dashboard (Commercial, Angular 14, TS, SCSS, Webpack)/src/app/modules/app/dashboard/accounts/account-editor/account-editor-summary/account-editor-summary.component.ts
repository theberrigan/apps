import {
    ChangeDetectionStrategy,
    Component, Input,
    OnDestroy,
    OnInit,
    ViewEncapsulation
} from '@angular/core';
import {Subscription} from 'rxjs';
import {
    AccountSummary,
} from '../../../../../../services/account.service';
import {int} from '../../../../../../lib/utils';

interface AccountLongevity {
    value: number;
    key: string;
}

@Component({
    selector: 'account-editor-summary',
    templateUrl: './account-editor-summary.component.html',
    styleUrls: [ './account-editor-summary.component.scss' ],
    changeDetection: ChangeDetectionStrategy.Default,
    encapsulation: ViewEncapsulation.None,
    host: {
        'class': 'account-editor-summary',
    }
})
export class AccountEditorSummaryComponent implements OnInit, OnDestroy {
    subs : Subscription[] = [];

    @Input()
    data : AccountSummary;

    accountLongevity : null | AccountLongevity = null;

    activeLPNs : string = null;

    inactiveLPNs : string = null;

    constructor () {}

    ngOnInit () {
        this.calcLongevity();
        this.processLPNs();
    }

    ngOnDestroy () : void {
        this.subs.forEach(sub => sub.unsubscribe());
    }

    processLPNs () {
        const activeLPNs : string[] = [];
        const inactiveLPNs : string[] = [];

        this.data?.plates?.forEach(lp => {
            if (lp.status === 'ACTIVE') {
                activeLPNs.push(lp.lp);
            } else {
                inactiveLPNs.push(lp.lp);
            }
        });

        this.activeLPNs = activeLPNs.length ? activeLPNs.join(', ') : null;
        this.inactiveLPNs = inactiveLPNs.length ? inactiveLPNs.join(', ') : null;
    }

    calcLongevity () {
        if (this.accountLongevity) {
            return;
        }

        this.accountLongevity = {
            value: 0,
            key: 'duration.minutes'
        };

        if (this.data && this.data.terms_accepted) {
            const minutes = int((Date.now() - new Date(this.data.terms_accepted).getTime()) / 1000 / 60);
            const hours = int(minutes / 60);
            const days = int(hours / 24);
            const months = int(days / 30);
            const years = int(days / 355);

            // console.log(minutes, hours, days, months, years);

            if (years >= 1) {
                this.accountLongevity.value = years;
                this.accountLongevity.key = 'duration.years';
            } else if (months >= 1) {
                this.accountLongevity.value = months;
                this.accountLongevity.key = 'duration.months';
            } else if (days >= 1) {
                this.accountLongevity.value = days;
                this.accountLongevity.key = 'duration.days';
            } else if (hours >= 1) {
                this.accountLongevity.value = hours;
                this.accountLongevity.key = 'duration.hours';
            } else {
                this.accountLongevity.value = minutes;
                this.accountLongevity.key = 'duration.minutes';
            }
        }
    }
}
