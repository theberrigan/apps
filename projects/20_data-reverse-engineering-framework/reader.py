import os
import sys
import struct

from math import ceil

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))) 

from bfw.utils import *



MEM_READER_SIZE_LIMIT = 256 * 1024 * 1024



class ReaderType:
    Auto = 0
    FS   = 1
    Mem  = 2

# .isMem()
# .getBuffer()  # for in-mem only
# bytes iterators
# .align()
class Reader:
    def __init__ (self, byteOrder):
        self.byteOrder = byteOrder

    def __del__ (self):
        self.close()

    def __enter__ (self):
        return self

    def __exit__ (self, *args, **kwargs):
        self.close()

    def setByteOrder (self, byteOrder):
        self.byteOrder = byteOrder

    def _struct (self, structFormat, asArray, byteOrder):
        if structFormat and structFormat[0] not in '@=<>!':
            if byteOrder == ByteOrder.Little:
                structFormat = '<' + structFormat
            elif byteOrder == ByteOrder.Big:
                structFormat = '>' + structFormat
            elif self.byteOrder == ByteOrder.Little:
                structFormat = '<' + structFormat
            elif self.byteOrder == ByteOrder.Big:
                structFormat = '>' + structFormat

        structSize = struct.calcsize(structFormat)
        dataChunk  = self.read(structSize)
        values     = struct.unpack(structFormat, dataChunk)

        if asArray or len(values) > 1:
            return list(values)

        return values[0]


    def int (self, size, signed=False):
        if not isinstance(size, int):
            raise Exception(f'Expected type of argument \'size\' is int, but { getType(size) } given')

        if size <= 0:
            raise Exception(f'Argument \'size\' expected to be greater than 0')

        data = self.read(size)

        if len(data) != size:
            raise Exception(f'Not enough data in buffer to read { size } byte(s)')

        if self.byteOrder == ByteOrder.Little:
            byteOrder = 'little'
        elif self.byteOrder == ByteOrder.Big:
            byteOrder = 'big'
        else:
            assert 0, f'Unknown byte order { self.byteOrder }'

        return int.from_bytes(data, byteOrder, signed=signed)

    def i8 (self, count=1, pad=0, asArray=False, byteOrder=ByteOrder.Auto):
        return self._struct(f'{ count }b{ pad }x', asArray, byteOrder)

    def u8 (self, count=1, pad=0, asArray=False, byteOrder=ByteOrder.Auto):
        return self._struct(f'{ count }B{ pad }x', asArray, byteOrder)

    def i16 (self, count=1, pad=0, asArray=False, byteOrder=ByteOrder.Auto):
        return self._struct(f'{ count }h{ pad }x', asArray, byteOrder)

    def u16 (self, count=1, pad=0, asArray=False, byteOrder=ByteOrder.Auto):
        return self._struct(f'{ count }H{ pad }x', asArray, byteOrder)

    def i32 (self, count=1, pad=0, asArray=False, byteOrder=ByteOrder.Auto):
        return self._struct(f'{ count }i{ pad }x', asArray, byteOrder)

    def u32 (self, count=1, pad=0, asArray=False, byteOrder=ByteOrder.Auto):
        return self._struct(f'{ count }I{ pad }x', asArray, byteOrder)

    def i64 (self, count=1, pad=0, asArray=False, byteOrder=ByteOrder.Auto):
        return self._struct(f'{ count }q{ pad }x', asArray, byteOrder)

    def u64 (self, count=1, pad=0, asArray=False, byteOrder=ByteOrder.Auto):
        return self._struct(f'{ count }Q{ pad }x', asArray, byteOrder)

    def f32 (self, count=1, pad=0, asArray=False, byteOrder=ByteOrder.Auto):
        return self._struct(f'{ count }f{ pad }x', asArray, byteOrder)

    def f64 (self, count=1, pad=0, asArray=False, byteOrder=ByteOrder.Auto):
        return self._struct(f'{ count }d{ pad }x', asArray, byteOrder)

    def vec2 (self, pad=0, byteOrder=ByteOrder.Auto):
        return self._struct(f'2f{ pad }x', True, byteOrder)

    def vec3 (self, pad=0, byteOrder=ByteOrder.Auto):
        return self._struct(f'3f{ pad }x', True, byteOrder)

    def vec4 (self, pad=0, byteOrder=ByteOrder.Auto):
        return self._struct(f'4f{ pad }x', True, byteOrder)

    def vec2i32 (self, pad=0, byteOrder=ByteOrder.Auto):
        return self._struct(f'2i{ pad }x', True, byteOrder)

    def vec3i32 (self, pad=0, byteOrder=ByteOrder.Auto):
        return self._struct(f'3i{ pad }x', True, byteOrder)

    def vec4i32 (self, pad=0, byteOrder=ByteOrder.Auto):
        return self._struct(f'4i{ pad }x', True, byteOrder)

    def ba (self, size=None, pad=0):
        if size is None:
            data = self.read()
        else:
            data = self.read(size)

        if pad > 0:
            self.skip(pad)

        return bytearray(data)

    def struct (self, structFormat, byteOrder=ByteOrder.Auto):
        return self._struct(structFormat, True, byteOrder)

    def string (self, size=-1, encoding='utf-8'):
        return readString(self, size, encoding) 

    def fixedString (self, size=-1, encoding='utf-8'):
        if size < 0:
            size = self.remaining()

        return self.read(size).decode(encoding)

    def alignedString (self, bound, encoding='utf-8'):
        return readAlignedString(self, bound, encoding)

    def ole (self):
        days = self.f64()

        if days < 25569:
            return None

        return fromTimestamp((days - 25569) * 24 * 3600)

    # TODO: case
    # TODO: byte order
    def guid (self, asString=False):
        print('WARNING! Byte order is not taken into account in Reader.guid method, little-endian used')

        a, b, c, d, e0, e1, e2, e3, e4, e5 = self.struct('<I3H6B')

        e = e0 << 40 | e1 << 32 | e2 << 24 | e3 << 16 | e4 << 8 | e5

        if asString:
            return f'{a:08x}-{b:04x}-{c:04x}-{d:04x}-{e:012x}'

        return (a, b, c, d, e)

    def align (self, bound):
        pos = self.tell()
        pos = ceil(pos / bound) * bound

        self.seek(pos)

    def skip (self, count, returnValue=None):
        self.seek(self.tell() + count)

        return returnValue

    def remaining (self):
        return max(0, self.getSize() - self.tell())

    def isEnd (self):
        return self.remaining() == 0

    def peek (self, offset=0, size=1):
        if size <= 0 or (self.tell() + offset) < 0:
            return b''

        pos = self.tell()

        self.fromCurrent(offset)

        data = self.read(size)

        self.seek(pos)

        return data

    def fromStart (self, offset):
        return self.seek(offset, SeekFrom.Start)

    def fromCurrent (self, offset):
        return self.seek(offset, SeekFrom.Current)

    def fromEnd (self, offset):
        return self.seek(offset, SeekFrom.End)

    def read (self, sizeToRead=None):
        raise NotImplementedError('Abstract method \'read\' is not implemented')

    def tell (self):
        raise NotImplementedError('Abstract method \'tell\' is not implemented')

    def seek (self, offset, whence=SeekFrom.Start):
        raise NotImplementedError('Abstract method \'seek\' is not implemented')

    def close (self):
        raise NotImplementedError('Abstract method \'close\' is not implemented')

    def getSize (self):
        raise NotImplementedError('Abstract method \'getSize\' is not implemented')

    def getFilePath (self):
        raise NotImplementedError('Abstract method \'getFilePath\' is not implemented')


class FSReader (Reader):
    def __init__ (self, filePath, byteOrder=ByteOrder.Little):
        self.f = open(filePath, 'rb')
        self.size = None

        super().__init__(byteOrder)

    def close (self):
        if self.f:
            self.f.close()

        self.f = None

    def read (self, sizeToRead = None):
        return self.f.read(sizeToRead)

    def tell (self):
        return self.f.tell()

    def seek (self, offset, whence=SeekFrom.Start):
        return self.f.seek(offset, whence)

    def getSize (self):
        if self.size is None:
            self.size = getFileSize(self.f.name)

        return self.size

    def getFilePath (self):
        return self.f.name


class MemReader (Reader):
    def __init__ (self, data, filePath=None, byteOrder=ByteOrder.Little):
        self.buffer   = data
        self.size     = len(data)
        self.cursor   = 0
        self.filePath = filePath

        super().__init__(byteOrder)

    def close (self):
        self.buffer = None
        self.size = 0
        self.cursor = 0

    def read (self, sizeToRead = None):
        sizeLeft = max(0, self.size - self.cursor)

        if sizeToRead is None or sizeToRead < 0 or sizeToRead >= sizeLeft:
            sizeToRead = sizeLeft

        if sizeToRead == 0:
            return b''

        chunk = self.buffer[self.cursor:self.cursor + sizeToRead]
        
        self.cursor += sizeToRead

        return chunk

    def tell (self):
        return self.cursor

    def seek (self, offset, whence=SeekFrom.Start):
        match whence:
            case SeekFrom.Start:
                base = 0
            case SeekFrom.Current:
                base = self.tell()
            case SeekFrom.End:
                base = self.getSize()
            case _:
                raise ValueError(f'whence value { whence } unsupported')

        cursor = base + offset

        if cursor < 0:
            raise OSError('Invalid argument')

        self.cursor = cursor

        return self.cursor

    def getSize (self):
        return self.size

    def getFilePath (self):
        return self.filePath


def openFile (filePath, readerType=ReaderType.Auto, byteOrder=ByteOrder.Little):
    if readerType == ReaderType.Mem or readerType == ReaderType.Auto and getFileSize(filePath) <= MEM_READER_SIZE_LIMIT:
        return MemReader(readBin(filePath), filePath, byteOrder)
            
    return FSReader(filePath, byteOrder)


__all__ = [
    'MEM_READER_SIZE_LIMIT',
    'ReaderType',
    'Reader',
    'FSReader',
    'MemReader',
    'openFile',
]


if __name__ == '__main__':
    with openFile(r"G:\Steam\steamapps\common\Fallout New Vegas enplczru\steam_eng\Data\Fallout - Meshes.bsa") as f:
        print(isinstance(f, MemReader), f.string(3), f.getSize(), f.getFilePath())

    with openFile(r"G:\Steam\steamapps\common\Fallout New Vegas enplczru\steam_eng\Data\FalloutNV.esm") as f:
        print(isinstance(f, MemReader), f.string(3), f.getSize(), f.getFilePath())