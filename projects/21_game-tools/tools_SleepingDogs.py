# Sleeping Dogs Tools

import sys
import regex

sys.path.insert(0, r'C:\Projects\PythonLib\python\v001')

from bfw.utils import *
from bfw.reader import *



GAME_DIR = r'G:\Steam\steamapps\common\SleepingDogsDefinitiveEdition'

BIX_SIGNATURE = b'\xA8\x40\x5C\x2C'



def unpack (bixPath, unpackDir):    
    bixPath = getAbsPath(bixPath)

    print('Unpacking', bixPath)

    if not isFile(bixPath):
        raise Exception(f'File is not found: { bixPath }')

    with openFile(bixPath) as f:
        sinature = f.read(4)

        if sinature != BIX_SIGNATURE:
            raise Exception('Unknown file signature')

        size1 = f.u32()
        size2 = f.u32()

        assert size1 == size2
        assert f.getSize() == (16 + size1)

        zeros1 = f.u32(7)

        assert zeros1 == [ 0, 0, 0, 0, 0, 0, 0 ]

        unk1 = f.u32()

        print(unk1)

        zeros2 = f.u32(5)

        assert zeros2 == [ 0, 0, 0, 0, 0 ]

        unk2 = f.u32()

        assert unk2 == 719815929

        print(unk2)

        f.seek(160)

        while f.remaining():
            x = f.u32()
            print(x)
        

    print(' ')
    # exit()


def unpackAll (rootDir, unpackDir):
    for filePath in iterFiles(rootDir, True, [ '.bix' ]):
        unpack(filePath, unpackDir)


if __name__ == '__main__':
    # unpackAll(GAME_DIR, joinPath(GAME_DIR, '.unpacked'))
    unpack(joinPath(GAME_DIR, 'Global.bix'), joinPath(GAME_DIR, '.unpacked'))