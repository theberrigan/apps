# Worms Ultimate Mayhem Tools

import sys

sys.path.insert(0, r'C:\Projects\PythonLib\python\v001')

from bfw.utils import *
from bfw.reader import *
from bfw.types.enums import Enum2



GAME_DIR = r'G:\Steam\steamapps\common\WormsXHD'
SAVE_DIR = r'G:\Steam\userdata\108850163\70600\remote'

XOM_SIGNATURE = b'MOIK'


def unpackXOM (filePath, unpackDir=None):    
    filePath = getAbsPath(filePath)

    if not isFile(filePath):
        raise Exception(f'File is not found: { filePath }')

    if not unpackDir:
        unpackDir = filePath + '.unpacked'

    # createDirs(unpackDir)

    with openFile(filePath) as f:
        signature = f.read(4)

        assert signature == XOM_SIGNATURE

        unk1   = f.u32()  # version?
        zeros1 = f.read(16)

        assert unk1 == 0x2000000, unk1
        assert zeros1 == (b'\x00' * len(zeros1)), zeros1

        typeCount = f.u32()
        contCount = f.u32()
        unk3      = f.u32()  # sometimes equals to contCount
        zeros2    = f.read(28)

        assert zeros2 == (b'\x00' * len(zeros2)), zeros2

        print(typeCount, contCount, unk3)

        for i in range(typeCount):
            key = f.string(4)

            assert key == 'TYPE'

            unk4  = f.u32()
            unk5  = f.u32()
            zero1 = f.u32()
            guid  = f.read(16)  # ?

            assert zero1 == 0

            name = f.string(32)

            print(unk4, unk5, name)

        key = f.read(4)

        assert key == b'GUID'

        zeros3 = f.read(12)

        assert zeros3 == (b'\x00' * len(zeros3)), zeros3

        key = f.read(4)

        assert key == b'SCHM'

        always1 = f.u32()

        assert always1 == 1, always1

        zeros4 = f.read(8)

        assert zeros4 == (b'\x00' * len(zeros4)), zeros4

        key = f.read(4)

        assert key == b'STRS'

        strCount = f.u32()
        strSize  = f.u32()

        strOffsets = [ None ] * strCount
        strings    = [ None ] * strCount

        for i in range(strCount):
            strOffsets[i] = f.u32()

        strStart = f.tell()

        for i in range(strCount):
            f.seek(strStart + strOffsets[i])

            strings[i] = f.string()

            print(strings[i])

        f.seek(strStart + strSize)




    # exit()


def unpackXOMs ():
    for rootDir in [
        # GAME_DIR,
        SAVE_DIR
    ]:
        for filePath in iterFiles(rootDir, True, [ '.xom' ]):
            print(filePath)

            unpackXOM(filePath)

            print(' ')



def main ():
    unpackXOMs()



if __name__ == '__main__':
    main()
