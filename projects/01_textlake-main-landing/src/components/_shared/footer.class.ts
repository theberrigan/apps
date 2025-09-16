import {bindMethods} from '../../js/utils';

export class Footer {
    constructor () {
        bindMethods(this);
    }

    public init () : void {
        const footerRoot = <HTMLElement>document.body.querySelector('#footer-root');

        if (!footerRoot) {
            return;
        }

        footerRoot.insertAdjacentHTML('afterend', require('./footer.template.html'));
        footerRoot.parentElement.removeChild(footerRoot);//.remove();

        let isFixed : boolean = true;

        const
            footerEl : HTMLElement = document.body.querySelector('.footer'),
            fixedEl : HTMLElement = footerEl.querySelector('.footer__fixed-container'),
            mimicEl : HTMLElement = footerEl.querySelector('.footer__mimic'),
            resize = () => {
                requestAnimationFrame(() => {
                    const footerHeight = fixedEl.getBoundingClientRect().height;

                    if ((window.innerHeight - 100) < (footerHeight - 150)) {  // 100 - panel height, 150 - footer padding top
                        if (isFixed) {
                            footerEl.classList.remove('footer_fixed');
                            isFixed = false;
                        }
                    } else {
                        mimicEl.style.height = fixedEl.getBoundingClientRect().height + 'px';

                        if (!isFixed) {
                            footerEl.classList.add('footer_fixed');
                            isFixed = true;
                        }
                    }
                });
            };

        (footerRoot.getAttribute('data-classes') || '').split(/\s+/g).forEach(className => {
            if (className.length) {
                footerEl.classList.add(className);
            }
        });

        footerEl.querySelector('.footer__copyright-year').textContent = String((new Date()).getFullYear());

        window.addEventListener('resize', resize);
        resize();
    }
}
