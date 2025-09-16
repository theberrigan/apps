import { SharedArrayBufferCtor, TAnyBin, TBytes, U8A } from '../common/types';
import {
    isAnyArrayBuffer,
    isArrayBuffer,
    isBinView,
    isBytes,
    isNone,
    isSafeInt,
    isSharedArrayBuffer,
} from '../common/type-checks';
import { BTError } from '../common/errors';
import { ANY_BIN_TYPE } from '../common/constants';
import { fmtType } from '../utils/debug';
import { min, trunc } from '../utils/math';
import { sliceArrayBuffer } from './buffers';


export const asBytes = (source : TAnyBin) : TBytes | null => {
    // Already Uint8[Clamped]Array
    if (isBytes(source)) {
        return source;
    }

    // DataView | TypedArray | node:Buffer (Uint8Array)
    if (isBinView(source)) {
        return new U8A(source.buffer, source.byteOffset, source.byteLength);
    }

    // ArrayBuffer | SharedArrayBuffer
    if (isAnyArrayBuffer(source)) {
        return new U8A(source);
    }

    // Do not change to exception
    return null;
}

export const toBytes = (source : TAnyBin) : U8A | null => {
    // DataView | TypedArray | node:Buffer (Uint8Array)
    if (isBinView(source)) {
        return new U8A(sliceArrayBuffer(source.buffer, source.byteOffset, source.byteOffset + source.byteLength));
    }

    // ArrayBuffer | SharedArrayBuffer
    if (isAnyArrayBuffer(source)) {
        return new U8A(sliceArrayBuffer(source));
    }

    // Do not change to exception
    return null;
}

export const areBytesSame = (a : TAnyBin, b : TAnyBin, sizeToCompare : number = Infinity) : boolean => {
    const bytesA = asBytes(a);

    if (!a || !bytesA) {
        throw new BTError(`Expected type of argument 'a' is ${ ANY_BIN_TYPE }, but ${ fmtType(a) } given`);
    }

    const bytesB = asBytes(b);

    if (!b || !bytesB) {
        throw new BTError(`Expected type of argument 'b' is ${ ANY_BIN_TYPE }, but ${ fmtType(b) } given`);
    }

    if (sizeToCompare !== Infinity && (!isSafeInt(sizeToCompare) || sizeToCompare < 0)) {
        throw new BTError(
            `Expected type of argument 'byteLimit' is safe non-negative ` +
            `integer or Infinity, but ${ fmtType(sizeToCompare) } given`
        );
    }

    if (sizeToCompare === 0) {
        return true;
    }

    const sizeA = bytesA.byteLength;
    const sizeB = bytesB.byteLength;

    if (!sizeA && !sizeB) {
        return true;
    }

    if (sizeA !== sizeB && (sizeA < sizeToCompare || sizeB < sizeToCompare)) {
        return false;
    }

    sizeToCompare = min(sizeA, sizeB, sizeToCompare);

    for (let i = 0; i < sizeToCompare; ++i) {
        if (bytesA[i] !== bytesB[i]) {
            return false;
        }
    }

    return true;
};

// in-place
export const swapBytes = <T extends TAnyBin>(data : T, itemSize : number | null = null) : T => {
    const bytes = asBytes(data);

    if (!data || !bytes) {
        throw new BTError(`Expected type of argument 'data' is ${ ANY_BIN_TYPE }, but ${ fmtType(data) } given`);
    }

    const byteCount = bytes.byteLength;

    if (isNone(itemSize)) {
        itemSize = null;
    } else if (!isSafeInt(itemSize) || itemSize < 0) {
        throw new BTError(
            `Expected type of argument 'itemSize' is safe non-negative ` +
            `integer or null, but ${ fmtType(itemSize) } given`
        );
    } else if (itemSize > byteCount) {
        throw new BTError(`Argument 'itemSize' (${ itemSize }) exceeds the data size (${ byteCount })`);
    }

    if (byteCount <= 1 || itemSize === 1) {
        return data;
    }

    if (itemSize === null || itemSize === byteCount) {
        bytes.reverse();
    } else {
        const itemCount = trunc(byteCount / itemSize);
        const swapSteps = trunc(itemSize / 2);

        // TODO: convert to a single loop
        for (let i = 0; i < itemCount; ++i) {
            for (let j = 0; j < swapSteps; ++j) {
                const indexA = itemSize * i + j;
                const indexB = itemSize * i + (itemSize - j - 1);
                const temp   = bytes[indexA];

                bytes[indexA] = bytes[indexB];
                bytes[indexB] = temp;
            }
        }
    }

    return data;
};
