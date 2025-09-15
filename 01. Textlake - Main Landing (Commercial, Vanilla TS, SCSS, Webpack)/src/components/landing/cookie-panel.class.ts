import {bindMethods} from '../../js/utils';

export class CookiePanel {
    constructor () {
        bindMethods(this);
    }

    public init () : void {
        if (!localStorage.getItem('isCookiePanelShown')) {
            requestAnimationFrame(() => {
                const
                    panelEl = document.querySelector('.cookie-panel'),
                    button = panelEl.querySelector('.cookie-panel__button-close');

                button.addEventListener('click', () => {
                    localStorage.setItem('isCookiePanelShown', '1');

                    requestAnimationFrame(() => {
                        panelEl.classList.remove('cookie-panel_visible');
                    });
                });

                panelEl.classList.add('cookie-panel_visible');
            });
        }
    }
}