import {OnInit, Component, HostListener, Renderer2, ViewEncapsulation} from '@angular/core';
import { animate, state, style, transition, trigger } from '@angular/animations';
import { TranslateService } from '@ngx-translate/core';
import { ActivatedRoute } from '@angular/router';
import {UserService} from '../../services/user.service';
import {defer} from '../../lib/utils';

// http://127.0.0.1:82/payments/15ced29a-b32b-4084-a067-19481049ee93
// http://127.0.0.1:82/payments/31bd39c8-5cfe-4e14-a729-6d47aea23e42

@Component({
    templateUrl: './payments-result.component.html',
    encapsulation: ViewEncapsulation.None,
    animations: [
        trigger('showPanel', [
            state('false', style({ transform: 'translateY(-100%)' })),
            state('true', style({ transform: 'translateY(0%)' })),
            transition('false => true', animate('0.4s ease-out'))
        ])
    ]
})
export class PaymentsResultComponent implements OnInit {
    public isReady : boolean = false;

    public isLangSwitcherActive : boolean = false;

    public currentLang : string = 'en';

    public langs : any[] = [
        {
            locale: 'en',
            name: 'English'
        },
        {
            locale: 'ru',
            name: 'Russian'
        },
        {
            locale: 'pl',
            name: 'Polish'
        },
        {
            locale: 'es',
            name: 'Spanish'
        },
        {
            locale: 'uk',
            name: 'Ukrainian'
        },
    ];

    public status : string = null;

    public constructor (
        private renderer : Renderer2,
        private route : ActivatedRoute,
        private translate : TranslateService,
        public userService : UserService
    ) {}

    public ngOnInit () {
        defer(() => {
            this.status = this.route.snapshot.params['status'];
            this.currentLang = this.userService.getUserData().local.language;

            this.isReady = true;
        });
    }

    public markLangSwitcherEvent (event : any) {
        event.isLangSwitcherEvent = true;
    }

    public toggleLangSwitcher () {
        this.isLangSwitcherActive = !this.isLangSwitcherActive;
    }

    @HostListener('click', [ '$event.isLangSwitcherEvent' ])
    public onComponentClick (isLangSwitcherEvent : boolean = false) {
        !isLangSwitcherEvent && (this.isLangSwitcherActive = false);
    }

    public onLangSwitch (lang : any) {
        // TODO: refactor lang [2]
        this.currentLang = lang.locale;
        const userData = this.userService.getUserData();
        userData.local.language = this.currentLang;
        this.userService.updateUserData(userData);
        // window.localStorage.setItem('userLang', this.currentLang);
        // this.translate.use(this.currentLang);
        this.isLangSwitcherActive = false;
    }
}
