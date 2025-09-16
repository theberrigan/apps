import {
    i16, i16c, i16s,
    i32, i32c, i32s, i64, i64c, i64s,
    i8, i8c, i8s, isI16, isI32, isI64, isI8, isU16, isU32, isU64, isU8,
    MAX_I16,
    MAX_I32, MAX_I64,
    MAX_I8,
    MAX_U16,
    MAX_U32, MAX_U64,
    MAX_U8,
    MIN_I16,
    MIN_I32, MIN_I64,
    MIN_I8,
    MIN_U16,
    MIN_U32, MIN_U64,
    MIN_U8,
    u16, u16c, u16s,
    u32, u32c, u32s, u64, u64c, u64s,
    u8, u8c, u8s,
} from '../../../src/main';


test('Test i8()', () => {
    expect(i8(0)).toBe(0);
    expect(i8(MAX_I8 + 1)).toBe(MIN_I8);
    expect(i8(MIN_I8 - 1)).toBe(MAX_I8);
});

test('Test u8()', () => {
    expect(u8(0)).toBe(0);
    expect(u8(MAX_U8 + 1)).toBe(MIN_U8);
    expect(u8(MIN_U8 - 1)).toBe(MAX_U8);
});

test('Test i16()', () => {
    expect(i16(0)).toBe(0);
    expect(i16(MAX_I16 + 1)).toBe(MIN_I16);
    expect(i16(MIN_I16 - 1)).toBe(MAX_I16);
});

test('Test u16()', () => {
    expect(u16(0)).toBe(0);
    expect(u16(MAX_U16 + 1)).toBe(MIN_U16);
    expect(u16(MIN_U16 - 1)).toBe(MAX_U16);
});

test('Test i32()', () => {
    expect(i32(0)).toBe(0);
    expect(i32(MAX_I32 + 1)).toBe(MIN_I32);
    expect(i32(MIN_I32 - 1)).toBe(MAX_I32);
});

test('Test u32()', () => {
    expect(u32(0)).toBe(0);
    expect(u32(MAX_U32 + 1)).toBe(MIN_U32);
    expect(u32(MIN_U32 - 1)).toBe(MAX_U32);
});

test('Test i64()', () => {
    expect(i64(0n) === 0n).toBe(true);
    expect(i64(MAX_I64 + 1n) === MIN_I64).toBe(true);
    expect(i64(MIN_I64 - 1n) === MAX_I64).toBe(true);
});

test('Test u64()', () => {
    expect(u64(0n) === 0n).toBe(true);
    expect(u64(MAX_U64 + 1n) === MIN_U64).toBe(true);
    expect(u64(MIN_U64 - 1n) === MAX_U64).toBe(true);
});

// ------------------------------------------------------------------------

test('Test i8c()', () => {
    expect(i8c(0)).toBe(0);
    expect(i8c(MAX_I8 + 1)).toBe(MAX_I8);
    expect(i8c(MIN_I8 - 1)).toBe(MIN_I8);
});

test('Test u8c()', () => {
    expect(u8c(0)).toBe(0);
    expect(u8c(MAX_U8 + 1)).toBe(MAX_U8);
    expect(u8c(MIN_U8 - 1)).toBe(MIN_U8);
});

test('Test i16c()', () => {
    expect(i16c(0)).toBe(0);
    expect(i16c(MAX_I16 + 1)).toBe(MAX_I16);
    expect(i16c(MIN_I16 - 1)).toBe(MIN_I16);
});

test('Test u16c()', () => {
    expect(u16c(0)).toBe(0);
    expect(u16c(MAX_U16 + 1)).toBe(MAX_U16);
    expect(u16c(MIN_U16 - 1)).toBe(MIN_U16);
});

test('Test i32c()', () => {
    expect(i32c(0)).toBe(0);
    expect(i32c(MAX_I32 + 1)).toBe(MAX_I32);
    expect(i32c(MIN_I32 - 1)).toBe(MIN_I32);
});

test('Test u32c()', () => {
    expect(u32c(0)).toBe(0);
    expect(u32c(MAX_U32 + 1)).toBe(MAX_U32);
    expect(u32c(MIN_U32 - 1)).toBe(MIN_U32);
});

test('Test i64c()', () => {
    expect(i64c(0n) === 0n).toBe(true);
    expect(i64c(MAX_I64 + 1n) === MAX_I64).toBe(true);
    expect(i64c(MIN_I64 - 1n) === MIN_I64).toBe(true);
});

test('Test u64c()', () => {
    expect(u64c(0n) === 0n).toBe(true);
    expect(u64c(MAX_U64 + 1n) === MAX_U64).toBe(true);
    expect(u64c(MIN_U64 - 1n) === MIN_U64).toBe(true);
});

// ------------------------------------------------------------------------

test('Test i8s()', () => {
    expect(i8s(0)).toBe(0);
    expect(i8s(MAX_I8)).toBe(MAX_I8);
    expect(i8s(MIN_I8)).toBe(MIN_I8);
    expect(() => i8s(MAX_I8 + 1)).toThrow(/is not in range of type i8/);
    expect(() => i8s(MIN_I8 - 1)).toThrow(/is not in range of type i8/);
});

test('Test u8s()', () => {
    expect(u8s(0)).toBe(0);
    expect(u8s(MAX_U8)).toBe(MAX_U8);
    expect(u8s(MIN_U8)).toBe(MIN_U8);
    expect(() => u8s(MAX_U8 + 1)).toThrow(/is not in range of type u8/);
    expect(() => u8s(MIN_U8 - 1)).toThrow(/is not in range of type u8/);
});

test('Test i16s()', () => {
    expect(i16s(0)).toBe(0);
    expect(i16s(MAX_I16)).toBe(MAX_I16);
    expect(i16s(MIN_I16)).toBe(MIN_I16);
    expect(() => i16s(MAX_I16 + 1)).toThrow(/is not in range of type i16/);
    expect(() => i16s(MIN_I16 - 1)).toThrow(/is not in range of type i16/);
});

test('Test u16s()', () => {
    expect(u16s(0)).toBe(0);
    expect(u16s(MAX_U16)).toBe(MAX_U16);
    expect(u16s(MIN_U16)).toBe(MIN_U16);
    expect(() => u16s(MAX_U16 + 1)).toThrow(/is not in range of type u16/);
    expect(() => u16s(MIN_U16 - 1)).toThrow(/is not in range of type u16/);
});

test('Test i32s()', () => {
    expect(i32s(0)).toBe(0);
    expect(i32s(MAX_I32)).toBe(MAX_I32);
    expect(i32s(MIN_I32)).toBe(MIN_I32);
    expect(() => i32s(MAX_I32 + 1)).toThrow(/is not in range of type i32/);
    expect(() => i32s(MIN_I32 - 1)).toThrow(/is not in range of type i32/);
});

test('Test u32s()', () => {
    expect(u32s(0)).toBe(0);
    expect(u32s(MAX_U32)).toBe(MAX_U32);
    expect(u32s(MIN_U32)).toBe(MIN_U32);
    expect(() => u32s(MAX_U32 + 1)).toThrow(/is not in range of type u32/);
    expect(() => u32s(MIN_U32 - 1)).toThrow(/is not in range of type u32/);
});

test('Test i64s()', () => {
    expect(i64s(0n)).toBe(0n);
    expect(i64s(MAX_I64) === MAX_I64).toBe(true);
    expect(i64s(MIN_I64) === MIN_I64).toBe(true);
    expect(() => i64s(MAX_I64 + 1n)).toThrow(/is not in range of type i64/);
    expect(() => i64s(MIN_I64 - 1n)).toThrow(/is not in range of type i64/);
});

test('Test u64s()', () => {
    expect(u64s(0n)).toBe(0n);
    expect(u64s(MAX_U64) === MAX_U64).toBe(true);
    expect(u64s(MIN_U64) === MIN_U64).toBe(true);
    expect(() => u64s(MAX_U64 + 1n)).toThrow(/is not in range of type u64/);
    expect(() => u64s(MIN_U64 - 1n)).toThrow(/is not in range of type u64/);
});

// ------------------------------------------------------------------------

test('Test isI8()', () => {
    expect(isI8(0)).toBe(true);
    expect(isI8(MIN_I8)).toBe(true);
    expect(isI8(MIN_I8 - 1)).toBe(false);
    expect(isI8(MAX_I8)).toBe(true);
    expect(isI8(MAX_I8 + 1)).toBe(false);
});

test('Test isU8()', () => {
    expect(isU8(0)).toBe(true);
    expect(isU8(MIN_U8)).toBe(true);
    expect(isU8(MIN_U8 - 1)).toBe(false);
    expect(isU8(MAX_U8)).toBe(true);
    expect(isU8(MAX_U8 + 1)).toBe(false);
});

test('Test isI16()', () => {
    expect(isI16(0)).toBe(true);
    expect(isI16(MIN_I16)).toBe(true);
    expect(isI16(MIN_I16 - 1)).toBe(false);
    expect(isI16(MAX_I16)).toBe(true);
    expect(isI16(MAX_I16 + 1)).toBe(false);
});

test('Test isU16()', () => {
    expect(isU16(0)).toBe(true);
    expect(isU16(MIN_U16)).toBe(true);
    expect(isU16(MIN_U16 - 1)).toBe(false);
    expect(isU16(MAX_U16)).toBe(true);
    expect(isU16(MAX_U16 + 1)).toBe(false);
});

test('Test isI32()', () => {
    expect(isI32(0)).toBe(true);
    expect(isI32(MIN_I32)).toBe(true);
    expect(isI32(MIN_I32 - 1)).toBe(false);
    expect(isI32(MAX_I32)).toBe(true);
    expect(isI32(MAX_I32 + 1)).toBe(false);
});

test('Test isU32()', () => {
    expect(isU32(0)).toBe(true);
    expect(isU32(MIN_U32)).toBe(true);
    expect(isU32(MIN_U32 - 1)).toBe(false);
    expect(isU32(MAX_U32)).toBe(true);
    expect(isU32(MAX_U32 + 1)).toBe(false);
});

test('Test isI64()', () => {
    expect(isI64(0n)).toBe(true);
    expect(isI64(MIN_I64)).toBe(true);
    expect(isI64(MIN_I64 - 1n)).toBe(false);
    expect(isI64(MAX_I64)).toBe(true);
    expect(isI64(MAX_I64 + 1n)).toBe(false);
});

test('Test isU64()', () => {
    expect(isU64(0n)).toBe(true);
    expect(isU64(MIN_U64)).toBe(true);
    expect(isU64(MIN_U64 - 1n)).toBe(false);
    expect(isU64(MAX_U64)).toBe(true);
    expect(isU64(MAX_U64 + 1n)).toBe(false);
});
