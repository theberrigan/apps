import os
import sys
import struct

from math import ceil
from zlib import crc32

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../..'))) 

from bfw.utils import *
from bfw.reader import *



MAX_CRC_CHUNK = 10 * 1024 * 1024
GLOBAL_SAMPLES_DIR = r'C:\Projects\_Data_Samples'



def collectSamplesInDir (rootDirs, destDir, exts, isRecursive=True, minSize=None, maxSize=None, noDups=True, addCRCSuffix=False, checkFn=None):
    isCRCNeeded  = noDups or addCRCSuffix
    isSizeNeeded = isCRCNeeded or minSize is not None or maxSize is not None

    knownFiles = {}

    destDir = getAbsPath(destDir)

    createDirs(destDir)

    if isinstance(rootDirs, str):
        rootDirs = [ rootDirs ]

    for rootDir in rootDirs:
        rootDir = getAbsPath(rootDir)

        for srcPath in iterFiles(rootDir, isRecursive, exts):
            if isSizeNeeded:
                fileSize = getFileSize(srcPath)
            else:
                fileSize = None

            if minSize is not None and fileSize < minSize or \
               maxSize is not None and fileSize > maxSize:
                continue

            fileCRC = None

            if isCRCNeeded:
                if fileSize <= MAX_CRC_CHUNK:
                    fileCRC = crc32(readBin(srcPath))
                else:
                    fileCRC = 0

                    with open(srcPath, 'rb') as f:
                        for _ in range(ceil(fileSize / MAX_CRC_CHUNK)):
                            fileCRC = crc32(f.read(MAX_CRC_CHUNK), fileCRC)

            if noDups:
                if fileCRC in knownFiles:
                    continue

                knownFiles[fileCRC] = True

            if addCRCSuffix:
                fileName, fileExt = splitExt(getBaseName(srcPath))

                fileName = f'{ fileName }.{fileCRC:08X}{ fileExt }'
            else:
                fileName = getBaseName(srcPath)

            dstPath = joinPath(destDir, fileName)

            if checkFn and checkFn(srcPath, fileSize, fileCRC) == False:
                continue

            # print(srcPath, dstPath)

            copyFile(srcPath, dstPath)

def collectSamplesInFile (rootDirs, destPath, exts, isRecursive=True, minSize=None, maxSize=None, noDups=True, checkFn=None):
    if isinstance(rootDirs, str):
        rootDirs = [ rootDirs ]

    destPath = getAbsPath(destPath)

    createFileDirs(destPath)

    dups  = {}
    count = 0

    with open(destPath, 'wb') as f:
        f.write(struct.pack('<Q', 0))

        for rootDir in rootDirs:
            for filePath in iterFiles(rootDir, isRecursive, exts):
                fileSize = getFileSize(filePath)

                if minSize is not None and fileSize < minSize or \
                   maxSize is not None and fileSize > maxSize:
                    continue

                fileCRC = 0

                if fileSize <= MAX_CRC_CHUNK:
                    fileCRC = crc32(readBin(filePath))
                else:
                    with open(filePath, 'rb') as f2:
                        for _ in range(ceil(fileSize / MAX_CRC_CHUNK)):
                            fileCRC = crc32(f2.read(MAX_CRC_CHUNK), fileCRC)

                if noDups:
                    if fileCRC in dups:
                        continue

                    dups[fileCRC] = True

                if checkFn and checkFn(filePath, fileSize, fileCRC) == False:
                    continue

                filePath = filePath.encode('utf-8')

                # f.write(struct.pack('<I', fileCRC))
                f.write(struct.pack('<I', len(filePath)))
                f.write(filePath)

                count += 1

        f.seek(0)

        f.write(struct.pack('<Q', count))

def iterSamplesInFile (binPath):
    binPath = getAbsPath(binPath)

    if not isFile(binPath):
        raise Exception(f'File does not exist: { binPath }')

    with open(binPath, 'rb') as f:
        count = readStruct('<Q', f)

        for _ in range(count):
            pathSize = readStruct('<I', f)
            filePath = f.read(pathSize).decode('utf-8')

            if isFile(filePath):
                yield filePath


################################################
####                TESTING                 ####
################################################

def _checkSample (filePath, fileSize, fileCRC):
    print(filePath, fileSize, fileCRC)

    return True

def _test_collectSamplesInDir_ ():
    collectSamplesInDir(
        rootDirs     = r'C:\Projects\_Data_Samples\dds',
        destDir      = r'C:\Projects\_Data_Samples\.trash',
        exts         = [ '.dds' ],
        isRecursive  = True, 
        minSize      = 600,
        maxSize      = 2 ** 32,
        addCRCSuffix = True,
        checkFn      = _checkSample
    )

def _test_collectSamplesInFile_ ():
    collectSamplesInFile(
        rootDirs    = getDrives(True),
        destPath    = joinPath(GLOBAL_SAMPLES_DIR, 'bmps.bin'),
        exts        = [ '.bmp' ],
        isRecursive = True,
        minSize     = 1,
        maxSize     = None,
        noDups      = True,
        checkFn     = _checkSample
    )

def _test_iterSamplesInFile_ ():
    for filePath in iterSamplesInFile(joinPath(GLOBAL_SAMPLES_DIR, 'bmps.bin')):
        print(filePath)

def _test_ ():
    # _test_collectSamplesInDir_()
    # _test_collectSamplesInFile_()
    _test_iterSamplesInFile_()


################################################
####                 EXPORT                 ####
################################################

__all__ = [
    'GLOBAL_SAMPLES_DIR',
    'collectSamplesInDir',
    'collectSamplesInFile',
    'iterSamplesInFile',
]



if __name__ == '__main__':
    _test_()