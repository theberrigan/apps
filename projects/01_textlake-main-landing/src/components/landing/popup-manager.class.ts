import {bindMethods, removeHashFromLocation, setLocationState} from '../../js/utils';
import {LanguageManager} from './language-manager.class';
import {DOM} from './ui.class';

export class PopupManager {
    public static get deps () : any {
        return {
            langManager: LanguageManager,
            dom: DOM
        };
    }

    public langManager : LanguageManager = null;

    public dom : DOM = null;

    public el : any = null;

    private activePopupHash : string = null;

    public constructor () {
        bindMethods(this);
    }

    public init () : void {
        const
            popupEl = document.body.querySelector('.popup'),
            contentWrapEl = popupEl.querySelector('.popup__content-wrap');

        this.el = {
            popup: popupEl,
            header: popupEl.querySelector('.popup__header'),
            content: popupEl.querySelector('.popup__content')
        };

        contentWrapEl.addEventListener('click', e => Object.defineProperty(e, '__popupMark', { value: true, configurable: true }));
        popupEl.addEventListener('click', (e : any) => !e.__popupMark && this.togglePopup(false));
    }

    public showPopup (popupId : string) {
        this.langManager
            .loadDocument(popupId)
            .then((documentHtml : string) => {
                if (documentHtml) {
                    const
                        titleKey = `popup.${ popupId }_title`,
                        title = this.langManager.getMessage(titleKey);

                    if (title && title !== titleKey) {
                        this.el.header.innerHTML = title;
                        this.el.header.classList.add('popup__header_visible');
                    } else {
                        this.el.header.classList.remove('popup__header_visible');
                    }

                    this.el.content.innerHTML = documentHtml;
                    this.el.content.querySelectorAll('[style]').forEach(el => el.removeAttribute('style'));
                    this.togglePopup(true, popupId);
                }
            });
    }

    public togglePopup (show : boolean, popupId? : string) : void {
        if (show) {
            this.activePopupHash = popupId ? `#popup=${ popupId }` : null;
            this.activePopupHash && setLocationState(this.activePopupHash);
            this.el.popup.classList.add('popup_visible');
        } else {
            removeHashFromLocation(this.activePopupHash);
            this.activePopupHash = null;
            this.el.popup.classList.remove('popup_visible');
        }

        this.dom.setScrollState(!show);
    }
}