import { Subscriber } from '../../js/subscriber.class';
import { bindMethods } from '../../js/utils';

export class Bootstrap extends Subscriber {
    public readonly isBootstrap : boolean = true;

    constructor () {
        super();
        bindMethods(this);
    }

    public init () : void {
        document.body.insertAdjacentHTML('beforeend', require('./template.html'));
    }

    public execute () : void {
        this.emit('ready');
    }
}