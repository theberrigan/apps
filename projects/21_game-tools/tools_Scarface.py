# Scarface Tools

import sys
import regex

sys.path.insert(0, r'C:\Projects\PythonLib\python\v001')

from bfw.utils import *
from bfw.reader import *



GAME_DIR = r'G:\Games\Scarface'

RCF_SIGNATURE = b'ATG CORE CEMENT LIBRARY\x00\x00\x00\x00\x00\x00\x00\x00\x00'


def readRCF (f, unpackDir, isNested=False):
    sinature = f.read(32)

    if sinature != RCF_SIGNATURE:
        raise Exception('Unknown file signature')

    unk1 = f.u32()

    assert unk1 == 16777474

    offset1 = f.u32()
    size1   = f.u32()

    offset2 = f.u32()
    size2   = f.u32()  # offset to toc

    unk2 = f.u32()

    assert unk2 == 0

    itemCount = f.u32()

    assert size1 % itemCount == 0

    f.seek(offset1)

    items = [ None ] * itemCount

    for i in range(itemCount):
        n1     = f.u32()
        offset = f.u32()
        size   = f.u32()

        items[i] = [n1, offset, size, None, None]

    assert (offset1 + size1) == f.tell()

    items.sort(key = lambda item: item[1])
       
    f.seek(offset2)

    unk3 = f.u32()

    assert unk3 == 2048

    unk4 = f.u32()

    assert unk4 == 0

    for i in range(itemCount):
        unk5 = f.u32()
        unk6 = f.u32()  # 2048
        unk7 = f.u32()  # 0

        assert unk6 == 2048
        assert unk7 == 0

        strSize = f.u32()
        itemPath = f.string(size=strSize)
        unk7 = f.read(3)

        assert unk7 == b'\x00\x00\x00'

        items[i][3] = unk5
        items[i][4] = itemPath

        # print(unk5, itemPath)

    assert (offset2 + size2) == f.tell()

    for n1, offset, size, unk5, itemPath in items:
        if isNested:
            print('   ', n1, unk5, itemPath)
        else:
            print(n1, offset, size, unk5, itemPath)

        f.seek(offset)

        data = f.read(size)

        if itemPath.lower().endswith('.rcf'):
            with MemReader(data, itemPath) as f2:
                readRCF(f2, unpackDir, True)
        else:
            itemPath = getAbsPath(joinPath(unpackDir, itemPath))

            createFileDirs(itemPath)

            writeBin(itemPath, data)

def unpack (rcfPath, unpackDir):    
    rcfPath = getAbsPath(rcfPath)

    print('Unpacking', rcfPath)

    if not isFile(rcfPath):
        raise Exception(f'File is not found: { rcfPath }')

    with openFile(rcfPath) as f:
        readRCF(f, unpackDir)

    print(' ')
    # exit()


def unpackAll (rootDir, unpackDir):
    for filePath in iterFiles(rootDir, True, [ '.rcf' ]):
        unpack(filePath, unpackDir)


if __name__ == '__main__':
    unpackAll(GAME_DIR, joinPath(GAME_DIR, '.unpacked'))
    # unpack(joinPath(GAME_DIR, 'cement.rcf'), joinPath(GAME_DIR, '.unpacked'))