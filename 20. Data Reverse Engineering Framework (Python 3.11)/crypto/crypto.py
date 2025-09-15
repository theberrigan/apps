import os
import sys
import secrets

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..'))) 

from bfw.utils import *


# array
# bisect
# memoryview

# array
# CBuffer
# (c_uint8 * 10)()
# BytesIO()
# bytes, bytearray
# Decimal
# Enum, EnumFlag
# Construct
# deflate, lz4, Oodle, brotli, gzip, lzma (2), zstd, lzo

# (size, source, srcSize, srcOffset, dstOffset)

# I8, I16, I32, I64
# U8, U16, U32, U64
# DI8, DI16, DI32, DI64
# DU8, DU16, DU32, DU64
# CI8, CI16, CI32, CI64
# CU8, CU16, CU32, CU64


def genFixedId (byteCount, toHex=True):
    token = secrets.token_bytes(byteCount)

    if toHex:
        token = token.hex().lower()

    return token



def _test_ ():
    myId = genFixedId(10)

    print(myId)



__all__ = [
    'genFixedId'
]



if __name__ == '__main__':
    _test_()