# Fahrenheit Tools

import sys

sys.path.insert(0, r'C:\Projects\PythonLib\python\v001')

from bfw.utils import *
from bfw.reader import *
from bfw.types.enums import Enum



GAME_DIR = r'G:\Games\Fahrenheit'

IDM_SIGNATURE = b'QUANTICDREAMTABIDMEM'



def unpack (filePath, unpackDir=None):
    filePath = getAbsPath(filePath)

    if not isFile(filePath):
        raise Exception(f'File is not found: { filePath }')

    if not unpackDir:
        unpackDir = filePath + '.unpacked'

    # createDirs(unpackDir)

    with openFile(filePath) as f:
        pass

    # exit()

def unpackAll (gameDir, unpackDir=None):
    for filePath in iterFiles(gameDir, True, [ '.dat', '.d01', '.d02', '.d03' ]):
        print(filePath)

        unpack(filePath, unpackDir)

        print(' ')


def unpackIDM (filePath):
    filePath = getAbsPath(filePath)

    if not isFile(filePath):
        raise Exception(f'File is not found: { filePath }')

    with openFile(filePath) as f:
        signature = f.read(len(IDM_SIGNATURE))

        assert signature == IDM_SIGNATURE, signature

        while f.tell() < 112:
            print(f.u32())


def main ():
    # unpackAll(GAME_DIR, joinPath(GAME_DIR, '.unpacked'))
    unpackIDM(joinPath(GAME_DIR, 'BigFile_PC.idm'))



if __name__ == '__main__':
    main()
