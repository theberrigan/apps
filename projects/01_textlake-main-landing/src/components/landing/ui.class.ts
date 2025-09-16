import { bindMethods } from '../../js/utils';
import {Power4, TweenLite} from 'gsap/all';

export class DOM {
    private topGap : number = 100;

    private pageScrollTween : any = null;

    constructor () {
        bindMethods(this);
    }

    public init () : void {

    }

    public delegate (el : any, eventName : string, descendantSelector : string, listener : Function) : void {
        if (typeof(el) === 'string') {
            el = document.body.querySelector(el);
        }

        if (!el) {
            return;
        }

        el.addEventListener('click', (e) => {
            const descendants = Array.from(el.querySelectorAll(descendantSelector));

            let target = e.target;

            while (target !== el) {
                if (descendants.includes(target)) {
                    Object.defineProperty(e, 'target', { value: target, configurable: true });
                    return listener(e);
                }

                target = target.parentNode;
            }
        });
    }

    public offset (el : any) : { top : number, left : number } {
        if (!el) {
            return null;
        }

        if (typeof(el) === 'string') {
            el = document.body.querySelector(el);
        }

        if (!el.getClientRects().length) {
            return {
                top: 0,
                left: 0
            };
        }

        const
            rect = el.getBoundingClientRect(),
            scrollTop = window.pageYOffset || document.documentElement.scrollTop || document.body.scrollTop,
            scrollLeft = window.pageXOffset || document.documentElement.scrollLeft || document.body.scrollLeft,
            clientTop = document.documentElement.clientTop || document.body.clientTop || 0,
            clientLeft = document.documentElement.clientLeft || document.body.clientLeft || 0;

        return {
            top: rect.top + scrollTop - clientTop,
            left: rect.left + scrollLeft - clientLeft
        };
    }

    public scrollPage (to : string | number | HTMLElement, animate : boolean = false) : void {
        if (typeof(to) === 'string') {
            to = <HTMLElement>document.querySelector(to);

            if (!to) {
                return;
            }
        }

        if (typeof(to) === 'object' && (to = (this.offset(to) || { top: null }).top) === null) {
            return;
        }

        to = Math.max(0, <number>to - this.topGap);

        if (animate) {
            this.pageScrollTween && this.pageScrollTween.kill();
            this.pageScrollTween = TweenLite.to(window, 0.3, {
                scrollTo: { y: to },
                ease: Power4.easeOut
            });
        } else {
            document.documentElement.scrollTop = to;
            document.body.scrollTop = to;
        }
    }

    public setScrollState (state : boolean) : void {
        document.body.classList[ state ? 'remove' : 'add' ]('scroll_disabled');
    }
}