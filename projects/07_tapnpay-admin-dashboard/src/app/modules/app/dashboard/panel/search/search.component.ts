import {
    AfterViewInit,
    ChangeDetectionStrategy,
    Component, ElementRef, HostBinding, HostListener,
    OnDestroy,
    OnInit,
    Renderer2, ViewChild,
    ViewEncapsulation
} from '@angular/core';
import {asyncScheduler, fromEvent, iif, Subscription} from 'rxjs';
import {
    AccountSearchResult,
    SEARCH_MAX_TERM_LENGTH,
    SEARCH_MIN_TERM_LENGTH,
    SearchService
} from '../../../../../services/search.service';
import {debounceTime, distinctUntilChanged, map, takeWhile, throttleTime} from 'rxjs/operators';
import {defer, escapeUnicodeString} from '../../../../../lib/utils';
import {DomService} from '../../../../../services/dom.service';
import {ACCOUNT_STATUS_COLOR} from '../../../../../services/account.service';
import {Router} from '@angular/router';


const SEARCH_HL_REGEX_PROPS = [ 'phone', 'lp', 'bpm' ];
const SEARCH_MAX_VISIBLE_ITEMS = 8;

@Component({
    selector: 'search',
    templateUrl: './search.component.html',
    styleUrls: [ './search.component.scss' ],
    changeDetection: ChangeDetectionStrategy.Default,
    encapsulation: ViewEncapsulation.None,
    host: {
        'class': 'search'
    },
})
export class SearchComponent implements OnInit, OnDestroy, AfterViewInit {
    readonly minTermLength = SEARCH_MIN_TERM_LENGTH;

    readonly maxTermLength = SEARCH_MAX_TERM_LENGTH;

    subs : Subscription[] = [];

    @ViewChild('searchEl')
    searchEl : ElementRef;

    accounts : AccountSearchResult[] = null;

    searchRequestId : number = -1;

    isSubmitting : boolean = false;

    term : string = '';

    isPopupVisible : boolean = false;

    get isClearButtonVisible () : boolean {
        return !!this.term;
    }

    readonly statusColors = ACCOUNT_STATUS_COLOR;

    @HostBinding('class.search_focus')
    hasInputFocus : boolean = false;

    @HostBinding('class.search_attracting')
    isAttracting : boolean = false;

    hoverAccountIndex : number = null;

    constructor (
        private el : ElementRef,
        private router : Router,
        private domService : DomService,
        private searchService : SearchService,
    ) {}

    ngOnInit () {

    }

    ngOnDestroy () {
        this.subs.forEach(sub => sub.unsubscribe());
    }

    ngAfterViewInit () {
        this.subs.push(
            fromEvent(this.searchEl.nativeElement, 'input')
                .pipe(
                    map((e : any) => e.target.value.trim()),
                    debounceTime(150),
                    distinctUntilChanged(),
                )
                .subscribe((term : string) => this.onTermChange(term))
        );

        this.subs.push(
            fromEvent(this.el.nativeElement, 'animationend').subscribe(() => {
                this.isAttracting = false;
            })
        );

        this.subs.push(
            fromEvent(document.documentElement, 'keydown').subscribe((e : KeyboardEvent) => {
                if (e.ctrlKey && e.code === 'KeyG' && this.searchEl) {
                    e.preventDefault();
                    this.isAttracting = true;
                    this.searchEl.nativeElement.focus();
                }
            })
        );
    }

    async onTermChange (term : string) {
        this.searchRequestId += 1;

        if (term.length < 3 || term.length > 15) {
            this.accounts = null;
            this.isSubmitting = false;
            this.isPopupVisible = false;
            return;
        }

        const currentRequestId = this.searchRequestId;
        this.isSubmitting = true;

        const [ accounts, regex ] = await Promise.all([
            this.searchService.search(term).toPromise(),
            this.compileRegexp(term),
        ]).catch(() => [ null, null ]);

        if (currentRequestId !== this.searchRequestId) {
            return;
        }

        if (accounts && accounts.length > 0) {
            const truncatedAccounts = accounts.slice(0, SEARCH_MAX_VISIBLE_ITEMS);

            if (regex) {
                truncatedAccounts.forEach(account => {
                    SEARCH_HL_REGEX_PROPS.forEach(prop => {
                        account[prop] = account[prop].replace(regex, '<span class="search__popup-item-highlight">$1</span>');
                    });
                });
            }

            this.accounts = truncatedAccounts;
        } else {
            this.accounts = null;
        }

        this.hoverAccountIndex = null;
        this.isSubmitting = false;
        this.isPopupVisible = true;
    }

    async compileRegexp (term : string) : Promise<null | RegExp> {
        if (!term) {
            return null;
        }

        term = escapeUnicodeString(term.replace(/\s+/gi, ' '));

        try {
            return RegExp(`(${ term })`, 'gi');
        } catch (e) {
            console.warn(`Failed to compile regex for term '${ term }'`);
        }

        return null;
    }

    onClearClick () {
        this.hidePopup();
        this.reset();

        defer(() => {
            if (this.searchEl) {
                this.searchEl.nativeElement.focus();
            }
        });
    }

    onItemMouseEnter (itemIndex : number) {
        this.hoverAccountIndex = itemIndex;
    }

    onItemMouseLeave () {
        this.hoverAccountIndex = null;
    }

    onItemClick () {
        this.hidePopup();
    }

    @HostListener('click', [ '$event' ])
    onHostClick (e : any) {
        this.domService.markEvent(e, 'searchHostClick');
    }

    @HostListener('document:click', [ '$event' ])
    onDocClick (e : any) {
        if (!this.domService.hasEventMark(e, 'searchHostClick')) {
            this.hidePopup();
        }
    }

    onInputFocus () {
        this.hasInputFocus = true;
        this.hoverAccountIndex = null;

        if (this.accounts) {
            this.isPopupVisible = true;
        }
    }

    onInputBlur () {
        this.hasInputFocus = false;
        // this.hoverAccountIndex = null;
    }

    onInputPressEnter () {
        const accountCount = this.accounts && this.accounts.length || 0;
        const accountIndex = this.hoverAccountIndex === null ? -1 : this.hoverAccountIndex;

        if (accountIndex < 0 || accountIndex >= accountCount) {
            return;
        }

        const account = this.accounts[accountIndex];

        this.router.navigate([ '/dashboard/accounts/', account.account_id ]);
        this.hidePopup();
        this.searchEl.nativeElement.blur();
    }

    onInputPressArrow (dir : -1 | 1) {
        const accountCount = this.accounts && this.accounts.length || 0;

        if (!accountCount) {
            return;
        }

        const currentIndex = this.hoverAccountIndex === null ? -1 : this.hoverAccountIndex;
        const newIndex = currentIndex + dir;

        this.hoverAccountIndex = (
            newIndex < 0 ? accountCount - 1 :
            newIndex >= accountCount ? 0 :
            newIndex
        );
    }

    onInputKeyPress (e : KeyboardEvent) {
        switch (e.code) {
            case 'ArrowUp':
                e.preventDefault();
                this.onInputPressArrow(-1);
                break;
            case 'ArrowDown':
                e.preventDefault();
                this.onInputPressArrow(1);
                break;
            case 'Enter':
                e.preventDefault();
                this.onInputPressEnter();
                break;
        }
    }

    hidePopup () {
        this.searchRequestId += 1;
        this.isSubmitting = false;
        this.isPopupVisible = false;
    }

    reset () {
        this.searchRequestId += 1;
        this.accounts = null;
        this.term = '';
    }

    getStatusColor (statusKey : string) : string {
        if (/_LOCK/i.test(statusKey)) {
            return this.statusColors['_LOCK'];
        }

        return this.statusColors[statusKey] || '#4875e7';
    }
}

