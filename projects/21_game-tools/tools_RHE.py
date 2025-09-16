# Roadhog Engine Tools
# Developer: Flying Wild Hog
# Games: Hard Reset [Redux], Shadow Warrior, etc.
# https://ru.wikipedia.org/wiki/Flying_Wild_Hog

import sys
import math

from zipfile import ZipFile

sys.path.insert(0, r'C:\Projects\PythonLib\python\v001')

from bfw.utils import *
from bfw.reader import *
from bfw.native.limits import MAX_U64


# GAME                | WINDOWS              | PS4
# --------------------|----------------------|--------
# Hard Reset          | v1 (encrypted .zips) | -
# Hard Reset Redux    | v2 package           | .psarc
# Shadow Warrior 2013 | v2 package           | .psarc
# Shadow Warrior 2    | v3 package           | .psarc


HR_GAME_DIR     = r'G:\Steam\steamapps\common\HardReset'
HRR_GAME_DIR    = r'G:\Steam\steamapps\common\Hard Reset Redux'
SW2013_GAME_DIR = r'G:\Games\Shadow Warrior 2013 dx11'
SW2_GAME_DIR    = r'G:\Steam\steamapps\common\Shadow Warrior 2'

GAME_DIRS = [
    HR_GAME_DIR,
    HRR_GAME_DIR,
    SW2013_GAME_DIR,
    SW2_GAME_DIR,
]

PKG_EXT = '.bin'

PKG_V1_SIGNATURE  = b'PK\x03\x04'  # zip signature
PKG_V1_PASSWORD   = b'9dU36jSJ@h265^k0b1!jrx*945F1'

# HR2011: b'9dU36jSJ@h265^k0b1!jrx*945F1'
# SW2013: b'@#viSS1t_*wWW.flY1nG!W1Ld&H0gR0X.c0M^!'

PKG_V3_SIGNATURE  = b'HOGP'
PKG_V3_BLOCK_SIZE = 2 ** 16



def unpackV1 (pkgPath, unpackDir):
    pkgPath = getAbsPath(pkgPath)

    if not isFile(pkgPath):
        raise Exception(f'Package file is not found: { pkgPath }')

    pkgName = dropExt(getBaseName(pkgPath))
    destDir = joinPath(unpackDir, pkgName)

    with ZipFile(pkgPath, 'r') as pkg:
        print(f'Extracting { pkgPath } to { destDir }')
        pkg.extractall(destDir, pwd=PKG_V1_PASSWORD)


def unpackV2 (pkgPath, unpackDir):
    pkgPath = getAbsPath(pkgPath)

    if not isFile(pkgPath):
        raise Exception(f'Package file is not found: { pkgPath }')

    pkgName = getBaseName(pkgPath)
    destDir = joinPath(unpackDir, pkgName)

    with openFile(pkgPath) as f:
        assetCount = f.u32()
        assetMetas = [ None ] * assetCount

        for i in range(assetCount):
            pathSize   = f.u32()
            path       = f.string(pathSize, 'cp1252')
            decompSize = f.u32()
            compSize   = f.u32()
            offset     = f.u64()
            unk5       = f.u32()  # not unique; very random; not flags; 1378887213, 2994593801, 3033576031, ...
            unk6       = f.u32()  # not unique; low random; not flags; 30XXXXXX: 30430436, 30533398, ...

            assetMetas[i] = {
                'path':       path,
                'offset':     offset,
                'compSize':   compSize,
                'decompSize': decompSize,
            }

        dataOffset = f.u32()

        for meta in assetMetas:
            path       = meta['path']
            offset     = meta['offset']
            compSize   = meta['compSize']
            decompSize = meta['decompSize']

            f.seek(dataOffset + offset)

            isCompressed = bool(compSize)

            if isCompressed:
                data = f.read(compSize)
                data = decompressData(data)
            else:
                data = f.read(decompSize)

            assert len(data) == decompSize

            outputPath = getAbsPath(joinPath(unpackDir, path))

            # print(f'\t{ outputPath }')

        assert not f.remaining()


def unpackV3 (pkgPath, unpackDir):
    pkgPath = getAbsPath(pkgPath)

    if not isFile(pkgPath):
        raise Exception(f'Package file is not found: { pkgPath }')

    pkgName = getBaseName(pkgPath)
    destDir = joinPath(unpackDir, pkgName)

    with openFile(pkgPath) as f:
        signature = f.read(4)

        if signature != PKG_V3_SIGNATURE:
            raise Exception(f'Wrong signature: { signature }')

        version = f.u32()

        if version != 3:
            raise Exception(f'Wrong version: { version }')

        dataSize = f.u64()

        f.skip(dataSize)

        metaSize   = f.u32()
        assetCount = f.u32()
        assetMetas = [ None ] * assetCount

        for i in range(assetCount):
            if f.remaining() < 24:
                raise Exception('Package is truncated')

            pathSize            = f.u16()
            path                = f.fixedString(pathSize, encoding='cp1252')  # TODO: or UTF-8?
            decompSize          = f.u32()  # equals 0 when !isPresent
            compSize            = f.u32()  # equals 0 when !isPresent
            firstBlockSizeIndex = f.u32()  # ordinal; equals 0xFFFFFFFF when !isPresent
            offset              = f.u64()  # equals 0xFFFFFFFFFFFFFFFF when !isPresent

            isPresent = offset != MAX_U64

            assetMetas[i] = {
                'isPresent':           isPresent,
                'path':                path,
                'offset':              offset,
                'compSize':            compSize,
                'decompSize':          decompSize,
                'firstBlockSizeIndex': firstBlockSizeIndex
            }

            assert not isPresent or compSize and decompSize

            # print(path, decompSize, compSize, assetId, offset)

        blockSizeCount = f.u32()
        blockSizes     = f.u16(blockSizeCount)

        assert not f.remaining()

        for meta in assetMetas:
            isPresent           = meta['isPresent']
            path                = meta['path']
            offset              = meta['offset']
            compSize            = meta['compSize']
            decompSize          = meta['decompSize']
            firstBlockSizeIndex = meta['firstBlockSizeIndex']

            outputPath = getAbsPath(joinPath(unpackDir, path))

            if '\\.unpack\\data\\cs\\' not in outputPath.lower():
                continue

            data = b''

            if isPresent:
                f.seek(offset)

                if compSize == decompSize:
                    data = f.read(compSize)
                else:
                    assert decompSize

                    blockCount = int(math.ceil(decompSize / PKG_V3_BLOCK_SIZE))
                    data       = bytearray(decompSize)
                    dataCursor = 0

                    for i in range(firstBlockSizeIndex, firstBlockSizeIndex + blockCount):
                        blockCompSize = blockSizes[i]

                        blockData = f.read(blockCompSize)

                        assert len(blockData) == blockCompSize

                        blockData = decompressData(blockData, mode=-15)

                        blockDecompSize = len(blockData)

                        data[dataCursor:dataCursor + blockDecompSize] = blockData

                        dataCursor += blockDecompSize

                    data = bytes(data)

                    assert dataCursor == decompSize

                assert len(data) == decompSize

            print(outputPath)
            createFileDirs(outputPath)
            writeBin(outputPath, data)


def unpack (pkgPath, unpackDir):
    signature = readBin(pkgPath, 4)

    if signature == PKG_V3_SIGNATURE:
        print('Version 3')
        unpackV3(pkgPath, unpackDir)
    elif signature == PKG_V1_SIGNATURE:
        print('Version 1')
        unpackV1(pkgPath, unpackDir)        
    else:
        print('Version 2')
        unpackV2(pkgPath, unpackDir)

def unpackAll (gameDir, unpackDir):
    if not isDir(gameDir):
        print(f'Game directory does not exist: { gameDir }')

    for pkgPath in iterFiles(gameDir, True, [ PKG_EXT ]):
        print(pkgPath)

        try:
            unpack(pkgPath, unpackDir)
        except Exception as e:
            print('ERROR:', e)

        # unpack(pkgPath, unpackDir)

        print(' ')

def unpackAll2 (gameDir):
    if not isDir(gameDir):
        print(f'Game directory does not exist: { gameDir }')

    for pkgPath in iterFiles(gameDir, True, [ PKG_EXT ]):
        print(pkgPath)

        try:
            unpack(pkgPath, dropExt(pkgPath))
        except Exception as e:
            print('ERROR:', e)

        # unpack(pkgPath, unpackDir)

        print(' ')

def main ():
    for gameDir in [ SW2_GAME_DIR ]:
        unpackAll(gameDir, joinPath(SW2_GAME_DIR, '.unpack'))


if __name__ == '__main__':
    main()
