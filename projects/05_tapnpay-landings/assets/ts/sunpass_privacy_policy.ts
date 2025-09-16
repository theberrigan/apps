const delegate = (el : any, eventName : string, descendantSelector : string, listener : Function) => {
    if (typeof(el) === 'string') {
        el = document.querySelector(el);
    }

    if (!el) {
        return;
    }

    el.addEventListener('click', (e) => {
        const descendants = [ ...el.querySelectorAll(descendantSelector) ];

        let target = e.target;

        while (target !== el) {
            if (descendants.includes(target)) {
                Object.defineProperty(e, 'target', { value: target, configurable: true });
                return listener(e);
            }

            target = target.parentNode;
        }
    });
};

const markEvent = (e : any, propKey : string, propValue : any = true) => {
    Object.defineProperty(e, `__${ propKey }`, { value: propValue, configurable: true });
    return e;
};

const hasEventMark = (e : any, propKey : string, propValue : any = true) => {
    return e[`__${ propKey }`] === propValue;
};

class LanguageSwitcher {
    public hostEl : HTMLElement;

    public buttonEl : HTMLElement;

    public curLangEl : HTMLElement;

    public popupEl : HTMLElement;

    public itemEls : HTMLElement[];

    public isPopupVisible : boolean = false;

    public langs : { [ key : string ] : string };

    public currentLang : string;

    constructor () {
        this.hostEl = document.body.querySelector('.language-switcher');
        this.buttonEl = this.hostEl.querySelector('.language-switcher__button');
        this.curLangEl = this.hostEl.querySelector('.language-switcher__current_language');
        this.popupEl = this.hostEl.querySelector('.language-switcher__popup');
        this.itemEls = Array.from(this.popupEl.querySelectorAll('.language-switcher__item'));

        this.langs = this.itemEls.reduce((acc, el : HTMLElement) => {
            const code = el.dataset.code.toLowerCase();

            acc[code] = el.dataset.shortName;

            return acc;
        }, {});

        this.buttonEl.addEventListener('click', (e) => this.onButtonClick(e));
        this.popupEl.addEventListener('click', (e) => this.onPopupClick(e));
        document.documentElement.addEventListener('click', (e) => this.onDocClick(e));
        delegate(this.popupEl, 'click', '.language-switcher__item', (e) => this.onItemClick(e));

        this.updateCurrentLangFromLocation();
    }

    onButtonClick (e : Event) {
        markEvent(e, 'lsButtonClick');

        this.isPopupVisible = !this.isPopupVisible;

        if (this.isPopupVisible) {
            this.hostEl.classList.add('language-switcher_visible');
        } else {
            this.hostEl.classList.remove('language-switcher_visible');
        }
    }

    onPopupClick (e : Event) {
        markEvent(e, 'lsPopupClick');
    }

    onItemClick (e : Event) {
        markEvent(e, 'lsItemClick');

        this.isPopupVisible = false;
        this.hostEl.classList.remove('language-switcher_visible');

        this.setLanguage((<HTMLElement>e.target).dataset.code.toLowerCase());
    }

    onDocClick (e : Event) {
        if (!hasEventMark(e, 'lsButtonClick') && !hasEventMark(e, 'lsItemClick') &&  !hasEventMark(e, 'lsPopupClick')) {
            this.isPopupVisible = false;
            this.hostEl.classList.remove('language-switcher_visible');
        }
    }

    updateCurrentLangFromLocation () {
        const currentLocation = new URL(window.location.href);

        this.currentLang = (currentLocation.pathname.replace(/^\/+/g, '').split('/')[0] || 'en').toLowerCase();

        if (!(this.currentLang in this.langs)) {
            this.currentLang = 'en';
        }

        this.setLanguageToUI(this.currentLang, this.langs[this.currentLang]);
    }

    setLanguage (code : string) {
        if (code === this.currentLang) {
            return;
        }

        this.currentLang = code;

        this.setLanguageToUI(this.currentLang, this.langs[this.currentLang]);

        const currentLocation = new URL(window.location.href);
        const pathParts = currentLocation.pathname.replace(/^\/+/g, '').split('/');
        const currentLangSlug = pathParts[0].toLowerCase();

        if (!(currentLangSlug in this.langs)) {
            pathParts.unshift('en');
        }

        pathParts[0] = code;

        currentLocation.pathname = pathParts.join('/');

        window.location.assign(currentLocation.toString());
    }

    setLanguageToUI (code : string, shortName : string) {
        this.curLangEl.textContent = shortName;
        this.itemEls.forEach(el => {
            if (el.dataset.code.toLowerCase() === code) {
                el.classList.add('language-switcher__item_current');
            } else {
                el.classList.remove('language-switcher__item_current');
            }
        });
    }

    getCurrentLang () : string {
        return this.currentLang;
    }
}


class Application {
    public langSwitcher : LanguageSwitcher;

    constructor () {
        this.langSwitcher = new LanguageSwitcher();
    }
}


const init = () => {
    (<any>window).sunpass = new Application();
};

/^(interactive|complete)$/.test(document.readyState) ? init() : window.addEventListener('load', init);
