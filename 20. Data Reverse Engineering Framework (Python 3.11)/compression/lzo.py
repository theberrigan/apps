import os
import sys
import struct

from math import ceil

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..'))) 

from bfw.utils import *
from bfw.reader import *
from bfw.writer import *
from bfw.native.base import *
from bfw.native.limits import *



LZO_DLL_PATH = joinPath(BIN_DIR, 'lzo2.dll')

# TODO: import from dll
LZO1X_1_MEM_COMPRESS   = 16384 * PTR64_BYTES
LZO1X_999_MEM_COMPRESS = 14 * 16384 * I16_BYTES

LZO_E_OK = 0



class LZO:
    _lib = None

    @classmethod
    def _loadLib (cls):
        if cls._lib:
            return

        lib = cls._lib = loadCDLL(LZO_DLL_PATH)

        lib.lzo1x_1_compress.restype  = CI32  # int
        lib.lzo1x_1_compress.argtypes = [
            CPtrVoid,  # arg1: const lzo_bytep src
            CU32,      # arg2: lzo_uint  src_len
            CPtrVoid,  # arg3: lzo_bytep dst
            CPtrVoid,  # arg4: lzo_uintp dst_len
            CPtrVoid,  # arg5: lzo_voidp wrkmem
        ]

        lib.lzo1x_decompress_safe.restype  = CI32  # int
        lib.lzo1x_decompress_safe.argtypes = [
            CPtrVoid,  # arg1: const lzo_bytep src
            CU32,      # arg2: lzo_uint  src_len
            CPtrVoid,  # arg3: lzo_bytep dst
            CPtrVoid,  # arg4: lzo_uintp dst_len
            CPtrVoid,  # arg5: lzo_voidp wrkmem (unused)
        ]

    @classmethod
    def lzo1x_1_compress (cls, srcBuffer, dataSize, dstBuffer):
        cls._loadLib()

        workSize  = LZO1X_1_MEM_COMPRESS
        wrkBuffer = CBuffer.create(workSize)
        dstSize   = CI32(0)

        result = cls._lib.lzo1x_1_compress(srcBuffer, dataSize, dstBuffer, cRef(dstSize), wrkBuffer)

        if result != LZO_E_OK:
            raise Exception('Failed to compress data')

        return dstSize.value

    @classmethod
    def lzo1x_decompress_safe (cls, workBuffer, compOffset, compSize, sourceSize):
        cls._loadLib()

        decompSize = CI32(sourceSize)

        result = cls._lib.lzo1x_decompress_safe(cRef(workBuffer, compOffset), compSize, workBuffer, cRef(decompSize), None)

        if result != LZO_E_OK:# or decompSize.value != sourceSize:
            raise Exception(f'Failed to decompress data: { result }, { decompSize.value }, { sourceSize } ')

        return bytes(workBuffer)[:sourceSize]

def _test_lzo1x_1_compress_ ():
    sourceData = b'Below we will have a Compression and Decompression section to demonstrate.'

    dataSize  = len(sourceData)
    blockSize = ceil(dataSize / 1024) * 1024
    workSize  = blockSize + blockSize // 16 + 64 + 3

    srcBuffer = CBuffer.fromSource(sourceData + (b'\x00' * (blockSize - dataSize)))
    dstBuffer = CBuffer.create(workSize)

    compSize = LZO.lzo1x_1_compress(srcBuffer, dataSize, dstBuffer)
    compData = bytes(dstBuffer)[:compSize]

    print(dataSize, compSize, compData)

    # ---------------------

    compOffset = workSize - compSize
    workBuffer = CBuffer.fromSource((b'\x00' * compOffset) + compData)

    decompData = LZO.lzo1x_decompress_safe(workBuffer, compOffset, compSize, dataSize)

    print(decompData)


# https://github.com/lz4/lz4/tree/dev/examples
def _test_ ():
    _test_lzo1x_1_compress_()

    # with openFile(r'C:\Users\Berrigan\Desktop\data.lzo') as f:
    #     signature = f.read(4)

    #     if signature != b'LZO\x00':
    #         raise Exception('Wrong signature')

    #     decompSize, compSize = readStruct('>II', f)

    #     compData = f.read(compSize)

    #     blockSize = ceil(decompSize / 1024) * 1024
    #     workSize  = blockSize + blockSize // 16 + 64 + 3

    #     compOffset = workSize - compSize
    #     workBuffer = CBuffer.fromSource((b'\x00' * compOffset) + compData)

    #     decompData = LZO.lzo1x_decompress_safe(workBuffer, compOffset, compSize, decompSize)

    #     writeBin(f.getFilePath() + '.bin', decompData)

    #     print('Ok')


__all__ = [
    'LZO'
]


if __name__ == '__main__':
    _test_()