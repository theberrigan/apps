# Silent Hill Homecoming Tools

import re
import sys
import regex

from math import ceil
from datetime import datetime

sys.path.insert(0, r'C:\Projects\PythonLib\python\v001')

from bfw.utils import *
from bfw.reader import *
from bfw.native.base import *
from bfw.native.limits import *
from bfw.compression.lzo import LZO




GAME_DIR = r'G:\Steam\steamapps\common\Silent Hill Homecoming'
PAKS_DIR = joinPath(GAME_DIR, 'Engine', 'pak', 'pc')
MISC_DIR = joinPath(GAME_DIR, '.misc')

UNPACK_DIR = joinPath(GAME_DIR, '.unpacked')

ASSETS_XML_PATH   = joinPath(GAME_DIR, 'Engine', 'assets_pc_b.xml')
ASSETS_JSON_PATH  = joinPath(MISC_DIR, 'assets_pc_b.json')
ASSETS_CACHE_PATH = joinPath(MISC_DIR, 'assets.json')

PAK_SIGNATURE = b'PAK_'

'''
Notes:
- Asset alignment: 2048
- LZO - b'LZO\x00' + U32(decompSize) + U32(compSize) + U8[compSize]

Asset types, in assets_pc_b.xml order:
.MYS  0/0*   - Render (Maya) scene (164)
.SCT  1/1*   - Sector (818)
.MDL  2/2    - Model (3533)
.MAT  3/3    - Material (5777)
.SYT  4/4    - Texture (16920)
.GIN  5/??   - Game properties (0)
.PIN  6/6    - Game properties (2)
.XWB  7/??   - Wave Bank (0)
.XSB  8/??   - Sound Bank (0)
.CSV  9/9    - Data table (90)
.DDB 10/11** - Dialog database (17)
.TXT 11/12   - Standard text (77)
.HKC 12/13   - Cinematic (1159)
.STR 13/15** - String table (98)
.PTM 14/16   - Particle template (1262)
.PGP 15/17   - Particle group (735)
.CMF 16/18   - FX system table (1)
.PHP 17/19*  - Phoneme data (1)
.MTM 18/20   - Mesh FX template (18)
.XML 19/21*  - Simple XML (908)
.GAT 20/22*  - Attachments (165)
.CAP 21/23*  - Capsule definitions (17)
.FTS 22/24   - Footstep rules (1)
.XML 23/??   - Serialized XML (908)
.STR 24/??   - Localized string table (98)
.APK 25/??   - Package (0)
.HKS 26/28*  - Havok Skeleton (228)
.HKA 27/29   - Havok Skeleton Anim (8461)
.HCL 28/30*  - Havok collision data (246)
.SES 29/31*  - SlayEd scene (312)
.XGS 30/??   - Sound Global Settings File (0)
.XWS 31/??   - Streamed Wave Bank (0)
.HKP 32/34*  - Havok Collision and Constraint D (341)
.NVM 33/35*  - Nav Mesh Sector Data (130)
.BIK 34/??   - Bink Movie (10)
.OGG 35/39   - Ogg Vorbis sound file (4447)
.SAC 36/40   - StdAudio Configuration file (18)
.XMB 37/??   - Binary XML file (0)
.GAB 38/??   - Binary GAT file (0)
.CAB 39/??   - Binary CAP file (0)
.FTB 40/??   - Binary FTS file (0)

no  = [ 5, 7, 8, 10, 14, 25, 26, 27, 32, 33, 36, 37, 38, 41 ]
chk = [ 1, 11, 15, 19, 21, 22, 23, 28, 30, 31, 34, 35 ]
knw = [ 0, 1, 2, 3, 4, 6, 9, 11, 12, 13, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 28, 29, 30, 31, 34, 35, 39, 40 ]
'''


# Flags extracted from g_SilentHill.sgl in this order:
# - 0  resourceflag_precached
# - 1  resourceflag_platform_pc
# - 2  resourceflag_platform_x360
# - 3  resourceflag_platform_ps3
# - 4  resourceflag_compressed
# - 5  resourceflag_streaming
# - 6  resourceflag_scriptbound
# - 7  resourceflag_has_instances
# - 8  resourceflag_globalpak
# - 9  resourceflag_missing
# - 10 resourceflag_ignore
# - 11 resourceflag_dead
# - 12 resourceflag_nofailmessage
# - 13 resourceflag_noautoload
# - 14 resourceflag_xboxcompressed
class AssetFlag:
    Unk0       = 1 << 0   # precache?
    Compressed = 1 << 4   # resourceflag_compressed (LZO 2.02)
    Unk5       = 1 << 5   # streamed?
    Unk6       = 1 << 6   # script bound?
    GlobalPak  = 1 << 8   # resourceflag_globalpak
    Unk12      = 1 << 12  # no fail message? (only fx_strings.str in GLOBAL.PAK)
    Unk13      = 1 << 13  # no auto load?


# TODO: reasearch None (?)
class AssetType:  # ext    ord  enum  description
    MYS = 0       # .MYS   0    0     Render (Maya) scene (164)
    SCT = 1       # .SCT   1    1     Sector (818)
    MDL = 2       # .MDL   2    2     Model (3533)
    MAT = 3       # .MAT   3    3     Material (5777)
    SYT = 4       # .SYT   4    4     Texture (16920)
    GIN = None    # .GIN   5    ??    Game properties (0)
    PIN = 6       # .PIN   6    6     Game properties (2)
    XWB = None    # .XWB   7    ??    Wave Bank (0)
    XSB = None    # .XSB   8    ??    Sound Bank (0)
    CSV = 9       # .CSV   9    9     Data table (90)
    DDB = 11      # .DDB   10   11    Dialog database (17)
    TXT = 12      # .TXT   11   12    Standard text (77)
    HKC = 13      # .HKC   12   13    Cinematic (1159)
    STR = 15      # .STR   13   15    String table (98)
    PTM = 16      # .PTM   14   16    Particle template (1262)
    PGP = 17      # .PGP   15   17    Particle group (735)
    CMF = 18      # .CMF   16   18    FX system table (1)
    PHP = 19      # .PHP   17   19    Phoneme data (1)
    MTM = 20      # .MTM   18   20    Mesh FX template (18)
    XML = 21      # .XML   19   21    Simple XML (908)
    GAT = 22      # .GAT   20   22    Attachments (165)
    CAP = 23      # .CAP   21   23    Capsule definitions (17)
    FTS = 24      # .FTS   22   24    Footstep rules (1)
    SXM = None    # .XML   23   ??    Serialized XML (908)
    LST = None    # .STR   24   ??    Localized string table (98)
    APK = None    # .APK   25   ??    Package (0)
    HKS = 28      # .HKS   26   28    Havok Skeleton (228)
    HKA = 29      # .HKA   27   29    Havok Skeleton Anim (8461)
    HCL = 30      # .HCL   28   30    Havok collision data (246)
    SES = 31      # .SES   29   31    SlayEd scene (312)
    XGS = None    # .XGS   30   ??    Sound Global Settings File (0)
    XWS = None    # .XWS   31   ??    Streamed Wave Bank (0)
    HKP = 34      # .HKP   32   34    Havok Collision and Constraint D (341)
    NVM = 35      # .NVM   33   35    Nav Mesh Sector Data (130)
    BIK = None    # .BIK   34   ??    Bink Movie (10)
    OGG = 39      # .OGG   35   39    Ogg Vorbis sound file (4447)
    SAC = 40      # .SAC   36   40    StdAudio Configuration file (18)
    XMB = None    # .XMB   37   ??    Binary XML file (0)
    GAB = None    # .GAB   38   ??    Binary GAT file (0)
    CAB = None    # .CAB   39   ??    Binary CAP file (0)
    FTB = None    # .FTB   40   ??    Binary FTS file (0)

ASSET_TYPE_TO_EXT = {
    AssetType.MYS: '.mys',
    AssetType.SCT: '.sct',
    AssetType.MDL: '.mdl',
    AssetType.MAT: '.mat',
    AssetType.SYT: '.syt',
  # AssetType.GIN: '.gin',
    AssetType.PIN: '.pin',
  # AssetType.XWB: '.xwb',
  # AssetType.XSB: '.xsb',
    AssetType.CSV: '.csv',
    AssetType.DDB: '.ddb',
    AssetType.TXT: '.txt',
    AssetType.HKC: '.hkc',
    AssetType.STR: '.str',
    AssetType.PTM: '.ptm',
    AssetType.PGP: '.pgp',
    AssetType.CMF: '.cmf',
    AssetType.PHP: '.php',
    AssetType.MTM: '.mtm',
    AssetType.XML: '.xml',
    AssetType.GAT: '.gat',
    AssetType.CAP: '.cap',
    AssetType.FTS: '.fts',
  # AssetType.SXM: '.xml',
  # AssetType.LST: '.str',
  # AssetType.APK: '.apk',
    AssetType.HKS: '.hks',
    AssetType.HKA: '.hka',
    AssetType.HCL: '.hcl',
    AssetType.SES: '.ses',
  # AssetType.XGS: '.xgs',
  # AssetType.XWS: '.xws',
    AssetType.HKP: '.hkp',
    AssetType.NVM: '.nvm',
  # AssetType.BIK: '.bik',
    AssetType.OGG: '.ogg',
    AssetType.SAC: '.sac',
  # AssetType.XMB: '.xmb',
  # AssetType.GAB: '.gab',
  # AssetType.CAB: '.cab',
  # AssetType.FTB: '.ftb' 
}


def getAssetExt (assetType):
    return ASSET_TYPE_TO_EXT.get(assetType, None)


def collectPaks (paksDir):
    pakMap = {}

    pakPaths = sorted(iterFiles(paksDir, False, [ '.pak' ]))

    for pakPath in pakPaths:
        print(pakPath)

        pakName = getFileName(pakPath)

        signature = readBin(pakPath, 4)

        if signature == PAK_SIGNATURE:
            pakMap[pakPath] = {
                'regex': re.compile(rf'^{ pakName }_(\d+)$', re.I),
                'chunks': {}
            }

            continue

        isParentFound = False
        
        for info in pakMap.values():
            match = re.match(info['regex'], pakName)

            if not match:
                continue

            chunkIndex = int(match.group(1), 10)  

            assert chunkIndex not in info['chunks']
            
            info['chunks'][chunkIndex] = pakPath

            isParentFound = True

        assert isParentFound

    paks = [ None ] * len(pakMap)

    for i, (parentPath, info) in enumerate(pakMap.items()):
        chunks = info['chunks'].items()
        chunks = sorted(chunks, key=lambda item: item[0])

        paks[i] = {
            'path': parentPath,
            'chunks': [ chunk[1] for chunk in chunks ]
        }

    return paks

# def unpackAll (rootDir, unpackDir):
#     for filePath in iterFiles(rootDir, False, [ '.pak' ]):
#         unpack(filePath, unpackDir)

def collectRootPaks (paksDir):
    paksDir = getAbsPath(paksDir)

    if not isDir(paksDir):
        raise Exception(f'Directory does not exist: { paksDir }')

    paks = []

    for pakPath in iterFiles(paksDir, False, [ '.pak' ]):
        signature = readBin(pakPath, 4)

        if signature == PAK_SIGNATURE:
            paks.append(pakPath)

    return paks


def parseAssetsList (xmlPath):
    with openFile(xmlPath) as f:
        node = f.read(4)

        assert node == b'\xEE\x14\x5E\xA5'

        zero1 = f.u32()

        assert zero1 == 0

        dirCount  = f.u32()
        nameCount = f.u32()
        assetDirs = {}

        for i in range(dirCount):
            node = f.read(4)

            assert node == b'\x14\x1D\x5E\xA5'

            dirName     = f.string(size=34)
            parentIndex = f.u32()

            if parentIndex == MAX_U32:
                dirPath = dirName
            else:
                dirPath = f'{ assetDirs[parentIndex] }/{ dirName }'

            assetDirs[i] = dirPath

        node = f.read(4)

        assert node == b'\x14\x1F\x5E\xA5'

        namesSize   = f.u32()
        namesOffset = f.tell()
        assetNames  = {}

        for i in range(nameCount):
            nameOffset = f.tell() - namesOffset
            assetName  = f.string()

            assetNames[nameOffset] = assetName

        assert f.tell() - namesOffset == namesSize

        assets = {}
        typeIndex = -1

        while True:
            typeIndex += 1

            node = f.read(4)

            if node == b'\x00\x1F\x5E\xA5':
                break

            assert node == b'\x46\x15\x5E\xA5'

            assetExt   = f.string(size=16).lower()
            assetHint  = f.string(size=32)
            startIndex = f.u16()

            if not assetExt:
                continue

            typeAssets = assets[typeIndex] = {
                'ext': assetExt,
                'hint': assetHint,
                'assets': {}
            }

            typeAssets = typeAssets['assets']

            # print(f'{assetHint:<32} {startIndex:>5}')

            assetCount = f.u32()

            # print(assetExt.upper(), '-', assetHint, f'({assetCount})')

            for i in range(assetCount):
                node = f.read(4)

                assert node == b'\x7E\x1F\x5E\xA5'

                nameOffset = f.u32()
                modTS      = f.u32()
                dirIndex   = f.u32()

                assetName = assetNames[nameOffset]
                assetPath = f'{ assetDirs[dirIndex] }/{ assetName }{ assetExt }'
                # modDate   = datetime.fromtimestamp(modTS)

                typeAssets[startIndex + i] = {
                    'path': assetPath,
                    'ts': modTS
                }

                # print(f'    {modDate} {assetPath}')

        assets = list(assets.values())

        for typeAssets in assets:
            typeAssets['assets'] = list(typeAssets['assets'].values())

        return assets

def assetsToJson (binPath, jsonPath=None):
    if not jsonPath:
        jsonPath = replaceExt(binPath, '.json')

    assets = parseAssetsList(binPath)

    writeJson(jsonPath, assets)

'''
{
    'paksDir': '',
    'paks': [
        {
            'pakName': 'GLOBAL'
            'pakExt': '.PAK'
            'chunkIndexDigits': 0,
            'chunks': [
                {
                    'chunkIndex': 0,  # real chunk index (see AssetType.MAT)
                    'assets': [
                        {
                            'chunkIndex': 0,  # from .pak file
                            'assetIndex': 0,
                            'name': '',
                            'ext': '',
                            'type': AssetType.TXT,
                            'flags': 0,
                            'ts': 0,
                            'offset': 0,
                            'size': 0,
                            'isAbsent': False,
                            'isCompressed': False,
                        }
                    ]
                }
            ]
        }
    ]
}
'''

def parseRootPacks (paksDir, rootPaks, noCache=False):
    # ------

    _cachePath = ASSETS_CACHE_PATH

    if not noCache:
        _cache = readJsonSafe(_cachePath)

        if _cache:
            return _cache

    # ------

    paksDir = getAbsPath(paksDir)

    db = {
        'paksDir': paksDir,
        'paks': None
    }

    packs = {}

    for i, rootPakPath in enumerate(rootPaks):
        pakFileName = getFileName(rootPakPath).lower()

        if pakFileName in [ 'shaders', 'shadersl' ]:
            print('Skip:', rootPakPath)
            continue

        # -----

        print(rootPakPath)

        pakName, pakExt = splitExt(getBaseName(rootPakPath))

        pak = packs[i] = {
            'pakName': pakName,
            'pakExt': pakExt,
            'chunkIndexDigits': 0,
            'chunks': None
        }

        with openFile(rootPakPath) as f:
            signature = f.read(4)

            if signature != PAK_SIGNATURE:
                raise Exception('Unknown file signature')

            version = f.u32()

            assert version == 1

            assetCount = f.u32()
            always0    = f.u32()

            assert always0 == 0

            maxChunkIndex = 0
            chunks = {}

            for j in range(assetCount):
                name       = f.string(size=64)
                flags      = f.u32()
                timestamp  = f.u32()  # timestamp
                offset     = f.u32()
                decompSize = f.i32()  # -1 if no data 
                chunkIndex = f.i16()  # -1 if current file
                assetType  = f.u16()  # see AssetType
                compSize   = f.i32()  # 0 if no data

                assert compSize == decompSize or compSize == 0 and decompSize == -1, (offset, decompSize, compSize)
                assert flags & AssetFlag.GlobalPak and pakName.lower() == 'global' or not (flags & AssetFlag.GlobalPak) and pakName.lower() != 'global'

                if chunkIndex > maxChunkIndex:
                    maxChunkIndex = chunkIndex

                if assetType == AssetType.MAT and flags & AssetFlag.Unk5:
                    containingChunkIndex = -1
                else:
                    containingChunkIndex = chunkIndex

                chunk = chunks.get(containingChunkIndex)

                if not chunk:
                    chunk = chunks[containingChunkIndex] = {
                        'chunkIndex': containingChunkIndex,
                        'assets': {}
                    }

                assetExt = getAssetExt(assetType)
                isAbsent = decompSize == -1

                assert assetExt is not None

                chunk['assets'][j] = {
                    'chunkIndex':   chunkIndex,
                    'assetIndex':   j,
                    'name':         name,
                    'ext':          assetExt,
                    'type':         assetType,
                    'flags':        flags,
                    'ts':           timestamp,
                    'offset':       offset,
                    'size':         compSize,
                    'isAbsent':     isAbsent,
                    'isCompressed': bool(flags & AssetFlag.Compressed)
                }

            chunks = sorted(chunks.values(), key=lambda item: item['chunkIndex'])

            for chunk in chunks:
                chunk['assets'] = sorted(chunk['assets'].values(), key=lambda item: item['offset'])

            pak['chunkIndexDigits'] = len(str(maxChunkIndex))
            pak['chunks'] = chunks

        print(' ')

    db['paks'] = list(packs.values())

    # ----

    writeJson(_cachePath, db)

    # ----

    return db

'''
{
    'paksDir': '',
    'paks': [
        {
            'pakName': 'GLOBAL'
            'pakExt': '.PAK'
            'chunkIndexDigits': 0,
            'chunks': [
                {
                    'chunkIndex': 0,  # -1 - root
                    'assets': [
                        {
                            'assetIndex': 0,
                            'name': '',
                            'ext': '',
                            'type': AssetType.TXT,
                            'flags': 0,
                            'ts': 0,
                            'offset': 0,
                            'size': 0,
                            'isAbsent': False,
                            'isCompressed': False,
                        }
                    ]
                }
            ]
        }
    ]
}
'''
def unpackRootPacks (db):
    assets = parseAssetsList(ASSETS_XML_PATH)
    assetDirMap = {}

    for extAssets in assets:
        for asset in extAssets['assets']:
            assetPath = asset['path']

            baseName = getBaseName(assetPath).lower()

            # assetDir = getDirPath(ASSETS_XML_PATH)
            assetDir = UNPACK_DIR
            assetDir = joinPath(assetDir, getDirPath(assetPath))
            assetDir = getAbsPath(assetDir)

            assert baseName not in assetDirMap or getRelPath(assetDirMap[baseName], assetDir) == '.'

            assetDirMap[baseName] = assetDir

    del assets

    # -------

    paksDir = db['paksDir']
    paks    = db['paks']

    for pak in paks:
        pakName = pak['pakName']
        pakExt  = pak['pakExt']
        chunks  = pak['chunks']

        chunkIndexDigits = pak['chunkIndexDigits']

        for chunk in chunks:
            chunkIndex = chunk['chunkIndex']

            if chunkIndex == -1:
                chunkName = f'{ pakName }{ pakExt }'
            else:
                chunkName = f'{ pakName }_{chunkIndex:0{chunkIndexDigits}}{ pakExt }'

            chunkPath   = joinPath(paksDir, chunkName)
            chunkAssets = chunk['assets']

            with openFile(chunkPath) as f:
                # print(chunkPath)

                for asset in chunkAssets:
                    assetIndex   = asset['assetIndex']
                    name         = asset['name']
                    ext          = asset['ext']
                    assetType    = asset['type']
                    flags        = asset['flags']
                    ts           = asset['ts']
                    offset       = asset['offset']
                    size         = asset['size']
                    isAbsent     = asset['isAbsent']
                    isCompressed = asset['isCompressed']

                    if isAbsent:
                        continue

                    assetKey  = (name + ext).lower()
                    assetDir  = assetDirMap.get(assetKey)
                    assetName = name + ext
                    assetPath = joinPath(assetDir, assetName)

                    assert assetDir

                    f.seek(offset)

                    head = f.read(4)

                    if head == b'EIFF':
                        always0 = f.u16()

                        assert always0 == 0

                        always511 = f.u16()

                        assert always511 == 511

                        unk3 = f.u16()  # 11, 12, 19, 23, 25, 26, 27, 28, 30, 31, 32, 34, 35, 36, 37, 40, 42, 43, 44, 45, 46, 47, 48, 49, 50, 51, 53, 54, 56

                        always11 = f.u16()

                        assert always11 == 11

                        contentSize = f.u32()

                        assert contentSize == (size - 16)
                        assert contentSize >= 4

                        head = f.read(4)
                        inEIFF = True
                    else:
                        contentSize = size
                        inEIFF = False

                    '''
                    # -------------

                    if assetType == AssetType.SYT and head == b'LZO\x00':
                        decompSize, compSize = readStruct('>II', f)

                        print(chunkPath, (offset, size), decompSize, compSize, f.tell(), assetPath)

                        compData = f.read(compSize)

                        blockSize = ceil(decompSize / 1024) * 1024
                        workSize  = blockSize + blockSize // 16 + 64 + 3

                        compOffset = workSize - compSize
                        workBuffer = CBuffer.fromSource((b'\x00' * compOffset) + compData)

                        decompData = LZO.lzo1x_decompress_safe(workBuffer, compOffset, compSize, decompSize)

                        data = decompData 

                        createDirs(assetDir)
                        writeBin(assetPath, data)

                        print(assetPath)

                    # ------------------

                    f.fromCurrent(-4)

                    data = f.read(contentSize)

                    createDirs(assetDir)
                    writeBin(assetPath, data)

                    print(assetPath)

                    continue

                    # -------------
                    '''

                    match assetType:
                        case AssetType.MYS:
                            assert head == b'MYSC'

                        case AssetType.SCT:
                            assert head == b'SCTR'

                        case AssetType.MDL:
                            assert head == b'MODL'

                        case AssetType.MTM:
                            assert head == b'MTMC'

                        case AssetType.SES:
                            assert head == b'LVLP'

                        case AssetType.NVM:
                            assert head == b'NAVM'

                        case AssetType.PIN | AssetType.CSV | AssetType.TXT | AssetType.HKC | AssetType.STR | AssetType.MAT:
                            _ = (head + f.read(size - 4)).decode('cp1252')

                        case AssetType.GAT | AssetType.CAP | AssetType.FTS | AssetType.XML:
                            _ = (head + f.read(size - 4)).decode('utf-8')

                        case AssetType.HKS | AssetType.HKA | AssetType.HKP:
                            assert head == b'W\xE0\xE0W'

                        case AssetType.CMF:
                            assert head == b'\x01\x00\x00\x00'

                        case AssetType.PHP:
                            assert head == b'\x01\x00\x00\x00'

                        case AssetType.SYT:
                            assert head in [ b'SYT\x00', b'LZO\x00' ]

                        case AssetType.DDB:
                            assert head == b'\x04\x00\xCD\xAB'

                        case AssetType.HCL:
                            assert head in [ b'a\x1b\x00\x00', b'_\x1b\x00\x00' ]

                            # if head == b'_\x1b\x00\x00':
                            #     print(name + ext, offset, size, chunkIndex, head, chunkPath); sys.exit()

                        case AssetType.OGG:
                            assert head == b'OggS'

                        case AssetType.SAC:
                            assert head == b'ACFG'

                        case AssetType.PTM:
                            assert inEIFF and head == b'PTMC' or not inEIFF

                        case AssetType.PGP:
                            assert inEIFF and head == b'PGPC' or not inEIFF

                        case _:
                            assert 0, assetType

    # AssetType.MYS: '.mys' - binary data packed in EIFF container (b'MYSC')
    # AssetType.SCT: '.sct' - binary data packed in EIFF container (b'SCTR')
    # AssetType.MDL: '.mdl' - binary data packed in EIFF container (b'MODL')
    # AssetType.MAT: '.mat' - text file encoded with CP1251 (?)
    # AssetType.SYT: '.syt' - raw binary data (b'SYT\x00') or binary data compressed with LZO (b'SYT\x00')
    # AssetType.PIN: '.pin' - text file encoded with CP1251 (?)
    # AssetType.CSV: '.csv' - text file encoded with CP1251 (?)
    # AssetType.DDB: '.ddb' - raw binary data (starting with b'\x04\x00\xCD\xAB') (?)
    # AssetType.TXT: '.txt' - text file encoded with CP1251
    # AssetType.HKC: '.hkc' - text file encoded with CP1251 (?)
    # AssetType.STR: '.str' - text file encoded with CP1251 (?)
    # AssetType.PTM: '.ptm' - raw binary data or binary data packed in EIFF container (b'PTMC')
    # AssetType.PGP: '.pgp' - raw binary data or binary data packed in EIFF container (b'PGPC')
    # AssetType.CMF: '.cmf' - raw binary data (starting with b'\x01\x00\x00\x00') (?)
    # AssetType.PHP: '.php' - raw binary data (starting with b'\x01\x00\x00\x00') (?)
    # AssetType.MTM: '.mtm' - binary data packed in EIFF container (b'MTMC')
    # AssetType.XML: '.xml' - xml encoded with UTF-8 (sometimes with BOM)
    # AssetType.GAT: '.gat' - xml encoded with UTF-8 (sometimes with BOM)
    # AssetType.CAP: '.cap' - xml encoded with UTF-8 (sometimes with BOM)
    # AssetType.FTS: '.fts' - xml encoded with UTF-8 (sometimes with BOM)
    # AssetType.HKS: '.hks' - raw binary data (b'W\xE0\xE0W')
    # AssetType.HKA: '.hka' - raw binary data (b'W\xE0\xE0W')
    # AssetType.HCL: '.hcl' - raw binary data (starting with b'a\x1b\x00\x00' or b'_\x1b\x00\x00') (?) 
    # AssetType.SES: '.ses' - binary data packed in EIFF container (b'LVLP')
    # AssetType.HKP: '.hkp' - raw binary data (b'W\xE0\xE0W')
    # AssetType.NVM: '.nvm' - binary data packed in EIFF container (b'NAVM')
    # AssetType.OGG: '.ogg' - OGG Vorbis file
    # AssetType.SAC: '.sac' - raw binary data (b'ACFG')

    # AssetFlag.Unk0 resourceflag_precached
    #     ".syt", 
    #     ".mat", 
    #     ".mdl", 
    #     ".ogg", 
    #     ".sac", 
    #     ".cmf", 
    #     ".ptm", 
    #     ".pgp", 
    #     ".mtm", 
    #     ".fts", 
    #     ".hks", 
    #     ".hka", 
    #     ".xml", 
    #     ".gat", 
    #     ".hcl", 
    #     ".hkp", 
    #     ".txt", 
    #     ".pin", 
    #     ".csv", 
    #     ".cap", 
    #     ".str", 
    #     ".ddb", 
    #     ".hkc", 
    #     ".php", 
    #     ".sct", 
    #     ".ses", 
    #     ".mys", 
    #     ".nvm"
    # AssetFlag.Unk5 resourceflag_streaming
    #     ".syt", 
    #     ".mdl", 
    #     ".mat", 
    #     ".sct"
    # AssetFlag.Unk6 resourceflag_scriptbound
    #     ".hka"
    # AssetFlag.Unk12 resourceflag_nofailmessage
    #     ".str"
    # AssetFlag.Unk13 resourceflag_noautoload
    #     ".mat", 
    #     ".syt", 
    #     ".mdl", 
    #     ".hkp", 
    #     ".hka"

def parseAllRootPacks (paksDir):
    paksDir = getAbsPath(paksDir)

    if 1:
        rootPaks = collectRootPaks(paksDir)
    else:
        rootPaks = [ joinPath(PAKS_DIR, 'GLOBAL.PAK') ]

    db = parseRootPacks(paksDir, rootPaks)

    unpackRootPacks(db)

# Decompressed data size less than info in meta:
# .unpacked\Meshes\props\pickups\robbierabbit\bankcubemap01.syt
def parseSYT (rootDir):
    for sytPath in iterFiles(rootDir, True, [ '.syt' ]):
        with openFile(sytPath) as f:
            signature = f.read(4)

            if signature == b'LZO\x00':
                print('Skip')
                continue

            assert signature == b'SYT\x00'

            # 0  | SYT\x00
            # 4  | 0
            # 8  | 1
            # 12 | 0
            # 16 | 1, 2, 4, 6, 7, 10, 101
            # 20 | 0, 10, 15, 30
            # 24 | 0, 16
            # 28 | width
            # 32 | height
            # 36 | 1, 6
            # 40 | 1, 2, 3, 4, 5, 6, 7, 8, 9
            # 44 | 2, 4
            # 48 | 0, 1, 3, 5
            # 52 | name
            # 56 | width2   # >= width
            # 60 | height2  # >= height
            # 64 | 0
            # 68 | 0, 2
            # 72 | 0, 2, 3
            # 76 | U8[24] == 0
            #    | --- 128 ---

            unk1 = f.u32()

            assert unk1 == 0

            unk2 = f.u32()

            assert unk2 == 1

            unk3 = f.u32()

            assert unk3 == 0

            unk4 = f.u32()

            assert unk4 in [ 1, 2, 4, 6, 7, 10, 101 ], (unk4, sytPath)

            unk5 = f.u32()

            assert unk5 in [ 0, 10, 15, 30 ], (unk5, sytPath)

            unk6 = f.u32()

            assert unk6 in [ 0, 16 ], (unk6, sytPath)

            width  = f.u32()
            height = f.u32()

            unk7 = f.u32()

            assert unk7 in [ 1, 6 ], (unk7, sytPath)

            unk8 = f.u32()

            assert unk8 in [ 1, 2, 3, 4, 5, 6, 7, 8, 9 ], (unk8, sytPath)

            unk9 = f.u32()

            assert unk9 in [ 2, 4 ], (unk9, sytPath)

            unk10 = f.u32()

            assert unk10 in [ 0, 1, 3, 5 ], (unk10, sytPath)

            name = f.string(size=32)

            width2  = f.u32()
            height2 = f.u32()

            assert width <= width2 and height <= height2, (width, height, width2, height2, sytPath)

            if width != width2 or height != height2:
                print(width, height, width2, height2)

            unk11 = f.u32()

            assert unk11 == 0, (unk11, sytPath)

            unk12 = f.u32()

            assert unk12 in [ 0, 2 ], (unk12, sytPath)

            unk13 = f.u32()

            assert unk13 in [ 0, 2, 3 ], (unk13, sytPath)

            tail = f.u32(6)

            assert sum(tail) == 0, (tail, sytPath)

            # print(name)

if __name__ == '__main__':
    # unpackAll(PAKS_DIR, UNPACK_DIR)
    # unpack(joinPath(PAKS_DIR, 'GLOBAL.PAK'), UNPACK_DIR)
    # print(toJson(collectPaks(PAKS_DIR)))
    # unpackGlobal(joinPath(PAKS_DIR, 'GLOBAL.PAK'), UNPACK_DIR)
    # print(collectRootPaks(PAKS_DIR)) 
    # parseAllRootPacks(PAKS_DIR)
    # parseAssetsList(ASSETS_XML_PATH)
    # assetsToJson(ASSETS_XML_PATH, ASSETS_JSON_PATH)
    parseSYT(UNPACK_DIR)