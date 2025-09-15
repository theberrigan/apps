# Frostpunk Tools

import sys

sys.path.insert(0, r'C:\Projects\PythonLib\python\v001')

from bfw.utils import *
from bfw.reader import *
from bfw.types.enums import Enum2



GAME_DIR = r'G:\Steam\steamapps\common\Frostpunk'

IDX_SIGNATURE = b'\x00\x02\x01'



class ItemMeta:
    def __init__ (self):
        self.id           = None
        self.compSize     = None
        self.decompSize   = None
        self.offset       = None
        self.isCompressed = None
        self.path         = None


def isASCIIString (data):
    for byte in data:
        if (byte < 32 or byte >= 127) and byte not in [ 9, 10, 13 ]: 
            return False

    return True


def unpackPack (filePath, unpackDir=None):    
    filePath = getAbsPath(filePath)

    if not isFile(filePath):
        raise Exception(f'File is not found: { filePath }')

    if not unpackDir:
        unpackDir = filePath + '.unpacked'

    idxPath = replaceExt(filePath, '.idx')
    datPath = replaceExt(filePath, '.dat')
    strPath = replaceExt(filePath, '.str')

    itemMap = {}
    items   = None

    with openFile(idxPath) as f:
        signature = f.read(3)

        assert signature == IDX_SIGNATURE

        itemCount = f.u64()

        items = [ None ] * itemCount

        for i in range(itemCount):
            item = items[i] = ItemMeta()

            item.id           = f.u32()
            item.compSize     = f.u64()
            item.decompSize   = f.u64()
            item.offset       = f.u64()  
            item.isCompressed = bool(f.u8())

            itemMap[item.id] = item

        assert not f.remaining()

    if isFile(strPath):
        with openFile(strPath) as f:
            signature = f.read(3)

            assert signature == IDX_SIGNATURE

            itemCount = f.u64()

            for i in range(itemCount):
                itemId = f.u32()

                item = itemMap[itemId]

                pathSize = f.u32()

                item.path = f.string(pathSize)

            assert not f.remaining()

    del itemMap

    with openFile(datPath) as f:
        for item in items:
            f.seek(item.offset)

            data = f.read(item.compSize)

            if item.isCompressed:
                data = decompressData(data, 31)

                assert len(data) == item.decompSize

            if item.path:
                itemPath = item.path
            else:
                if data[:4] == b'OggS':
                    ext = '.ogg'
                elif isASCIIString(data):
                    ext = '.txt'
                else:
                    ext = '.bin'

                itemPath = f'{item.id:08X}{ext}'

            itemPath = getAbsPath(joinPath(unpackDir, itemPath))

            createFileDirs(itemPath)

            writeBin(itemPath, data)



def unpackAll ():
    for filePath in iterFiles(GAME_DIR, True, [ '.dat' ]):
        print(filePath)

        unpackPack(filePath)

        print(' ')


def main ():
    unpackAll()
    # unpackPack(joinPath(GAME_DIR, 'textures-s3.dat'))
    # unpackPack(joinPath(GAME_DIR, 'archives.dat'))



if __name__ == '__main__':
    main()
