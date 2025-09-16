import { Bench } from 'tinybench';
import { TAnyArrayBuffer, U8A } from '../common/types';
import { i64, u32, u8 } from '../utils/type-cast';
import { isStr } from '../common/type-checks';
import { arrayAppend } from '../utils/misc';


// See also: https://web.archive.org/web/20141214075641/http://jsperf.com/typed-array-fast-filling/4
const compareArrayBufferCopying = () : Bench => {
    const copyAnyArrayBuffer1 = (
        source       : TAnyArrayBuffer,
        destOffset   : number,
        destSize     : number,
        sourceOffset : number,
        sourceSize   : number,
        forceUnshare : boolean = false
    ) : TAnyArrayBuffer => {
        const target = new ArrayBuffer(destSize);
        const srcU8A = new Uint8Array(source);
        const dstU8A = new Uint8Array(target);

        for (let i = 0; i < sourceSize; ++i) {
            dstU8A[destOffset + i] = srcU8A[sourceOffset + i];
        }

        return target;
    };

    const copyAnyArrayBuffer2 = (
        source       : TAnyArrayBuffer,
        destOffset   : number,
        destSize     : number,
        sourceOffset : number,
        sourceSize   : number,
        forceUnshare : boolean = false
    ) : TAnyArrayBuffer => {
        const target = new ArrayBuffer(destSize);
        const srcU8A = new Uint8Array(source);
        const dstU8A = new Uint8Array(target);

        dstU8A.set(srcU8A, destOffset);

        return target;
    };

    const copyAnyArrayBuffer3 = (
        source       : TAnyArrayBuffer,
        destOffset   : number,
        destSize     : number,
        sourceOffset : number,
        sourceSize   : number,
        forceUnshare : boolean = false
    ) : TAnyArrayBuffer => {
        const target = new ArrayBuffer(destSize);
        const srcU8A = new Uint8Array(source, sourceOffset, sourceSize);
        const dstU8A = new Uint8Array(target, destOffset, destSize - destOffset);

        for (let i = 0; i < Math.trunc(sourceSize / 16); i += 16) {
            dstU8A[i + 0]  = srcU8A[i + 0];
            dstU8A[i + 1]  = srcU8A[i + 1];
            dstU8A[i + 2]  = srcU8A[i + 2];
            dstU8A[i + 3]  = srcU8A[i + 3];
            dstU8A[i + 4]  = srcU8A[i + 4];
            dstU8A[i + 5]  = srcU8A[i + 5];
            dstU8A[i + 6]  = srcU8A[i + 6];
            dstU8A[i + 7]  = srcU8A[i + 7];
            dstU8A[i + 8]  = srcU8A[i + 8];
            dstU8A[i + 9]  = srcU8A[i + 9];
            dstU8A[i + 10] = srcU8A[i + 10];
            dstU8A[i + 11] = srcU8A[i + 11];
            dstU8A[i + 12] = srcU8A[i + 12];
            dstU8A[i + 13] = srcU8A[i + 13];
            dstU8A[i + 14] = srcU8A[i + 14];
            dstU8A[i + 15] = srcU8A[i + 15];
        }

        return target;
    };

    const bench = new Bench({
        name: 'Copy array buffers',
        time: 100
    });

    const destOffset = 32;

    const source1 = new Uint8Array(Array(256).fill(0).map((_, i) => i));

    bench.add('Byte by byte', () => {
        const result = copyAnyArrayBuffer1(source1.buffer, destOffset, destOffset + source1.byteLength, 0, source1.byteLength);
    });

    const source2 = new Uint8Array(Array(256).fill(0).map((_, i) => i + 128));

    bench.add('TypeArray.set', () => {
        const result = copyAnyArrayBuffer2(source2.buffer, destOffset, destOffset + source2.byteLength, 0, source2.byteLength);
    });

    const source3 = new Uint8Array(Array(256).fill(0).map((_, i) => i));

    bench.add('16 bytes by 16 bytes', () => {
        const result = copyAnyArrayBuffer3(source3.buffer, destOffset, destOffset + source3.byteLength, 0, source3.byteLength);
    });

    return bench;
};

const typeCheck = () : Bench => {
    const bench = new Bench({
        name: 'Check is var a string',
        time: 100
    });

    const str = 'copyAnyArrayBuffer1(source.buffer, 0, source.byteLength, 0, source.byteLength)';

    bench.add('Operator', () => {
        if (typeof str === 'string') {
            str.slice(1);
        }
    });

    bench.add('Function', () => {
        if (isStr(str)) {
            str.slice(1);
        }
    });

    return bench;
};

const testCasts = () : Bench => {
    const bench = new Bench({
        name: 'Manual cast vs TypedArray cast',
        time: 100
    });

    const nums = Array.from({ length: 256 }, (_, i) => BigInt(i) + 0xFFFFFFFFFFFFFFFFn);
    const u64a = new BigInt64Array(1);

    bench.add('TypedArray cast', () => {
        for (let num of nums) {
            u64a[0] = num;
            num = u64a[0];
        }
    });

    bench.add('Manual cast', () => {
        for (let num of nums) {
            num = i64(num);
        }
    });

    return bench;
}

const testFill = () : Bench => {
    const bytes = new Uint8Array(Array.from({ length: 256 }, (_, i) => i));

    const b = bytes.buffer;
    const v = new DataView(b);

    const fill1 = (view : DataView, offset : number, size : number, byte : number) : void => {
        for (let i = 0; i < size; ++i) {
            view.setUint8(offset + i, byte);
        }
    };

    const fill2 = (buffer : ArrayBuffer, offset : number, size : number, byte : number) : void => {
        if (size > 0) {
            new U8A(buffer, offset, size).fill(byte);
        }
    };

    const bench = new Bench({
        name: 'DataView fill vs U8A fill',
        time: 100
    });

    bench.add('U8A fill', () => {
        fill2(b, 0, b.byteLength, 0xCD);
    });

    bench.add('DataView fill', () => {
        fill1(v, 0, b.byteLength, 0xCD);
    });

    return bench;
}

const padArray = () : Bench => {
    const bench = new Bench({
        name: 'Pad array',
        time: 500
    });

    const fillData = Array(64).fill(0xFF);

    let bytes1 = Array.from({ length: 256 }, (_, i) => i);

    bench.add('Pad with arr1.push.apply(arr, arr2)', () => {
        Array.prototype.push.apply(bytes1, fillData);
    });

    let bytes2 = Array.from({ length: 256 }, (_, i) => i);

    bench.add('Pad with arr1.concat(arr2)', () => {
        bytes2 = bytes2.concat(fillData);
    });

    let bytes3 = Array.from({ length: 256 }, (_, i) => i);

    bench.add('Pad with [ ...arr1, ...arr2 ]', () => {
        bytes3 = [ ...bytes3, ...fillData ];
    });

    let bytes4 = Array.from({ length: 256 }, (_, i) => i);

    bench.add('Pad with arr1.push(arr2[i])', () => {
        arrayAppend(bytes4, fillData);
    });

    return bench;
}

/*
const swapBytesTest = () : Bench => {
    const bench = new Bench({
        name: 'Swap bytes',
        time: 500
    });

    let bytes1 = new U8A(Array.from({ length: 256 }, (_, i) => i));

    bench.add('Loop', () => {
        swapBytes(bytes1, 4);
    });

    let bytes2 = new U8A(Array.from({ length: 256 }, (_, i) => i));

    bench.add('U8A', () => {
        swapBytes2(bytes2, 4);
    });

    return bench;
}
*/


export const perfTests = [
    // compareArrayBufferCopying(),
    // typeCheck(),
    // testCasts(),
    testFill(),
    // swapBytesTest(),
];
