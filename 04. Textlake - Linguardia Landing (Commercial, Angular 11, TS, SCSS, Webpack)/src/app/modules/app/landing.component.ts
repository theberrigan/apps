import {
    AfterViewInit,
    Component,
    ElementRef, EventEmitter,
    OnDestroy,
    OnInit,
    Renderer2,
    ViewChild,
    ViewEncapsulation
} from '@angular/core';
import { load as initRecaptcha } from 'recaptcha-v3'
import { CONFIG } from '../../../../config/app/dev';
import {ILang, LANGS, LangService} from '../../services/lang.service';
import {DomService} from '../../services/dom.service';
import {FileLikeObject, FileUploader} from 'ng2-file-upload';
import {LandingService} from '../../services/landing.service';
import {FormBuilder, FormGroup} from '@angular/forms';
import animateScrollTo from 'animated-scroll-to';
import {DeviceService} from '../../services/device.service';

class Attachment {
    public name : string = null;
    public uuid : string = null;
}

@Component({
    selector: 'landing',
    templateUrl: './landing.component.html',
    styleUrls: [ './landing.component.scss' ],
    encapsulation: ViewEncapsulation.None,
    host: {
        'class': 'landing',
    }
})
export class LandingComponent implements OnInit, OnDestroy, AfterViewInit {
    public langs : ILang[] = LANGS;

    public activeLang : string = 'en';

    public isLangMenuActive : boolean = false;

    public isPanelInverted : boolean = false;

    public listeners : any[] = [];

    public form : FormGroup;

    public isFormValid : boolean = false;

    public isSending : boolean = false;

    public recaptchaTokenPromise : Promise<string>;

    public year : number = 2020;

    public isPresigning : boolean = false;

    public isDropzoneOver : boolean = false;

    @ViewChild('uploaderInput')
    public uploaderInputEl : ElementRef;

    public uploader : FileUploader = null;

    public uploadErrors : { args : any, reason : string }[] = [];

    public uploadingProgress : number = 0;

    public uploadQueueSize : number = 0;

    public attachments : Attachment[] = [];

    public svg : SVGElement[] = [];

    public resizeDebounceTimer : any = null;

    constructor (
        public renderer : Renderer2,
        private formBuilder : FormBuilder,
        public deviceService : DeviceService,
        public domService : DomService,
        public langService : LangService,
        public landingService : LandingService
    ) {}

    public ngOnInit () {
        this.year = (new Date()).getFullYear();
        this.activeLang = this.fetchLang();
        this.langService.use(this.activeLang);
        this.addListener(this.renderer.listen('document', 'click', e => this.onDocumentClick(e)));
        this.addListener(this.renderer.listen('window', 'scroll', () => this.onPageScroll()));

        this.form = this.formBuilder.group({
            name: [ '' ],
            companyName: [ '' ],
            email: [ '' ],
            phone: [ '' ],
            translateTo: [ '' ],
            instructions: [ '' ]
        });

        requestAnimationFrame(() => this.onPageScroll());

        this.recaptchaTokenPromise = new Promise(resolve => {
            initRecaptcha(CONFIG.recaptcha.publicKey).then(recaptcha => {
                recaptcha.execute(CONFIG.recaptcha.action).then(token => {
                    resolve(token);
                });
            });
        });

        this.initUploader();
    }

    public ngAfterViewInit () : void {
        setTimeout(() => {
            if (this.deviceService.browser.IE) {
                this.svg = Array.prototype.slice.call(document.querySelectorAll('.svg_mimic-width'));

                if (this.svg.length > 0) {
                    this.addListener(this.renderer.listen('window', 'resize', () => this.resizeSvg()));
                    this.resizeSvg();
                }
            }
        }, 4);
    }

    public ngOnDestroy () {
        this.listeners.forEach(unlisten => unlisten());
    }

    public addListener (listener : any) {
        this.listeners = [ ...this.listeners, listener ];
    }

    public resizeSvg () : void {
        if (this.resizeDebounceTimer !== null) {
            clearTimeout(this.resizeDebounceTimer);
            this.resizeDebounceTimer = null;
        }

        this.resizeDebounceTimer = setTimeout(() => {
            this.svg.forEach(svg => {
                const parent = <HTMLElement>svg.parentNode;
                const parentWidth = parent.clientWidth;

                if (typeof(parentWidth) !== 'number') {
                    return;
                }

                const parentStyle = window.getComputedStyle(parent);
                const svgViewBox = (svg.getAttribute('viewBox') || '').split(' ');

                let currentSvgWidth = null;
                let currentSvgHeight = null;

                if (svgViewBox.length === 4) {
                    [ currentSvgWidth, currentSvgHeight ] = svgViewBox.slice(2).map(num => Math.round(parseFloat(num)));
                } else {
                    const svgRect = svg.getBoundingClientRect();
                    currentSvgWidth = Math.round(svgRect.width);
                    currentSvgHeight = Math.round(svgRect.height);
                }

                const svgWidth = Math.round(Math.max(0, parentWidth - parseFloat(parentStyle.paddingLeft) - parseFloat(parentStyle.paddingRight)));
                const svgHeight = Math.round(svgWidth * (currentSvgHeight / currentSvgWidth));

                console.log(svgWidth, svgHeight);

                svg.setAttribute('width', String(svgWidth));
                svg.setAttribute('height', String(svgHeight));
                svg.setAttribute('preserveAspectRatio', 'none');
            });
        }, 75);
    }

    public onDocumentClick (e : any) : void {
        if (this.domService.hasEventMark(e, 'ltc')) {
            this.isLangMenuActive = !this.isLangMenuActive;
        } else if (this.domService.hasEventMark(e, 'lic') || !this.domService.hasEventMark(e, 'lmc')) {
            this.isLangMenuActive = false;
        }
    }

    public fetchLang () : string {
        const activeLang = window.localStorage.getItem('language');

        if (this.langs.some(lang => lang.code === activeLang)) {
            return activeLang;
        }

        return (this.langs.find(lang => lang.isDefault) || { code: 'en' }).code;
    }

    public saveLang (langCode : string) : void {
        window.localStorage.setItem('language', langCode);
    }

    public onLangTriggerClick (e : any) : void {
        this.domService.markEvent(e, 'ltc');
    }

    public onLangMenuClick (e : any) : void {
        this.domService.markEvent(e, 'lmc');
    }

    public onLangItemClick (langCode : string, e : any) : void {
        this.domService.markEvent(e, 'lic');
        this.activeLang = langCode;
        this.saveLang(langCode);
        this.langService.use(langCode);
    }

    public getScrollTop () : number {
        return window.pageYOffset || document.documentElement.scrollTop || document.body.scrollTop || 0;
    }

    public onPageScroll () : void {
        this.isPanelInverted = this.getScrollTop() >= 50;
    }

    public onAnchorClick (e : any) : void {
        e.preventDefault();

        const href = e.target.getAttribute('href') || '';

        if (href[0] !== '#') {
            return;
        }

        const toEl = document.body.querySelector(href);

        if (!toEl) {
            return;
        }

        if (!toEl.getClientRects().length) {
            return;
        }

        const
            rect = toEl.getBoundingClientRect(),
            scrollTop = window.pageYOffset || document.documentElement.scrollTop || document.body.scrollTop,
            clientTop = document.documentElement.clientTop || document.body.clientTop || 0,
            top = rect.top + scrollTop - clientTop,
            panelHeight = 150;

        animateScrollTo(Math.max(0, top - panelHeight), {
            maxDuration: 250,
            minDuration: 250,
            speed: 250,
        });
    }

    // ----------------------------

    // POST - presign, PUT - upload
    public initUploader () : void {
        this.recaptchaTokenPromise.then(recaptchaToken => {
            this.uploader = new FileUploader({
                maxFileSize: 350 * 1024 * 1024,
                autoUpload: false,     // manual upload
                disableMultipart: true, // switch POST to PUT
                headers: [
                    {
                        name: 'Linguardia-Recaptcha-Token',
                        value: recaptchaToken
                    }
                ]
            });

            // Set PUT method for each file
            this.uploader.onAfterAddingFile = (file : any) => {
                file.method = 'PUT';
            };

            // Reset uploader and presign all files
            this.uploader.onAfterAddingAll = () => {
                this.uploadErrors = [];
                this.uploadingProgress = 0;
                this.isPresigning = true;

                this.presignFiles(this.uploader.queue).then(files => {
                    files.forEach(file => {
                        if (!file.presignData) {
                            file.cancel();  // onErrorItem will be called
                        }
                    });

                    this.uploadQueueSize = this.uploader.queue.length;
                    this.uploader.uploadAll();
                    this.isPresigning = false;
                });
            };

            // Set unique upload url for every file
            this.uploader.onBeforeUploadItem = (file : any) => {
                this.uploader.setOptions({
                    url: file.presignData.url
                });

                file.withCredentials = false;
            };

            // Add file to attachments array if it was uploaded successfully
            this.uploader.onSuccessItem = (file : any) => {
                const attachment = new Attachment();

                attachment.name = file.file.name;
                attachment.uuid = file.presignData.uuid;

                this.attachments.push(attachment);
            };

            // Add error message to array if file uploading failed
            this.uploader.onErrorItem = (file : any) => {
                this.uploadErrors.push({
                    reason: 'common',
                    args: {
                        name: file.file.name
                    }
                });
            };

            // this.uploader.onWhenAddingFileFailed = (item : FileLikeObject, filter: any, options: any) => {
            //     console.log('onWhenAddingFileFailed');
            //     this.uploadErrors.push({
            //         reason: [ 'queueLimit', 'fileSize' ].includes(filter.name) ? filter.name : 'common',
            //         name: item.name
            //     });
            // };

            // Update uploading progress
            this.uploader.onProgressAll = (progress : any) => {
                this.uploadingProgress = 10 + Math.round(progress / 100 * 90);
            };

            // Reset uploader after uploading
            this.uploader.onCompleteAll = () => {
                this.uploadingProgress = 0;
                this.uploader.clearQueue();
            };
        });
    }

    public presignFiles (files : any[]) : Promise<any[]> {
        return new Promise(resolve => {
            const filesCount = files.length;
            let requestsDone = 0;

            this.recaptchaTokenPromise.then(recaptchaToken => {
                files.forEach(file => {
                    this.landingService.presignFile(file.file.name, recaptchaToken).toPromise().then(response => {
                        file.presignData = response;
                    }).catch(() => {
                        file.presignData = null;
                    }).then(() => {
                        requestsDone++;
                        this.uploadingProgress = Math.round(10 / filesCount * requestsDone);

                        if (requestsDone >= filesCount) {
                            resolve(files);
                        }
                    });
                });
            });
        });
    }

    public get isUploading () : boolean {
        return this.isPresigning || this.uploader.isUploading;
    }

    public onDropzoneClick () : void {
        if (this.isUploading || !this.uploaderInputEl) {
            return;
        }

        this.uploaderInputEl.nativeElement.click();
    }

    public onDropzoneOver (isDropzoneOver : boolean) : void {
        this.isDropzoneOver = isDropzoneOver;
    }

    public onDeleteAttachment (attachment : Attachment) : void {
        if (this.isSending) {
            return;
        }

        this.attachments.splice(this.attachments.indexOf(attachment), 1);
    }

    public validate () : void {
        setTimeout(() => {
            const formValue = this.form.getRawValue();
            const { name, email, phone, translateTo } = formValue;
            this.isFormValid = (
                name.trim().length > 0 &&
                translateTo.trim().length > 0 &&
                (
                    email.trim().length > 0 ||
                    phone.trim().length > 0
                )
            );
        }, 4);
    }

    public onSubmit () : void {
        if (this.isSending || !this.isFormValid) {
            return;
        }

        this.isSending = true;

        const formValue = this.form.getRawValue();

        Object.keys(formValue).forEach(key => {
            formValue[key] = formValue[key].trim();
        });

        formValue.instructions = (
            `Name: ${ formValue.name } 
            Company Name: ${ formValue.companyName } 
            Email: ${ formValue.email } 
            Phone: ${ formValue.phone } 
            Translate to: ${ formValue.translateTo } 
            
            Instructions:
            ${ formValue.instructions }`
        );

        formValue.origin = location.href;
        formValue.attachments = this.attachments;

        this.recaptchaTokenPromise.then(recaptchaToken => {
            this.landingService.sendRequest(formValue, recaptchaToken).toPromise().then(() => {
                this.form.reset();
                this.attachments = [];
                this.isFormValid = false;
                this.uploadErrors = [];
                alert(this.langService.translate('form.ok'));
            }).catch(() => {
                alert(this.langService.translate('form.error'));
            }).then(() => {
                this.isSending = false;
            });
        });
    }
}
