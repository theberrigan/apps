# Chaser Tools

import sys

import lzo

sys.path.insert(0, r'C:\Projects\PythonLib\python\v001')

from bfw.utils import *
from bfw.reader import *
from bfw.types.enums import Enum2



GAME_DIR = r'G:\Steam\steamapps\common\Chaser'



class FileItem:
    def __init__ (self):
        self.path         = None
        self.dataOffset   = None
        self.compSize     = None
        self.decompSize   = None
        self.flags        = None
        self.isCompressed = None


def unpackPackage (filePath, unpackDir=None):
    filePath = getAbsPath(filePath)

    if not isFile(filePath):
        raise Exception(f'File is not found: { filePath }')

    if not unpackDir:
        unpackDir = filePath + '.unpacked'

    with openFile(filePath) as f:
        f.fromEnd(-4)

        metaOffset = f.u32()

        f.seek(metaOffset)

        metaSize  = f.u32()
        unk1      = f.u32()
        dirsSize  = f.u32()
        dirCount  = f.u32()
        filesSize = f.u32()
        fileCount = f.u32()

        assert unk1 == 8192

        dirItems  = [ f.string() for _ in range(dirCount) ]
        fileItems = [ FileItem() for _ in range(fileCount) ]

        for fileItem in fileItems:
            fileItem.path = f.string()

        for fileItem in fileItems:
            fileItem.dataOffset   = f.u32()
            fileItem.compSize     = f.u32()
            fileItem.decompSize   = f.u32()
            dirIndex              = f.u16()
            fileItem.flags        = f.u16()
            fileItem.isCompressed = bool(fileItem.flags & 2)
            fileItem.path         = joinPath(dirItems[dirIndex], fileItem.path)

        fileItems.sort(key=lambda item: item.dataOffset)

        for fileItem in fileItems:
            f.seek(fileItem.dataOffset)

            print(fileItem.compSize)
            print(fileItem.decompSize)
            print(' ')

            # data = f.read(fileItem.compSize)

            size     = f.u32()
            itemsEnd = f.tell() + size - 8

            s = 0

            while f.tell() < itemsEnd:
                unk1 = f.u32()
                unk3 = f.u32()

                s += unk1

                print(unk1, unk3)

            print(' ')
            print(s)

            return

            # if fileItem.isCompressed:
            #     data = lzo.decompress(data, False, fileItem.decompSize * 2)
            #     exit()

            # print(toJson(fileItem))


def unpackAll ():
    for filePath in iterFiles(GAME_DIR, True, [ '.fs' ]):
        print(filePath)

        unpackPackage(filePath)

        print(' ')


def main ():
    # unpackAll()
    unpackPackage(joinPath(GAME_DIR, 'Data', 'Textures.fs'))




if __name__ == '__main__':
    main()
