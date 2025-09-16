import { ModuleLoader } from '../../js/module-loader';
import { Bootstrap }    from './bootstrap.class';
import { Tutorial } from './tutorial';
import { DOM } from '../landing/ui.class';
import {Footer} from '../_shared/footer.class';

export default function init () {
    return ModuleLoader.load([
        Bootstrap, Tutorial, DOM, Footer
    ]);
}