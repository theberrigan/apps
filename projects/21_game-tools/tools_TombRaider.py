# Tomb Raider (2013) Tools

import sys

sys.path.insert(0, r'C:\Projects\PythonLib\python\v001')

from bfw.utils import *
from bfw.reader import *
from bfw.types.enums import Enum2



GAME_DIR = r'G:\Steam\steamapps\common\Tomb Raider'



def unpack (filePath, unpackDir):    
    filePath = getAbsPath(filePath)

    if not isFile(filePath):
        raise Exception(f'File is not found: { filePath }')

    with openFile(filePath) as f:
        signature = f.read(4)

        if signature != b'TAFS':
            raise Exception('Wrong signature')

        unk1 = f.u32()
        unk2 = f.u32()

        assert unk1 == 3
        assert unk2 == 4

        itemCount = f.u32()

        unk3  = f.u32()
        unk4  = f.read(4)
        unk5  = f.u32()
        unk6  = f.u32()
        unk7  = f.u32()
        unk8  = f.u32()
        unk9  = f.u32()
        unk10 = f.u32()
        unk11 = f.u32()

        assert unk3 == 0
        assert unk4 == b'pc-w'
        assert unk5 == 0
        assert unk6 == 0
        assert unk7 == 0
        assert unk8 == 0
        assert unk9 == 0
        assert unk10 == 0
        assert unk11 == 0

        for i in range(itemCount):
            unk12  = f.u32()
            unk13  = f.u32()
            size   = f.u32()
            offset = f.u32()

            assert unk13 == 0xFFFFFFFF

            index = offset & 0xFF

            offset = offset & 0xFFFFFF00

            print(index, offset, size, unk12, unk13)

            # 171885 - size of 0 item
            # 195777

            # 55296


    # exit()

def unpackAll (gameDir, unpackDir):
    for filePath in iterFiles(gameDir, True, [ '.tiger' ]):
        print(filePath)

        unpack(filePath, unpackDir)

        print(' ')

def main ():
    # unpackAll(GAME_DIR, joinPath(GAME_DIR, '.unpacked'))
    unpack(joinPath(GAME_DIR, 'bigfile.000.tiger'), joinPath(GAME_DIR, '.unpacked'))


if __name__ == '__main__':
    main()
