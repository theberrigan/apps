import { TAnyBin, U8A } from '../common/types';
import { isStr } from '../common/type-checks';
import { BTError } from '../common/errors';
import { fmtType } from '../utils/debug';
import { MAX_U8 } from '../common/native-types';
import { ANY_BIN_TYPE } from '../common/constants';
import { asBytes } from './bytes';


export const textToBin = (text : string) : U8A => {
    if (!isStr(text)) {
        throw new BTError(`Expected type of argument 'text' is string, but ${ fmtType(text) } given`);
    }

    const cpCount = text.length;
    const bytes   = [];

    for (let i = 0; i < cpCount; ++i) {
        let code = text.charCodeAt(i);

        if (code > MAX_U8) {
            throw new BTError(`Unable to encode codepoint ${ code.toString(16).toUpperCase() } because it is too large`);
        }

        bytes.push(code);
    }

    return new U8A(bytes);
};

export const binToText = (data : TAnyBin) : string => {
    const bytes = asBytes(data);

    if (!bytes) {
        throw new BTError(`Expected type of argument 'data' is ${ ANY_BIN_TYPE }, but ${ fmtType(data) } given`);
    }

    return String.fromCharCode.apply(null, <any>bytes);
};
