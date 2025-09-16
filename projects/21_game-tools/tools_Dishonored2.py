# Dishonored 2 Tools

import re
import sys

sys.path.insert(0, r'C:\Projects\PythonLib\python\v001')

from bfw.utils import *
from bfw.reader import *
from bfw.writer import *
from bfw.types.enums import Enum



GAME_DIR = r'G:\Steam\steamapps\common\Dishonored2'

MASTER_INDEX_NAME = 'master.index'
INDEX_SIGNATURE   = b'SER'
PACK_SIGNATURE    = b'AKPK'



class MasterIndexData:
    def __init__ (self):
        self.indices         = None
        self.resources       = None
        self.sharedResources = None


class IndexFileMeta:
    def __init__ (self):
        self.groupId          = None
        self.fileName         = None
        self.filePath         = None
        self.resourceFileName = None
        self.resourceFilePath = None


class ResourceFileMeta:
    def __init__ (self):
        self.fileId   = None
        self.groupId  = None
        self.fileName = None
        self.filePath = None


class SharedResourceFileMeta:
    def __init__ (self):
        self.fileId   = None
        self.unk1     = None
        self.unk2     = None
        self.fileName = None
        self.filePath = None


class IndexItemMeta:
    def __init__ (self):
        self.index        = None
        self.type         = None
        self.name         = None
        self.path         = None
        self.offset       = None
        self.decompSize   = None
        self.compSize     = None
        self.unk1         = None
        self.flags        = None
        self.fileId       = None
        self.isShared     = None
        self.isCompressed = None


class IndexItemFlag (Enum):
    Shared = 1 << 7  # 0x80


class ResourceReader:
    @classmethod 
    def unpackGame (cls, gameDir, destDir=None):
        if not isDir(gameDir):
            raise Exception(f'Game directory does not exist: { gameDir }')

        masterPath = getAbsPath(joinPath(gameDir, 'base', MASTER_INDEX_NAME))

        if not isFile(masterPath):
            raise Exception(f'Master index file does not exist: { masterPath }')

        if not destDir:
            destDir = getAbsPath(joinPath(gameDir, 'base', '.extracted'))

        cls().unpackMasterIndex(masterPath, destDir)

    @classmethod 
    def unpackGroup (cls, indexPath, destDir=None):
        indexPath = getAbsPath(indexPath)

        if not isFile(indexPath):
            raise Exception(f'Index file does not exist: { indexPath }')

        indexDir   = getDirPath(indexPath)
        masterPath = getAbsPath(joinPath(indexDir, MASTER_INDEX_NAME))

        if not isFile(masterPath):
            raise Exception(f'Master index file does not exist: { masterPath }')

        if not destDir:
            destDir = getAbsPath(joinPath(indexDir, '.extracted'))

        cls().unpackGroupIndex(indexPath, masterPath, destDir)

    @classmethod 
    def showMasterIndexContent (cls, masterPath):
        masterPath = getAbsPath(masterPath)

        if not isFile(masterPath):
            raise Exception(f'Master index file does not exist: { masterPath }')

        master = cls().readMasterIndex(masterPath)

        print('--- INDICES ---')
        print(' ')

        for item in master.indices:
            print(f'groupId = { item.groupId }; fileName = "{ item.fileName }"; resourceFileName = "{ item.resourceFileName }"')

        print(' ')
        print('--- RESOURCES ---')
        print(' ')

        for item in master.resources:
            print(f'groupId = { item.groupId }; fileId = { item.fileId }; fileName = "{ item.fileName }"')

        print(' ')
        print('--- SHARED RESOURCES ---')
        print(' ')

        for item in master.sharedResources:
            print(f'unk1 = { item.unk1 }; unk2 = { item.unk2 }; fileId = { item.fileId }; fileName = "{ item.fileName }"')

        print(' ')

    def __init__ (self):
        self.unpackedFiles = []

    def readString (self, f):
        size = f.u32(byteOrder=ByteOrder.Little)

        return f.fixedString(size=size)

    def unpackGroupIndex (self, indexPath, masterPath, destDir):
        master    = self.readMasterIndex(masterPath)
        indexName = getBaseName(indexPath).lower()
        isFound   = False

        for item in master.indices:
            if indexName == item.fileName:
                self.unpackIndex(item.filePath, destDir, master)
                isFound = True
                break

        if not isFound:
            raise Exception(f'Index file { indexName } is not mentioned in the master index file, so this file cannot be unpacked')

    def unpackMasterIndex (self, masterPath, destDir):
        masterPath = getAbsPath(masterPath)

        if not isFile(masterPath):
            raise Exception(f'File is not found: { masterPath }')

        master = self.readMasterIndex(masterPath)

        for item in master.indices:
            self.unpackIndex(item.filePath, destDir, master)
  
    def readMasterIndex (self, masterPath):
        masterPath = getAbsPath(masterPath)

        if not isFile(masterPath):
            raise Exception(f'File is not found: { masterPath }')

        master = MasterIndexData()

        master.indices         = []
        master.resources       = []
        master.sharedResources = []

        masterDir = getDirPath(masterPath)

        with openFile(masterPath, byteOrder=ByteOrder.Big) as f:
            version   = f.u8()
            signature = f.read(3)

            assert signature == INDEX_SIGNATURE, signature
            assert version == 4, version

            unk1       = f.u16()  # _resourceStringCount (2)
            indexCount = f.u16()

            assert unk1 == 2, unk1

            for i in range(indexCount):
                indexMeta = IndexFileMeta()

                indexMeta.groupId          = i
                indexMeta.fileName         = self.readString(f).lower()
                indexMeta.filePath         = joinPath(masterDir, indexMeta.fileName)
                indexMeta.resourceFileName = self.readString(f).lower()
                indexMeta.resourceFilePath = joinPath(masterDir, indexMeta.resourceFileName)

                master.indices.append(indexMeta)

                resourceMeta = ResourceFileMeta()

                resourceMeta.fileId   = i
                resourceMeta.groupId  = i
                resourceMeta.fileName = indexMeta.resourceFileName
                resourceMeta.filePath = indexMeta.resourceFilePath

                master.resources.append(resourceMeta)

            resourceCount = f.u32()

            for i in range(resourceCount):
                resourceMeta = ResourceFileMeta()

                resourceMeta.fileName = self.readString(f).lower()
                resourceMeta.filePath = joinPath(masterDir, resourceMeta.fileName)
                resourceMeta.groupId  = f.u16()
                resourceMeta.fileId   = indexCount + i

                master.resources.append(resourceMeta)

            sharedCount = f.u32()

            for i in range(sharedCount):
                resourceMeta = SharedResourceFileMeta()

                resourceMeta.fileId   = i
                resourceMeta.unk1     = f.u32()
                resourceMeta.unk2     = f.u32()
                resourceMeta.fileName = self.readString(f).lower()
                resourceMeta.filePath = joinPath(masterDir, resourceMeta.fileName)

                master.sharedResources.append(resourceMeta)

        return master

    def unpackIndex (self, indexPath, destDir, master=None):
        indexPath = getAbsPath(indexPath)

        if not isFile(indexPath):
            raise Exception(f'File is not found: { indexPath }')

        if not master:
            master = readMasterIndex(replaceBaseName(indexPath, MASTER_INDEX_NAME))

        items = self.readIndex(indexPath)

        for item in items:
            if item.isShared:
                resourceMeta = master.sharedResources[item.fileId]
            else:
                resourceMeta = master.resources[item.fileId]

            resourceKey = item.offset | item.fileId << 64 | item.isShared << 80

            if resourceKey in self.unpackedFiles:
                continue

            self.unpackedFiles.append(resourceKey)

            if item.compSize == 0:
                data = b''
            else:
                # TODO: cache descriptors
                with openFile(resourceMeta.filePath) as f:
                    f.seek(item.offset)

                    data = f.read(item.compSize)

                    if item.isCompressed:
                        # TODO: determine mode
                        data = decompressData(data, mode=15)

                        assert len(data) == item.decompSize, (len(data), item.decompSize)

            if item.path:
                itemPath = getAbsPath(joinPath(destDir, item.path))
            else:
                itemPath = getAbsPath(joinPath(destDir, '.unnamed', f'{ calcMD5(data) }.bin'))

            createFileDirs(itemPath)

            writeBin(itemPath, data)  # .iggytex | .iggy | .imp

    def readIndex (self, indexPath):
        indexPath = getAbsPath(indexPath)

        if not isFile(indexPath):
            raise Exception(f'File is not found: { indexPath }')

        items = []

        with openFile(indexPath, byteOrder=ByteOrder.Big) as f:
            version   = f.u8()
            signature = f.read(3)

            assert signature == INDEX_SIGNATURE, signature
            assert version == 5, version

            dataSize = f.u32()

            unk1 = f.read(24)

            assert unk1 == (b'\x00' * len(unk1))
            assert f.getSize() == (f.tell() + dataSize)

            itemCount = f.u32()

            for i in range(itemCount):
                item = IndexItemMeta()

                item.index        = f.u32()
                item.type         = self.readString(f)
                item.name         = self.readString(f)
                item.path         = self.readString(f)
                item.offset       = f.u64()
                item.decompSize   = f.u32()
                item.compSize     = f.u32()
                unk1              = f.read(7)  # zeros
                item.unk1         = f.u8()     # 0, 32
                item.flags        = f.u8()     # 0, 0x80
                item.fileId       = f.u8()     # 0, 1, 2, 4, 5, 6, 8, 9, 10, 12, 13, 14, 16, 17, 18, 20, 21, 22, 24, 25, 26
                item.isShared     = bool(item.flags & IndexItemFlag.Shared)
                item.isCompressed = item.decompSize > item.compSize

                assert unk1 == b'\x00\x00\x00\x00\x00\x00\x00'
                assert item.unk1 in [ 0, 32 ]
                assert item.flags in [ 0, 0x80 ]
                assert item.fileId in [ 0, 1, 2, 4, 5, 6, 8, 9, 10, 12, 13, 14, 16, 17, 18, 20, 21, 22, 24, 25, 26 ]

                items.append(item)

        return items


# ---------------------------------------------------------------


class PackItemMeta:
    def __init__ (self):
        self.unk12     = None
        self.unk13     = None
        self.size      = None
        self.offset    = None
        self.typeId    = None
        self.unk21     = None
        self.typeName  = None
        self.isPersist = None


class PackReader:
    @classmethod 
    def unpackGame (cls, gameDir, destDir=None):
        if not isDir(gameDir):
            raise Exception(f'Game directory does not exist: { gameDir }')

        packDir = getAbsPath(joinPath(gameDir, 'base', 'pck'))

        if not isDir(packDir):
            raise Exception(f'Game pack directory does not exist: { packDir }')

        if not destDir:
            destDir = joinPath(packDir, '.extracted')

        for packPath in iterFiles(packDir, False, [ '.pck' ]):
            cls().unpackPack(packPath, joinPath(destDir, getFileName(packPath)))

    def __init__ (self):
        pass

    def unpackPack (self, packPath, destDir):
        packPath = getAbsPath(packPath)

        if not isFile(packPath):
            raise Exception(f'File is not found: { packPath }')

        with openFile(packPath) as f:
            signature = f.read(4)

            assert signature == PACK_SIGNATURE

            metaSize    = f.u32()
            unk1        = f.u32()  # always 1
            typesSize   = f.u32()
            persistSize = f.u32()  # persistent or preload?
            indexSize   = f.u32()  # itemSize * itemCount + 4
            unk5        = f.u32()  # always 4

            assert unk1 == 1, unk1
            assert unk5 == 4, unk5

            typesStart = f.tell()
            typesEnd   = typesStart + typesSize  
            typeCount  = f.u32()

            types = {}

            for i in range(typeCount):
                offset = f.u32()
                typeId = f.u32()

                types[typeId] = offset

            for typeId, offset in types.items():
                f.seek(typesStart + offset)

                types[typeId] = f.string(encoding='utf-16-le')

            f.seek(typesEnd)

            items = []

            persistStart = f.tell()
            persistCount = f.u32()

            for i in range(persistCount):
                item = PackItemMeta()

                item.unk12     = f.u32()  # 3782295518 (0xE1713FDE) (id?)
                item.unk13     = f.u32()  # always 1
                item.size      = f.u32()
                item.offset    = f.u32()
                item.typeId    = f.u32()
                item.typeName  = types[item.typeId]
                item.isPersist = True

                assert item.unk13 == 1, item.unk13

                items.append(item)

            assert f.tell() == (persistStart + persistSize)

            itemCount = f.u32()
            unk17     = f.u32()  # 227956 (0 or any number)

            assert (itemCount * 20 + 4) == indexSize

            dataStart = 8 + metaSize

            for i in range(itemCount):
                item = PackItemMeta()

                item.unk18     = f.u32()  # always 1; same as unk13
                item.size      = f.u32()
                item.offset    = f.u32()
                item.typeId    = f.u32()
                item.unk21     = f.u32()  # grows similar to offset (id?)
                item.typeName  = types[item.typeId]
                item.isPersist = False

                assert item.unk18 == 1, item.unk18

                items.append(item)

            assert f.tell() == dataStart, (f.tell(), dataStart)

            items.sort(key=lambda item: item.offset)

            # only one non-persistent item has id (item.unk21) 0 and it is the last one
            # persistent items always come first



def main ():
    PackReader.unpackGame(GAME_DIR)

    # ResourceReader.unpackGame(GAME_DIR)
    # ResourceReader.unpackGroup(joinPath(GAME_DIR, 'base', 'game3_patch.index'))
    # ResourceReader.showMasterIndexContent(joinPath(GAME_DIR, 'base', MASTER_INDEX_NAME))



if __name__ == '__main__':
    main()
