import { BTError } from '../../../src/main';

test('Test BTError', async () => {
    expect(() => { throw new BTError(); }).toThrow(BTError);
});
