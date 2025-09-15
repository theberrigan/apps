from utils import *
from reader import *
from steam import *


FNV_APP_ID = 22490
FNV_BASE_DIR_NAME = 'Fallout New Vegas'

RF_SIGNATURE = b'TES4'



def findFNVDir ():
    return findGameDir(FNV_APP_ID, [ FNV_BASE_DIR_NAME ])


def readRecordFile (espPath):
    print(espPath)

    with openFile(espPath) as f:
        signature = f.read(4)

        if signature != RF_SIGNATURE:
            print('Unknown ESP signature')
            return

        headerSize = f.u32()
        flags = f.u8()

        f.skip(11)

        formVer = f.u32()

        print(headerSize, flags, formVer)

        print('Ok')

def main ():
    gameDir = findFNVDir()

    if not gameDir:
        print('Game dir is not found')
        return

    dataDir = joinPath(gameDir, 'steam_eng', 'Data')

    for filePath in iterFiles(dataDir, False, includeExts=[ '.esp' ]):
        readRecordFile(filePath)


if __name__ == '__main__':
    main()
