# Call of Duty World at War Tools

import sys

sys.path.insert(0, r'C:\Projects\PythonLib\python\v001')

from bfw.utils import *
from bfw.reader import *
from bfw.types.enums import Enum2



GAME_DIR = r'G:\Games\Call of Duty - World at War'
FF_SIGNATURE = b'IWffu100'



def unpack (filePath, unpackDir=None):    
    filePath = getAbsPath(filePath)

    if not isFile(filePath):
        raise Exception(f'File is not found: { filePath }')

    if not unpackDir:
        unpackDir = filePath + '.unpacked'

    # createDirs(unpackDir)

    with openFile(filePath) as f:
        signature = f.read(len(FF_SIGNATURE))

        if signature != FF_SIGNATURE:
            raise Exception('Wrong signature')

        unk1 = f.u32()

        assert unk1 == 387, unk1

        data = f.read()
        data = decompressData(data)

        # writeBin(filePath + '.bin', data)
        # sys.exit()
        # 1140
        # 4560

    with MemReader(data) as f:
        dataSize = f.u32()

        unks = f.u32(8)

        itemCount = f.u32()

        for i in unks:
            print(i)

        print(':', itemCount, itemCount * 4)


    # exit()

def unpackAll (gameDir, unpackDir=None):
    for filePath in iterFiles(gameDir, True, [ '.ff' ]):
        print(filePath)

        unpack(filePath, unpackDir)

        print(' ')

def main ():
    unpackAll(GAME_DIR, joinPath(GAME_DIR, '.unpacked'))
    # unpack(joinPath(GAME_DIR, 'zone', 'Russian', 'ber1_load.ff'))



if __name__ == '__main__':
    main()
