import { BTError } from '../../common/errors';
import { U8A } from '../../common/types';


export type TEncodingFn = (str : string) => U8A;

export interface TEncodingTable {
    [ key : string ] : number;
}

// https://docs.python.org/3/library/codecs.html#standard-encodings
// https://encoding.spec.whatwg.org/#names-and-labels
export const createEncodingFn = (name : string, table : TEncodingTable) : TEncodingFn => {
    return (str : string) : U8A => {
        const bytes : number[] = [];

        for (let char of str) {
            const code = char.codePointAt(0);

            if (code === undefined || code === null) {
                throw new BTError(`Failed to encode character '${ char }' to ${ name }`);
            }

            // ASCII
            if (code < 0x80) {
                bytes.push(code);

            // Current encoding
            } else {
                const byte = table[char];

                if (byte === undefined || byte === null) {
                    throw new BTError(`Failed to encode character '${ char }' to ${ name }`);
                }

                bytes.push(byte);
            }
        }

        return new U8A(bytes);
    };
};
