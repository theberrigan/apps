import { binToBase64, base64ToBin } from '../../../src/main';

test('Test binToBase64() and base64ToBin()', () => {
    const bytes  = Array.from({ length: 256 }, (_, i) => i);
    const encRef = (  // created in Python
        'AAECAwQFBgcICQoLDA0ODxAREhMUFRYXGBkaGxwdHh8gISIjJCUmJygpKissLS4vMDEy' +
        'MzQ1Njc4OTo7PD0+P0BBQkNERUZHSElKS0xNTk9QUVJTVFVWV1hZWltcXV5fYGFiY2Rl' +
        'ZmdoaWprbG1ub3BxcnN0dXZ3eHl6e3x9fn+AgYKDhIWGh4iJiouMjY6PkJGSk5SVlpeY' +
        'mZqbnJ2en6ChoqOkpaanqKmqq6ytrq+wsbKztLW2t7i5uru8vb6/wMHCw8TFxsfIycrL' +
        'zM3Oz9DR0tPU1dbX2Nna29zd3t/g4eLj5OXm5+jp6uvs7e7v8PHy8/T19vf4+fr7/P3+/w=='
    );

    const encoded = binToBase64(new Uint8Array(bytes));

    expect(encoded).toBe(encRef);

    const decoded = base64ToBin(encoded);

    expect(decoded instanceof Uint8Array).toBe(true);

    const decodedArray = Array.from(decoded);

    expect(decodedArray).toEqual(bytes);

    // ---------------------------------------------

    expect(() => binToBase64(<any>undefined)                    ).toThrow(/Expected type of argument 'data' is/);
    expect(() => binToBase64(<any>null)                         ).toThrow(/Expected type of argument 'data' is/);
    expect(() => binToBase64(<any>true)                         ).toThrow(/Expected type of argument 'data' is/);
    expect(() => binToBase64(<any>false)                        ).toThrow(/Expected type of argument 'data' is/);
    expect(() => binToBase64(<any>(NaN)                        )).toThrow(/Expected type of argument 'data' is/);
    expect(() => binToBase64(<any>(Infinity)                   )).toThrow(/Expected type of argument 'data' is/);
    expect(() => binToBase64(<any>(-Infinity)                  )).toThrow(/Expected type of argument 'data' is/);
    expect(() => binToBase64(<any>(Number.MIN_SAFE_INTEGER - 1))).toThrow(/Expected type of argument 'data' is/);
    expect(() => binToBase64(<any>(Number.MAX_SAFE_INTEGER + 1))).toThrow(/Expected type of argument 'data' is/);
    expect(() => binToBase64(<any>(0)                          )).toThrow(/Expected type of argument 'data' is/);
    expect(() => binToBase64(<any>(0n)                         )).toThrow(/Expected type of argument 'data' is/);
    expect(() => binToBase64(<any>(1.0)                        )).toThrow(/Expected type of argument 'data' is/);
    expect(() => binToBase64(<any>(1.5)                        )).toThrow(/Expected type of argument 'data' is/);
    expect(() => binToBase64(<any>('0')                        )).toThrow(/Expected type of argument 'data' is/);
    expect(() => binToBase64(<any>('')                         )).toThrow(/Expected type of argument 'data' is/);
    expect(() => binToBase64(<any>({})                         )).toThrow(/Expected type of argument 'data' is/);
    expect(() => binToBase64(<any>(Object.create(null))        )).toThrow(/Expected type of argument 'data' is/);
    expect(() => binToBase64(<any>([])                         )).toThrow(/Expected type of argument 'data' is/);
    expect(() => binToBase64(<any>(Array())                    )).toThrow(/Expected type of argument 'data' is/);
    expect(() => binToBase64(<any>(/regex/)                    )).toThrow(/Expected type of argument 'data' is/);
    expect(() => binToBase64(<any>(Symbol())                   )).toThrow(/Expected type of argument 'data' is/);
    expect(() => binToBase64(<any>(() => {})                   )).toThrow(/Expected type of argument 'data' is/);
    expect(() => binToBase64(<any>(function () {})             )).toThrow(/Expected type of argument 'data' is/);
    expect(() => binToBase64(<any>(function *() {})            )).toThrow(/Expected type of argument 'data' is/);
    expect(() => binToBase64(<any>(class X {})                 )).toThrow(/Expected type of argument 'data' is/);
    expect(() => binToBase64(<any>(new (class X {}))           )).toThrow(/Expected type of argument 'data' is/);
    expect(() => binToBase64(<any>(new Error('error'))         )).toThrow(/Expected type of argument 'data' is/);
    expect(() => binToBase64(<any>(new Set())                  )).toThrow(/Expected type of argument 'data' is/);
    expect(() => binToBase64(<any>(new Map())                  )).toThrow(/Expected type of argument 'data' is/);
    expect(() => binToBase64(<any>(new Date())                 )).toThrow(/Expected type of argument 'data' is/);

    expect(binToBase64(new DataView(new ArrayBuffer()))).toBe('');
    expect(binToBase64(new ArrayBuffer())              ).toBe('');
    expect(binToBase64(new SharedArrayBuffer())        ).toBe('');
    expect(binToBase64(new Int8Array())                ).toBe('');
    expect(binToBase64(new Uint8Array())               ).toBe('');
    expect(binToBase64(new Uint8ClampedArray())        ).toBe('');
    expect(binToBase64(new Int16Array())               ).toBe('');
    expect(binToBase64(new Uint16Array())              ).toBe('');
    expect(binToBase64(new Int32Array())               ).toBe('');
    expect(binToBase64(new Uint32Array())              ).toBe('');
    expect(binToBase64(new Int32Array())               ).toBe('');
    expect(binToBase64(new Uint32Array())              ).toBe('');
    expect(binToBase64(new BigInt64Array())            ).toBe('');
    expect(binToBase64(new BigUint64Array())           ).toBe('');
    expect(binToBase64(new Float32Array())             ).toBe('');
    expect(binToBase64(new Float64Array())             ).toBe('');
    expect(binToBase64(Buffer.alloc(0))                ).toBe('');  // Node Buffer
});
