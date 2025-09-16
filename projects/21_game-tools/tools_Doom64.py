# DOOM64 Tools

import sys

sys.path.insert(0, r'C:\Projects\PythonLib\python\v001')

from bfw.utils import *
from bfw.reader import *
from bfw.types.enums import Enum2



GAME_DIR = r'G:\Steam\steamapps\common\Doom 64'

WAD_SIGNATURE  = b'IWAD'
PWAD_SIGNATURE = b'PWAD'
WAV_SIGNATURE  = b'RIFF'
PNG_SIGNATURE  = b'\x89PNG'
MTHD_SIGNATURE = b'MThd'



class ItemMeta:
    def __init__ (self):
        self.name   = None
        self.size   = None
        self.offset = None


def isASCIIString (data):
    for byte in data:
        if (byte < 32 or byte >= 127) and byte not in [ 9, 10, 13 ]: 
            return False

    return True


def unpackWAD (filePath, unpackDir=None):    
    filePath = getAbsPath(filePath)

    if not isFile(filePath):
        raise Exception(f'File is not found: { filePath }')

    if not unpackDir:
        unpackDir = filePath + '.unpacked'

    with openFile(filePath) as f:
        signature = f.read(4)

        assert signature in [ WAD_SIGNATURE, PWAD_SIGNATURE ]

        itemCount  = f.u32()
        metaOffset = f.u32()

        f.seek(metaOffset)

        items = []

        for i in range(itemCount):
            item = ItemMeta()

            item.offset = f.u32()
            item.size   = f.u32()
            item.name   = f.string(8)

            if item.name == '?':
                item.name = 'ISAMM'

            if item.size > 0:
                items.append(item)

        createDirs(unpackDir)

        for item in items:
            if not item.size:
                continue

            f.seek(item.offset)

            data = f.read(item.size)

            signature = data[:4]

            if signature == PWAD_SIGNATURE:
                ext = '.pwad'

            elif signature == WAD_SIGNATURE:
                ext = '.wad'

            elif signature == WAV_SIGNATURE:
                ext = '.wav'

            elif signature == PNG_SIGNATURE:
                ext = '.png'

            elif signature == MTHD_SIGNATURE:
                ext = '.mthd'

            elif isASCIIString(data):
                ext = '.txt'

            else:
                ext = '.bin'

            itemPath = joinPath(unpackDir, f'{ item.name }{ ext }')

            writeBin(itemPath, data)


def unpackAll ():
    for filePath in iterFiles(GAME_DIR, True, [ '.wad', '.pwad' ]):
        print(filePath)

        unpackWAD(filePath)

        print(' ')



def main ():
    unpackAll()



if __name__ == '__main__':
    main()
