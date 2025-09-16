import os
import re
import sys
import json
import struct
import subprocess

from math import ceil
from zlib import decompressobj, crc32 as getCRC32
from stat import S_IREAD, S_IWRITE
from collections import namedtuple as createNamedTuple
from os.path import (
    join as joinPath, 
    isfile as isFile, 
    isdir as isDir, 
    exists as checkPathExists, 
    splitext as splitExt, 
    isabs as isAbsPath, 
    abspath as getAbsPath, 
    normpath as getNormPath, 
    relpath as getRelPath, 
    basename as getBaseName, 
    dirname as getDirPath, 
    getsize as getFileSize
)



def iterFiles (rootDir, isRecursive=True, includeExts=[], excludeExts=[]):
    assert not (includeExts and excludeExts), 'Expected only \'includeExts\' or \'excludeExts\' argument, not both'

    rootDir = getAbsPath(rootDir)
    includeExts = [ item.lower() for item in includeExts ]
    excludeExts = [ item.lower() for item in excludeExts ]

    if not isDir(rootDir):
        print(f'Dir does not exist: { rootDir }')
        return

    if isRecursive:
        for dirPath, _, fileNames in os.walk(rootDir):
            for fileName in fileNames:
                filePath = joinPath(dirPath, fileName)
                fileExt  = getExt(fileName)

                if (includeExts and fileExt not in includeExts) or (excludeExts and fileExt in excludeExts):
                    continue

                yield filePath
    else:
        for item in os.listdir(rootDir):
            itemPath = joinPath(rootDir, item)
            itemExt  = getExt(item)

            if not isFile(itemPath) or (includeExts and itemExt not in includeExts) or (excludeExts and itemExt in excludeExts):
                continue

            yield itemPath


PathInfo = createNamedTuple('PathInfo', (
    'path',      # C:\Python\3.11_x64\python.EXE
    'dirPath',   # C:\Python\3.11_x64
    'baseName',  # python.EXE
    'fileName',  # python
    'fileExt'    # .exe (in lowercase)
))


def parsePath (path):
    path = getNormPath(path)
    dirPath = getDirPath(path)
    baseName = getBaseName(path)
    fileName, fileExt = splitExt(baseName)

    return PathInfo(
       path     = path, 
       dirPath  = dirPath, 
       baseName = baseName, 
       fileName = fileName, 
       fileExt  = fileExt.lower()
    )


def getExt (path, noDot=False):
    ext = splitExt(path)[1].lower()

    return ext[1:] if ext and noDot else ext


def getFileName (path):
    return splitExt(getBaseName(path))[0]


def replaceExtension (filePath, newExt):
    if newExt[0] != '.':
        newExt = '.' + newExt

    return splitExt(filePath)[0] + newExt.lower()


def createDirs (dirPath):
    os.makedirs(dirPath, exist_ok=True)


def removeFile (filePath):
    if not checkPathExists(filePath):
        return 

    if not isFile(filePath):
        raise Exception(f'Is not a file: { filePath }')

    setReadOnly(filePath, False)

    os.remove(filePath)


def toJson (data, pretty=True):
    if pretty:
        indent = 4
        separators=(', ', ': ')
    else:
        indent = None
        separators=(',', ':')

    return json.dumps(data, indent=indent, separators=separators, ensure_ascii=False)  


def writeJson (filePath, data, pretty=True, encoding='utf-8'):
    data = toJson(data, pretty=pretty)

    with open(filePath, 'w', encoding=encoding) as f:
        f.write(data) 


def readJson (filePath, encoding='utf-8'):
    with open(filePath, 'r', encoding=encoding) as f:
        return json.loads(f.read().strip())


def readJsonSafe (filePath, default=None, encoding='utf-8'):
    try:
        return readJson(filePath, encoding=encoding)
    except:
        return default


def decompressData (data):
    decompress = decompressobj()
    data = decompress.decompress(data)
    data += decompress.flush()

    return data


def align (value, boundary):
    return ceil(value / boundary) * boundary


def getFileCRC32 (filePath):
    with open(filePath, 'rb') as f:
        return getCRC32(f.read())


def formatSize (size):
    if size >= (1024 ** 3):
        return '{:.1f}GB'.format(size / (1024 ** 3))
    elif size >= (1024 ** 2):
        return '{:.1f}MB'.format(size / (1024 ** 2))
    elif size >= 1024:
        return '{:.1f}KB'.format(size / 1024)
    else:
        return '{}B'.format(size)


def formatHex (byteSeq, sep=' '):
    return sep.join([ f'{byte:02X}' for byte in byteSeq ])


def formatBytes (byteSeq):
    return '\\x' + formatHex(byteSeq, '\\x')


def readStruct (structFormat, source):
    structSize = struct.calcsize(structFormat)
    dataChunk  = source.read(structSize)
    values     = struct.unpack(structFormat, dataChunk)

    return values[0] if len(values) == 1 else values


def readString (source, size=-1, encoding='utf-8'):
    encoding = (encoding or '').lower()

    if encoding in [ '', 'ascii', 'utf8', 'utf-8' ]:
        null = b'\x00'
        width = 1
    elif encoding in [ 'utf16', 'utf-16', 'utf-16le', 'utf-16-le', 'utf-16be', 'utf-16-be' ]:
        null = b'\x00\x00'
        width = 2
    elif encoding is not None:
        raise Exception(f'Not supported encoding: { encoding }')

    if not isinstance(size, int):
        size = -1
    elif size == 0:
        return '' if encoding else b''

    startOffset = source.tell()
    endOffset   = (startOffset + size) if size > 0 else -1

    buff = b''

    while endOffset < 0 or (source.tell() + width) <= endOffset:
        byte = source.read(width)

        if len(byte) < width or byte == null:
            break

        buff += byte

    if endOffset > 0:
        assert source.tell() <= endOffset
        source.seek(endOffset)

    return buff.decode(encoding) if encoding else buff


def readAlignedString (source, boundary, encoding='utf-8'):
    startOffset = source.tell()
    string      = readString(source, encoding=encoding)
    endOffset   = source.tell()
    finalOffset = align(endOffset - startOffset, boundary)

    source.seek(finalOffset)

    return string


def findPattern (data, pattern):
    offsets = []

    if not data or not pattern:
        return offsets

    dataSize    = len(data)
    patternSize = len(pattern)
    startOffset = 0

    while startOffset < dataSize:
        chunk = data[startOffset:]

        try:
            offset = chunk.index(pattern)
        except:
            offset = -1

        if offset >= 0:
            offsets.append(startOffset + offset)
            startOffset = startOffset + offset + patternSize
        else:
            break

    return offsets


def checkReadOnly (path):
    if not checkPathExists(path):
        return False

    return not (os.stat(path).st_mode & S_IWRITE)


def setReadOnly (path, isReadOnly):
    if not checkPathExists(path):
        return 

    os.chmod(path, (S_IREAD if isReadOnly else S_IWRITE))


class MemReader:
    def __init__ (self, data, name=None):
        self.buffer = data
        self.size = len(data)
        self.cursor = 0
        self.name = name

    def __del__ (self):
        self.close()

    def __enter__ (self):
        return self

    def __exit__ (self, *args, **kwargs):
        self.close()

    def open (self):
        pass

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

    def skip (self, count):
        self.seek(self.tell() + count)

    def i8 (self, count=1, pad=0):
        return readStruct(f'<{ count }b{ pad }x', self)

    def u8 (self, count=1, pad=0):
        return readStruct(f'<{ count }B{ pad }x', self)

    def i16 (self, count=1, pad=0):
        return readStruct(f'<{ count }h{ pad }x', self)

    def u16 (self, count=1, pad=0):
        return readStruct(f'<{ count }H{ pad }x', self)

    def i32 (self, count=1, pad=0):
        return readStruct(f'<{ count }i{ pad }x', self)

    def u32 (self, count=1, pad=0):
        return readStruct(f'<{ count }I{ pad }x', self)

    def f32 (self, count=1, pad=0):
        return readStruct(f'<{ count }f{ pad }x', self)

    def vec3 (self, pad=0):
        return readStruct(f'<3f{ pad }x', self)

    def struct (self, structFormat):
        return readStruct(structFormat, self)

    def string (self, size=-1, encoding='utf-8'):
        return readString(self, size, encoding) 


if __name__ == '__main__':
    pass