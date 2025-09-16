# Still Life 2 Tools

import sys

sys.path.insert(0, r'C:\Projects\PythonLib\python\v001')

from bfw.utils import *
from bfw.reader import *
from bfw.types.enums import Enum2



GAME_DIR = r'G:\Steam\steamapps\common\Still life 2'

DAT_KEY = bytes.fromhex('29 23 BE 84 E1 6C D6 AE 52 90 49 F1 F1 BB E9 EB')

DAT_SIGNATURE = b'GMGB'



class ItemMeta:
    def __init__ (self):
        self.path = None
        self.size = None


def unpackPak (filePath, unpackDir=None):
    filePath = getAbsPath(filePath)

    if not isFile(filePath):
        raise Exception(f'File is not found: { filePath }')

    if not unpackDir:
        unpackDir = filePath + '.unpacked'

    with openFile(filePath) as f:
        signature = f.read(4)

        if signature != DAT_SIGNATURE:
            raise Exception('Unknown signature')

        itemCount = f.u32()

        items = [ None ] * itemCount

        for i in range(itemCount):
            item = items[i] = ItemMeta()

            item.path = f.string().lower()
            item.size = f.u32()

        for item in items:
            data = f.read(item.size)

            itemPath = getAbsPath(joinPath(unpackDir, item.path))

            createFileDirs(itemPath)

            writeBin(itemPath, data)


def decryptPack (filePath):
    filePath = getAbsPath(filePath)

    if not isFile(filePath):
        raise Exception(f'File is not found: { filePath }')

    if readBin(filePath, 4) == DAT_SIGNATURE:
        print('Already decrypted')
        return

    tmpPath = replaceExt(filePath, '.tmp')

    keySize = len(DAT_KEY)

    with openFile(filePath) as f, \
         open(tmpPath, 'wb') as f2:

        while f.remaining():
            data = f.ba(16 * 1024 * 1024)

            dataSize = len(data)

            for i in range(dataSize):
                data[i] ^= DAT_KEY[i % keySize]

            f2.write(data)

    removeFile(filePath)
    rename(tmpPath, filePath)


def isSI2Pack (filePath):
    return getFileName(filePath).lower().startswith('sl2')
        

def unpackAll ():
    for filePath in iterFiles(GAME_DIR, True, [ '.dat' ]):
        if not isSI2Pack(filePath):
            continue
            
        print(filePath)

        unpackPak(filePath, joinPath(GAME_DIR, '.unpacked'))

        print(' ')


def decryptAll ():
    for filePath in iterFiles(GAME_DIR, True, [ '.dat' ]):
        if not isSI2Pack(filePath):
            continue

        print(filePath)

        decryptPack(filePath)

        print(' ')


def main ():
    unpackAll()
    # decryptAll()



if __name__ == '__main__':
    main()
