# Dead Cells Tools

import sys

sys.path.insert(0, r'C:\Projects\PythonLib\python\v001')

from bfw.utils import *
from bfw.reader import *
from bfw.types.enums import Enum2



GAME_DIR = r'G:\Steam\steamapps\common\Dead Cells'

PAK_SIGNATURE = b'PAK\x01'



class NodeType (Enum2):
    File = 0
    Dir  = 1


class FileItem:
    def __init__ (self):
        self.path   = None
        self.offset = None
        self.size   = None
        self.unk2   = None


def readNode (f, baseOffset, path='', files=None):
    if files is None:
        files = []

    nameSize = f.u8()

    if nameSize:
        name = f.string(nameSize)
    else:
        name = ''

    nodePath = joinPath(path, name)

    nodeType = f.u8()

    if nodeType == NodeType.File:
        item = FileItem()

        item.path   = nodePath
        item.offset = f.u32() + baseOffset
        item.size   = f.u32()
        item.unk2   = f.u32()

        files.append(item)

    elif nodeType == NodeType.Dir:
        childCount = f.u32()

        for i in range(childCount):
            readNode(f, baseOffset, nodePath, files)

    else:
        raise Exception('Unknown item type')

    return files


def unpackPak (filePath, unpackDir=None):    
    filePath = getAbsPath(filePath)

    if not isFile(filePath):
        raise Exception(f'File is not found: { filePath }')

    if not unpackDir:
        unpackDir = filePath + '.unpacked'

    with openFile(filePath) as f:
        signature = f.read(4)

        assert signature == PAK_SIGNATURE

        dataOffset = f.u32()
        unk1       = f.u32()
        checksum   = f.string(64)
        fileItems  = readNode(f, dataOffset)

        for item in fileItems:
            f.seek(item.offset)

            data = f.read(item.size)

            itemPath = joinPath(unpackDir, item.path)

            createFileDirs(itemPath)

            writeBin(itemPath, data)
        

def unpackAll ():
    for filePath in iterFiles(GAME_DIR, True, [ '.pak' ]):
        print(filePath)

        unpackPak(filePath)

        print(' ')



def main ():
    unpackAll()



if __name__ == '__main__':
    main()
