# Syberia 2 Tools

import sys

sys.path.insert(0, r'C:\Projects\PythonLib\python\v001')

from bfw.utils import *
from bfw.reader import *
from bfw.types.enums import Enum2



GAME_DIR = r'G:\Steam\steamapps\common\Syberia 2'

SYB_SIGNATURE = b'VXBG'
NMO_SIGNATURE = b'Nemo Fi\x00'



class MetaItem:
    def __init__ (self):
        self.name = None
        self.size = None


def unpackSyb (filePath, unpackDir=None):
    filePath = getAbsPath(filePath)

    if not isFile(filePath):
        raise Exception(f'File is not found: { filePath }')

    if not unpackDir:
        unpackDir = filePath + '.unpacked'

    with openFile(filePath) as f:
        signature = f.read(4)

        assert signature == SYB_SIGNATURE

        metaSize = f.u32()
        metaEnd  = metaSize + 8

        items = []

        while f.tell() < metaEnd:
            item = MetaItem()

            items.append(item)

            item.name = f.string()
            item.size = f.u32()

        createDirs(unpackDir)

        for item in items:
            data = f.read(item.size)

            itemPath = joinPath(unpackDir, item.name)

            writeBin(itemPath, data)

        assert not f.remaining()


def unpackNmo (filePath, unpackDir=None):
    filePath = getAbsPath(filePath)

    if not isFile(filePath):
        raise Exception(f'File is not found: { filePath }')

    if not unpackDir:
        unpackDir = filePath + '.unpacked'

    with openFile(filePath) as f:
        signature = f.read(8)

        assert signature == NMO_SIGNATURE

        unk1           = f.u32()  # CRC???
        unk2           = f.u32()  # always 84418562
        unk3           = f.u32()  # always 8
        unk4           = f.u32()  # always 0
        unk5           = f.u32()  # always 0 or 8
        metaSize       = f.u32()  #
        compDataSize   = f.u32()  #
        decompDataSize = f.u32()  #
        unk9           = f.u32()  # always 1
        unk10          = f.u32()  # 2, 56, 1, 62, 61, 81, 63, 59, 60, 58, 83...
        unk11          = f.u32()  # 8319
        unk12          = f.u32()  # always 0
        unk13          = f.u32()  # 33882160
        unk14          = f.u32()  # 56

        meta = f.read(metaSize)

        data = f.read(compDataSize)

        isMetaCompressed = meta[:2] == b'\x78\x5E'
        isDataCompressed = data[:2] == b'\x78\x5E'
        # data = decompressData(data)

        assert unk2 == 84418562
        assert unk3 == 8, unk3
        assert unk4 == 0, unk4
        assert unk5 in [ 0, 8 ], unk5
        assert unk12 in [ 0 ], unk12
        assert unk13 in [ 33882160, 33882112 ], unk13

        '''
        isMetaCompressed = True
        isDataCompressed = True
        unk9  = 1
        unk10 = 2
        unk11 = 8322 (0b10000010000010)
        unk12 = 0
        unk14 = 56

        isMetaCompressed = False
        isDataCompressed = True
        unk9  = 1
        unk10 = 1
        unk11 = 8324 (0b10000010000100)
        unk12 = 0
        unk14 = 40

        isMetaCompressed = False
        isDataCompressed = False
        unk9  = 1
        unk10 = 35
        unk11 = 83   (0b00000001010011)
        unk12 = 0
        unk14 = 1012

        '''

        # print(unk1)
        # print(unk2)
        # print(unk3)
        # print(unk4)
        # print(unk5)
        # print(metaSize)
        # print(compDataSize)
        # print(decompDataSize)
        print(f'isMetaCompressed = { isMetaCompressed }')
        print(f'isDataCompressed = { isDataCompressed }')
        print(f'unk9  = { unk9 }')
        print(f'unk10 = { unk10 }')
        print(f'unk11 = { unk11 }')
        print(f'unk12 = { unk12 }')
        print(f'unk14 = { unk14 }')

        # assert len(data) == decompDataSize

        # exit()





def unpackAllSyb ():
    for filePath in iterFiles(GAME_DIR, True, [ '.syb' ]):
        print(filePath)

        unpackSyb(filePath)

        print(' ')


def unpackAllNmo ():
    for filePath in iterFiles(GAME_DIR, True, [ '.nmo' ]):
        print(filePath)

        unpackNmo(filePath)

        print(' ')


def main ():
    # unpackAllSyb()
    unpackAllNmo()




if __name__ == '__main__':
    main()
