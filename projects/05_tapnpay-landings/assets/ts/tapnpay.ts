const EMAIL_REGEXP = /^(?=.{1,254}$)(?=.{1,64}@)[a-zA-Z0-9!#$%&'*+/=?^_`{|}~-]+(?:\.[a-zA-Z0-9!#$%&'*+/=?^_`{|}~-]+)*@[a-zA-Z0-9](?:[a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?(?:\.[a-zA-Z0-9](?:[a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?)*$/;
const PHONE_REGEXP = /^[+\-()\s\d]+$/;

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

const setScrollState = (state : boolean) => {
    if (state) {
        document.body.classList.remove('scroll_disabled');
    } else {
        document.body.classList.add('scroll_disabled');
    }
};

const markEvent = (e : any, propKey : string, propValue : any = true) => {
    Object.defineProperty(e, `__${ propKey }`, { value: propValue, configurable: true });
    return e;
};

const hasEventMark = (e : any, propKey : string, propValue : any = true) => {
    return e[`__${ propKey }`] === propValue;
};

const getEventMark = (e : any, propKey : string) => {
    return e[`__${ propKey }`];
};


interface AppConfig {
    isLoggedIn : boolean;
    phoneFormURL : string;
    feedbackFormURL : string;
    recaptchaSiteKey : string;
}

interface FeedbackRequestData {
    email : string;
    phone : string;
    comment : string;
    first_name : string;
    last_name : string;
}


class DemoVideo {
    public contentEl : HTMLElement;

    public coverEl : HTMLElement;

    public readonly videoId : string = 'AcgvIV9rqE8';

    constructor () {
        this.contentEl = document.body.querySelector('.section-main__video-content');
        this.coverEl = document.body.querySelector('.section-main__video-cover');

        this.coverEl.addEventListener('click', () => this.onCoverClick());
    }

    onCoverClick () {
        const playerEl = document.createElement('iframe');

        playerEl.className = 'section-main__video-iframe';
        playerEl.allowFullscreen = true;
        playerEl.frameBorder = '0';
        playerEl.setAttribute('allow', 'accelerometer; autoplay; encrypted-media; gyroscope; picture-in-picture');
        playerEl.src = `https://www.youtube.com/embed/${ this.videoId }?autoplay=1`;

        this.contentEl.appendChild(playerEl);
        this.coverEl.style.display = 'none';
    }
}


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
}


class Feedback {
    hostEl : HTMLElement;

    messageEl : HTMLElement;

    fieldsetEl : HTMLFieldSetElement;

    formEl : HTMLFormElement;

    buttonEl : HTMLButtonElement;

    fieldEls : HTMLInputElement[];

    isFormValid : boolean = false;

    isSubmitting : boolean = false;

    constructor (
        private readonly config : AppConfig
    ) {
        this.hostEl = document.body.querySelector('.section-feedback__content');
        this.messageEl = this.hostEl.querySelector('.section-feedback__message');
        this.fieldsetEl = this.hostEl.querySelector('.section-feedback__fieldset');
        this.formEl = this.fieldsetEl.querySelector('.section-feedback__form');
        this.fieldEls = Array.from(this.formEl.querySelectorAll('input[name], textarea[name], select[name]'));
        this.buttonEl = this.formEl.querySelector('.section-feedback__button');

        this.formEl.addEventListener('submit', (e) => this.onFormSubmit(e));
        this.formEl.addEventListener('reset', () => this.onFormReset());
        this.fieldEls.forEach(el => {
            el.dataset.isValid = 'false';

            el.addEventListener('input', (e) => this.validateForm(e, false));
            el.addEventListener('change', (e) => this.validateForm(e, true));
            el.addEventListener('focus', (e) => this.validateForm(e, true));
            el.addEventListener('blur', (e) => this.validateForm(e, true));
        });

        this.validateForm();
        this.setSubmitting(false);
        this.setMessage(null);
    }

    resetForm () {
        this.formEl.reset();
    }

    validateForm (e : Event = null, showErrors : boolean = false) {
        const target = <HTMLInputElement>(e?.target);

        if (target) {
            this.validateField(target, showErrors);
        } else {
            this.fieldEls.forEach(el => this.validateField(el, showErrors));
        }

        const isFormValid = this.fieldEls.every(el => el.dataset.isValid === 'true');

        this.setValidState(isFormValid);
    }

    validateField (fieldEl : HTMLInputElement | HTMLTextAreaElement, showErrors : boolean) {
        const value = fieldEl.value.trim();
        let isValid = !value && !fieldEl.required;

        if ((<any>fieldEl) instanceof HTMLInputElement) {
            switch (fieldEl.type) {
                case 'email': {
                    isValid ||= value && EMAIL_REGEXP.test(value);
                    break;
                }
                case 'tel': {
                    isValid ||= value && PHONE_REGEXP.test(value) && this.sanitizePhone(value).length >= 6;
                    break;
                }
                default: {
                    isValid ||= value.length > 0;
                    break;
                }
            }
        } else if ((<any>fieldEl) instanceof HTMLTextAreaElement) {
            isValid ||= value.length > 0;
        } else if ((<any>fieldEl) instanceof HTMLSelectElement) {
            isValid ||= !!value;
        }

        if (!isValid && showErrors) {
            fieldEl.classList.add(fieldEl.dataset.errorClass);
        } else {
            fieldEl.classList.remove(fieldEl.dataset.errorClass);

        }

        fieldEl.dataset.isValid = String(!!(isValid));
    }

    setValidState (isValid) {
        this.isFormValid = isValid;
        this.buttonEl.disabled = !this.isFormValid;
    }

    setSubmitting (isSubmitting) {
        this.isSubmitting = isSubmitting;
        this.fieldsetEl.disabled = this.isSubmitting;

        if (this.isSubmitting) {
            this.buttonEl.classList.add('button_progress');
        } else {
            this.buttonEl.classList.remove('button_progress');
        }
    }

    sanitizePhone (phone) {
        return (phone || '').replace(/[^\d]+/g, '');
    }

    getFormData () : FeedbackRequestData {
        return this.fieldEls.reduce((acc : FeedbackRequestData, fieldEl : HTMLInputElement | HTMLTextAreaElement) => {
            let value : string = fieldEl.value.trim();

            if (fieldEl.type === 'tel') {
                value = this.sanitizePhone(value);
            }

            acc[fieldEl.name] = value;

            return acc;
        }, <FeedbackRequestData>{});
    }

    onFormSubmit (e : Event) {
        e.preventDefault();

        if (this.isSubmitting) {
            return;
        }

        this.validateForm();

        if (!this.isFormValid) {
            return;
        }

        this.setSubmitting(true);
        this.setMessage(null);

        const grecaptcha = (<any>window).grecaptcha;

        grecaptcha.ready(() => {
            grecaptcha.execute(this.config.recaptchaSiteKey, { action: 'submit_feedback_form' }).then((token) => {
                const formData = this.getFormData();

                fetch(this.config.feedbackFormURL, {
                    method: 'POST',
                    mode: 'cors',
                    headers: {
                        'Accept': 'application/json, text/plain, */*',
                        'Content-Type': 'application/json',
                        'TNP-Recaptcha-Token': token
                    },
                    body: JSON.stringify(formData)
                }).then((response) => {
                    return response.json();
                }).then((response) => {
                    if (response === 'OK') {
                        return true;
                    }

                    console.warn('Failed to send request:', response);
                    return false;
                }).catch((e) => {
                    console.warn('Failed to send request:', e);
                    return false;
                }).then((isOk) => {
                    if (isOk) {
                        this.setSubmitting(false);
                        this.resetForm();
                        this.setMessage({
                            isError: false,
                            message: 'Thank you! We will review your request and respond within 1 business day. Please go to our FAQ\'s to view helpful information'
                        });
                    } else {
                        this.setSubmitting(false);
                        this.setMessage({
                            isError: true,
                            message: 'Uh oh! We are having some technical difficulties and are working quickly to fix them. Please try again later'
                        });
                    }
                });
            });
        });
    }

    onFormReset () {
        requestAnimationFrame(() => this.validateForm());
    }

    setMessage (data) {
        if (data) {
            this.messageEl.innerHTML = data.message;

            if (data.isError) {
                this.messageEl.classList.add('section-feedback__message_error');
            } else {
                this.messageEl.classList.remove('section-feedback__message_error');
            }

            this.messageEl.classList.add('section-feedback__message_visible');
        } else {
            this.messageEl.classList.remove('section-feedback__message_visible');
        }
    }
}


class Application {
    public adminBarEl : HTMLElement;

    public panelEl : HTMLElement;

    public navEl : HTMLElement;

    public adminBarHeight : number = 0;

    public isAdminBarFixed : boolean = true;

    public isPanelInversed : boolean = false;

    public isNavActive : boolean = false;

    public readonly panelBreakpoint : number = 50;

    public langSwitcher : LanguageSwitcher;

    public demoVideo : DemoVideo;

    public feedback : Feedback;

    constructor (
        private readonly config : AppConfig
    ) {
        this.setupRecaptcha(this.config.recaptchaSiteKey);

        this.adminBarEl = document.body.querySelector(':scope > #wpadminbar');
        this.panelEl = document.body.querySelector(':scope > .panel');
        this.navEl = document.body.querySelector('.nav');

        this.langSwitcher = new LanguageSwitcher();
        this.demoVideo = new DemoVideo();
        this.feedback = new Feedback(this.config);

        window.addEventListener('scroll', () => this.onScroll());
        window.addEventListener('resize', () => this.onResize());

        delegate(this.navEl, 'click', 'a, .nav__overlay, .nav__hide', () => this.toggleNav(false));
        document.body.querySelector('.nav-switcher').addEventListener('click', () => this.toggleNav());

        this.onResize();
    }

    onResize () {
        if (this.config.isLoggedIn && this.adminBarEl) {
            this.adminBarHeight = this.adminBarEl.getBoundingClientRect().height;
            this.isAdminBarFixed = window.getComputedStyle(this.adminBarEl).position === 'fixed';
        } else {
            this.adminBarHeight = 0;
            this.isAdminBarFixed = true;
        }

        this.redrawPanel();
    }

    onScroll () {
        this.redrawPanel();
    }

    redrawPanel () {
        requestAnimationFrame(() => {
            if (this.isAdminBarFixed) {
                this.panelEl.style.top = this.adminBarHeight + 'px';
            } else {
                this.panelEl.style.top = Math.max(0, this.adminBarHeight - window.scrollY) + 'px';
            }

            if (window.scrollY < this.panelBreakpoint) {
                if (this.isPanelInversed) {
                    this.panelEl.classList.remove('panel_inversed');
                    this.isPanelInversed = false;
                }
            } else {
                if (!this.isPanelInversed) {
                    this.panelEl.classList.add('panel_inversed');
                    this.isPanelInversed = true;
                }
            }
        });
    }

    toggleNav (state? : boolean) {
        requestAnimationFrame(() => {
            this.isNavActive = typeof(state) === 'boolean' ? state : !this.isNavActive;

            setScrollState(!this.isNavActive);

            if (this.isNavActive) {
                this.navEl.classList.add('nav_active');
            } else {
                this.navEl.classList.remove('nav_active');
            }
        });
    }

    setupRecaptcha (siteKey : string) {
        const script = document.createElement('script');
        script.src = `https://www.google.com/recaptcha/api.js?render=${ siteKey }`;
        document.head.appendChild(script);
    }
}

const init = () => {
    const config : AppConfig = (<any>window).tnpConfig;

    if (!config) {
        throw new Error('App config is not found');
    }

    (<any>window).tnp = new Application(config);
};

/^(interactive|complete)$/.test(document.readyState) ? init() : window.addEventListener('load', init);
