import { bindMethods } from '../../js/utils';
import { DOM } from '../landing/ui.class';

export class Tutorial {
    public static get deps () : any {
        return {
            dom: DOM
        };
    }

    public dom : DOM = null;

    private current : any = null;

    public constructor () {
        bindMethods(this);
    }

    private getTutorialIdFromUrl (url : string) : string {
        const match = url.match(/[\/\\]+tutorial[\/\\]+([A-z\d_-]+)/i);
        return match ? match[1] : null;
    }

    public init () : void {
        const
            cache : any = {},
            initialTutorialId = this.getTutorialIdFromUrl(window.location.href),
            contentEl = document.body.querySelector('.tutorial__content'),
            containerEl = document.body.querySelector('.tutorial');

        let firstLinkEl = null,
            targetLinkEl = null;

        Array.prototype.slice.call(containerEl.querySelectorAll('a')).forEach((linkEl : any) => {
            const tutorialId = this.getTutorialIdFromUrl(linkEl.href);

            if (!tutorialId) {
                return;
            }

            let tutorialEl : any = cache[tutorialId] || (cache[tutorialId] = contentEl.querySelector('#tutorial-' + tutorialId));

            if (!tutorialEl) {
                return;
            }

            Object.defineProperty(tutorialEl, '__id', { value: tutorialId, configurable: true });
            Object.defineProperty(linkEl, '__tutorial', { value: tutorialEl, configurable: true });

            if (linkEl.classList.contains('tutorial__nav-link')) {
                if (!tutorialEl.__navLink) {
                    Object.defineProperty(tutorialEl, '__navLink', { value: linkEl, configurable: true });
                }

                if (tutorialId === initialTutorialId) {
                    targetLinkEl = linkEl;
                }

                if (!firstLinkEl) {
                    firstLinkEl = linkEl;
                }
            }
        });

        this.dom.delegate(containerEl, 'click', 'a', e => {
            const tutorialEl = e.target.__tutorial;

            if (tutorialEl) {
                e.preventDefault();
                this.switch(tutorialEl);
            }
        });

        this.switch((targetLinkEl || firstLinkEl).__tutorial);
    }

    private switch (tutorialEl : any) : void {
        if (this.current) {
            this.current.classList.remove('tutorial__article_current');
            this.current.__navLink.classList.remove('tutorial__nav-link_current');
        }

        tutorialEl.classList.add('tutorial__article_current');
        tutorialEl.__navLink.classList.add('tutorial__nav-link_current');

        const pageTitle = (tutorialEl.__navLink.textContent || '').trim();
        
        document.title = pageTitle ? `${ pageTitle } | Textlake` : 'Textlake – Translation Management System';

        this.current = tutorialEl;

        history.pushState(null, null, '/tutorial/' + tutorialEl.__id + window.location.search + window.location.hash);
    }
}
