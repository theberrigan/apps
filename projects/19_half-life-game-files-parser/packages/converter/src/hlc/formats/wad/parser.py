from ...common import bfw
from ...common.consts import GAME_DIR
from .consts import *
from .types import *

from bfw.utils import *
from bfw.reader import *



class WADEntry:
    def __init__ (self, wadPath, wadName, resPath, name, offset, size, type_, raw):
        self.wadPath = wadPath
        self.wadName = wadName
        self.resPath = resPath
        self.name    = name
        self.offset  = offset
        self.size    = size
        self.type_   = type_
        self.raw     = raw


class WADDatabase:
    def __init__ (self):
        self.wadNames = None
        self.entries  = None

    def collect (self, rootDir):
        self.wadNames = []
        self.entries  = {}

        for wadPath in iterFiles(rootDir, True, includeExts=[ '.wad' ]):
            wadName = getBaseName(wadPath).lower()  # decals.wad

            self.wadNames.append(wadName)

            with openFile(wadPath) as f:
                signature = f.read(4)

                if signature != WAD_SIGNATURE:
                    raise Exception(f'Not a WAD file: { wadPath }')

                entryCount = f.i32()
                tocOffset  = f.i32()

                f.seek(tocOffset)

                entries = []

                for _ in range(entryCount):
                    dataOffset = f.i32()      # filepos
                    compSize   = f.i32()      # disksize - compressed or uncompressed (size of embedded data)
                    decompSize = f.i32()      # size - uncompressed
                    type_      = f.i8()       # TYP_* (WADLumpType)
                    attributes = f.i8(pad=2)  # file attributes
                    name       = f.string(WAD_MAX_ITEM_NAME_LENGTH).strip().lower()  # +0medkit

                    assert dataOffset > 0
                    assert compSize > 0
                    assert decompSize > 0
                    assert compSize == decompSize
                    assert '*' not in name
                    assert not attributes
                    assert type_ in [
                        WADLumpType.Palette,
                        WADLumpType.GFX,
                        WADLumpType.Mip,
                        WADLumpType.QFont
                    ], type_

                    resBasePath = f'{ wadName }/{ name }'

                    ext = WAD_TYPE_TO_EXT.get(type_, '').lower()

                    if ext:
                        resFullPath = f'{ resBasePath }.{ ext }'
                    else:
                        resFullPath = resBasePath

                    entry = WADEntry(
                        wadPath = wadPath,
                        wadName = wadName,
                        resPath = resFullPath,
                        name    = name,
                        offset  = dataOffset,
                        size    = compSize,
                        type_   = type_,
                        raw     = None,
                    )

                    self.entries[resBasePath] = self.entries[resFullPath] = entry

                    entries.append(entry)

                for entry in entries:
                    f.seek(entry.offset)

                    entry.raw = f.read(entry.size)

        return self

    def findEntry (self, resPath, resType=None) -> WADEntry | None:
        resName = getFileName(resPath).lower()
        resExt  = getExt(resPath)

        wadName = getFileName(getDirPath(resPath))

        if wadName:
            wadName  = replaceExt(wadName, '.wad').lower()
            wadNames = [ wadName ]
        else:
            wadNames = self.wadNames

        for wadName in wadNames:
            if resType == WADLumpType.Any:
                resExt = ''
            else:
                resExt = WAD_TYPE_TO_EXT.get(resType, resExt)

            if resExt and resExt[0] != '.':
                resExt = '.' + resExt

            key = f'{ wadName }/{ resName }{ resExt.lower() }'

            entry = self.entries.get(key)

            if entry:
                return entry

        return None

    def hasEntry (self, resPath, resType=None) -> bool:
        return self.findEntry(resPath, resType) is not None

    def openEntry (self, resPath, resType=None) -> MemReader | None:
        entry = self.findEntry(resPath, resType)

        if not entry:
            return None

        return MemReader(entry.raw, entry.wadPath)

gWADCache = None

def getWADs (rootDir=GAME_DIR):
    global gWADCache

    if gWADCache is not None:
        return gWADCache

    gWADCache = WADDatabase().collect(rootDir)

    return gWADCache



def _test_ ():
    for key in getWADs().entries.keys():
        print(key)

    print(getWADs().findEntry('xeno_sup3').resPath)



__all__ = [
    'WAD_TYPE_TO_EXT',
    'WAD_EXT_TO_TYPE',
    'WADLumpType',
    'getWADs',

    '_test_',
]



if __name__ == '__main__':
    _test_()
