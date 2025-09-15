# https://www.daubnet.com/en/file-format-ico
# https://www.daubnet.com/en/file-format-cur
# https://en.wikipedia.org/wiki/ICO_(file_format)
# https://docs.fileformat.com/image/ico/

import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../..'))) 

from bfw.utils import *
from bfw.reader import *



SCRIPT_DIR  = getDirPath(getAbsPath(__file__))
SAMPLES_DIR = getAbsPath(joinPath(SCRIPT_DIR, 'samples', 'ico_and_cur'))



class ContainerType:
    Ico = 1
    Cur = 2

    @classmethod
    def isValid (cls, value):
        return value in [ cls.Ico, cls.Cur ]


def unpack (filePath):
    print(getBaseName(filePath))

    with openFile(filePath) as f:
        always0  = f.u16()
        fileType = f.u16()

        assert not always0
        assert ContainerType.isValid(fileType)

        isIco = fileType == ContainerType.Ico
        imgCount = f.u16()

        for i in range(imgCount):
            width  = f.u8() or 256
            height = f.u8() or 256

            # colors in palette
            colorCount = f.u8()
            hasPalette = colorCount > 0
            always0    = f.u8()

            # assert not always0

            if always0:
                print('Invalid 3!')
                return

            tmp1 = f.u16()
            tmp2 = f.u16()

            if isIco:
                if tmp1 not in [ 0, 1 ]:
                    print('Invalid 4!')
                    return

                print(f'{ width }x{ height }; { colorCount } colors; { tmp1 } planes; { tmp2 }bpp')
            else:
                print(f'{ width }x{ height }; { colorCount } colors; hs-x: { tmp1 }; hs-y: { tmp2 }')

            dataSize   = f.u32()
            dataOffset = f.u32()



    print(' ')

def unpackSamples ():
    for filePath in iterFiles(SAMPLES_DIR, False, [ '.ico', '.cur' ]):
        unpack(filePath)

def collectSamples ():
    knownIcons = {}

    for drive in getDrives():
        for srcPath in iterFiles(f'{ drive }:\\', True, [ '.ico', '.cur' ]):
            fileSize = getFileSize(srcPath)

            if fileSize < 4 or fileSize > (2 * 1024 * 1024):
                continue

            fileExt = getExt(srcPath)

            with openFile(srcPath) as f:
                always0  = f.u16()
                fileType = f.u16()

                if always0 != 0 or \
                   not ContainerType.isValid(fileType) or \
                   fileExt == '.ico' and fileType != ContainerType.Ico or \
                   fileExt == '.cur' and fileType != ContainerType.Cur:
                    continue

            fileData = readBin(srcPath)
            fileCRC  = calcCRC32(fileData)

            if fileCRC in knownIcons:
                continue

            knownIcons[fileCRC] = True

            dstName = getFileName(srcPath)
            dstName = f'{dstName}.{fileCRC:08X}{fileExt}' 
            dstPath = joinPath(SAMPLES_DIR, dstName)

            print(srcPath, dstPath)

            writeBin(dstPath, fileData)


if __name__ == '__main__':
    # collectSamples()
    unpackSamples()