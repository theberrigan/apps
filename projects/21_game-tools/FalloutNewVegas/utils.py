import os
import json
import struct

from math import ceil
from zlib import decompressobj
from stat import S_IREAD, S_IWRITE
from collections import namedtuple as createNamedTuple
from os.path import (
    join as joinPath, 
    isfile as isFile, 
    isdir as isDir, 
    exists as checkPathExists, 
    splitext as splitExt, 
    abspath as getAbsPath, 
    normpath as getNormPath, 
    relpath as getRelPath, 
    basename as getBaseName, 
    dirname as getDirPath, 
    getsize as getFileSize,
    expandvars as expandPathVars
)


# SCRIPT_DIR = getDirPath(getAbsPath(__file__))


def iterFiles (rootDir, isRecursive=True, includeExts=None, excludeExts=None):
    if excludeExts is None:
        excludeExts = []

    if includeExts is None:
        includeExts = []

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


def getExt (path, dropDot=False):
    ext = splitExt(path)[1].lower()

    if dropDot and ext and ext[0] == '.':
        return ext[1:]

    return ext


def dropExt (path):
    return splitExt(path)[0]


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
        separators = (', ', ': ')
    else:
        indent = None
        separators = (',', ':')

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

    if encoding in [ '', 'ascii', 'cp1251', 'cp1252', 'utf8', 'utf-8' ]:
        null = b'\x00'
        width = 1
    elif encoding in [ 'utf16', 'utf-16', 'utf-16le', 'utf-16-le', 'utf-16be', 'utf-16-be' ]:
        null = b'\x00\x00'
        width = 2
    else:
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


def setBit (bits, bit):
    return bits | bit


def clearBit (bits, bit):
    return bits & ~bit


def isBitSet (bits, bit):
    return bool(bits & bit)


__all__ = [
    'createNamedTuple',
    'joinPath',
    'isFile',
    'isDir',
    'checkPathExists',
    'splitExt',
    'getAbsPath',
    'getNormPath',
    'getRelPath',
    'getBaseName',
    'getDirPath',
    'getFileSize',
    'expandPathVars',
    'iterFiles',
    'PathInfo',
    'parsePath',
    'getExt',
    'dropExt',
    'getFileName',
    'replaceExtension',
    'createDirs',
    'removeFile',
    'toJson',
    'writeJson',
    'readJson',
    'readJsonSafe',
    'decompressData',
    'align',
    'formatSize',
    'formatHex',
    'formatBytes',
    'readStruct',
    'readString',
    'readAlignedString',
    'findPattern',
    'checkReadOnly',
    'setReadOnly',
    'setBit',
    'clearBit',
    'isBitSet',
]


if __name__ == '__main__':
    pass
