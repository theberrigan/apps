import { isLittleEndianPlatform } from '../../../src/main';


test('Test isLittleEndianPlatform', () => {
    expect(isLittleEndianPlatform === false || isLittleEndianPlatform === true).toBe(true);
});


