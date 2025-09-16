from ...common import bfw
from ...common.consts import *

from .consts import *
from .types import *

from bfw.utils import *
from bfw.reader import *
from bfw.types.enums import Enum





class IMG:
    def __init__ (self):
        self.filePath : str | None = None
        self.entries : list[IMGIndexEntry] | None = None
        self.f : Reader | None = None


class IMGIndexEntry:
    def __init__ (self):
        self.offset : int | None = None
        self.size   : int | None = None
        self.name   : str | None = None


class IMGReader:
    @classmethod
    def fromFile (cls, filePath : str) -> 'IMG':
        if not isFile(filePath):
            raise OSError(f'File does not exist: { filePath }')

        rawData = readBin(filePath)
        reader  = MemReader(rawData, filePath)

        return cls().read(reader)

    @classmethod
    def unpackAll (cls, rootDir : str, outRootDir : str):
        for filePath in iterFiles(rootDir, True, [ IMG_EXT ]):
            print(filePath)

            outDir = getRelPath(dropExt(filePath), rootDir)
            outDir = joinPath(outRootDir, outDir)

            if checkPathExists(outDir):
                raise OSError(f'Path already exists: { outDir }')

            txd = IMGReader.fromFile(filePath)

            createDirs(outDir)

            for entry in txd.entries:
                f = txd.f

                f.seek(entry.offset)

                data = f.read(entry.size)

                outPath = joinPath(outDir, entry.name)

                print(f'\t{ filePath } ==> { outPath }')

                writeBin(outPath, data)

            print(' ')

    def read (self, f : Reader) -> 'IMG':
        assert f

        img = IMG()

        img.filePath = f.getFilePath()
        img.f = f

        self.readIndex(img)

        return img

    def readIndex (self, img : IMG):
        idxPath = replaceExt(img.filePath, IMG_INDEX_EXT)

        if not isFile(idxPath):
            raise OSError(f'File does not exist: { idxPath }')

        img.entries = []

        with openFile(idxPath) as f:
            while f.remaining() >= IMG_INDEX_ENTRY_SIZE:
                entry = IMGIndexEntry()

                entry.offset = f.u32() * 2048
                entry.size   = f.u32() * 2048
                entry.name   = f.string(size=24)

                img.entries.append(entry)

        img.entries.sort(key=lambda item: item.offset)



def _test_ ():
    for filePath in iterFiles(GAME_DIR, True, [ IMG_EXT ]):
        print(filePath)
        txd = IMGReader.fromFile(filePath)
        print(' ')



__all__ = [
    'IMGReader',

    '_test_',
]



if __name__ == '__main__':
    _test_()
