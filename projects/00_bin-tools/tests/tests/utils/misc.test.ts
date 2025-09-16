import { strToInt } from '../../../src/main';
import { arrayAppend, condenseString } from '../../../src/utils/misc';


test('Test condenseString()', () => {
    expect(condenseString('')).toBe('');
    expect(condenseString('a b c')).toBe('abc');
    expect(condenseString('\t \ta \t\r\nb  \r\r  c\t\t\n\r')).toBe('abc');
});

test('Test arrayAppend()', () => {
    const a : number[] = [];
    const b : number[] = arrayAppend(a, [ 1, 2, 3 ]);

    expect(a).toBe(b);
    expect(a.length).toBe(3);
    expect(a[0]).toBe(1);
    expect(a[1]).toBe(2);
    expect(a[2]).toBe(3);
});

test('Test strToInt()', () => {
    const maxSafeBigInt     = BigInt(Number.MAX_SAFE_INTEGER);
    const minSafeBigInt     = BigInt(Number.MIN_SAFE_INTEGER);
    const maxSafeBigIntNext = BigInt(Number.MAX_SAFE_INTEGER) + 1n;
    const minSafeBigIntPrev = BigInt(Number.MIN_SAFE_INTEGER) - 1n;

    expect(strToInt('0') === 0).toBe(true);
    expect(strToInt('0', true) === 0n).toBe(true);

    expect(strToInt(String(maxSafeBigInt)) === Number.MAX_SAFE_INTEGER).toBe(true);
    expect(strToInt(String(minSafeBigInt)) === Number.MIN_SAFE_INTEGER).toBe(true);

    expect(strToInt(String(maxSafeBigInt), true) === maxSafeBigInt).toBe(true);
    expect(strToInt(String(minSafeBigInt), true) === minSafeBigInt).toBe(true);

    expect(strToInt(String(maxSafeBigIntNext)) === maxSafeBigIntNext).toBe(true);
    expect(strToInt(String(minSafeBigIntPrev)) === minSafeBigIntPrev).toBe(true);

    expect(() => strToInt(<any>undefined)                    ).toThrow(/Expected type of argument 'strNum' is non-empty string/i);
    expect(() => strToInt(<any>null)                         ).toThrow(/Expected type of argument 'strNum' is non-empty string/i);
    expect(() => strToInt(<any>true)                         ).toThrow(/Expected type of argument 'strNum' is non-empty string/i);
    expect(() => strToInt(<any>false)                        ).toThrow(/Expected type of argument 'strNum' is non-empty string/i);
    expect(() => strToInt(<any>NaN)                          ).toThrow(/Expected type of argument 'strNum' is non-empty string/i);
    expect(() => strToInt(<any>Infinity)                     ).toThrow(/Expected type of argument 'strNum' is non-empty string/i);
    expect(() => strToInt(<any>-Infinity)                    ).toThrow(/Expected type of argument 'strNum' is non-empty string/i);
    expect(() => strToInt(<any>(Number.MIN_SAFE_INTEGER - 1))).toThrow(/Expected type of argument 'strNum' is non-empty string/i);
    expect(() => strToInt(<any>(Number.MAX_SAFE_INTEGER + 1))).toThrow(/Expected type of argument 'strNum' is non-empty string/i);
    expect(() => strToInt(<any>0)                            ).toThrow(/Expected type of argument 'strNum' is non-empty string/i);
    expect(() => strToInt(<any>0n)                           ).toThrow(/Expected type of argument 'strNum' is non-empty string/i);
    expect(() => strToInt(<any>1.0)                          ).toThrow(/Expected type of argument 'strNum' is non-empty string/i);
    expect(() => strToInt(<any>1.5)                          ).toThrow(/Expected type of argument 'strNum' is non-empty string/i);
    expect(() => strToInt(<any>'')                           ).toThrow(/Expected type of argument 'strNum' is non-empty string/i);
    expect(() => strToInt(<any>'1-3')                        ).toThrow(/Failed to parse value/i);
    expect(() => strToInt(<any>{})                           ).toThrow(/Expected type of argument 'strNum' is non-empty string/i);
    expect(() => strToInt(<any>Object.create(null))          ).toThrow(/Expected type of argument 'strNum' is non-empty string/i);
    expect(() => strToInt(<any>[])                           ).toThrow(/Expected type of argument 'strNum' is non-empty string/i);
    expect(() => strToInt(<any>Array())                      ).toThrow(/Expected type of argument 'strNum' is non-empty string/i);
    expect(() => strToInt(<any>(/regex/))                    ).toThrow(/Expected type of argument 'strNum' is non-empty string/i);
    expect(() => strToInt(<any>Symbol())                     ).toThrow(/Expected type of argument 'strNum' is non-empty string/i);
    expect(() => strToInt(<any>(() => {}))                   ).toThrow(/Expected type of argument 'strNum' is non-empty string/i);
    expect(() => strToInt(<any>function () {})               ).toThrow(/Expected type of argument 'strNum' is non-empty string/i);
    expect(() => strToInt(<any>function *() {})              ).toThrow(/Expected type of argument 'strNum' is non-empty string/i);
    expect(() => strToInt(<any>class X {})                   ).toThrow(/Expected type of argument 'strNum' is non-empty string/i);
    expect(() => strToInt(<any>new (class X {}))             ).toThrow(/Expected type of argument 'strNum' is non-empty string/i);
    expect(() => strToInt(<any>new Error('error'))           ).toThrow(/Expected type of argument 'strNum' is non-empty string/i);
    expect(() => strToInt(<any>new Set())                    ).toThrow(/Expected type of argument 'strNum' is non-empty string/i);
    expect(() => strToInt(<any>new Map())                    ).toThrow(/Expected type of argument 'strNum' is non-empty string/i);
    expect(() => strToInt(<any>new Date())                   ).toThrow(/Expected type of argument 'strNum' is non-empty string/i);
    expect(() => strToInt(<any>new Uint8Array())             ).toThrow(/Expected type of argument 'strNum' is non-empty string/i);
});


