import {
    MAX_INT_BI,
    MIN_INT_BI,
    SharedArrayBufferCtor,
    TAnyBin,
    TBinView,
    TBytes,
    TTypedArray,
    TypedArray, U8A, U8CA,
} from './types';


export const isNone = (value : any) : value is (undefined | null) => {
    return value === undefined || value === null;
};

export const isArray : ((value : any) => value is any[]) = Array.isArray;

export const isFinite  : ((value : any) => value is number) = <any>Number.isFinite;
export const isInt     : ((value : any) => value is number) = <any>Number.isInteger;
export const isSafeInt : ((value : any) => value is number) = <any>Number.isSafeInteger;
export const isNaN     : ((value : any) => value is number) = <any>Number.isNaN;

export const isBigInt = (value : any) : value is bigint => {
    return typeof value === 'bigint';
};

export const isSafeBigInt = (value : any) : value is bigint => {
    return typeof value === 'bigint' && MIN_INT_BI <= value && value <= MAX_INT_BI;
};

export const isNum = (value : any) : value is number => {
    return typeof value === 'number';
};

export const isAnyNum = (value : any) : value is (number | bigint) => {
    return typeof value === 'number' || typeof value === 'bigint';
};

export const isAnyInt = (value : any) : value is (number | bigint) => {
    return isInt(value) || typeof value === 'bigint';
};

export const isByteInt = (value : any) : value is number => {
    return isSafeInt(value) && 0 <= value && value <= 255;
};

export const isBool = (value : any) : value is boolean => {
    return typeof value === 'boolean';
};

export const isStr = (value : any) : value is string => {
    return typeof value === 'string';
};

export const isFn = (value : any) : value is Function => {
    return typeof value === 'function';
};

export const isPlainObject = (value : any) : value is Object => {
    return value?.constructor === Object;
};

export const isTypedArray = (value : any) : value is TTypedArray => {
    return value instanceof TypedArray;
};

export const isBinView : ((value : any) => value is TBinView) = <any>ArrayBuffer.isView;

export const isArrayBuffer = (value : any) : value is ArrayBuffer => {
    return value instanceof ArrayBuffer;
};

export const isSharedArrayBuffer = (value : any) : value is SharedArrayBuffer => {
    // SharedArrayBuffer is only available in cross-origin isolated contexts
    // globalThis.crossOriginIsolated === true also works
    return !isNone(SharedArrayBufferCtor) && value instanceof SharedArrayBufferCtor;
};

export const isAnyArrayBuffer = (value : any) : value is (ArrayBuffer | SharedArrayBuffer) => {
    return value instanceof ArrayBuffer || isSharedArrayBuffer(value);
};

export const isAnyBin = (value : any) : value is TAnyBin => {
    return isBinView(value) || isAnyArrayBuffer(value);
};

export const isByteArray = (value : any) : value is number[] => {
    return isArray(value) && value.every(n => isSafeInt(n) && n >= 0 && n <= 255);
};

export const isBytes = (value : any) : value is TBytes => {
    return value instanceof U8A || value instanceof U8CA;
};
