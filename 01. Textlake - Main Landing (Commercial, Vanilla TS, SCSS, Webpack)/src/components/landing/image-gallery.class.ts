import {bindMethods, fancybox} from '../../js/utils';
import {LanguageManager} from './language-manager.class';
import {DOM} from './ui.class';
const config = require('../../config/config.json');

export class ImageGallery {
    public static get deps () : any {
        return {
            langManager: LanguageManager,
            dom: DOM
        };
    }

    public langManager : LanguageManager = null;

    public dom : DOM = null;

    private images : any = null;

    private active : any = null;

    public constructor () {
        bindMethods(this);
    }

    public init () : void {
        this.images = {
            all: [],
            gallery: []
        };

        const
            nestEl = document.body.querySelector('.section-screenshots__screenshots'),
            selectorEl = document.body.querySelector('.section-screenshots__dots');

        let galleryIndex : number = 0;

        [
            'standalone',
            'gallery'
        ].forEach(type => {
            config.images[type].forEach(image => {
                image.url = require(`../../images/${ image.url }`);
                image.id = image.id || null;
                image.caption = image.caption || '';
                image.galleryItem = {
                    src: image.url,
                    type: 'image',
                    opts: {}
                };

                if (image.isGallery = (type === 'gallery')) {
                    const anchorEl = document.createElement('a');

                    anchorEl.href = image.url;
                    anchorEl.style.backgroundImage = `url('${ image.url }')`;
                    anchorEl.className = 'section-screenshots__screenshot';

                    const dotEl = document.createElement('button');
                    dotEl.type = 'button';
                    dotEl.className = 'section-screenshots__dot';

                    image.anchorEl = anchorEl;
                    image.dotEl = dotEl;

                    nestEl.appendChild(anchorEl);
                    selectorEl.appendChild(dotEl);

                    Object.defineProperty(dotEl, '__image', { value: image, configurable: true });
                    Object.defineProperty(anchorEl, '__galleryIndex', { value: galleryIndex++, configurable: true });

                    this.images.gallery.push(image.galleryItem);
                }

                this.images.all.push(image);
            });
        });

        this.langManager.onLanguageChanged(this.localizeCaptions);
        this.localizeCaptions();

        this.switchImage(this.images.all.find(image => image.isGallery));

        this.dom.delegate(selectorEl, 'click', '.section-screenshots__dot', e => this.switchImage(e.target.__image));
        this.dom.delegate(nestEl, 'click', '.section-screenshots__screenshot', e => {
            e.preventDefault();
            this.showGallery(e.target.__galleryIndex);
        });

        // Fancybox

        fancybox.defaults.loop = true;
        fancybox.defaults.buttons = [ 'zoom', 'close' ];
        fancybox.defaults.animationEffect = 'zoom-in-out';
        fancybox.defaults.animationDuration = 250;
        fancybox.defaults.hash = false;
        fancybox.defaults.idleTime = 0;
        fancybox.defaults.preventCaptionOverlap = true;
        fancybox.defaults.transitionEffect = 'tube';
        fancybox.defaults.i18n.en = {
            CLOSE: '',
            NEXT: '',
            PREV: '',
            ERROR: '',
            PLAY_START: '',
            PLAY_STOP: '',
            FULL_SCREEN: '',
            THUMBS: '',
            DOWNLOAD: '',
            SHARE: '',
            ZOOM: ''
        };
    }

    private localizeCaptions () : void {
        this.images.all.forEach(image => {
            image.galleryItem.opts.caption = this.langManager.translatePrefixed(image.caption || '');
        });
    }

    private switchImage (switchTo : any) : void {
        if (!switchTo || this.active === switchTo) {
            return;
        }

        if (this.active) {
            this.active.anchorEl.classList.remove('section-screenshots__screenshot_current');
            this.active.dotEl.classList.remove('section-screenshots__dot_current');
        }

        switchTo.anchorEl.classList.add('section-screenshots__screenshot_current');
        switchTo.dotEl.classList.add('section-screenshots__dot_current');

        this.active = switchTo;
    }

    public showImage (imageId : string) : void {
        const image = this.images.all.find(image => image.id === imageId);

        if (image) {
            fancybox.open(image.galleryItem);
        }
    }

    public showGallery (startIndex : number = 0) : void {
        fancybox.open(this.images.gallery, {}, startIndex);
    }
}

enum LoadingState {
    CREATED,
    LOADING,
    READY,
    ERROR
}

class ImageItem {    
    private readonly url : string = null;
    
    private readonly id : string = null;
    
    private readonly originalCaption : string = null;
    
    private readonly translatedCaption : string = null;

    public imgEl : HTMLImageElement = null;
    
    public itemEl : HTMLDivElement = null;

    public spinnerEl : HTMLDivElement = null;

    public state : LoadingState = null;

    public whRatio : number = 0;

    public hwRatio : number = 0;

    public offsetX : number = 0;

    public nextImage : ImageItem = null;

    public prevImage : ImageItem = null;

    public subscription : any = null;

    public isVisible : boolean = false;

    // -----------

    public currentWidth : number = 0;

    public currentHeight : number = 0;

    public width : number = 0;  // img.naturalWidth

    public height : number = 0;  // img.naturalHeight

    public left : number = 0;

    public baseTranslateX : number = 0;

    public scale : number = 1;
    
    constructor (options : any) {
        bindMethods(this);

        this.url = require(`../../images/${ options.url }`);
        this.id = options.id || null;
        this.originalCaption = options.caption || '';
        this.translatedCaption = null;
        this.state = LoadingState.CREATED;

        this.imgEl = document.createElement('img');  // TODO: IEWIN ? new Image() : document.createElement('img');
        
        this.itemEl = document.createElement('div');
        this.itemEl.className = 'gallery__image';

        this.spinnerEl = document.createElement('div');
        this.spinnerEl.className = 'gallery__spinner';

        this.itemEl.appendChild(this.imgEl);
        this.itemEl.appendChild(this.spinnerEl);
    }

    public load (callback : any) : void {  // TODO: loading progress
        // These two final states won't change. Just return.
        if (this.state === LoadingState.READY || this.state === LoadingState.ERROR) {
            return;
        }

        this.subscription = callback;

        if (this.state === LoadingState.CREATED) {
            this.state = LoadingState.LOADING;

            this.imgEl.addEventListener('load', () => {
                this.width = this.imgEl.naturalWidth;
                this.height = this.imgEl.naturalHeight;

                this.whRatio = this.width / this.height;
                this.hwRatio = this.height / this.width;

                this.state = LoadingState.READY;
                this.subscription && this.subscription(this);
                this.subscription = null;
            });

            this.imgEl.addEventListener('error', () => {
                this.state = LoadingState.ERROR;
                this.subscription && this.subscription(this);
                this.subscription = null;
            });

            this.imgEl.src = this.url;
        }
    }

    public unsubscribe () : void {
        this.subscription = null;
    }
}

/*
var transitionEnd = (function() {
    var el = document.createElement("fakeelement"),
        t;

    var transitions = {
        transition: "transitionend",
        OTransition: "oTransitionEnd",
        MozTransition: "transitionend",
        WebkitTransition: "webkitTransitionEnd"
    };

    for (t in transitions) {
        if (el.style[t] !== undefined) {
            return transitions[t];
        }
    }

    return "transitionend";
})();
*/

/*
<div class="gallery">
    <div class="gallery__bg"></div>
    <div class="gallery__images"></div>
    <div class="gallery__caption-wrap">
        <div class="gallery__caption"></div>
    </div>
    <div class="gallery__counter">
        <span class="gallery__counter-current"></span>/<span class="gallery__counter-total"></span>
    </div>
    <div class="gallery__screen"></div>
    <button type="button" class="gallery__button gallery__button_prev">prev</button>
    <button type="button" class="gallery__button gallery__button_next">next</button>
    <button type="button" class="gallery__button gallery__button_close">close</button>
</div>

export class ImageGallery2 {
    public static get deps () : any {
        return {
            langManager: LanguageManager,
            dom: DOM
        };
    }

    public langManager : LanguageManager = null;

    public dom : DOM = null;

    private timeline : TimelineLite = null;

    private images : any = {};

    private state : any = null;
    
    private el : any = null;

    private isZoomed : boolean = false;

    private hammer : Hammer = null;

    private globalListeners : any[] = null;

    private isPopupVisible : boolean = false;

    private isAnimating : boolean = false;

    private redrawAfterAnimation : boolean = false;

    private isReady : boolean = false;

    private deltaX : number = 0;

    private deltaY : number = 0;

    private detectedGesture : string = '';

    // ---------------



    public constructor () {
        bindMethods(this);
    }

    public init () : void {
        this.timeline = new TimelineLite();

        this.prepareImages();

        this.globalListeners = [
            {
                el: window,
                event: 'resize',
                listener: () => requestAnimationFrame(this.onResize)
            }
        ];

        const galleryEl = document.querySelector('.gallery');

        this.el = {
            gallery: galleryEl,
            images: galleryEl.querySelector('.gallery__images'),
            screen: galleryEl.querySelector('.gallery__screen'),
            counter: galleryEl.querySelector('.gallery__counter'),
            caption: galleryEl.querySelector('.gallery__caption'),
            counterCurrent: galleryEl.querySelector('.gallery__counter-current'),
            counterTotal: galleryEl.querySelector('.gallery__counter-total'),
            buttonPrev: galleryEl.querySelector('.gallery__button_prev'),
            buttonNext: galleryEl.querySelector('.gallery__button_next'),
            buttonClose: galleryEl.querySelector('.gallery__button_close'),
        };

        this.mountInternalListeners();

        // tmp
        this.showGallery();
    }

    private prepareImages () : void {
        [
            'standalone',
            'gallery'
        ].forEach(type => {
            this.images[type] = config.images[type].map(image => {
                return new ImageItem({
                    url: image.url,
                    id: image.id,
                    caption: image.caption
                });
            });
        });

        let maxGalleryIndex = this.images.gallery.length - 1;

        if (maxGalleryIndex > 0) {
            for (let i = 0; i <= maxGalleryIndex; i++) {
                const image = this.images.gallery[i];
                image.prevImage = this.images.gallery[ i === 0 ? maxGalleryIndex : (i - 1) ];
                image.nextImage = this.images.gallery[ i === maxGalleryIndex ? 0 : (i + 1) ];
            }
        }
    }

    private mountInternalListeners () : void {
        // this.hammer.set({ enable: false });
        this.hammer = new Hammer(this.el.screen, {
            recognizers: [
                [ Hammer.Pinch, { enable: true } ],
                [ Hammer.Pan,   { direction: Hammer.DIRECTION_ALL } ],
                [ Hammer.Swipe, { direction: Hammer.DIRECTION_ALL }, [ 'pan' ] ],
                [ Hammer.Tap ],
                [ Hammer.Tap,   { event: 'doubletap', taps: 2 }, [ 'tap' ] ],
            ]
        });

        this.hammer.on([
            'pinch',
            'tap', 'doubletap',
            'pan', 'panend',
            'swipeleft', 'swiperight', 'swipeup', 'swipedown'
        ].join(' '), (e) => {
            this.timeline.clear();

            if (!this.detectedGesture) {
                if (e.type === 'pan') {
                    this.detectedGesture = Math.abs(e.deltaX) > Math.abs(e.deltaY) ? 'panX' : 'panY';
                }
            }

            if (e.type === 'pan') {
                if (this.detectedGesture === 'panX') {
                    requestAnimationFrame(() => {
                        this.deltaX = e.deltaX;
                        this.redrawSlider();
                    });
                } else if (this.detectedGesture === 'panY') {
                    requestAnimationFrame(() => {
                        this.deltaY = e.deltaY;
                        this.redrawSlider();
                    });
                }
            }

            if (e.type === 'panend') {
                if (this.detectedGesture === 'panX') {
                    this.timeline
                        .to(this, 0.5, {
                            deltaX: 0,
                            ease: Power2.easeOut,
                            onUpdate: () => {
                                this.redrawSlider();
                            },
                            onComplete: () => {

                            }
                        });
                } else if (this.detectedGesture === 'panY') {
                    this.timeline
                        .to(this, 0.5, {
                            deltaY: 0,
                            ease: Power2.easeOut,
                            onUpdate: () => {
                                this.redrawSlider();
                            },
                            onComplete: () => {

                            }
                        });
                }

                this.detectedGesture = '';
            }

            // console.log(e.type);
            // if (e.type === 'tap') {
            //     const __curImg = this.state.current;
            //     const currentImageRect = __curImg.itemEl.getBoundingClientRect();
            //     // const screenRect = this.el.screen.getBoundingClientRect();
            //
            //     if (
            //         e.center.x < currentImageRect.left ||
            //         e.center.x > currentImageRect.right ||
            //         e.center.y < currentImageRect.top ||
            //         e.center.y > currentImageRect.bottom
            //     ) {
            //         console.log('outside');
            //     } else {
            //         console.log('inside');
            //
            //         if (this.isZoomed) {
            //             __curImg.itemEl.style.transform = `scale(1, 1)`;
            //         } else {
            //             const scale = __curImg.imgEl.naturalWidth / __curImg.imgEl.width;
            //             __curImg.itemEl.style.transformOrigin = `${ e.center.x - currentImageRect.left }px ${ e.center.y - currentImageRect.top }px`;
            //             __curImg.itemEl.style.transform = `scale(${ scale }, ${ scale })`;
            //         }
            //
            //         this.isZoomed = !this.isZoomed;
            //     }
            // }
            //
            // console.log(e.type, e);
        });

        this.el.buttonPrev.addEventListener('click', this.prevImage);
        this.el.buttonNext.addEventListener('click', this.nextImage);
        this.el.buttonClose.addEventListener('click', this.closePopup);
        // Hammer.on(document.documentElement, 'mouseup', (e) => {
        //     this.detectedGesture = '';
        //     // move back or forward
        // });
        // this.el.images.addEventListener(transitionEnd, (e) => {
        //     if (e.target === this.el.images) {
        //         this.onAfterAnimation();
        //     }
        // });
    }

    private mountGlobalListeners () : void {
        this.globalListeners.forEach(item => {
            item.el.addEventListener(item.event, item.listener);
        });
    }

    private unmountGlobalListeners () : void {
        this.globalListeners.forEach(item => {
            item.el.removeEventListener(item.event, item.listener);
        });
    }

    private onResize () : void {
        const
            currentImage : ImageItem = this.state.current,
            prevImage : ImageItem = this.state.current.prevImage,
            nextImage : ImageItem = this.state.current.nextImage,
            contRect = this.el.images.getBoundingClientRect(),
            maxWidth = contRect.width - 15 * 2,
            maxHeight = contRect.height - 15 * 2;

        // let currentLeft;

        [
            currentImage,
            prevImage,
            nextImage
        ].forEach(image => {
            let height, width;

            if (image.state === LoadingState.READY) {
                image.currentHeight = height = Math.min(image.height, maxHeight, Math.min(image.width, maxWidth) * image.hwRatio);
                image.currentWidth = width = height * image.whRatio;
            } else {
                // TODO: show loaded image
                // TODO: show failed image
                image.currentHeight = image.currentWidth = width = height = Math.min(maxHeight, maxWidth);
            }

            const left = (contRect.width - width) / 2;

            image.itemEl.style.height = height + 'px';
            image.itemEl.style.width = width + 'px';
            image.itemEl.style.top = (contRect.height - height) / 2 + 'px';
            image.itemEl.style.left = left + 'px';

            // if (image === currentImage) {
            //     currentLeft = left;
            //     image.baseTranslateX = 0;
            // } else if (image) {
            //     if (image === prevImage) {
            //         image.baseTranslateX = currentLeft - left - width;
            //         // image.itemEl.style.transform = `translateX(${ currentLeft - left - width }px)`;
            //     } else if (image === nextImage) {
            //         image.baseTranslateX = left - currentLeft + width;
            //         // image.itemEl.style.transform = `translateX(${ left - currentLeft + width }px)`;
            //     }
            // }
        });

        this.redrawSlider();
    }

    // TODO: split resize and redraw fns
    public redrawSlider () : void {
        const
            currentImage : ImageItem = this.state.current,
            prevImage : ImageItem = this.state.current.prevImage,
            nextImage : ImageItem = this.state.current.nextImage;

        currentImage.itemEl.style.transform = `translate(${ currentImage.baseTranslateX + this.deltaX }px, ${ this.deltaY }px)`;
        prevImage.itemEl.style.transform = `translateX(${ prevImage.baseTranslateX }px) scale(0.5, 0.5)`;
        nextImage.itemEl.style.transform = `translateX(${ nextImage.baseTranslateX }px) scale(0.5, 0.5)`;

        if (this.deltaX) {
            if (Math.abs(this.deltaX) < 50) {
                currentImage.itemEl.style.opacity = '1';
                prevImage.itemEl.style.opacity = nextImage.itemEl.style.opacity = '0';
                prevImage.itemEl.style.transform = `translateX(${ prevImage.baseTranslateX }px) scale(0.5, 0.5)`;
                nextImage.itemEl.style.transform = `translateX(${ nextImage.baseTranslateX }px) scale(0.5, 0.5)`;
                return;
            }

            const threshold : number = (currentImage.currentWidth + (this.deltaX < 0 ? nextImage : prevImage).currentWidth) / 2 - 50 * 2;
            const ratio = 1 / threshold * Math.min(threshold, Math.max(0, Math.abs(this.deltaX) - 50));

           // currentImage.itemEl.style.opacity = String(1 - ratio);

            if (this.deltaX < 0) {
                nextImage.itemEl.style.opacity = String(ratio);
                nextImage.itemEl.style.transform = `translateX(${ nextImage.baseTranslateX }px) scale(${ ratio }, ${ ratio })`;

                prevImage.itemEl.style.opacity = '0';
            } else {
                prevImage.itemEl.style.opacity = String(ratio);
                prevImage.itemEl.style.transform = `translateX(${ prevImage.baseTranslateX }px) scale(${ ratio }, ${ ratio })`;

                nextImage.itemEl.style.opacity = '0';
            }
        }
    }

    // private animate () : void {
    //     // if (this.isAnimating) {
    //     //     this.timeline.clear();
    //     //     this.onAfterAnimation();
    //     // }
    //
    //     this.isAnimating = true;
    //     this.el.images.style.transform = `translateX(${ this.state.current.offsetX }px)`;
    //
    //     // this.timeline
    //     //     .to(this.el.images, 0.5, {
    //     //         x: this.state.current.offsetX,
    //     //         ease: Power2.easeOut,
    //     //         onComplete: () => {
    //     //             this.onAfterAnimation();
    //     //             this.isAnimating = false;
    //     //         }
    //     //     });
    // }
    //
    // private onAfterAnimation () : void {
    //     if (this.redrawAfterAnimation) {
    //         this.redrawSlider();
    //         this.redrawAfterAnimation = false;
    //     }
    //
    //     this.isAnimating = false;
    // }

    private redrawCounter () : void {
        if (this.state) {
            this.el.counterCurrent.textContent = String(this.state.images.indexOf(this.state.current) + 1);
            this.el.counterTotal.textContent = String(this.state.images.length);
        } else {
            this.el.counterCurrent.textContent = '0';
            this.el.counterTotal.textContent = '0';
        }
    }

    private redrawCaption () : void {
        this.el.caption.innerHTML = this.state && this.state.current.translatedCaption || '';
    }

    private prevImage () : void {
        if (this.state.current && this.state.current.prevImage) {
            this.switchImage(this.state.current.prevImage);
            this.redrawSlider();
        }
    }

    private nextImage () : void {
        if (this.state.current && this.state.current.nextImage) {
            this.switchImage(this.state.current.nextImage);
            this.redrawSlider();
        }
    }

    public switchImage (imageToShow? : ImageItem) : void {
        if (this.state.current) {
            this.state.current.itemEl.classList.remove('gallery__image_current');
            this.state.current.isVisible = false;
        }

        this.state.current = imageToShow || this.state.images[0];
        this.state.current.itemEl.classList.add('gallery__image_current');
        this.state.current.isVisible = true;

        this.redrawCounter();
        this.redrawCaption();
    }

    // index - id | index
    public showGallery (index? : string | number) : void {
        this.state = {
            isGallery: true,
            images: this.images.gallery
        };

        let imageToShow = null;

        if (typeof(index) === 'number') {
            imageToShow = this.state.images[index];
        } else if(typeof(index) === 'string') {
            imageToShow = this.state.images.find(image  => image.id === index);
        }

        this.switchImage(imageToShow);
        this.showPopup();
    }

    public showStandalone (imageId : string) : void {
        const image = this.images.standalone.find(image => image.id === imageId);

        if (!image) {
            return;
        }

        this.state = {
            isGallery: false,
            images: [ image ]
        };

        this.switchImage();
        this.showPopup();
    }

    private showPopup () : void {
        if (this.state.images.length <= 1) {
            this.el.buttonPrev.classList.add('click', 'gallery__button_hidden');
            this.el.buttonNext.classList.add('click', 'gallery__button_hidden');
            this.el.counter.classList.add('click', 'gallery__counter_hidden');
        } else {
            this.el.buttonPrev.classList.remove('click', 'gallery__button_hidden');
            this.el.buttonNext.classList.remove('click', 'gallery__button_hidden');
            this.el.counter.classList.remove('click', 'gallery__counter_hidden');
        }

        this.state.images.forEach(image => {
            image.translatedCaption = this.langManager.translatePrefixed(image.originalCaption || '');
            image.load(() => {
                requestAnimationFrame(() => {
                    this.onResize();
                });
            });
            this.el.images.appendChild(image.itemEl);
        });

        this.dom.setScrollState(false);

        this.el.gallery.classList.add('gallery_visible');

        requestAnimationFrame(() => {
            this.onResize();
            this.mountGlobalListeners();
        });
    }

    private closePopup () : void {
        this.el.gallery.classList.remove('gallery_visible');

        this.state.images.forEach((image : ImageItem) => {
            image.unsubscribe();
            image.isVisible = false;
            this.el.images.removeChild(image.itemEl);
        });

        this.state = null;
        this.unmountGlobalListeners();
        this.redrawCounter();
        this.redrawCaption();
        this.dom.setScrollState(true);
        this.isPopupVisible = false;
    }

    // const baseOffset = {
    //     x: -Math.round(img.width / 2),
    //     y: -Math.round(img.height / 2),
    // };
    //
    // image.style.width = `${ img.width }px`;
    // image.style.height = `${ img.height }px`;
    //
    // image.appendChild(img);
    // this.el.images.appendChild(image);
    //
    // let isZoomed = false;
    //
    // const getScale = () => {
    //     if (isZoomed) {
    //         return 1;
    //     }
    //
    //     const contRect = this.el.images.getBoundingClientRect();
    //
    //     return Math.min(
    //         1,
    //         contRect.width / img.width,
    //         contRect.height / img.height
    //     );
    // };
    //
    // const transform = {
    //     x: baseOffset.x,
    //     y: baseOffset.y,
    //     scale: 1
    // };
    //
    // const updateTransform = () => {
    //     requestAnimationFrame(() => {
    //         image.style.transform = `translate(${ transform.x }px, ${ transform.y }px)`;
    //     });
    // };
    //
    // const resize = () => {
    //     transform.scale = getScale();
    //     updateTransform();
    // };
    //
    // window.addEventListener('resize', resize);
    // resize();
    //
    // // MOVE
    // let isDown = false;
    // let start = null;
    // let isMoved = false;
    //
    // this.el.images.addEventListener('mousedown', (e : MouseEvent) => {
    //     start = [ e.clientX, e.clientY, now() ];
    //     console.log(e.type);
    //     isDown = true;
    // });
    //
    // document.documentElement.addEventListener('mouseup', (e) => {
    //     if (isMoved) {
    //         // Сдвигать без зума можно до какого-то предела Х.
    //         // Если предела достигнут, то даже если человек не отпустил палец, выполнить действие.
    //
    //         transform.x = baseOffset.x;
    //         transform.y = baseOffset.y;
    //         updateTransform();
    //     } else {
    //         const
    //             diffX = e.clientX - start[0],
    //             diffY = e.clientY - start[1],
    //             diffTime = now() - start[2];
    //
    //         console.log(diffX, diffY, diffTime);
    //
    //         // Move
    //         if (Math.abs(diffX) > 35 || Math.abs(diffY) > 35) {
    //             if (isZoomed) {
    //                 // return to base position
    //             } else {
    //                 // return to center, or next/prev image, or close
    //             }
    //
    //             // Click -> zoom
    //         } else if (diffTime < 150) {
    //             requestAnimationFrame(() => {
    //                 isZoomed = !isZoomed;
    //                 transform.scale = getScale();
    //                 updateTransform();
    //             });
    //         }
    //     }
    //
    //     console.log(e.type);
    //     moveAxis = null;
    //     isMoved = false;
    //     isDown = false;
    //     start = null;
    // });
    //
    // let moveAxis = null;
    // let moveBound : any = {};
    //
    // this.el.images.addEventListener('mousemove', (e : MouseEvent) => {
    //     if (!isDown) {
    //         return;
    //     }
    //
    //     if (isZoomed) {
    //         const
    //             diffX = e.clientX - start[0],
    //             diffY = e.clientY - start[1];
    //
    //         if (Math.abs(diffX) > 10 || Math.abs(diffY) > 10) {
    //             isMoved = true;
    //             transform.x = baseOffset.x + diffX;
    //             transform.y = baseOffset.y + diffY;
    //             updateTransform();
    //         }
    //     } else {
    //         const
    //             diffX = e.clientX - start[0],
    //             diffY = e.clientY - start[1];
    //
    //         if (moveAxis === 'x') {
    //             isMoved = true;
    //             const offset = baseOffset.x + diffX;
    //             if (offset >= moveBound.min && offset <= moveBound.max) {
    //                 transform.x = offset;
    //                 updateTransform();
    //             }
    //         } else if (moveAxis === 'y') {
    //             isMoved = true;
    //             transform.y = baseOffset.y + diffY;
    //             updateTransform();
    //         } else if (Math.abs(diffX) > 10 && Math.abs(diffX) > Math.abs(diffY)) {
    //             moveAxis = 'x';
    //             moveBound.min = baseOffset.x - 100;
    //             moveBound.max = baseOffset.x + 100;
    //         } else if (Math.abs(diffY) > 10 && Math.abs(diffY) > Math.abs(diffX)) {
    //             moveAxis = 'y';
    //         }
    //     }
    // });
}
*/