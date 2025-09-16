import {bindMethods, getScrollTop} from '../../js/utils';

export class Panel {
    private el : any = null;

    private isInversed : boolean = false;

    private readonly breakpoint : number = 50;

    public constructor () {
        bindMethods(this);
    }

    public init () : void {
        this.el = {
            panel: document.body.querySelector('.panel')
        };

        window.addEventListener('scroll', this.redraw);
        window.addEventListener('resize', this.redraw);
        this.redraw();
    }

    public redraw () {
        requestAnimationFrame(() => {
            if (getScrollTop() < this.breakpoint) {
                if (this.isInversed) {
                    this.el.panel.classList.remove('panel_inversed');
                    this.isInversed = false;
                }
            } else {
                if (!this.isInversed) {
                    this.el.panel.classList.add('panel_inversed');
                    this.isInversed = true;
                }
            }
        });
    }
}