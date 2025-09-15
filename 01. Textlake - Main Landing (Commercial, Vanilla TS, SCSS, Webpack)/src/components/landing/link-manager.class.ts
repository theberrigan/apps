import {bindMethods, setLocationState} from '../../js/utils';
import {PopupManager} from './popup-manager.class';
import {ImageGallery} from './image-gallery.class';
import {DOM} from './ui.class';

export class LinkManager {
    public static get deps () : any {
        return {
            popupManager: PopupManager,
            imageGallery: ImageGallery,
            dom: DOM
        };
    }

    public popupManager : PopupManager = null;

    public imageGallery : ImageGallery = null;

    public dom : DOM = null;

    public constructor () {
        bindMethods(this);
    }

    public init () : void {
        this.dom.delegate(document.body, 'click', 'a', (e) => {
            const href = e.target.getAttribute('href') || '';

            // Scroll on top
            if (href === '/') {
                e.preventDefault();
                this.dom.scrollPage(0, true);
                setLocationState('/');

                // Scroll to element with id #...
            } else if (href[0] === '#') {
                e.preventDefault();
                this.executeHashAction(href);
            }
        });

        this.executeHashAction(location.hash, true);
    }

    private executeHashAction (hash : string, isInitial : boolean = false) : void {
        if (!hash || hash[0] !== '#' || hash.length < 2) {
            return;
        }

        if (hash.indexOf('=') !== -1) {
            const [ action, value ] = hash.slice(1).split('=');

            if (value) {
                if (action === 'popup') {
                    this.popupManager.showPopup(value);
                    setLocationState(hash);
                } else if (action === 'image') {
                    this.imageGallery.showImage(value);
                }
            }

            return;
        }

        this.dom.scrollPage(hash, !isInitial);
        setLocationState(hash);
    }
}