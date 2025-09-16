import {
    I8A,
    U8A,
    U8CA,
    I16A,
    U16A,
    I32A,
    U32A,
    I64A,
    U64A,
    F32A,
    F64A,
    MIN_INT,
    MAX_INT,
    MIN_INT_BI,
    MAX_INT_BI,
    TypedArray,
    SharedArrayBufferCtor,
} from '../../../src/main';


test('Compare type aliases with globals', async () => {
    expect(I8A).toBe(Int8Array);
    expect(U8A).toBe(Uint8Array);
    expect(U8CA).toBe(Uint8ClampedArray);
    expect(I16A).toBe(I16A);
    expect(U16A).toBe(Uint16Array);
    expect(I32A).toBe(Int32Array);
    expect(U32A).toBe(Uint32Array);
    expect(I64A).toBe(BigInt64Array);
    expect(U64A).toBe(BigUint64Array);
    expect(F32A).toBe(Float32Array);
    expect(F64A).toBe(Float64Array);

    expect(MIN_INT).toBe(Number.MIN_SAFE_INTEGER);
    expect(MAX_INT).toBe(Number.MAX_SAFE_INTEGER);
    expect(MIN_INT_BI).toBe(BigInt(Number.MIN_SAFE_INTEGER));
    expect(MAX_INT_BI).toBe(BigInt(Number.MAX_SAFE_INTEGER));

    expect(TypedArray).toBe(Object.getPrototypeOf(Uint8Array));

    expect(SharedArrayBufferCtor).toBe(SharedArrayBuffer);
});
