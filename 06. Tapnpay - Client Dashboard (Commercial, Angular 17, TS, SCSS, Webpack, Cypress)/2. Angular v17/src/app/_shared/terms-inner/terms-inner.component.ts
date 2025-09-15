import {
    ChangeDetectionStrategy,
    Component,
    ElementRef,
    Input,
    OnDestroy,
    OnInit,
    Renderer2,
    ViewChild,
    ViewEncapsulation
} from '@angular/core';
import {ActivatedRoute, Router} from '@angular/router';
import {Location} from '@angular/common';
import {TitleService} from '../../services/title.service';
import {LangService} from '../../services/lang.service';
import {fromEvent, Subscription} from 'rxjs';
import {AcceptedTermsResponse, AcceptTermsResponse, TermsData, TermsService} from '../../services/terms.service';
import {SafeHtml} from '@angular/platform-browser';
import {DeviceService, ViewportBreakpoint} from '../../services/device.service';
import {defer} from '../../lib/utils';
import {ToastService} from '../../services/toast.service';
import {UserService} from '../../services/user.service';

type State = 'loading' | 'list' | 'terms' | 'error';

@Component({
    selector: 'terms-inner',
    templateUrl: './terms-inner.component.html',
    styleUrls: ['./terms-inner.component.scss'],
    encapsulation: ViewEncapsulation.None,
    changeDetection: ChangeDetectionStrategy.Default,
    host: {
        'class': 'terms-inner'
    }
})
export class TermsInnerComponent implements OnInit, OnDestroy {
    state: State;

    @Input() termsNameToShow: string = null;
    @Input() isLoadTerms: boolean = true;

    public isAcceptable: boolean = false;

    public termsPageHtmlContent: string | SafeHtml = '';

    public subs: Subscription[] = [];

    public phone: string = null;

    @ViewChild('contentEl')
    contentEl: ElementRef;

    @ViewChild('panelEl')
    panelEl: ElementRef;

    viewportBreakpoint: ViewportBreakpoint;

    panelWidth: number = 0;

    panelBottom: number = 0;

    panelLeft: number = 0;

    contentBottomPadding: number = 40;

    isPanelSticky: boolean = false;

    isChecked: boolean = false;

    isSubmitting: boolean = false;

    readonly isDashboard: boolean = false;

    acceptedTerms: AcceptedTermsResponse;

    docItems: {
        name: string;
        title: string;
        type: string;
    }[] = [
        {
            name: 'ntta-31072020',
            title: 'tapNpay – Northern Texas Toll Authority',
            type: 'Terms & Conditions'
        },
        {
            name: 'sunpass-071221',
            title: 'tapNpay – Florida SunPass',
            type: 'Terms & Conditions'
        },
        {
            name: 'fastrak-071221',
            title: 'tapNpay – California FasTrak',
            type: 'Terms & Conditions'
        },
        {
            name: 'ipass-071221',
            title: 'tapNpay – Illinois Ipass',
            type: 'Terms & Conditions'
        },
        {
            name: 'GOODTOGO-102822',
            title: 'tapNpay – GoodToGo Washington',
            type: 'Terms & Conditions'
        },
        {
            name: 'TXHUB-102822',
            title: 'tapNpay – Northern Texas Toll Authority',
            type: 'Terms & Conditions'
        },
        {
            name: 'neoride-081623',
            title: 'neoRide',
            type: 'Terms & Conditions'
        }
    ];

    isFirstTimeLoaded: boolean = false;

    isLangChangedManually: boolean = false;

    constructor(
        private renderer: Renderer2,
        private router: Router,
        private route: ActivatedRoute,
        private location: Location,
        private titleService: TitleService,
        private langService: LangService,
        private termsService: TermsService,
        private deviceService: DeviceService,
        private toastService: ToastService,
        private userService: UserService,
    ) {
        this.state = 'loading';
        this.viewportBreakpoint = this.deviceService.viewportBreakpoint;
        this.isDashboard = this.router.url.toLowerCase().startsWith('/dashboard');
    }

    public ngOnInit() {
        console.log(this.termsNameToShow);
        this.loadTerms();

        this.subs.push(this.langService.onLangChange(() => {
            if (this.isDashboard) {
                this.loadTerms();
            } else if (this.isFirstTimeLoaded) {
                this.isLangChangedManually = true;
                this.loadTerms();
            }
        }));

        this.subs.push(fromEvent(window, 'scroll').subscribe(() => this.redraw()));
        this.subs.push(fromEvent(window, 'resize').subscribe(() => this.redraw()));

        this.deviceService.onResize.subscribe(message => {
            if (message.breakpointChange) {
                this.viewportBreakpoint = this.deviceService.viewportBreakpoint;
                defer(() => this.redraw());
            }
        });
    }

    public ngOnDestroy() {
        this.subs.forEach(sub => sub.unsubscribe());
    }

    async loadTerms() {
        this.state = 'loading';

        let currentLangCode = this.langService.getCurrentLangCode();

        if (this.isDashboard) {
            if (!this.acceptedTerms) {
                this.acceptedTerms = await this.termsService.fetchAcceptedTerms().toPromise().catch(() => null);
            }

            if (!this.acceptedTerms) {
                this.state = 'error';
                this.isFirstTimeLoaded = true;
                return;
            }

            const termsName = this.isLoadTerms ? this.acceptedTerms.terms_name : this.termsNameToShow;

            this.termsPageHtmlContent = await this.termsService.fetchTerms(termsName, currentLangCode).toPromise().catch(() => null);
            this.isAcceptable = false;
            this.state = this.termsPageHtmlContent ? 'terms' : 'error';
            defer(() => this.redraw());
        } else {
            const phone = this.phone = this.route.snapshot.params['phone'] || null;

            if (phone) {
                const termsData: TermsData = await this.termsService.validateTermsData({phone}, true).catch(() => null);

                console.log(termsData);

                console.warn('Reg lang:', this.termsService.regLang);

                if (!this.isLangChangedManually && this.termsService.regLang && currentLangCode != this.termsService.regLang) {
                    currentLangCode = this.termsService.regLang;
                    this.userService.setLang(currentLangCode);
                }

                this.termsService.setTermsData(termsData);

                this.phone = termsData.phone;
                this.isAcceptable = !!this.phone;

                if (this.isAcceptable) {
                    const name = termsData.name;

                    this.termsPageHtmlContent = await this.termsService.fetchTerms(name, currentLangCode).toPromise().catch(() => null);

                    if (this.termsPageHtmlContent) {
                        this.state = 'terms';
                        this.isFirstTimeLoaded = true;
                        defer(() => this.redraw());
                        return;
                    }
                } else {
                    this.router.navigateByUrl('/auth');
                    // this.location.replaceState('/terms');
                }
            }

            this.isFirstTimeLoaded = true;
            this.state = 'list';
        }
    }

    async onListItemClick(name: string) {
        this.state = 'loading';

        const langCode = this.langService.getCurrentLangCode();

        this.termsPageHtmlContent = await this.termsService.fetchTerms(name, langCode).toPromise().catch(() => null);
        this.isAcceptable = false;
        this.state = this.termsPageHtmlContent ? 'terms' : 'error';

        defer(() => this.redraw());
    }

    /*
    public loadTerms () {
        this.isReady = false;
        const langCode = this.langService.getCurrentLangCode();

        this.termsService.fetchTerms(langCode).subscribe((html) => {
            this.content = html;
            this.isReady = true;
            defer(() => this.redraw());
        });
    }
     */

    public redraw() {
        if (!this.isAcceptable || !this.contentEl || !this.panelEl) {
            return;
        }

        const contentRect = this.contentEl.nativeElement.getBoundingClientRect();

        this.panelWidth = Math.round(contentRect.width);
        this.panelLeft = Math.round(contentRect.left);
        this.panelBottom = Math.max(0, window.innerHeight - Math.round(contentRect.bottom));
        this.contentBottomPadding = Math.round(this.panelEl.nativeElement.getBoundingClientRect().height) + 30;
        this.isPanelSticky = this.panelBottom > 1;
    }

    public onSubmit() {
        if (!this.isChecked || !this.phone) {
            return;
        }

        this.isSubmitting = true;

        const onError = () => {
            this.toastService.create({
                message: ['terms.submit.error'],
                timeout: 7000
            });

            this.isSubmitting = false;
        };

        const onDone = ({isOk, token}: AcceptTermsResponse) => {
            if (!isOk) {
                return onError();
            }

            this.userService.applyToken(token, true).then(isOk => {
                if (!isOk) {
                    return onError();
                }

                this.router.navigateByUrl('/dashboard/invoices');

                /*
                this.toastService.create({
                    message: [ 'terms.submit.ok' ],
                    timeout: 6000
                });
                 */

                this.isSubmitting = false;
            });
        };

        this.subs.push(this.termsService.acceptTerms(this.phone).subscribe(
            response => onDone(response),
            () => onDone({isOk: false, token: null})
        ));
    }
}
