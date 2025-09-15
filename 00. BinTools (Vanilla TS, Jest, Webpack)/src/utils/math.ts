import { BTError } from '../common/errors';
import { fmtType } from './debug';


export const trunc = Math.trunc;
export const pow   = Math.pow;
export const min   = Math.min;
export const max   = Math.max;
export const floor = Math.floor;
export const ceil  = Math.ceil;
export const log2  = Math.log2;

export const nextPOT = (num : number) : number => {
    if (!Number.isSafeInteger(num) || num < 0) {
        throw new BTError(`Expected type of argument 'num' is safe non-negative integer, but ${ fmtType(num) } given`);
    }

    if (num === 0) {
        return 0;
    }

    return 2 ** ceil(log2(num));
};
