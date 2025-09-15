# Mafia II Tools

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



GAME_DIR = r'G:\Steam\steamapps\common\Mafia II'
SDS_DIR  = joinPath(GAME_DIR, 'pc', 'sds')

SDS_SIGNATURE = b'SDS\x00'
SDS_VERSION   = 19

SDS_BLOCK_INFO_SIGNATURE = b'\x55\x45\x7A\x6C'

SDS_ENCRYPT_MARK   = b'\x00\x00\x00\x00\x00\x00\x00\x45\x8B\x1A\xD9\x10\x00\x00\x00/tables/fsfh.bin\x01'
SDS_ENCRYPT_KEYS   = [ 0x73766E46, 0x6D454D5A, 0x336A6D68, 0x38425072 ]
SDS_ENCRYPT_PARAMS = [
    (0x79FB0B01, 0x4B989BCD, 5),  # sum, delta, rounds
    (0xA62336C0, 0x9D3119B6, 32)
]

SDS_RES_TYPE_TO_EXT = {
    'Actors':             '.act',   # no path ~
    'AnimalTrafficPaths': '.atp',   # no path ???
    'Collisions':         '.col',   # no path ??~
    'Cutscene':           '.cts',   # no path ??~
    'Effects':            '.fx',    # no path ???
    'EntityDataStorage':  '.eds',   # no path ??~
    'FrameNameTable':     '.fntbl', # no path ~
    'FrameResource':      '.fres',  # no path ??~ (similar to Collisions?)
    'FxActor':            '.fxa',   # no path ?~~ (OC3 FaceFX)
    'FxAnimSet':          '.fxas',  # no path ?~~ (OC3 FaceFX)
    'VertexBufferPool':   '.vbp',   # no path ??? (mesh? 950mb)
    'IndexBufferPool':    '.ibp',   # no path ??? (mesh VIs? 230mb)
    'ItemDesc':           '.idsc',  # no path ??? (small)
    'NAV_AIWORLD_DATA':   '.naid',  # no path ??~ (Kynapse) (09_Slaughterhouse-Inetrier::AIWorldPart-slaughi-bin-file)
    'NAV_HPD_DATA':       '.nhpdd', # no path (kynapse .hpd file)
    'NAV_OBJ_DATA':       '.nod',   # no path (kynapse .obj file)
    'PREFAB':             '.pfab',  # no path ???
    'Script':             '.scr',   # no path ??? (lua 5.1 compiled script)
    'Speech':             '.spch',  # no path ~
    'Table':              '.tbl',   # no path ~
    'Translokator':       '.tlr',   # no path ???
    'Animated Texture':   '.anmt',  # has path ~
    'Animation2':         '.anm2',  # has path ???
    'AudioSectors':       '.asec',  # has path ??~
    'MemFile':            '.memf',  # has path ?~~
    'Mipmap':             '.texmm', # has path ++?
    'Sound':              '.snd',   # has path +++
    'SoundTable':         '.stbl',  # has path ?~~
    'Texture':            '.tex',   # has path ++?
    'XML':                '.bxml',  # has path +++
}

SDS_EXT_TO_RES_TYPE = { v: k for k, v in SDS_RES_TYPE_TO_EXT.items() }

SDS_RES_TYPE_TO_EXT = {
    'Actors':             lambda: None,
    'AnimalTrafficPaths': lambda: None,
    'Collisions':         lambda: None,
    'Cutscene':           lambda: None,
    'Effects':            lambda: None,
    'EntityDataStorage':  lambda: None,
    'FrameNameTable':     lambda: None,
    'FrameResource':      lambda: None,
    'FxActor':            lambda: None,
    'FxAnimSet':          lambda: None,
    'VertexBufferPool':   lambda: None,
    'IndexBufferPool':    lambda: None,
    'ItemDesc':           lambda: None,
    'NAV_AIWORLD_DATA':   lambda: None,
    'NAV_HPD_DATA':       lambda: None,
    'NAV_OBJ_DATA':       lambda: None,
    'PREFAB':             lambda: None,
    'Script':             lambda: None,
    'Speech':             lambda: None,
    'Table':              lambda: None,
    'Translokator':       lambda: None,
    'Animated Texture':   lambda: None,
    'Animation2':         lambda: None,
    'AudioSectors':       lambda: None,
    'MemFile':            lambda: None,
    'Mipmap':             lambda: None,
    'Sound':              lambda: None,
    'SoundTable':         lambda: None,
    'Texture':            lambda: None,
    'XML':                lambda: None,
}

DDS_SIGNATURE  = b'DDS '
FSB4_SIGNATURE = b'FSB4'


class SDSPlatform (Enum2):
    PC   = b'PC\x00\x00'
    X360 = b'XBOX'
    PS3  = b'PS3\x00'


def toU32 (num):
    return CU32(num).value

def u32ls (num, shift):
    assert 0 <= shift
    return (toU32(num) << shift) & MAX_U32

def u32rs (num, shift):
    assert 0 <= shift
    return toU32(num) >> shift

def u32add (a, b):
    return toU32(toU32(a) + toU32(b))

def u32sub (a, b):
    return toU32(toU32(a) - toU32(b))

def u32mul (a, b):
    return toU32(toU32(a) * toU32(b))

def calcFNV32 (data):
    checksum = 0x811C9DC5

    for byte in data:
        checksum = u32mul(checksum, 0x1000193) ^ byte

    return checksum

def decryptBuffer (data, keys, params):
    assert isinstance(data, bytearray)

    size = len(data) // 8 * 8

    if not size:
        return data

    delta  = params[1]
    rounds = params[2]

    for i in range(0, size, 8):
        sum_ = params[0]

        v0, v1 = struct.unpack('<II', data[i:i + 8])

        for _ in range(rounds):
            v1 = u32sub(v1, u32add(u32ls(v0, 4), keys[2]) ^ u32add(v0, sum_) ^ u32add(u32rs(v0, 5), keys[3]))
            v0 = u32sub(v0, u32add(u32ls(v1, 4), keys[0]) ^ u32add(v1, sum_) ^ u32add(u32rs(v1, 5), keys[1]))

            sum_ = u32sub(sum_, delta)

        data[i:i + 8] = struct.pack('<II', v0, v1)

    return data

def decryptFile (srcPath, dstPath):
    with openFile(srcPath, dstPath) as f:
        if f.getSize() < (0x10000 + 16):
            return False

        f.seek(128)

        mark = f.read(32)

        if mark != SDS_ENCRYPT_MARK:
            return False

        f.seek(0x10000)

        data = f.ba()

    params = None

    for candidate in SDS_ENCRYPT_PARAMS:
        header = decryptBuffer(data[:16], SDS_ENCRYPT_KEYS, candidate)

        if header[:4] != SDS_SIGNATURE:
            continue

        checksum = struct.unpack('<I', header[12:16])[0]

        if calcFNV32(header[:12]) == checksum:
            params = candidate            
            break

    assert params

    data = decryptBuffer(data, SDS_ENCRYPT_KEYS, params)

    assert data[:4] == SDS_SIGNATURE

    writeBin(dstPath, data)

    return True

# BINk
# Facial animations by OC3 Ent.
# Autodesk kynapse
# PhysX
# FMOD FSB4
# Scripts - lua
def unpack (filePath, unpackDir=None):
    gameRoot = findAncestorDirByFile(getDirPath(filePath), 'mafia2.exe')

    if not gameRoot:
        raise Exception('Game root dir not found')

    dstRelDir = dropExt(filePath)
    dstRelDir = getRelPath(dstRelDir, gameRoot)
    dstRelDir = joinPath('_', dstRelDir)

    filePath = getAbsPath(filePath)

    if not isFile(filePath):
        raise Exception(f'File is not found: { filePath }')

    if unpackDir is None:
        unpackDir = filePath + '.unpacked'

    decFilePath = filePath + '.decrypted'

    if isFile(decFilePath) or decryptFile(filePath, decFilePath):
        filePath = decFilePath
        print('Replaced with decrypted SDS')

    data = None

    with openFile(filePath) as f:
        header = f.read(12)

        f.seek(0)

        signature = f.read(4)

        if signature != SDS_SIGNATURE:
            raise Exception(f'Invalid signature: { signature }')

        version    = f.u32()    # +
        platform   = f.read(4)  # +
        headerHash = f.u32()

        if version != SDS_VERSION:
            raise Exception(f'Unsupported version: { version }')

        if platform != SDSPlatform.PC:
            raise Exception(f'Unsupported platform: { platform }')
        
        if calcFNV32(header) != headerHash:
            raise Exception(f'Invalid header hash')
            
        # signature-- always19--- always17232 always16...
        # always72--- unk9bytsOff xmlOffset-- ttlSlotRam- 
        # ttlSlotVram ttlOtherRam ttlOthrVram always1---- 
        # always_null_terminated_string------------------  // string "73979+" or uint 11065
        # xmlEntryCnt C4 53 2C ED stringCount ........... 
        # ....... fixedString[stringCount] ..............
        # .. 55 45 7A 6C 00 40 00 00 04 74 29 00 00 01 00 // "55 45 7A 6C 00 40 00 00 04" - unknown 9 bytes, same in all SDSes
        # 40 00 00 20 00 00 00 00 40 01 00 01 00 0F 08 54 
        # 29 00 00 00 00 00 00 00 00 00 00 00 00 00 00 

        resTypesOffset  = f.u32()
        blockInfoOffset = f.u32()
        xmlOffset       = f.u32()
        ttlSlotRam      = f.u32()  # + 
        ttlSlotVram     = f.u32()  # + 
        ttlOtherRam     = f.u32()  # + 
        ttlOthrVram     = f.u32()  # + 
        always1         = f.u32()
        unkStr1         = f.string(16)
        resCount        = f.u32()
        unk1            = f.u32()  # checksum???

        assert f.tell() == resTypesOffset, (f.tell(), resTypesOffset)

        f.seek(resTypesOffset)

        resTypeCount = f.u32()

        assert resTypesOffset == 72, resTypesOffset
        assert always1 == 1, always1
        assert unkStr1 == '73979+', unkStr1

        resTypes = {}

        # Actors
        # AnimalTrafficPaths
        # Animated Texture
        # Animation2
        # AudioSectors
        # Collisions
        # Cutscene
        # Effects
        # EntityDataStorage
        # FrameNameTable
        # FrameResource
        # FxActor
        # FxAnimSet
        # IndexBufferPool
        # ItemDesc
        # MemFile
        # Mipmap
        # NAV_AIWORLD_DATA
        # NAV_HPD_DATA
        # NAV_OBJ_DATA
        # PREFAB
        # Script
        # Sound
        # SoundTable
        # Speech
        # Table
        # Texture
        # Translokator
        # VertexBufferPool
        # XML
        for i in range(resTypeCount):
            resTypeId   = f.u32()
            resNameSize = f.u32()
            resName     = f.fixedString(resNameSize)
            unk2        = f.u32()

            resTypes[resName] = resTypes[resTypeId] = {
                'id':   resTypeId,
                'name': resName,
                'unk2': unk2
            }

        assert f.tell() == blockInfoOffset

        f.seek(blockInfoOffset)

        signature = f.read(4)

        if signature != SDS_BLOCK_INFO_SIGNATURE:
            raise Exception(f'Invalid block signature: { signature }')

        blockAlignment = f.u32()
        unk3           = f.u8()

        assert unk3 == 4, unk3

        with BinWriter() as bw:
            while True:
                contentSize  = f.u32()
                isCompressed = f.u8()

                assert isCompressed in [ 0, 1 ], isCompressed

                if not contentSize:
                    break

                if isCompressed:
                    decompSize = f.u32()

                    unk6 = f.u32()
                    unk7 = f.u32()
                    unk8 = f.u32()

                    assert decompSize <= blockAlignment, (decompSize, blockAlignment)
                    assert unk6 == 32, unk6
                    assert unk7 == 81920, unk7
                    assert unk8 == 135200769, unk8

                    compSize = f.u32()

                    unk9 = f.u32()
                    unk10 = f.u32()
                    unk11 = f.u32()

                    assert (contentSize - 32) == compSize
                    assert unk9 == 0, unk9
                    assert unk10 == 0, unk10
                    assert unk11 == 0, unk11

                    # f.skip(compSize)
                    data = f.read(compSize)
                    data = decompressData(data)
                else:
                    data = f.read(contentSize)

                bw.write(data)

            data = bw.getRaw()

        assert f.tell() == xmlOffset

        f.seek(xmlOffset)

        xml = f.read()
        xml = XMLNode(xml)

        resources = [ None ] * resCount

        # ResourceInfo.CustomDebugInfo always None
        # ResourceInfo.TypeName
        # ResourceInfo.SourceDataDescription
        # ResourceInfo.SlotRamRequired
        # ResourceInfo.SlotVramRequired
        # ResourceInfo.OtherRamRequired
        # ResourceInfo.OtherVramRequired
        for i, info in enumerate(xml.findAll('ResourceInfo')):
            res = resources[i] = {}

            for param in info.getChildren():
                key   = param.getTag()
                value = param.getText().strip()

                if param.getAttribute('__type') == 'Int':
                    value = int(value, 10)
                elif not value:
                    value = None

                if key == 'SourceDataDescription' and value.lower() == 'not available':
                    value = None

                res[key] = value

    with MemReader(data) as f:
        for res in resources:
            start = f.tell()

            header = f.read(26)

            f.seek(start)

            typeId   = f.u32()
            size     = f.u32()
            version  = f.u16()
            slotRam  = f.u32()
            slotVram = f.u32()
            otherRam = f.u32()
            othrVram = f.u32()
            checksum = f.u32()

            assert calcFNV32(header) == checksum
            assert version in [ 0, 1, 2, 3, 4, 5, 6, 28 ], version
            assert resTypes[typeId]['name'] == res['TypeName']
            assert slotRam == res['SlotRamRequired']
            assert slotVram == res['SlotVramRequired']
            assert otherRam == res['OtherRamRequired']
            assert othrVram == res['OtherVramRequired']

            data = f.read(size - 30)

            resTypeName = res['TypeName']
            resTypeExt  = SDS_RES_TYPE_TO_EXT[resTypeName]
            resPath     = res['SourceDataDescription']

            if resPath is None:
                dstName = f'{start:08X}{ resTypeExt }'
                dstPath = joinPath(dstRelDir, dstName)
            elif resPath == getBaseName(resPath):
                dstName = f'{ resPath }{ resTypeExt }'
                dstPath = joinPath(dstRelDir, dstName)
            else:
                dstPath = resPath + resTypeExt

            dstPath = getAbsPath(joinPath(unpackDir, dstPath))

            print(dstPath)

            createFileDirs(dstPath)

            writeBin(dstPath, data)

# Target systems:
# - UnknownTargetSystem
# - AI_BRAIN_CFG
# - AI_DYNCOV_DATA
# - AnimalTraffic
# - AnimEngineConfig
# - AudioCarEffects
# - AudioContextsConfig
# - AudioReverbs
# - COAT_PARAMS
# - forceFeedbackEffects
# - Human2Config
# - JukeBox_Params
# - RadioConfig
# - SoundMixConfig
# - StreamedMusicTable
# - SYS_FACEFX
class BinXML:
    def __init__ (self):
        self.unk1            = None
        self.unk2            = None
        self.version         = None
        self.encoding        = None
        self.targetSystem    = None
        self.xmlPath         = None
        self.namesBaseOffset = None

    @classmethod
    def parseFile (cls, filePath):
        if not isFile(filePath):
            raise OSError(f'File does not exist: { filePath }')

        return cls.parseBuffer(readBin(filePath))

    @classmethod
    def parseBuffer (cls, data):
        return BinXML().parseData(data)

    def parseData (self, data):
        with MemReader(data) as f:
            strSize           = f.u32()
            self.targetSystem = f.fixedString(strSize)
            self.unk1         = f.u8()
            strSize           = f.u32()
            self.xmlPath      = f.fixedString(strSize)
            self.version      = f.u8()
            self.unk2         = f.u32()  # TODO: related to file size (~5x times biger)

            assert self.unk1 in [ 0, 1, 32, 232 ], self.unk1

            # print(self.targetSystem)
            # print(self.xmlPath)
            # print(f'unk1={ self.unk1 }')
            # print(f'unk2={ self.unk2 }')

            if self.version == 0:
                self.encoding = 'ISO-8859-1'
                return self.parseV0(f)
            elif self.version == 1:
                self.encoding = 'utf-8'
                return self.parseV1(f)
            else:
                raise Exception('Unknown parser version')

    def parseV0 (self, f):
        unk4                 = f.u8()
        itemsSize            = f.u32()
        self.namesBaseOffset = f.tell()

        assert unk4 == 0, unk4

        f.skip(itemsSize)

        root = self.readNodeV0(f)
        root = self.normalizeRootV0(root)
        xml  = self.buildXML(root)

        return xml

    def readNameV0 (self, f, offset):
        origPos = f.tell()

        f.seek(self.namesBaseOffset + offset)

        # 1 - [string] node value
        # 4 - [string] node tag, attr name, attr value
        # 2 - [bin] unknown value
        # 3 - [bin] unknown value
        # 5 - [bin] unknown value
        # 8 - [bin] unknown value
        nameType = f.u32()
        unk5     = f.u32()

        if nameType in [ 1, 4 ]:
            value = f.string(encoding=self.encoding)

        elif nameType in [ 2, 3, 5, 8 ]:
            value = f.string(encoding=None)
            value = f'{{type:{ nameType }}}:{ formatHex(value) }'

        else:
            raise Exception(f'Unknown name type: { nameType }')

        assert unk5 == 0, unk5

        f.seek(origPos)

        return value

    def readNodeV0 (self, f, expectedId=None):
        tagOffset     = f.u32()
        contentOffset = f.u32()
        nodeId        = f.u32()
        childCount    = f.u32()

        # TODO: there are cases when both content text and child elements are present
        # assert not childCount or not contentOffset, (childCount, contentOffset)

        if expectedId is not None:
            assert nodeId == expectedId, (nodeId, expectedId)

        if childCount:
            childIds = f.u32(childCount, asArray=True)
        else:
            childIds = []

        attrCount = f.u32()
        nodeTag   = self.readNameV0(f, tagOffset)
        nodeAttrs = [ None ] * attrCount

        for i in range(attrCount):
            nameOffset  = f.u32()
            attrName    = self.readNameV0(f, nameOffset)
            valueOffset = f.u32()
            attrValue   = self.readNameV0(f, valueOffset)

            nodeAttrs[i] = (attrName, attrValue)

        if childCount:
            nodeValue = [ self.readNodeV0(f, childIds[i]) for i in range(childCount) ]
        elif contentOffset:
            nodeValue = self.readNameV0(f, contentOffset)
        else:
            nodeValue = ''

        return (nodeTag, nodeAttrs, nodeValue)

    def normalizeRootV0 (self, root):
        tag, attrs, value = root

        assert not tag, tag
        assert len(value) <= 1

        root = value[0]  # TODO: what if there are no nodes?

        self.addMetaAttrs(root[1])

        return root

    def parseV1 (self, f):
        root = self.readRootNodeV1(f)
        root = self.normalizeRootV1(root)
        xml  = self.buildXML(root)

        return xml

    def readRootNodeV1 (self, f):
        itemType = self.readItemHeaderV1(f)

        assert itemType == 1, itemType

        return self.readNodeV1(f)

    def readItemHeaderV1 (self, f):
        itemSize = f.u16()  # with string terminator
        itemType = f.u8()

        return itemType

    def readValueV1 (self, f):
        childCount = f.u8()   # TODO: or what is it?
        valueSize  = f.u16()  # TODO: is it u16 or u8?

        assert childCount == 0, childCount

        return f.string(valueSize + 1, encoding=self.encoding)

    def readAttrV1 (self, f):
        nameSize = f.u8()
        name     = f.string(nameSize + 1, encoding=self.encoding)
        itemType = self.readItemHeaderV1(f)

        assert itemType == 4, itemType

        value = self.readValueV1(f)

        return (name, value)

    def readNodeV1 (self, f):
        tagSize    = f.u8()
        childCount = f.u8()  # TODO: is it u8 or u16?
        unk5       = f.u8()
        attrCount  = f.u8()

        assert unk5 == 0, valueSize

        nodeTag   = f.string(tagSize + 1, encoding=self.encoding)
        nodeAttrs = [ None ] * attrCount
        nodeValue = [ None ] * childCount

        for i in range(childCount):
            itemType = self.readItemHeaderV1(f)

            assert itemType in [ 1, 4 ], itemType

            if itemType == 1:
                nodeValue[i] = self.readNodeV1(f)
            elif itemType == 4:
                assert childCount == 1
                nodeValue = self.readValueV1(f)

        for i in range(attrCount):
            itemType = self.readItemHeaderV1(f)

            assert itemType == 5, itemType

            nodeAttrs[i] = self.readAttrV1(f)

        return (nodeTag, nodeAttrs, nodeValue)

    def normalizeRootV1 (self, root):
        self.addMetaAttrs(root[1])

        return root

    def addMetaAttrs (self, attrs):
        attrs.insert(0, ('_bxml-version', str(self.version)))
        attrs.insert(1, ('_unk1', str(self.unk1)))
        attrs.insert(2, ('_unk2', str(self.unk2)))
        attrs.insert(3, ('_target-system', self.targetSystem))
        attrs.insert(4, ('_original-path', self.xmlPath))

    def buildXML (self, node, xml=None, level=0):
        if level == 0:
            xml = [
                f'<?xml version="1.0" encoding="{ self.encoding }" standalone="yes"?>'
            ]

        indent = ' ' * (4 * level)

        tag, attrs, value = node

        attrs = ''.join([ f' { k }={ toJson(v) }' for k, v in attrs ])

        if len(value) == 0:
            xml.append(f'{ indent }<{ tag }{ attrs }/>')
        elif isinstance(value, list):
            xml.append(f'{ indent }<{ tag }{ attrs }>') 

            for child in value:
                self.buildXML(child, xml, level + 1)

            xml.append(f'{ indent }</{ tag }>')
        else:
            xml.append(f'{ indent }<{ tag }{ attrs }>{ value }</{ tag }>')

        if level == 0:
            xml = '\n'.join(xml)

        return xml

# ---------------------------------------------------------

def unpackTextureBuffer (data, isBaseTex):
    with MemReader(data) as f:
        unk1       = f.u32()
        unk2       = f.u32()
        unk3       = f.u8()
        hasMipMaps = False

        if isBaseTex:
            hasMipMaps = bool(f.u8())

        data = f.read()

        assert data[:4] == DDS_SIGNATURE

        return data

def createTexturePath (filePath, isBaseTex):
    ext = getExt(filePath)

    if ext == '.dds':
        filePath = dropExt(filePath)

    if isBaseTex:
        ext = '.tex.dds'
    else:
        ext = '.mm.dds'

    return filePath + ext

# ---------------------------------------------------------

def unpackSoundBuffer (data):
    with MemReader(data) as f:
        pathSize     = f.u8()
        internalPath = f.fixedString(pathSize)
        dataSize     = f.u32()

        data = f.read(dataSize)

        assert not getExt(internalPath)
        assert data[:4] == FSB4_SIGNATURE
        assert not f.remaining()

        return data

def createSoundPath (filePath):
    return filePath + '.fsb4'

# ---------------------------------------------------------

def unpackSoundTableBuffer (data):
    with MemReader(data) as f:
        f.seek(27647)

        while f.tell() < 189819:
            unk0     = f.u32()
            unk1     = f.u16()
            count    = f.u8()

            print(unk0, unk1, count)

            for i in range(count):
                pathSize = f.u8()
                path     = f.fixedString(pathSize)
                _b       = f.read(5)

                print(path, '|', formatHex(_b))
                
            print(f.tell())

            # f.skip(5)


# ---------------------------------------------------------

def unpackAll (gameDir, unpackDir=None):
    for filePath in iterFiles(gameDir, True, [ '.sds' ]):
        print(filePath)

        unpack(filePath, unpackDir)

        print(' ')

    # print('\n'.join(sorted(list(_c.keys()))))
    # print(toJson(_c))

def main ():
    unpackDir = joinPath(GAME_DIR, '.unpacked')

    # unpackAll(GAME_DIR, unpackDir)
    # unpack(joinPath(SDS_DIR, 'weapons', 'weapons.sds'))
    # unpack(joinPath(SDS_DIR, 'sound_city', 'sound_city.sds'))
    # unpack(joinPath(GAME_DIR, 'pc', 'dlcs', 'cnt_greaser', 'sds', 'cars', 'hot_rod_2.sds'))

    unpackSoundTableBuffer(readBin(r"G:\Steam\steamapps\common\Mafia II\.unpacked\_\dlcs\cnt_joes_adventures\sds\tables\ingame\SoundTable.bin.stbl"))

    # for filePath in iterFiles(unpackDir, True, [ '.stbl' ]):
    #     print(filePath)
    #     unpackSoundBuffer(readBin(filePath))
    #     print(' ')



if __name__ == '__main__':
    main()
    