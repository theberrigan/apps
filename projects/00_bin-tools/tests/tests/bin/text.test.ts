import { binToText, textToBin } from '../../../src/main';


test('Test textToBin() and binToText()', () => {
    expect(textToBin('')).toEqual(new Uint8Array(0));
    expect(textToBin('abc')).toEqual(new Uint8Array([ 0x61, 0x62, 0x63 ]));
    expect(() => textToBin(<any>null)).toThrow(/Expected type of argument 'text' is string/);
    expect(() => textToBin('🎈')).toThrow(/Unable to encode codepoint/);

    expect(binToText(new Uint8Array(0))).toEqual('');
    expect(binToText(new Uint8Array([ 0x61, 0x62, 0x63 ]))).toEqual('abc');
    expect(() => binToText(<any>null)).toThrow(/Expected type of argument 'data' is/);
});
