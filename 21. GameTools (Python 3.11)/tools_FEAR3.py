# F.E.A.R. 3 Tools

import sys

sys.path.insert(0, r'C:\Projects\PythonLib\python\v001')

from bfw.utils import *
from bfw.reader import *
from bfw.types.enums import Enum2



GAME_DIR = r'G:\Steam\steamapps\common\F.E.A.R. 3'

DSPACK_SIGNATURE_LE = b'mgf \x08\x01ZZ'
DSPACK_SIGNATURE_BE = b' fgmZZ\x01\x08'



def unpackArch (filePath, unpackDir=None):    
    filePath = getAbsPath(filePath)

    if not isFile(filePath):
        raise Exception(f'File is not found: { filePath }')

    if not unpackDir:
        unpackDir = filePath + '.unpacked'

    # 2430
    # 51305
    with openFile(filePath) as f:
        signature = f.read(8)

        if signature == DSPACK_SIGNATURE_BE:
            f.setByteOrder(ByteOrder.Big)
        elif signature != DSPACK_SIGNATURE_LE:
            raise Exception('Unknown signature')

        zeros1 = f.u32()

        assert zeros1 == 0

        itemCount  = f.u32()
        unkSize1    = f.u32()
        unkOffset1 = f.u32()
        unk4       = f.u32()
        unkSize2   = f.u32()
        unkOffset2 = f.u32()
        strSize    = f.u32()
        strOffset  = f.u32()
        unk9       = f.u32()
        unk10      = f.u32()
        unk11      = f.u32()
        unk12      = f.u32()
        unk13      = f.u32()
        unk14      = f.u32()
        unk15      = f.u32()

        print(f'itemCount:{itemCount}', f'unkSize1:{unkSize1}', f'unkOffset1:{unkOffset1}', unk4, f'unkSize2:{unkSize2}', f'unkOffset2:{unkOffset2}', f'strSize:{ strSize }', f'strOffset:{strOffset}', unk9, unk10, unk11, unk12, unk13, unk14, unk15)

        f.seek(unkOffset1)

        for i in range(itemCount):
            unk16 = f.u32()
            unk17 = f.u32()
            unk18 = f.u32()
            unk19 = f.u32()
            unk20 = f.u32()
            unk21 = f.u32()

            print(unk16, unk17, unk18, unk19, unk20, unk21)

        print(f.tell())



        r'''
        G:\Steam\steamapps\common\F.E.A.R. 3\resources\Audio.dsPack
        2813 67512 104816 123 2952 101856 72523 172336 0 32768 8 32768 0 4095 123
         
        G:\Steam\steamapps\common\F.E.A.R. 3\resources\Boot.dsPack
        2464 59136 112560 571 13704 98848 51316 171696 0 32768 34 32768 0 4095 571
         
        G:\Steam\steamapps\common\F.E.A.R. 3\resources\DLC_MP1.dsPack
        668 16032 53648 132 3168 50480 19100 69680 0 32768 34 32768 0 4095 132
         
        G:\Steam\steamapps\common\F.E.A.R. 3\resources\DLC_MP2.dsPack
        832 19968 59216 177 4248 54960 20553 79184 0 32768 34 32768 0 4095 177
         
        G:\Steam\steamapps\common\F.E.A.R. 3\resources\Patch.dsPack
        40 960 35408 44 1056 34352 1158 36368 0 32768 34 32768 0 4095 44
         
        G:\Steam\steamapps\common\F.E.A.R. 3\resources\Preloads.dsPack
        557 13368 57216 305 7320 49888 11800 70592 0 32768 34 32768 0 4095 305
         
        G:\Steam\steamapps\common\F.E.A.R. 3\resources\Resource.dsPack
        30853 740472 959024 5158 123792 835232 862342 1699504 0 32768 34 32768 0 4095 5158
         
        G:\Steam\steamapps\common\F.E.A.R. 3\resources\Localized\Audio\English.dsPack
        2450 58800 92960 36 864 92096 67754 151760 0 32768 8 32768 0 4095 36
        '''
        


def unpackAll ():
    for filePath in iterFiles(GAME_DIR, True, [ '.dsPack' ]):
        print(filePath)

        unpackArch(filePath)

        print(' ')



def main ():    
    # unpackAll()
    unpackArch(joinPath(GAME_DIR, 'resources', 'Boot.dsPack'))



if __name__ == '__main__':
    main()
