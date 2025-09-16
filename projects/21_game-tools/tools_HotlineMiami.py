# Hotline Miami Tools

import sys

sys.path.insert(0, r'C:\Projects\PythonLib\python\v001')

from bfw.utils import *
from bfw.reader import *
from bfw.types.enums import Enum2



GAME_DIR = r'G:\Steam\steamapps\common\hotline_miami'

PHYRE_SIGNATURE = b'RYHP'
LGCP_SIGNATURE  = b'LGCP'



class Item:
    def __init__ (self):
        self.path   = None
        self.size   = None
        self.offset = None


def unpackWAD (filePath, unpackDir=None):    
    filePath = getAbsPath(filePath)

    if not isFile(filePath):
        raise Exception(f'File is not found: { filePath }')

    if not unpackDir:
        unpackDir = filePath + '.unpacked'

    with openFile(filePath) as f:
        metaSize  = f.u32()
        itemCount = f.u32()

        items = [ None ] * itemCount

        for i in range(itemCount):
            item = items[i] = Item()

            pathSize = f.u32()

            item.path   = f.string(size=pathSize)
            item.size   = f.u32()
            item.offset = f.u32()

        dataStart = f.tell()

        for item in items:
            print(item.path)

            f.seek(dataStart + item.offset)

            data = f.read(item.size)

            if getExt(item.path) != '.phyre':
                continue

            with MemReader(data) as f2:
                signature = f2.read(4)

                assert signature == PHYRE_SIGNATURE

                unk1 = f2.u32()
                unk2 = f2.u32()

                assert unk1 == 84, unk1

                signature = f2.read(4)

                assert signature == LGCP_SIGNATURE

                for j in range(30):
                    print(f2.u32())

    # exit()


def unpackAll ():
    for filePath in iterFiles(GAME_DIR, True, [ '.wad' ]):
        print(filePath)

        unpackWAD(filePath)

        print(' ')



def main ():
    unpackAll()



if __name__ == '__main__':
    main()
