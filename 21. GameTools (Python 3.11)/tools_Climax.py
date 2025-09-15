# Climax Studios Tools

import sys
import struct

sys.path.insert(0, r'C:\Projects\PythonLib\python\v001')

from bfw.utils import *
from bfw.reader import *
from bfw.writer import BinWriter
from bfw.xml import *
from bfw.types.enums import Enum2
from bfw.native.base import CU32
from bfw.native.limits import MAX_U32



# Games:
# - Silent Hill Origins
# - Silent Hill Shattered Memories

# Resources:
# - https://helco.github.io/zzdocs/resources/BSP/
# - https://github.com/kabbi/zanzarah-tools
# - https://formats.kaitai.io/renderware_binary_stream/
# - https://wiki.xentax.spektr.me/index.php/RenderWare_DAT
# - https://wiki.xentax.spektr.me/index.php/RenderWare_RWS
# - https://wiki.xentax.spektr.me/index.php/RenderWare_TXD
# - https://www.pcgamingwiki.com/wiki/Engine:RenderWare
# - https://www.copetti.org/writings/consoles/wii/
# - https://wiibrew.org/wiki/Memory_map

# Notes:
# - .AWD - RenderWare Audio Wave Dictionary



SHO_PS2_SRC_DIR  = r'D:\.dev\SilentHill\SHO\PS2\ISOUnpacked'
SHO_PS2_DST_DIR  = r'D:\.dev\SilentHill\SHO\PS2\ARCUnpacked'

SHSM_PS2_SRC_DIR = r'D:\.dev\SilentHill\SHSM\PS2\ISOUnpacked'
SHSM_PS2_DST_DIR = r'D:\.dev\SilentHill\SHSM\PS2\ARCUnpacked'

SHSM_WII_SRC_DIR = r'D:\.dev\SilentHill\SHSM\Wii\ISOUnpacked'
SHSM_WII_DST_DIR = r'D:\.dev\SilentHill\SHSM\Wii\ARCUnpacked'



PACKAGE_EXT = r'.arc'

ARC_V1_SIGNATURE  = b'A2.0'
ARC_V2_SIGNATURE = b'\x10\xFA\x00\x00'

RW_TYPE_TO_ID = createDoubleMap({
    'rwID_NAOBJECT':         0x00,
    'rwID_STRUCT':           0x01,
    'rwID_STRING':           0x02,
    'rwID_EXTENSION':        0x03,
    'rwID_CAMERA':           0x05,
    'rwID_TEXTURE':          0x06,
    'rwID_MATERIAL':         0x07,
    'rwID_MATLIST':          0x08,
    'rwID_ATOMICSECT':       0x09,
    'rwID_PLANESECT':        0x0A,
    'rwID_WORLD':            0x0B,
    'rwID_SPLINE':           0x0C,
    'rwID_MATRIX':           0x0D,
    'rwID_FRAMELIST':        0x0E,
    'rwID_GEOMETRY':         0x0F,
    'rwID_CLUMP':            0x10,
    'rwID_LIGHT':            0x12,
    'rwID_UNICODESTRING':    0x13,
    'rwID_ATOMIC':           0x14,
    'rwID_TEXTURENATIVE':    0x15,
    'rwID_TEXDICTIONARY':    0x16,
    'rwID_ANIMDATABASE':     0x17,
    'rwID_IMAGE':            0x18,
    'rwID_SKINANIMATION':    0x19,
    'rwID_GEOMETRYLIST':     0x1A,
    'rwID_ANIMANIMATION':    0x1B,
    'rwID_HANIMANIMATION':   0x1B,
    'rwID_TEAM':             0x1C,
    'rwID_CROWD':            0x1D,
    'rwID_DMORPHANIMATION':  0x1E,
    'rwID_RIGHTTORENDER':    0x1f,
    'rwID_MTEFFECTNATIVE':   0x20,
    'rwID_MTEFFECTDICT':     0x21,
    'rwID_TEAMDICTIONARY':   0x22,
    'rwID_PITEXDICTIONARY':  0x23,
    'rwID_TOC':              0x24,
    'rwID_PRTSTDGLOBALDATA': 0x25,
    'rwID_ALTPIPE':          0x26,
    'rwID_PIPEDS':           0x27,
    'rwID_PATCHMESH':        0x28,
    'rwID_CHUNKGROUPSTART':  0x29,
    'rwID_CHUNKGROUPEND':    0x2A,
    'rwID_UVANIMDICT':       0x2B,
    'rwID_COLLTREE':         0x2C,
    'rwID_ENVIRONMENT':      0x2D,
    'rwID_COREPLUGINIDMAX':  0x2E,
})
'''
    "rwID_TEXDICTIONARY": [
        22
    ],
    "rwaID_WAVEDICT": [
        2057
    ],
    "rwID_WORLD": [
        11
    ],
    "rwID_AUDIOCUES": [
        3840
    ],
    "rwID_CBSP": [
        4352
    ],
    "rwID_CLUMP": [
        16
    ],
    "rwID_HANIMANIMATION": [
        27
    ],
    "rwID_RWS": [
        36,
        41,
        35,
        43
    ],
    "rwID_STATETRANSITION": [
        3073
    ],
    "rwpID_BODYDEF": [
        2311
    ],
    "rwID_COMBATCOLLISION": [
        3074
    ],
    "rwID_DMORPHANIMATION": [
        30
    ],
    "rwID_POLYAREA": [
        3072
    ],
    "rwID_AINAVMESH": [
        3080
    ],
    "rwID_SPLINE": [
        12
    ],
    "rwID_KFONT": [
        4096
    ],
    "JPG": [
        3774863615
    ]
'''

# RW_ID_TO_TYPE = swapDict(RW_TYPE_TO_ID)

KNOWN_EXTS = [
    '.cmi',
    '.ico',
    '.eng',
    '.fre',
    '.ger',
    '.ita',
    '.jap',
    '.spa',
    '.jpg',
    '.lst',
    '.log',
    '.txd',
    '.xml',
]


class ArcItemV1:
    def __init__ (self):
        self.name       = None
        self.nameOffset = None
        self.dataOffset = None
        self.compSize   = None
        self.decompSize = None

class ArcItemV2:
    def __init__ (self):
        self.id         = None  # name/path hash
        self.dataOffset = None
        self.compSize   = None
        self.decompSize = None


def getUnpackDirName (baseDir):
    return baseDir + '.unpacked'


class ArcV1:
    @classmethod
    def unpackFile (cls, filePath, unpackDir):
        if not isFile(filePath):
            raise OSError(f'File does not exist: { filePath }')

        with openFile(filePath) as f:
            return cls._unpack(f, unpackDir)

    @classmethod
    def unpackBuffer (cls, data, unpackDir):
        with MemReader(data) as f:
            return cls._unpack(f, unpackDir)

    @classmethod
    def _unpack (cls, f, unpackDir):
        signature = f.read(4)

        if signature != ARC_V1_SIGNATURE:
            raise Exception(f'Invalid archive v1 signature: { signature }')

        itemCount     = f.u32()
        contentOffset = f.u32()
        namesOffset   = f.u32()
        namesSize     = f.u32()

        items = [ ArcItemV1() for _ in range(itemCount) ]

        for item in items:
            item.name       = None
            item.nameOffset = f.u32()
            item.dataOffset = f.u32()
            item.compSize   = f.u32()
            item.decompSize = f.u32()  # data compressed if decompSize > 0

        unk1 = f.u32()
        unk2 = f.u32()
        unk3 = f.u32()

        print(unk1, unk2, unk3)

        for item in items:
            f.seek(namesOffset + item.nameOffset)

            item.name = f.string()

            # print(toJson(item))

        createDirs(unpackDir)

        for item in items:
            f.seek(item.dataOffset)

            data = f.read(item.compSize)

            if item.decompSize:
                data = decompressData(data)

                assert len(data) == item.decompSize

            dstPath = joinPath(unpackDir, item.name)

            if getExt(dstPath) == PACKAGE_EXT:
                print('Child arc:', dstPath)

                dstPath = getUnpackDirName(dstPath)

                cls.unpackBuffer(data, dstPath)
            else:
                print('Writing:', dstPath)

                writeBin(dstPath, data)


class ArcV2:
    @classmethod
    def unpackFile (cls, filePath, unpackDir):
        if not isFile(filePath):
            raise OSError(f'File does not exist: { filePath }')

        with openFile(filePath) as f:
            return cls._unpack(f, unpackDir)

    @classmethod
    def unpackBuffer (cls, data, unpackDir):
        with MemReader(data) as f:
            return cls._unpack(f, unpackDir)

    @classmethod
    def _unpack (cls, f, unpackDir):
        signature = f.read(4)

        if signature != ARC_V2_SIGNATURE:
            raise Exception(f'Invalid archive v1 signature: { signature }')

        itemCount     = f.u32()
        contentOffset = f.u32()
        namesOffset   = f.u32()

        assert namesOffset == 0, namesOffset

        items = [ ArcItemV2() for _ in range(itemCount) ]

        for item in items:
            item.id         = f.u32()
            item.dataOffset = f.u32()
            item.compSize   = f.u32()
            item.decompSize = f.u32()  # data compressed if decompSize > 0

        unk1 = f.u32()
        unk2 = f.u32()
        unk3 = f.u32()

        print(unk1, unk2, unk3)

        createDirs(unpackDir)

        for item in items:
            f.seek(item.dataOffset)

            data = f.read(item.compSize)

            if item.decompSize:
                data = decompressData(data)

                assert len(data) == item.decompSize

            dstPath = joinPath(unpackDir, f'{item.id:08X}.bin')

            if data[:4] == ARC_V2_SIGNATURE:
                print('Child arc:', dstPath)

                dstPath = replaceExt(dstPath, '.arc')
                dstPath = getUnpackDirName(dstPath)
                
                cls.unpackBuffer(data, dstPath)
            else:
                print('Writing:', dstPath)

                writeBin(dstPath, data)


def unpack (filePath, unpackDir=None):
    filePath = getAbsPath(filePath)

    if not isFile(filePath):
        raise Exception(f'File is not found: { filePath }')

    if unpackDir is None:
        unpackDir = getUnpackDirName(filePath)

    signature = readBin(filePath, 4)

    if signature == ARC_V1_SIGNATURE:
        ArcV1.unpackFile(filePath, unpackDir)
    elif signature == ARC_V2_SIGNATURE:
        ArcV2.unpackFile(filePath, unpackDir)
    else:
        raise Exception(f'Unknown file signature: { signature }')


def unpackAll (gameDir, unpackDir=None):
    for filePath in iterFiles(gameDir, True, [ PACKAGE_EXT ]):
        print(filePath)

        if unpackDir:
            dstDir = joinPath(unpackDir, getBaseName(filePath))
        else:
            dstDir = filePath

        dstDir = getUnpackDirName(dstDir)

        unpack(filePath, dstDir)

        print(' ')


class RWBSHeader:
    def __init__ (self):
        self.sectionType    = None
        self.contentSize    = None
        self.sectionVersion = None
        self.contentStart   = None
        self.sectionEnd     = None

    @classmethod
    def read (cls, f):
        header = cls()

        header.sectionType    = f.u32()
        header.contentSize    = f.u32()
        header.sectionVersion = f.u32()
        header.contentStart   = f.tell()
        header.sectionEnd     = header.contentStart + header.contentSize

        return header


class RWBSSectionUnk1:
    def __init__ (self, header):
        self.header = header
        self.items  = None

    @classmethod
    def read (cls, f, header):
        section = cls(header)

        itemCount = f.u32()

        section.items = items = [ None ] * itemCount

        for i in range(itemCount + 1):
            name  = f.alignedString(4)
            value = f.u32()

            if name:
                items[i] = (name, value)

        return section

    def print (self):
        for name, value in self.items:
            print(name, value)

_c = set()

class RWBSSectionUnk2:
    def __init__ (self, header):
        self.header = header

    @classmethod
    def read (cls, f, header):
        section = cls(header)

        _start = f.tell()

        metaSize = f.u32()

        # <meta>

        strSize    = f.u32()
        sourceName = f.string(strSize)  # AudioTravis.rws

        guid       = readGUID(f)

        strSize    = f.u32()
        assetType  = f.string(strSize)

        strSize    = f.u32()
        path       = f.string(strSize)

        strSize    = f.u32()
        sourceDir  = f.string(strSize)  # Z:\Silent Hill Origins\Art_Final\Sound\BanksGeneric\Textures\

        unk5       = f.u32()

        # </meta>

        dataSize = f.u32()
        data     = f.read(dataSize)

        print(f'sourceName={ sourceName } guid={ guid } assetType={ assetType } path={ path } sourceDir={ sourceDir } unk5={ unk5 }')

        if path:
            _c.add(getAbsPath(path.split('{')[0].rstrip('\\')))

        if sourceDir:
            _c.add(getAbsPath(sourceDir.rstrip('\\')))

        return section

    def print (self):
        pass

def readGUID (f):    
    # u32         - u16   - u16   - b2    - b6
    # 10 93 F7 17 - 9D 7F - F6 49 - 9F E5 - 3A BE 5A 95 B5 3A // 17F79310-7F9D-49F6-9FE5-3ABE5A95B53A

    a = f.u32()
    b = f.u16()
    c = f.u16()
    d = f.read(2)
    e = f.read(6)

    return f'{a:08X}-{b:04X}-{c:04X}-{ d.hex() }-{ e.hex() }'.upper()



RWBS_SECTION_MAP = {
    0x71C: RWBSSectionUnk1,
    0x716: RWBSSectionUnk2,
}

class RWBS:
    @classmethod
    def parseFile (cls, filePath):
        if not isFile(filePath):
            raise OSError(f'File does not exist: { filePath }')

        with openFile(filePath) as f:
            return cls._parse(f)

    @classmethod
    def parseBuffer (cls, data):
        with MemReader(data) as f:
            return cls._parse(f)

    @classmethod
    def _parse (cls, f):
        rwbs = cls()

        while f.remaining():
            header       = RWBSHeader.read(f)
            sectionClass = RWBS_SECTION_MAP.get(header.sectionType)

            if sectionClass:
                section = sectionClass.read(f, header)

                # if header.sectionType == 0x71C:
                #     section.print()
            else:
                f.skip(header.contentSize)

            assert 0 <= (header.sectionEnd - f.tell()) < 4

            f.seek(header.sectionEnd)


        return rwbs



def main ():
    IGNORE_EXTS = [
        '.cmi',
        '.ico',
        '.eng',
        '.fre',
        '.ger',
        '.ita',
        '.jap',
        '.spa',
        '.jpg',
        '.lst',
        '.log',
        '.txd',
        '.xml',
    ]

    IGNORE_FILES = [
        'Strings'
    ]

    for filePath in iterFiles(SHO_PS2_DST_DIR, True, excludeExts=KNOWN_EXTS):
        print(filePath)

        if getFileName(filePath) in IGNORE_FILES:
            continue

        RWBS.parseFile(filePath)

        print(' ')

    # print(toJson(_c))

    for p in sorted(list(_c), key=lambda k: k.lower()):
        print(p)

    exit()

        

    '''
    custom = [ 'Strings...' ]

    signs = [
        # Inventory.arc, CInventoryItemDef, Audiotest, CIGCCharacter, CEnemyBehaviour, 
        # CPlayerBehaviour, CSpotLight.Torch, DO_*, DH_*, GlobalStream, HO_*,
        # HospitalDoor, IntroRoad, MO_*, SA_*, TH_*, TO_*, 
        b'\x1c\x07\x00\x00',
        b'\x16\x07\x00\x00',
        b'\x04\x07\x00\x00',

        # pad.stream
        b'\x1c\x07\x00\x00',
        b'\x16\x07\x00\x00',

        # AudioPlayer, FontEUR, FontJAP, LocaleUI, Startup, UiData
        b'\x16\x07\x00\x00',
    ]

    versions = [
        # Inventory.arc, CInventoryItemDef, AudioPlayer, Audiotest, CIGCCharacter, 
        # CEnemyBehaviour, CPlayerBehaviour, CSpotLight.Torch, DO_*, DH_*, FontEUR, 
        # FontJAP, GlobalStream, HO_*, HospitalDoor, IntroRoad, LocaleUI, MO_*,
        # pad.stream, SA_*, Startup, TH_*, TO_*, 
        469893221,
    ]
    '''

    _t = []
    _v = []

    # SHO_PS2_DST_DIR
    for filePath in iterFiles(SHO_PS2_DST_DIR, True, excludeExts=KNOWN_EXTS):
        exs = [
            # 'AudioPlayer',
            # 'Audiotest',
            # 'CInventoryItemDef',
            # 'Inventory.arc.unpacked',
            # 'CIGCCharacter',
            # 'CPlayerBehaviour',
            'Strings.'
        ]

        # if 'CSpotLight.Torch' not in filePath:
        #     continue

        # if not getBaseName(filePath).startswith('UiData'):
        #     continue

        if [ True for x in exs if x in filePath ]:
            continue

        print(filePath)

        with openFile(filePath) as f: 
            while f.remaining():
                sectionType    = f.u32()
                sectionSize    = f.u32()
                sectionVersion = f.u32()
                contentStart   = f.tell()
                sectionEnd     = contentStart + sectionSize

                if sectionType == 0x71C:
                    itemCount = f.u32()

                    print(itemCount)

                    for i in range(itemCount + 1):
                        name = f.alignedString(4)
                        value = f.u32()

                        print(name, value)
                else: # 0x716
                    f.skip(sectionSize)

                assert f.tell() == sectionEnd

                if sectionType not in _t:
                    _t.append(sectionType)

                if sectionVersion not in _v:
                    _v.append(sectionVersion)

    # print(toJson(_t))
    # print(toJson(_v))
    
    exit()

    for x in sorted(list(set([ getExt(filePath) for filePath in iterFiles(SHO_PS2_DST_DIR, True) ]))):
        print(f"'{ x }'")

    exit()

    for filePath in iterFiles(SHO_PS2_DST_DIR, True, excludeExts=[ '.jpg', '.xml' ]):
        pass

    exit()

    for gameDir, unpackDir in [
        (SHO_PS2_SRC_DIR, SHO_PS2_DST_DIR),
        (SHSM_PS2_SRC_DIR, SHSM_PS2_DST_DIR),
        (SHSM_WII_SRC_DIR, SHSM_WII_DST_DIR)
    ]:
        print('=' * 50)
        print('GAME:', gameDir, unpackDir)
        print('=' * 50)
        unpackAll(gameDir, unpackDir)
        print('=' * 50)
        print('\n\n')


if __name__ == '__main__':
    main()
    