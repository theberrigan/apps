import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..'))) 

from bfw.utils import *
from bfw.writer import *
from bfw.native.base import *



CRYPTO_DLL_PATH = joinPath(BIN_DIR, 'bfw.crypto.dll')



class NativeCrypto:
    _lib = None

    @classmethod
    def _loadLib (cls):
        if cls._lib:
            return

        lib = cls._lib = loadCDLL(CRYPTO_DLL_PATH)

        lib.xorBuffer.restype  = CU8  # uint8_t
        lib.xorBuffer.argtypes = [
            CPtrVoid,  # arg1: uint8_t *pBuffer
            CU32,      # arg2: uint32_t bufferSize
            CPtrVoid,  # arg3: const uint8_t *pKey
            CU32,      # arg4: uint32_t keySize
        ]

    @classmethod
    def xorBuffer (cls, data, key):
        cls._loadLib()

        dataBuffer = CBuffer.fromSource(data)
        dataSize   = len(dataBuffer)
        keyBuffer  = CBuffer.fromSource(key)
        keySize    = len(keyBuffer)

        isOk = cls._lib.xorBuffer(dataBuffer, dataSize, keyBuffer, keySize)

        if not isOk:
            raise Exception(f'Failed to XOR buffer: dataSize={ dataSize } keySize={ keySize }')

        return data


        
def _test_ ():
    pass



__all__ = [
    'NativeCrypto'
]



if __name__ == '__main__':
    _test_()
