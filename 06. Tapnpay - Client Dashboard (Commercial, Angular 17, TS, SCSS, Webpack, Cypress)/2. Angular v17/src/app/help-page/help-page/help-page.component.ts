import {ChangeDetectionStrategy, Component, OnInit, Renderer2, ViewEncapsulation} from '@angular/core';
import {Router} from '@angular/router';
import {TitleService} from '../../services/title.service';
import {UntypedFormBuilder} from '@angular/forms';
import {ToastService} from '../../services/toast.service';
import {DeviceService, ViewportBreakpoint} from '../../services/device.service';
import {Subscription} from 'rxjs';
import {ILang, LANGS, LangService} from '../../services/lang.service';
import {TermsService, TermsSession} from '../../services/terms.service';
import { NEO_RIDE_LOGO_URL } from '../../constants/logo.constants';

@Component({
    selector: 'help-page',
    templateUrl: './help-page.component.html',
    styleUrls: ['./help-page.component.scss'],
    changeDetection: ChangeDetectionStrategy.Default,
    encapsulation: ViewEncapsulation.None,
    host: {
        'class': 'help-page'
    }
})
export class HelpPageComponent implements OnInit {
    readonly langs = LANGS;

    currentLang: ILang;

    termsSession: TermsSession;

    viewportBreakpoint: ViewportBreakpoint;

    subs: Subscription[] = [];

    public NEO_RIDE_LOGO_URL = NEO_RIDE_LOGO_URL;

    constructor(
        private renderer: Renderer2,
        private router: Router,
        private formBuilder: UntypedFormBuilder,
        private titleService: TitleService,
        private toastService: ToastService,
        private deviceService: DeviceService,
        private termsService: TermsService,
        private langService: LangService,
    ) {
        window.scroll(0, 0);

        this.viewportBreakpoint = this.deviceService.viewportBreakpoint;

        this.subs.push(this.deviceService.onResize.subscribe(message => {
            if (message.breakpointChange) {
                this.viewportBreakpoint = this.deviceService.viewportBreakpoint;
            }
        }));

        this.setTermsState(this.termsService.getTermsSession());
        this.termsService.onTermsSessionChange.subscribe(session => this.setTermsState(session));

        this.updateCurrentLang();
        this.langService.onLangChange(() => this.updateCurrentLang());
    }

    ngOnInit(): void {

    }

    ngOnDestroy(): void {
        this.subs.forEach(sub => sub.unsubscribe());
    }

    setTermsState(termsSession: TermsSession) {
        this.termsSession = termsSession;
    }

    updateCurrentLang() {
        const currentLangCode = this.langService.getCurrentLangCode();
        this.currentLang = this.langs.find(lang => lang.code === currentLangCode);
    }
}
