import { Subscriber } from '../../js/subscriber.class';
import { bindMethods } from '../../js/utils';

export class Bootstrap extends Subscriber {
    public readonly isBootstrap : boolean = true;

    public svg : SVGElement[] = [];

    public resizeDebounceTimer : any = null;

    constructor () {
        super();
        bindMethods(this);
    }

    public init () : void {
        document.body.insertAdjacentHTML('beforeend', require('./template.html'));

        const ua = window.navigator.userAgent.toLowerCase();
        const isOpera = /opera/i.test(ua) || /opr/i.test(ua);
        const isIE = !isOpera && /(msie|trident\/)/i.test(ua);

        if (isIE) {
            document.documentElement.classList.add('browser_IE');

            this.svg = Array.prototype.slice.call(document.querySelectorAll('.svg_mimic-width'));

            if (this.svg.length > 0) {
                window.addEventListener('resize', () => this.resizeSvg());
                this.resizeSvg();
            }
        }
    }

    public execute () : void {
        const detailsEl : any = document.querySelector('.section-advantages__security-details');
        
        document.querySelector('.section-advantages__button-learn-more').addEventListener('click', () => {
            detailsEl.classList.toggle('section-advantages__security-details_visible');
        });

        this.emit('ready');
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
}
