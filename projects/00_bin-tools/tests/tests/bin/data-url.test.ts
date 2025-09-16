import { binToDataUrl, dataUrlToBin } from '../../../src/main';
// import { _binToDataUrl, _dataUrlToBin } from '../../../src/bin/data-url';

test('Test binToDataUrl() and dataUrlToBin()', async () => {
    const u8a1 = new Uint8Array([ 1, 2, 3, 4 ]);
    const u8a2 = new Uint8Array(u8a1.buffer, 1, 2);
    const du1  = binToDataUrl(u8a1, 'audio/mpeg');
    const du2  = binToDataUrl(u8a2);

    expect(du1).toEqual('data:audio/mpeg;base64,AQIDBA==');
    expect(du2).toEqual('data:text/plain;base64,AgM=');
    expect(() => binToDataUrl(u8a1, ' \r\t\n')).toThrow(/Expected type of argument 'mimeType' is non-empty string/);
    expect(() => binToDataUrl(<any>null)).toThrow(/Expected type of argument 'data' is/);

    expect(await dataUrlToBin(du1)).toEqual(new Uint8Array([ 1, 2, 3, 4 ]));
    expect(await dataUrlToBin(du2)).toEqual(new Uint8Array([ 2, 3 ]));

    await dataUrlToBin(<any>null).catch(e => expect(String(e)).toMatch(/Expected type of argument 'dataUrl' is string, but/));
    await dataUrlToBin('  as;a+sd1').catch(e => expect(String(e)).toMatch(/Failed to decode Data URL/));
});
