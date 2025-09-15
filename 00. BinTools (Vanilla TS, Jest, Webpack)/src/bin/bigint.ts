import { BTError } from '../common/errors';
import { fmtType } from '../utils/debug';
import { TAnyBin, U8A } from '../common/types';
import { ANY_BIN_TYPE } from '../common/constants';
import { isBigInt, isNone } from '../common/type-checks';
import { arrayAppend } from '../utils/misc';
import { asBytes } from './bytes';


export const bigIntToBin = (num : bigint, size : number | null = null, bigEndian : boolean = false) : U8A => {
    if (!isBigInt(num)) {
        throw new BTError(`Expected type of argument 'num' is BigInt, but ${ fmtType(num) } given`);
    }

    if (isNone(size)) {
        size = null;
    }

    if (num === 0n) {
        return new U8A(size ?? 1);
    }

    const isNegative = num < 0n;
    const fillByte   = isNegative ? 0xFF : 0x00;

    let quotient = isNegative ? -num : num;
    let bytes    = [];  // little endian
    let byte     = 0;
    let shift    = 0;

    // LSB -> MSB
    while (true) {
        const bit = Number(quotient % 2n);

        byte |= bit << shift;

        if (shift === 7) {
            bytes.push(byte);
            byte  = 0;
            shift = 0;
        } else {
            shift++;
        }

        quotient /= 2n;

        if (quotient === 0n) {
            if (byte > 0) {
                bytes.push(byte);
            }

            break;
        }
    }

    let byteCount = bytes.length;

    if (isNegative) {
        let carry = 1;

        for (let i = 0; i < byteCount; ++i) {
            const oldByte = bytes[i];

            let newByte = 0;

            for (let shift = 0; shift < 8; ++shift) {
                let bit = (oldByte >> shift) & 1;

                bit = (bit === 1 ? 0 : 1) + carry;

                if (bit === 1) {
                    carry = 0;
                    newByte |= bit << shift;
                } else if (bit === 2) {
                    carry = 1;
                }
            }

            bytes[i] = newByte;
        }

        if (bytes[byteCount - 1] < 0x80) {
            bytes.push(fillByte);
            byteCount++;
        }
    }

    if (size !== null) {
        if (byteCount > size) {
            throw new BTError(`${ size } bytes is not enough to encode ${ num }n`);
        }

        if (byteCount < size) {
            arrayAppend(bytes, Array(size - byteCount).fill(fillByte));
        }
    }

    if (bigEndian) {
        bytes.reverse();
    }

    return new U8A(bytes);
};

export const binToBigInt = (source : TAnyBin, isSigned : boolean = false, bigEndian : boolean = false) : bigint => {
    const bytes = asBytes(source);

    if (isNone(bytes)) {
        throw new BTError(`Expected type of argument 'source' is ${ ANY_BIN_TYPE }, but ${ fmtType(source) } given`);
    }

    const byteCount = bytes.length;

    if (!byteCount) {
        return 0n;
    }

    // we work with little-endian arrays
    if (bigEndian) {
        bytes.reverse();
    }

    let result = 0n;
    let shift  = 0n;

    for (let byte of bytes) {
        result |= BigInt(byte) << shift;

        shift += 8n;
    }

    if (isSigned) {
        const bitCount = 8n * BigInt(byteCount);

        const isNegative = result & (1n << (bitCount - 1n));

        if (isNegative) {
            result -= 1n;
            result ^= 2n ** bitCount - 1n;
            result = -result;
        }
    }

    return result;
};
