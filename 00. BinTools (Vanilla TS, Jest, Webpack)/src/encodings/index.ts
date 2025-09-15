import { U8A } from '../common/types';
import { encodeUTF16 } from './codecs/utf16';
import { encodeCP866 } from './codecs/cp866';
import { encodeCP1251 } from './codecs/cp1251';
import { encodeCP1252 } from './codecs/cp1252';


type TEncodeFn = (
    typeof TextEncoder.prototype.encode |
    ((str : string, withBOM? : boolean) => U8A)
);

export type TEncodeFactory = () => TEncodeFn;

export type TDecodeFn = typeof TextDecoder.prototype.decode;
export type TDecodeFactory = (fatal : boolean, ignoreBOM : boolean) => TDecodeFn;

// Memory leak???
/*
const getEncodeFn = (() => {
    const cache : {
        [ key : string ] : TEncodeFn
    } = {};

    return (encoding : string) : TEncodeFn => {
        const fn = cache[encoding];

        if (fn) {
            return fn;
        }

        const encoder = new TextEncoder();

        return (cache[encoding] = encoder.encode.bind(encoder));
    };
})();

const getDecodeFn = (() => {
    const cache : {
        [ key : string ] : TDecodeFn
    } = {};

    return (encoding : string, fatal : boolean, ignoreBOM : boolean) : TDecodeFn => {
        const key = `${ encoding }|${ fatal }|${ ignoreBOM }`;

        const fn = cache[key];

        if (fn) {
            return fn;
        }

        const decoder = new TextDecoder(encoding, {
            fatal,
            ignoreBOM
        });

        return (cache[key] = decoder.decode.bind(decoder));
    };
})();
*/

const getEncodeFn = () : TEncodeFn => {
    const encoder = new TextEncoder();

    return encoder.encode.bind(encoder);
};

const getDecodeFn = (encoding : string, fatal : boolean, ignoreBOM : boolean) : TDecodeFn => {
    const decoder = new TextDecoder(encoding, {
        fatal,
        ignoreBOM
    });

    return decoder.decode.bind(decoder);
};

type TEncodingReadCharFn = (
    typeof DataView.prototype.getUint8  |
    typeof DataView.prototype.getUint16 |
    typeof DataView.prototype.getUint32
);


export interface IEncodingInfoItem {
    aliases       : string[];
    charSize      : number;
    readCharFn    : TEncodingReadCharFn;
    decodeFactory : TDecodeFactory | null;
    encodeFactory : TEncodeFactory | null;
}

// export only for testing
// noinspection SpellCheckingInspection
export const ENCODING_INFO : IEncodingInfoItem[] = [
    {
        aliases:        [ 'utf-8', 'utf8', 'unicode-1-1-utf-8' ],
        charSize:       1,
        readCharFn:     DataView.prototype.getUint8,
        decodeFactory:  (fatal : boolean, ignoreBOM : boolean) => getDecodeFn('utf-8', fatal, ignoreBOM),
        encodeFactory:  getEncodeFn
    },
    {
        aliases:        [ 'utf-16le', 'utf-16' ],
        charSize:       2,
        readCharFn:     DataView.prototype.getUint16,
        decodeFactory:  (fatal : boolean, ignoreBOM : boolean) => getDecodeFn('utf-16le', fatal, ignoreBOM),
        encodeFactory:  () => (str : string, withBOM : boolean = false) => encodeUTF16(str, withBOM, false)
    },
    {
        aliases:        [ 'utf-16be' ],
        charSize:       2,
        readCharFn:     DataView.prototype.getUint16,
        decodeFactory:  (fatal : boolean, ignoreBOM : boolean) => getDecodeFn('utf-16be', fatal, ignoreBOM),
        encodeFactory:  () => (str : string, withBOM : boolean = false) => encodeUTF16(str, withBOM, true)
    },
    {
        aliases:        [ 'cp866', 'ibm866', '866', 'csibm866' ],
        charSize:       1,
        readCharFn:     DataView.prototype.getUint8,
        decodeFactory:  (fatal : boolean, ignoreBOM : boolean) => getDecodeFn('cp866', fatal, ignoreBOM),
        encodeFactory:  () => encodeCP866
    },
    {
        aliases:        [ 'iso-8859-2', 'csisolatin2', 'iso-ir-101', 'iso8859-2', 'iso88592', 'iso_8859-2', 'iso_8859-2:1987', 'l2', 'latin2' ],
        charSize:       1,
        readCharFn:     DataView.prototype.getUint8,
        decodeFactory:  (fatal : boolean, ignoreBOM : boolean) => getDecodeFn('iso-8859-2', fatal, ignoreBOM),
        encodeFactory:  null
    },
    {
        aliases:        [ 'iso-8859-3', 'csisolatin3', 'iso-ir-109', 'iso8859-3', 'iso88593', 'iso_8859-3', 'iso_8859-3:1988', 'l3', 'latin3' ],
        charSize:       1,
        readCharFn:     DataView.prototype.getUint8,
        decodeFactory:  (fatal : boolean, ignoreBOM : boolean) => getDecodeFn('iso-8859-3', fatal, ignoreBOM),
        encodeFactory:  null
    },
    {
        aliases:        [ 'iso-8859-4', 'csisolatin4', 'iso-ir-110', 'iso8859-4', 'iso88594', 'iso_8859-4', 'iso_8859-4:1988', 'l4', 'latin4' ],
        charSize:       1,
        readCharFn:     DataView.prototype.getUint8,
        decodeFactory:  (fatal : boolean, ignoreBOM : boolean) => getDecodeFn('iso-8859-4', fatal, ignoreBOM),
        encodeFactory:  null
    },
    {
        aliases:        [ 'iso-8859-5', 'csisolatincyrillic', 'cyrillic', 'iso-ir-144', 'iso88595', 'iso_8859-5', 'iso_8859-5:1988' ],
        charSize:       1,
        readCharFn:     DataView.prototype.getUint8,
        decodeFactory:  (fatal : boolean, ignoreBOM : boolean) => getDecodeFn('iso-8859-5', fatal, ignoreBOM),
        encodeFactory:  null
    },
    {
        aliases:        [ 'iso-8859-6', 'arabic', 'asmo-708', 'csiso88596e', 'csiso88596i', 'csisolatinarabic', 'ecma-114', 'iso-8859-6-e', 'iso-8859-6-i', 'iso-ir-127', 'iso8859-6', 'iso88596', 'iso_8859-6', 'iso_8859-6:1987' ],
        charSize:       1,
        readCharFn:     DataView.prototype.getUint8,
        decodeFactory:  (fatal : boolean, ignoreBOM : boolean) => getDecodeFn('iso-8859-6', fatal, ignoreBOM),
        encodeFactory:  null
    },
    {
        aliases:        [ 'iso-8859-7', 'csisolatingreek', 'ecma-118', 'elot_928', 'greek', 'greek8', 'iso-ir-126', 'iso8859-7', 'iso88597', 'iso_8859-7', 'iso_8859-7:1987', 'sun_eu_greek' ],
        charSize:       1,
        readCharFn:     DataView.prototype.getUint8,
        decodeFactory:  (fatal : boolean, ignoreBOM : boolean) => getDecodeFn('iso-8859-7', fatal, ignoreBOM),
        encodeFactory:  null
    },
    {
        aliases:        [ 'iso-8859-8', 'csiso88598e', 'csisolatinhebrew', 'hebrew', 'iso-8859-8-e', 'iso-ir-138', 'iso8859-8', 'iso88598', 'iso_8859-8', 'iso_8859-8:1988', 'visual' ],
        charSize:       1,
        readCharFn:     DataView.prototype.getUint8,
        decodeFactory:  (fatal : boolean, ignoreBOM : boolean) => getDecodeFn('iso-8859-8', fatal, ignoreBOM),
        encodeFactory:  null
    },
    {
        aliases:        [ 'iso-8859-8-i', 'iso-8859-8i', 'csiso88598i', 'logical' ],
        charSize:       1,
        readCharFn:     DataView.prototype.getUint8,
        decodeFactory:  (fatal : boolean, ignoreBOM : boolean) => getDecodeFn('iso-8859-8-i', fatal, ignoreBOM),
        encodeFactory:  null
    },
    {
        aliases:        [ 'iso-8859-10', 'csisolatin6', 'iso-ir-157', 'iso8859-10', 'iso885910', 'l6', 'latin6' ],
        charSize:       1,
        readCharFn:     DataView.prototype.getUint8,
        decodeFactory:  (fatal : boolean, ignoreBOM : boolean) => getDecodeFn('iso-8859-10', fatal, ignoreBOM),
        encodeFactory:  null
    },
    {
        aliases:        [ 'iso-8859-13', 'iso8859-13', 'iso885913' ],
        charSize:       1,
        readCharFn:     DataView.prototype.getUint8,
        decodeFactory:  (fatal : boolean, ignoreBOM : boolean) => getDecodeFn('iso-8859-13', fatal, ignoreBOM),
        encodeFactory:  null
    },
    {
        aliases:        [ 'iso-8859-14', 'iso8859-14', 'iso885914' ],
        charSize:       1,
        readCharFn:     DataView.prototype.getUint8,
        decodeFactory:  (fatal : boolean, ignoreBOM : boolean) => getDecodeFn('iso-8859-14', fatal, ignoreBOM),
        encodeFactory:  null
    },
    {
        aliases:        [ 'iso-8859-15', 'csisolatin9', 'iso8859-15', 'iso885915', 'l9', 'latin9' ],
        charSize:       1,
        readCharFn:     DataView.prototype.getUint8,
        decodeFactory:  (fatal : boolean, ignoreBOM : boolean) => getDecodeFn('iso-8859-15', fatal, ignoreBOM),
        encodeFactory:  null
    },
    // {
    //     aliases:        [ 'iso-8859-16' ],
    //     charSize:       1,
    //     readCharFn:     DataView.prototype.getUint8,
    //     decodeFactory:  (fatal : boolean, ignoreBOM : boolean) => getDecodeFn('iso-8859-16', fatal, ignoreBOM),
    //     encodeFactory:  null
    // },
    {
        aliases:        [ 'koi8-r', 'cskoi8r', 'koi', 'koi8', 'koi8_r' ],
        charSize:       1,
        readCharFn:     DataView.prototype.getUint8,
        decodeFactory:  (fatal : boolean, ignoreBOM : boolean) => getDecodeFn('koi8-r', fatal, ignoreBOM),
        encodeFactory:  null
    },
    {
        aliases:        [ 'koi8-u' ],
        charSize:       1,
        readCharFn:     DataView.prototype.getUint8,
        decodeFactory:  (fatal : boolean, ignoreBOM : boolean) => getDecodeFn('koi8-u', fatal, ignoreBOM),
        encodeFactory:  null
    },
    {
        aliases:        [ 'macintosh', 'csmacintosh', 'mac', 'x-mac-roman' ],
        charSize:       1,
        readCharFn:     DataView.prototype.getUint8,
        decodeFactory:  (fatal : boolean, ignoreBOM : boolean) => getDecodeFn('macintosh', fatal, ignoreBOM),
        encodeFactory:  null
    },
    {
        aliases:        [ 'windows-874', 'dos-874', 'iso-8859-11', 'iso8859-11', 'iso885911', 'tis-620' ],
        charSize:       1,
        readCharFn:     DataView.prototype.getUint8,
        decodeFactory:  (fatal : boolean, ignoreBOM : boolean) => getDecodeFn('windows-874', fatal, ignoreBOM),
        encodeFactory:  null
    },
    {
        aliases:        [ 'windows-1250', 'cp1250', 'x-cp1250' ],
        charSize:       1,
        readCharFn:     DataView.prototype.getUint8,
        decodeFactory:  (fatal : boolean, ignoreBOM : boolean) => getDecodeFn('windows-1250', fatal, ignoreBOM),
        encodeFactory:  null
    },
    {
        aliases:        [ 'cp1251', 'windows-1251', 'x-cp1251' ],
        charSize:       1,
        readCharFn:     DataView.prototype.getUint8,
        decodeFactory:  (fatal : boolean, ignoreBOM : boolean) => getDecodeFn('windows-1251', fatal, ignoreBOM),
        encodeFactory:  () => encodeCP1251
    },
    {
        aliases:        [ 'cp1252', 'windows-1252', 'ansi_x3.4-1968', 'ascii', 'cp819', 'csisolatin1', 'ibm819', 'iso-8859-1', 'iso-ir-100', 'iso8859-1', 'iso88591', 'iso_8859-1', 'iso_8859-1:1987', 'l1', 'latin1', 'us-ascii', 'x-cp1252' ],
        charSize:       1,
        readCharFn:     DataView.prototype.getUint8,
        decodeFactory:  (fatal : boolean, ignoreBOM : boolean) => getDecodeFn('windows-1252', fatal, ignoreBOM),
        encodeFactory:  () => encodeCP1252
    },
    {
        aliases:        [ 'windows-1253', 'cp1253', 'x-cp1253' ],
        charSize:       1,
        readCharFn:     DataView.prototype.getUint8,
        decodeFactory:  (fatal : boolean, ignoreBOM : boolean) => getDecodeFn('windows-1253', fatal, ignoreBOM),
        encodeFactory:  null
    },
    {
        aliases:        [ 'windows-1254', 'cp1254', 'csisolatin5', 'iso-8859-9', 'iso-ir-148', 'iso8859-9', 'iso88599', 'iso_8859-9', 'iso_8859-9:1989', 'l5', 'latin5', 'x-cp1254' ],
        charSize:       1,
        readCharFn:     DataView.prototype.getUint8,
        decodeFactory:  (fatal : boolean, ignoreBOM : boolean) => getDecodeFn('windows-1254', fatal, ignoreBOM),
        encodeFactory:  null
    },
    {
        aliases:        [ 'windows-1255', 'cp1255', 'x-cp1255' ],
        charSize:       1,
        readCharFn:     DataView.prototype.getUint8,
        decodeFactory:  (fatal : boolean, ignoreBOM : boolean) => getDecodeFn('windows-1255', fatal, ignoreBOM),
        encodeFactory:  null
    },
    {
        aliases:        [ 'windows-1256', 'cp1256', 'x-cp1256' ],
        charSize:       1,
        readCharFn:     DataView.prototype.getUint8,
        decodeFactory:  (fatal : boolean, ignoreBOM : boolean) => getDecodeFn('windows-1256', fatal, ignoreBOM),
        encodeFactory:  null
    },
    {
        aliases:        [ 'windows-1257', 'cp1257', 'x-cp1257' ],
        charSize:       1,
        readCharFn:     DataView.prototype.getUint8,
        decodeFactory:  (fatal : boolean, ignoreBOM : boolean) => getDecodeFn('windows-1257', fatal, ignoreBOM),
        encodeFactory:  null
    },
    {
        aliases:        [ 'windows-1258', 'cp1258', 'x-cp1258' ],
        charSize:       1,
        readCharFn:     DataView.prototype.getUint8,
        decodeFactory:  (fatal : boolean, ignoreBOM : boolean) => getDecodeFn('windows-1258', fatal, ignoreBOM),
        encodeFactory:  null
    },
    {
        aliases:        [ 'x-mac-cyrillic', 'x-mac-ukrainian' ],
        charSize:       1,
        readCharFn:     DataView.prototype.getUint8,
        decodeFactory:  (fatal : boolean, ignoreBOM : boolean) => getDecodeFn('x-mac-cyrillic', fatal, ignoreBOM),
        encodeFactory:  null
    },
    {
        aliases:        [ 'gbk', 'chinese', 'csgb2312', 'csiso58gb231280', 'gb2312', 'gb_2312', 'gb_2312-80', 'iso-ir-58', 'x-gbk' ],
        charSize:       1,
        readCharFn:     DataView.prototype.getUint8,
        decodeFactory:  (fatal : boolean, ignoreBOM : boolean) => getDecodeFn('gbk', fatal, ignoreBOM),
        encodeFactory:  null
    },
    {
        aliases:        [ 'gb18030' ],
        charSize:       1,
        readCharFn:     DataView.prototype.getUint8,
        decodeFactory:  (fatal : boolean, ignoreBOM : boolean) => getDecodeFn('gb18030', fatal, ignoreBOM),
        encodeFactory:  null
    },
    // {
    //     aliases:        [ 'hz-gb-2312' ],
    //     charSize:       1,
    //     readCharFn:     DataView.prototype.getUint8,
    //     decodeFactory:  (fatal : boolean, ignoreBOM : boolean) => getDecodeFn('hz-gb-2312', fatal, ignoreBOM),
    //     encodeFactory:  null
    // },
    {
        aliases:        [ 'big5', 'big5-hkscs', 'cn-big5', 'csbig5', 'x-x-big5' ],
        charSize:       1,
        readCharFn:     DataView.prototype.getUint8,
        decodeFactory:  (fatal : boolean, ignoreBOM : boolean) => getDecodeFn('big5', fatal, ignoreBOM),
        encodeFactory:  null
    },
    {
        aliases:        [ 'euc-jp', 'cseucpkdfmtjapanese', 'x-euc-jp' ],
        charSize:       1,
        readCharFn:     DataView.prototype.getUint8,
        decodeFactory:  (fatal : boolean, ignoreBOM : boolean) => getDecodeFn('euc-jp', fatal, ignoreBOM),
        encodeFactory:  null
    },
    {
        aliases:        [ 'iso-2022-jp', 'csiso2022jp' ],
        charSize:       1,
        readCharFn:     DataView.prototype.getUint8,
        decodeFactory:  (fatal : boolean, ignoreBOM : boolean) => getDecodeFn('iso-2022-jp', fatal, ignoreBOM),
        encodeFactory:  null
    },
    {
        aliases:        [ 'shift-jis', 'csshiftjis', 'ms_kanji', 'shift_jis', 'sjis', 'windows-31j', 'x-sjis' ],
        charSize:       1,
        readCharFn:     DataView.prototype.getUint8,
        decodeFactory:  (fatal : boolean, ignoreBOM : boolean) => getDecodeFn('shift-jis', fatal, ignoreBOM),
        encodeFactory:  null
    },
    {
        aliases:        [ 'euc-kr', 'cseuckr', 'csksc56011987', 'iso-ir-149', 'korean', 'ks_c_5601-1987', 'ks_c_5601-1989', 'ksc5601', 'ksc_5601', 'windows-949' ],
        charSize:       1,
        readCharFn:     DataView.prototype.getUint8,
        decodeFactory:  (fatal : boolean, ignoreBOM : boolean) => getDecodeFn('euc-kr', fatal, ignoreBOM),
        encodeFactory:  null
    },
    // {
    //     aliases:        [ 'iso-2022-kr', 'csiso2022kr' ],
    //     charSize:       1,
    //     readCharFn:     DataView.prototype.getUint8,
    //     decodeFactory:  (fatal : boolean, ignoreBOM : boolean) => getDecodeFn('iso-2022-kr', fatal, ignoreBOM),
    //     encodeFactory:  null
    // },
];

const ENCODING_MAP : {
    [ encoding : string ] : IEncodingInfoItem
} = {};

ENCODING_INFO.forEach((info) => {
    info.aliases.forEach((alias) => {
        ENCODING_MAP[alias] = info;
    });
});

export const getEncodingInfo = (encoding : string) : IEncodingInfoItem | null => {
    return ENCODING_MAP[encoding.toLowerCase()] || null;
};

export {
    encodeUTF16,
    encodeCP866,
    encodeCP1251,
    encodeCP1252,
};
