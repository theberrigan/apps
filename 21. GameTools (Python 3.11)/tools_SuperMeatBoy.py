# Super Meat Boy Tools

import sys

sys.path.insert(0, r'C:\Projects\PythonLib\python\v001')

from bfw.utils import *
from bfw.reader import *
from bfw.types.enums import Enum2



GAME_DIR = r'G:\Steam\steamapps\common\Super Meat Boy'



class DirItem:
    def __init__ (self):
        self.unk1  = None
        self.path  = None


class FileItem:
    def __init__ (self):
        self.offset   = None
        self.size     = None
        self.dirIndex = None


def unpackArch (filePath, unpackDir=None):    
    filePath = getAbsPath(filePath)

    if not isFile(filePath):
        raise Exception(f'File is not found: { filePath }')

    if not unpackDir:
        unpackDir = filePath + '.unpacked'

    with openFile(filePath) as f:
        dirCount = f.u32()  # 5 / 29 (like dirs)

        dirItems = [ None ] * dirCount

        for _ in range(dirCount):
            dirIndex = f.u32()

            item = dirItems[dirIndex] = DirItem()

            item.fileIndex = f.u32()

        fileCount = f.u32()  # 616 / 2770

        fileItems = [ None ] * fileCount

        for i in range(fileCount):
            item = fileItems[i] = FileItem()

            item.offset   = f.u32()
            item.size     = f.u32()
            item.dirIndex = f.u32()

        dirPathsSize  = f.u32()
        filePathsSize = f.u32()

        for item in dirItems:
            item.path = f.string()

        for item in fileItems:
            item.path = f.string()

        for item in fileItems:
            f.seek(item.offset)

            data = f.read(item.size)

            itemPath = getAbsPath(joinPath(unpackDir, item.path))

            createFileDirs(itemPath)

            writeBin(itemPath, data)


def unpackAll ():
    for filePath in iterFiles(GAME_DIR, True, [ '.dat' ]):
        print(filePath)

        unpackArch(filePath)

        print(' ')



def main ():
    # unpackAll()
    unpackArch(joinPath(GAME_DIR, 'gameaudio.dat'))
    unpackArch(joinPath(GAME_DIR, 'gamedata.dat'))



if __name__ == '__main__':
    main()
