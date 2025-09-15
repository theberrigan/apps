import {
    ChangeDetectionStrategy,
    Component,
    ElementRef, HostListener, NgZone,
    OnInit,
    Renderer2,
    ViewChild,
    ViewEncapsulation
} from '@angular/core';
import {ActivatedRoute, Router} from '@angular/router';
import { Location} from '@angular/common';
import {DeviceService, ViewportBreakpoint} from '../../../services/device.service';
import {LangService} from '../../../services/lang.service';
import {fromEvent, Subscription} from 'rxjs';
import {SafeHtml} from '@angular/platform-browser';
import {defer} from '../../../lib/utils';
import {FaqCategory, FaqCategoryItem, FaqService} from '../../../services/faq.service';
import {debounceTime, distinctUntilChanged, map} from 'rxjs/operators';
import {cloneDeep} from 'lodash-es';
import {animate, animateChild, query, style, transition, trigger} from '@angular/animations';

type ListState = 'loading' | 'list' | 'empty' | 'error';

interface FaqFlatItem {
    id : number;
    categoryId : string;
    questionId : string;
    question : string;
    answer : string;
    isExpanded : boolean;
}

@Component({
    selector: 'faq-inner',
    templateUrl: './faq-inner.component.html',
    styleUrls: [ './faq-inner.component.scss' ],
    changeDetection: ChangeDetectionStrategy.Default,
    encapsulation: ViewEncapsulation.None,
    host: {
        'class': 'faq-inner'
    },
    animations: [
        trigger('answerExpand', [
            transition(':enter', [
                style({ height: '0px' }),
                animate('0.15s cubic-bezier(0.5, 1, 0.89, 1)', style({ height: '*' }))
            ]),
            transition(':leave', [
                style({ height: '*' }),
                animate('0.15s cubic-bezier(0.5, 1, 0.89, 1)', style({ height: '0px' }))
            ])
        ]),
    ]
})
export class FaqInnerComponent implements OnInit {
    viewportBreakpoint : ViewportBreakpoint;

    subs : Subscription[] = [];

    listState : ListState = 'loading';

    activeId : string = null;

    currentLang : string = 'en';

    faq : FaqCategory[] = null;

    faqFlat : FaqFlatItem[] = null;

    faqSearchItems : FaqFlatItem[] = null;

    searchValue : string = '';

    searchTimeout : any = null;

    isClearVisible : boolean = false;

    @ViewChild('searchInputEl')
    searchInputEl : ElementRef;

    constructor (
        private hostEl : ElementRef,
        private renderer : Renderer2,
        private router : Router,
        private route : ActivatedRoute,
        private zone : NgZone,
        private location : Location,
        private faqService : FaqService,
        private langService : LangService,
        private deviceService : DeviceService,
    ) {
        this.viewportBreakpoint = this.deviceService.viewportBreakpoint;
        this.deviceService.onResize.subscribe((message) => {
            if (message.breakpointChange) {
                this.viewportBreakpoint = message.breakpointChange.current;
            }
        });
    }

    ngOnInit () {
        this.listState = 'loading';

        this.currentLang = this.langService.getCurrentLangCode();
        const targetId : string = this.route.snapshot.params['id'] || null;

        this.subs.push(this.langService.onLangChange((e : any) => {
            this.currentLang = e.lang;
            this.resetSearch();
            this.loadFaq();
        }));

        this.loadFaq(targetId);
    }

    ngOnDestroy () {
        this.subs.forEach(sub => sub.unsubscribe());
    }

    switchItem (key : string) {
        this.activeId = key === this.activeId ? null : key;
        this.updateUrl(this.activeId);
    }

    async loadFaq (scrollToId : string = null) {
        this.faq = await this.faqService.fetchFAQ(this.currentLang).toPromise().catch(() => null);

        if (this.faq) {
            let itemCounter = 0;

            this.faqFlat = this.faq.reduce((acc : FaqFlatItem[], category : FaqCategory) => {
                category.items.forEach(item => {
                    acc.push({
                        id: ++itemCounter,
                        categoryId: category.id,
                        questionId: item.id,
                        question: item.question,
                        answer: item.answer,
                        isExpanded: false,
                    });
                });

                return acc;
            }, []);

            this.listState = this.faq.length > 0 ? 'list' : 'empty';
        } else {
            this.faqFlat = null;
            this.listState = 'error';
        }

        if (scrollToId) {
            defer(() => {
                const questionEl = this.hostEl.nativeElement.querySelector(`.faq-inner [data-question-id='${ scrollToId }']`);

                if (questionEl) {
                    this.activeId = scrollToId;
                    const questionRect = questionEl.getBoundingClientRect();
                    const questionHeight = questionRect.height;
                    const questionTop = questionRect.top;
                    const targetY = Math.max(0, Math.round(questionTop - (window.innerHeight - questionHeight) / 2));

                    window.scrollTo(0, targetY);
                }
            });
        } else if (!this.deviceService.device.touch) {
            this.focusOnSearchInput();
        }

        console.log(this.faqFlat);
    }

    updateUrl (targetId : string) {
        const { pathname, search, hash } = window.location;

        const newPath = /\/dashboard\//i.test(pathname) ? '/dashboard/faq' : '/faq';
        const finalPath = targetId ? `${ newPath }/${ targetId }` : newPath;

        this.location.replaceState(`${ finalPath }${ search }${ hash }`);
    }

    faqCategoryTrackBy (index, item : FaqCategory) : string {
        return item.id;
    }

    faqItemTrackBy (index, item : FaqCategoryItem) : string {
        return item.id;
    }

    faqFlatTrackBy (index, item : FaqFlatItem) : number {
        return item.id;
    }

    resetSearchTimeout () {
        if (this.searchTimeout !== null) {
            clearTimeout(this.searchTimeout);
            this.searchTimeout = null;
        }
    }

    onSearch () {
        this.resetSearchTimeout();

        this.isClearVisible = !!this.searchValue;

        const value : string = (this.searchValue || '').trim();

        if (value.length < 3) {
            this.faqSearchItems = null;
            return;
        }

        this.searchTimeout = setTimeout(() => {
            this.zone.run(() => {
                this.resetSearchTimeout();
                this.doSearch(value);
            });
        }, 250);
    }

    doSearch (value : string) {
        const regexPattern = (
            value
                .trim()
                .replace(/\s+/, ' ')
                .split('')
                .map(char => char === ' ' ? '\\s' : ('\\u' + char.charCodeAt(0).toString(16).padStart(4, '0')))
                .join('')
        );

        let regex : RegExp = null;

        try {
            regex = RegExp(`(${ regexPattern })`, 'ig');
        } catch (e) {
            console.warn(`Failed to compile regex for value '${ value }'`);
            return;
        }

        this.faqSearchItems = this.faqFlat.reduce((acc : FaqFlatItem[], item : FaqFlatItem) => {
            const newQuestion = item.question.replace(regex, '<span class="faq-inner__search-highlight">$1</span>');
            const newAnswer = item.answer.replace(regex, '<span class="faq-inner__search-highlight">$1</span>');
            const hasAnswerMatch = newAnswer !== item.answer;

            if (newQuestion !== item.question || hasAnswerMatch) {
                const foundItem = cloneDeep(item);

                foundItem.question = newQuestion;
                foundItem.answer = newAnswer;
                foundItem.isExpanded = hasAnswerMatch;

                acc.push(foundItem);
            }

            return acc;
        }, []);
    }

    toggleSearchItem (item : FaqFlatItem) {
        item.isExpanded = !item.isExpanded;
    }

    resetSearch () {
        this.resetSearchTimeout();
        this.searchValue = '';
        this.faqSearchItems = null;
        this.isClearVisible = false;
    }

    onClearSearchClick () {
        this.resetSearch();

        if (!this.deviceService.device.touch) {
            this.focusOnSearchInput();
        }
    }

    onSearchKeyDown (e : KeyboardEvent) {
        if (e.code === 'Escape') {
            e.preventDefault();
            this.resetSearch();
            this.searchInputEl.nativeElement?.blur();
        }
    }

    focusOnSearchInput () {
        defer(() => this.searchInputEl?.nativeElement.focus());
    }

    @HostListener('document:keydown', [ '$event' ])
    onDocKeyDown (e : KeyboardEvent) {
        if (e.ctrlKey && e.code === 'KeyF') {
            const inputEl = this.searchInputEl.nativeElement || null;

            if (inputEl && !inputEl.matches(':focus')) {
                e.preventDefault();
                inputEl.focus();
            }
        }
    }
}
