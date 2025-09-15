export type I8A  = Int8Array;
export type U8A  = Uint8Array;  // node:Buffer inherited from it
export type U8CA = Uint8ClampedArray;
export type I16A = Int16Array;
export type U16A = Uint16Array;
export type I32A = Int32Array;
export type U32A = Uint32Array;
export type I64A = BigInt64Array;
export type U64A = BigUint64Array;
export type F32A = Float32Array;
export type F64A = Float64Array;

export type TTypedArray = I8A | U8A | U8CA | I16A | U16A | I32A | U32A | I64A | U64A | F32A | F64A;

export type TTypedArrayCtor = (
    Int8ArrayConstructor         |
    Uint8ArrayConstructor        |
    Uint8ClampedArrayConstructor |
    Int16ArrayConstructor        |
    Uint16ArrayConstructor       |
    Int32ArrayConstructor        |
    Uint32ArrayConstructor       |
    Float32ArrayConstructor      |
    Float64ArrayConstructor      |
    BigInt64ArrayConstructor     |
    BigUint64ArrayConstructor
);

export type TBinView = DataView | TTypedArray;

export type TAnyArrayBuffer = ArrayBuffer | SharedArrayBuffer;

export type TBytes = U8A | U8CA;

export type TAnyBin = TAnyArrayBuffer | TBinView;

export type TInt = number | bigint;

export type THexString = string;

export type TBase64 = string;

export type TBase64DataURL = string;

// DataView.prototype.[get|set]<type>
export type TDataViewGetFn<T> = (offset : number, littleEndian? : boolean) => T;
export type TDataViewSetFn<T> = (offset : number, value : T, littleEndian? : boolean) => void;

// ----------------------------------------

export const I8A  = Int8Array;
export const U8A  = Uint8Array;
export const U8CA = Uint8ClampedArray;
export const I16A = Int16Array;
export const U16A = Uint16Array;
export const I32A = Int32Array;
export const U32A = Uint32Array;
export const I64A = BigInt64Array;
export const U64A = BigUint64Array;
export const F32A = Float32Array;
export const F64A = Float64Array;

export const MIN_INT    = Number.MIN_SAFE_INTEGER;
export const MAX_INT    = Number.MAX_SAFE_INTEGER;
export const MIN_INT_BI = BigInt(MIN_INT);
export const MAX_INT_BI = BigInt(MAX_INT);

export const TypedArray = Object.getPrototypeOf(U8A);

export const SharedArrayBufferCtor : SharedArrayBufferConstructor | undefined = (() => {
    if (typeof SharedArrayBuffer !== 'undefined') {
        return SharedArrayBuffer;
    }

    if (typeof WebAssembly !== 'undefined' && typeof WebAssembly.Memory === 'function') {
        try {
            const memory = new WebAssembly.Memory({
                initial: 1,
                maximum: 1,   // required
                shared: true  // required
            });

            return <SharedArrayBufferConstructor>(memory.buffer.constructor);
        } catch (e) {}
    }

    return undefined;
})();
