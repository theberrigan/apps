import { TBBGrowSizeFn } from './types';
import { ceil, min, nextPOT } from '../utils/math';
import { BinBuffer } from './index';


export const defaultGrowSizeFn : TBBGrowSizeFn = (
    minBufferSize : number,
    maxPageSize   : number,
    _             : BinBuffer
) : number => {
    const pageSize = min(nextPOT(minBufferSize), nextPOT(maxPageSize));
    const pagedBufferSize = ceil(minBufferSize / pageSize) * pageSize;

    // If free space in last incomplete page is less than
    // half the size of a page, then add one more extra page
    if ((pagedBufferSize - minBufferSize) < (pageSize / 2)) {
        return pagedBufferSize + pageSize;
    }

    return pagedBufferSize;
};
