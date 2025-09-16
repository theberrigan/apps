import {Bootstrap} from './bootstrap.class';
import { TimelineLite, Elastic, Power0, Power1, Power2 } from 'gsap/all';
import {bindMethods, getScrollTop} from '../../js/utils';


export class Workflow {
    public static get deps () : any {
        return { bootstrap: Bootstrap };
    }

    private el : any = null;

    private timeline : TimelineLite = null;

    private maskLength : number = null;

    private isAnimated : boolean = false;

    public bootstrap : Bootstrap = null;

    constructor () {
        bindMethods(this);
    }

    public init () : void {
        this.timeline = new TimelineLite();

        const
            wrapEl = document.body.querySelector('.section-scheme__scheme-wrap'),
            schemeEl = wrapEl.querySelector('.scheme');

        this.el = {
            wrap: wrapEl,
            scheme: schemeEl,

            mask: schemeEl.querySelector('.scheme__pathway_mask'),

            dotBg1: schemeEl.querySelector('.scheme__dot-bg_1'),
            dotBg2: schemeEl.querySelector('.scheme__dot-bg_2'),
            dotBg3: schemeEl.querySelector('.scheme__dot-bg_3'),
            dotBg4: schemeEl.querySelector('.scheme__dot-bg_4'),
            dotBg5: schemeEl.querySelector('.scheme__dot-bg_5'),
            dotBg6: schemeEl.querySelector('.scheme__dot-bg_6'),

            dotFg1: schemeEl.querySelector('.scheme__dot-fg_1'),
            dotFg2: schemeEl.querySelector('.scheme__dot-fg_2'),
            dotFg3: schemeEl.querySelector('.scheme__dot-fg_3'),
            dotFg4: schemeEl.querySelector('.scheme__dot-fg_4'),
            dotFg5: schemeEl.querySelector('.scheme__dot-fg_5'),
            dotFg6: schemeEl.querySelector('.scheme__dot-fg_6'),

            step1text: wrapEl.querySelector('.scheme-text__step_1'),
            step2text: wrapEl.querySelector('.scheme-text__step_2'),
            step3text: wrapEl.querySelector('.scheme-text__step_3'),
            step4text: wrapEl.querySelector('.scheme-text__step_4'),
            step5text: wrapEl.querySelector('.scheme-text__step_5'),
            step6text: wrapEl.querySelector('.scheme-text__step_6'),

            step1: schemeEl.querySelector('.scheme__step_1'),
            step1mark1: schemeEl.querySelector('.scheme__step-1-mark-1'),
            step1mark2: schemeEl.querySelector('.scheme__step-1-mark-2'),
            step1mark3: schemeEl.querySelector('.scheme__step-1-mark-3'),
            step1line1: schemeEl.querySelector('.scheme__step-1-line-1'),
            step1line2: schemeEl.querySelector('.scheme__step-1-line-2'),
            step1line3: schemeEl.querySelector('.scheme__step-1-line-3'),

            step2: schemeEl.querySelector('.scheme__step_2'),
            step2list: schemeEl.querySelector('.scheme__step-2-list'),

            step3: schemeEl.querySelector('.scheme__step_3'),

            step4man1: schemeEl.querySelector('.scheme__step-4-man-1'),
            step4man2: schemeEl.querySelector('.scheme__step-4-man-2'),
            step4man3: schemeEl.querySelector('.scheme__step-4-man-3'),
            step4man4: schemeEl.querySelector('.scheme__step-4-man-4'),
            step4loupe: schemeEl.querySelector('.scheme__step-4-loupe'),

            step5: schemeEl.querySelector('.scheme__step_5'),
            step5arrows: schemeEl.querySelector('.scheme__step-5-arrows'),
            step5lang1: schemeEl.querySelector('.scheme__step-5-lang-1'),
            step5lang2: schemeEl.querySelector('.scheme__step-5-lang-2'),

            step6: schemeEl.querySelector('.scheme__step_6'),
            step6letter: schemeEl.querySelector('.scheme__step-6-letter')
        };

        this.maskLength = this.el.mask.getTotalLength && this.el.mask.getTotalLength() || 2945.770263671875;

        this.timeline
            // Hide wrap
            .set(wrapEl, { opacity: 0 })

            // Pathway mask
            .set(this.el.mask, { strokeDasharray: `${ this.maskLength }px`, strokeDashoffset: `${ this.maskLength }px` })

            // Dots
            .set([
                this.el.dotBg1, this.el.dotBg2, this.el.dotBg3, this.el.dotBg4, this.el.dotBg5, this.el.dotBg6,
                this.el.dotFg1, this.el.dotFg2, this.el.dotFg3, this.el.dotFg4, this.el.dotFg5, this.el.dotFg6
            ], { scale: 0, transformOrigin: '50% 50%' })

            // Text
            .set([
                this.el.step1text, this.el.step2text, this.el.step3text,
                this.el.step4text, this.el.step5text, this.el.step6text
            ], { opacity: 0, y: 20 })

            // Step 1
            .set(this.el.step1, { transformOrigin: '50% 150%', rotation: -15, opacity: 0 })
            .set(this.el.step1mark1, { transformOrigin: '50% 50%', scale: 0 })
            .set(this.el.step1mark2, { transformOrigin: '50% 50%', scale: 0 })
            .set(this.el.step1mark3, { transformOrigin: '50% 50%', scale: 0 })
            .set(this.el.step1line1, { transformOrigin: '0% 50%', scaleX: 0 })
            .set(this.el.step1line2, { transformOrigin: '0% 50%', scaleX: 0 })
            .set(this.el.step1line3, { transformOrigin: '0% 50%', scaleX: 0 })

            // Step 2
            .set(this.el.step2, { opacity: 0, y: 20 })
            .set(this.el.step2list, { y: -40 })

            // Step 3
            .set(this.el.step3, { opacity: 0, y: -15 })

            // Step 4
            .set(this.el.step4man1, { transformOrigin: '50% 50%', scale: 0 })
            .set(this.el.step4man2, { transformOrigin: '50% 50%', scale: 0 })
            .set(this.el.step4man3, { transformOrigin: '50% 50%', scale: 0 })
            .set(this.el.step4man4, { transformOrigin: '50% 50%', scale: 0 })
            .set(this.el.step4loupe, { opacity: 0, x: -40 })

            // Step 5
            .set(this.el.step5, { opacity: 0 })
            .set(this.el.step5arrows, { transformOrigin: '50% 50%', opacity: 0, rotation: 90 })
            .set(this.el.step5lang1, { x: 26, y: 26 })
            .set(this.el.step5lang2, { x: -26, y: -26 })

            // Step 6
            .set(this.el.step6, { opacity: 0 })
            .set(this.el.step6letter, { transformOrigin: '50% 50%', x: -60, rotation: -15 });

        this.bootstrap.on('ready', () => this.setListeners());
    }

    private checkVisibility () : void {
        requestAnimationFrame(() => {
            const
                rect = this.el.scheme.getBoundingClientRect(),
                scrollTop : number = getScrollTop(),
                pageYOffsetTop : number = rect.top + scrollTop,
                pageYOffsetBottom : number = pageYOffsetTop + rect.height;

            if ((scrollTop + window.innerHeight - 200) > pageYOffsetTop && scrollTop < pageYOffsetBottom) {
                this.removeListeners();
                this.animate();
            }
        });
    }

    private animate () : void {
        if (this.isAnimated) {
            return;
        }

        this.isAnimated = true;

        this.timeline
            // Show scheme
            .set(this.el.wrap, { opacity: 1 })
            .to(this.el.mask, 3.5, { strokeDashoffset: '0px', ease: Power1.easeOut }, '+=0.1')

            // Step 1
            .to([ this.el.dotBg1, this.el.dotFg1 ], 0.5, { scale: 1, ease: Elastic.easeOut }, '-=3.5')
            .to(this.el.step1text, 0.5, { opacity: 1, y: 0, ease: Power2.easeOut }, '-=3.5')
            .to(this.el.step1, 1, { rotation: 0, opacity: 1, ease: Power2.easeOut }, '-=3.5')
            .to(this.el.step1mark1, 0.5, { scale: 1, ease: Power2.easeOut }, '-=3.3')
            .to(this.el.step1line1, 0.5, { scaleX: 1, ease: Power2.easeOut }, '-=3.2')
            .to(this.el.step1mark2, 0.5, { scale: 1, ease: Power2.easeOut }, '-=3.1')
            .to(this.el.step1line2, 0.5, { scaleX: 1, ease: Power2.easeOut }, '-=3.0')
            .to(this.el.step1mark3, 0.5, { scale: 1, ease: Power2.easeOut }, '-=2.9')
            .to(this.el.step1line3, 0.5, { scaleX: 1, ease: Power2.easeOut }, '-=2.8')

            // Step 2
            .to([ this.el.dotBg2, this.el.dotFg2 ], 0.5, { scale: 1, ease: Elastic.easeOut }, '-=3')
            .to(this.el.step2text, 0.5, { opacity: 1, y: 0, ease: Power2.easeOut }, '-=3')
            .to(this.el.step2, 1, { y: 0, opacity: 1, ease: Power2.easeOut }, '-=3')
            .to(this.el.step2list, 1, { y: 0, ease: Power2.easeOut }, '-=3')

            // Step 3
            .to([ this.el.dotBg3, this.el.dotFg3 ], 0.5, { scale: 1, ease: Elastic.easeOut }, '-=2.5')
            .to(this.el.step3text, 0.5, { opacity: 1, y: 0, ease: Power2.easeOut }, '-=2.5')
            .to(this.el.step3, 0.2, { y: 0, opacity: 1, ease: Power1.easeInOut }, '-=2.5')
            .to(this.el.step3, 0.3, { y: -15, ease: Power1.easeInOut }, '-=2.25')
            .to(this.el.step3, 0.3, { y: 0, ease: Power1.easeInOut }, '-=2')

            // Step 4
            .to([ this.el.dotBg4, this.el.dotFg4 ], 0.5, { scale: 1, ease: Elastic.easeOut }, '-=2')
            .to(this.el.step4text, 0.5, { opacity: 1, y: 0, ease: Power2.easeOut }, '-=2')
            .to(this.el.step4man1, 0.3, { scale: 1, ease: Power2.easeOut }, '-=2')
            .to(this.el.step4man2, 0.3, { scale: 1, ease: Power2.easeOut }, '-=1.7')
            .to(this.el.step4man3, 0.3, { scale: 1, ease: Power2.easeOut }, '-=1.6')
            .to(this.el.step4man4, 0.3, { scale: 1, ease: Power2.easeOut }, '-=1.6')
            .to(this.el.step4loupe, 1.5, { opacity: 1, x: 0, ease: Power2.easeOut }, '-=2')

            // Step 5
            .to([ this.el.dotBg5, this.el.dotFg5 ], 0.5, { scale: 1, ease: Elastic.easeOut }, '-=1.5')
            .to(this.el.step5text, 0.5, { opacity: 1, y: 0, ease: Power2.easeOut }, '-=1.5')
            .to(this.el.step5, 0.3, { opacity: 1, ease: Power0.easeNone }, '-=1.5')
            .to(this.el.step5lang1, 0.5, { x: 0, y: 0, ease: Power2.easeOut }, `-=1.3`)
            .to(this.el.step5lang2, 0.5, { x: 0, y: 0, ease: Power2.easeOut }, `-=1.3`)
            .to(this.el.step5arrows, 0.75, { opacity: 1, rotation: 0, ease: Power2.easeOut }, '-=1.25')

            // Step 6
            .to([ this.el.dotBg6, this.el.dotFg6 ], 0.5, { scale: 1, ease: Elastic.easeOut }, '-=0.25')
            .to(this.el.step6text, 0.5, { opacity: 1, y: 0, ease: Power2.easeOut }, '-=0.5')
            .to(this.el.step6, 0.3, { opacity: 1, ease: Power0.easeNone }, '-=0.5')
            .to(this.el.step6letter, 1.1, { x: 0, rotation: 0, ease: Power2.easeOut }, '-=0.5')

        // .play(2);
    }

    private removeListeners () : void {
        window.removeEventListener('scroll', this.checkVisibility);
        window.removeEventListener('resize', this.checkVisibility);
    }

    public setListeners () : void {
        window.addEventListener('scroll', this.checkVisibility);
        window.addEventListener('resize', this.checkVisibility);
        this.checkVisibility();
    }
}
