import os
import re
import sys
import json
import zlib
import gzip
import regex
import struct

from hashlib import md5
from typing import Type, TypeVar, List
from uuid import uuid4
from time import time as getTime, sleep
from math import ceil
from stat import S_IREAD, S_IWRITE
from copy import deepcopy as deepCopy
from ctypes import windll
from shutil import rmtree as removeTree, copyfile as copyFileWithoutMeta, copy2 as copyFileWithMeta
from collections import namedtuple as createNamedTuple
from datetime import datetime
from os import rename
from os.path import (
    # join as joinPath, 
    isfile as isFile, 
    isdir as isDir, 
    isabs as isAbsPath,
    exists as checkPathExists, 
    splitext as splitExt, 
    splitdrive as splitDrive,
    abspath as getAbsPath, 
    normpath as getNormPath, 
    relpath as getRelPath, 
    basename as getBaseName, 
    dirname as getDirPath, 
    getsize as getFileSize,
    samefile as areSamePaths,
    expandvars as expandPathVars
)


# SCRIPT_DIR = getDirPath(getAbsPath(__file__))

# TODO:
# https://realpython.com/python-mmap
# replaceDir
# replaceFileName
# replaceBaseName
# in iterFiles preprocess exts
# findFiles (like iterFiles but with file names) (glob?)
# base16 (like base64 but hex)
# rename openFile -> openBinFile
# rename read/write* -> read/write*File
# add different compressors
# registry reader/writer
# xml reader/writer
# adapt reader to different byte orders like writer
# calcFileEntropy, graphFileEntropy
# binaryFind in files (smthlike regex)
# graphData
# setupPrint(color, flush)
# PE reader
# findFileInFS
# cryptography
# C-exactly arithmetics
# find file dups in fs
# scan fs and show summary
# print table
# LE/BE reader
# set all elements of list to <value>, like memset
# pointer wrapper with pointer arithmetics
# profiling https://docs.python.org/3/library/profile.html#profile.Profile
# data structures: FastList (list class based on dict), LinkedList
# VLC downloader
# datetime framework
# adoptBaseName(dstPath, srcPath)
# isPathPrefix
# isPathSuffix
# readCommentedJson
# ----------------
# formatTable
# formatHex
# formatDate
# formatTime
# formatSize
# ----------------
# pe tools
# compression
# registry
# steam (steamapi, steamkit2, steamless)
# xml, ini parser
# signature finder
# game engine detector
# game engine hierarchy
# models, anims, textures converter
# audio tools (play, converter, codecs, fmod/wwise)
# graphics lib bindings (glfw, glew, opengl, cglm)
# Cmath
# signature finder
# crypto key finder
# entropy visualizer
# crypto & compr detection
# disasm (zydex), string and signatures search in exe
# cryptography
# uuid, my id generator
# typed array
# export decorators
# zStr - NT var size string
# aStr - zStr NT var size string with alignment
# fString - fixed size str (w/o term.)
# iso/mds/mdf
# inno .exe unpacker
# install shield extractor
# PS3/4/5/XBOX archives and packages
# lua, squirrel
# lzss, lzo, lzx, lzma, lzma2, deflate, oodle

# ------------------
# u32
# u32a
# cu32
# cu32a
# struct
# b - bytes
# ba - bytearray
# zStr - NT variable size string [with alignment]
# fStr - fixed-size non-NT string
# vec2
# vec2a
# cvec2
# cvec2a

# String
# WString
# Struct
# CBuffer
# 
# ------------------

# see Qt, Nodejs, 

# blib - berrigan's library

# Game Research Framework
# grf.fs  # glob
# grf.hash.{crcN,fnvN,md5,shaN,blake,shake,xxHash,SipHash}
# grf.crypto.{AES256}
# grf.compression.{Deflate,LZMA,LZMA2,LZO,LZX,LZ4,LZ77,LZR,LZW,LZSS,ZStd,RLE,Huffman,Oodle,Brotli,Zip,Rar,SevenZip}
# grf.regex
# grf.encodings.{Base64}
# grf.parsers.{xml,html,json,ini,vdf}
# grf.services.{steam,getSteamDir,getLibDirs}
# grf.platform.{win.{registry,pe,asm}}
# grf.audio.{wwise,fmod,playAudio,convertAudio}
# grf.image.{png,jpeg,astc,dds...}
# grf.cg.{fbx,convertModel}
# grf.cg.{image,mesh,model,anim}
# grf.chrono
# grf.{stream,reader,writer}
# grf.math
# grf.dsa  # data structures and algorithms
# grf.dv.{printer,graph,toHTML}  # data visualization
# grf.net.{parseUrl,requests}
# grf.pl.{lua,qbms}
# grf.analysis.{entropy}
# grf.fmt
# grf.scan
# grf.ge.{ue,unity,cryengine,source,goldsrc,denuia}
# grf.stat  # statistics

# import inspect

# def export (fn):
#     stack = inspect.stack()[1][0]
#     gVars = stack.f_globals

#     if '__all__' not in gVars:
#         gVars['__all__'] = []

#     gVars['__all__'].append(fn.__name__)

#     return fn


PATH_SEP = os.path.sep

class ByteOrder:
    Auto   = 0
    Big    = 1
    Little = 2

    @classmethod
    def getSystem (cls):
        if sys.byteorder == 'little':
            return cls.Little

        return cls.Big

class SeekFrom:
    Start   = os.SEEK_SET
    Current = os.SEEK_CUR
    End     = os.SEEK_END

'''
# https://github.com/django/django/blob/263f7319192b217c4e3b1eea0ea7809836392bbc/django/core/management/color.py#L28C1-L67C6
def supports_color():
    # Return True if the running system's terminal supports color,
    # and False otherwise.

    def vt_codes_enabled_in_windows_registry():
        # Check the Windows Registry to see if VT code handling has been enabled
        # by default, see https://superuser.com/a/1300251/447564.
        try:
            # winreg is only available on Windows.
            import winreg
        except ImportError:
            return False
        else:
            try:
                reg_key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, "Console")
                reg_key_value, _ = winreg.QueryValueEx(reg_key, "VirtualTerminalLevel")
            except FileNotFoundError:
                return False
            else:
                return reg_key_value == 1

    # isatty is not always implemented, #6223.
    is_a_tty = hasattr(sys.stdout, "isatty") and sys.stdout.isatty()

    return is_a_tty and (
        sys.platform != "win32"
        or (HAS_COLORAMA and getattr(colorama, "fixed_windows_console", False))
        or "ANSICON" in os.environ
        or
        # Windows Terminal supports VT codes.
        "WT_SESSION" in os.environ
        or
        # Microsoft Visual Studio Code's built-in terminal supports colors.
        os.environ.get("TERM_PROGRAM") == "vscode"
        or vt_codes_enabled_in_windows_registry()
    )
'''


# TODO: make patch
# noinspection PyShadowingBuiltins
def my_print (*args, **kwargs):
    if 'flush' in kwargs:
        del kwargs['flush']

    lock = kwargs.get('lock')

    if lock:
        del kwargs['lock']
        lock.acquire()

    print(*args, flush=True, **kwargs)

    if lock:
        lock.release()


def formatPrintArgs (args):
    return ' '.join([ str(arg) for arg in args ])


# https://stackoverflow.com/a/38617204
def printS (*args, **kwargs):
    print(f'\033[92m{ formatPrintArgs(args) }\033[0m', **kwargs)


def printW (*args, **kwargs):
    print(f'\033[93m{ formatPrintArgs(args) }\033[0m', **kwargs)


def printE (*args, **kwargs):
    print(f'\033[91m{ formatPrintArgs(args) }\033[0m', **kwargs)

def die (*args, **kwargs):
    print(*args, **kwargs)
    sys.exit(0)

def pjp (obj):
    print(toJson(obj))

def pjpd (obj):
    print(toJson(obj))
    exit()

def pji (obj):
    print(toJson(obj, pretty=False))


def splitSpaces (string):
    return re.split(r'\s+', string)


# TODO: includeExts and excludeExts should accept regex
def iterFiles (rootDir, isRecursive=True, includeExts=None, excludeExts=None):
    '''
    def normalizeFilter (items):
        items = items or []

        if not isinstance(items, list):
            items = [ items ]

        exts = []
        res  = []
        fns  = []

        for item in items:
            if isinstance(item, str):
                exts.append(item.lower())
            elif callable(item):
                fns.append(item)
            elif isinstance(item, re.Pattern):
                res.append((item, re))
            elif isinstance(item, regex.Pattern):
                res.append((item, regex))
            else:
                raise Exception('iterFiles extension filter must be a string, function or regex')

        return exts, res, fns

    def checkFilter (path, filters, isExcluded):
        exts, patterns, fns = filters

        ext = getExt(path)
        baseName = getBaseName(path)

        # True

        if (ext in exts) != value:
            return False

        for pattern, mod in patterns:
            match = mod.search(pattern, baseName, mod.I)

            if bool(match) != value:
                return False
    '''
    assert not (includeExts and excludeExts), 'Expected only \'includeExts\' or \'excludeExts\' argument, not both'

    includeExts = [ ext.lower() for ext in (includeExts or []) ]
    excludeExts = [ ext.lower() for ext in (excludeExts or []) ]

    rootDir = getAbsPath(rootDir)

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


def findAncestorDirByFile (startDir, fileName):
    currentDir = getAbsPath(startDir)
    prevDir = currentDir

    while True:
        if isFile(joinPath(currentDir, fileName)):
            return currentDir

        parentDir = getAbsPath(joinPath(currentDir, '..'))

        if areSamePaths(parentDir, prevDir):
            return None

        prevDir = currentDir
        currentDir = parentDir


def findFileInEnv (filePath):
    envDirs = os.environ['PATH'].split(os.pathsep)

    for envDir in envDirs:
        absFilePath = getAbsPath(joinPath(envDir, filePath))

        if isFile(absFilePath):
            return absFilePath

    return None


class PathInfo:
    def __init__ (self, path, dirPath, baseName, fileName, fileExt):
        self.path     = path      # C:\Python\3.11_x64\python.EXE
        self.dirPath  = dirPath   # C:\Python\3.11_x64
        self.baseName = baseName  # python.EXE
        self.fileName = fileName  # python
        self.fileExt  = fileExt   # .exe (in lowercase)

    def build (self):
        return joinPath(self.dirPath, self.fileName + self.fileExt)


def parsePath (path):
    path     = getNormPath(path)
    dirPath  = getDirPath(path)
    baseName = getBaseName(path)
    fileName, fileExt = splitExt(baseName)

    return PathInfo(
       path     = path, 
       dirPath  = dirPath, 
       baseName = baseName, 
       fileName = fileName, 
       fileExt  = fileExt.lower()
    )


def getDrive (path, dropSep=False):
    drive = splitDrive(path)[0]

    if dropSep:
        drive = drive.strip(':')

    return drive


def joinPath (*paths):
    if not paths:
        return None

    if len(paths) == 1:
        return paths[0]

    lastIndex = len(paths) - 1
    newPaths  = []

    for i, path in enumerate(paths):
        if i == 0: 
            path2 = path.rstrip('\\/')

            if path and not path2:
                newPaths.append(path)
            elif path2:
                newPaths.append(path2)
        elif i == lastIndex:
            newPaths.append(path.lstrip('\\/'))
        else:
            newPaths.append(path.strip('\\/'))

    return os.path.sep.join(newPaths)


def getScriptDir (scriptPath):
    return getAbsPath(getDirPath(scriptPath))


def getExt (path, dropDot=False, toLowerCase=True):
    ext = splitExt(path)[1]

    if toLowerCase:
        ext = ext.lower()

    if dropDot and ext and ext[0] == '.':
        return ext[1:]

    return ext


def dropExt (path):
    return splitExt(path)[0]


def replaceExt (filePath, newExt):
    if newExt and newExt[0] != '.':
        newExt = '.' + newExt

    return splitExt(filePath)[0] + newExt.lower()


def replaceBaseName (filePath, newBaseName):
    return joinPath(getDirPath(filePath), newBaseName)


def replaceFileName (filePath, newFileName):
    dirPath = getDirPath(filePath)
    ext     = getExt(filePath)

    return joinPath(dirPath, newFileName + ext)


def getFileName (path):
    return splitExt(getBaseName(path))[0]


def createDirs (dirPath):
    os.makedirs(dirPath, exist_ok=True)


def createFileDirs (filePath):
    createDirs(getDirPath(filePath))


def removeDirs (dirPath):
    if not checkPathExists(dirPath):
        return 

    removeTree(dirPath)


def removeFile (filePath):
    if not checkPathExists(filePath):
        return 

    if not isFile(filePath):
        raise Exception(f'Is not a file: { filePath }')

    setReadOnly(filePath, False)

    os.remove(filePath)

def copyFile (srcPath, dstPath, keepMeta=False):
    if keepMeta:
        copyFileWithMeta(srcPath, dstPath)
    else:
        copyFileWithoutMeta(srcPath, dstPath)

def getPathModTime (filePath):
    return os.path.getmtime(filePath)

def getPathCreateTime (filePath):
    return os.path.getctime(filePath)

def parseJson (data):
    return json.loads(data.strip())

def parseJsonSafe (data, default=None):
    try:
        return parseJson(data)
    except:
        return default

def encodeJsonValue (obj):
    if hasattr(obj, '__dict__'):
        return vars(obj)

    return repr(obj)

def toJson (data, pretty=True):
    if pretty:
        indent = 4
        separators = (',', ': ')
    else:
        indent = None
        separators = (',', ':')

    return json.dumps(data, indent=indent, separators=separators, ensure_ascii=False, default=encodeJsonValue)


def readJson (filePath, encoding='utf-8'):
    text = readText(filePath, encoding)

    return json.loads(text.strip())


def readJsonSafe (filePath, default=None, encoding='utf-8'):
    try:
        return readJson(filePath, encoding=encoding)
    except:
        return default

# TODO: as arraybuffer, rename
def readBin (filePath, size=-1):
    with open(filePath, 'rb') as f:
        return f.read(size)


def readText (filePath, encoding='utf-8'):
    with open(filePath, 'r', encoding=encoding) as f:
        return f.read()


def readLines (filePath, encoding='utf-8'):
    lines = readText(filePath, encoding).split('\n')
    lines = [ line.rstrip('\r') for line in lines ]

    return lines 


def writeJson (filePath, data, pretty=True, encoding='utf-8'):
    text = toJson(data, pretty=pretty)
    writeText(filePath, text, encoding)


def writeText (filePath, text, encoding='utf-8'):
    with open(filePath, 'w', encoding=encoding) as f:
        f.write(text)


def writeBin (filePath, data):
    with open(filePath, 'wb') as f:
        f.write(data)


def compressData (data, level=9, mode=zlib.MAX_WBITS):
    compress = zlib.compressobj(level=level, wbits=mode)
    data = compress.compress(data)
    data += compress.flush()

    return data


def decompressData (data, mode=zlib.MAX_WBITS):
    decompress = zlib.decompressobj(wbits=mode)
    data = decompress.decompress(data)
    data += decompress.flush()

    return data

def decompressFile (filePath, mode=zlib.MAX_WBITS):
    data = readBin(filePath)
    data = decompressData(data)

    writeBin(filePath + '.decompressed', data)

def decompressGzipFile (filePath):
    data = readBin(filePath)
    data = gzip.decompress(data)

    writeBin(filePath + '.decompressed', data)

def decompressGzip (data):
    return gzip.decompress(data)

def calcCRC32 (data):
    return zlib.crc32(data) & 0xFFFFFFFF

def calcMD5 (data):
    return md5(data).hexdigest().lower()

def createUUID (toUpperCase=False, asHex=False):
    uuid = uuid4()

    if asHex:
        uuid = uuid.hex
    else:
        uuid = str(uuid)

    if toUpperCase:
        return uuid.upper()

    return uuid.lower()


def align (value, bound):
    return ceil(value / bound) * bound


def isPow2 (num):
    if isinstance(num, float):
        if not num.is_integer():
            return False

        num = float(num)

    return (num & (num - 1)) == 0 and num != 0


def clamp (value : float | int, minValue : float | int, maxValue : float | int) -> float | int:
    return min(maxValue, max(minValue, value))


def zeroPad (seq, size=None, bound=None):
    if not isinstance(seq, bytes) and \
       not isinstance(seq, bytearray) and \
       not isinstance(seq, list) and \
       not isinstance(seq, str):
        raise Exception('seq expected to be bytes, list or str')

    seqSize = len(seq)

    if size is not None and bound is not None:
        raise Exception('size and bound are exclusive args')

    if size is None and bound is None:
        raise Exception('size or bound expected')

    if size is not None:
        if not isinstance(size, int):
            raise Exception('size expected to be int')   

        if size < 0:
            raise Exception('size expected to be >= 0')     

    if bound is not None:
        if not isinstance(bound, int):
            raise Exception('bound expected to be int')

        if bound < 1:
            raise Exception('bound expected to be >= 1')

        size = align(seqSize, bound)

    if size <= seqSize:
        if isinstance(seq, list):
            return seq[:]  # copy list
        
        return seq

    if isinstance(seq, bytes) or isinstance(seq, bytearray):
        zero = b'\x00'
    elif isinstance(seq, str):
        zero = '\x00'
    elif isinstance(seq, list):
        zero = [ 0 ]

    return seq + (zero * (size - seqSize))

def getType (value):
    return type(value).__name__

def isStr (value):
    return isinstance(value, str)

def isInt (value):
    return isinstance(value, int)

def isFloat (value):
    return isinstance(value, float)

def isNum (value):
    return isInt(value) or isFloat(value)

def isDict (value):
    return isinstance(value, dict)

def isList (value):
    return isinstance(value, list)

def swapDict (d):
    return { v: k for k, v in d.items() }

def createDoubleMap (d):
    return d | swapDict(d)

def addUnique (arr, key, value=None):
    if key in arr:
        return

    if isDict(arr):
        arr[key] = value
    elif isList(arr):
        arr.append(key)


def concatLists (*lists : list[list]) -> list:
    return sum(lists, [])


TArrayType = TypeVar('TArrayType')

def Array (count : int, cls : Type[TArrayType], *args, **kwargs) -> List[TArrayType]:
    return [ cls(*args, **kwargs) for _ in range(count) ]


def fromTimestamp (sec):
    return datetime.fromtimestamp(sec)


def formatTimestamp (ms):
    ms = int(ms)
    
    n = ms // 1000
    h = n // 3600
    m = n % 3600 // 60
    s = n % 60

    return f'{h:02}:{m:02}:{s:02}'


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


def formatByteString (byteSeq : bytes | bytearray):
    return ''.join([ chr(b) if b < 128 else rf'\x{b:02X}' for b in byteSeq ])


def formatFloat (n : float, decimal=7):
    # do not use str(n) due to scientific notation
    m, e = f'{n:.{decimal}f}'.split('.')

    e = e.strip('0') or '0'

    return f'{m}.{e}'


def getStrTerm (encoding):
    len1 = len(''.encode(encoding))
    len2 = len('\x00'.encode(encoding))

    return b'\x00' * (len2 - len1)


def readStruct (structFormat, source):
    structSize = struct.calcsize(structFormat)
    dataChunk  = source.read(structSize)
    values     = struct.unpack(structFormat, dataChunk)

    return values[0] if len(values) == 1 else list(values)


def readString (source, size=-1, encoding='utf-8'):
    encoding = (encoding or '').lower()

    if encoding:
        null = getStrTerm(encoding)
    else:
        null = b'\x00'

    width = len(null)

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


def readAlignedString (source, bound, encoding='utf-8'):
    startOffset = source.tell()
    string      = readString(source, encoding=encoding)
    endOffset   = source.tell()
    alignedSize = align(endOffset - startOffset, bound)

    source.seek(startOffset + alignedSize)

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


def getBits (num, size, shift):
    return (num >> shift) & (2 ** size - 1)


def splitBits (num, *sizes):
    keepCount  = len([ s for s in sizes if s > 0 ])
    totalCount = len(sizes)
    shift      = 0
    result     = [ 0 ] * keepCount
    keepIndex  = keepCount - 1

    for i in range(totalCount - 1, -1, -1):
        size = sizes[i]

        if size == 0:
            continue

        if size < 0:
            size = -size
        else:
            result[keepIndex] = getBits(num, size, shift)
            keepIndex -= 1

        shift += size

    assert keepIndex == -1, f'keepIndex = { keepIndex }'

    return result


def setBit (bits : int, bit : int) -> int:
    return bits | bit


def clearBit (bits : int, bit : int) -> int:
    # in python bit inverse op (~) is not working properly
    # so, use dynamically created mask and xor
    # https://stackoverflow.com/q/7278779
    count = (bits | bit | 1).bit_length()
    mask  = (2 ** count) - 1

    return bits & (mask ^ bit)


def isBitSet (bits : int, bit : int) -> bool:
    return bool(bits & bit)

def xorBuffer (buffer, key):
    keySize = len(key)

    if keySize > 0:
        for i in range(len(buffer)):
            buffer[i] ^= key[i % keySize]

    return buffer


def getDrives (asRoot=False):
    letters = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'
    bitmask = windll.kernel32.GetLogicalDrives()
    drives  = []

    for letter in letters:
        if bitmask & 1:
            if asRoot:
                drives.append(letter + ':' + PATH_SEP)
            else:
                drives.append(letter)

        bitmask >>= 1

    return drives

def addEnvPath (path, toEnd=False):
    if toEnd:
        os.environ['PATH'] = os.environ['PATH'] + os.pathsep + path
    else:
        os.environ['PATH'] = path + os.pathsep + os.environ['PATH']

def getTimestamp (toMS=True):
    ts = getTime()

    if toMS:
        ts *= 1000

    return int(ts)


# Samples: [LR][LR][LR]...
# https://ccrma.stanford.edu/courses/422-winter-2014/projects/WaveFormat/
def saveAsWave (filePath, pcmData, channelCount, sampleRate, sampleSize=2):
    pcmDataSize = len(pcmData)

    with BinWriter() as f:
        f.write(b'RIFF')                                 # 0x00  char[4]  ChunkID        "RIFF" (Resource Interchange File Format)
        f.u32(pcmDataSize + 36)                          # 0x04  dword    ChunkSize      size from SDT format + 36
        f.write(b'WAVE')                                 # 0x08  char[4]  Format         "WAVE"
        f.write(b'fmt ')                                 # 0x0C  char[4]  Subchunk1ID    "fmt "
        f.u32(16)                                        # 0x10  dword    SubchunkSize   16
        f.u16(1)                                         # 0x14  word     AudioFormat    1 (PCM)
        f.u16(channelCount)                              # 0x16  word     NumChannels    1 (mono)
        f.u32(sampleRate)                                # 0x18  dword    SampleRate     sample rate from SDT format 
        f.u32(sampleSize * channelCount * sampleRate)    # 0x1C  dword    ByteRate       sample rate from SDT format * 2  (Sample Rate * BitsPerSample * Channels) / 8.
        f.u16(sampleSize * channelCount)                 # 0x20  word     BlockAlign     2
        f.u16(sampleSize * 8)                            # 0x22  word     BitsPerSample  16
        f.write(b'data')                                 # 0x24  char[4]  Subchunk2ID    "data"
        f.u32(pcmDataSize)                               # 0x28  dword    Sunchunk2Size  size from SDT format
        f.write(pcmData)                                 # 0x2C  -        Data           raw SFX data

        f.save(filePath)


# https://en.wikipedia.org/wiki/UTF-8#Encoding
def toUTF8 (string):
    buff = bytearray()

    for char in string:
        code = ord(char)

        if code <= 0x7F:
            buff.append(code)
        elif code <= 0x7FF:
            buff.append(0xC0 | ((code >> 6) & 31))
            buff.append(0x80 | (code & 63))
        elif code <= 0xFFFF:
            buff.append(0xE0 | ((code >> 12) & 15))
            buff.append(0x80 | ((code >> 6) & 63))
            buff.append(0x80 | (code & 63))
        elif code <= 0x10FFFF:
            buff.append(0xF0 | ((code >> 18) & 7))
            buff.append(0x80 | ((code >> 12) & 63))
            buff.append(0x80 | ((code >> 6) & 63))
            buff.append(0x80 | (code & 63))
        else:
            raise Exception('Code point is too big')

    return bytes(buff)

def fromUTF8 (byteSeq):
    chars  = []
    count  = len(byteSeq)
    cursor = 0

    while cursor < count:
        a = byteSeq[cursor]

        if (a & 0xF8) == 0xF0:
            if (count - cursor) < 4:
                raise Exception('Failed to decode')

            b = byteSeq[cursor + 1]
            c = byteSeq[cursor + 2]
            d = byteSeq[cursor + 3]

            if not (b & 0xC0 == c & 0xC0 == d & 0xC0 == 0x80):
                raise Exception('Invalid secondary bytes')

            code = ((a & 7) << 18) | ((b & 63) << 12) | ((c & 63) << 6) | (d & 63)
            cursor += 4

        elif (a & 0xF0) == 0xE0:
            if (count - cursor) < 3:
                raise Exception('Failed to decode')

            b = byteSeq[cursor + 1]
            c = byteSeq[cursor + 2]

            if not (b & 0xC0 == c & 0xC0 == 0x80):
                raise Exception('Invalid secondary bytes')

            code = ((a & 15) << 12) | ((b & 63) << 6) | (c & 63)
            cursor += 3

        elif (a & 0xE0) == 0xC0:
            if (count - cursor) < 2:
                raise Exception('Failed to decode')

            b = byteSeq[cursor + 1]

            if (b & 0xC0) != 0x80:
                raise Exception('Invalid secondary bytes') 

            code = ((a & 31) << 6) | (b & 63)
            cursor += 2

        elif (a & 0x80) == 0:
            code = a
            cursor += 1
        else:
            raise Exception('Invalid start byte')

        chars.append(chr(code))

    return ''.join(chars)

def decode1251 (string):
    table = {
        128: 1026,
        129: 1027,
        130: 8218,
        131: 1107,
        132: 8222,
        133: 8230,
        134: 8224,
        135: 8225,
        136: 8364,
        137: 8240,
        138: 1033,
        139: 8249,
        140: 1034,
        141: 1036,
        142: 1035,
        143: 1039,
        144: 1106,
        145: 8216,
        146: 8217,
        147: 8220,
        148: 8221,
        149: 8226,
        150: 8211,
        151: 8212,
        153: 8482,
        154: 1113,
        155: 8250,
        156: 1114,
        157: 1116,
        158: 1115,
        159: 1119,
        161: 1038,
        162: 1118,
        163: 1032,
        165: 1168,
        168: 1025,
        170: 1028,
        175: 1031,
        178: 1030,
        179: 1110,
        180: 1169,
        184: 1105,
        185: 8470,
        186: 1108,
        188: 1112,
        189: 1029,
        190: 1109,
        191: 1111,    
    }

    output = []

    for code in string:
        if code == 152:
            continue

        if code >= 192:
            code += 848
        elif code >= 128:
            code = table.get(code, code)

        output.append(chr(code))

    return ''.join(output)

def decode1252 (string):
    table = {
        128: 8364,
        129: None,
        130: 8218,
        131: 402,
        132: 8222,
        133: 8230,
        134: 8224,
        135: 8225,
        136: 710,
        137: 8240,
        138: 352,
        139: 8249,
        140: 338,
        141: None,
        142: 381,
        143: None,
        144: None,
        145: 8216,
        146: 8217,
        147: 8220,
        148: 8221,
        149: 8226,
        150: 8211,
        151: 8212,
        152: 732,
        153: 8482,
        154: 353,
        155: 8250,
        156: 339,
        157: None,
        158: 382,
        159: 376,
    }

    output = []

    for code in string:
        if 128 <= code < 160:
            code = table.get(code)

            if code is None:
                continue

        output.append(chr(code))

    return ''.join(output)






def __test__ ():
    print(bin(clearBit(0b1010, 0b11100))[2:])
    print(formatByteString(b'ID\xFFSQ'))
    print(joinPath(r'\\/abc\\/\\', r'\\/def\\/\\', r'\\/ghr\\/\\'))
    print(formatHex((99931).to_bytes(4, 'little')))
    print(getDrives())

    a = []
    b = zeroPad([], bound=4)

    assert a == b and a is not b

    print(zeroPad(bytearray(b'x'), bound=4))

    print(toUTF8('Привет - russian, € - euro, 你好 - chinese, नमस्ते - hindi, $ £ И ह € 한 𐍈').decode('utf-8'))
    print(fromUTF8(toUTF8('Привет - russian, € - euro, 你好 - chinese, नमस्ते - hindi, $ £ И ह € 한 𐍈')))

    print(decode1251(bytearray([ i for i in range(256) ])))
    print(decode1252(bytearray([ i for i in range(256) ])))
    print(formatFloat(1.234567890))



__all__ = [
    'sleep',
    'deepCopy',
    'copyFile',
    'createNamedTuple',
    'rename',
    'getDrive',
    'joinPath',
    'isFile',
    'isDir',
    'isAbsPath',
    'checkPathExists',
    'splitExt',
    'splitDrive',
    'getAbsPath',
    'getNormPath',
    'getRelPath',
    'getBaseName',
    'getDirPath',
    'getFileSize',
    'areSamePaths',
    'expandPathVars',
    'PATH_SEP',
    'ByteOrder',
    'SeekFrom',
    # 'print',
    'printS',
    'printW',
    'printE',
    'die',
    'pjp',
    'pjpd',
    'pji',
    'splitSpaces',
    'iterFiles',
    'findAncestorDirByFile',
    'findFileInEnv',
    'PathInfo',
    'parsePath',
    'getScriptDir',
    'getExt',
    'dropExt',
    'replaceExt',
    'replaceBaseName',
    'replaceFileName',
    'getFileName',
    'createDirs',
    'createFileDirs',
    'removeDirs',
    'removeFile',
    'getPathModTime',
    'getPathCreateTime',
    'parseJson',
    'parseJsonSafe',
    'toJson',
    'readJson',
    'readJsonSafe',
    'readBin',
    'readText',
    'readLines',
    'writeJson',
    'writeText',
    'writeBin',
    'compressData',
    'decompressData',
    'decompressFile',
    'decompressGzipFile',
    'decompressGzip',
    'calcCRC32',
    'calcMD5',
    'createUUID',
    'align',
    'isPow2',
    'clamp',
    'zeroPad',
    'getType',
    'isStr',
    'isInt',
    'isFloat',
    'isNum',
    'isDict',
    'isList',
    'createDoubleMap',
    'addUnique',
    'concatLists',
    'Array',
    # 'TArrayType',
    'fromTimestamp',
    'formatTimestamp',
    'formatSize',
    'formatHex',
    'formatBytes',
    'formatByteString',
    'getStrTerm',
    'readStruct',
    'readString',
    'readAlignedString',
    'findPattern',
    'checkReadOnly',
    'setReadOnly',
    'getBits',
    'splitBits',
    'setBit',
    'clearBit',
    'isBitSet',
    'xorBuffer',
    'getDrives',
    'addEnvPath',
    'getTimestamp',
    'saveAsWave',
]



if __name__ == '__main__':
    __test__()