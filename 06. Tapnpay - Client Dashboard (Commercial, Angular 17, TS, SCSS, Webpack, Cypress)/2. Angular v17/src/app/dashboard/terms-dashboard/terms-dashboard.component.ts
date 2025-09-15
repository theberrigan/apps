import {ChangeDetectionStrategy, Component, OnInit, Renderer2, ViewEncapsulation} from '@angular/core';
import {Router} from '@angular/router';
import {TitleService} from '../../services/title.service';
import {DeviceService, ViewportBreakpoint} from '../../services/device.service';
import {AcceptedTermsResponse, ExtendedTerms, TermsService} from "../../services/terms.service";

@Component({
    selector: 'terms-dashboard',
    templateUrl: './terms-dashboard.component.html',
    styleUrls: ['./terms-dashboard.component.scss'],
    changeDetection: ChangeDetectionStrategy.Default,
    encapsulation: ViewEncapsulation.None,
    host: {
        'class': 'terms-dashboard'
    }
})
export class TermsDashboardComponent implements OnInit {
    viewportBreakpoint: ViewportBreakpoint;
    isUserHasExtendedTollAuthorities: boolean = false;
    listOfExtendedTerms: ExtendedTerms[] = [];
    firstSelectedTerms: ExtendedTerms;
    isLoading: boolean = true;
    public allTermsList: ExtendedTerms[];

    constructor(
        private renderer: Renderer2,
        private router: Router,
        private titleService: TitleService,
        private deviceService: DeviceService,
        private termsService: TermsService
    ) {
        window.scroll(0, 0);

        this.viewportBreakpoint = this.deviceService.viewportBreakpoint;
        this.deviceService.onResize.subscribe((message) => {
            if (message.breakpointChange) {
                this.viewportBreakpoint = message.breakpointChange.current;
            }
        });
    }

    public ngOnInit() {
        this.titleService.setTitle('terms.page_title');

        this.termsService.fetchAcceptedTerms().subscribe(
            (termsHttpResponse: AcceptedTermsResponse) => {
                this.listOfExtendedTerms = termsHttpResponse.extended_terms;
                this.firstSelectedTerms = {
                    terms_name: termsHttpResponse.terms_name,
                    toll_authority_name: termsHttpResponse?.toll_authority_name ?
                        termsHttpResponse?.toll_authority_name : termsHttpResponse.terms_name.split('-')[0].toUpperCase(),
                };
                this.allTermsList = [this.firstSelectedTerms, ...termsHttpResponse.extended_terms];
                this.isUserHasExtendedTollAuthorities = termsHttpResponse.extended_terms.length > 0;
                this.isLoading = false;
            },
            (error) => {
                this.isLoading = false;
                console.error(error);
            });
    }


    expandItem() {

    }
}
