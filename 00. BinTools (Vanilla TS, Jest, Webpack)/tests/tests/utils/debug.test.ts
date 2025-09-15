import { fmtType } from '../../../src/utils/debug';


test('Test fmtType()', async () => {
    expect(fmtType(null)).toBe('<null>');
});
