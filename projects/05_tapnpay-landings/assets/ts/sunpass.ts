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
    phoneFormBrand : string;
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

const injectFormSubmittedTag = async () => {
    return new Promise<void>((resolve) => {
        const script = document.createElement('script');

        script.src = 'https://tag.simpli.fi/sifitag/9a43b790-4a63-013a-4fc0-06abc14c0bc6';
        script.onload = () => resolve();
        script.onerror = () => resolve();

        document.head.appendChild(script);
    });
};


class FAQ {
    public activeItemEl : HTMLElement;

    constructor () {
        const itemMainEls : HTMLElement[] = Array.from(document.body.querySelectorAll('.section-faq__item-main'));

        itemMainEls.forEach(el => el.addEventListener('click', () => {
            this.onItemMainClick(el.closest('.section-faq__item'));
        }));
    }

    onItemMainClick (itemEl : HTMLElement) {
        if (this.activeItemEl) {
            this.activeItemEl.classList.remove('section-faq__item_active');
        }

        if (this.activeItemEl === itemEl) {
            this.activeItemEl = null;
        } else {
            itemEl.classList.add('section-faq__item_active');
            this.activeItemEl = itemEl;
        }
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

    getCurrentLang () : string {
        return this.currentLang;
    }
}

class PhoneForm {
    isValid : boolean = false;

    isSubmitting : boolean = false;

    formEl : HTMLFormElement;

    fieldsetEl : HTMLFieldSetElement;

    inputEl : HTMLInputElement;

    buttonEl : HTMLButtonElement;

    messageEl : HTMLElement;

    constructor (
        private readonly config : AppConfig,
        private readonly rootEl : HTMLElement,
        private readonly langSwitcher : LanguageSwitcher
    ) {
        this.rootEl = rootEl;
        this.formEl = rootEl.querySelector('.phone-form__form');
        this.fieldsetEl = rootEl.querySelector('.phone-form__fieldset');
        this.inputEl = rootEl.querySelector('.phone-form__input');
        this.buttonEl = rootEl.querySelector('.phone-form__button');
        this.messageEl = rootEl.querySelector('.phone-form__message');

        this.formEl.addEventListener('submit', (e) => this.onFormSubmit(e));
        this.inputEl.addEventListener('input', () => this.validate());
        this.inputEl.addEventListener('change', () => this.validate());
        this.inputEl.addEventListener('focus', () => this.validate());
        this.inputEl.addEventListener('blur', () => this.validate());

        this.setValidState(false);
        this.setSubmitting(false);
        this.setMessage(null);
    }

    onFormSubmit (e) {
        e.preventDefault();

        if (this.isSubmitting) {
            return;
        }

        this.validate();

        if (!this.isValid) {
            return;
        }

        this.setSubmitting(true);
        this.setMessage(null);

        const grecaptcha = (<any>window).grecaptcha;

        grecaptcha.ready(() => {
            grecaptcha.execute(this.config.recaptchaSiteKey, { action: 'submit_phone_form' }).then((token) => {
                const phone = this.sanitizePhone(this.getPhone());

                fetch(this.config.phoneFormURL, {
                    method: 'POST',
                    mode: 'cors',
                    headers: {
                        'Accept': 'application/json, text/plain, */*',
                        'Content-Type': 'application/json',
                        'TNP-Recaptcha-Token': token
                    },
                    body: JSON.stringify({
                        phone,
                        language: this.langSwitcher.getCurrentLang(),
                        brand: this.config.phoneFormBrand
                    })
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
                }).then(async (isOk) => {
                    if (isOk) {
                        // window.location.assign('/thank-you-for-signing-up/');
                        await injectFormSubmittedTag();
                        this.setSubmitting(false);
                        this.resetForm();
                        this.setMessage({
                            isError: false,
                            message: 'Thank you for getting started! You will receive a text message momentarily that will guide you through the registration process'
                        });
                    } else {
                        this.setSubmitting(false);
                        this.setMessage({
                            isError: true,
                            message: 'Unfortunately, something went wrong. Please try again later'
                        });
                    }
                });
            });
        });
    }

    resetForm () {
        this.inputEl.value = '';
        this.validate();
    }

    getPhone () {
        return (this.inputEl.value || '').trim();
    }

    sanitizePhone (phone) {
        return (phone || '').replace(/[^\d]+/g, '');
    }

    validate () {
        const phone = this.getPhone();
        const phoneDigits = this.sanitizePhone(phone);
        const isPhoneValid = /^[+\-()\s\d]+$/.test(phone) && phoneDigits.length >= 6;

        this.setValidState(isPhoneValid);
    }

    setValidState (isValid) {
        this.isValid = isValid;
        this.buttonEl.disabled = !this.isValid;
    }

    setSubmitting (isSubmitting) {
        this.isSubmitting = isSubmitting;
        this.fieldsetEl.disabled = this.isSubmitting;

        if (this.isSubmitting) {
            this.buttonEl.classList.add('phone-form__button_progress');
        } else {
            this.buttonEl.classList.remove('phone-form__button_progress');
        }
    }

    setMessage (data) {
        if (data) {
            this.messageEl.innerHTML = data.message;

            if (data.isError) {
                this.messageEl.classList.add('phone-form__message_error');
            } else {
                this.messageEl.classList.remove('phone-form__message_error');
            }

            this.messageEl.classList.add('phone-form__message_visible');
        } else {
            this.messageEl.classList.remove('phone-form__message_visible');
        }
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
        this.fieldEls = Array.from(this.formEl.querySelectorAll('input[name], textarea[name]'));
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

        if (fieldEl instanceof HTMLInputElement) {
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
        } else if (fieldEl instanceof HTMLTextAreaElement) {
            isValid ||= value.length > 0;
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
                }).then(async (isOk) => {
                    if (isOk) {
                        await injectFormSubmittedTag();
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

    public phoneForms : PhoneForm[];

    public faq : FAQ;

    public feedback : Feedback;

    constructor (
        private readonly config : AppConfig
    ) {
        this.setupRecaptcha(this.config.recaptchaSiteKey);

        this.langSwitcher = new LanguageSwitcher();
        this.faq = new FAQ();
        this.feedback = new Feedback(this.config);

        this.adminBarEl = document.body.querySelector(':scope > #wpadminbar');
        this.panelEl = document.body.querySelector(':scope > .panel');
        this.navEl = document.body.querySelector('.nav');
        this.phoneForms = Array.from(document.querySelectorAll('.phone-form')).map((el : HTMLElement) => {
            return new PhoneForm(this.config, el, this.langSwitcher);
        });

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
    const config : AppConfig = (<any>window).sunpassConfig;

    if (!config) {
        throw new Error('App config is not found');
    }

    (<any>window).sunpass = new Application(config);
};

/^(interactive|complete)$/.test(document.readyState) ? init() : window.addEventListener('load', init);
