# Wolfenstein II: The New Colossus Extractor

import os, struct, json, ctypes, zlib, gzip, math, copy, regex, threading, time
import sys
import pefile
from collections import namedtuple
from datetime import datetime
from typing import Union, Any, Tuple

import pyoodle

GAME_DIR = r'G:\Steam\steamapps\common\Wolfenstein.II.The.New.Colossus'
SIGNATURE_IDCL = b'IDCL'
SIGNATURE_TEXDB = b'\x4F\xA5\xC2\x29\x2E\xF3\xC7\x61'

class PEExportItem:
    def __init__ (self, name=None, ordinal=None):
        self.name = name
        self.ordinal = ordinal

    def __str__ (self):
        return self.name.decode('utf-8') if self.name else ''


class OodleLib:
    def __init__ (self, filePath=None, majorVersion=None):
        self.filePath = filePath
        self.majorVersion = majorVersion
        self.exportTable = None
        self.exportNames = None

    def getExportTable (self):
        if not self.exportTable:
            self.exportTable = getDLLExportTable(self.filePath)

        return self.exportTable

    def getExportNames (self):
        if not self.exportNames:
            self.exportNames = [ str(item) for item in self.getExportTable() ]

        return self.exportNames

    def getMajorVersion (self):
        return self.majorVersion

    def getPath (self):
        return self.filePath


def getOodleLibsInDir (libsDir):
    if not isinstance(libsDir, str) or not os.path.isdir(libsDir):
        raise NotADirectoryError('Directory not found')

    libs = []

    for item in os.listdir(libsDir):
        itemPath = os.path.join(libsDir, item)

        if os.path.isfile(itemPath):
            matches = regex.match(OODLE_DLL_REGEX, item)

            if matches:
                majorVersion = int(matches.group(1))

                libs.append(OodleLib(itemPath, majorVersion))

    return sorted(libs, key=lambda item: item.getMajorVersion())


# https://github.com/erocarrera/pefile/blob/wiki/UsageExamples.md
def getDLLExportTable (libPath):
    if not isinstance(libPath, str) or not os.path.isfile(libPath):
        raise FileNotFoundError('DLL not found')

    pe = pefile.PE(libPath, fast_load=True)
    pe.parse_data_directories(directories=[
        pefile.DIRECTORY_ENTRY['IMAGE_DIRECTORY_ENTRY_EXPORT']
    ])

    exportTable = [ PEExportItem(symbol.name, symbol.ordinal) for symbol in pe.DIRECTORY_ENTRY_EXPORT.symbols ]

    return exportTable


def getOodleLibDiff (libsDir):
    if not isinstance(libsDir, str) or not os.path.isdir(libsDir):
        raise NotADirectoryError('Directory not found')

    libs = getOodleLibsInDir(libsDir)
    diff = []

    for i in range(len(libs) - 1):
        lib1 = libs[i]
        lib2 = libs[i + 1]

        v1items = set(lib1.getExportNames())
        v2items = set(lib2.getExportNames())

        diff.append({
            'versions': (lib1.getMajorVersion(), lib2.getMajorVersion()),
            'diff': {
                '+': list(v2items - v1items),
                '-': list(v1items - v2items)
            }
        })

    return diff

# ----------------------------------------------------------------------------------------------------------------------



def abort (*args, **kwargs):
    if args or kwargs:
        print(*args, **kwargs)

    sys.exit(0)


def formatBytes (byteSeq):
    return ' '.join([ '{:02X}'.format(b) for b in byteSeq ])


def readStruct (structFormat, descriptor):
    structSize = struct.calcsize(structFormat)
    dataBuffer = descriptor.read(structSize)

    if len(dataBuffer) != structSize:
        return None

    items = struct.unpack(structFormat, dataBuffer)

    return items[0] if len(items) == 1 else items


def readNullString (descriptor):
    buff = b''

    while True:
        byte = descriptor.read(1)

        if byte == b'\x00':
            break

        buff += byte

    return buff.decode('utf-8')


def getFileCRC32 (filePath, startPos=0):
    with open(filePath, 'rb') as f:
        checksum = 0

        f.seek(startPos)

        while True:
            data = f.read(8192)

            if not data:
                break

            checksum = zlib.crc32(data, checksum)

        return checksum

def formatDateMicroseconds (value):
    if not isinstance(value, int):
        return ''

    dt = datetime.fromtimestamp(value // 1000000)

    return dt.strftime('%d.%m.%Y %H:%M:%S')


def printTable (title, header, values, formatFns=None):
    sep = ' | '
    rows = [ list(row) for row in [ header, *values ] ]
    maxRowLength = -1

    formatFns = formatFns if isinstance(formatFns, list) else []
    formatFns.insert(0, None)

    for i, row in enumerate(rows):
        if i == 0:
            row.insert(0, '#')
        else:
            row.insert(0, i - 1)

        maxRowLength = max(maxRowLength, len(row))

    maxLengths  = [ -1 for _ in range(maxRowLength) ]
    numericCols = [ True for _ in range(maxRowLength) ]

    for i, row in enumerate(rows):
        for j, value in enumerate(row):
            if i > 0 and j < len(formatFns) and formatFns[j]:
                value = formatFns[j](value)

            value = str(value)
            row[j] = value
            maxLengths[j] = max(maxLengths[j], len(value))

            if i > 0:
                numericCols[j] = numericCols[j] and value.isnumeric()

    print('\n{}'.format(title))

    for i, row in enumerate(rows):
        for j, value in enumerate(row):
            valueLength = maxLengths[j]

            if numericCols[j]:
                row[j] = value.rjust(valueLength)
            else:
                row[j] = value.ljust(valueLength)

        print(sep.join(row))

        if i == 0:
            print('-' * (sum(maxLengths) + len(sep) * max(0, len(maxLengths) - 1)))

    print(' ')

_tmp = None

# See: Doom Resource Explorer
def unpackResources (filePath):
    global _tmp

    if not os.path.isfile(filePath):
        print('File doesn\'t exist:', filePath)
        return

    fileName = os.path.basename(filePath)
    fileSize = os.path.getsize(filePath)

    print('{} {} '.format(fileName, fileSize).ljust(200, '-'))

    with open(filePath, 'rb') as f:
        # +   -          -           -  -  -           -    -         -           +      +      +      -      -  -   +       -   +       -   +        -   -   -   +        -  +         -   +        -
        # 1   2          3           4  5  6           7    8         9           10     11     12     13     14 15  16      17  18      19  20       21  22  23  24       25 26        27  28       29
        # 12, 236763720, 3457587392, 0, 1, 4294967295, 255, 81805874, 2219275889, 50839, 15542, 87794, 101679, 0, 0, 5495352, 0, 7320936, 0, 12816288, 0, 120, 0, 12816288, 0, 13313632, 0, 14483456, 0
        # ---------------------------
        # 120 - header
        # var - section 1 (some items index)

        header = readStruct('<4s13I8Q', f)

        if not header:
            raise Exception('Failed to read the header')

        signature = header[0]

        if signature != SIGNATURE_IDCL:
            raise Exception('It is not a resources file: {}'.format(filePath))

        version          = header[1]   # const 12
        unk2             = header[2]   # ? big random number, CRC?
        unk3             = header[3]   # ? big random number, CRC?
        const0           = header[4]   # const 0
        const1           = header[5]   # const 1
        constFFFFFFFF    = header[6]   # const 0xFFFFFFFF
        constFF          = header[7]   # const 0xFF
        unk8             = header[8]   # ? big random number, CRC?
        unk9             = header[9]   # ? big random number, CRC?
        indexItemCount   = header[10]  # + 144 bytes per item
        s3_count         = header[11]  # + 32 bytes per item, see [19] and [23]
        s4_count         = header[12]  # +
        s5_count         = header[13]  # + 8 bytes per item
        const0           = header[14]  # const 0
        s2_size          = header[15]  # +
        stringsOffset    = header[16]  # +
        s3_offset        = header[17]  # +
        indexItemsOffset = header[18]  # +
        s3_offsetDup     = header[19]  # + (always dup, why?)
        s4_offset        = header[20]  # + (see [12])
        contentOffset    = header[21]  # +

        f.seek(indexItemsOffset)

        indexItems = []

        for i in range(indexItemCount):
            #                                                             +            +      +
            # 0  1  2  3  4           5           6  7  8  9 10 11 12 13  14       15  16 17  18 19  20          21        22          23      24          25       26 27 28 29 30 31 32 33 34 35 
            # 0, 0, 1, 0, 4294967295, 4294967295, 0, 0, 0, 0, 0, 0, 0, 0, 14483456, 0, 16, 0, 16, 0, 4171641641, 62540365, 1773768202, 351425, 4171641641, 62540365, 0, 0, 0, 0, 0, 0, 2, 0, 0, 0
            # 0, 0, 1, 0, 4294967295, 4294967295, 0, 0, 2, 0, 0, 0, 0, 0, 14483520, 0, 16, 0, 16, 0, 4171641641, 62540365, 1773768202, 351425, 4171641641, 62540365, 0, 0, 0, 0, 0, 0, 2, 0, 0, 0
            # 0, 0, 1, 0, 4294967295, 4294967295, 0, 0, 4, 0, 0, 0, 0, 0, 14483584, 0, 16, 0, 16, 0, 4171641641, 62540365, 1773768202, 351425, 4171641641, 62540365, 0, 0, 0, 0, 0, 0, 2, 0, 0, 0
            # Total: 178077

            # ----------------------------------------------------------------------------------------------------------
            (
                const0,           # [0]  const 0
                const1,           # [1]  const 1
                unk34,            # [2]  const 0xFFFFFFFFFFFFFFFF
                unk36,            # [3]  ? values: all - 178077, unq - 31930, min - 0, max - 87794; <= fs (related to s4_count, not unique per file)
                entryType,        # [4]  ? values: all - 178077, unq - 69351, min - 0, max - 101677; <= fs (related to s5_count, not unique per file)
                const0,           # [5]  const 0
                const0,           # [6]  const 0
                itemOffset,       # [7]  +
                itemCompSize,     # [8]  +
                itemDecompSize,   # [9]  +
                unk50,            # [10] ? values: all - 178077, unq - 153579, min - 5154,   max - 4294955920 (large random number, not unique per file) ~43304
                modifiedDate,     # [11] + modification date in microseconds
                unk54,            # [12] ? values: all - 178077, unq - 153591, min - 1,      max - 4294955920 (large random number, not unique per file) ~43312
                unk56,            # [13] ? 20 values: 0, 1, 2, 3, 4, 8, 9, 10, 11, 12, 13, 14, 16, 18, 21, 26, 44, 45, 46, 47 (seems like it is related to entryType)
                unk58,            # [14] ? 13 values: 0, 4259840, 2, 4259842, 13238274, 4, 4259844, 2097154, 2162690, 2228226, 3080194, 2293762, 3211266
                const0,           # [15] const 0
                unk62,            # [16] ? 2 values: 2, 3
                const0,           # [17] const 0
            ) = readStruct('<18Q', f)

            #             0      1          2           3             4               5      6             7      8      9      10
            indexItem = [ unk36, entryType, itemOffset, itemCompSize, itemDecompSize, unk50, modifiedDate, unk54, unk56, unk58, unk62 ]

            indexItems.append(indexItem)

        # -------------------------------------------------

        f.seek(stringsOffset)

        indexStringCount = readStruct('<Q', f)
        indexStringOffsets = readStruct('<{}Q'.format(indexStringCount), f)
        indexStringBaseOffset = f.tell()
        indexStrings = []

        for offset in indexStringOffsets:
            f.seek(indexStringBaseOffset + offset)
            indexString = readNullString(f)
            indexStrings.append(indexString)

        # -------------------------------------------------

        f.seek(s3_offset)

        resources = []

        for i in range(s3_count):
            (
                keyIndex,       # [0] +
                const0,         # [1] const 0
                valueIndex,     # [2] +
                const0,         # [3] const 0
                valueTypeNum,   # [4] 2 | 5 (2 - doesn't have '#'; 5 - has '#')
                const1,         # [5] const 1
                unk72,          # [6] ? values: all - 49310, unq - 33043, min - 0, max - 4294893614
                unk73,          # [7] ? values: all - 49310, unq - 25211, min - 0, max - 4294846071 (0 for ['voiceover', 'particle', 'sound', 'projectileImpactEffect', 'rumble', 'damage', 'material', 'visemeSet', 'renderLayerDefinition', 'weapon', 'renderParm', 'renderParmSet', 'renderProgFlag'], not 0 for ['baseModel', 'skeleton', 'rs_emb_sfile', 'geistanim'])
            ) = readStruct('<8I', f)

            key          = indexStrings[keyIndex]  # enum [ 'rs_emb_sfile', 'skeleton', 'material', 'sound', 'visemeSet', 'voiceover', 'damage', 'baseModel', 'particle', 'projectileImpactEffect', 'geistanim', 'rumble', 'weapon', 'renderParm', 'renderProgFlag', 'renderLayerDefinition', 'renderParmSet' ]
            value        = indexStrings[valueIndex]
            valueType    = [ None, None, 'RAW', None, None, 'REF' ][valueTypeNum]

            resource = (unk72, unk73, const1, valueType, key, value)
            resources.append(resource)

        # -------------------------------------------------

        f.seek(s4_offset)

        resourceIndices = []

        for i in range(s4_count):
            resourceIndex = readStruct('<I', f)
            resourceIndices.append(resources[resourceIndex])
            # print(resources[resourceIndex])

        # -------------------------------------------------

        itemTypeIndices = [ readStruct('<Q', f) for _ in range(s5_count) ]

        for indexItem in indexItems:
            indexItem[1] = indexStrings[itemTypeIndices[indexItem[1]]]

        # -------------------------------------------------

        if f.read(4) != SIGNATURE_IDCL:
            print('</IDCL> not found')

        # -------------------------------------------------

        if 1:
            print('\nindexItemCount: {}\nindexStringCount: {}\ns3_count: {}\ns4_count: {}\ns5_count: {}'.format(indexItemCount, indexStringCount, s3_count, s4_count, s5_count))

            printTable(
                'indexItems ({}):'.format(indexItemCount),
                [ 'unk36', 'entryType', 'itemOffset', 'itemCompSize', 'itemDecompSize', 'unk50', 'modifiedDate', 'unk54', 'unk56', 'unk58', 'unk62' ],
                indexItems,
                [ None, None, None, None, None, None, formatDateMicroseconds, None, None, None, None ]
            )

            # printTable(
            #     'resources ({}):'.format(s3_count),
            #     [ 'unk72', 'unk73', 'const1', 'valueType', 'key', 'value' ],
            #     resources
            # )

            # printTable(
            #     'resourceIndices ({}):'.format(s4_count),
            #     [ 'unk72', 'unk73', 'const1', 'valueType', 'key', 'value' ],
            #     resourceIndices
            # )

            # printTable(
            #     's5_strings ({}):'.format(s5_count),
            #     [ 'string' ],
            #     [ [ string ] for string in s5_strings ]
            # )

    print('-' * 200)


def unpackTextureDB (filePath):
    global _tmp

    if not os.path.isfile(filePath):
        print('File doesn\'t exist:', filePath)
        return

    fileName = os.path.basename(filePath)
    fileSize = os.path.getsize(filePath)

    print('{} {} '.format(fileName, fileSize).ljust(200, '-'))

    with open(filePath, 'rb') as f:
        header = readStruct('<8s3Q', f)

        if not header:
            raise Exception('Failed to read the header')

        signature, unk1, unk2, itemCount = header

        if signature != SIGNATURE_TEXDB:
            raise Exception('It is not a texdb file: {}'.format(filePath))

        indices = []

        for i in range(itemCount):
            unk3, unk4 = readStruct('<2Q', f)
            indices.append((unk3, unk4))

        for i, j in sorted(indices, key=lambda item: item[1]):
            print(i, j)



    print('-' * 200)


def unpackAll (rootDir):
    unpackers = {
        # '.texdb':     unpackTextureDB,
        '.resources': unpackResources
    }

    def walk (directory):
        if not os.path.isdir(directory):
            return

        for item in os.listdir(directory):
            itemPath = os.path.join(directory, item)

            if os.path.isdir(itemPath):
                walk(itemPath)
            elif os.path.isfile(itemPath):
                ext = os.path.splitext(item)[1].lower()

                if ext in unpackers:
                    unpackers[ext](itemPath)

    walk(rootDir)


if __name__ == '__main__':    
    # unpackResources(os.path.join(GAME_DIR, 'base', 'chunk_1.resources'))
    # unpackResources(os.path.join(GAME_DIR, 'base', 'chunk_3.resources'))  # 100mb
    # unpackResources(os.path.join(GAME_DIR, 'base', 'chunk_7.resources'))  # 25mb
    # unpackResources(os.path.join(GAME_DIR, 'base', 'chunk_8.resources'))
    # unpackResources(os.path.join(GAME_DIR, 'base', 'patch_1.resources'))
    # unpackResources(os.path.join(GAME_DIR, 'base', 'patch_2.resources'))
    # unpackResources(os.path.join(GAME_DIR, 'base', 'patch_4_chunkbase_6.resources'))
    # unpackResources(os.path.join(GAME_DIR, 'base', 'gameresources.resources'))

    # unpackTextureDB(os.path.join(GAME_DIR, 'base', 'patch_1.texdb'))

    # unpackAll(GAME_DIR)

    print('End')



# ---------------------------------------------------------------------------------------------------------------

# https://stackoverflow.com/questions/252417/how-can-i-use-a-dll-file-from-python
# hllDll = ctypes.WinDLL('G:\\Steam\\steamapps\\common\\Wolfenstein.The.New.Order\\base\\oo2core_8_win64.dll')

#     typedef int WINAPI OodLZ_CompressFunc(
#   int codec, uint8 *src_buf, size_t src_len, uint8 *dst_buf, int level,
#   void *opts, size_t offs, size_t unused, void *scratch, size_t scratch_size);
#   
# typedef int WINAPI OodLZ_DecompressFunc(
#   uint8 *src_buf, int src_len, uint8 *dst, size_t dst_size, int fuzz,
#   int crc, int verbose, uint8 *dst_base, size_t e, void *cb, void *cb_ctx, 
#   void *scratch, size_t scratch_size, int threadPhase);

    # OodLZ_Compress

'''
0 abilityInfo
1 abilityInventoryItem
2 aiBehavior
3 aiBehaviorEvents
4 aiBehaviorVo
5 aiComponent_BreakableLimbs
6 aiComponent_FuelLines
7 aiComponent_PanzerhundTank
8 aiComponent_ThrusterBackpack
9 aiEvent
10 aiFSMManager
11 aiGlobalSettings
12 aiTurnParms
13 aimAssist
14 ammo
15 anim
16 animEvent
17 animSys
18 announcementBackgrounds
19 articulatedFigure
20 automapicon
21 baseModel
22 breakable
23 cameraTrigger
24 cfile
25 cgr
26 challenge
27 challengeinfo_score
28 chapter
29 chaptervariation
30 chronicleInfo
31 chronicleStoreInfo
32 chronicleVolumeInfo
33 cm
34 commodity
35 compfile
36 constrainedbodies
37 credits
38 damage
39 damageFilter
40 decalatlas
41 depthOfField
42 destructionmodeldata
43 devInvLoadout
44 devMenuOption
45 dynamicChallenge
46 ebolt
47 entitlements
48 entityDamage
49 entityDef
50 env
51 envexplosion
52 explosion
53 extkisclule
54 extralocation
55 extras
56 extratype
57 faction
58 factionGraph
59 fga
60 file
61 flamethrower
62 flare
63 font
64 footstepeffects
65 fx
66 gameMode
67 geistPosture
68 geistSetup
69 geistanim
70 geistanimpara
71 geistidentity
72 glassmodel
73 globalflag
74 goreBehavior
75 goreGraph
76 goreMannequin
77 gorewounds
78 guielement
79 guiwarmapelement
80 health
81 healthComponent
82 hkcloth
83 hknavmesh
84 image
85 inventoryItem
86 json
87 kisculeGraph
88 layer
89 lightatlas
90 loadingscreen
91 loadout
92 lodGroup
93 lootDrop
94 mannequinmodel
95 mapInfo
96 material
97 md6Def
98 medal
99 metric
100 midnightScene
101 midnightSceneGroup
102 midnight_logic_container
103 midnight_logic_container_ai
104 midnight_logic_container_interact
105 mission
106 missionobj
107 model
108 modelAsset
109 modelstream
110 onlineLevel
111 particle
112 particleStage
113 performancesProfileSetup
114 perks
115 playerArmIK
116 playerLegIK
117 playerProps
118 progressiondebug
119 projectile
120 projectileImpactEffect
121 propAttribs
122 propDamage
123 propDissolve
124 propExplode
125 propHealth
126 propItem
127 propUse
128 prtmeshdist
129 pvs
130 renderLayerDefinition
131 renderParm
132 renderParmSet
133 renderProgFlag
134 renderProgResource
135 rewardTable
136 ribbon
137 rumble
138 screenViewShake
139 securityUnlock
140 skeleton
141 skins
142 sound
143 soundinfo
144 spineIK
145 staticImage
146 staticParticleModel
147 staticShadowGeom
148 staticStreamTree
149 swfhudresource
150 swfjournalresource
151 swfresource
152 swfshellresource
153 table
154 targeting
155 tooltip
156 trackingParms
157 transsortatlas
158 tutorialEvent
159 unlock
160 unlockable
161 upgrade
162 videoOptionConfig
163 videoOptionPreset
164 visemeSet
165 voiceover
166 voicetrack
167 weapon
168 weaponDataBarrageWeapon
169 weaponDataDKW
170 weaponDataLKW
171 weaponReticle
172 weaponReticleSWFInfo
173 weaponmovement
'''

'''

            (
                const0,           # [0]  const 0
                const0,           # [1]  const 0
                const1,           # [2]  const 1
                const0,           # [3]  const 0
                unk34,            # [4]  const 0xFFFFFFFF
                unk35,            # [5]  const 0xFFFFFFFF
                unk36,            # [6]  ? values: all - 178077, unq - 31930, min - 0, max - 87794; <= fs (related to s4_count, not unique per file)
                const0,           # [7]  const 0
                unk38,            # [8]  ? values: all - 178077, unq - 69351, min - 0, max - 101677; <= fs (related to s5_count, not unique per file)
                const0,           # [9]  const 0
                const0,           # [10] const 0
                const0,           # [11] const 0
                const0,           # [12] const 0
                const0,           # [13] const 0
                itemOffset,       # [14] +
                const0,           # [15] const 0
                itemCompSize,     # [16] +
                const0,           # [17] const 0
                itemDecompSize,   # [18] +
                const0,           # [19] const 0
                unk50,            # [20] ? values: all - 178077, unq - 153579, min - 5154,   max - 4294955920 (large random number, not unique per file) ~43304
                unk51,            # [21] ? values: all - 178077, unq - 153578, min - 9493,   max - 4294928452 (large random number, not unique per file) ~43305
                unk52,            # [22] ? values: all - 178077, unq - 140305, min - 14156,  max - 4294929240 (large random number, not unique per file) ~35777
                unk53,            # [23] ? values: all - 178077, unq - 1203,   min - 348414, max - 359214; <= fs (not random less-frequently repeated number) ~446
                unk54,            # [24] ? values: all - 178077, unq - 153591, min - 1,      max - 4294955920 (large random number, not unique per file) ~43312
                unk55,            # [25] ? values: all - 178077, unq - 153589, min - 0,      max - 4294949429 (large random number, not unique per file) ~43313
                unk56,            # [26] ? 20 values: 0, 1, 2, 3, 4, 8, 9, 10, 11, 12, 13, 14, 16, 18, 21, 26, 44, 45, 46, 47 (seems like it is related to unk38)
                unk57,            # [27] ? 4 values: 0, 1, 2, 3
                unk58,            # [28] ? 13 values: 0, 4259840, 2, 4259842, 13238274, 4, 4259844, 2097154, 2162690, 2228226, 3080194, 2293762, 3211266
                const0,           # [29] const 0
                const0,           # [30] const 0
                const0,           # [31] const 0
                unk62,            # [32] ? 2 values: 2, 3
                unk63,            # [33] ? values: all - 178077, unq - 109, min - 0, max - 207; <= fs
                const0,           # [34] const 0
                const0,           # [35] const 0
            ) = readStruct('<18Q', f)

            #             0      1      2           3             4               5      6      7      8      9      10     11     12     13     14     15
            indexItem = [ unk36, unk38, itemOffset, itemCompSize, itemDecompSize, unk50, unk51, unk52, unk53, unk54, unk55, unk56, unk57, unk58, unk62, unk63 ]
'''