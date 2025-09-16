import {bindMethods, clone, mergeObjects} from '../../js/utils';
import {DOM} from './ui.class';
import {Network} from './network.class';
const config = require('../../config/config.json');

export class LanguageManager {
    public static get deps () : any {
        return {
            dom: DOM,
            network: Network
        };
    }

    public dom : DOM = null;

    public network : Network = null;

    // ------------------

    private languages : any[] = null;

    private preferredLanguageCodes : string[] = null;

    private defaultLanguage : any = null;

    private el : any = null;

    private languageCodes : string[] = null;

    private currentLanguage : any = null;

    private isActive : boolean = false;

    private languageChangedListeners : any[] = [];

    private messages : any = null;

    public constructor () {
        bindMethods(this);
    }

    public init () : Promise<any> {
        return new Promise((resolve) => {
            // 1. Get languages list from config
            this.languages = clone(config.languages).map(lang => {
                lang.code = lang.code.toLowerCase();
                lang.data = null;
                lang.documents = {};
                lang.url = `locale/${ lang.code }/messages.json`;
                lang.isDefault = lang.isDefault === true;
                return lang;
            });

            this.languageCodes = this.languages.map(lang => lang.code);

            // 2. Get default (fallback) language
            this.defaultLanguage = this.languages.find(lang => lang.isDefault) || this.languages[0];
            this.defaultLanguage.isDefault = true;

            // 3. Get preferred languages
            this.preferredLanguageCodes = this.getPreferredLanguageCodes() || [ this.defaultLanguage.code ];

            // 4. Get current language
            let currentLanguageCode : string = this.restoreLanguage();

            if (!currentLanguageCode) {
                currentLanguageCode = this.defaultLanguage.code;

                for (let i = 0, len = this.preferredLanguageCodes.length; i < len; i++) {
                    const languageCode : string = this.preferredLanguageCodes[i];
                    if (this.languageCodes.indexOf(languageCode) >= 0) {
                        currentLanguageCode = languageCode;
                        break;
                    }
                }
            }

            this.currentLanguage = this.languages.find(lang => lang.code === currentLanguageCode) || this.defaultLanguage;
            this.saveLanguage();

            // --------------------

            // 5. DOM
            const switcherEl = document.body.querySelector('.language-switcher');

            this.el = {
                switcher: switcherEl,
                current: switcherEl.querySelector('.language-switcher__current_language'),
                items: []
            };

            const listEl : any = switcherEl.querySelector('.language-switcher__list');

            this.languages.forEach(lang => {
                const itemEl : any = document.createElement('li');
                itemEl.className = 'language-switcher__item';
                itemEl.innerHTML = lang.name;

                Object.defineProperty(itemEl, '__language', { value: lang, configurable: true });

                listEl.appendChild(itemEl);
                this.el.items.push(itemEl);
            });

            this.dom.delegate(listEl, 'click', 'li', e => {
                this.useLanguage(e.target.__language);
                this.togglePopup(false);
            });

            this.updateCurrentLanguage();

            // 6. Set listeners
            this.el.switcher.addEventListener('click', e => {
                Object.defineProperty(e, '__languageSwitcherMark', { value: true, configurable: true });
            });

            document.querySelector('.language-switcher__button').addEventListener('click', () => this.togglePopup());

            document.body.addEventListener('click', (e : any) => {
                if (!e.__languageSwitcherMark) {
                    this.togglePopup(false);
                }
            });

            // --------------------

            const isDefaultUsed : boolean = this.currentLanguage === this.defaultLanguage;

            Promise.all([
                this.network.get(this.defaultLanguage.url),
                isDefaultUsed ? Promise.resolve(null) : this.network.get(this.currentLanguage.url)
            ])
                .then(([ defaultLanguage, currentLanguage ] : [ any, any ]) => {
                    this.defaultLanguage.data = defaultLanguage;

                    if (!isDefaultUsed) {
                        this.currentLanguage.data = currentLanguage;
                    }

                    this.updateMessages();
                    this.localize();
                })
                .catch(reason => console.warn('Can`t load locale file:', reason))
                .then(() => resolve());
        });
    }

    public loadDocument (documentName : string) : Promise<string> {
        return new Promise(resolve => {
            if (documentName in this.currentLanguage.documents) {
                resolve(
                    this.currentLanguage.documents[documentName] ||
                    this.defaultLanguage.documents[documentName]
                );

                return;
            }

            const isDefaultUsed : boolean = this.currentLanguage === this.defaultLanguage;

            Promise.all([
                this.network.get(`locale/${ this.defaultLanguage.code }/${ documentName }.html`, 'html'),
                isDefaultUsed ?
                    Promise.resolve(null) :
                    this.network.get(`locale/${ this.currentLanguage.code }/${ documentName }.html`, 'html')
            ])
                .then(([ defDoc, curDoc ] : [ any, any ]) => {
                    defDoc = this.defaultLanguage.documents[documentName] = (defDoc || '').trim() || null;

                    if (!isDefaultUsed) {
                        curDoc = this.currentLanguage.documents[documentName] = (curDoc || '').trim() || null;
                    }

                    resolve(curDoc || defDoc);
                })
                .catch(reason => console.warn('Can`t load document:', reason))
                .then(() => resolve(null));
        });
    }

    private updateMessages () : void {
        this.messages = mergeObjects(this.defaultLanguage.data, this.currentLanguage.data || {});
        this.languageChangedListeners.forEach(callback => callback(this.currentLanguage.code));
    }

    private localize () : void {
        requestAnimationFrame(() => {
            document.querySelectorAll('[data-i18n]').forEach((el : any) => {
                el.dataset.i18n.split(',').forEach(item => {
                    const
                        pair = item.split('='),
                        messageKey = pair.pop(),
                        attr = pair[0];

                    let message : string = this.getMessage(messageKey);

                    if (message === null) {
                        console.warn('No message found in the locale file:', el.dataset.i18n);
                        return;
                    }

                    attr ? el.setAttribute(attr, message) : (el.innerHTML = message);
                });
            });
        });
    }

    public translatePrefixed (messageKey : string) : string {
        if (typeof(messageKey) !== 'string' || messageKey.slice(0, 5) !== 'i18n=') {
            return messageKey;
        }

        return this.getMessage(messageKey.slice(5));
    }

    public getMessage (messageKey : string) : string {
        if (typeof(messageKey) !== 'string') {
            console.warn('[getMessage] Wrong key:', messageKey);
            return null;
        }

        const message : string = this.walk(this.messages, messageKey.split('.'));

        return message === null ? messageKey : message;
    }

    private walk (tree : any, keyChain : string[]) : any {
        if (!tree || !Array.isArray(keyChain) || !keyChain.length) {
            return null;
        }

        tree = tree[ keyChain.shift() ];

        if (keyChain.length) {
            return typeof(tree) === 'object' ? this.walk(tree, keyChain) : null;
        } else {
            return typeof(tree) === 'string' || typeof(tree) === 'object' ? tree : null;
        }
    }

    private togglePopup (isActive? : boolean) : void {
        requestAnimationFrame(() => {
            this.isActive = typeof(isActive) === 'boolean' ? isActive : !this.isActive;
            this.el.switcher.classList[ this.isActive ? 'add' : 'remove' ]('language-switcher_visible');
        });
    }

    private useLanguage (lang : any) : void {
        if (this.currentLanguage === lang) {
            return;
        }

        this.currentLanguage = lang;
        this.updateCurrentLanguage();
        this.saveLanguage();

        if (this.currentLanguage.data) {
            this.updateMessages();
            this.localize();
            return;
        }

        this.network
            .get(this.currentLanguage.url)
            .then(locale => {
                this.currentLanguage.data = locale;
                this.updateMessages();
                this.localize();
            });
    }

    private updateCurrentLanguage () : void {
        this.el.current.textContent = this.currentLanguage.code;
        this.el.items.forEach(el => {
            el.classList[ el.__language === this.currentLanguage ? 'add' : 'remove' ]('language-switcher__item_current');
        });
    }

    private restoreLanguage () : string {
        return localStorage.getItem('language');
    }

    private saveLanguage () : void {
        localStorage.setItem('language', this.currentLanguage.code);
    }

    private getPreferredLanguageCodes () : string[] {
        const preferredLanguages = (
            (navigator.languages || [ navigator.language || <string>(<any>navigator).userLanguage || <string>(<any>navigator).browserLanguage ])
                .filter(lang => !!lang)
                .map(lang => lang.split(/[_\-]/).shift().toLowerCase())
                .filter((val, i, arr) => arr.indexOf(val) === i)
        );

        return preferredLanguages.length ? preferredLanguages : null;
    }

    public onLanguageChanged (listener : any) : void {
        this.languageChangedListeners.push(listener);
    }
}
