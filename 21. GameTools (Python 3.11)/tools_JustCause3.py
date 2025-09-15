# Just Cause 3 Tools

import sys

sys.path.insert(0, r'C:\Projects\PythonLib\python\v001')

from bfw.utils import *
from bfw.reader import *
from bfw.types.enums import Enum2



GAME_DIR = r'G:\Steam\steamapps\common\Just Cause 3'

TAB_SIGNATURE = b'TAB\x00'



class ItemMeta:
    def __init__ (self):
        self.id     = None
        self.offset = None
        self.size   = None

'''
def isASCIIString (data):
    for byte in data:
        if (byte < 32 or byte >= 127) and byte not in [ 9, 10, 13 ]: 
            return False

    return True
'''

def unpackArc (filePath, unpackDir=None):    
    filePath = getAbsPath(filePath)

    if not isFile(filePath):
        raise Exception(f'File is not found: { filePath }')

    if not unpackDir:
        unpackDir = filePath + '.unpacked'

    tabPath = replaceExt(filePath, '.tab')
    arcPath = replaceExt(filePath, '.arc')

    items = []

    with openFile(tabPath) as f:
        signature = f.read(4)

        assert signature == TAB_SIGNATURE

        unk1 = f.read(8)

        assert unk1 == b'\x02\x00\x01\x00\x00\x08\x00\x00'

        while f.remaining():
            item = ItemMeta()

            items.append(item)

            item.id     = f.u32()
            item.offset = f.u32()
            item.size   = f.u32()

    with openFile(arcPath) as f:
        for item in items:
            f.seek(item.offset)

            data = f.read(item.size)


def unpackAll ():
    for filePath in iterFiles(GAME_DIR, True, [ '.arc' ]):
        print(filePath)

        unpackArc(filePath)

        print(' ')


def main ():
    unpackAll()
    # unpackArc(joinPath(GAME_DIR, 'textures-s3.dat'))



if __name__ == '__main__':
    main()
