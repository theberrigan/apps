import {ModuleLoader} from '../../js/module-loader';
import {Bootstrap} from './bootstrap.class';

export default function init () {
    return ModuleLoader.load([
        Bootstrap
    ]);
}