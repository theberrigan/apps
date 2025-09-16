import { TAnyBin, TBase64DataURL, U8A } from '../common/types';
import { BTError } from '../common/errors';
import { ANY_BIN_TYPE } from '../common/constants';
import { fmtType } from '../utils/debug';
import { isAnyBin, isNone, isStr } from '../common/type-checks';
import { binToBase64 } from './base64';


// Private
export const _binToDataUrl = (data : TAnyBin, mimeType : string = 'text/plain') : TBase64DataURL => {
    // data:text/plain;base64,<data>
    return `data:${ mimeType };base64,${ binToBase64(data) }`;
};

// Public
export const binToDataUrl = (data : TAnyBin, mimeType : string = 'text/plain') : TBase64DataURL => {
    if (!isAnyBin(data)) {
        throw new BTError(`Expected type of argument 'data' is ${ ANY_BIN_TYPE }, but ${ fmtType(data) } given`);
    }

    if (!isStr(mimeType) || !mimeType.trim()) {
        throw new BTError(`Expected type of argument 'mimeType' is non-empty string, but ${ fmtType(mimeType) } given`);
    }

    mimeType = mimeType.trim();

    return _binToDataUrl(data, mimeType);
};

// TODO: convert to sync
export const _dataUrlToBin = async (dataUrl : TBase64DataURL) : Promise<U8A> => {
    const response : Blob | null = await fetch(dataUrl).then((response) => {
        return response.blob();
    }).catch(() : Promise<null> => {
        return null;
    });

    if (response === null) {
        throw new BTError('Failed to decode Data URL');
    }

    const buffer = await response.arrayBuffer();

    return new U8A(buffer);
};

// Public
export const dataUrlToBin = async (dataUrl : TBase64DataURL) : Promise<U8A> => {
    if (!isStr(dataUrl)) {
        throw new BTError(`Expected type of argument 'dataUrl' is string, but ${ fmtType(dataUrl) } given`);
    }

    return _dataUrlToBin(dataUrl);
};
