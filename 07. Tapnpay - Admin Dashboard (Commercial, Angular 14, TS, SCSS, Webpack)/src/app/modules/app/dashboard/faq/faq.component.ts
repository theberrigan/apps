import {
    ChangeDetectionStrategy,
    Component, ElementRef, HostListener, Input,
    OnDestroy,
    OnInit, ViewChild,
    ViewEncapsulation
} from '@angular/core';
import {Subscription} from 'rxjs';
import {TitleService} from '../../../../services/title.service';
import {FaqService} from '../../../../services/faq.service';
import {ToastService} from '../../../../services/toast.service';


@Component({
    selector: 'faq',
    templateUrl: './faq.component.html',
    styleUrls: [ './faq.component.scss' ],
    changeDetection: ChangeDetectionStrategy.Default,
    encapsulation: ViewEncapsulation.None,
    host: {
        'class': 'faq'
    },
})
export class FAQComponent implements OnInit, OnDestroy {
    subs : Subscription[] = [];

    isDropzoneVisible : boolean = false;

    isUploading : boolean = false;

    @ViewChild('uploadForm')
    uploadForm : ElementRef;

    @ViewChild('uploadInput')
    uploadInput : ElementRef;

    constructor (
        private titleService : TitleService,
        private toastService : ToastService,
        private faqService : FaqService,
    ) {
        this.titleService.setTitle('faq.page_title');
    }

    ngOnInit () : void {

    }

    ngOnDestroy () : void {
        this.subs.forEach(sub => sub.unsubscribe());
    }

    @HostListener('document:dragenter', [ '$event' ])
    onDocDragEnter (e : DragEvent) {
        e.stopPropagation();
        e.preventDefault();

        if (this.isUploading) {
            return;
        }

        const items : DataTransferItem[] = Array.from(e.dataTransfer.items || []);

        if (items.some(item => item.kind === 'file') === false) {
            return;
        }

        this.isDropzoneVisible = true;
    }

    onDropzoneDragOver (e) {
        e.stopPropagation();
        e.preventDefault();
        // set dropEffect to 'copy' to fire 'drop' event later
        e.dataTransfer.dropEffect = 'copy';
    }

    onDropzoneDragEnter (e) {
        e.stopPropagation();
        e.preventDefault();
    }

    onDropzoneDragLeave (e) {
        e.stopPropagation();
        e.preventDefault();

        this.isDropzoneVisible = false;
    }

    onFileDrop (e) {
        if (this.isUploading) {
            return;
        }

        e.stopPropagation();
        e.preventDefault();

        this.isDropzoneVisible = false;

        const file : File  = (e?.dataTransfer?.files || [])[0];
        this.uploadFile(file);
    }

    onFileChange () {
        const file : File  = (this.uploadInput?.nativeElement?.files || [])[0];
        this.uploadForm?.nativeElement?.reset();
        this.uploadFile(file);
    }

    async uploadFile (file : File) {
        if (this.isUploading || !file) {
            return;
        }

        this.isUploading = true;

        const isOk = await this.faqService.uploadFile(file).toPromise().catch(() => false);

        this.isUploading = false;

        this.toastService.create({
            message: [ isOk ? 'faq.upload_success' : 'faq.upload_error' ],
            timeout: 5000
        });
    }

    onDecoDropzoneClick () {
        if (this.isUploading) {
            return;
        }

        this.uploadInput.nativeElement?.click();
    }

    /*
    async init () {
        const response = await this.faqService.fetchFAQ().toPromise().catch(() => null);

        if (response) {
            const data = this.parseFaqXml(response);

            console.log(data);
        }
    }

    parseFaqXml (data : string) : any {
        const getElements = (el : Element, selector : string) : Element[] => {
            return Array.from(el.querySelectorAll(selector));
        }

        const getAttr = (el : Element, attr : string, toLowerCase : boolean = false) : string => {
            const value = (el.getAttribute(attr) || '').trim();
            return toLowerCase ? value.toLowerCase() : value;
        };

        const getText = (el : Element, toLowerCase : boolean = false) : string => {
            const text = (el.textContent || '').trim();
            return toLowerCase ? text.toLowerCase() : text;
        };

        const dom = new DOMParser().parseFromString(data, 'application/xml');
        const faqEl = dom.querySelector('faq');

        if (dom.querySelector('parsererror') || !faqEl) {
            console.warn('Failed to parse xml:', dom);
            return null;
        }

        return {
            languages: getElements(faqEl, ':scope > languages > language').map(langEl => ({
                code: getAttr(langEl, 'code', true),
                name: getText(langEl),
            })),
            categories: getElements(faqEl, ':scope > categories > category').map(catEl => ({
                names: getElements(catEl, ':scope > name > content').map(contEl => ({
                    langCode: getAttr(contEl, 'lang-code', true),
                    name: getText(contEl),
                })),
                questions: getElements(catEl, ':scope > question-answers > question-answer').map(qaEl => ({
                    questionId: getAttr(qaEl, 'id', true),
                    question: getElements(qaEl, ':scope > question > content').map(contEl => ({
                        langCode: getAttr(contEl, 'lang-code', true),
                        content: getText(contEl),
                    })),
                    answer: getElements(qaEl, ':scope > answer > content').map(contEl => ({
                        langCode: getAttr(contEl, 'lang-code', true),
                        content: getText(contEl),
                    }))
                }))
            }))
        };
    }*/
}
