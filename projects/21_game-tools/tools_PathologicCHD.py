# Pathologic Classic HD Tools

import sys

sys.path.insert(0, r'C:\Projects\PythonLib\python\v001')

from bfw.utils import *
from bfw.reader import *
from bfw.types.enums import Enum2



GAME_DIR = r'G:\Steam\steamapps\common\Pathologic Classic HD'

VFS_SIGNATURE = b'LP1C'



class ItemMeta:
    def __init__ (self):
        self.name   = None
        self.size   = None
        self.offset = None
        self.unk2   = None
        self.unk3   = None



def unpackVFS (filePath, unpackDir=None):    
    filePath = getAbsPath(filePath)

    if not isFile(filePath):
        raise Exception(f'File is not found: { filePath }')

    if not unpackDir:
        unpackDir = filePath + '.unpacked'

    with openFile(filePath) as f:
        signature = f.read(4)

        assert signature == VFS_SIGNATURE

        unk1 = f.u32()

        assert unk1 in [ 0, 1 ]

        itemCount = f.u32()

        items = [ None ] * itemCount

        for i in range(itemCount):
            items[i] = item = ItemMeta()

            nameSize    = f.u8()
            item.name   = f.string(size=nameSize, encoding='cp1251')
            item.size   = f.u32()
            item.offset = f.u32()
            item.unk2   = f.u32()
            item.unk3   = f.u32()

        createDirs(unpackDir)

        for item in items:
            dstPath = joinPath(unpackDir, item.name)

            print(dstPath)

            f.seek(item.offset)

            data = f.read(item.size)

            writeBin(dstPath, data)


def unpackAll ():
    for filePath in iterFiles(GAME_DIR, True, [ '.vfs' ]):
        print(filePath)

        unpackVFS(filePath)

        print(' ')



def main ():
    unpackAll()



if __name__ == '__main__':
    main()
