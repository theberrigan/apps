# Hitman: World of Assassination Tools

import re
import sys

sys.path.insert(0, r'C:\Projects\PythonLib\python\v001')

from bfw.utils import *
from bfw.reader import *
from bfw.writer import *
from bfw.native.base import *
from bfw.native.limits import *
from bfw.compression.lz4 import LZ4
from bfw.crypto.native import NativeCrypto
from bfw.types.enums import Enum




GAME_DIR       = r'G:\Steam\steamapps\common\HITMAN 3'
RETAIL_DIR     = joinPath(GAME_DIR, 'Retail')
THUMBS_NAME    = 'thumbs.dat'
PACK_DEF_NAME  = 'packagedefinition.txt'
# THUMBS_PATH  = joinPath(RETAIL_DIR, 'thumbs.dat')
# RUNTIME_DIR  = joinPath(GAME_DIR, 'Runtime')
RPKG_SIGNATURE = b'2KPR'
RPKG_DATA_KEY  = bytes.fromhex('DC45A69CD3724CAB')

XTEA_HEADER = bytes.fromhex('223D6F9AB3F8FEB661D9CC1C62DE8341')
XTEA_KEYS   = [ 0x30F95282, 0x1F48C419, 0x295F8548, 0x2A78366D ]
XTEA_DELTA  = 0x61C88647  # uint32
XTEA_SUM    = 0xC6EF3720  # uint32



def i32 (value):
    return CI32(value).value


def u32 (value):
    return CU32(value).value


class Crypto:
    @classmethod 
    def decryptFile (cls, srcPath, dstPath=None, checkHeader=True, checkIntegrity=True):
        srcPath = getAbsPath(srcPath)

        if not isFile(srcPath):
            raise Exception(f'File does not exist: { srcPath }')

        data = readBin(srcPath)
        data = cls()._decryptBuffer(data, checkHeader, checkIntegrity)

        if dstPath:
            createFileDirs(dstPath)
            writeBin(dstPath, data)

        return data

    @classmethod 
    def decryptBuffer (cls, data, checkHeader=True, checkIntegrity=True):
        return cls()._decryptBuffer(data, checkHeader, checkIntegrity)

    def _decryptBuffer (self, data, checkHeader=True, checkIntegrity=True):
        with MemReader(data) as f, BinWriter() as f2:
            if f.remaining() < 20:
                raise Exception('File is truncated')

            header = f.read(16)
            crc32  = f.u32()

            if checkHeader and header != XTEA_HEADER:
                raise Exception('Header is incorrect')            

            assert f.remaining() % 8 == 0

            while f.remaining() > 0:
                a = f.i32()
                b = f.i32()

                a, b = self._decryptBlock(a, b)

                f2.i32(a)
                f2.i32(b)

            data = f2.getRaw()
            data = data.rstrip(b'\x00')

            if checkIntegrity and crc32 != calcCRC32(data):
                raise Exception('Checksums do not match')

            return data

    def _decryptBlock (self, a, b):
        a = u32(a)
        b = u32(b)

        xxSum = u32(XTEA_SUM)

        for i in range(32):
            b = u32(b - u32(i32(u32((((a << 4) & MAX_U32) ^ (a >> 5)) + a)) ^ i32(i32(xxSum) + i32(XTEA_KEYS[(xxSum >> 11) & 3]))))
            xxSum = u32(xxSum + XTEA_DELTA)
            a = u32(a - u32(i32(u32((((b << 4) & MAX_U32) ^ (b >> 5)) + b)) ^ i32(i32(xxSum) + i32(XTEA_KEYS[xxSum & 3]))))

        return i32(a), i32(b)


class PDPartition:
    def __init__ (self):
        self.name       = None
        self.parent     = None
        self.type       = None
        self.patchLevel = None
        self.items      = None
        self.files      = None


class PDPartitionType (Enum):
    Standard = 1
    Addon    = 2


class PackDefParser:
    @classmethod 
    def fromFile (cls, filePath):
        return cls()._parseFile(filePath)

    def _parseFile (self, filePath):
        filePath = getAbsPath(filePath)

        if not isFile(filePath):
            raise Exception(f'File does not exist: { filePath }')

        data = Crypto.decryptFile(filePath)
        data = data.decode('utf-8')
        data = data.split('\n')

        partitions = []
        partition  = None

        for line in data:
            line = line.strip()

            if not line or line.startswith('//'):
                continue

            if line[0] == '@':
                key, *params = [ item.strip() for item in re.split(r'\s+', line) ]

                match key:
                    case '@partition':
                        partition = PDPartition()

                        partition.items = []
                        partition.files = []

                        partitions.append(partition)

                        for param in params:
                            name, value = param.split('=')

                            match name:
                                case 'name':
                                    partition.name = value
                                case 'parent':
                                    if value == 'none':
                                        partition.parent = None
                                    else:
                                        partition.parent = value
                                case 'type':
                                    match value:
                                        case 'standard':
                                            partition.type = PDPartitionType.Standard
                                        case 'addon':
                                            partition.type = PDPartitionType.Addon
                                        case _:
                                            raise Exception(f'Unexpected partition type: { value }')
                                case 'patchlevel':
                                    partition.patchLevel = int(value, 10)
                                case _:
                                    raise Exception(f'Unexpected param name: { name }')
                    case _:
                        raise Exception(f'Unexpected key: { key }')
            else:
                assert partition

                partition.items.append(line)

        chunksDir = getDirPath(filePath)

        for i, partition in enumerate(partitions):
            partition.files.append(joinPath(chunksDir, f'chunk{ i }.rpkg'))

            for j in range(partition.patchLevel):
                partition.files.append(joinPath(chunksDir, f'chunk{ i }patch{ j + 1 }.rpkg'))

        return partitions


class ConfigParam:
    def __init__ (self, key, value):
        self.key   = key
        self.value = value


class ConfigCommand:
    def __init__ (self, command):
        self.command = command


class ConfigUnknown:
    def __init__ (self, value):
        self.value = value


class Config:
    def __init__ (self, sections):
        self.sections = sections

    def __getitem__ (self, key):
        sectionName, key = key.split('/')

        section = self.sections.get(sectionName)

        if section is None:
            raise Exception(f'Config section "{ sectionName }" does not exist')

        for item in section:
            if isinstance(item, ConfigParam) and item.key == key:
                return item.value

        raise Exception(f'Key "{ key }" does not exist in the config section "{ sectionName }"')


class Unpacker:
    @classmethod 
    def unpackGame (cls, gameDir, destDir=None):
        cls()._unpackGame(gameDir, destDir)

    def _unpackGame (self, gameDir, destDir=None):
        if not isDir(gameDir):
            raise Exception(f'Game directory does not exist: { gameDir }')

        thumbsPath = getAbsPath(joinPath(gameDir, 'Retail', THUMBS_NAME))

        if not isFile(thumbsPath):
            raise Exception(f'Thumbs file does not exist: { thumbsPath }')

        if destDir:
            destDir = getAbsPath(destDir)
        else:
            destDir = getAbsPath(joinPath(gameDir, '.extracted'))

        config = self._loadConfig(thumbsPath)

        projectPath = config['application/PROJECT_PATH']
        runtimePath = config['application/RUNTIME_PATH']

        runtimeDir = getAbsPath(joinPath(getDirPath(thumbsPath), projectPath, runtimePath))
        packDefPath = joinPath(runtimeDir, PACK_DEF_NAME)

        if not isFile(packDefPath):
            raise Exception(f'Package definition file does not exist: { packDefPath }')

        packDef = PackDefParser.fromFile(packDefPath)

        pjp(packDef)

    def _loadConfig (self, thumbsPath):
        data = Crypto.decryptFile(thumbsPath)
        data = data.decode('utf-8')
        data = data.split('\n')

        sections = {}
        section  = None

        for line in data:
            line = line.strip()

            if not line or line.startswith('#'):
                continue

            if line[0] == '[':
                assert line[-1] == ']', line

                sectionName = line[1:-1]

                section = sections[sectionName] = []
            else:
                assert section is not None

                match = re.match(r'^([^\s=]+)\s*=\s*(.*)$', line)

                if match:
                    key   = match[1]
                    value = match[2]

                    if value.isnumeric():
                        value = int(value, 10)

                    section.append(ConfigParam(key, value))
                
                    continue

                match = re.match(r'^ConsoleCmd\s*(.*)$', line)

                if match:
                    section.append(ConfigCommand(match[1]))

                    continue

                section.append(ConfigUnknown(line))

        return Config(sections)


class IndexItem:
    def __init__ (self):
        self.unk1         = None
        self.unk2         = None
        self.offset       = None
        self.compSize     = None
        self.decompSize   = None
        self.isEncrypted  = None
        self.isCompressed = None
        self.fileExt      = None
        self.info         = None


def unpack (filePath):    
    filePath = getAbsPath(filePath)

    if not isFile(filePath):
        raise Exception(f'File is not found: { filePath }')

    with openFile(filePath) as f:
        signature = f.read(4)

        assert signature == RPKG_SIGNATURE

        # const: 01 00 00 | chunk (BE): 00 00 | patch (BE): 00 00 | const: 78 78
        unk1      = f.u32()
        chunkId   = f.u8()
        unk2      = f.u8()
        patchId   = f.u8()
        unk3      = f.u16()
        itemCount = f.u32()
        indexSize = f.u32()
        infosSize = f.u32()

        if patchId:
            return

        if patchId > 0:
            count1 = f.u32()
        else:
            count1 = 0

        assert unk1 == 1, unk1
        assert unk2 in [ 0, 1 ], unk2  # chunk28.rpkg == 1
        assert unk3 == 30840, unk3

        print(f'chunkId={ chunkId } patchId={ patchId } itemCount={ itemCount } indexSize={ indexSize } infosSize={ infosSize } count1={ count1 }')

        items = [ IndexItem() for _ in range(itemCount) ]

        indexStart = f.tell()

        for item in items:
            item.unk1         = f.u32()
            item.unk2         = f.u32()
            item.offset       = f.u64()
            num1              = f.u32()
            item.compSize     = num1 & (2 ** 30 - 1)  # TODO: is it correct? Mask must be 0x3fffffff?
            item.isEncrypted  = bool(num1 & (1 << 31))
            item.isCompressed = item.compSize > 0

            # assert bool(num1 & (1 << 30)) == False, (bin(num1), len(bin(num1)) - 1, num1)

        assert (f.tell() - indexStart) == indexSize

        for i in range(count1):
            unk4 = f.u32()
            unk5 = f.u32()
            # print(unk4, unk5)

        infosStart = f.tell()

        for item in items:
            signature       = f.read(4)
            extraSize       = f.u32()
            zeros1          = f.u32()
            item.decompSize = f.u32()
            infoData        = f.read(8 + extraSize)

            assert zeros1 == 0, zeros1

            item.info = (signature, infoData)

            match signature:
                case b'ABJM':
                    pass
                case b'ADCS':
                    pass
                case b'AVSA':
                    pass
                case b'BBIA':
                    pass
                case b'BCIU':
                    pass
                case b'BDIV':
                    pass
                case b'BESA':
                    pass
                case b'BGSW':
                    pass
                case b'BPCE':
                    pass
                case b'BTAM':
                    pass
                case b'BWSD':
                    pass
                case b'BWSW':
                    pass
                case b'CAXF':
                    pass
                case b'COLA':
                    pass
                case b'CXOB':
                    pass
                case b'DMRC':
                    pass
                case b'DMTA':
                    pass
                case b'DXET':
                    pass
                case b'DXTV':
                    pass
                case b'EGLD':
                    pass
                case b'ENIL':
                    pass
                case b'ETAM':
                    pass
                case b'FEDS':
                    pass
                case b'FXFG':
                    pass
                case b'GNLC':
                    pass
                case b'GRIA':
                    pass
                case b'GROB':
                    pass
                case b'ITAM':
                    pass
                case b'IXFG':
                    pass
                case b'KNBW':
                    pass
                case b'KSMB':
                    pass
                case b'LERP':
                    pass
                case b'LTID':
                    pass
                case b'MEWW':
                    pass
                case b'MIRP':
                    pass
                case b'MUNE':
                    pass
                case b'NOSJ':
                    pass
                case b'NTRM':
                    pass
                case b'OPER':
                    pass
                case b'PHSY':
                    pass
                case b'PMET':
                    pass
                case b'PVAN':
                    pass
                case b'RCOL':
                    pass
                case b'RTRM':
                    pass
                case b'SAXF':
                    pass
                case b'SERE':
                    pass
                case b'SERO':
                    pass
                case b'SEWW':
                    pass
                case b'TCIU':
                    pass
                case b'TESA':
                    pass
                case b'TGSW':
                    pass
                case b'TPCE':
                    pass
                case b'TPPC':
                    pass
                case b'TTAM':
                    pass
                case b'TWSW':
                    pass
                case b'TXET':
                    pass
                case b'ULBC':
                    pass
                case b'ULBT':
                    pass
                case b'VEWW':
                    pass
                case b'VLTR':
                    pass
                case b'VXFG':
                    pass
                case b'XBIA':
                    pass
                case b'XDIG':
                    pass
                case b'ZBIA':
                    pass
                case _:
                    assert 0, (f.tell() - 4, name)

            item.fileExt = '.' + signature.decode('ascii').lower()[::-1]

        assert (f.tell() - infosStart) == infosSize

        for item in items:
            f.seek(item.offset)

            if item.isCompressed:
                rawDataSize = item.compSize
            else:
                rawDataSize = item.decompSize

            if rawDataSize:
                data = f.ba(rawDataSize)

                if item.isEncrypted:
                    data = NativeCrypto.xorBuffer(data, RPKG_DATA_KEY)

                if item.isCompressed:
                    data = LZ4.decompress(data, item.decompSize)
            else:
                data = b''

            # if item.isEncrypted and item.isCompressed and len(data) >= 1024 * 1024:
            #     writeBin(rf'G:\Steam\steamapps\common\HITMAN 3\Runtime\_trash\{ item.offset }.bin', data)
            #     print(item.offset); exit()

            # if item.info[0] == b'XDIG':
            #     writeBin(rf'G:\Steam\steamapps\common\HITMAN 3\Runtime\_trash\{ item.offset }{ item.fileExt }', data)
            #     print(item.offset); # exit()


def unpackAll ():
    for filePath in iterFiles(joinPath(GAME_DIR, 'Runtime'), False, [ '.rpkg' ]):
        print(filePath)

        unpack(filePath)

        print(' ')



def main ():
    Crypto.decryptFile(r"G:\Steam\steamapps\common\Hitman™\Runtime\packagedefinition.txt", r"G:\Steam\steamapps\common\Hitman™\Runtime\packagedefinition.dec.txt")
    # Crypto.decryptFile(joinPath(RUNTIME_DIR, PACK_DEF_NAME), joinPath(RUNTIME_DIR, 'packagedefinition.decrypted.txt'))
    # Crypto.decryptFile(joinPath(GAME_DIR, 'Retail', THUMBS_NAME), joinPath(GAME_DIR, 'Retail', 'thumbs.decrypted.dat'))

    # PackDefParser.fromFile(joinPath(RUNTIME_DIR, PACK_DEF_NAME))

    # Unpacker.unpackGame(GAME_DIR)

    # unpack(r'G:\Steam\steamapps\common\HITMAN 3\Runtime\chunk0patch1.rpkg'); exit()

    # unpackAll()




if __name__ == '__main__':
    main()

'''
AIBB <- AI BehaviorTreeEntityBlueprint
AIBX <- AI BehaviorTreeEntityType
AIBZ <- AI CompiledBehaviorTreeResource
AIRG <- AI ReasoningGridResource
ALOC <- Physics / PhysX
ASEB <- AspectEntityBlueprint
ASET <- AspectEntityType
ASVA <- AnimSetVariation
ATMD <- AMD
BLOB <- ResourceBlob
BMSK <- BoneMask
BORG <- AnimationBoneData
CBLU <- CppEntityBlueprint
CLNG <- DialogCascadingLanguageDependencies
CPPT <- CppEntityType
CRMD <- CrowdMapDataResource
DITL <- DialogSoundTemplateList
DLGE <- DialogEvent
ECPB <- ExtendedCppEntityBlueprint
ECPT <- ExtendedCppEntityType
ENUM <- EnumType
ERES <- EntityResource
FXAC <- ACTOR
FXAS <- ANIMATION SET
GFXF <- SCALEFORM FLASH ARCHIVES FOR FLASH / SCALEFORM
GFXI <- SCALEFORM IMAGES
GFXV <- SCALEFORM VIDEO / USM/CRI 
GIDX <- GLOBAL RESOURCES IDX
HIKC <- HIKCharacter
IMAP <- IDMap
JSON <- JSON RESOURCE
LINE <- TEXTLINE
LOCR <- LOCALIZATION LANGUAGE / TEXT
MATB <- RENDER MATERIAL EntityBlueprint
MATE <- RENDER MATERIAL Effect
MATI <- RENDER MATERIAL Instance
MATT <- RENDER MATERIAL EntityType
MJBA <- Animation
MRTN <- Network
MRTR <- RIG
NAVP <- NavpowerNavmesh
ORES <- ONLINE RESOURCES
PREL <- Preload
PRIM <- MODELS / RenderPrimitive
REPO <- REPOSITORY FILE
RTLV <- RuntimeLocalizedVideo
SCDA <- ScatterData
SCTX <- ScatterTexture
SDEF <- SoundAmbienceDefs
TBLU <- TemplateBlueprint
TELI <- TextList
TEMP <- Template
TEXD <- DummyTextureData / DDS TEXTURES
TEXT <- RenderTexture / MORE DDS TEXTURES
UICB <- UIControl
UICD <- UIControl
UICT <- UIControl
VIDB <- VideoDatabaseResource
VTXD <- VertexData
WBNK <- WwiseBank
WSGB <- AudioStateBlueprint
WSGT <- AudioStateType
WSWB <- AudioSwitchBlueprint
WSWT <- AudioSwitchType
WWEM <- Wem AUDIO DATA CONTAINER FOR WWISE
WWEV <- Wwise EVENT
WWFX <- Wwise FX
YSHP <- PHYSICS SYSTEM
'''