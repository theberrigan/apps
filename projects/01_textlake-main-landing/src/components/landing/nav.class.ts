import {bindMethods} from '../../js/utils';
import {DOM} from './ui.class';

export class Nav {
    public static get deps () : any {
        return {
            dom: DOM
        };
    }

    private isActive : boolean = false;

    public dom : DOM = null;

    private el : any = null;

    public constructor () {
        bindMethods(this);
    }

    public init () : void {
        this.el = {
            nav: document.querySelector('.nav')
        };

        this.dom.delegate(this.el.nav, 'click', 'a, .nav__overlay, .nav__hide', () => this.toggle(false));
        document.body.querySelector('.nav-switcher').addEventListener('click', () => this.toggle());
    }

    private toggle (state? : boolean) : void {
        requestAnimationFrame(() => {
            this.isActive = typeof(state) === 'boolean' ? state : !this.isActive;
            this.dom.setScrollState(!this.isActive);
            this.el.nav.classList[ this.isActive ? 'add' : 'remove' ]('nav_active');
        });
    }
}