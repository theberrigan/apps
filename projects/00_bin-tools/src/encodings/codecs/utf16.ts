import { U16_BYTES } from '../../common/native-types';
import { U8A } from '../../common/types';


const UTF16_BOM = 0xFEFF;  // BE

// JS strings already in UTF-16, just write u16 codepoints
// https://en.wikipedia.org/wiki/UTF-16
export const encodeUTF16 = (str : string, withBOM : boolean = false, bigEndian : boolean = false) : U8A => {
    if (!str) {
        return new U8A(0);
    }

    const codeCount = str.length;
    const bomByte   = Number(withBOM);
    const byteCount = U16_BYTES * (bomByte + codeCount);
    const buffer    = new ArrayBuffer(byteCount);
    const view      = new DataView(buffer);

    if (withBOM) {
        view.setUint16(0, UTF16_BOM, !bigEndian);
    }

    for (let i = 0; i < codeCount; ++i) {
        const offset = U16_BYTES * (bomByte + i);
        const code   = str.charCodeAt(i);

        view.setUint16(offset, code, !bigEndian);
    }

    return new U8A(view.buffer);
};
