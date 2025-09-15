import os
import sys

from array import array

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from bfw.utils import *



# https://docs.python.org/3/library/array.html
class TypedArray:
    def __init__ (self, source, byteOrder, swapBytes):
        self._arr = None
        self._bo  = None

        self._init(source, byteOrder, swapBytes)

    def _init (self, source, byteOrder, swapBytes):
        cls = self.__class__

        if source is None:
            source = b''

        self._arr = array(cls.TypeCode, source)
        self._bo  = byteOrder

        assert self._arr.itemsize == cls.TypeSize

        if self._bo == ByteOrder.Auto:
            self._bo = ByteOrder.getSystem()

        if swapBytes:
            self.swapBytes()

    def swapBytes (self):
        self._arr.byteswap()

        if self._bo == ByteOrder.Little:
            self._bo = ByteOrder.Big
        else:
            self._bo = ByteOrder.Little

    def toLittleEndian (self):
        if self._bo == ByteOrder.Big:
            self.swapBytes()

    def toBigEndian (self):
        if self._bo == ByteOrder.Little:
            self.swapBytes()

class I8Array (TypedArray):
    TypeSize = 1
    TypeCode = 'b'

    def __init__ (self, source=None, byteOrder=ByteOrder.Auto, swapBytes=False):
        super().__init__(source, byteOrder, swapBytes)

class U8Array (TypedArray):
    TypeSize = 1
    TypeCode = 'B'

class I16Array (TypedArray):
    TypeSize = 2
    TypeCode = 'h'

class U16Array (TypedArray):
    TypeSize = 2
    TypeCode = 'H'

class I32Array (TypedArray):
    TypeSize = 4
    TypeCode = 'l'

class U32Array (TypedArray):
    TypeSize = 4
    TypeCode = 'L'

class I64Array (TypedArray):
    TypeSize = 8
    TypeCode = 'q'

class U64Array (TypedArray):
    TypeSize = 8
    TypeCode = 'Q'

class F32Array (TypedArray):
    TypeSize = 4
    TypeCode = 'f'

class F64Array (TypedArray):
    TypeSize = 8
    TypeCode = 'd'



def _test_ ():
    arr = I8Array()



__all__ = [
    'TypedArray',
    'I8Array',
    'U8Array',
    'I16Array',
    'U16Array',
    'I32Array',
    'U32Array',
    'I64Array',
    'U64Array',
    'F32Array',
    'F64Array',
]



if __name__ == '__main__':
    _test_()