# Ren'Py Visual Novel Engine Tools

import sys

sys.path.insert(0, r'C:\Projects\PythonLib\python\v001')

from bfw.utils import *
from bfw.reader import *
from bfw.types.enums import Enum



ES_DIR = r'G:\Steam\steamapps\common\Everlasting Summer'



class RPYCEntry:
    def __init__ (self):
        self.index  = None
        self.offset = None
        self.size   = None


def unpackRPYC (filePath):
    filePath = getAbsPath(filePath)

    if not isFile(filePath):
        raise Exception(f'File does not exist: { filePath }')

    if not getFileSize(filePath):
        return

    with openFile(filePath) as f:
        signature = f.read(10)

        if signature != b'RENPY RPC2':
            raise Exception(f'Unknown signature: { filePath }')

        entries = []

        while True:
            entry = RPYCEntry()

            entry.index  = f.u32()
            entry.offset = f.u32()
            entry.size   = f.u32()

            if entry.index == 0:
                break

            entries.append(entry)

        destDir = filePath + '.unpacked'

        createDirs(destDir)

        for entry in entries:
            f.seek(entry.offset)

            data = f.read(entry.size)
            data = decompressData(data)

            destPath = joinPath(destDir, f'{ entry.index }.bin')

            writeBin(destPath, data)

        f.fromEnd(-16)

        unk1 = f.read(16)



# .rpyb - cache
# .rpyc - ?
# .rpa  - archive
def unpackAll (gameDir):
    if not isDir(gameDir):
        raise Exception(f'Game directory does not exist: { gameDir }')

    for filePath in iterFiles(gameDir, True, [ '.rpyc' ]):
        match getExt(filePath):
            case '.rpyc':
                print(filePath)
                unpackRPYC(filePath)
                print(' ')


def main ():
    # unpackAll(ES_DIR)
    unpackRPYC(joinPath(ES_DIR, 'game', 'resources.rpyc'))
    # decompressFile(joinPath(ES_DIR, 'game', 'cache', 'bytecode.rpyb'))



if __name__ == '__main__':
    main()
