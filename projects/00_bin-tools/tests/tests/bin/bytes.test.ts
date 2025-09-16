import { areBytesSame, asBytes, swapBytes, toBytes } from '../../../src/main';


test('Test asBytes()', () => {
    const u8a  = new Uint8Array([ 1, 2, 3, 4, 5, 6, 7, 8 ]);
    const u8ca = new Uint8ClampedArray(1);

    expect(asBytes(u8a) === u8a).toBe(true);
    expect(asBytes(u8ca) === u8ca).toBe(true);

    const u16a = new Uint16Array(1);

    expect(asBytes(u16a)).toBeInstanceOf(Uint8Array);
    expect(asBytes(u16a).buffer === u16a.buffer).toBe(true);

    const dv = new DataView(u16a.buffer);

    expect(asBytes(dv)).toBeInstanceOf(Uint8Array);
    expect(asBytes(dv).buffer === u16a.buffer).toBe(true);

    const u16a2 = new Uint16Array(u8a.buffer, 2, 2);

    expect(asBytes(u16a2).length).toBe(4);
    expect(asBytes(u16a2).byteLength).toBe(4);
    expect(asBytes(u16a2)).toEqual(new Uint8Array([ 3, 4, 5, 6 ]));

    const ab  = new ArrayBuffer(0);
    const sab = new SharedArrayBuffer(0);

    expect(asBytes(ab).buffer === ab).toBe(true);
    expect(asBytes(sab).buffer === sab).toBe(true);

    // Node Buffer
    const buffer = Buffer.alloc(1);

    expect(asBytes(buffer)).toBeInstanceOf(Uint8Array);
    expect(asBytes(buffer).buffer === buffer.buffer).toBe(true);

    expect(asBytes(<any>[ 0, 1, 2, 3, 255 ])).toBe(null);
    expect(asBytes(<any>[ -1, 1, 2, 3 ])    ).toBe(null);
    expect(asBytes(<any>[ 0, 1, 2, 3, 256 ])).toBe(null);
});

test('Test toBytes()', () => {
    const u8a  = new Uint8Array([ 1, 2, 3, 4, 5, 6, 7, 8 ]);
    const u8ca = new Uint8ClampedArray(1);

    expect(toBytes(u8a)).toBeInstanceOf(Uint8Array);
    expect(toBytes(u8a) !== u8a).toBe(true);
    expect(toBytes(u8a).buffer).not.toBe(u8a.buffer);
    expect(toBytes(u8ca)).toBeInstanceOf(Uint8Array);
    expect(toBytes(u8a)).toEqual(u8a);

    const u16a = new Uint16Array(1);

    expect(toBytes(u16a)).toBeInstanceOf(Uint8Array);
    expect(toBytes(u16a).buffer !== u16a.buffer).toBe(true);

    const dv = new DataView(u16a.buffer);

    expect(toBytes(dv)).toBeInstanceOf(Uint8Array);
    expect(toBytes(dv).buffer !== u16a.buffer).toBe(true);

    const u16a2 = new Uint16Array(u8a.buffer, 2, 2);

    expect(toBytes(u16a2).length).toBe(4);
    expect(toBytes(u16a2).byteLength).toBe(4);

    const ab  = new ArrayBuffer(0);
    const sab = new SharedArrayBuffer(0);

    expect(toBytes(ab).buffer !== ab).toBe(true);
    expect(toBytes(sab).buffer !== sab).toBe(true);

    // Node Buffer
    const buffer = Buffer.alloc(1);

    expect(toBytes(buffer)).toBeInstanceOf(Uint8Array);
    expect(toBytes(buffer).buffer !== buffer.buffer).toBe(true);

    expect(toBytes(<any>[ 0, 1, 2, 3, 255 ])).toBe(null);
    expect(toBytes(<any>[ -1, 1, 2, 3 ])    ).toBe(null);
    expect(toBytes(<any>[ 0, 1, 2, 3, 256 ])).toBe(null);
});

test('Test areBytesSame()', () => {
    let u8a  = new Uint8Array([ 1, 2, 3, 4, 5, 6, 7, 8 ]);
    let u8a2 = new Uint8Array(u8a.buffer, 2, 4);
    let u16a = new Uint16Array(u8a.buffer, 2, 2);

    expect(areBytesSame(u8a2, u16a)).toBe(true);
    expect(areBytesSame(u8a2, u16a, 0)).toBe(true);
    expect(areBytesSame(u8a2, u16a, 1024)).toBe(true);
    expect(areBytesSame(u8a2, u16a, Infinity)).toBe(true);
    expect(() => areBytesSame(u8a2, u16a, <any>[])).toThrow(/Expected type of argument 'byteLimit' is safe non-negative/);
    expect(() => areBytesSame(u8a2, u16a, -1)).toThrow(/Expected type of argument 'byteLimit' is safe non-negative/);
    expect(() => areBytesSame(u8a2, u16a, 1e65)).toThrow(/Expected type of argument 'byteLimit' is safe non-negative/);
    expect(() => areBytesSame(<any>null, u16a)).toThrow(/Expected type of argument 'a' is/);
    expect(() => areBytesSame(u8a2, <any>null)).toThrow(/Expected type of argument 'b' is/);

    let u8a3  = new Uint8Array([ 3, 4, 254, 255 ]);
    let u16a2 = new Uint16Array(u8a3.buffer);

    expect(areBytesSame(u8a2, u16a2)).toBe(false);
    expect(areBytesSame(u8a2, u16a2, 2)).toBe(true);
    expect(areBytesSame(u8a2, u16a2, 3)).toBe(false);
    expect(areBytesSame(u8a2, u16a2, Infinity)).toBe(false);

    expect(areBytesSame(u8a2, new DataView(u16a2.buffer), 2)).toBe(true);

    expect(areBytesSame(new Uint8Array([ 1, 2 ]), new Uint16Array([ 300, 400 ]))).toBe(false);
    expect(areBytesSame(new Uint8Array([ 1, 2 ]), new Uint16Array([ 300, 400 ]), 0)).toBe(true);
    expect(areBytesSame(new Uint8Array([ 1, 2 ]), new Uint8Array([ 1, 2, 3, 4, 5 ]), 2)).toBe(true);
    expect(areBytesSame(new Uint8Array([ 1, 2 ]), new Uint8Array([ 1, 2, 3, 4, 5 ]), 3)).toBe(false);
});

test('Test swapBytes()', () => {
    expect(swapBytes(new Uint8Array(0))).toEqual(new Uint8Array(0));
    expect(swapBytes(new Uint8Array([ 3 ]))).toEqual(new Uint8Array([ 3 ]));
    expect(swapBytes(new Uint8Array([ 3, 4, 5, 6 ]))).toEqual(new Uint8Array([ 6, 5, 4, 3 ]));
    expect(swapBytes(new Uint8Array([ 3, 4, 5, 6 ]), 2)).toEqual(new Uint8Array([ 4, 3, 6, 5 ]));
    expect(swapBytes(new Uint8Array([ 3, 4, 5, 6 ]), 1)).toEqual(new Uint8Array([ 3, 4, 5, 6 ]));
    expect(swapBytes(new Uint8Array([ 1, 2, 3, 4, 5, 6, 7, 8 ]), 3)).toEqual(new Uint8Array([ 3, 2, 1, 6, 5, 4, 7, 8 ]));

    expect(() => swapBytes(<any>null)).toThrow(/Expected type of argument 'data' is/);
    expect(() => swapBytes(<any>{a:5})).toThrow(/Expected type of argument 'data' is/);
    expect(() => swapBytes(new Uint8Array([ 3 ]), 2)).toThrow(/Argument 'itemSize' \(/);
    expect(() => swapBytes(new Uint8Array([ 3 ]), <any>[])).toThrow(/Expected type of argument 'itemSize' is safe non-negative/);
    expect(() => swapBytes(new Uint8Array([ 3 ]), Infinity)).toThrow(/Expected type of argument 'itemSize' is safe non-negative/);
    expect(() => swapBytes(new Uint8Array([ 3 ]), -1)).toThrow(/Expected type of argument 'itemSize' is safe non-negative/);
});
