import { TAnyBin, TBase64, U8A } from '../common/types';
import { binToText, textToBin } from './text';


export const strToBase64 = globalThis.btoa;
export const base64ToStr = globalThis.atob;

// TODO: check base64 type
export const base64ToBin = (base64 : TBase64) : U8A => {
    return textToBin(base64ToStr(base64));
};

export const binToBase64 = (data : TAnyBin) : TBase64 => {
    return strToBase64(binToText(data));
};
