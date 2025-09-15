import {
    TBytes,
    TAnyArrayBuffer,
    TAnyBin,
    TTypedArray,
    TTypedArrayCtor,
    TBase64DataURL,
    TDataViewGetFn,
    TDataViewSetFn,
    U8A,
    I8A,
    U32A,
    U8CA,
    I16A,
    U16A,
    I32A,
    I64A,
    U64A,
    F32A,
    F64A,
} from '../common/types';
import { ceil, max, min, nextPOT, trunc } from '../utils/math';
import { isBrowser } from '../common/env';
import { getEncodingInfo, IEncodingInfoItem, TDecodeFactory } from '../encodings';
import { BTError } from '../common/errors';
import {
    i16,
    i16c, i16s,
    i32,
    i32c, i32s, i64, i64c, i64s,
    i8,
    i8c, i8s,
    u16,
    u16c, u16s,
    u32,
    u32c, u32s, u64, u64c, u64s,
    u8,
    u8c, u8s,
} from '../utils/type-cast';
import { fmtType } from '../utils/debug';
import { ANY_BIN_TYPE } from '../common/constants';
import { _binToDataUrl } from '../bin/data-url';
import { _binToHex, _hexToBin, isHex } from '../bin/hex';
import { bigIntToBin, binToBigInt } from '../bin/bigint';
import {
    EBBIntWriteMode, EBBSeekFrom, IBBCursorMap, IBBCursorStack, IBBInternalOptions,
    IBBInternalState,
    IBBOptions,
    TBBGrowSizeFn,
    TBBCreateInput,
    TBBSource,
    TGetBufferFromSourceResult,
} from './types';
import { defaultGrowSizeFn } from './functions';
import {
    isAnyArrayBuffer,
    isAnyBin,
    isBinView, isBool, isByteInt, isFn,
    isNone,
    isNum,
    isPlainObject,
    isSafeInt, isSharedArrayBuffer,
    isStr,
} from '../common/type-checks';
import { hasEnumIntValue } from '../utils/misc';
import { cloneView, copyAnyArrayBuffer, sliceArrayBuffer } from '../bin/buffers';
import { asBytes } from '../bin/bytes';


export class BinBuffer {
    static get DEFAULT_OPT_SOURCE () : null {
        return null;
    }

    static get DEFAULT_OPT_SOURCE_OFFSET () : number {
        return 0;  // must be non-negative integer
    }

    static get DEFAULT_OPT_SOURCE_SIZE () : null {
        return null;
    }

    static get DEFAULT_OPT_FORCE_COPY_SOURCE () : boolean {
        return false;
    }

    static get DEFAULT_OPT_SIZE () : null {
        return null;
    }

    static get DEFAULT_OPT_CAPACITY () : null {
        return null;  // don't change, must be null
    }

    static get DEFAULT_OPT_FULL_COPY () : boolean {
        return true;
    }

    static get DEFAULT_OPT_FORCE_UNSHARE () : boolean {
        return false;
    }

    static get DEFAULT_OPT_AUTO_CAPACITY () : boolean {
        return false;
    }

    static get DEFAULT_OPT_GROW_SIZE_FN () : TBBGrowSizeFn {
        return defaultGrowSizeFn;
    }

    static get DEFAULT_OPT_ZERO_MEM_ON_GROW () : boolean {
        return false;
    }

    static get DEFAULT_OPT_MAX_PAGE_SIZE () : number {
        return 2 * 1024 * 1024;  // 2mb
    }

    static get DEFAULT_OPT_READ_ONLY () : boolean {
        return false;
    }

    static get DEFAULT_OPT_INT_WRITE_MODE () : EBBIntWriteMode {
        return EBBIntWriteMode.Strict;
    }

    static get DEFAULT_OPT_BIG_ENDIAN () : boolean {
        return false;
    }

    private static get _DEFAULT_STATE () : IBBInternalState {
        return {
            cursor: 0,
            cursorStack: [],
            cursorMap: {},
            lastReadSize: 0,
            lastWriteSize: 0,
        };
    }

    static get DEFAULT_OPTIONS () : IBBOptions {
        return {
            source:           BinBuffer.DEFAULT_OPT_SOURCE,
            sourceOffset:     BinBuffer.DEFAULT_OPT_SOURCE_OFFSET,
            sourceSize:       BinBuffer.DEFAULT_OPT_SOURCE_SIZE,
            forceCopySource:  BinBuffer.DEFAULT_OPT_FORCE_COPY_SOURCE,
            size:             BinBuffer.DEFAULT_OPT_SIZE,
            capacity:         BinBuffer.DEFAULT_OPT_CAPACITY,
            fullCopy:         BinBuffer.DEFAULT_OPT_FULL_COPY,
            forceUnshare:     BinBuffer.DEFAULT_OPT_FORCE_UNSHARE,
            autoCapacity:     BinBuffer.DEFAULT_OPT_AUTO_CAPACITY,
            growSizeFn:       BinBuffer.DEFAULT_OPT_GROW_SIZE_FN,
            zeroMemOnGrow:    BinBuffer.DEFAULT_OPT_ZERO_MEM_ON_GROW,
            maxPageSize:      BinBuffer.DEFAULT_OPT_MAX_PAGE_SIZE,
            readOnly:         BinBuffer.DEFAULT_OPT_READ_ONLY,
            intWriteMode:     BinBuffer.DEFAULT_OPT_INT_WRITE_MODE,
            bigEndian:        BinBuffer.DEFAULT_OPT_BIG_ENDIAN,
        };
    }

    private static _normalizeOptions = (optionsOrSourceOrSize : TBBCreateInput) : IBBOptions => {
        let options : IBBOptions = {};

        // Don't validate, just normalize it
        if (isNum(optionsOrSourceOrSize)) {
            options.size = optionsOrSourceOrSize;

        } else if (
            isAnyBin(optionsOrSourceOrSize) ||
            optionsOrSourceOrSize instanceof BinBuffer ||
            isStr(optionsOrSourceOrSize)
        ) {
            options.source = optionsOrSourceOrSize;

        } else if (isPlainObject(optionsOrSourceOrSize)) {
            options = <IBBOptions>optionsOrSourceOrSize;

        } else if (!isNone(optionsOrSourceOrSize)) {
            BinBuffer._throwUnexpectedOptionsType(optionsOrSourceOrSize);
        }

        return options;
    };

    private static _getBufferFromSource = (source : TBBSource | null) : TGetBufferFromSourceResult => {
        const result : TGetBufferFromSourceResult = {
            buffer:           null,
            bufferDataOffset: 0,
            bufferDataSize:   0,
            bufferCapacity:   0,  // don't set to null
        };

        // No source
        if (isNone(source)) {
            result.buffer           = null;  // don't change, must be null
            result.bufferDataOffset = 0;
            result.bufferDataSize   = 0;
            result.bufferCapacity   = 0;

        // Hex string (THexString)
        } else if (isHex(source)) {
            result.buffer           = _hexToBin(source).buffer;
            result.bufferDataOffset = 0;
            result.bufferDataSize   = result.buffer.byteLength;
            result.bufferCapacity   = result.bufferDataSize;

        // Instance of this class
        } else if (source instanceof BinBuffer) {
            result.buffer           = source.internalBuffer;
            result.bufferDataOffset = source.internalOffset;
            result.bufferDataSize   = source.size;
            result.bufferCapacity   = source.capacity;

        // TypedArray | DataView | node:Buffer (Uint8Array)
        } else if (isBinView(source)) {
            result.buffer           = source.buffer;
            result.bufferDataOffset = source.byteOffset;
            result.bufferDataSize   = source.byteLength;
            result.bufferCapacity   = result.bufferDataSize;

        // ArrayBuffer | SharedArrayBuffer
        } else if (isAnyArrayBuffer(source)) {
            result.buffer           = source;
            result.bufferDataOffset = 0;
            result.bufferDataSize   = source.byteLength;
            result.bufferCapacity   = result.bufferDataSize;

        } else {
            BinBuffer._throwUnexpectedOptionsType(source);
        }

        return result;
    };

    private static _throwUnexpectedOptionsType = (value : any) : never => {
        throw new BTError(
            `Argument 'optionsOrSourceOrSize' expected to be ` +
            `either options object of type IBBOptions, ` +
            `or source of type ${ ANY_BIN_TYPE } | BinBuffer | THexString, ` +
            `or buffer size of safe non-negative integer type, ` +
            `but ${ fmtType(value) } given`
        );
    };

    static create (optionsOrSourceOrSize? : TBBCreateInput) : BinBuffer {
        let {
            source,
            sourceOffset,
            sourceSize,
            forceCopySource,
            size,
            capacity,
            fullCopy,
            forceUnshare,
            autoCapacity,
            growSizeFn,
            zeroMemOnGrow,
            maxPageSize,
            readOnly,
            intWriteMode,
            bigEndian,
        } = BinBuffer._normalizeOptions(optionsOrSourceOrSize);

        optionsOrSourceOrSize = null;

        source ??= BinBuffer.DEFAULT_OPT_SOURCE;

        let {
            buffer,
            bufferDataOffset,
            bufferDataSize,
            bufferCapacity,  // inherited from BinBuffer source
        } = BinBuffer._getBufferFromSource(source);

        if (!isNone(sourceOffset)) {
            if (buffer === null) {
                throw new BTError(`Option 'sourceOffset' is specified, but 'source' is not`);
            }

            if (!isSafeInt(sourceOffset) || sourceOffset < 0) {
                throw new BTError(
                    `Expected type of option 'sourceOffset' is safe ` +
                    `non-negative integer, but ${ fmtType(sourceOffset) } given`
                );
            }

            if (sourceOffset > bufferDataSize) {
                throw new BTError(
                    `Option 'sourceOffset' (${ sourceOffset }) is greater ` +
                    `than actual source data size (${ bufferDataSize })`
                );
            }

            bufferDataOffset += sourceOffset;
            bufferDataSize   -= sourceOffset;
            bufferCapacity   -= sourceOffset;
        }

        // Deal with sourceSize after sourceOffset
        if (!isNone(sourceSize)) {
            if (buffer === null) {
                throw new BTError(`Option 'sourceSize' is specified, but 'source' is not`);
            }

            if (!isSafeInt(sourceSize) || sourceSize < 0) {
                throw new BTError(
                    `Expected type of option 'sourceSize' is safe ` +
                    `non-negative integer, but ${ fmtType(sourceSize) } given`
                );
            }

            if (sourceSize > bufferDataSize) {
                throw new BTError(
                    `Option 'sourceSize' (${ sourceSize }) is greater ` +
                    `than actual source data size (${ bufferDataSize })`
                );
            }

            bufferDataSize = sourceSize;  // became smaller or didn't change
        }

        // Deal with size after sourceOffset and sourceSize
        if (isNone(size)) {
            size = bufferDataSize;
        } else if (!isSafeInt(size) || size < 0) {
            throw new BTError(
                `Expected type of option 'size' is safe ` +
                `non-negative integer, but ${ fmtType(size) } given`
            );
        } else if (size < bufferDataSize) {
            throw new BTError(
                `Option 'size' (${ size }) is too small ` +
                `to fit the source data of size ${ bufferDataSize }`
            );
        }

        // Deal with capacity after sourceOffset, sourceSize and size
        if (isNone(capacity)) {
            capacity = max(size, bufferCapacity);
        } else if (!isSafeInt(capacity) || capacity < 0) {
            throw new BTError(
                `Expected type of option 'capacity' is safe ` +
                `non-negative integer, but ${ fmtType(capacity) } given`
            );
        } else if (capacity < bufferDataSize) {
            throw new BTError(
                `Option 'capacity' (${ capacity }) is too small ` +
                `to fit the source data of size ${ bufferDataSize }`
            );
        }

        if (isNone(forceCopySource)) {
            forceCopySource = BinBuffer.DEFAULT_OPT_FORCE_COPY_SOURCE;
        } else if (buffer === null && forceCopySource === true) {
            throw new BTError(`Option 'forceCopySource' is specified, but 'source' is not`);
        } else if (!isBool(forceCopySource)) {
            throw new BTError(
                `Expected type of option 'forceCopySource' ` +
                `is boolean, but ${ fmtType(forceCopySource) } given`
            );
        }

        if (isNone(autoCapacity)) {
            autoCapacity = BinBuffer.DEFAULT_OPT_AUTO_CAPACITY;
        } else if (!isBool(autoCapacity)) {
            throw new BTError(
                `Expected type of option 'autoCapacity' ` +
                `is boolean, but ${ fmtType(autoCapacity) } given`
            );
        }

        if (isNone(readOnly)) {
            readOnly = BinBuffer.DEFAULT_OPT_READ_ONLY;
        } else if (!isBool(readOnly)) {
            throw new BTError(
                `Expected type of option 'readOnly' ` +
                `is boolean, but ${ fmtType(readOnly) } given`
            );
        }

        if (isNone(bigEndian)) {
            bigEndian = BinBuffer.DEFAULT_OPT_BIG_ENDIAN;
        } else if (!isBool(bigEndian)) {
            throw new BTError(
                `Expected type of option 'bigEndian' ` +
                `is boolean, but ${ fmtType(bigEndian) } given`
            );
        }

        if (isNone(intWriteMode)) {
            intWriteMode = BinBuffer.DEFAULT_OPT_INT_WRITE_MODE;
        } else if (!hasEnumIntValue(intWriteMode, EBBIntWriteMode)) {
            throw new BTError(
                `Expected type of option 'intWriteMode' ` +
                `is EBBIntWriteMode, but ${ fmtType(intWriteMode) } given`
            );
        }

        if (isNone(maxPageSize)) {
            maxPageSize = BinBuffer.DEFAULT_OPT_MAX_PAGE_SIZE;
        } else if (!isSafeInt(maxPageSize) || maxPageSize <= 0) {
            throw new BTError(
                `Expected type of option 'maxPageSize' ` +
                `is safe positive integer, but ${ fmtType(maxPageSize) } given`
            );
        }

        if (isNone(zeroMemOnGrow)) {
            zeroMemOnGrow = BinBuffer.DEFAULT_OPT_ZERO_MEM_ON_GROW;
        } else if (!isBool(zeroMemOnGrow)) {
            throw new BTError(
                `Expected type of option 'zeroMemOnGrow' ` +
                `is boolean, but ${ fmtType(zeroMemOnGrow) } given`
            );
        }

        if (isNone(growSizeFn)) {
            growSizeFn = BinBuffer.DEFAULT_OPT_GROW_SIZE_FN;
        } else if (!isFn(growSizeFn)) {
            throw new BTError(
                `Expected type of option 'growSizeFn' ` +
                `is function, but ${ fmtType(growSizeFn) } given`
            );
        }

        if (isNone(fullCopy)) {
            fullCopy = BinBuffer.DEFAULT_OPT_FULL_COPY;
        } else if (!isBool(fullCopy)) {
            throw new BTError(
                `Expected type of option 'fullCopy' ` +
                `is boolean, but ${ fmtType(fullCopy) } given`
            );
        }

        // General rule:
        // bufferDataSize <= size <= capacity <= maxCapacity
        //
        // This is [Shared]ArrayBuffer, which was passed as 'source'
        // or was extracted from 'source'. It or its full or partial
        // copy will become a binBuffer.internalBuffer. This diagram
        // shows a case where bufferDataSize < size < capacity < maxCapacity.
        // +=======================+======================+=================+
        // |                       |----bufferDataSize----|_____            |
        // |                       |------------size------------|_____      |
        // |                       |-------------capacity-------------|_____|
        // |                       |----------------maxCapacity-------------|
        // +=======================+========================================+
        // ^-- buffer start        ^-- bufferDataOffset        buffer end --^
        //                         ^-- will be binBuffer.internalOffset

        let viewOffset = 0;

        if (buffer !== null) {
            const bufferSize    = buffer.byteLength;
            const maxCapacity   = bufferSize - bufferDataOffset;
            const needToExtend  = maxCapacity < capacity;
            const needToUnshare = forceUnshare && isSharedArrayBuffer(buffer);
            const needToCopy    = forceCopySource || needToExtend || needToUnshare;

            viewOffset = bufferDataOffset;

            if (needToCopy) {
                let dstSize   : number;
                let srcOffset : number;
                let srcSize   : number;

                if (fullCopy) {
                    dstSize   = bufferDataOffset + max(capacity, maxCapacity);
                    srcOffset = 0;
                    srcSize   = bufferSize;
                } else {
                    dstSize   = capacity;
                    srcOffset = bufferDataOffset;
                    srcSize   = bufferDataSize;

                    viewOffset = 0;
                }

                buffer = copyAnyArrayBuffer(buffer, 0, dstSize, srcOffset, srcSize, forceUnshare);
            }

            // zero bytes between bufferDataSize and size, if any
            if (zeroMemOnGrow) {
                const dirtOffset = viewOffset + bufferDataSize;
                const dirtSize   = size - bufferDataSize;

                if (dirtSize > 0) {
                    new U8A(buffer, dirtOffset, dirtSize).fill(0);
                }
            }
        } else {
            buffer = new ArrayBuffer(size);
        }

        const view = new DataView(buffer, viewOffset, capacity);

        return new BinBuffer({
            view,
            dataSize: size,
            autoCapacity,
            readOnly,
            bigEndian,
            intWriteMode,
            maxPageSize,
            zeroMemOnGrow,
            growSizeFn,
            fullCopy,
        }, BinBuffer._DEFAULT_STATE);
    };

    // SOME OPTIONS SETTERS/GETTERS
    // ----------------------------------

    private _autoCapacity : boolean;

    get autoCapacity () : boolean {
        this._ensureOpen();

        return this._autoCapacity;
    }

    set autoCapacity (value : boolean) {
        this._ensureOpen();

        if (!isBool(value)) {
            throw new BTError(`Expected type of argument is boolean, but ${ fmtType(value) } given`);
        }

        this._autoCapacity = value;
    }

    private _zeroMemOnGrow : boolean;

    get zeroMemOnGrow () : boolean {
        this._ensureOpen();

        return this._zeroMemOnGrow;
    }

    set zeroMemOnGrow (value : boolean) {
        this._ensureOpen();

        if (!isBool(value)) {
            throw new BTError(`Expected type of argument is boolean, but ${ fmtType(value) } given`);
        }

        this._zeroMemOnGrow = value;
    }

    private _readOnly : boolean;

    get readOnly () : boolean {
        this._ensureOpen();

        return this._readOnly;
    }

    set readOnly (value : boolean) {
        this._ensureOpen();

        if (!isBool(value)) {
            throw new BTError(`Expected type of argument is boolean, but ${ fmtType(value) } given`);
        }

        this._readOnly = value;
    }

    private _intWriteMode : EBBIntWriteMode;

    get intWriteMode () : EBBIntWriteMode {
        this._ensureOpen();

        return this._intWriteMode;
    }

    set intWriteMode (value : EBBIntWriteMode) {
        this._ensureOpen();

        if (!hasEnumIntValue(value, EBBIntWriteMode)) {
            throw new BTError(`Expected type of argument is EBBIntWriteMode, but ${ fmtType(value) } given`);
        }

        this._intWriteMode = value;
    }

    private _bigEndian : boolean;

    get bigEndian () : boolean {
        this._ensureOpen();

        return this._bigEndian;
    }

    set bigEndian (value : boolean) {
        this._ensureOpen();

        if (!isBool(value)) {
            throw new BTError(`Expected type of argument is boolean, but ${ fmtType(value) } given`);
        }

        this._bigEndian = value;
    }

    private _maxPageSize : number;

    get maxPageSize () : number {
        this._ensureOpen();

        return this._maxPageSize;
    }

    set maxPageSize (value : number) {
        this._ensureOpen();

        if (!isSafeInt(value) || value <= 0) {
            throw new BTError(`Expected type of argument is safe positive integer, but ${ fmtType(value) } given`);
        }

        this._maxPageSize = value;
    }

    private _growSizeFn : TBBGrowSizeFn | null = null;

    get growSizeFn () : TBBGrowSizeFn {
        this._ensureOpen();

        return this._growSizeFn;
    }

    set growSizeFn (value : TBBGrowSizeFn) {
        this._ensureOpen();

        if (!isFn(value)) {
            throw new BTError(`Expected type of argument is function, but ${ fmtType(value) } given`);
        }

        this._growSizeFn = value;
    }

    private _fullCopy : boolean | null = null;

    get fullCopy () : boolean {
        this._ensureOpen();

        return this._fullCopy;
    }

    set fullCopy (value : boolean) {
        this._ensureOpen();

        if (!isBool(value)) {
            throw new BTError(`Expected type of argument is boolean, but ${ fmtType(value) } given`);
        }

        this._fullCopy = value;
    }

    // INTERNAL PROPS SETTERS/GETTERS
    // ----------------------------------

    private _view        : DataView | null       = null;  // no public access
    private _bufferSize  : number | null         = null;  // no public access
    private _cursor      : number | null         = null;  // use this.tell() / this.seek()
    private _cursorStack : IBBCursorStack | null = null;  // use this.getCursorStack()
    private _cursorMap   : IBBCursorMap | null   = null;  // use this.getCursorMap()

    private _isShared : boolean | null = null;

    get isShared () : boolean {
        this._ensureOpen();

        return this._isShared;
    }

    private _lastReadSize : number | null = null;

    get lastReadSize () : number {
        this._ensureOpen();

        return this._lastReadSize;
    }

    private _lastWriteSize : number | null = null;

    get lastWriteSize () : number {
        this._ensureOpen();

        return this._lastWriteSize;
    }

    private _buffer : TAnyArrayBuffer | null = null;

    get internalBuffer () : TAnyArrayBuffer {
        this._ensureOpen();

        return this._buffer;
    }

    private _viewOffset : number | null = null;

    get internalOffset () : number {
        this._ensureOpen();

        return this._viewOffset;
    }

    private _viewSize : number | null = null;

    get capacity () : number {
        this._ensureOpen();

        return this._viewSize;
    }

    private _dataSize : number | null = null;

    get size () : number {
        this._ensureOpen();

        return this._dataSize;
    }

    private _isOpen : boolean | null = null;

    get isOpen () : boolean {
        return this._isOpen;
    }

    constructor (
        {
            view,
            dataSize,
            autoCapacity,
            readOnly,
            intWriteMode,
            bigEndian,
            maxPageSize,
            growSizeFn,
            zeroMemOnGrow,
            fullCopy,
        } : IBBInternalOptions,
        {
            cursor,
            cursorStack,
            cursorMap,
            lastReadSize,
            lastWriteSize,
        } : IBBInternalState
    ) {
        this._isOpen = true;

        this._view       = null;  // always projects onto the entire buffer or its acceptable part
        this._viewOffset = null;  // offset of this._view in this._buffer
        this._viewSize   = null;  // size of the entire buffer or its acceptable part (this.capacity)
        this._buffer     = null;  // underlying view buffer
        this._bufferSize = null;

        this._updateView(view);

        this._dataSize        = dataSize;  // size of buffer visible to end user (this.size)
        this._autoCapacity    = autoCapacity;
        this._readOnly        = readOnly;
        this._intWriteMode    = intWriteMode;
        this._bigEndian       = bigEndian;
        this._maxPageSize     = maxPageSize;
        this._zeroMemOnGrow   = zeroMemOnGrow;
        this._growSizeFn      = growSizeFn;
        this._fullCopy        = fullCopy;
        this._cursor          = cursor;
        this._cursorStack     = cursorStack;
        this._cursorMap       = cursorMap;
        this._lastReadSize    = lastReadSize;
        this._lastWriteSize   = lastWriteSize;
    }

    private _updateView = (view : DataView) : void => {
        this._view       = view;
        this._viewOffset = view.byteOffset;
        this._viewSize   = view.byteLength;
        this._buffer     = view.buffer;
        this._bufferSize = view.buffer.byteLength;
        this._isShared   = isSharedArrayBuffer(view.buffer);
    };

    private _reset = () : void => {
        this._autoCapacity  = null;
        this._zeroMemOnGrow = null;
        this._readOnly      = null;
        this._intWriteMode  = null;
        this._bigEndian     = null;
        this._maxPageSize   = null;
        this._growSizeFn    = null;
        this._fullCopy      = null;
        // ------------------------
        this._dataSize      = null;
        // ------------------------
        this._view          = null;
        this._viewOffset    = null;
        this._viewSize      = null;
        this._buffer        = null;
        this._bufferSize    = null;
        this._isShared      = null;
        // ------------------------
        this._cursor        = null;
        this._cursorStack   = null;
        this._cursorMap     = null;
        this._lastReadSize  = null;
        this._lastWriteSize = null;
    };

    close = () : void => {
        if (this._isOpen) {
            this._isOpen = false;
            this._reset();
        }
    };

    // INTERNAL DATA-SLICING/VIEWING METHODS
    // -----------------------------------------------------------------------------------------------------------------

    // buffer; copy; unshare/do-not-unshare
    private _sliceBuffer = <
        T extends boolean,
        R = T extends true ? ArrayBuffer : TAnyArrayBuffer
    > (
        offset       : number        = 0,
        size         : number | null = null,
        forceUnshare : T             = <T>false
    ) : R => {
        size ??= (this._bufferSize - offset);

        if (forceUnshare && this._isShared) {
            return <R>copyAnyArrayBuffer(this._buffer, 0, size, offset, size, forceUnshare);
        }

        return <R>sliceArrayBuffer(this._buffer, offset, offset + size);
    };

    // bytes; copy/no-copy; unshare/do-not-unshare
    private _chunkData = (
        offset       : number        = 0,
        size         : number | null = null,
        forceCopy    : boolean       = false,
        forceUnshare : boolean       = false
    ) : U8A => {
        offset += this._viewOffset;
        size ??= (this._dataSize - offset);

        const subBytes = new U8A(this._buffer, offset, size);

        if (forceCopy || forceUnshare && this._isShared) {
            const dstBytes = new U8A(size);

            dstBytes.set(subBytes);

            return dstBytes;
        }

        return subBytes;
    };

    // use this._sliceBuffer() instead if need to unshare
    private _copyDataAsBuffer = () : TAnyArrayBuffer => {
        return sliceArrayBuffer(this._buffer, this._viewOffset, this._viewOffset + this._dataSize);
    };

    private _copyDataAsView = () : DataView => {
        return new DataView(this._copyDataAsBuffer());
    };

    private _getBufferForBlob = () : ArrayBuffer => {
        let buffer : ArrayBuffer;

        if (this._isShared || this._isDataAPartOfBuffer()) {
            // Blob cannot be created from SharedArrayBuffer, so unshare it if it is so
            // buffer = this._sliceDataBuffer(0, this._dataSize, true);
            buffer = this._sliceBuffer(this._viewOffset, this._dataSize, true);
        } else {
            buffer = <ArrayBuffer>this._buffer;
        }

        return buffer;
    };

    private _isDataAPartOfBuffer = () : boolean => {
        return this._viewOffset > 0 || this._dataSize < this._bufferSize;
    };

    private _ensureOpen = () : void => {
        if (!this._isOpen) {
            throw new BTError('This instance is closed and can no longer be used');
        }
    };

    private _ensureWritable = () : void => {
        if (this._readOnly) {
            throw new BTError('Unable to write data in read-only mode');
        }
    };

    // SIZE MANIPULATION METHODS
    // -----------------------------------------------------------------------------------------------------------------

    // Auto: grow
    // User: shrink/grow
    private _resize = (
        newDataSize       : number,
        forceAutoCapacity : boolean,
        fill              : boolean | null = null,  // true - force do; false - force don't; null - auto
        fillByte          : number         = 0
    ) : void => {
        const curDataSize = this._dataSize;

        if (newDataSize === curDataSize) {
            return;
        }

        if (newDataSize < curDataSize) {
            this._dataSize = newDataSize;
            return;
        }

        // It is necessary to increase capacity or even internal buffer
        if (newDataSize > this._viewSize) {
            if (!forceAutoCapacity && !this._autoCapacity) {
                throw new BTError(`Auto capacity increase is not allowed, change 'autoCapacity' to true to allow it`);
            }

            const minBufferSize = this._viewOffset + newDataSize;
            const newBufferSize = this._growSizeFn.call(this, minBufferSize, this._maxPageSize, this);

            if (!isSafeInt(newBufferSize)) {
                throw new BTError(
                    `Expected type of value returned by growSizeFn is ` +
                    `safe integer, but ${ fmtType(newBufferSize) } returned`
                );
            }

            if (newBufferSize < minBufferSize) {
                throw new BTError(
                    `Value returned by growSizeFn (${ newBufferSize }) is ` +
                    `less than the minimum target size (${ minBufferSize })`
                );
            }

            this._resizeInternals(newBufferSize);
        }

        if (fill !== false && (fill === true || this._zeroMemOnGrow)) {
            const dirtSize = newDataSize - curDataSize;

            // use this._viewOffset directly, as it was updated
            this._fastFill(this._viewOffset + curDataSize, dirtSize, fillByte);
        }

        this._dataSize = newDataSize;
    };

    private _resizeInternals = (newBufferSize : number) : void => {
        const curViewOffset = this._viewOffset;
        const curBufferSize = this._bufferSize;
        const newViewSize   = newBufferSize - curViewOffset;

        // Resize (replace) internal ArrayBuffer
        if (newBufferSize > curBufferSize) {
            let newViewOffset = curViewOffset;
            let destSize      = newViewSize;
            let sourceOffset  = curViewOffset;
            let sourceSize    = this._dataSize;

            if (this._fullCopy) {
                newViewOffset = 0;
                destSize      = newBufferSize;
                sourceOffset  = 0;
                sourceSize    = curBufferSize;
            }

            const newBuffer = copyAnyArrayBuffer(this._buffer, 0, destSize, sourceOffset, sourceSize, false);

            this._updateView(new DataView(newBuffer, newViewOffset, newViewSize));

        // Resize view only
        } else if (newViewSize > this._viewSize) {
            this._updateView(new DataView(this._buffer, curViewOffset, newViewSize));
        }
    };

    reserve = (capacity : number, ensurePOT : boolean = false) : BinBuffer => {
        this._ensureOpen();
        this._ensureWritable();

        if (!isSafeInt(capacity) || capacity < 0) {
            throw new BTError(
                `Expected type of argument 'capacity' is safe ` +
                `non-negative integer, but ${ fmtType(capacity) } given`
            );
        }

        if (ensurePOT) {
            capacity = nextPOT(capacity);
        }

        if (capacity > this._viewSize) {
            const newBufferSize = this._viewOffset + capacity;

            this._resizeInternals(newBufferSize);
        }

        return this;
    };

    resize = (size : number) : BinBuffer => {
        this._ensureOpen();
        this._ensureWritable();

        if (size === this._dataSize) {
            return this;
        }

        if (!isSafeInt(size) || size < 0) {
            throw new BTError(
                `Expected type of argument 'size' is safe ` +
                `non-negative integer, but ${ fmtType(size) } given`
            );
        }

        this._resize(size, true, null);

        return this;
    };

    resizeBy = (sizeDelta : number) : BinBuffer => {
        this._ensureOpen();
        this._ensureWritable();

        if (sizeDelta === 0) {
            return this;
        }

        if (!isSafeInt(sizeDelta)) {
            throw new BTError(
                `Expected type of argument 'sizeDelta' is safe ` +
                `integer, but ${ fmtType(sizeDelta) } given`
            );
        }

        const newSize = this._dataSize + sizeDelta;

        if (newSize < 0) {
            throw new BTError(`Unable to resize buffer because calculated size is negative: ${ newSize }`);
        }

        this._resize(newSize, true, null);

        return this;
    };

    fit = (forceCopy : boolean = false) : BinBuffer => {
        this._ensureOpen();
        this._ensureWritable();

        if (forceCopy || this._isDataAPartOfBuffer()) {
            this._updateView(this._copyDataAsView());
        }

        return this;
    };

    // CLONE, TO*/AS* METHODS
    // -----------------------------------------------------------------------------------------------------------------

    private _clone = (
        updateOptions : Partial<IBBInternalOptions> | null,
        copyState     : boolean,
        cloneBuffer   : boolean
    ) : BinBuffer => {
        updateOptions ||= {};

        const currentOptions : IBBInternalOptions = {
            view:          cloneView(this._view, cloneBuffer),
            dataSize:      this._dataSize,
            autoCapacity:  this._autoCapacity,
            readOnly:      this._readOnly,
            bigEndian:     this._bigEndian,
            intWriteMode:  this._intWriteMode,
            maxPageSize:   this._maxPageSize,
            growSizeFn:    this._growSizeFn,
            zeroMemOnGrow: this._zeroMemOnGrow,
            fullCopy:      this._fullCopy,
        };

        const cloneOptions : IBBInternalOptions = Object.assign(currentOptions, updateOptions);

        let state : IBBInternalState;

        if (copyState) {
            state = {
                cursor:        this._cursor,
                cursorStack:   [ ...this._cursorStack ],
                cursorMap:     { ...this._cursorMap },
                lastReadSize:  this._lastReadSize,
                lastWriteSize: this._lastWriteSize,
            };
        } else {
            state = BinBuffer._DEFAULT_STATE;
        }

        return new BinBuffer(cloneOptions, state);
    };

    clone = (copyState : boolean = false, cloneBuffer : boolean = false) : BinBuffer => {
        this._ensureOpen();

        return this._clone(null, copyState, cloneBuffer);
    };

    private _createTypedArrayGetter = <T extends TTypedArray>(
        ctor       : TTypedArrayCtor,
        copyBuffer : boolean
    ) : (() => T) => {
        const itemSize = ctor.BYTES_PER_ELEMENT;

        return () : T => {
            this._ensureOpen();

            let buffer : TAnyArrayBuffer;
            let viewOffset : number;
            let dataSize : number;

            if (copyBuffer) {
                buffer     = this._copyDataAsBuffer();
                viewOffset = 0;
                dataSize   = buffer.byteLength;
            } else {
                buffer     = this._buffer;
                viewOffset = this._viewOffset;
                dataSize   = this._dataSize;
            }

            if (viewOffset % itemSize !== 0) {
                throw new BTError(
                    `Unable to create typed array because starting offset ` +
                    `is not a multiple of its element size (${ itemSize })`
                );
            }

            if (dataSize % itemSize !== 0) {
                throw new BTError(
                    `Unable to create typed array because binBuffer.size ` +
                    `is not a multiple of its element size (${ itemSize })`
                );
            }

            const itemCount = trunc(dataSize / itemSize);

            return <T>(new ctor(<ArrayBuffer>buffer, viewOffset, itemCount));
        };
    };

    asView = () : DataView => {
        this._ensureOpen();

        return new DataView(this._buffer, this._viewOffset, this._dataSize);
    };

    asI8A  = this._createTypedArrayGetter<I8A>(I8A, false);
    asU8A  = this._createTypedArrayGetter<U8A>(U8A, false);
    asU8CA = this._createTypedArrayGetter<U8CA>(U8CA, false);
    asI16A = this._createTypedArrayGetter<I16A>(I16A, false);
    asU16A = this._createTypedArrayGetter<U16A>(U16A, false);
    asI32A = this._createTypedArrayGetter<I32A>(I32A, false);
    asU32A = this._createTypedArrayGetter<U32A>(U32A, false);
    asI64A = this._createTypedArrayGetter<I64A>(I64A, false);
    asU64A = this._createTypedArrayGetter<U64A>(U64A, false);
    asF32A = this._createTypedArrayGetter<F32A>(F32A, false);
    asF64A = this._createTypedArrayGetter<F64A>(F64A, false);

    toView = () : DataView => {
        this._ensureOpen();

        return this._copyDataAsView();
    };

    toI8A  = this._createTypedArrayGetter<I8A>(I8A, true);
    toU8A  = this._createTypedArrayGetter<U8A>(U8A, true);
    toU8CA = this._createTypedArrayGetter<U8CA>(U8CA, true);
    toI16A = this._createTypedArrayGetter<I16A>(I16A, true);
    toU16A = this._createTypedArrayGetter<U16A>(U16A, true);
    toI32A = this._createTypedArrayGetter<I32A>(I32A, true);
    toU32A = this._createTypedArrayGetter<U32A>(U32A, true);
    toI64A = this._createTypedArrayGetter<I64A>(I64A, true);
    toU64A = this._createTypedArrayGetter<U64A>(U64A, true);
    toF32A = this._createTypedArrayGetter<F32A>(F32A, true);
    toF64A = this._createTypedArrayGetter<F64A>(F64A, true);

    toHex = (upperCase : boolean = false, sep : string = '') : string => {
        this._ensureOpen();

        return _binToHex(this._chunkData(), upperCase, sep);
    };

    toDataURL = (mimeType : string = 'text/plain') : TBase64DataURL => {
        this._ensureOpen();

        return _binToDataUrl(this._chunkData(), mimeType);
    };

    toBlob = (options? : BlobPropertyBag) : Blob => {
        this._ensureOpen();

        return new Blob([ this._getBufferForBlob() ], options);
    };

    toFile = (fileName : string, options? : FilePropertyBag) : File => {
        this._ensureOpen();

        return new File([ this._getBufferForBlob() ], fileName, options);
    };

    // static toString = () : string => {
    //     return 'BinBuffer';
    // }

    // toString = () : string => {
    //     if (this._isOpen) {
    //         return (
    //             `BinBuffer(isOpen=true, size=${ this._dataSize }, capacity=${ this._viewSize }, ` +
    //             `cursor=${ this._cursor }, internalOffset=${ this._viewOffset })`
    //         );
    //     }
    //
    //     return `BinBuffer(isOpen=false)`;
    // }

    // use this.asU8A() if no copy needed
    getData = () : U8A => {
        this._ensureOpen();

        return this._chunkData(0, null, true, true);
    };

    detachInternalView = () : DataView => {
        this._ensureOpen();

        const view = this._view;

        this.close();

        return view;
    };

    detachInternalBuffer = () : TAnyArrayBuffer => {
        this._ensureOpen();

        const buffer = this._buffer;

        this.close();

        return buffer;
    };

    download = (fileName? : string | null, mimeType? : string | null) : BinBuffer => {
        this._ensureOpen();

        if (!isBrowser) {
            throw new BTError('This environment does not support file downloads');
        }

        if (isNone(fileName)) {
            fileName = '';
        } else if (!isStr(fileName)) {
            throw new BTError(
                `Expected type of argument 'fileName' is string ` +
                `or null, but ${ fmtType(fileName) } given`
            );
        }

        let blobOptions : BlobPropertyBag = {};

        if (isStr(mimeType)) {
            blobOptions.type = mimeType;
        } else if (!isNone(mimeType)) {
            throw new BTError(
                `Expected type of argument 'mimeType' is string ` +
                `or null, but ${ fmtType(mimeType) } given`
            );
        }

        const blob = this.toBlob(blobOptions);

        const url = window.URL.createObjectURL(blob);

        const linkEl = document.createElement('a');

        linkEl.style.display = 'none';
        linkEl.href = url;
        linkEl.download = fileName;

        document.body.appendChild(linkEl);

        linkEl.click();

        setTimeout(() => {
            linkEl.remove();
            window.URL.revokeObjectURL(url);
        }, 2000);

        return this;
    };

    // CURSOR POSITIONING METHODS
    // -----------------------------------------------------------------------------------------------------------------

    private _seekGrow = (newCursor : number) : void => {
        this._ensureWritable();

        if (newCursor > this._dataSize) {
            this._resize(newCursor, true, true);
        }
    };

    private _remainder = () : number => {
        return max(0, this._dataSize - this._cursor);
    };

    get remainder () : number {
        this._ensureOpen();

        return this._remainder();
    };

    get isEnd () : boolean {
        this._ensureOpen();

        return this._remainder() === 0;
    };

    get cursor () : number {
        this._ensureOpen();

        return this._cursor;
    };

    skip = (size : number) : number => {
        this._ensureOpen();

        if (size === 0) {
            return this._cursor;
        }

        if (!isSafeInt(size) || size < 0) {
            throw new BTError(
                `Expected type of argument 'size' is safe ` +
                `non-negative integer, but ${ fmtType(size) } given`
            );
        }

        this._cursor += size;

        return this._cursor;
    };

    seek = (
        offset    : number,
        from      : EBBSeekFrom   = EBBSeekFrom.Start,
        forceGrow : boolean       = false,
    ) : number => {
        this._ensureOpen();

        if (!isSafeInt(offset)) {
            throw new BTError(`Expected type of argument 'offset' is safe integer, but ${ fmtType(offset) } given`);
        }

        let newCursor : number;

        switch (from) {
            case EBBSeekFrom.Start: {
                newCursor = offset;
                break;
            }
            case EBBSeekFrom.Here: {
                newCursor = this._cursor + offset;
                break;
            }
            case EBBSeekFrom.End: {
                newCursor = this._dataSize + offset;
                break;
            }
            default: {
                throw new BTError(`Expected type of argument 'from' is EBBSeekFrom, but ${ fmtType(from) } given`);
            }
        }

        if (newCursor < 0) {
            throw new BTError(`Unable to seek because calculated offset is negative: ${ newCursor }`);
        }

        if (forceGrow) {
            this._seekGrow(newCursor);
        }

        return (this._cursor = newCursor);
    };

    seekFromStart = (offset : number, forceGrow : boolean = false) : number => {
        // this._ensureOpen is called in this.seek
        return this.seek(offset, EBBSeekFrom.Start, forceGrow);
    };

    seekFromHere = (offset : number, forceGrow : boolean = false) : number => {
        // this._ensureOpen is called in this.seek
        return this.seek(offset, EBBSeekFrom.Here, forceGrow);
    };

    seekFromEnd = (offset : number, forceGrow : boolean = false) : number => {
        // this._ensureOpen is called in this.seek
        return this.seek(offset, EBBSeekFrom.End, forceGrow);
    };

    align = (bound : number, forceGrow : boolean = false) : number => {
        this._ensureOpen();

        if (!isSafeInt(bound) || bound <= 0) {
            throw new BTError(
                `Expected type of argument 'bound' is safe ` +
                `positive integer, but ${ fmtType(bound) } given`
            );
        }

        const newCursor = ceil(this._cursor / bound) * bound;

        if (forceGrow) {
            this._seekGrow(newCursor);
        }

        this._cursor = newCursor;

        return this._cursor;
    };

    // CURSOR STACK
    // -----------------------------------------------------------------------------------------------------------------

    pushCursor = () : number => {
        this._ensureOpen();

        this._cursorStack.push(this._cursor);

        return this._cursor;
    };

    popCursor = (applyCursor : boolean = true) : number => {
        this._ensureOpen();

        if (!this._cursorStack.length) {
            throw new BTError('Failed to pop cursor because there are no available cursors on the stack');
        }

        const cursor = this._cursorStack.pop();

        if (applyCursor) {
            this._cursor = cursor;
        }

        return cursor;
    };

    getCursorStack = (reverse : boolean = false) : number[] => {
        this._ensureOpen();

        const cursors = [ ...this._cursorStack ];

        if (reverse) {
            cursors.reverse();
        }

        return cursors;
    };

    ejectCursorStack = (reverse : boolean = false) : number[] => {
        this._ensureOpen();

        const cursors = [ ...this._cursorStack ];

        if (reverse) {
            cursors.reverse();
        }

        this._cursorStack = [];

        return cursors;
    };

    // CURSOR MAP
    // -----------------------------------------------------------------------------------------------------------------

    setCursorName = (name : string) : number => {
        this._ensureOpen();

        if (!isStr(name) || !name.length) {
            throw new BTError(`Expected type of argument 'name' is string, but ${ fmtType(name) } given`);
        }

        return (this._cursorMap[name] = this._cursor);
    };

    getNamedCursor = (name : string) : number | null => {
        this._ensureOpen();

        if (!isStr(name) || !name.length) {
            throw new BTError(`Expected type of argument 'name' is string, but ${ fmtType(name) } given`);
        }

        return this._cursorMap[name] ?? null;
    };

    applyNamedCursor = (name : string) : number | null => {
        // this._ensureOpen() called in this.getNamedCursor()
        const cursor = this.getNamedCursor(name);

        if (cursor === null) {
            throw new BTError(`Cursor with name "${ name }" is not found`);
        }

        this._cursor = cursor;

        return cursor;
    };

    getCursorMap = () : IBBCursorMap => {
        this._ensureOpen();

        return { ...this._cursorMap };
    };

    ejectCursorMap = () : IBBCursorMap => {
        this._ensureOpen();

        const cursors = { ...this._cursorMap };

        this._cursorMap = {};

        return cursors;
    };

    // DATA MUTATION METHODS
    // -----------------------------------------------------------------------------------------------------------------

    private _fastFill = (offset : number, size : number, byte : number) : void => {
        if (size > 0) {
            new U8A(this._buffer, offset, size).fill(byte);
        }
    };

    private _getFillParams = (
        mod        : number | TAnyBin,
        offset     : number,
        size       : number | null,
        modArgName : string
    ) : [ TBytes, number, TBytes, number ] | null => {
        const dataSize = this._dataSize;

        if (!isSafeInt(offset) || offset < 0) {
            throw new BTError(
                `Expected type of argument 'offset' is safe ` +
                `non-negative integer, but ${ fmtType(offset) } given`
            );
        }

        if (offset > dataSize) {
            throw new BTError(`Argument 'offset' (${ offset }) exceeds the buffer size`);
        }

        if (isNone(size)) {
            size = dataSize - offset;
        } else if (!isSafeInt(size) || size < 0) {
            throw new BTError(
                `Expected type of argument 'size' is safe ` +
                `non-negative integer or null, but ${ fmtType(size) } given`
            );
        }

        if (size === 0) {
            return null;
        }

        if ((offset + size) > dataSize) {
            throw new BTError(`Sum of the 'offset' and 'size' arguments exceeds the buffer size`);
        }

        if (isByteInt(mod)) {
            mod = new U8A([ mod ]);
        } else if (isAnyBin(mod) && mod.byteLength > 0) {
            mod = asBytes(mod);
        } else {
            throw new BTError(
                `Expected type of argument '${ modArgName }' is non-empty ${ ANY_BIN_TYPE } ` +
                `or integer in range [0, 255], but ${ fmtType(mod) } given`
            );
        }

        const bytes      = this._chunkData(offset, size);
        const byteCount  = bytes.byteLength;
        const fillerSize = mod.length;

        return [ bytes, byteCount, mod, fillerSize ];
    };

    fill = (filler : number | TAnyBin, offset : number = 0, size : number | null = null) : BinBuffer => {
        this._ensureOpen();
        this._ensureWritable();

        const params = this._getFillParams(filler, offset, size, 'filler');

        if (params !== null) {
            const [ targetBytes, targetSize, modBytes, modSize ] = params;

            if (modSize === 1) {
                targetBytes.fill(modBytes[0]);
            } else {
                for (let i = 0; i <= targetSize; ++i) {
                    targetBytes[i] = modBytes[i % modSize];
                }
            }
        }

        return this;
    };

    xor = (key : number | TAnyBin, offset : number = 0, size : number | null = null) : BinBuffer => {
        this._ensureOpen();
        this._ensureWritable();

        const params = this._getFillParams(key, offset, size, 'key');

        if (params !== null) {
            const [ targetBytes, targetSize, modBytes, modSize ] = params;

            for (let i = 0; i <= targetSize; ++i) {
                targetBytes[i] ^= modBytes[i % modSize];
            }
        }

        return this;
    };

    clear = (withCapacity : boolean = false) : BinBuffer => {
        this._ensureOpen();
        this._ensureWritable();

        const clearSize = withCapacity ? this._viewSize : this._dataSize;

        this._fastFill(this._viewOffset, clearSize, 0);

        return this;
    };

    unshare = () : BinBuffer => {
        this._ensureOpen();
        this._ensureWritable();

        if (this._isShared) {
            let newViewOffset : number;
            let size : number;
            let sourceOffset : number;

            if (this._fullCopy) {
                sourceOffset  = 0;
                size          = this._bufferSize;
                newViewOffset = this._viewOffset;
            } else {
                sourceOffset  = this._viewOffset;
                size          = this._viewSize;
                newViewOffset = 0;
            }

            const newBuffer = this._sliceBuffer(sourceOffset, size, true);
            const newView   = new DataView(newBuffer, newViewOffset, this._viewSize);

            this._updateView(newView);
        }

        return this;
    };

    // RAW BYTES PEEK/READ METHODS
    // -----------------------------------------------------------------------------------------------------------------

    private _createReadFn = (advanceCursor : boolean) : ((size : number) => U8A) => {
        return (size : number) : U8A => {
            this._ensureOpen();

            if (size === 0) {
                if (advanceCursor) {
                    this._lastReadSize = 0;
                }

                return new U8A(0);
            }

            if (!isSafeInt(size) || size < 0) {
                throw new BTError(
                    `Expected type of 'size' is safe non-negative ` +
                    `integer, but ${ fmtType(size) } given`
                );
            }

            if (this._remainder() < size) {
                throw new BTError(`Unable to read ${ size } bytes because there is not enough data in buffer`);
            }

            // const buffer = copyAnyArrayBuffer(this._buffer, 0, size, this._viewOffset + this._cursor, size, true);
            const bytes = this._chunkData(this._cursor, size, true, true);

            if (advanceCursor) {
                this._lastReadSize = size;
                this._cursor += size;
            }

            return bytes;
        };
    };

    read = this._createReadFn(true);
    peek = this._createReadFn(false);

    // TYPED NUMBERS PEEK/READ METHODS
    // -----------------------------------------------------------------------------------------------------------------

    private _ensureNumReadSize = (size : number, typeName : string) : void => {
        if (this._remainder() < size) {
            throw new BTError(
                `Unable to read ${ typeName } of size ${ size } ` +
                `because there is not enough data in buffer`
            );
        }
    };

    private _createNumReadFn = <T extends number | bigint>(
        readFn        : TDataViewGetFn<T>,
        typeSize      : number,
        typeName      : string,
        advanceCursor : boolean
    ) : ((bigEndian? : boolean | null) => T) => {
        return (bigEndian : boolean | null = null) : T => {
            this._ensureOpen();
            this._ensureNumReadSize(typeSize, typeName);

            bigEndian ??= this._bigEndian;

            const value = readFn.call(this._view, this._cursor, !bigEndian);

            if (advanceCursor) {
                this._lastReadSize = typeSize;
                this._cursor += typeSize;
            }

            return <T>value;
        };
    };

    private _createBIReadFn = (
        isSigned      : boolean,
        advanceCursor : boolean
    ) : ((size : number, bigEndian? : boolean | null) => bigint) => {
        return (size : number, bigEndian : boolean | null = null) : bigint => {
            this._ensureOpen();
            this._ensureNumReadSize(size, 'BigInt');

            bigEndian ??= this._bigEndian;

            // copy is not necessary
            const bytes = this._chunkData(this._cursor, size);
            const value = binToBigInt(bytes, isSigned, bigEndian);

            if (advanceCursor) {
                this._lastReadSize = size;
                this._cursor += size;
            }

            return value;
        };
    };

    readBI  = this._createBIReadFn(true, true);
    readUBI = this._createBIReadFn(false, true);
    readI8  = this._createNumReadFn<number>(DataView.prototype.getInt8,      1, 'i8',  true);
    readU8  = this._createNumReadFn<number>(DataView.prototype.getUint8,     1, 'u8',  true);
    readI16 = this._createNumReadFn<number>(DataView.prototype.getInt16,     2, 'i16', true);
    readU16 = this._createNumReadFn<number>(DataView.prototype.getUint16,    2, 'u16', true);
    readI32 = this._createNumReadFn<number>(DataView.prototype.getInt32,     4, 'i32', true);
    readU32 = this._createNumReadFn<number>(DataView.prototype.getUint32,    4, 'u32', true);
    readI64 = this._createNumReadFn<bigint>(DataView.prototype.getBigInt64,  8, 'i64', true);
    readU64 = this._createNumReadFn<bigint>(DataView.prototype.getBigUint64, 8, 'u64', true);
    // readF16 = this._createNumReadFn<number>(DataView.prototype.getFloat16,   2, 'f16', true);  // add support later
    readF32 = this._createNumReadFn<number>(DataView.prototype.getFloat32,   4, 'f32', true);
    readF64 = this._createNumReadFn<number>(DataView.prototype.getFloat64,   8, 'f64', true);

    peekBI  = this._createBIReadFn(true, false);
    peekUBI = this._createBIReadFn(false, false);
    peekI8  = this._createNumReadFn<number>(DataView.prototype.getInt8,      1, 'i8',  false);
    peekU8  = this._createNumReadFn<number>(DataView.prototype.getUint8,     1, 'u8',  false);
    peekI16 = this._createNumReadFn<number>(DataView.prototype.getInt16,     2, 'i16', false);
    peekU16 = this._createNumReadFn<number>(DataView.prototype.getUint16,    2, 'u16', false);
    peekI32 = this._createNumReadFn<number>(DataView.prototype.getInt32,     4, 'i32', false);
    peekU32 = this._createNumReadFn<number>(DataView.prototype.getUint32,    4, 'u32', false);
    peekI64 = this._createNumReadFn<bigint>(DataView.prototype.getBigInt64,  8, 'i64', false);
    peekU64 = this._createNumReadFn<bigint>(DataView.prototype.getBigUint64, 8, 'u64', false);
    // peekF16 = this._createNumReadFn<number>(DataView.prototype.getFloat16,   2, 'f16', false);  // add support later
    peekF32 = this._createNumReadFn<number>(DataView.prototype.getFloat32,   4, 'f32', false);
    peekF64 = this._createNumReadFn<number>(DataView.prototype.getFloat64,   8, 'f64', false);

    // TYPED ARRAY PEEK/READ METHODS
    // -----------------------------------------------------------------------------------------------------------------

    private _ensureArrayReadSize = (totalSize : number, count : number, typeName : string | null = null) : void => {
        if (this._remainder() < totalSize) {
            throw new BTError(
                `Unable to read ${ typeName }(${ count }) of total size ` +
                `${ totalSize } byte(s) because buffer does not have enough data`
            );
        }
    };

    private _createArrayReadFn = <T extends TTypedArray>(
        arrCtor       : TTypedArrayCtor,
        typeSize      : number,
        advanceCursor : boolean
    ) : ((count : number) => T) => {
        return (count : number) : T => {
            this._ensureOpen();

            if (count === 0) {
                if (advanceCursor) {
                    this._lastReadSize = 0;
                }

                return <T>new arrCtor(0);
            }

            if (!isSafeInt(count) || count < 0) {
                throw new BTError(
                    `Expected type of 'count' is safe non-negative ` +
                    `integer, but ${ fmtType(count) } given`
                );
            }

            const totalSize = typeSize * count;

            this._ensureArrayReadSize(totalSize, count, arrCtor.name);

            const buffer = this._sliceBuffer(this._viewOffset + this._cursor, totalSize, true);

            if (advanceCursor) {
                this._lastReadSize = totalSize;
                this._cursor += totalSize;
            }

            return <T>new arrCtor(buffer);
        };
    };

    peekI8A  = this._createArrayReadFn<I8A> (I8A,  1, false);
    peekU8A  = this._createArrayReadFn<U8A> (U8A,  1, false);
    peekU8CA = this._createArrayReadFn<U8CA>(U8CA, 1, false);
    peekI16A = this._createArrayReadFn<I16A>(I16A, 2, false);
    peekU16A = this._createArrayReadFn<U16A>(U16A, 2, false);
    peekI32A = this._createArrayReadFn<I32A>(I32A, 4, false);
    peekU32A = this._createArrayReadFn<U32A>(U32A, 4, false);
    peekI64A = this._createArrayReadFn<I64A>(I64A, 8, false);
    peekU64A = this._createArrayReadFn<U64A>(U64A, 8, false);
    peekF32A = this._createArrayReadFn<F32A>(F32A, 4, false);
    peekF64A = this._createArrayReadFn<F64A>(F64A, 8, false);

    readI8A  = this._createArrayReadFn<I8A> (I8A,  1, true);
    readU8A  = this._createArrayReadFn<U8A> (U8A,  1, true);
    readU8CA = this._createArrayReadFn<U8CA>(U8CA, 1, true);
    readI16A = this._createArrayReadFn<I16A>(I16A, 2, true);
    readU16A = this._createArrayReadFn<U16A>(U16A, 2, true);
    readI32A = this._createArrayReadFn<I32A>(I32A, 4, true);
    readU32A = this._createArrayReadFn<U32A>(U32A, 4, true);
    readI64A = this._createArrayReadFn<I64A>(I64A, 8, true);
    readU64A = this._createArrayReadFn<U64A>(U64A, 8, true);
    readF32A = this._createArrayReadFn<F32A>(F32A, 4, true);
    readF64A = this._createArrayReadFn<F64A>(F64A, 8, true);

    // STRING/BUFFER PEEK/READ METHODS
    // -----------------------------------------------------------------------------------------------------------------

    private _getEncodingInfo = (
        encoding     : string,
        checkDecoder : boolean,
        checkEncoder : boolean
    ) : IEncodingInfoItem => {
        const info = getEncodingInfo(encoding);

        if (!info) {
            throw new BTError(`Encoding "${ encoding }" is not supported`);
        }

        if (checkDecoder && !info.decodeFactory) {
            throw new BTError(`Encoding "${ encoding }" does not support text decoding`);
        }

        if (checkEncoder && !info.encodeFactory) {
            throw new BTError(`Encoding "${ encoding }" does not support text encoding`);
        }

        return info;
    };

    private _readZStrBuffer = (
        size         : number | null,
        encoding     : string,
        checkDecoder : boolean
    ) : [ number | null, number | null, number | null, TDecodeFactory | null ] => {
        const remainderSize = this._remainder();

        if (isNone(size)) {
            size = null;
        } else if (!isSafeInt(size) || size < 0) {
            throw new BTError(
                `Expected type of 'size' is safe non-negative ` +
                `integer, but ${ fmtType(size) } given`
            );
        } else if (size > remainderSize) {
            throw new BTError(
                `Unable to read ${ size }-byte string ` +
                `because there is not enough data in the buffer`
            );
        }

        if (size === 0) {
            return [ this._cursor, null, null, null ];
        }

        const { charSize, readCharFn, decodeFactory } = this._getEncodingInfo(encoding, checkDecoder, false);

        // what if maxSize % charSize != 0 for wide character string (utf-16/32)?
        const startOffset  = this._cursor;
        const maxSize      = size ?? remainderSize;  // always: size === null || size <= remainderSize
        const maxCharCount = trunc(maxSize / charSize);

        let endOffset = startOffset;
        let strCursor = startOffset;

        for (let i = 0; i < maxCharCount; ++i) {
            // Byte order doesn't matter here
            const charCode = readCharFn.call(this._view, strCursor);

            strCursor += charSize;

            if (charCode === 0) {
                break;
            }

            endOffset += charSize;
        }

        const strSize   = endOffset - startOffset;
        const newCursor = size === null ? strCursor : (startOffset + maxSize);

        return [ newCursor, startOffset, strSize, decodeFactory ];
    };

    readZStr = (
        size      : number | null = null,
        encoding  : string        = 'utf-8',
        isStrict  : boolean       = false,
        ignoreBOM : boolean       = false
    ) : string => {
        this._ensureOpen();

        const [ newCursor, strOffset, strSize, decodeFactory ] = this._readZStrBuffer(size, encoding, true);

        let result : string = '';

        if (strOffset !== null && strSize) {
            const decode = decodeFactory(isStrict, ignoreBOM);

            result = decode(this._chunkData(strOffset, strSize, false, true));
        }

        this._lastReadSize = newCursor - this._cursor;
        this._cursor = newCursor;

        return result;
    };

    readZStrBytes = (size : number | null = null, encoding : string = 'utf-8') : U8A => {
        this._ensureOpen();

        const [ newCursor, strOffset, strSize ] = this._readZStrBuffer(size, encoding, false);

        let result : U8A;

        if (strOffset !== null && strSize) {
            result = this._chunkData(strOffset, strSize, true, true);
        } else {
            result = new U8A(0);
        }

        this._lastReadSize = newCursor - this._cursor;
        this._cursor = newCursor;

        return result;
    };

    peekZStr = (
        size      : number | null = null,
        encoding  : string        = 'utf-8',
        isStrict  : boolean       = false,
        ignoreBOM : boolean       = false
    ) : string => {
        this._ensureOpen();

        const [ _, strOffset, strSize, decodeFactory ] = this._readZStrBuffer(size, encoding, true);

        if (strOffset === null || !strSize) {
            return '';
        }

        const decode = decodeFactory(isStrict, ignoreBOM);

        return decode(this._chunkData(strOffset, strSize, false, true));
    };

    peekZStrBytes = (size : number | null = null, encoding : string = 'utf-8') : U8A => {
        this._ensureOpen();

        const [ _, strOffset, strSize ] = this._readZStrBuffer(size, encoding, false);

        if (strOffset === null || !strSize) {
            return new U8A(0);
        }

        return this._chunkData(strOffset, strSize, true, true);
    };

    private _readStrBuffer = (size : number) : [ ArrayBuffer, number ] => {
        if (!isSafeInt(size) || size < 0) {
            throw new BTError(
                `Expected type of 'size' is safe non-negative ` +
                `integer, but ${ fmtType(size) } given`
            );
        }

        if (this._remainder() < size) {
            throw new BTError(
                `Unable to read ${ size }-byte string ` +
                `because there is not enough data in the buffer`
            );
        }

        if (size === 0) {
            return [ new ArrayBuffer(0), this._cursor ];
        }

        const strOffset = this._viewOffset + this._cursor;
        const buffer    = this._sliceBuffer(strOffset, size, true);
        const newCursor = strOffset + size;

        return [ buffer, newCursor ];
    };

    readStr = (
        size      : number,
        encoding  : string  = 'utf-8',
        isStrict  : boolean = false,
        ignoreBOM : boolean = false
    ) : string => {
        this._ensureOpen();

        const [ buffer, newCursor ] = this._readStrBuffer(size);

        const result = this._getEncodingInfo(encoding, false, true).decodeFactory(isStrict, ignoreBOM)(buffer);

        this._lastReadSize = newCursor - this._cursor;
        this._cursor = newCursor;

        return result
    };

    readStrBytes = (size : number) : U8A => {
        this._ensureOpen();

        const [ buffer, newCursor ] = this._readStrBuffer(size);

        this._lastReadSize = newCursor - this._cursor;
        this._cursor = newCursor;

        return new U8A(buffer);
    };

    peekStr = (
        size      : number,
        encoding  : string  = 'utf-8',
        isStrict  : boolean = false,
        ignoreBOM : boolean = false
    ) : string => {
        this._ensureOpen();

        const [ buffer ] = this._readStrBuffer(size);

        return this._getEncodingInfo(encoding, false, true).decodeFactory(isStrict, ignoreBOM)(buffer);
    };

    peekStrBytes = (size : number) : U8A => {
        // this._ensureOpen() called in this._readStrBuffer()
        return new U8A(this._readStrBuffer(size)[0]);
    };

    // BYTES WRITE METHODS
    // -----------------------------------------------------------------------------------------------------------------

    private _ensureEnoughSpace = (sizeToWrite : number, fillByte : number = 0) : void => {
        // If the cursor extends beyond the size of the visible data buffer,
        // [this._cursor - this._dataSize] must first be filled with null bytes.
        const cursor      = this._cursor;
        const dataSize    = this._dataSize;
        const minDataSize = cursor + sizeToWrite;

        // Resize without fill
        if (minDataSize > dataSize) {
            this._resize(minDataSize, false, false);
        }

        if (cursor > dataSize) {
            const offset = this._viewOffset + dataSize;
            const size   = cursor - dataSize;

            this._fastFill(offset, size, fillByte);
        }
    };

    private _copyToView = (cursor : number, bytes : TBytes, sizeLimit : number = Infinity) : void => {
        const size = min(bytes.byteLength, sizeLimit);

        for (let i = 0; i < size; ++i) {
            this._view.setUint8(cursor + i, bytes[i]);
        }
    };

    private _write = (data : TBytes) : number => {
        const size = data.byteLength;

        if (size === 0) {
            return (this._lastWriteSize = 0);
        }

        this._ensureEnoughSpace(size);

        this._copyToView(this._cursor, data);

        this._cursor += size;

        return (this._lastWriteSize = size);
    };

    write = (data : TAnyBin) : number => {
        this._ensureOpen();
        this._ensureWritable();

        if (isAnyBin(data)) {
            data = asBytes(data);
        } else {
            throw new BTError(`Expected type of 'data' is ${ ANY_BIN_TYPE }, but ${ fmtType(data) } given`);
        }

        return this._write(data);
    };

    private _createNumWriteFn = <T extends number | bigint>(
        writeFn  : TDataViewSetFn<T>,
        typeSize : number,
        castFns  : ((num : T) => T)[] | null = null
    ) : ((value : T, bigEndian? : boolean | null) => number) => {
        return (value : T, bigEndian : boolean | null = null) : number => {
            this._ensureOpen();
            this._ensureWritable();
            this._ensureEnoughSpace(typeSize);

            if (castFns) {
                value = castFns[this.intWriteMode](value);
            }

            bigEndian ??= this._bigEndian;

            writeFn.call(this._view, this._cursor, value, !bigEndian)

            this._cursor += typeSize;

            return (this._lastWriteSize = typeSize);
        };
    };

    writeI8  = this._createNumWriteFn<number>(DataView.prototype.setInt8,      1, [ i8,  i8c,  i8s  ]);
    writeU8  = this._createNumWriteFn<number>(DataView.prototype.setUint8,     1, [ u8,  u8c,  u8s  ]);
    writeI16 = this._createNumWriteFn<number>(DataView.prototype.setInt16,     2, [ i16, i16c, i16s ]);
    writeU16 = this._createNumWriteFn<number>(DataView.prototype.setUint16,    2, [ u16, u16c, u16s ]);
    writeI32 = this._createNumWriteFn<number>(DataView.prototype.setInt32,     4, [ i32, i32c, i32s ]);
    writeU32 = this._createNumWriteFn<number>(DataView.prototype.setUint32,    4, [ u32, u32c, u32s ]);
    writeI64 = this._createNumWriteFn<bigint>(DataView.prototype.setBigInt64,  8, [ i64, i64c, i64s ]);
    writeU64 = this._createNumWriteFn<bigint>(DataView.prototype.setBigUint64, 8, [ u64, u64c, u64s ]);
    // writeF16 = this._createNumWriteFn<number>(DataView.prototype.setFloat16,   2);  // add support later
    writeF32 = this._createNumWriteFn<number>(DataView.prototype.setFloat32,   4);
    writeF64 = this._createNumWriteFn<number>(DataView.prototype.setFloat64,   8);

    writeBI = (num : bigint, size : number | null = null, bigEndian : boolean | null = null) : number => {
        bigEndian ??= this._bigEndian;

        return this._write(bigIntToBin(num, size, bigEndian))
    };

    writeStr = (
        str       : string,
        encoding  : string        = 'utf-8',
        terminate : boolean       = false,
        size      : number | null = null,
        withBOM   : boolean       = false,
        bound     : number | null = null,
        padByte   : number        = 0
    ) : number => {
        this._ensureOpen();
        this._ensureWritable();

        if (!isStr(str)) {
            throw new BTError(`Expected type of 'str' is string, but ${ fmtType(str) } given`);
        }

        if (!isBool(terminate)) {
            throw new BTError(`Expected type of 'terminate' is boolean, but ${ fmtType(terminate) } given`);
        }

        if (isNone(size)) {
            size = null;
        } else if (!isSafeInt(size) || size < 0) {
            throw new BTError(`Expected type of 'size' is safe non-negative integer or null, but ${ fmtType(size) } given`);
        }

        if (isNone(bound)) {
            bound = 1;
        } else if (!isSafeInt(bound) || bound <= 0) {
            throw new BTError(`Expected type of 'bound' is safe positive integer, but ${ fmtType(bound) } given`);
        }

        if (size !== null && bound !== 1) {
            throw new BTError(`Arguments 'size' and 'bound' are mutually exclusive`);
        }

        if (!str.length && !terminate || size === 0) {
            return (this._lastWriteSize = 0);
        }

        const { encodeFactory, charSize } = this._getEncodingInfo(encoding, false, true);

        // strByteCount <= terminatedSize <= paddedSize <= finalSize
        const strBytes       = encodeFactory()(str, withBOM);
        const strByteCount   = strBytes.byteLength;
        let   termSize       = terminate ? charSize : 0;
        const terminatedSize = strByteCount + termSize;
        const paddedSize     = ceil(terminatedSize / bound) * bound;
        const finalSize      = size ?? paddedSize;

        this._ensureEnoughSpace(finalSize);

        let cursor = this._cursor;

        this._copyToView(cursor, strBytes, finalSize);

        if (strByteCount < finalSize) {
            const viewOffset = this._viewOffset;

            cursor += strByteCount;

            termSize = min(finalSize - strByteCount, termSize);

            if (termSize > 0) {
                this._fastFill(viewOffset + cursor, termSize, 0);
            }

            cursor += termSize;

            const paddingSize = finalSize - strByteCount - termSize;

            if (paddingSize > 0) {
                this._fastFill(viewOffset + cursor, paddingSize, padByte);
            }
        }

        this._cursor += finalSize;

        return (this._lastWriteSize = finalSize);
    };
}
