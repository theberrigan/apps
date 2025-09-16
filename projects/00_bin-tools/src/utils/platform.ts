import { U16A, U8A } from '../common/types';


export const isLittleEndianPlatform : boolean = (() => {
    const u8a  = new U8A([ 0x12, 0x34 ]);
    const u16a = new U16A(u8a.buffer);

    return u16a[0] === 0x3412;
})();
