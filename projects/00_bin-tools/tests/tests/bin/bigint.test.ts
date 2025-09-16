import { bigIntToBin, binToBigInt } from '../../../src/main';


test('Test bigIntToBin() and binToBigInt()', () => {
    expect(() => bigIntToBin(256n, 1)).toThrow(/bytes is not enough to encode/);

    expect(() => bigIntToBin(<any>undefined)                    ).toThrow(/Expected type of argument 'num' is BigInt/);
    expect(() => bigIntToBin(<any>null)                         ).toThrow(/Expected type of argument 'num' is BigInt/);
    expect(() => bigIntToBin(<any>true)                         ).toThrow(/Expected type of argument 'num' is BigInt/);
    expect(() => bigIntToBin(<any>false)                        ).toThrow(/Expected type of argument 'num' is BigInt/);
    expect(() => bigIntToBin(<any>(NaN)                        )).toThrow(/Expected type of argument 'num' is BigInt/);
    expect(() => bigIntToBin(<any>(Infinity)                   )).toThrow(/Expected type of argument 'num' is BigInt/);
    expect(() => bigIntToBin(<any>(-Infinity)                  )).toThrow(/Expected type of argument 'num' is BigInt/);
    expect(() => bigIntToBin(<any>(Number.MIN_SAFE_INTEGER - 1))).toThrow(/Expected type of argument 'num' is BigInt/);
    expect(() => bigIntToBin(<any>(Number.MAX_SAFE_INTEGER + 1))).toThrow(/Expected type of argument 'num' is BigInt/);
    expect(() => bigIntToBin(<any>(0)                          )).toThrow(/Expected type of argument 'num' is BigInt/);
    expect(() => bigIntToBin(<any>(1.0)                        )).toThrow(/Expected type of argument 'num' is BigInt/);
    expect(() => bigIntToBin(<any>(1.5)                        )).toThrow(/Expected type of argument 'num' is BigInt/);
    expect(() => bigIntToBin(<any>('0')                        )).toThrow(/Expected type of argument 'num' is BigInt/);
    expect(() => bigIntToBin(<any>('')                         )).toThrow(/Expected type of argument 'num' is BigInt/);
    expect(() => bigIntToBin(<any>({})                         )).toThrow(/Expected type of argument 'num' is BigInt/);
    expect(() => bigIntToBin(<any>(Object.create(null))        )).toThrow(/Expected type of argument 'num' is BigInt/);
    expect(() => bigIntToBin(<any>([])                         )).toThrow(/Expected type of argument 'num' is BigInt/);
    expect(() => bigIntToBin(<any>(Array())                    )).toThrow(/Expected type of argument 'num' is BigInt/);
    expect(() => bigIntToBin(<any>(/regex/)                    )).toThrow(/Expected type of argument 'num' is BigInt/);
    expect(() => bigIntToBin(<any>(Symbol())                   )).toThrow(/Expected type of argument 'num' is BigInt/);
    expect(() => bigIntToBin(<any>(() => {})                   )).toThrow(/Expected type of argument 'num' is BigInt/);
    expect(() => bigIntToBin(<any>(function () {})             )).toThrow(/Expected type of argument 'num' is BigInt/);
    expect(() => bigIntToBin(<any>(function *() {})            )).toThrow(/Expected type of argument 'num' is BigInt/);
    expect(() => bigIntToBin(<any>(class X {})                 )).toThrow(/Expected type of argument 'num' is BigInt/);
    expect(() => bigIntToBin(<any>(new (class X {}))           )).toThrow(/Expected type of argument 'num' is BigInt/);
    expect(() => bigIntToBin(<any>(new Error('error'))         )).toThrow(/Expected type of argument 'num' is BigInt/);
    expect(() => bigIntToBin(<any>(new Set())                  )).toThrow(/Expected type of argument 'num' is BigInt/);
    expect(() => bigIntToBin(<any>(new Map())                  )).toThrow(/Expected type of argument 'num' is BigInt/);
    expect(() => bigIntToBin(<any>(new Date())                 )).toThrow(/Expected type of argument 'num' is BigInt/);

    expect(() => binToBigInt(<any>undefined)                    ).toThrow(/Expected type of argument 'source' is/);
    expect(() => binToBigInt(<any>null)                         ).toThrow(/Expected type of argument 'source' is/);
    expect(() => binToBigInt(<any>true)                         ).toThrow(/Expected type of argument 'source' is/);
    expect(() => binToBigInt(<any>false)                        ).toThrow(/Expected type of argument 'source' is/);
    expect(() => binToBigInt(<any>(NaN)                        )).toThrow(/Expected type of argument 'source' is/);
    expect(() => binToBigInt(<any>(Infinity)                   )).toThrow(/Expected type of argument 'source' is/);
    expect(() => binToBigInt(<any>(-Infinity)                  )).toThrow(/Expected type of argument 'source' is/);
    expect(() => binToBigInt(<any>(Number.MIN_SAFE_INTEGER - 1))).toThrow(/Expected type of argument 'source' is/);
    expect(() => binToBigInt(<any>(Number.MAX_SAFE_INTEGER + 1))).toThrow(/Expected type of argument 'source' is/);
    expect(() => binToBigInt(<any>(0)                          )).toThrow(/Expected type of argument 'source' is/);
    expect(() => binToBigInt(<any>(1.0)                        )).toThrow(/Expected type of argument 'source' is/);
    expect(() => binToBigInt(<any>(1.5)                        )).toThrow(/Expected type of argument 'source' is/);
    expect(() => binToBigInt(<any>('0')                        )).toThrow(/Expected type of argument 'source' is/);
    expect(() => binToBigInt(<any>('')                         )).toThrow(/Expected type of argument 'source' is/);
    expect(() => binToBigInt(<any>({})                         )).toThrow(/Expected type of argument 'source' is/);
    expect(() => binToBigInt(<any>(Object.create(null))        )).toThrow(/Expected type of argument 'source' is/);
    expect(() => binToBigInt(<any>([])                         )).toThrow(/Expected type of argument 'source' is/);
    expect(() => binToBigInt(<any>(Array())                    )).toThrow(/Expected type of argument 'source' is/);
    expect(() => binToBigInt(<any>(/regex/)                    )).toThrow(/Expected type of argument 'source' is/);
    expect(() => binToBigInt(<any>(Symbol())                   )).toThrow(/Expected type of argument 'source' is/);
    expect(() => binToBigInt(<any>(() => {})                   )).toThrow(/Expected type of argument 'source' is/);
    expect(() => binToBigInt(<any>(function () {})             )).toThrow(/Expected type of argument 'source' is/);
    expect(() => binToBigInt(<any>(function *() {})            )).toThrow(/Expected type of argument 'source' is/);
    expect(() => binToBigInt(<any>(class X {})                 )).toThrow(/Expected type of argument 'source' is/);
    expect(() => binToBigInt(<any>(new (class X {}))           )).toThrow(/Expected type of argument 'source' is/);
    expect(() => binToBigInt(<any>(new Error('error'))         )).toThrow(/Expected type of argument 'source' is/);
    expect(() => binToBigInt(<any>(new Set())                  )).toThrow(/Expected type of argument 'source' is/);
    expect(() => binToBigInt(<any>(new Map())                  )).toThrow(/Expected type of argument 'source' is/);
    expect(() => binToBigInt(<any>(new Date())                 )).toThrow(/Expected type of argument 'source' is/);

    // Positive tests generated by /misc/scripts/test_gen.py
    // -----------------------------------------------------------------------------------------------------------------

    let bytes : Uint8Array;
    let num : bigint;
    let size : number;
    let bigEndian : boolean;
    let isSigned : boolean;

    num = 0n;
    size = null;
    bigEndian = false;
    isSigned = false;
    bytes = bigIntToBin(num, size, bigEndian);
    expect(bytes).toEqual(new Uint8Array([ 0x00 ]));
    expect(binToBigInt(bytes, isSigned, bigEndian) === num).toBe(true);

    num = 1n;
    size = null;
    bigEndian = false;
    isSigned = false;
    bytes = bigIntToBin(num, size, bigEndian);
    expect(bytes).toEqual(new Uint8Array([ 0x01 ]));
    expect(binToBigInt(bytes, isSigned, bigEndian) === num).toBe(true);

    num = -1n;
    size = null;
    bigEndian = false;
    isSigned = true;
    bytes = bigIntToBin(num, size, bigEndian);
    expect(bytes).toEqual(new Uint8Array([ 0xff ]));
    expect(binToBigInt(bytes, isSigned, bigEndian) === num).toBe(true);

    num = 255n;
    size = null;
    bigEndian = false;
    isSigned = false;
    bytes = bigIntToBin(num, size, bigEndian);
    expect(bytes).toEqual(new Uint8Array([ 0xff ]));
    expect(binToBigInt(bytes, isSigned, bigEndian) === num).toBe(true);

    num = -255n;
    size = null;
    bigEndian = false;
    isSigned = true;
    bytes = bigIntToBin(num, size, bigEndian);
    expect(bytes).toEqual(new Uint8Array([ 0x01, 0xff ]));
    expect(binToBigInt(bytes, isSigned, bigEndian) === num).toBe(true);

    num = 256n;
    size = null;
    bigEndian = false;
    isSigned = false;
    bytes = bigIntToBin(num, size, bigEndian);
    expect(bytes).toEqual(new Uint8Array([ 0x00, 0x01 ]));
    expect(binToBigInt(bytes, isSigned, bigEndian) === num).toBe(true);

    num = -256n;
    size = null;
    bigEndian = false;
    isSigned = true;
    bytes = bigIntToBin(num, size, bigEndian);
    expect(bytes).toEqual(new Uint8Array([ 0x00, 0xff ]));
    expect(binToBigInt(bytes, isSigned, bigEndian) === num).toBe(true);

    num = 32767n;
    size = null;
    bigEndian = false;
    isSigned = false;
    bytes = bigIntToBin(num, size, bigEndian);
    expect(bytes).toEqual(new Uint8Array([ 0xff, 0x7f ]));
    expect(binToBigInt(bytes, isSigned, bigEndian) === num).toBe(true);

    num = -32767n;
    size = null;
    bigEndian = false;
    isSigned = true;
    bytes = bigIntToBin(num, size, bigEndian);
    expect(bytes).toEqual(new Uint8Array([ 0x01, 0x80 ]));
    expect(binToBigInt(bytes, isSigned, bigEndian) === num).toBe(true);

    num = 33023n;
    size = null;
    bigEndian = false;
    isSigned = false;
    bytes = bigIntToBin(num, size, bigEndian);
    expect(bytes).toEqual(new Uint8Array([ 0xff, 0x80 ]));
    expect(binToBigInt(bytes, isSigned, bigEndian) === num).toBe(true);

    num = -33023n;
    size = null;
    bigEndian = false;
    isSigned = true;
    bytes = bigIntToBin(num, size, bigEndian);
    expect(bytes).toEqual(new Uint8Array([ 0x01, 0x7f, 0xff ]));
    expect(binToBigInt(bytes, isSigned, bigEndian) === num).toBe(true);

    num = 4294967295n;
    size = null;
    bigEndian = false;
    isSigned = false;
    bytes = bigIntToBin(num, size, bigEndian);
    expect(bytes).toEqual(new Uint8Array([ 0xff, 0xff, 0xff, 0xff ]));
    expect(binToBigInt(bytes, isSigned, bigEndian) === num).toBe(true);

    num = -4294967295n;
    size = null;
    bigEndian = false;
    isSigned = true;
    bytes = bigIntToBin(num, size, bigEndian);
    expect(bytes).toEqual(new Uint8Array([ 0x01, 0x00, 0x00, 0x00, 0xff ]));
    expect(binToBigInt(bytes, isSigned, bigEndian) === num).toBe(true);

    num = 4294967296n;
    size = null;
    bigEndian = false;
    isSigned = false;
    bytes = bigIntToBin(num, size, bigEndian);
    expect(bytes).toEqual(new Uint8Array([ 0x00, 0x00, 0x00, 0x00, 0x01 ]));
    expect(binToBigInt(bytes, isSigned, bigEndian) === num).toBe(true);

    num = -4294967296n;
    size = null;
    bigEndian = false;
    isSigned = true;
    bytes = bigIntToBin(num, size, bigEndian);
    expect(bytes).toEqual(new Uint8Array([ 0x00, 0x00, 0x00, 0x00, 0xff ]));
    expect(binToBigInt(bytes, isSigned, bigEndian) === num).toBe(true);

    num = 18446744073709551615n;
    size = null;
    bigEndian = false;
    isSigned = false;
    bytes = bigIntToBin(num, size, bigEndian);
    expect(bytes).toEqual(new Uint8Array([ 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff ]));
    expect(binToBigInt(bytes, isSigned, bigEndian) === num).toBe(true);

    num = -18446744073709551615n;
    size = null;
    bigEndian = false;
    isSigned = true;
    bytes = bigIntToBin(num, size, bigEndian);
    expect(bytes).toEqual(new Uint8Array([ 0x01, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0xff ]));
    expect(binToBigInt(bytes, isSigned, bigEndian) === num).toBe(true);

    num = 18446744073709551616n;
    size = null;
    bigEndian = false;
    isSigned = false;
    bytes = bigIntToBin(num, size, bigEndian);
    expect(bytes).toEqual(new Uint8Array([ 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x01 ]));
    expect(binToBigInt(bytes, isSigned, bigEndian) === num).toBe(true);

    num = -18446744073709551616n;
    size = null;
    bigEndian = false;
    isSigned = true;
    bytes = bigIntToBin(num, size, bigEndian);
    expect(bytes).toEqual(new Uint8Array([ 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0xff ]));
    expect(binToBigInt(bytes, isSigned, bigEndian) === num).toBe(true);

    num = 340282366920938463463374607431768211455n;
    size = null;
    bigEndian = false;
    isSigned = false;
    bytes = bigIntToBin(num, size, bigEndian);
    expect(bytes).toEqual(new Uint8Array([ 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff ]));
    expect(binToBigInt(bytes, isSigned, bigEndian) === num).toBe(true);

    num = -340282366920938463463374607431768211455n;
    size = null;
    bigEndian = false;
    isSigned = true;
    bytes = bigIntToBin(num, size, bigEndian);
    expect(bytes).toEqual(new Uint8Array([ 0x01, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0xff ]));
    expect(binToBigInt(bytes, isSigned, bigEndian) === num).toBe(true);

    num = 340282366920938463463374607431768211456n;
    size = null;
    bigEndian = false;
    isSigned = false;
    bytes = bigIntToBin(num, size, bigEndian);
    expect(bytes).toEqual(new Uint8Array([ 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x01 ]));
    expect(binToBigInt(bytes, isSigned, bigEndian) === num).toBe(true);

    num = -340282366920938463463374607431768211456n;
    size = null;
    bigEndian = false;
    isSigned = true;
    bytes = bigIntToBin(num, size, bigEndian);
    expect(bytes).toEqual(new Uint8Array([ 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0xff ]));
    expect(binToBigInt(bytes, isSigned, bigEndian) === num).toBe(true);

    num = 0n;
    size = 20;
    bigEndian = false;
    isSigned = false;
    bytes = bigIntToBin(num, size, bigEndian);
    expect(bytes).toEqual(new Uint8Array([ 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00 ]));
    expect(binToBigInt(bytes, isSigned, bigEndian) === num).toBe(true);

    num = 1n;
    size = 20;
    bigEndian = false;
    isSigned = false;
    bytes = bigIntToBin(num, size, bigEndian);
    expect(bytes).toEqual(new Uint8Array([ 0x01, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00 ]));
    expect(binToBigInt(bytes, isSigned, bigEndian) === num).toBe(true);

    num = -1n;
    size = 20;
    bigEndian = false;
    isSigned = true;
    bytes = bigIntToBin(num, size, bigEndian);
    expect(bytes).toEqual(new Uint8Array([ 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff ]));
    expect(binToBigInt(bytes, isSigned, bigEndian) === num).toBe(true);

    num = 255n;
    size = 20;
    bigEndian = false;
    isSigned = false;
    bytes = bigIntToBin(num, size, bigEndian);
    expect(bytes).toEqual(new Uint8Array([ 0xff, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00 ]));
    expect(binToBigInt(bytes, isSigned, bigEndian) === num).toBe(true);

    num = -255n;
    size = 20;
    bigEndian = false;
    isSigned = true;
    bytes = bigIntToBin(num, size, bigEndian);
    expect(bytes).toEqual(new Uint8Array([ 0x01, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff ]));
    expect(binToBigInt(bytes, isSigned, bigEndian) === num).toBe(true);

    num = 256n;
    size = 20;
    bigEndian = false;
    isSigned = false;
    bytes = bigIntToBin(num, size, bigEndian);
    expect(bytes).toEqual(new Uint8Array([ 0x00, 0x01, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00 ]));
    expect(binToBigInt(bytes, isSigned, bigEndian) === num).toBe(true);

    num = -256n;
    size = 20;
    bigEndian = false;
    isSigned = true;
    bytes = bigIntToBin(num, size, bigEndian);
    expect(bytes).toEqual(new Uint8Array([ 0x00, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff ]));
    expect(binToBigInt(bytes, isSigned, bigEndian) === num).toBe(true);

    num = 32767n;
    size = 20;
    bigEndian = false;
    isSigned = false;
    bytes = bigIntToBin(num, size, bigEndian);
    expect(bytes).toEqual(new Uint8Array([ 0xff, 0x7f, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00 ]));
    expect(binToBigInt(bytes, isSigned, bigEndian) === num).toBe(true);

    num = -32767n;
    size = 20;
    bigEndian = false;
    isSigned = true;
    bytes = bigIntToBin(num, size, bigEndian);
    expect(bytes).toEqual(new Uint8Array([ 0x01, 0x80, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff ]));
    expect(binToBigInt(bytes, isSigned, bigEndian) === num).toBe(true);

    num = 33023n;
    size = 20;
    bigEndian = false;
    isSigned = false;
    bytes = bigIntToBin(num, size, bigEndian);
    expect(bytes).toEqual(new Uint8Array([ 0xff, 0x80, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00 ]));
    expect(binToBigInt(bytes, isSigned, bigEndian) === num).toBe(true);

    num = -33023n;
    size = 20;
    bigEndian = false;
    isSigned = true;
    bytes = bigIntToBin(num, size, bigEndian);
    expect(bytes).toEqual(new Uint8Array([ 0x01, 0x7f, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff ]));
    expect(binToBigInt(bytes, isSigned, bigEndian) === num).toBe(true);

    num = 4294967295n;
    size = 20;
    bigEndian = false;
    isSigned = false;
    bytes = bigIntToBin(num, size, bigEndian);
    expect(bytes).toEqual(new Uint8Array([ 0xff, 0xff, 0xff, 0xff, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00 ]));
    expect(binToBigInt(bytes, isSigned, bigEndian) === num).toBe(true);

    num = -4294967295n;
    size = 20;
    bigEndian = false;
    isSigned = true;
    bytes = bigIntToBin(num, size, bigEndian);
    expect(bytes).toEqual(new Uint8Array([ 0x01, 0x00, 0x00, 0x00, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff ]));
    expect(binToBigInt(bytes, isSigned, bigEndian) === num).toBe(true);

    num = 4294967296n;
    size = 20;
    bigEndian = false;
    isSigned = false;
    bytes = bigIntToBin(num, size, bigEndian);
    expect(bytes).toEqual(new Uint8Array([ 0x00, 0x00, 0x00, 0x00, 0x01, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00 ]));
    expect(binToBigInt(bytes, isSigned, bigEndian) === num).toBe(true);

    num = -4294967296n;
    size = 20;
    bigEndian = false;
    isSigned = true;
    bytes = bigIntToBin(num, size, bigEndian);
    expect(bytes).toEqual(new Uint8Array([ 0x00, 0x00, 0x00, 0x00, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff ]));
    expect(binToBigInt(bytes, isSigned, bigEndian) === num).toBe(true);

    num = 18446744073709551615n;
    size = 20;
    bigEndian = false;
    isSigned = false;
    bytes = bigIntToBin(num, size, bigEndian);
    expect(bytes).toEqual(new Uint8Array([ 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00 ]));
    expect(binToBigInt(bytes, isSigned, bigEndian) === num).toBe(true);

    num = -18446744073709551615n;
    size = 20;
    bigEndian = false;
    isSigned = true;
    bytes = bigIntToBin(num, size, bigEndian);
    expect(bytes).toEqual(new Uint8Array([ 0x01, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff ]));
    expect(binToBigInt(bytes, isSigned, bigEndian) === num).toBe(true);

    num = 18446744073709551616n;
    size = 20;
    bigEndian = false;
    isSigned = false;
    bytes = bigIntToBin(num, size, bigEndian);
    expect(bytes).toEqual(new Uint8Array([ 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x01, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00 ]));
    expect(binToBigInt(bytes, isSigned, bigEndian) === num).toBe(true);

    num = -18446744073709551616n;
    size = 20;
    bigEndian = false;
    isSigned = true;
    bytes = bigIntToBin(num, size, bigEndian);
    expect(bytes).toEqual(new Uint8Array([ 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff ]));
    expect(binToBigInt(bytes, isSigned, bigEndian) === num).toBe(true);

    num = 340282366920938463463374607431768211455n;
    size = 20;
    bigEndian = false;
    isSigned = false;
    bytes = bigIntToBin(num, size, bigEndian);
    expect(bytes).toEqual(new Uint8Array([ 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0x00, 0x00, 0x00, 0x00 ]));
    expect(binToBigInt(bytes, isSigned, bigEndian) === num).toBe(true);

    num = -340282366920938463463374607431768211455n;
    size = 20;
    bigEndian = false;
    isSigned = true;
    bytes = bigIntToBin(num, size, bigEndian);
    expect(bytes).toEqual(new Uint8Array([ 0x01, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0xff, 0xff, 0xff, 0xff ]));
    expect(binToBigInt(bytes, isSigned, bigEndian) === num).toBe(true);

    num = 340282366920938463463374607431768211456n;
    size = 20;
    bigEndian = false;
    isSigned = false;
    bytes = bigIntToBin(num, size, bigEndian);
    expect(bytes).toEqual(new Uint8Array([ 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x01, 0x00, 0x00, 0x00 ]));
    expect(binToBigInt(bytes, isSigned, bigEndian) === num).toBe(true);

    num = -340282366920938463463374607431768211456n;
    size = 20;
    bigEndian = false;
    isSigned = true;
    bytes = bigIntToBin(num, size, bigEndian);
    expect(bytes).toEqual(new Uint8Array([ 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0xff, 0xff, 0xff, 0xff ]));
    expect(binToBigInt(bytes, isSigned, bigEndian) === num).toBe(true);

    num = 0n;
    size = null;
    bigEndian = true;
    isSigned = false;
    bytes = bigIntToBin(num, size, bigEndian);
    expect(bytes).toEqual(new Uint8Array([ 0x00 ]));
    expect(binToBigInt(bytes, isSigned, bigEndian) === num).toBe(true);

    num = 1n;
    size = null;
    bigEndian = true;
    isSigned = false;
    bytes = bigIntToBin(num, size, bigEndian);
    expect(bytes).toEqual(new Uint8Array([ 0x01 ]));
    expect(binToBigInt(bytes, isSigned, bigEndian) === num).toBe(true);

    num = -1n;
    size = null;
    bigEndian = true;
    isSigned = true;
    bytes = bigIntToBin(num, size, bigEndian);
    expect(bytes).toEqual(new Uint8Array([ 0xff ]));
    expect(binToBigInt(bytes, isSigned, bigEndian) === num).toBe(true);

    num = 255n;
    size = null;
    bigEndian = true;
    isSigned = false;
    bytes = bigIntToBin(num, size, bigEndian);
    expect(bytes).toEqual(new Uint8Array([ 0xff ]));
    expect(binToBigInt(bytes, isSigned, bigEndian) === num).toBe(true);

    num = -255n;
    size = null;
    bigEndian = true;
    isSigned = true;
    bytes = bigIntToBin(num, size, bigEndian);
    expect(bytes).toEqual(new Uint8Array([ 0xff, 0x01 ]));
    expect(binToBigInt(bytes, isSigned, bigEndian) === num).toBe(true);

    num = 256n;
    size = null;
    bigEndian = true;
    isSigned = false;
    bytes = bigIntToBin(num, size, bigEndian);
    expect(bytes).toEqual(new Uint8Array([ 0x01, 0x00 ]));
    expect(binToBigInt(bytes, isSigned, bigEndian) === num).toBe(true);

    num = -256n;
    size = null;
    bigEndian = true;
    isSigned = true;
    bytes = bigIntToBin(num, size, bigEndian);
    expect(bytes).toEqual(new Uint8Array([ 0xff, 0x00 ]));
    expect(binToBigInt(bytes, isSigned, bigEndian) === num).toBe(true);

    num = 32767n;
    size = null;
    bigEndian = true;
    isSigned = false;
    bytes = bigIntToBin(num, size, bigEndian);
    expect(bytes).toEqual(new Uint8Array([ 0x7f, 0xff ]));
    expect(binToBigInt(bytes, isSigned, bigEndian) === num).toBe(true);

    num = -32767n;
    size = null;
    bigEndian = true;
    isSigned = true;
    bytes = bigIntToBin(num, size, bigEndian);
    expect(bytes).toEqual(new Uint8Array([ 0x80, 0x01 ]));
    expect(binToBigInt(bytes, isSigned, bigEndian) === num).toBe(true);

    num = 33023n;
    size = null;
    bigEndian = true;
    isSigned = false;
    bytes = bigIntToBin(num, size, bigEndian);
    expect(bytes).toEqual(new Uint8Array([ 0x80, 0xff ]));
    expect(binToBigInt(bytes, isSigned, bigEndian) === num).toBe(true);

    num = -33023n;
    size = null;
    bigEndian = true;
    isSigned = true;
    bytes = bigIntToBin(num, size, bigEndian);
    expect(bytes).toEqual(new Uint8Array([ 0xff, 0x7f, 0x01 ]));
    expect(binToBigInt(bytes, isSigned, bigEndian) === num).toBe(true);

    num = 4294967295n;
    size = null;
    bigEndian = true;
    isSigned = false;
    bytes = bigIntToBin(num, size, bigEndian);
    expect(bytes).toEqual(new Uint8Array([ 0xff, 0xff, 0xff, 0xff ]));
    expect(binToBigInt(bytes, isSigned, bigEndian) === num).toBe(true);

    num = -4294967295n;
    size = null;
    bigEndian = true;
    isSigned = true;
    bytes = bigIntToBin(num, size, bigEndian);
    expect(bytes).toEqual(new Uint8Array([ 0xff, 0x00, 0x00, 0x00, 0x01 ]));
    expect(binToBigInt(bytes, isSigned, bigEndian) === num).toBe(true);

    num = 4294967296n;
    size = null;
    bigEndian = true;
    isSigned = false;
    bytes = bigIntToBin(num, size, bigEndian);
    expect(bytes).toEqual(new Uint8Array([ 0x01, 0x00, 0x00, 0x00, 0x00 ]));
    expect(binToBigInt(bytes, isSigned, bigEndian) === num).toBe(true);

    num = -4294967296n;
    size = null;
    bigEndian = true;
    isSigned = true;
    bytes = bigIntToBin(num, size, bigEndian);
    expect(bytes).toEqual(new Uint8Array([ 0xff, 0x00, 0x00, 0x00, 0x00 ]));
    expect(binToBigInt(bytes, isSigned, bigEndian) === num).toBe(true);

    num = 18446744073709551615n;
    size = null;
    bigEndian = true;
    isSigned = false;
    bytes = bigIntToBin(num, size, bigEndian);
    expect(bytes).toEqual(new Uint8Array([ 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff ]));
    expect(binToBigInt(bytes, isSigned, bigEndian) === num).toBe(true);

    num = -18446744073709551615n;
    size = null;
    bigEndian = true;
    isSigned = true;
    bytes = bigIntToBin(num, size, bigEndian);
    expect(bytes).toEqual(new Uint8Array([ 0xff, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x01 ]));
    expect(binToBigInt(bytes, isSigned, bigEndian) === num).toBe(true);

    num = 18446744073709551616n;
    size = null;
    bigEndian = true;
    isSigned = false;
    bytes = bigIntToBin(num, size, bigEndian);
    expect(bytes).toEqual(new Uint8Array([ 0x01, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00 ]));
    expect(binToBigInt(bytes, isSigned, bigEndian) === num).toBe(true);

    num = -18446744073709551616n;
    size = null;
    bigEndian = true;
    isSigned = true;
    bytes = bigIntToBin(num, size, bigEndian);
    expect(bytes).toEqual(new Uint8Array([ 0xff, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00 ]));
    expect(binToBigInt(bytes, isSigned, bigEndian) === num).toBe(true);

    num = 340282366920938463463374607431768211455n;
    size = null;
    bigEndian = true;
    isSigned = false;
    bytes = bigIntToBin(num, size, bigEndian);
    expect(bytes).toEqual(new Uint8Array([ 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff ]));
    expect(binToBigInt(bytes, isSigned, bigEndian) === num).toBe(true);

    num = -340282366920938463463374607431768211455n;
    size = null;
    bigEndian = true;
    isSigned = true;
    bytes = bigIntToBin(num, size, bigEndian);
    expect(bytes).toEqual(new Uint8Array([ 0xff, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x01 ]));
    expect(binToBigInt(bytes, isSigned, bigEndian) === num).toBe(true);

    num = 340282366920938463463374607431768211456n;
    size = null;
    bigEndian = true;
    isSigned = false;
    bytes = bigIntToBin(num, size, bigEndian);
    expect(bytes).toEqual(new Uint8Array([ 0x01, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00 ]));
    expect(binToBigInt(bytes, isSigned, bigEndian) === num).toBe(true);

    num = -340282366920938463463374607431768211456n;
    size = null;
    bigEndian = true;
    isSigned = true;
    bytes = bigIntToBin(num, size, bigEndian);
    expect(bytes).toEqual(new Uint8Array([ 0xff, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00 ]));
    expect(binToBigInt(bytes, isSigned, bigEndian) === num).toBe(true);

    num = 0n;
    size = 20;
    bigEndian = true;
    isSigned = false;
    bytes = bigIntToBin(num, size, bigEndian);
    expect(bytes).toEqual(new Uint8Array([ 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00 ]));
    expect(binToBigInt(bytes, isSigned, bigEndian) === num).toBe(true);

    num = 1n;
    size = 20;
    bigEndian = true;
    isSigned = false;
    bytes = bigIntToBin(num, size, bigEndian);
    expect(bytes).toEqual(new Uint8Array([ 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x01 ]));
    expect(binToBigInt(bytes, isSigned, bigEndian) === num).toBe(true);

    num = -1n;
    size = 20;
    bigEndian = true;
    isSigned = true;
    bytes = bigIntToBin(num, size, bigEndian);
    expect(bytes).toEqual(new Uint8Array([ 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff ]));
    expect(binToBigInt(bytes, isSigned, bigEndian) === num).toBe(true);

    num = 255n;
    size = 20;
    bigEndian = true;
    isSigned = false;
    bytes = bigIntToBin(num, size, bigEndian);
    expect(bytes).toEqual(new Uint8Array([ 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0xff ]));
    expect(binToBigInt(bytes, isSigned, bigEndian) === num).toBe(true);

    num = -255n;
    size = 20;
    bigEndian = true;
    isSigned = true;
    bytes = bigIntToBin(num, size, bigEndian);
    expect(bytes).toEqual(new Uint8Array([ 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0x01 ]));
    expect(binToBigInt(bytes, isSigned, bigEndian) === num).toBe(true);

    num = 256n;
    size = 20;
    bigEndian = true;
    isSigned = false;
    bytes = bigIntToBin(num, size, bigEndian);
    expect(bytes).toEqual(new Uint8Array([ 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x01, 0x00 ]));
    expect(binToBigInt(bytes, isSigned, bigEndian) === num).toBe(true);

    num = -256n;
    size = 20;
    bigEndian = true;
    isSigned = true;
    bytes = bigIntToBin(num, size, bigEndian);
    expect(bytes).toEqual(new Uint8Array([ 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0x00 ]));
    expect(binToBigInt(bytes, isSigned, bigEndian) === num).toBe(true);

    num = 32767n;
    size = 20;
    bigEndian = true;
    isSigned = false;
    bytes = bigIntToBin(num, size, bigEndian);
    expect(bytes).toEqual(new Uint8Array([ 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x7f, 0xff ]));
    expect(binToBigInt(bytes, isSigned, bigEndian) === num).toBe(true);

    num = -32767n;
    size = 20;
    bigEndian = true;
    isSigned = true;
    bytes = bigIntToBin(num, size, bigEndian);
    expect(bytes).toEqual(new Uint8Array([ 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0x80, 0x01 ]));
    expect(binToBigInt(bytes, isSigned, bigEndian) === num).toBe(true);

    num = 33023n;
    size = 20;
    bigEndian = true;
    isSigned = false;
    bytes = bigIntToBin(num, size, bigEndian);
    expect(bytes).toEqual(new Uint8Array([ 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x80, 0xff ]));
    expect(binToBigInt(bytes, isSigned, bigEndian) === num).toBe(true);

    num = -33023n;
    size = 20;
    bigEndian = true;
    isSigned = true;
    bytes = bigIntToBin(num, size, bigEndian);
    expect(bytes).toEqual(new Uint8Array([ 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0x7f, 0x01 ]));
    expect(binToBigInt(bytes, isSigned, bigEndian) === num).toBe(true);

    num = 4294967295n;
    size = 20;
    bigEndian = true;
    isSigned = false;
    bytes = bigIntToBin(num, size, bigEndian);
    expect(bytes).toEqual(new Uint8Array([ 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0xff, 0xff, 0xff, 0xff ]));
    expect(binToBigInt(bytes, isSigned, bigEndian) === num).toBe(true);

    num = -4294967295n;
    size = 20;
    bigEndian = true;
    isSigned = true;
    bytes = bigIntToBin(num, size, bigEndian);
    expect(bytes).toEqual(new Uint8Array([ 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0x00, 0x00, 0x00, 0x01 ]));
    expect(binToBigInt(bytes, isSigned, bigEndian) === num).toBe(true);

    num = 4294967296n;
    size = 20;
    bigEndian = true;
    isSigned = false;
    bytes = bigIntToBin(num, size, bigEndian);
    expect(bytes).toEqual(new Uint8Array([ 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x01, 0x00, 0x00, 0x00, 0x00 ]));
    expect(binToBigInt(bytes, isSigned, bigEndian) === num).toBe(true);

    num = -4294967296n;
    size = 20;
    bigEndian = true;
    isSigned = true;
    bytes = bigIntToBin(num, size, bigEndian);
    expect(bytes).toEqual(new Uint8Array([ 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0x00, 0x00, 0x00, 0x00 ]));
    expect(binToBigInt(bytes, isSigned, bigEndian) === num).toBe(true);

    num = 18446744073709551615n;
    size = 20;
    bigEndian = true;
    isSigned = false;
    bytes = bigIntToBin(num, size, bigEndian);
    expect(bytes).toEqual(new Uint8Array([ 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff ]));
    expect(binToBigInt(bytes, isSigned, bigEndian) === num).toBe(true);

    num = -18446744073709551615n;
    size = 20;
    bigEndian = true;
    isSigned = true;
    bytes = bigIntToBin(num, size, bigEndian);
    expect(bytes).toEqual(new Uint8Array([ 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x01 ]));
    expect(binToBigInt(bytes, isSigned, bigEndian) === num).toBe(true);

    num = 18446744073709551616n;
    size = 20;
    bigEndian = true;
    isSigned = false;
    bytes = bigIntToBin(num, size, bigEndian);
    expect(bytes).toEqual(new Uint8Array([ 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x01, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00 ]));
    expect(binToBigInt(bytes, isSigned, bigEndian) === num).toBe(true);

    num = -18446744073709551616n;
    size = 20;
    bigEndian = true;
    isSigned = true;
    bytes = bigIntToBin(num, size, bigEndian);
    expect(bytes).toEqual(new Uint8Array([ 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00 ]));
    expect(binToBigInt(bytes, isSigned, bigEndian) === num).toBe(true);

    num = 340282366920938463463374607431768211455n;
    size = 20;
    bigEndian = true;
    isSigned = false;
    bytes = bigIntToBin(num, size, bigEndian);
    expect(bytes).toEqual(new Uint8Array([ 0x00, 0x00, 0x00, 0x00, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff ]));
    expect(binToBigInt(bytes, isSigned, bigEndian) === num).toBe(true);

    num = -340282366920938463463374607431768211455n;
    size = 20;
    bigEndian = true;
    isSigned = true;
    bytes = bigIntToBin(num, size, bigEndian);
    expect(bytes).toEqual(new Uint8Array([ 0xff, 0xff, 0xff, 0xff, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x01 ]));
    expect(binToBigInt(bytes, isSigned, bigEndian) === num).toBe(true);

    num = 340282366920938463463374607431768211456n;
    size = 20;
    bigEndian = true;
    isSigned = false;
    bytes = bigIntToBin(num, size, bigEndian);
    expect(bytes).toEqual(new Uint8Array([ 0x00, 0x00, 0x00, 0x01, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00 ]));
    expect(binToBigInt(bytes, isSigned, bigEndian) === num).toBe(true);

    num = -340282366920938463463374607431768211456n;
    size = 20;
    bigEndian = true;
    isSigned = true;
    bytes = bigIntToBin(num, size, bigEndian);
    expect(bytes).toEqual(new Uint8Array([ 0xff, 0xff, 0xff, 0xff, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00 ]));
    expect(binToBigInt(bytes, isSigned, bigEndian) === num).toBe(true);
});
