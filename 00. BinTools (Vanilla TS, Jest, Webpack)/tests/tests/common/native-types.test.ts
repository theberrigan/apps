import {
    POW2_7, POW2_7_BI, POW2_8, POW2_8_BI, POW2_15, POW2_15_BI, POW2_16, POW2_16_BI, POW2_31, POW2_31_BI,
    POW2_32, POW2_32_BI, POW2_63, POW2_63_BI, POW2_64, POW2_64_BI, MAX_U8, MIN_U8, MAX_U8_BI, MIN_U8_BI,
    MAX_I8, MIN_I8, MAX_I8_BI, MIN_I8_BI, MAX_U16, MIN_U16, MAX_U16_BI, MIN_U16_BI, MAX_I16, MIN_I16,
    MAX_I16_BI, MIN_I16_BI, MAX_U32, MIN_U32, MAX_U32_BI, MIN_U32_BI, MAX_I32, MIN_I32, MAX_I32_BI,
    MIN_I32_BI, MAX_U64, MIN_U64, MAX_U64_BI, MIN_U64_BI, MAX_I64, MIN_I64, MAX_I64_BI, MIN_I64_BI,
    I8_BYTES, U8_BYTES, I16_BYTES, U16_BYTES, I32_BYTES, U32_BYTES, I64_BYTES, U64_BYTES, I8_BITS, U8_BITS,
    I16_BITS, U16_BITS, I32_BITS, U32_BITS, I64_BITS, U64_BITS, PTR32_BYTES, PTR64_BYTES, PTR32_BITS, PTR64_BITS
} from '../../../src/main';


test('Check values and sizes of native numeric types', async () => {
    expect(POW2_7     === 2 ** 7         ).toBe(true);
    expect(POW2_7_BI  === BigInt(2 ** 7) ).toBe(true);
    expect(POW2_8     === 2 ** 8         ).toBe(true);
    expect(POW2_8_BI  === BigInt(2 ** 8) ).toBe(true);
    expect(POW2_15    === 2 ** 15        ).toBe(true);
    expect(POW2_15_BI === BigInt(2 ** 15)).toBe(true);
    expect(POW2_16    === 2 ** 16        ).toBe(true);
    expect(POW2_16_BI === BigInt(2 ** 16)).toBe(true);
    expect(POW2_31    === 2 ** 31        ).toBe(true);
    expect(POW2_31_BI === BigInt(2 ** 31)).toBe(true);
    expect(POW2_32    === 2 ** 32        ).toBe(true);
    expect(POW2_32_BI === BigInt(2 ** 32)).toBe(true);
    expect(POW2_63    === BigInt(2 ** 63)).toBe(true);
    expect(POW2_63_BI === BigInt(2 ** 63)).toBe(true);
    expect(POW2_64    === BigInt(2 ** 64)).toBe(true);
    expect(POW2_64_BI === BigInt(2 ** 64)).toBe(true);

    expect(MIN_U8     === 0                  ).toBe(true);
    expect(MAX_U8     === 2 ** 8 - 1         ).toBe(true);
    expect(MIN_U8_BI  === 0n                 ).toBe(true);
    expect(MAX_U8_BI  === BigInt(2 ** 8 - 1) ).toBe(true);
    expect(MIN_U16    === 0                  ).toBe(true);
    expect(MAX_U16    === (2 ** 16 - 1)      ).toBe(true);
    expect(MIN_U16_BI === 0n                 ).toBe(true);
    expect(MAX_U16_BI === BigInt(2 ** 16 - 1)).toBe(true);
    expect(MIN_U32    === 0                  ).toBe(true);
    expect(MAX_U32    === 2 ** 32 - 1        ).toBe(true);
    expect(MIN_U32_BI === 0n                 ).toBe(true);
    expect(MAX_U32_BI === BigInt(2 ** 32 - 1)).toBe(true);
    expect(MIN_U64    === 0n                 ).toBe(true);
    expect(MAX_U64    === 2n ** 64n - 1n     ).toBe(true);
    expect(MIN_U64_BI === 0n                 ).toBe(true);
    expect(MAX_U64_BI === 2n ** 64n - 1n     ).toBe(true);

    expect(MIN_I8     === -128               ).toBe(true);
    expect(MAX_I8     === 127                ).toBe(true);
    expect(MIN_I8_BI  === -128n              ).toBe(true);
    expect(MAX_I8_BI  === 127n               ).toBe(true);
    expect(MIN_I16    === -(2 ** 15)         ).toBe(true);
    expect(MAX_I16    === 2 ** 15 - 1        ).toBe(true);
    expect(MIN_I16_BI === BigInt(-(2 ** 15)) ).toBe(true);
    expect(MAX_I16_BI === BigInt(2 ** 15 - 1)).toBe(true);
    expect(MIN_I32    === -(2 ** 31)         ).toBe(true);
    expect(MAX_I32    === 2 ** 31 - 1        ).toBe(true);
    expect(MIN_I32_BI === BigInt(-(2 ** 31)) ).toBe(true);
    expect(MAX_I32_BI === BigInt(2 ** 31 - 1)).toBe(true);
    expect(MIN_I64    === -(2n ** 63n)       ).toBe(true);
    expect(MAX_I64    === 2n ** 63n - 1n     ).toBe(true);
    expect(MIN_I64_BI === -(2n ** 63n)       ).toBe(true);
    expect(MAX_I64_BI === 2n ** 63n - 1n     ).toBe(true);

    expect(U8_BYTES   ).toBe(1);
    expect(I8_BYTES   ).toBe(1);
    expect(I16_BYTES  ).toBe(2);
    expect(U16_BYTES  ).toBe(2);
    expect(I32_BYTES  ).toBe(4);
    expect(U32_BYTES  ).toBe(4);
    expect(I64_BYTES  ).toBe(8);
    expect(U64_BYTES  ).toBe(8);
    expect(I8_BITS    ).toBe(8);
    expect(U8_BITS    ).toBe(8);
    expect(I16_BITS   ).toBe(16);
    expect(U16_BITS   ).toBe(16);
    expect(I32_BITS   ).toBe(32);
    expect(U32_BITS   ).toBe(32);
    expect(I64_BITS   ).toBe(64);
    expect(U64_BITS   ).toBe(64);
    expect(PTR32_BYTES).toBe(4);
    expect(PTR64_BYTES).toBe(8);
    expect(PTR32_BITS ).toBe(32);
    expect(PTR64_BITS ).toBe(64);
});
