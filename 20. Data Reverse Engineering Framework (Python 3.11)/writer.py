import os
import sys

from io import BytesIO
from struct import pack

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))) 

from bfw.utils import *



class BinWriter:
    def __init__ (self, byteOrder=ByteOrder.Little, data=None):
        self.bio = BytesIO(data)
        self.byteOrder = byteOrder

    def __enter__ (self):
        return self

    def __exit__ (self, *args, **kwargs):
        self.close()

    def __del__ (self):
        self.close()

    def _struct (self, structFormat, args, byteOrder):
        if structFormat and structFormat[0] not in '@=<>!':
            if byteOrder == ByteOrder.Little:
                structFormat = '<' + structFormat
            elif byteOrder == ByteOrder.Big:
                structFormat = '>' + structFormat
            elif self.byteOrder == ByteOrder.Little:
                structFormat = '<' + structFormat
            elif self.byteOrder == ByteOrder.Big:
                structFormat = '>' + structFormat

        return self.write(pack(structFormat, *args))

    def _vecs (self,  vecs, byteOrder):
        vecs  = sum(vecs, [])

        return self._struct(f'{ len(vecs) }f', vecs, byteOrder)

    def i8 (self, *nums, byteOrder=ByteOrder.Auto):
        return self._struct(f'{ len(nums) }b', nums, byteOrder)

    def u8 (self, *nums, byteOrder=ByteOrder.Auto):
        return self._struct(f'{ len(nums) }B', nums, byteOrder)

    def i16 (self, *nums, byteOrder=ByteOrder.Auto):
        return self._struct(f'{ len(nums) }h', nums, byteOrder)

    def u16 (self, *nums, byteOrder=ByteOrder.Auto):
        return self._struct(f'{ len(nums) }H', nums, byteOrder)

    def i32 (self, *nums, byteOrder=ByteOrder.Auto):
        return self._struct(f'{ len(nums) }i', nums, byteOrder)

    def u32 (self, *nums, byteOrder=ByteOrder.Auto):
        return self._struct(f'{ len(nums) }I', nums, byteOrder)

    def i64 (self, *nums, byteOrder=ByteOrder.Auto):
        return self._struct(f'{ len(nums) }q', nums, byteOrder)

    def u64 (self, *nums, byteOrder=ByteOrder.Auto):
        return self._struct(f'{ len(nums) }Q', nums, byteOrder)

    def f32 (self, *nums, byteOrder=ByteOrder.Auto):
        return self._struct(f'{ len(nums) }f', nums, byteOrder)

    def f64 (self, *nums, byteOrder=ByteOrder.Auto):
        return self._struct(f'{ len(nums) }d', nums, byteOrder)

    def vec2 (self, *vecs, byteOrder=ByteOrder.Auto):
        return self._vecs(vecs, byteOrder)

    def vec3 (self, *vecs, byteOrder=ByteOrder.Auto):
        return self._vecs(vecs, byteOrder)

    def vec4 (self, *vecs, byteOrder=ByteOrder.Auto):
        return self._vecs(vecs, byteOrder)

    def struct (self, structFormat, *args):
        return self._struct(structFormat, args, ByteOrder.Auto)

    def string (self, string, isNT=False, size=-1, encoding='utf-8'):
        data = string.encode(encoding)

        if isNT:
            data += getStrTerm(encoding)

        if size >= 0:
            data = data[:size]

        start = self.tell()

        size -= self.write(data)

        if size > 0:
            self.zeros(size)

        return self.tell() - start

    def zeros (self, count):
        return self.write(b'\x00' * count)

    def align (self, boundary):
        oldSize = self.tell()
        newSize = align(oldSize, boundary)

        if newSize > oldSize:
            return self.zeros(newSize - oldSize)

        return 0

    def write (self, data):
        return self.bio.write(data)

    def close (self):
        if self.bio:
            self.bio.close()

        self.bio = None

    def tell (self):
        return self.bio.tell()

    def seek (self, offset, whence=SeekFrom.Start):
        return self.bio.seek(offset, whence)

    def getSize (self):
        return self.bio.getbuffer().nbytes

    def getRaw (self):
        return self.bio.getvalue()

    def save (self, filePath):
        writeBin(filePath, self.bio.getvalue())



def __test__ ():
    with BinWriter() as f:
        print(f.string('Hello', True, 8, 'utf-16-le'))
        print(f.struct('III', 1, 2, 3))
        print(f.u32(0xFFFFFFFF, 0xDDDDDDDD, 0xAAAAAAAA, 0x11223344, byteOrder=ByteOrder.Big))
        print(f.vec3([1, 2, 3], [4, 5, 6], byteOrder=ByteOrder.Big))
        print(f.getSize())
        print(f.align(128))
        print(f.getSize())
        print(f.align(1))
        print(f.getSize())
        print(f.getRaw())



__all__ = [
    'BinWriter'
]



if __name__ == '__main__':
    __test__()