export const $ = require('jquery');
export const fancybox = require('./plugins/fancybox')($);

const CLASS_NAME_REGEXP : RegExp = /^(?:function|class)\s*([^{(\s]+)/i;

export const getClassName = (cls : any) : string => {
    if (cls.name) {
        return cls.name;
    }

    const match = cls.toString().match(CLASS_NAME_REGEXP);

    return match ? match[1] : '';
};

export const bindMethods = instance => {
    for (let key in instance) {
        if (typeof(instance[key]) === 'function') {
            instance[key] = instance[key].bind(instance);
        }
    }
};

export const lowerFirstLetter = (str : string) : string => {
    return (str[0] || '').toLowerCase() + (str.slice(1) || '');
};

export const removeHashFromLocation = (targetHash? : string) => {
    targetHash = (targetHash || '').slice(1);

    const [ url, currentHash ] = location.href.split('#');

    if (currentHash && (!targetHash || currentHash === targetHash)) {
        setLocationState(url);
    }
};

export const setLocationState = (state : string) => {
    if (history.replaceState) {
        history.replaceState(null, null, state);
    }
};

export const clone = entity => {
    if (Array.isArray(entity)) {
        return entity.map(item => clone(item));
    } else if (typeof(entity) === 'object') {
        const obj = {};

        for (let key in entity) {
            obj[key] = clone(entity[key]);
        }

        return obj;
    }

    return entity;
};

export const getScrollTop = () : number => {
    return window.pageYOffset || document.documentElement.scrollTop || document.body.scrollTop || 0;
};

export const isObject = entity => Object.prototype.toString.call(entity) === '[object Object]';

export const mergeObjects = (...objs) => {
    const result : any = {};

    objs.forEach(obj => {
        Object.keys(obj).forEach(key => {
            const val = obj[key];

            if (isObject(val)) {
                const exVal = result[key];
                result[key] = key in result && isObject(exVal) ? mergeObjects(exVal, val) : clone(val);
            } else {
                result[key] = clone(val);
            }
        });
    });

    return result;
};

// This is not current time stamp!
export const now : () => number = (function () {
    if (performance && performance.now) {
        return performance.now.bind(performance);  // more precisely
    }

    if (Date.now) {
        return Date.now.bind(Date);  // faster
    }

    if (+(new Date()) > 0) {
        return function () {
            return +(new Date());
        };
    }

    return function () {
        return (new Date()).getTime();  // worst
    };
})();