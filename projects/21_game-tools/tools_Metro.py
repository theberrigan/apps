# Metro (Redux) Games Tools

import sys
import regex

sys.path.insert(0, r'C:\Projects\PythonLib\python\v001')

from bfw.utils import *
from bfw.reader import *
from bfw.compression.lz4 import LZ4



METRO2_DIR = r'G:\Steam\steamapps\common\Metro Last Light Redux'
METRO3_DIR = r'G:\Steam\steamapps\common\Metro Exodus'

VFX_EXT_REGEX = regex.compile(r'^\.vfx\d*$', regex.I)


class VFX3EntryFlag:
    Patch   = 1 << 2  # only used with Dir and with patch_*.vfx (+multientry?)
    Dir     = 1 << 3
    Removed = 1 << 4  # mark file as deleted, used in patch_*.vfx

    @classmethod
    def isDir (cls, flags):
        return bool(flags & cls.Dir)

    @classmethod
    def isRemoved (cls, flags):
        return bool(flags & cls.Removed)


class VFXVersion:
    V1 = 1
    V3 = 3

    @classmethod
    def isSupported (cls, version):
        return version in [
            cls.V1,
            cls.V3
        ]

    @classmethod
    def getUnpacker (cls, version):
        if not cls.isSupported(version):
            return None

        unpackers = {
            cls.V1: unpackV1,
            cls.V3: unpackV3
        }

        return unpackers[version]


def unpackV1 (vfxPath, unpackDir):
    print('Unpack v1')

    gameDir = getDirPath(vfxPath)

    with openFile(vfxPath) as f:
        signature = f.u32()

        assert signature == 1

        version = f.u32()

        assert version == 1

        guid     = f.read(16)
        pkgCount = f.u32()
        capacity = f.u32()
        unk2     = f.u32()

        for i in range(pkgCount):
            pkgName   = f.string()
            itemCount = f.u32()

            print(pkgName, itemCount)

            for j in range(itemCount):
                itemName = f.string()
                print('   ', itemName)

            pkgSize = f.u32()

            print(pkgSize)
            print(' ')

        for i in range(capacity):
            attrs = f.u16()
            index4 = f.u16()

            # assert attrs in [ 0, 1, 8 ], attrs

            if attrs == 0:  # file
                offset     = f.u32()
                decompSize = f.u32()
                compSize   = f.u32()
                print('File:', attrs, offset, compSize, decompSize)
            elif attrs == 8:  # dir
                offset = f.u32()
                print('Dir:', attrs, offset)
            else:
                print(attrs, index4)

def readMaskedString (f):
    strSize = f.u8()
    strMask = f.u8()

    if strSize > 1:
        codes = list(f.read(strSize - 1))
    else:
        codes = []

    for i, code in enumerate(codes):
        codes[i] = chr(code ^ strMask)

    null = f.u8()

    assert null == 0

    return ''.join(codes)


class VFX3CompressionType:
    LZ4 = 1


class VFX3Data:
    def __init__ (self):
        self.path            = None
        self.version         = VFXVersion.V3
        self.compressionType = VFX3CompressionType.LZ4
        self.contentVersion  = None
        self.guid            = None
        self.packages        = []
        self.entries         = []
        self.items           = []


class VFX3Package:
    def __init__ (self):
        self.name   = None
        self.levels = []
        self.chunk  = None

    def __str__ (self):
        return self.name


class VFX3DirEntry:
    def __init__ (self):
        self.flags      = VFX3EntryFlag.Dir
        self.path       = None
        self.firstEntry = None
        self.entryCount = None


class VFX3FileEntry:
    def __init__ (self):
        self.flags        = 0
        self.path         = None
        self.packageIndex = None
        self.offset       = None
        self.decompSize   = None
        self.compSize     = None


class VFX3Item:
    def __init__ (self):
        self.path         = None
        self.isRemoved    = False
        self.isCompressed = False
        self.packageIndex = None
        self.offset       = None
        self.decompSize   = None
        self.compSize     = None


def unpackV3 (vfxPath, unpackDir):
    print('Unpack v3', getBaseName(vfxPath))

    vfxPath = getAbsPath(vfxPath)

    if not isFile(vfxPath):
        raise Exception(f'File is not found: { vfxPath }')

    vfx = readVFX3(vfxPath)
    vfx.items = entriesToItemsV3(vfx.entries)

    return vfx

    # if getBaseName(vfxPath) == 'patch_01.vfx':
    #     printVFX3(vfx)

    # verifyVFX3(vfx)

def readVFX3 (vfxPath):
    vfxPath = getAbsPath(vfxPath)

    if not isFile(vfxPath):
        raise Exception(f'File is not found: { vfxPath }')

    vfx = VFX3Data()

    vfx.path = vfxPath

    with openFile(vfxPath) as f:
        vfx.version = f.u32()

        assert vfx.version == VFXVersion.V3
        
        vfx.compressionType = f.u32()

        assert vfx.compressionType == VFX3CompressionType.LZ4

        vfx.contentVersion = int(f.string())
        vfx.guid           = f.guid(True)
        packageCount       = f.u32()
        entryCount         = f.u32()
        zeros1             = f.u32()

        assert zeros1 == 0

        packages = vfx.packages = [ None ] * packageCount

        for i in range(packageCount):
            pkg = packages[i] = VFX3Package()

            pkg.name   = f.string()
            levelCount = f.u32()
            pkg.levels = [ f.string() for _ in range(levelCount) ]
            pkg.chunk  = f.u32()

        entries = vfx.entries = [ None ] * entryCount

        for i in range(entryCount):
            flags = f.u16()

            if VFX3EntryFlag.isDir(flags):
                entry = entries[i] = VFX3DirEntry()

                entry.flags      = flags
                entry.entryCount = f.u16()
                entry.firstEntry = f.u32()
                entry.path       = readMaskedString(f)
            else:
                entry = entries[i] = VFX3FileEntry()

                entry.flags        = flags
                entry.packageIndex = f.u16()
                entry.offset       = f.u32()
                entry.decompSize   = f.u32()
                entry.compSize     = f.u32()
                entry.path         = readMaskedString(f)

    return vfx

def entriesToItemsV3 (entries):
    items = []

    if not entries:
        return items

    def walk (parentPath, startIndex, count):
        for i in range(startIndex, startIndex + count):
            entry = entries[i]
            entryPath = joinPath(parentPath, entry.path)

            if isinstance(entry, VFX3DirEntry):
                walk(entryPath, entry.firstEntry, entry.entryCount)
            else:
                item = VFX3Item()

                item.path         = getNormPath(entryPath)
                item.isRemoved    = VFX3EntryFlag.isRemoved(entry.flags)
                item.isCompressed = entry.compSize != entry.decompSize
                item.packageIndex = entry.packageIndex
                item.offset       = entry.offset
                item.decompSize   = entry.decompSize
                item.compSize     = entry.compSize

                items.append(item)     

    rootEntry = entries[0]

    assert isinstance(rootEntry, VFX3DirEntry), 'Root entry expected to be a directory'

    walk(rootEntry.path, rootEntry.firstEntry, rootEntry.entryCount)

    return items

def verifyVFX3 (vfx):
    print(getBaseName(vfx.path))

    vfxDir = getDirPath(vfx.path)
    sizes  = []

    for pkg in vfx.packages:
        size = getFileSize(joinPath(vfxDir, pkg.name))
        sizes.append(size)
        # print('-', pkg.name, size)

    assert len(sizes) == len(vfx.packages)

    for entry in vfx.entries:
        if not isinstance(entry, VFX3DirEntry):
            pass
            # if entry.packageIndex < len(sizes):
            #     pkg = vfx.packages[entry.packageIndex]
            #     # assert (entry.flags & VFX3EntryFlag.Unk), (pkg.name, entry.path, bin(entry.flags), entry.offset, entry.compSize, entry.decompSize)

            #     # if not getBaseName(vfx.path).startswith('content_'):
            #     #     assert not (entry.flags & VFX3EntryFlag.Unk)
            # else:
            #     assert (entry.flags & VFX3EntryFlag.Unk)
        else:
            if entry.flags & VFX3EntryFlag.Patch:
                print('+++', entry.path)
            else:                
                print('---', entry.path)

                # assert (entry.flags & VFX3EntryFlag.Patch), (entry.path, bin(entry.flags))

    # for pkg in vfx.packages:
    #     print(pkg.chunk, pkg.name)

    print(' ')

def printVFX3 (vfx):
    print(getBaseName(vfx.path))
    print('Version:', vfx.version)
    print('Compression type:', vfx.compressionType)
    print('Content version:', vfx.contentVersion)
    print('GUID:', vfx.guid)
    print('Packages:')

    for pkg in vfx.packages:
        print('- Name:', pkg.name)
        print('  Chunk:', pkg.chunk)
        print('  Levels:')

        for lvl in pkg.levels:
            print('  -', lvl)

    print('Entries:')

    for entry in vfx.entries:
        if isinstance(entry, VFX3DirEntry):
            print(f'dir  | flags: {entry.flags:05b} | { entry.entryCount } file(s) | { entry.path }')
        elif not VFX3EntryFlag.isRemoved(entry.flags):
            print(f'file | flags: {entry.flags:05b} | { vfx.packages[entry.packageIndex].name }[{ entry.offset }:{ entry.compSize }] ({ entry.decompSize }) | { entry.path }')

    print(' ')

def isVFXFile (filePath):
    if not isFile(filePath):
        return False

    ext = getExt(getBaseName(filePath))

    return regex.match(VFX_EXT_REGEX, ext) is not None

def collectVFXFiles (rootDir):
    vfxFiles = []

    for filePath in iterFiles(rootDir, False):
        if isVFXFile(filePath):
            vfxFiles.append(filePath)

    return vfxFiles


if __name__ == '__main__':
    # unpackGame(METRO2_DIR, joinPath(METRO2_DIR, '!unpacked'))
    # unpackGame(METRO3_DIR, joinPath(METRO3_DIR, '!unpacked'))
    # unpackV3(joinPath(METRO3_DIR, 'patch_02.vfx'), joinPath(METRO3_DIR, '!unpacked'))

    vfxs = []

    for vfxPath in collectVFXFiles(METRO3_DIR):
        vfx = unpackV3(vfxPath, joinPath(METRO3_DIR, '!unpacked'))
        vfxs.append(vfx)

    vfxs.sort(key=lambda item: item.contentVersion)

    db = {}
    delSize = 0

    for vfx in vfxs:
        for item in vfx.items:
            if not item.isRemoved and item.isCompressed:
                pkgPath = joinPath(METRO3_DIR, vfx.packages[item.packageIndex].name)

                print(pkgPath, item.offset, item.compSize, item.decompSize)

                with openFile(pkgPath) as f:
                    f.seek(item.offset)
                    # blockSize = f.u32()
                    # blockDecompSize = f.u32()
                    # print(blockSize,blockDecompSize);exit()
                    data = f.read(item.compSize)

                data = LZ4.decompressBlocked(data, item.decompSize)

                print(len(data) == item.decompSize)

                writeBin(r"C:\Users\Berrigan\Desktop\data.bin", data)

                exit()

            if item.path in db:
                delSize += db[item.path]

                # if item.isRemoved:
                #     print('REMOVED:', item.path)
                # else:
                #     print('REPLACED:', item.path)

            if item.isRemoved:
                db[item.path] = 0
            else:
                db[item.path] = item.compSize

    print(delSize, len(db))






'''
{
    "4": [
        "patch", 
        "patch_00", 
        "patch_01", 
        "patch_01_shared", 
        "patch_02", 
        "patch_03", 
        "patch_04"
    ], 
    "8": [
        "content", 
        "patch", 
        "patch_00", 
        "patch_01", 
        "patch_01_shared", 
        "patch_02", 
        "patch_03", 
        "patch_04"
    ], 
    "16": [
        "patch_01", 
        "patch_01_shared", 
        "patch_02", 
        "patch_03", 
        "patch_04"
    ]
}

def unpackGame (gameDir, unpackDir):
    print('Unpacking', gameDir)

    vfxPath = joinPath(gameDir, 'content.vfx')

    if not isFile(vfxPath):
        print('File does not exist:', vfxPath)
        return

    with openFile(vfxPath) as f:
        signature = f.u32()

        if signature == 1:
            unpackV1(vfxPath, unpackDir)
        elif signature == 3:
            unpackV3(vfxPath, unpackDir)
        else:
            print('Unknown VFX file signature:', signature)

def getVFXVersion (vfxPath):
    with openFile(vfxPath) as f:
        version = f.u32()

    return version

def getUnpacker (version):
    version = getVFXVersion(vfxPath)

    if version

def unpack (srcPath, unpackDir):
    print('Unpacking', srcPath)

    if isFile(srcPath):
        if not isVFXFile(srcPath):
            print('Path is not a .vfx file:', srcPath)
            return

        version = getVFXVersion(srcPath)

        if not VFXVersion.isSupported(version):
            print('Unsupported version of the .vfx file:', version)
            return

        unpacker = VFXVersion.getUnpacker(srcPath)

        assert unpacker, '.vfx version is supported, but corresponding unpacker is not found'

    elif isDir(srcPath):

    else:
        print('Path does not exist:', srcPath)
'''