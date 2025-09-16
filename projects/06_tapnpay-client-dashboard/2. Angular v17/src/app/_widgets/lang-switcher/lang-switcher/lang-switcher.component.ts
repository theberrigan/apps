import {
    ChangeDetectionStrategy,
    Component,
    HostBinding,
    HostListener, OnDestroy,
    OnInit,
    Renderer2,
    ViewEncapsulation
} from '@angular/core';
import {Router} from '@angular/router';
import {TitleService} from '../../../services/title.service';
import {defer} from '../../../lib/utils';
import {UntypedFormBuilder, FormGroup} from '@angular/forms';
import {ToastService} from '../../../services/toast.service';
import {DeviceService, ViewportBreakpoint} from '../../../services/device.service';
import {Subscription} from 'rxjs';
import {ILang, LANGS, LangService} from '../../../services/lang.service';
import {TermsService, TermsSession} from '../../../services/terms.service';
import {DomService} from '../../../services/dom.service';
import {UserService} from '../../../services/user.service';

@Component({
    selector: 'lang-switcher',
    templateUrl: './lang-switcher.component.html',
    styleUrls: [ './lang-switcher.component.scss' ],
    changeDetection: ChangeDetectionStrategy.Default,
    encapsulation: ViewEncapsulation.None,
    host: {
        'class': 'lang-switcher'
    }
})
export class LangSwitcherComponent implements OnInit, OnDestroy {
    readonly langs = LANGS;

    currentLang : ILang;

    @HostBinding('class.lang-switcher_active')
    isLangMenuActive : boolean = false;

    subs : Subscription[] = [];

    constructor (
        private renderer : Renderer2,
        private router : Router,
        private formBuilder : UntypedFormBuilder,
        private titleService : TitleService,
        private toastService : ToastService,
        private deviceService : DeviceService,
        private termsService : TermsService,
        private langService : LangService,
        private domService : DomService,
        private userService : UserService,
    ) {
        window.scroll(0, 0);

        this.updateCurrentLang();
        this.subs.push(this.langService.onLangChange(() => this.updateCurrentLang()));
    }

    ngOnInit () : void {

    }

    ngOnDestroy () : void {
        this.subs.forEach(sub => sub.unsubscribe());
    }

    updateCurrentLang () {
        const currentLangCode = this.langService.getCurrentLangCode();
        this.currentLang = this.langs.find(lang => lang.code === currentLangCode);
    }

    onLangItemClick (lang : ILang, e : any) {
        this.currentLang = lang;
        this.userService.setLang(lang.code);
        this.domService.markEvent(e, 'langItemClick');
    }

    onLangMenuClick (e : any) {
        this.domService.markEvent(e, 'langMenuClick');
    }

    onLangTriggerClick (e : any) {
        this.domService.markEvent(e, 'langTriggerClick');
    }

    @HostListener('document:click', [ '$event' ])
    onDocClick (e : any) {
        if (this.domService.isHasEventMark(e, 'langTriggerClick')) {
            this.isLangMenuActive = !this.isLangMenuActive;
        } else if (!this.domService.isHasEventMark(e, 'langMenuClick') || this.domService.isHasEventMark(e, 'langItemClick')) {
            this.isLangMenuActive = false;
        }
    }
}
