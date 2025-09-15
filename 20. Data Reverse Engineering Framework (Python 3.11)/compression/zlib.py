import os
import sys
import zlib

from math import log2

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..'))) 

from bfw.utils import *



# Notes:
# - deflate - compression algo
# - zlib - one of the wrappers for deflate-compressed data
# - gzip - one of the wrappers for deflate-compressed data
# - zlib and gzip are incompatible
# - ZL class below supports zlib and gzip depending on the wbits argument
# See: https://stackoverflow.com/a/68538037


class DeflateContainerType:
    Unknown = 0
    No      = 1  # raw deflate data w/o meta
    Zlib    = 2  # deflate data with zlib meta
    Gzip    = 3  # deflate data with gzip meta

class DeflateLevel:
    Default = -1
    No      = 0
    Min     = 1
    Optimal = 6
    Max     = 9

DEFLATE_MIN_DICT_SIZE_POW = 9
DEFLATE_MAX_DICT_SIZE_POW = 15
DEFLATE_MIN_DICT_SIZE     = 2 ** DEFLATE_MIN_DICT_SIZE_POW
DEFLATE_MAX_DICT_SIZE     = 2 ** DEFLATE_MAX_DICT_SIZE_POW
DEFLATE_DEFAULT_DICT_SIZE = DEFLATE_MAX_DICT_SIZE

        
class Deflate:
    @classmethod
    def compress (cls, data, level=DeflateLevel.Default, dictSize=DEFLATE_DEFAULT_DICT_SIZE, containerType=DeflateContainerType.Zlib):
        if level == DeflateLevel.Default:
            level = DeflateLevel.Optimal

        if level < 0 or level > 9:
            raise Exception(f'Wrong deflate compression level: { level }')

        dictSizePow = log2(max(1, dictSize))

        if dictSize <= 0 or \
           int(dictSizePow) != dictSizePow or \
           dictSizePow < DEFLATE_MIN_DICT_SIZE_POW or \
           dictSizePow > DEFLATE_MAX_DICT_SIZE_POW:
            raise Exception(
                f'Dictionary size must be a power of two from { DEFLATE_MIN_DICT_SIZE } ' \
                f'(2^{ DEFLATE_MIN_DICT_SIZE_POW }) to { DEFLATE_MAX_DICT_SIZE } ' \
                f'(2^{ DEFLATE_MAX_DICT_SIZE_POW }), { dictSize } given'
            )

        dictSizePow = int(dictSizePow)

        if containerType == DeflateContainerType.No:
            windowBits = -dictSizePow
        elif containerType == DeflateContainerType.Zlib:
            windowBits = dictSizePow
        elif containerType == DeflateContainerType.Gzip:
            windowBits = 16 + dictSizePow
        else:
            raise Exception(f'Unknown deflate container type: { containerType }')

        return zlib.compress(data, level=level, wbits=windowBits)

    @classmethod
    def decompress (cls):
        pass

    @classmethod
    def getContainerType (cls, data):
        if len(data) < 2:
            return DeflateContainerType.Unknown

        a = data[0]
        b = data[1]

        if a == 0x1F and b == 0x8B:
            return DeflateContainerType.Gzip

        compMethod = a & 15
        dictSize   = (a >> 4) & 15
        signature  = (a << 8) | b

        if compMethod == 8 and dictSize < 8 and signature % 31 == 0:
            return DeflateContainerType.Zlib

        return DeflateContainerType.Unknown

    @classmethod
    def isSupportedContainer (cls, data):
        return cls.getContainerType(data) != DeflateContainerType.Unknown

    @classmethod
    def createCompressor (cls):
        return cls.getContainerType(data) != DeflateContainerType.Unknown

class DeflateMemoryUsage:
    Default = zlib.DEF_MEM_LEVEL
    Min     = 1
    Max     = 9

class DeflateCodecUsage:
    Default       = zlib.Z_DEFAULT_STRATEGY  # LZ + Huffman
    EntropyFixed  = zlib.Z_FIXED             # don't use dynamic Huffman codes
    EntropyOnly   = zlib.Z_HUFFMAN_ONLY      # Huffman only
    PreferEntropy = zlib.Z_FILTERED          # prefer Huffman over LZ
    RLE           = zlib.Z_RLE               # LZ with limited match distance to 1

class DeflateCompressor:
    def __init__ (
        self,
        level         = DeflateLevel.Default,
        dictSize      = DEFLATE_DEFAULT_DICT_SIZE,
        containerType = DeflateContainerType.Zlib,
        memUsage      = DeflateMemoryUsage.Default,
        codecUsage    = DeflateCodecUsage.Default,
        dictData      = None
    ):
        self.co = zlib.compressobj()

    def compress (self, data):
        return self.co.compress(data)


def _test_ ():
    # -------------------

    sourceData = b'Below we will have a Compression and Decompression section to demonstrate.'

    # -------------------

    # compData = zlib.compress(sourceData)

    # print(compData)

    import gzip

    gzData = gzip.compress(sourceData)
    zlData1 = zlib.compress(sourceData, wbits=9)
    zlData2 = zlib.compress(sourceData, wbits=15)

    print(formatHex(gzData))
    print(formatHex(zlData1))
    print(formatHex(zlData2))
    print(Deflate.getContainerType(gzData))
    print(Deflate.getContainerType(zlData1))
    print(Deflate.getContainerType(zlData2))

    compData = zlib.compress(sourceData)
    print(Deflate.isSupportedContainer(compData))

    print(Deflate.compress(sourceData, 1, 2**16, DeflateContainerType.No))



__all__ = [
#    'LZ4'
]


if __name__ == '__main__':
    _test_()

