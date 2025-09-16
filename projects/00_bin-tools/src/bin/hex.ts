import { TAnyBin, TBytes, THexString, U8A } from '../common/types';
import { BTError } from '../common/errors';
import { fmtType } from '../utils/debug';
import { ANY_BIN_TYPE } from '../common/constants';
import { bigIntToBin, binToBigInt } from './bigint';
import { isAnyBin, isArray, isByteArray, isInt, isStr } from '../common/type-checks';
import { condenseString } from '../utils/misc';
import { asBytes } from './bytes';


export const hexInt = (value : string) : number => {
    return parseInt(value, 16);
};

export const isHex = (value : any, oneByteAtLeast : boolean = false) : value is THexString => {
    if (!isStr(value)) {
        return false;
    }

    value = condenseString(value);

    if (!value.length) {
        return !oneByteAtLeast;
    }

    // has at least 1 byte
    return /^([\da-f]{2})+$/i.test(value);
};

export const _hexToBin = (hex : THexString) : U8A => {
    hex = condenseString(hex);

    if (!hex.length) {
        return new U8A(0);
    }

    return new U8A(hex.match(/../g).map(hexInt));
};

export const hexToBin = (hex : THexString) : U8A => {
    if (!isHex(hex, false)) {
        throw new BTError(`Expected type of argument 'hex' is string, but ${ fmtType(hex) } given`);
    }

    return _hexToBin(hex);
};

export const _binToHex = (source : TBytes | number[], upperCase : boolean = false, sep : string = '') : string => {
    source = isArray(source) ? source : [ ...asBytes(source) ];

    const bytes = source.map(b => numToHex(b, upperCase, 1, false));

    return bytes.join(sep);
};

export const binToHex = (source : TAnyBin | number[], upperCase : boolean = false, sep : string = '') : string => {
    if (isAnyBin(source)) {
        source = [ ...asBytes(source) ];
    } else if (!isByteArray(source)) {
        throw new BTError(
            `Expected type of argument 'source' is ${ ANY_BIN_TYPE } ` +
            `| number[], but ${ fmtType(source) } given`
        );
    }

    return _binToHex(source, upperCase, sep);
};

export const numToHex = (
    num       : number,
    upperCase : boolean = false,
    byteCount : number  = 0,  // -1 - don't pad, 0 - auto
    addPrefix : boolean = false,
    prefix    : string  = '0x',
) : string => {
    if (!isInt(num)) {
        throw new BTError(
            `Expected type of argument 'num' is integer, ` +
            `but ${ fmtType(num) } given`
        );
    }

    const sign = num < 0 ? '-' : '';

    if (sign) {
        num = -num;
    }

    let hex = num.toString(16);

    if (upperCase) {
        hex = hex.toUpperCase();
    }

    let paddedSize = 0;

    // floor(log(num, 16)) + 1 -- bytes required to store num
    if (byteCount === 0) {
        paddedSize = hex.length + hex.length % 2;
    } else if (byteCount > 0) {
        paddedSize = byteCount * 2;
    }

    if (paddedSize > 0) {
        hex = hex.padStart(paddedSize, '0')
    }

    return sign + (addPrefix ? prefix : '') + hex;
};

export const bigIntToHex = (
    num       : bigint,
    size      : number | null = null,
    bigEndian : boolean       = false,
    upperCase : boolean       = false,
    sep       : string        = ''
) : string => {
    return binToHex(bigIntToBin(num, size, bigEndian), upperCase, sep);
};

export const hexToBigInt = (
    hex       : THexString,
    isSigned  : boolean = false,
    bigEndian : boolean = false,
) : bigint => {
    return binToBigInt(hexToBin(hex), isSigned, bigEndian);
};
