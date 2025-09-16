import { TAnyArrayBuffer, TAnyBin, THexString } from '../common/types';
import { BinBuffer } from './index';


export type TBBGrowSizeFn = (minBufferSize : number, maxPageSize : number, binBuffer : BinBuffer) => number;

// NOTE: Do not change the numeric values since they are used as indices into an array
export enum EBBIntWriteMode {
    Cast   = 0,
    Clamp  = 1,
    Strict = 2,
}

export enum EBBSeekFrom {
    Start = 0,
    Here  = 1,
    End   = 2,
}

export type TBBSource = TAnyBin | BinBuffer | THexString;

export interface IBBOptions {
    source?          : TBBSource | null;
    sourceOffset?    : number | null;
    sourceSize?      : number | null;
    forceCopySource? : boolean | null;
    size?            : number | null;
    capacity?        : number | null;
    fullCopy?        : boolean | null;
    forceUnshare?    : boolean | null;
    autoCapacity?    : boolean | null;
    growSizeFn?      : TBBGrowSizeFn | null;
    zeroMemOnGrow?   : boolean | null;
    maxPageSize?     : number | null;
    readOnly?        : boolean | null;
    intWriteMode?    : EBBIntWriteMode | null;
    bigEndian?       : boolean | null;
}

export type TBBCreateInput = TBBSource | IBBOptions | number | null | undefined;

export interface TGetBufferFromSourceResult {
    buffer           : TAnyArrayBuffer | null;
    bufferDataOffset : number;
    bufferDataSize   : number;
    bufferCapacity   : number;
}

export interface IBBInternalOptions {
    view            : DataView;
    dataSize        : number;
    autoCapacity    : boolean;
    readOnly        : boolean;
    intWriteMode    : EBBIntWriteMode;
    bigEndian       : boolean;
    maxPageSize     : number;
    growSizeFn      : TBBGrowSizeFn;
    zeroMemOnGrow   : boolean;
    fullCopy        : boolean;
}

export interface IBBInternalState {
    cursor        : number;
    cursorStack   : IBBCursorStack;
    cursorMap     : IBBCursorMap;
    lastReadSize  : number;
    lastWriteSize : number;
}

export type IBBCursorStack = number[];

export interface IBBCursorMap {
    [ key : string ] : number;
}
