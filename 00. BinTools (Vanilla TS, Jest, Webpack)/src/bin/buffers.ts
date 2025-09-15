import {
    SharedArrayBufferCtor,
    TAnyArrayBuffer,
    TTypedArray,
    U8A,
} from '../common/types';
import { BTError } from '../common/errors';
import { fmtType } from '../utils/debug';
import {
    isBinView,
    isNone,
    isSafeInt, isSharedArrayBuffer, isTypedArray,
} from '../common/type-checks';
import { isArrayBufferResizeSupported, isSharedArrayBufferGrowSupported } from '../utils/support';


const G = globalThis;

export const isSharedArrayBufferGlobal = () : boolean => {
    return !isNone(G.SharedArrayBuffer);
};

export const makeSharedArrayBufferGlobal = () : SharedArrayBufferConstructor | undefined => {
    return (G.SharedArrayBuffer = <SharedArrayBufferConstructor>SharedArrayBufferCtor);
};

export const isAnyArrayBufferResizable = (buffer : TAnyArrayBuffer, targetSize : number | null = null) : boolean => {
    if (isNone(targetSize)) {
        targetSize = null;
    } else if (!isSafeInt(targetSize) || targetSize < 0) {
        throw new BTError(
            `Expected type of argument 'targetSize' is safe ` +
            `non-negative integer, but ${ fmtType(targetSize) } given`
        );
    }

    if (buffer instanceof ArrayBuffer) {
        return (
            isArrayBufferResizeSupported &&
            buffer.resizable &&
            (
                targetSize === null ||
                targetSize <= buffer.maxByteLength
            )
        );
    }

    if (isSharedArrayBuffer(buffer)) {
        return (
            isSharedArrayBufferGrowSupported &&
            buffer.growable &&
            (
                targetSize === null ||
                buffer.byteLength <= targetSize &&  // shared can only grow
                targetSize <= buffer.maxByteLength
            )
        );
    }

    throw new BTError(
        `Expected type of argument 'buffer' is ArrayBuffer | ` +
        `SharedArrayBuffer, but ${ fmtType(buffer) } given`
    );
};

export const resizeAnyArrayBuffer = (buffer : TAnyArrayBuffer, newSize : number) : boolean => {
    if (!isAnyArrayBufferResizable(buffer, newSize)) {
        return false;
    }

    if (buffer instanceof ArrayBuffer) {
        buffer.resize(newSize);
        return true;
    }

    if (isSharedArrayBuffer(buffer)) {
        buffer.grow(newSize);
        return true;
    }

    return false;
};

export const getAnyArrayBufferMaxSize = (buffer : TAnyArrayBuffer) : number => {
    if (isAnyArrayBufferResizable(buffer)) {
        return buffer.maxByteLength;
    }

    return buffer.byteLength;
};

export const unshareArrayBuffer = (source : TAnyArrayBuffer, forceCopy : boolean = false) : ArrayBuffer => {
    if (source instanceof ArrayBuffer) {
        return forceCopy ? source.slice(0) : source;
    }

    const size = source.byteLength;

    if (size === 0) {
        return new ArrayBuffer(0);
    }

    const output = new ArrayBuffer(size);
    const srcU8A = new U8A(source);
    const outU8A = new U8A(output);

    for (let i = 0; i < size; ++i) {
        outU8A[i] = srcU8A[i];
    }

    return output;
};

export const copyAnyArrayBuffer = <
    T extends boolean,
    R = T extends true ? ArrayBuffer : TAnyArrayBuffer
> (
    source       : TAnyArrayBuffer,
    destOffset   : number,
    destSize     : number,
    sourceOffset : number,
    sourceSize   : number,
    forceUnshare : T = <T>false
) : R => {
    let ctor : ArrayBufferConstructor | SharedArrayBufferConstructor = ArrayBuffer;

    if (!forceUnshare && isSharedArrayBuffer(source) && SharedArrayBufferCtor) {
        ctor = SharedArrayBufferCtor;
    }

    const dstBuffer = new ctor(destSize);

    if (sourceSize) {
        const dstBytes = new U8A(dstBuffer, destOffset);
        const srcBytes = new U8A(source, sourceOffset, sourceSize);

        dstBytes.set(srcBytes);
    }

    return <R>dstBuffer;
};

// Slicing zero-length SharedArrayBuffer throws error:
// "TypeError: SharedArrayBuffer subclass returned this from species constructor"
// https://github.com/nodejs/node/blob/33505d1bb0802e6848a07540a6fd6ad78870f441/deps/v8/src/builtins/builtins-arraybuffer.cc#L317
export const sliceArrayBuffer = <T extends TAnyArrayBuffer>(
    buffer : T,
    start  : number             = 0,
    end    : number | undefined = undefined
) : T => {
    if (buffer.byteLength === 0 && isSharedArrayBuffer(buffer)) {
        return <T>new (<any>buffer.constructor)(0);
    }

    return <T>buffer.slice(start, end);
}

export const cloneArrayBuffer = <T extends TAnyArrayBuffer>(buffer : T) : T => {
    return <T>sliceArrayBuffer(buffer);
}

export const cloneView = <T extends DataView | TTypedArray>(view : T, cloneBuffer : boolean = false) : T => {
    if (!isBinView(view)) {
        throw new BTError(`Expected type of argument 'view' is DataView | TypedArray, but ${ fmtType(view) } given`);
    }

    const buffer = cloneBuffer ? cloneArrayBuffer(view.buffer) : view.buffer;

    return new (<any>view.constructor)(buffer, view.byteOffset, (<TTypedArray>view).length ?? view.byteLength);
};

