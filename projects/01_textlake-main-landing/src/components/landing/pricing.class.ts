import {bindMethods} from '../../js/utils';

export class Pricing {
    constructor () {
        bindMethods(this);
    }

    public init () : void {
        requestAnimationFrame(() => {
            const el : any = Array.from(document.querySelectorAll('.section-pricing__plan-items')).map(wrap => {
                return Array.from(wrap.querySelectorAll('li'));
            });

            const pairCount : number = Math.min(...el.map(arr => arr.length));

            for (let i = 0; i < pairCount; i++) {
                let maxHeight : number = 0;

                for (let j = 0, len = el.length; j < len; j++) {
                    maxHeight = Math.max(maxHeight, el[j][i].getBoundingClientRect().height);
                }

                for (let j = 0, len = el.length; j < len; j++) {
                    el[j][i].style.minHeight = maxHeight + 'px';
                }
            }
        });
    }
}