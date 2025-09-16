// Classes
import { ModuleLoader }    from '../../js/module-loader';
import { Bootstrap }       from './bootstrap.class';
import { DOM }             from './ui.class';
import { LanguageManager } from './language-manager.class';
import { ImageGallery }    from './image-gallery.class';
import { Panel }           from './panel.class';
import { Nav }             from './nav.class';
import { VideoGallery }    from './video-gallery.class';
import { PopupManager }    from './popup-manager.class';
import { Workflow }        from './workflow.class';
import { LinkManager }     from './link-manager.class';
import { Pricing }         from './pricing.class';
import { CookiePanel }     from './cookie-panel.class';
import { Footer }          from '../_shared/footer.class';
import { Network }         from './network.class';


export default function init () {
    return ModuleLoader.load([
        Bootstrap, DOM, Network, LanguageManager, Panel, Nav, CookiePanel,
        ImageGallery, VideoGallery, Pricing, Workflow, PopupManager, LinkManager, Footer
    ]);
}