import os
import re
import struct
from abc import abstractmethod, ABCMeta

from gogta.constants import NULL_BYTE
from gogta.common import getIndex
from io import TextIOWrapper, BufferedReader, UnsupportedOperation
import inspect

# openFile(filePath, mode, offset, size)
# openBuffer()
# io.BufferedReader
# io.DEFAULT_BUFFER_SIZE

# module (file) -> module (funcs...)

'''
file + t/b
file + t/b + o/s
buff + t/b
buff + t/b + o/s

[any] buffering == -1 - auto
[bin] buffering == 0  - disable buffering
[txt] buffering == 1  - enable line buffering
[any] buffering > 1   - buffer size
'''


class TextFileReader:
    pass


class TextBufferReader:
    pass


READER_SEEK_FROM_START   = 0
READER_SEEK_FROM_CURRENT = 1
READER_SEEK_FROM_END     = 2


class BinaryReaderBase (metaclass=ABCMeta):
    def __init__ (self):
        self._readerType = None
        self._bufferSize = None
        self._chunkOffset = None
        self._chunkSize = None
        self._cursorStart = None
        self._cursorEnd = None

    @abstractmethod
    def __del__ (self):
        pass

    @abstractmethod
    def __enter__ (self):
        pass

    @abstractmethod
    def __exit__ (self):
        pass

    def _checkChunkBoundaries (self, chunkOffset, chunkSize):
        if (chunkOffset is not None) and (not isinstance(chunkOffset, int) or chunkOffset < 0):
            raise ValueError("Incorrect value of 'chunkOffset', it must be None or non-negative integer")

        if (chunkSize is not None) and (not isinstance(chunkSize, int) or chunkSize < 0):
            raise ValueError("Incorrect value of 'chunkSize', it must be None or non-negative integer")

    @abstractmethod
    def _updateCursorByChunk (self):
        pass

    @abstractmethod
    def _clampReadSize (self, size):
        pass

    def _checkOpen(self, message):
        if not self.isOpen:
            raise ValueError(message)

    @property
    @abstractmethod
    def isOpen (self):
        pass

    @property
    @abstractmethod
    def isAtEnd (self):
        pass

    @property
    def bufferSize (self):
        self._checkOpen(f"Can't get 'bufferSize', { self._readerType } is closed")
        return self._bufferSize

    @property
    def chunkOffset (self):
        return self._chunkOffset

    @property
    def chunkSize (self):
        return self._chunkSize

    @property
    def cursorStart (self):
        self._checkOpen(f"Can't get 'cursorStart', { self._readerType } is closed")
        return self._cursorStart

    @property
    def cursorEnd (self):
        self._checkOpen(f"Can't get 'cursorEnd', { self._readerType } is closed")
        return self._cursorEnd

    @abstractmethod
    def close (self):
        pass

    def move (self, chunkOffset, chunkSize):
        self._checkChunkBoundaries(chunkOffset, chunkSize)

        self._chunkOffset = chunkOffset
        self._chunkSize = chunkSize

        if self.isOpen:
            self._updateCursorByChunk()

    @abstractmethod
    def read (self, size=None):
        pass

    @abstractmethod
    def peek (self, size=None):
        pass

    @abstractmethod
    def seek (self, offset, fromWhat=READER_SEEK_FROM_START):
        pass

    @abstractmethod
    def tell (self, isAbsolute=False):
        pass

    def readStruct (self, structFormat):
        self._checkOpen(f"Can't call 'readStruct' on closed { self._readerType }")

        values = struct.unpack(structFormat, self.read(struct.calcsize(structFormat)))

        return values if len(values) > 1 else values[0]

    def readString (self, size=None, limit=None, isNullTerminated=False, encoding='utf-8'):
        self._checkOpen(f"Can't call 'readString' on closed { self._readerType }")

        if limit is not None:
            if not isinstance(limit, int) or limit <= 0:
                raise ValueError('Incorrect value of \'limit\', it must be None or positive integer')

            if size is not None:
                raise ValueError("'size' and 'limit' can not be used together")

            if not isNullTerminated:
                raise ValueError("'limit' can not be used with isNullTerminated == False")

        if (size is not None) and (not isinstance(size, int) or size <= 0):
            raise ValueError("Incorrect value of 'size', it must be None or positive integer")

        if self.isAtEnd:
            return '' if encoding else b''

        string = b''

        # !isNullTerminated + size
        #  isNullTerminated + size
        if size:
            string = self.read(size)

            if isNullTerminated:
                index = getIndex(string, NULL_BYTE)

                if index >= 0:
                    string = string[:index]

        #  isNullTerminated
        #  isNullTerminated + limit
        elif isNullTerminated:
            count = 0

            while (not self.isAtEnd) and (limit is None or count < limit):
                byte = self.read(1)

                if byte == NULL_BYTE:
                    break

                string += byte
                count += 1

        # !isNullTerminated
        else:
            string = self.read()

        return string.decode(encoding) if encoding else string


class BinaryFileReader (BinaryReaderBase):
    def __init__(self, filePath, chunkOffset=None, chunkSize=None, bufferSize=-1):
        super().__init__()

        self._readerType = 'file'

        if not isinstance(filePath, str):
            raise TypeError('Unexpected type of file path')

        if not os.path.isfile(filePath):
            raise IOError(f'File does not exist: { filePath }')

        self._checkChunkBoundaries(chunkOffset, chunkSize)

        self._filePath = filePath
        self._chunkOffset = chunkOffset
        self._chunkSize = chunkSize
        self._bufferSize = bufferSize

        self._mode = 'rb'
        self._cursorStart = 0
        self._cursorEnd = 0

        self._fileSize = os.path.getsize(self.filePath)
        self._descriptor = open(self.filePath, mode=self.mode, buffering=self.bufferSize)

        self._updateCursorByChunk()

    def __del__ (self):
        self.close()

    def __enter__ (self):
        return self

    def __exit__ (self, *args, **kwargs):
        self.close()

    def _updateCursorByChunk (self):
        self._checkOpen('Can\'t update cursor of a closed file')

        self._cursorStart = min(self.fileSize, self.chunkOffset or 0)
        self._cursorEnd = min(self.fileSize, self.cursorStart + (self.fileSize if self.chunkSize is None else self.chunkSize))

        self._descriptor.seek(self.cursorStart)

    def _clampReadSize (self, size):
        if (size is not None) and (not isinstance(size, int) or size < 0):
            raise ValueError('Incorrect value of \'size\', it must be None or non-negative integer')

        maxSize = self.cursorEnd - self._descriptor.tell()
        size = maxSize if size is None else min(size, maxSize)

        return size

    @property
    def isOpen (self):
        return bool(self._descriptor)

    @property
    def isAtEnd (self):
        self._checkOpen("Can't get 'isAtEnd', file is closed")
        return self._descriptor.tell() >= self._cursorEnd

    @property
    def fileSize (self):
        self._checkOpen("Can't get 'size', file is closed")
        return self._fileSize

    @property
    def filePath (self):
        return self._filePath

    @property
    def mode (self):
        return self._mode

    def close (self):
        if not self.isOpen:
            return

        self._descriptor.close()
        self._descriptor = None
        self._fileSize = 0
        self._cursorStart = 0
        self._cursorEnd = 0

    def read (self, size=None):
        self._checkOpen('Can\'t call \'read\' on closed file')
        return self._descriptor.read(self._clampReadSize(size))

    def peek (self, size=None):
        self._checkOpen("Can't call 'peek' on closed file")
        return self._descriptor.peek(self._clampReadSize(size))

    def seek (self, offset, fromWhat=READER_SEEK_FROM_START):
        self._checkOpen("Can't call 'seek' on closed file")

        if fromWhat == READER_SEEK_FROM_START:
            offset = self.cursorStart + offset
        elif fromWhat == READER_SEEK_FROM_CURRENT:
            offset = self._descriptor.tell() + offset
        elif fromWhat == READER_SEEK_FROM_END:
            offset = self.cursorEnd + offset
        else:
            raise ValueError("Incorrect value of 'fromWhat', it must be 0, 1 or 2")

        offset = min(max(offset, self.cursorStart), self.cursorEnd)

        return self._descriptor.seek(offset)

    def tell (self, isAbsolute=False):
        self._checkOpen("Can't call 'tell' on closed file")

        if isAbsolute:
            return self._descriptor.tell()
        else:
            return self._descriptor.tell() - self.cursorStart


class BinaryBufferReader (BinaryReaderBase):
    def __init__ (self, buffer, chunkOffset=None, chunkSize=None):
        super().__init__()

        self._readerType = 'buffer'

        if not isinstance(buffer, bytes):
            raise ValueError("Incorrect value of 'buffer', it must be bytes object")

        self._checkChunkBoundaries(chunkOffset, chunkSize)

        self._buffer = buffer
        self._chunkOffset = chunkOffset
        self._chunkSize = chunkSize
        self._bufferSize = len(self._buffer)
        self._cursorStart = 0
        self._cursorEnd = 0
        self._cursorPos = 0

        self._updateCursorByChunk()

    def __del__ (self):
        self.close()

    def __enter__ (self):
        return self

    def __exit__ (self, *args, **kwargs):
        self.close()

    def _updateCursorByChunk (self):
        self._checkOpen("Can't update cursor, buffer is closed")

        self._cursorStart = min(self.bufferSize, self.chunkOffset or 0)
        self._cursorEnd = min(self.bufferSize, self.cursorStart + (self.bufferSize if self.chunkSize is None else self.chunkSize))
        self._cursorPos = self.cursorStart

    def _clampReadSize (self, size):
        if (size is not None) and (not isinstance(size, int) or size < 0):
            raise ValueError("Incorrect value of 'size', it must be None or non-negative integer")

        maxSize = self.cursorEnd - self._cursorPos
        size = maxSize if size is None else min(size, maxSize)

        return size

    @property
    def isOpen (self):
        return isinstance(self._buffer, bytes)

    @property
    def isAtEnd (self):
        self._checkOpen("Can't get 'isAtEnd', buffer is closed")
        return self._cursorPos >= self._cursorEnd

    def close (self):
        if not self.isOpen:
            return

        self._buffer = None
        self._chunkOffset = None
        self._chunkSize = None
        self._bufferSize = 0
        self._cursorStart = 0
        self._cursorEnd = 0
        self._cursorPos = 0

    def read (self, size=None):
        self._checkOpen("Can't call 'read' on closed buffer")

        newCursorPos = self._cursorPos + self._clampReadSize(size)
        bufferSlice = self._buffer[self._cursorPos:newCursorPos]

        self._cursorPos = newCursorPos

        return bufferSlice

    def peek (self, size=None):
        self._checkOpen("Can't call 'peek' on closed buffer")

        return self._buffer[self._cursorPos:self._cursorPos + self._clampReadSize(size)]

    def seek (self, offset, fromWhat=READER_SEEK_FROM_START):
        self._checkOpen("Can't call 'seek' on closed buffer")

        if fromWhat == READER_SEEK_FROM_START:
            offset = self.cursorStart + offset
        elif fromWhat == READER_SEEK_FROM_CURRENT:
            offset = self._cursorPos + offset
        elif fromWhat == READER_SEEK_FROM_END:
            offset = self.cursorEnd + offset
        else:
            raise ValueError("Incorrect value of 'fromWhat', it must be 0, 1 or 2")

        offset = min(max(offset, self.cursorStart), self.cursorEnd)

        self._cursorPos = offset

        return self._cursorPos

    def tell (self, isAbsolute=False):
        self._checkOpen("Can't call 'tell' on closed buffer")

        if isAbsolute:
            return self._cursorPos
        else:
            return self._cursorPos - self.cursorStart


class Reader:
    def __init__ (self, filePath):
        self.filePath = filePath
        self.descriptor = None
        self.open()

    def __del__ (self):
        self.close()

    def __enter__ (self):
        return self

    def __exit__ (self, *args, **kwargs):
        self.close()

    def open (self):
        if self.descriptor is None:
            self.descriptor = open(self.filePath, 'rb')

    def close (self):
        if self.descriptor:
            self.descriptor.close()
            self.descriptor = None

    def read (self, size=None):
        return self.descriptor.read(size)

    def readStruct (self, structFormat):
        return struct.unpack(structFormat, self.descriptor.read(struct.calcsize(structFormat)))

    def tell (self):
        return self.descriptor.tell()

    def seek (self, pos):
        return self.descriptor.seek(pos)



class LineReader:
    def __init__ (self, filePath):
        self.filePath = filePath
        self.lines = None
        self.size = 0
        self.cursor = 0
        self.readEntireFile()

    def readEntireFile (self):
        if not os.path.isfile(self.filePath):
            raise Exception('File doesn\'t exist: {}'.format(self.filePath))

        with open(self.filePath, 'r', encoding='utf-8') as f:
            self.lines = [ line.strip() for line in f.readlines() ]
            self.size = len(self.lines)
            self.cursor = 0

    def readLine (self, skipEmptyLines=False):
        while not self.isAtEnd():
            line = self.lines[self.cursor]
            self.cursor += 1

            if line or not skipEmptyLines:
                return line

        return None

    def isAtEnd (self):
        return not self.lines or not self.size or self.cursor >= self.size

    def tell (self):
        return self.cursor


def splitSectionedTextLine (line):
    line = re.sub(r'[\s,]+$', '', line)
    return re.split(r'[\s,]+', line)


def clearSectionedTextLine (line):
    if not line:
        return line

    return re.split(r'[#;]', line, 1)[0].strip()


def readSectionedTextFile (filePath, sectionClasses):
    reader = LineReader(filePath)
    items = []
    sectionClass = None

    while not reader.isAtEnd():
        line = clearSectionedTextLine(reader.readLine())

        assert line is not None, 'Unexpected EOF'

        if not line:
            continue

        if sectionClass:
            if line.lower() == 'end':
                sectionClass = None
                continue

            values = splitSectionedTextLine(line)
            item = sectionClass(*values)
            
            items.append(item)
        else:
            sectionType = line.lower()

            assert sectionType in sectionClasses, 'Unknown section type: {} ({})'.format(sectionType, filePath)

            sectionClass = sectionClasses[sectionType]

    return items


if __name__ == '__main__':
    # with BinaryFileReader('_sample.txt') as f:
    #     print(f.read(10))
    with BinaryBufferReader(bytes(range(10)), 2, 4) as f:
        print(f.readStruct('<I'))
