import { isInt, isStr } from '../common/type-checks';
import { MAX_INT_BI, MIN_INT_BI, TInt } from '../common/types';
import { BTError } from '../common/errors';
import { fmtType } from './debug';


export const condenseString = (str : string) : string => {
    return str.replace(/\s+/g, '');
};

export const arrayAppend = (target : any[], source : any[]) : any[] => {
    for (let item of source) {
        target.push(item);
    }

    return target;
};

export const hasEnumIntValue = <T>(value : T, e : any) : value is T => {
    return isInt(value) && (value in e);
}

// in: string int
// out: BigInt, safe (int)number
export const strToInt = <
    T extends boolean,
    R = T extends true ? bigint : TInt
>(strNum : string, forceBigInt : T = <T>false) : R => {
    let value : bigint;

    if (!isStr(strNum) || !(strNum = condenseString(strNum))) {
        throw new BTError(`Expected type of argument 'strNum' is non-empty string, but ${ fmtType(strNum) } given`);
    }

    try {
        value = BigInt(strNum);
    } catch (e) {
        throw new BTError(`Failed to parse value ${ fmtType(strNum) } as integer (${ (<Error>e).message })`);
    }

    if (forceBigInt || value < MIN_INT_BI || value > MAX_INT_BI) {
        return <R>value;
    }

    return <R>Number(strNum);
};
