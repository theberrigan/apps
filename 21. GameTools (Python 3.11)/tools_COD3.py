# Call of Duty 3 Tools

import os
import sys

import math

sys.path.insert(0, r'C:\Projects\PythonLib\python\v001')

from bfw.utils import *
from bfw.reader import *
from bfw.types.enums import Enum2



# COD2BRO - 01.11.05
# COD3    - 07.11.06

COD2BRO_DIR     = r'D:\Documents\Downloads\Torrents\!COD\COD2BRO'
COD2BRO_RUS_DIR = r'D:\Documents\Downloads\Torrents\!COD\COD2BRO_RUS'
COD3_DIR        = r'D:\Documents\Downloads\Torrents\!COD\COD3'

COD_SIGNATURE = b'KAPF'


_c = {}

# STRING | TRTS
# DTEX   | APKF (confirmed once)
# SCRIPT | SNR2
# FLI    | NILF
# AUDIO  | <path>
# ANIM   | b'\x01\x01\x01\x00'

def unpack (filePath, unpackDir=None):    
    filePath = getAbsPath(filePath)

    if not isFile(filePath):
        raise Exception(f'File is not found: { filePath }')

    if not unpackDir:
        unpackDir = filePath + '.unpacked'

    # createDirs(unpackDir)

    # [0]
    # signature
    # unk1
    # unk2
    # namedResCount
    # resourcesOffsets
    # pathsOffset
    # offset3
    # someString
    # pakCount
    # resCount
    # paksMetaOffset
    # _resourcesOffsets (== resourcesOffsets)
    # [72]
    # namedResources[namedResCount] = [ name, unks2, resMetaOffset, offset ]
    # [paksMetaOffset]
    # paks[pakCount] = [ offset, size, alignedSize, unk8 ]
    # namedResources[i : namedResCount]['pakMeta'] = [ offset, size, alignedSize, unk8 ]  // seek(item['pakMetaOffset']) for each item
    # [resourcesOffsets]
    # resources[resCount] = [ nameOffset, pathOffset, size, pak = paks[index], unks5 ]
    # ??? offset?
    # resources[i : resCount]['name'] = str
    # [pathsOffset]
    # resources[i : resCount]['path'] = str

    with openFile(filePath) as f:
        signature = f.read(len(COD_SIGNATURE))

        if signature != COD_SIGNATURE:
            raise Exception('Wrong signature')

        unk1          = f.u32()  # COD2 - 1073825710, COD3 - 1073993482
        unk2          = f.u32()  # COD2 - 28, COD3 - 48
        namedResCount = f.u32()  # 1, 2, 3, 4, 5, 6

        assert unk1 in [ 1073825710, 1073993482 ], unk1
        assert unk2 in [ 28, 48 ], unk2

        namedResCount -= 1

        isCOD3 = unk1 == 1073993482 and unk2 == 48

        assert isCOD3 or unk1 == 1073825710 and unk2 == 28

        resourcesOffsets  = f.u32()
        pathsOffset       = f.u32()
        offset3           = f.u32()
        someString        = f.string(size=32)  # 'CODAUTO21', 'TALIGHTING01', 'CODLIGHTING', 'CODOPTERON2', 'MTHEYER', 'CODOPTERON3'
        pakCount          = f.u16()            # APKF count
        resCount          = f.u16()
        paksMetaOffset    = f.u32()
        _resourcesOffsets = f.u32()

        # <-- f.tell() == 72

        print(f'namedResCount={ namedResCount } paksMetaOffset={ paksMetaOffset } resourcesOffsets={ resourcesOffsets } pathsOffset={ pathsOffset } offset3={ offset3 } someString={ someString } pakCount={ pakCount } resCount={ resCount }')

        assert _resourcesOffsets == resourcesOffsets, (_resourcesOffsets, resourcesOffsets)

        print('-' * 10)

        namedResources = [ None ] * namedResCount

        for i in range(namedResCount):
            name          = f.string(12)
            always1       = f.u16()  # TODO: what?
            subResCount   = f.u16()
            pakMetaOffset = f.u32()
            infoOffset    = f.u32()

            assert always1 == 1, always1

            namedResources[i] = {
                'name':          name,
                'infoOffset':    infoOffset,
                'always1':       always1,
                'subResCount':   subResCount,
                'pakMetaOffset': pakMetaOffset,
                'pakMeta':       None,
                'info':          None
            }

        # -----------------------------------

        assert paksMetaOffset == f.tell(), (paksMetaOffset, f.tell())

        f.seek(paksMetaOffset)

        paks = [ None ] * pakCount

        for i in range(pakCount):
            offset      = f.u32()
            size        = f.u32()
            alignedSize = f.u32()  # or 0xFFFFFFFF
            unk8        = f.u32()
            zeros1      = f.u32(4)

            assert unk8 in [ 128, 130, 132, 194, 226 ], unk8
            assert sum(zeros1) == 0, zeros1

            paks[i] = {
                'offset':      offset,
                'size':        size,
                'alignedSize': alignedSize,
                'unk8':        unk8,
            }

        # -----------------------------------

        # <-- f.tell() == namedResources[0]['pakMetaOffset']
        assert not namedResources or f.tell() == namedResources[0]['pakMetaOffset'], (f.tell(), namedResources[0]['pakMetaOffset'])

        if namedResources:
            assert ((resourcesOffsets - f.tell()) / namedResCount) == 32

            for item in namedResources:
                f.seek(item['pakMetaOffset'])

                offset      = f.u32()
                size        = f.u32()
                alignedSize = f.u32()  # or 0xFFFFFFFF
                unk8        = f.u32()
                zeros1      = f.u32(4)

                assert unk8 == 0, unk8
                assert sum(zeros1) == 0, zeros1

                item['pakMeta'] = {
                    'offset':      offset,
                    'size':        size,
                    'alignedSize': alignedSize,
                    'unk8':        unk8
                }

        assert resourcesOffsets == f.tell()

        # -----------------------------------

        f.seek(resourcesOffsets)

        resources = [ None ] * resCount

        for i in range(resCount):
            nameOffset = f.u32()
            pathOffset = f.u32()
            size       = f.u32()
            pakIndex   = f.u32()
            _x = f.tell()
            unks5      = f.u16(2)
            f.seek(_x)
            unks5     += f.u32(asArray=True)
            # unks5      = f.u32()

            resources[i] = {
                'nameOffset': nameOffset,
                'pathOffset': pathOffset,
                'size':       size,
                'pakIndex':   pakIndex,
                'unks5':      unks5,
                'name':       None,
                'path':       None,
            }

        # <-- f.tell() == resources[0]['nameOffset']

        # -----------------------------------

        for item in namedResources:
            f.seek(item['infoOffset'])

            item['info'] = [ None ] * item['subResCount']

            for i in range(item['subResCount']):
                nameOffset = f.u32()
                pathOffset = f.u32()
                size       = f.u32()
                zero       = f.u32()
                offset     = f.u32()  # aligned offset???

                assert zero == 0, zero
                assert (item['pakMeta']['offset'] + offset) < (item['pakMeta']['offset'] + item['pakMeta']['size']), (offset, item['pakMeta']['offset'], item['pakMeta']['size'])

                item['info'][i] = {
                    'nameOffset': nameOffset,
                    'pathOffset': pathOffset,
                    'offset':     offset,  # alignet offset relative to item['pakMeta']['offset']
                    'size':       size,
                    'name':       None
                }

            for info in item['info']:
                f.seek(info['nameOffset'])
                info['name'] = f.alignedString(4)

            for info in item['info']:
                f.seek(info['pathOffset'])
                info['path'] = f.alignedString(4)

        # -----------------------------------

        for res in resources:
            f.seek(res['nameOffset'])
            res['name'] = f.alignedString(4)

        # -----------------------------------

        f.seek(pathsOffset)

        for res in resources:
            f.seek(res['pathOffset'])
            res['path'] = f.alignedString(4)

        # -----------------------------------

        # start of content
        f.seek(align(offset3, 4096))

        for i, item in enumerate(paks):
            print(f'paks[{ i }]={ toJson(item, False) }')

        print('-' * 10)

        for i, item in enumerate(namedResources):
            print(f'namedResources[{ i }]={ toJson(item, False) }')

        print('-' * 10)

        for i, item in enumerate(resources):
            print(f'resources[{ i }]={ toJson(item, False) }')

        # -----------------------------------

        for res in namedResources:
            baseOffset = res['pakMeta']['offset']

            for subRes in res['info']:
                absOffset = baseOffset + subRes['offset']

                ext = getExt(subRes['name']).lower()

                sign = f.read(4)

                if sign not in _c:
                    _c[sign] = []

                if ext not in _c[sign]:
                    _c[sign].append(ext)

        return

        if isCOD3:
            pass # unk7 = f.string(size=32)
        else:
            unk7 = f.read(16)
            print(formatHex(unk7))




    # exit()

def unpackAll (gameDir, unpackDir=None):
    for filePath in iterFiles(gameDir, True, [ '.cod' ]):
        print(filePath)

        unpack(filePath, unpackDir)

        print(' ')


def main ():
    if 1:
        for gameDir in [
            COD3_DIR,
            # COD2BRO_DIR,
            # COD2BRO_RUS_DIR
        ]:
            for filePath in iterFiles(gameDir, includeExts=[ '.cod' ]):
                if getFileName(filePath).lower() == 'weapfrvi':
                    continue

                print(filePath)

                unpack(filePath)

                print(' ')

                # sys.exit()
    else:
        # unpack(joinPath(COD3_DIR, 'usrdir', 'mp', 'rouen', 'zn01.cod'))
        # unpack(joinPath(COD3_DIR, 'usrdir', 'mp', 'ederdam', 'ederdam.cod'))
        unpack(joinPath(COD3_DIR, 'usrdir', 'sp', 'frontend.cod'))

    for k, v in _c.items():
        print(k, v)

    # print(' '.join([ str(k) for k in sorted(_c.keys()) ]))

    


if __name__ == '__main__':
    main()
