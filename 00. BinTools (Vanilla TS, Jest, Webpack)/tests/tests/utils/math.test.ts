import { nextPOT } from '../../../src/utils/math';

test('Test nextPOT()', () => {
    expect(nextPOT(0)).toBe(0);

    let num = 1;

    for (let e = 0; e <= 15; e++) {
        const pot = 2 ** e;

        for (; num <= pot; num++) {
            expect(nextPOT(num)).toBe(pot);
        }
    }

});


