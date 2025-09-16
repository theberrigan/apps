import { I16A, I32A, I64A, I8A, TInt, TTypedArray, U16A, U32A, U64A, U8A } from '../common/types';
import {
    MAX_I16,
    MAX_I32,
    MAX_I64_BI,
    MAX_I8,
    MAX_U16,
    MAX_U32,
    MAX_U64_BI,
    MAX_U8,
    MIN_I16,
    MIN_I32,
    MIN_I64_BI,
    MIN_I8,
    MIN_U16,
    MIN_U32,
    MIN_U64_BI,
    MIN_U8,
} from '../common/native-types';
import { BTError } from '../common/errors';


// C-like overflow cast
// ---------------------

const createCaster = <T extends TInt>(cell : TTypedArray) => (num : T) : T => {
    cell[0] = num;

    return <T>cell[0];
};

export const i8  = createCaster<number>(new I8A(1));
export const u8  = createCaster<number>(new U8A(1));
export const i16 = createCaster<number>(new I16A(1));
export const u16 = createCaster<number>(new U16A(1));
export const i32 = createCaster<number>(new I32A(1));
export const u32 = createCaster<number>(new U32A(1));
export const i64 = createCaster<bigint>(new I64A(1));
export const u64 = createCaster<bigint>(new U64A(1));


// Clamp cast
// ---------------------

const createClampedCaster = <T extends TInt>(v1 : T, v2 : T) => (num : T) : T => {
    if (num < v1) {
        return v1;
    }

    if (num > v2) {
        return v2;
    }

    return num;
};

export const i8c  = createClampedCaster<number>(MIN_I8, MAX_I8);
export const u8c  = createClampedCaster<number>(MIN_U8, MAX_U8);
export const i16c = createClampedCaster<number>(MIN_I16, MAX_I16);
export const u16c = createClampedCaster<number>(MIN_U16, MAX_U16);
export const i32c = createClampedCaster<number>(MIN_I32, MAX_I32);
export const u32c = createClampedCaster<number>(MIN_U32, MAX_U32);
export const i64c = createClampedCaster<bigint>(MIN_I64_BI, MAX_I64_BI);
export const u64c = createClampedCaster<bigint>(MIN_U64_BI, MAX_U64_BI);


// Strict cast
// ---------------------

const createStrictCaster = <T extends TInt>(v1 : T, v2 : T, typeName : string) => (num : T) : T => {
    if (v1 <= num && num <= v2) {
        return num;
    }

    throw new BTError(`Integer ${ num } is not in range of type ${ typeName } [${ v1 }, ${ v2 }]`);
};

export const i8s  = createStrictCaster<number>(MIN_I8, MAX_I8, 'i8');
export const u8s  = createStrictCaster<number>(MIN_U8, MAX_U8, 'u8');
export const i16s = createStrictCaster<number>(MIN_I16, MAX_I16, 'i16');
export const u16s = createStrictCaster<number>(MIN_U16, MAX_U16, 'u16');
export const i32s = createStrictCaster<number>(MIN_I32, MAX_I32, 'i32');
export const u32s = createStrictCaster<number>(MIN_U32, MAX_U32, 'u32');
export const i64s = createStrictCaster<bigint>(MIN_I64_BI, MAX_I64_BI, 'i64');
export const u64s = createStrictCaster<bigint>(MIN_U64_BI, MAX_U64_BI, 'u64');


// Check int limits
// ---------------------

const createLimitChecker = <T extends TInt>(v1 : T, v2 : T) => (num : T) : num is T => {
    return v1 <= num && num <= v2;
};

export const isI8  = createLimitChecker<number>(MIN_I8, MAX_I8);
export const isU8  = createLimitChecker<number>(MIN_U8, MAX_U8);
export const isI16 = createLimitChecker<number>(MIN_I16, MAX_I16);
export const isU16 = createLimitChecker<number>(MIN_U16, MAX_U16);
export const isI32 = createLimitChecker<number>(MIN_I32, MAX_I32);
export const isU32 = createLimitChecker<number>(MIN_U32, MAX_U32);
export const isI64 = createLimitChecker<bigint>(MIN_I64_BI, MAX_I64_BI);
export const isU64 = createLimitChecker<bigint>(MIN_U64_BI, MAX_U64_BI);
