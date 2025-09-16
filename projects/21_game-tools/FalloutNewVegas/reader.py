from utils import *


MEM_READER_SIZE_LIMIT = 256 * 1024 * 1024


class Reader:
    TYPE_FS = 1
    TYPE_MEMORY = 2

    def __init__ (self, reader):
        self.reader = reader

    def __del__ (self):
        self.close()

    def __enter__ (self):
        return self

    def __exit__ (self, *args, **kwargs):
        self.close()

    def skip (self, count):
        self.reader.seek(self.reader.tell() + count)

    def i8 (self, count=1, pad=0):
        return readStruct(f'<{ count }b{ pad }x', self.reader)

    def u8 (self, count=1, pad=0):
        return readStruct(f'<{ count }B{ pad }x', self.reader)

    def i16 (self, count=1, pad=0):
        return readStruct(f'<{ count }h{ pad }x', self.reader)

    def u16 (self, count=1, pad=0):
        return readStruct(f'<{ count }H{ pad }x', self.reader)

    def i32 (self, count=1, pad=0):
        return readStruct(f'<{ count }i{ pad }x', self.reader)

    def u32 (self, count=1, pad=0):
        return readStruct(f'<{ count }I{ pad }x', self.reader)

    def i64 (self, count=1, pad=0):
        return readStruct(f'<{ count }q{ pad }x', self.reader)

    def u64 (self, count=1, pad=0):
        return readStruct(f'<{ count }Q{ pad }x', self.reader)

    def f32 (self, count=1, pad=0):
        return readStruct(f'<{ count }f{ pad }x', self.reader)

    def f64 (self, count=1, pad=0):
        return readStruct(f'<{ count }d{ pad }x', self.reader)

    def struct (self, structFormat):
        return readStruct(structFormat, self.reader)

    def string (self, size=-1, encoding='utf-8'):
        return readString(self.reader, size, encoding)

    def close (self):
        pass

    def getSize (self):
        pass

    def getFilePath (self):
        pass


class FSReader (Reader):
    def __init__ (self, filePath):
        self.f = open(filePath, 'rb')
        self.size = None

        super().__init__(self)

    def close (self):
        if self.f:
            self.f.close()

        self.f = None

    def read (self, sizeToRead = None):
        return self.f.read(sizeToRead)

    def tell (self):
        return self.f.tell()

    def seek (self, offset):
        return self.f.seek(offset)

    def getSize (self):
        if self.size is None:
            self.size = getFileSize(self.f.name)

        return self.size

    def getFilePath (self):
        return self.f.name


class MemReader (Reader):
    def __init__ (self, data, filePath = None):
        self.buffer = data
        self.size = len(data)
        self.cursor = 0
        self.filePath = filePath

        super().__init__(self)

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

    def seek (self, offset):
        if not isinstance(offset, int) or offset < 0:
            raise OSError('Invalid argument')

        self.cursor = offset

        return self.cursor

    def getSize (self):
        return self.size

    def getFilePath (self):
        return self.filePath


def openFile (filePath, readerType = None):
    if readerType == Reader.TYPE_MEMORY or readerType is None and getFileSize(filePath) <= MEM_READER_SIZE_LIMIT:
        with open(filePath, 'rb') as f:
            return MemReader(f.read(), filePath)
            
    return FSReader(filePath)


def __test__ ():
    with openFile(r"G:\Steam\steamapps\common\Fallout New Vegas enplczru\Data\Fallout - Meshes.bsa") as f:
        print(isinstance(f, MemReader), f.string(3), f.getSize(), f.getFilePath())

    with openFile(r"G:\Steam\steamapps\common\Fallout New Vegas enplczru\Data\FalloutNV.esm") as f:
        print(isinstance(f, MemReader), f.string(3), f.getSize(), f.getFilePath())


__all__ = [
    'MEM_READER_SIZE_LIMIT',
    'Reader',
    'FSReader',
    'MemReader',
    'openFile',
]


if __name__ == '__main__':
    __test__()
