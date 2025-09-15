import { isProd } from '../common/env';
import { BTAssertError } from '../common/errors';
import { TypedArray } from '../common/types';


export const fmtType = (value : any) : string => {
    const strLimit = 32;
    const type = typeof value;

    if (value === undefined || value === null) {
        return `<${ value }>`;
    }

    if (type === 'string') {
        if (value.length > strLimit) {
            value = value.slice(0, strLimit) + '…';
        }

        value = value.replaceAll(`'`, `\\'`);

        return `String('${ value }')`;
    }

    if (value === Infinity || value === -Infinity || Number.isNaN(value)) {
        return String(value);
    }

    if ([ 'number', 'bigint', 'boolean' ].includes(type)) {
        return `${ value.constructor.name }(${ value })`;
    }

    if (value instanceof RegExp) {
        return `RegExp(${ value })`;
    }

    if (value instanceof Date) {
        return `Date('${ value.toISOString() }')`;
    }

    if (value instanceof TypedArray || Array.isArray(value)) {
        return `${ value.constructor.name }(${ value.length })`;
    }

    if (value instanceof ArrayBuffer || (typeof SharedArrayBuffer !== 'undefined' && value instanceof SharedArrayBuffer)) {
        return `${ value.constructor.name }(${ value.byteLength })`;
    }

    if (type === 'function') {
        if (value.name) {
            return `<function ${ value.name }>`;
        } else {
            return `<anonymous function>`;
        }
    }

    const nameTag  = Object.prototype.toString.call(value);
    const tagMatch = nameTag.match(/^\[object\s+([^\]]+)]$/i);

    if (tagMatch) {
        return `<${ tagMatch[1] }>`;
    }

    value = String(value);

    if (value.length > strLimit) {
        value = value.slice(0, strLimit) + '…';
    }

    return `<${ type } ${ value }>`;
};

export const assert = (() => {
    if (isProd) {
        return () => {};
    }

    return (isOk : any, ...messageArgs : any[]) : void => {
        if (!isOk) {
            const message = messageArgs.map(String).join(' ');

            throw new BTAssertError(message);
        }
    };
})();

export const log = (...args : any[]) : void => {
    console.log(...args);
};

export const logErr = (...args : any[]) : void => {
    console.error(...args);
};

export const logWarn = (...args : any[]) : void => {
    console.warn(...args);
};
