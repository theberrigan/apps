import { bindMethods, getClassName, lowerFirstLetter } from './utils';

export class ModuleLoader {
    public readonly modules : any[] = [];
    public bootstrap : any = null;

    constructor () {
        bindMethods(this);
    }

    static load (modules : any[]) {
        return (new ModuleLoader()).load(modules);
    }

    private _instantiate (cls : any, deps : any[]) : Promise<any> {
        return new Promise(resolve => {
            const instance = new cls();

            deps.forEach(dep => instance[dep.key] = dep.instance);
            const initResult : any = instance.init ? instance.init() : null;

            return initResult instanceof Promise ? initResult.then(() => resolve(instance)) : resolve(instance);
        });
    }

    public load (modules : any[]) {
        return new Promise((resolve, reject) => {
            modules = [ ...modules ];

            const resolved : any[] = [];  // { cls, instance }, { cls, instance }, { cls, instance }

            const next = () => {
                if (!modules.length) {
                    resolve(this);
                    return;
                }

                for (let i = 0; i < modules.length; i++) {
                    const cls = modules[i];

                    const deps =
                        Object
                            .entries(cls.deps || {})
                            .map(([ key, cls ]) => {
                                return {
                                    key,
                                    instance: (resolved.find(r => r.cls === cls) || { instance: null }).instance
                                };
                            });

                    if (deps.every(dep => dep.instance !== null)) {
                        this._instantiate(cls, deps).then(instance => {
                            // Object.defineProperty(
                            //     this,
                            //     lowerFirstLetter(getClassName(cls)),
                            //     {
                            //         value: instance,
                            //         configurable: true
                            //     }
                            // );

                            this.modules.push(instance);
                            instance.isBootstrap && (this.bootstrap = instance);

                            resolved.push({ cls, instance });
                            modules.splice(i, 1);
                            next();
                        });

                        return;
                    }
                }

                reject(this);
            };

            next();
        });
    }
}