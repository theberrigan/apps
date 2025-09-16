# Limbo

import re
import sys
import struct

from PIL import Image as PILImage

sys.path.insert(0, r'C:\Projects\PythonLib\python\v001')

from bfw.utils import *
from bfw.reader import *



GAME_DIR = r'G:\Steam\steamapps\common\Limbo'

MATERIALS = [
    'branch',
    'brickwall',
    'cliff',
    'concrete',
    'grass',
    'ground',
    'ladder_metal',
    'ladder_wood',
    'ladder_roots',
    'ladder_tin',
    'leaves',
    'metal',
    'metal_grid',
    'metal_heavy',
    'puddle',
    'rope_organic',
    'rope_chain',
    'sand',
    'snow',
    'soil_debris',
    'timber',
    'wood'
]

for i, m in enumerate(MATERIALS):
    m = m.encode('utf-8')
    s = struct.pack('<B', len(m))

    MATERIALS[i] = s + m

MATERIALS = b'|'.join(MATERIALS)

MATERIALS_REGEX = re.compile(MATERIALS)

XYZ_REGEX = re.compile(rb'\-?\d+\.\d{6},\-?\d+\.\d{6},\-?\d+\.\d{6}')


def tryParseLoc (data):
    with MemReader(data) as f:
        unk1  = f.u32()

        assert unk1 == 1

        count = f.u32()

        for i in range(count):
            size  = f.u32()
            key   = f.fixedString(size)
            size  = f.u32()
            value = f.fixedString(size)

    assert not f.remaining()

def parseSprite (filePath):
    with openFile(filePath) as f:
        w = 4096
        h = 4096
        f.seek(63)
        level = 0

        while f.remaining():
            print(level, w, h)

            res = w * h
            pixels = [ 0 ] * (res * 4)

            for i in range(w * h):
                s, a = f.u8(2)

                pixels[i * 4 + 0] = s
                pixels[i * 4 + 1] = s
                pixels[i * 4 + 2] = s
                pixels[i * 4 + 3] = a

            data = struct.pack(f'<{ (res * 4) }B', *pixels)

            image = PILImage.frombytes('RGBA', (w, h), data)

            image.save(filePath + f'_{ level }.png')

            w //= 2
            h //= 2

            level += 1

def saveImage (imagePath, width, height, rawBuffer):
    pxCount  = width * height
    dstBytes = 4 * pxCount
    pixels   = [ 0 ] * dstBytes

    for i in range(pxCount):
        shade = rawBuffer[i * 2 + 0]
        alpha = rawBuffer[i * 2 + 1]

        pixels[i * 4 + 0] = shade
        pixels[i * 4 + 1] = shade
        pixels[i * 4 + 2] = shade
        pixels[i * 4 + 3] = alpha

    data = struct.pack(f'<{ dstBytes }B', *pixels)

    image = PILImage.frombytes('RGBA', (width, height), data)

    image.save(imagePath)


class DataType:
    Unknown     = 0
    PlainText   = 1
    BoyConfig   = 2
    Shader      = 3
    Sprite      = 4
    Script      = 5
    SmallScript = 6
    Font        = 7
    Loc         = 8


def getDataType (data):
    isText = False

    if b'\x00' not in data:
        try:
            data.decode('utf-8')
            isText = True
        except:
            pass

    shaderSigns = [
        b'sampler2D ',
        b'float4 ',
        b'float2 ',
        b'register(s',
        b'File: op_invert.fx',
        b'COLOR0',
        b'#define ',
        b'VS_INPUT ',
        b'VS_OUTPUT ',
        b'#define ',
    ]

    if isText:
        if b'boydir = ' in data:
            return DataType.BoyConfig
        
        for sign in shaderSigns:
            if sign in data:
                return DataType.Shader

        return DataType.PlainText

    if data.startswith(b'\x09\x00\x00\x00\x02\x00\x00\x00\x01\x00\x00\x00'):
        return DataType.Sprite

    if data.startswith(b'\x14\x00\x00\x00\x8A\xBD\xD1\xF4\xA0\xF3\xED\x77'):
        return DataType.Script

    if data.startswith(b'\x41\x02\x00\x00\x8A\xBD\xD1\xF4\xA0\xF3\xED\x77'):
        return DataType.SmallScript

    if data.startswith(b'\x00\x01\x00\x00\x00'):
        return DataType.Font

    try:
        tryParseLoc(data)
        return DataType.Loc
    except:
        pass

    return DataType.Unknown


def unpackPackage (pkgPath):
    outputDir = pkgPath + '_unpacked'

    with openFile(pkgPath, ReaderType.Mem) as f:
        itemCount = f.u32()
        itemIndex = [ None ] * itemCount

        for i in range(itemCount):
            itemIndex[i] = f.u32(3)

        contentStart = f.tell()

        for unk1, offset, size in itemIndex:
            absOffset = contentStart + offset

            f.seek(absOffset)

            data = f.read(size)

            isCompressed = data[:2] == b'\x78\x9C'

            itemName = f'{absOffset:08X}_{unk1:08X}'

            if isCompressed:
                data = decompressData(data)
                itemName += '.decomp'

            dataType = getDataType(data)

            match dataType:
                case DataType.Unknown:
                    subType = struct.unpack('<I', data[:4])[0]
                    itemDir = joinPath('unknown', str(subType))
                    itemName += '.bin'
                case DataType.PlainText:
                    itemDir = 'text'
                    itemName += '.txt'
                case DataType.BoyConfig:
                    itemDir = 'boy_configs'
                    itemName += '.txt'
                case DataType.Shader:
                    itemDir = 'shaders'
                    itemName += '.hlsl'
                case DataType.Sprite:
                    itemDir = 'sprites'
                    itemName += '.bin'
                case DataType.Script:
                    itemDir = 'scripts'
                    itemName += '.bin'
                case DataType.SmallScript:
                    itemDir = 'scripts2'
                    itemName += '.bin'
                case DataType.Font:
                    itemDir = 'fonts'
                    itemName += '.ttf'
                case DataType.Loc:
                    itemDir = 'loc'
                    itemName += '.bin'
                case _:
                    assert 0

            itemDir  = joinPath(outputDir, itemDir)
            itemPath = joinPath(itemDir, itemName)

            createDirs(itemDir)
            writeBin(itemPath, data)

            print(f'{unk1:08X}', contentStart + offset, size, isCompressed, itemName)

            
def unpackPackages (rootDir):
    for pkgPath in iterFiles(rootDir, True, [ '.pkg' ]):
        print(pkgPath)
        unpackPackage(pkgPath)
        print(' ')

def checkSprites ():
    spritesDir = joinPath(GAME_DIR, 'limbo_boot.pkg_unpacked', 'sprites')

    paths = []
    unk4s = []

    for filePath in iterFiles(spritesDir, True, [ '.bin' ]):
        with openFile(filePath) as f:
            _always9, _always2, flags, unk4 = f.u32(4)

            assert _always9 == 9
            assert _always2 == 2  # channel count?
            assert flags in [ 1, 9, 17 ]

            # flags:
            # 1 << 0 - ? (has alpha?) (always set)
            # 1 << 3 - black only
            # 1 << 4 - b/w atlas

            if unk4 not in unk4s:
                unk4s.append(unk4)

            pathSize = f.u8()

            spritePath = f.fixedString(pathSize)

            if spritePath not in paths:
                paths.append(spritePath)

            _always7 = f.u32()
            unk6     = f.u16()
            width    = f.u16()
            height   = f.u16()
            unk9     = f.u8()
            mipCount = f.u8()
            unk11    = f.u8()

            assert _always7 == 7

            assert unk6 in [ 0, 3084, 13107, 51400 ], unk6

            print(filePath)
            print(spritePath)
            print(f'mips={ mipCount } width={ width } height={ height }')
            print(flags, unk4)
            print(unk6, unk9, unk11)

            print(' ')

            # if flags == 17:
            #     for i in range(10):
            #         pngPath = joinPath(GAME_DIR, 'limbo_boot.pkg_unpacked', f'{ flags }_{ i }.png')

            #         if not isFile(pngPath):
            #             data = f.read()
            #             saveImage(pngPath, width, height, data)
            #             break

    paths.sort()
    unk4s.sort()

    print(len(paths))
    print(unk4s)

def createScriptTemplate (scriptPath):
    XYZ_REGEX   = re.compile(rb'\-?\d+\.\d+,\-?\d+\.\d+,\-?\d+\.\d+')
    XY_REGEX    = re.compile(rb'\-?\d+\.\d+,\-?\d+\.\d+')
    FLOAT_REGEX = re.compile(rb'\-?\d+\.\d+')
    INT_REGEX   = re.compile(rb'\-?\d+')
    PATH_REGEX  = re.compile(rb'data/')

    mats = readText(joinPath(GAME_DIR, 'limbo_boot.pkg_unpacked', 'text', '0131DE4B_9D08B84F__materials_list.txt__.txt'))
    mats = [ line.strip() for line in mats.split('\n') if line.strip() ]

    for i, m in enumerate(mats):
        m = m.encode('utf-8')
        s = struct.pack('<B', len(m))

        mats[i] = s + m

    MATERIALS_REGEX = re.compile(b'|'.join(mats))

    data  = readBin(scriptPath)
    items = {}

    with openFile(scriptPath) as f:
        for typeKey, typeRegex in [
            ('vec3',  XYZ_REGEX),
            ('vec2',  XY_REGEX),
            ('float', FLOAT_REGEX),
            ('int',   INT_REGEX),
            ('path',  PATH_REGEX),
            ('mats',  MATERIALS_REGEX),
        ]:
            for match in re.finditer(typeRegex, data):
                literal = match[0]
                offset  = match.span()[0] - 3
                size    = data[offset + 2]

                if typeKey != 'path' and size != len(literal) or offset in items:
                    continue

                f.seek(offset)

                unk1, unk2, size = f.u8(3)

                if unk2 != 1:
                    continue

                literal = f.fixedString(size)

                items[offset] = {
                    'id': unk1,
                    'type': typeKey,
                    'offset': offset,
                    'size': size,
                    'literal': literal
                }

    items = [ x[1] for x in sorted(items.items(), key=lambda a: a[0]) ]

    prefix = 'b_' if 'limbo_boot.pkg' in scriptPath else 'rt_'

    name = prefix + getFileName(scriptPath).split('.')[0] + '.bt'

    templatePath = joinPath(GAME_DIR, '_templates', name)

    # https://www.sweetscape.com/010editor/manual/TemplateVariables.htm

    template = [
        '''
        RequiresVersion( 14 );

        typedef struct {
            ubyte unk1;
            ubyte unk2;
            ubyte size;
            char  content[size];
        } Item;

        LittleEndian();

        local uint c = 0;

        '''
    ]

    for item in items:
        offset = item['offset']
        template.append(f'FSeek({ offset });')
        template.append(f'Item item <bgcolor=((c % 2) == 0 ? 0x9BFF9B : 0x9B9BFF)>;\n')
        template.append(f'c++;\n')

    template = '\n'.join(template)

    createDirs(getDirPath(templatePath))

    writeText(templatePath, template)

    # print(template)
    print(getRelPath(scriptPath, GAME_DIR))
    print(getRelPath(templatePath, GAME_DIR))


def checkScripts ():
    XYZ_REGEX   = re.compile(rb'\-?\d+\.\d+,\-?\d+\.\d+,\-?\d+\.\d+')
    XY_REGEX    = re.compile(rb'\-?\d+\.\d+,\-?\d+\.\d+')
    FLOAT_REGEX = re.compile(rb'\-?\d+\.\d+')
    PATH_REGEX  = re.compile(rb'data/')

    mats = readText(joinPath(GAME_DIR, 'limbo_boot.pkg_unpacked', 'text', '0131DE4B_9D08B84F__materials_list.txt__.txt'))
    mats = [ line.strip() for line in mats.split('\n') if line.strip() ]

    for i, m in enumerate(mats):
        m = m.encode('utf-8')
        s = struct.pack('<B', len(m))

        mats[i] = s + m

    MATERIALS_REGEX = re.compile(b'|'.join(mats))

    items = {}

    for scriptsDir in [
        joinPath(GAME_DIR, 'limbo_runtime.pkg_unpacked', 'scripts'),
        joinPath(GAME_DIR, 'limbo_boot.pkg_unpacked', 'scripts'),
    ]:
        for scriptPath in iterFiles(scriptsDir, True, [ '.bin' ]):
            print(scriptPath)

            checkedOffsets = {}

            with openFile(scriptPath) as f:
                data = f.read()

                for typeKey, regex in [
                    ('xyz', XYZ_REGEX),
                    ('xy', XY_REGEX),
                    ('float', FLOAT_REGEX),
                    ('path', PATH_REGEX),
                    ('mats', MATERIALS_REGEX),
                ]:
                    itemOffsets = {}
                    typeItems = items[typeKey] = {}

                    for match in re.finditer(regex, data):
                        m = match[0]
                        i = match.span()[0]
                        size = data[i - 1]
                        offset = i - 3

                        if size == len(m) and offset not in checkedOffsets:
                            checkedOffsets[offset] = True
                            itemOffsets[offset] = True

                    for offset in itemOffsets.keys():
                        f.seek(offset)
                        unk1, unk2, size = f.u8(3)
                        literal = f.string(size)

                        if unk2 != 1:
                            continue

                        assert unk2 == 1, (offset, literal)

                        if unk1 not in typeItems:
                            typeItems[unk1] = []

                        if typeKey == 'path':
                            literal = getExt(literal)
                        elif typeKey == 'mats':
                            pass
                        else:
                            literal = None

                        if literal is not None and literal not in typeItems[unk1]:
                            typeItems[unk1].append(literal)

                '''
                unk1, unk2, unk3 = f.u32(3)

                assert unk1 == 20 and unk2 == 4107386250 and unk3 == 2012083104

                checksum = f.fixedString(32)

                assert re.match(r'^[\dA-F]+$', checksum, re.I)

                hasChecksum = bool(checksum.strip('0'))

                # print(checksum, hasChecksum)

                unk4 = f.u32()

                assert unk4 == 7791616

                unk5 = f.u16()

                assert unk5 in [ 36, 48, 50, 51, 52 ]

                unk6 = f.u16()

                assert unk6 in [ 0, 154, 155, 156, 161, 162, 163, 164, 177, 178, 179, 180, 181, 182, 183 ]

                unk7 = f.u32()

                # when there is not checksum, unk7 is 0
                assert unk7 or not hasChecksum

                unk8 = f.u16()

                # if unk6 not in _tmp:
                #     _tmp.append(unk6)

                assert unk8 in [ 0, 1, 256 ]

                print(unk8)
                '''

            print(' ')

    print(toJson(items))

    for typeKey, typeStat in items.items():
        print(f'{ typeKey }:')

        for key, lits in typeStat.items():
            lits = ' '.join(lits)
            print(f'{unk1:02X} 01 XX -- { lits }')

        print(' ')



'''
XYZ Coords:
- 05 01 XX -- XYZ
- 06 01 XX -- XYZ
- 09 01 XX -- XYZ
- 0A 01 XX -- XYZ
- 11 01 XX -- XYZ
- 1A 01 XX -- XYZ
- 1B 01 XX -- XYZ
- FF 01 XX -- XYZ

Materials:
- 00 01 XX -- branch cliff concrete grass ground ladder_metal ladder_tin leaves metal metal_grid metal_heavy puddle sand snow soil_debris timber wood
- 05 01 XX -- branch cliff concrete grass ground ladder_metal ladder_tin leaves metal metal_grid metal_heavy puddle sand snow soil_debris timber wood
- 1B 01 XX -- branch brickwall cliff concrete grass ground ladder_metal ladder_roots ladder_tin ladder_wood leaves metal metal_grid metal_heavy puddle rope_chain rope_organic sand snow timber wood

Paths:
- 00 01 XX -- .branch
- 04 01 XX -- .anim .bnk .script
- 0E 01 XX -- .branch
- 10 01 XX -- .png
- 12 01 XX -- .png
- 1C 01 XX -- .png
- FF 01 XX -- .fx
'''
# -----------------------------------------
# .scene
# .branch
# .script
# .anim

# oX   oY   w  h  pivX pivY  pathATLAS
# 1594 3760 43 63 42   32   "data/sprites/characters/insects/half_butterfly.pngBLUR_A"

# "data/levels/_resource/camera/mockup_cam.branch"

# Many stringified numbers:
# - limbo_runtime.pkg_unpacked/scripts
# - limbo_boot.pkg_unpacked/scripts
# 
# Have similar signature as scripts:
# - limbo_boot.pkg_unpacked/scripts2
#
# No signature, have some strings like attrs:
# - limbo_boot.pkg_unpacked/_scripts_or_attrs

# 1-6 - scripts
# 7 - ???
# 8 - scripts
# 9 - scripts, sprites/textures
# 10-92 - scripts
# ------------------------------------------
# 7
# ------------------------------------------
# L calf -- 129
# L foot -- 129
# L forearm -- 129
# L thigh -- 91
# L upperarm -- 91
# R calf -- 129
# R foot -- 129
# R forearm -- 129
# R thigh -- 91
# R upperarm - 91
# head -- 91
# pelvis -- 91
# torso -- 76

#               head
# L upperarm -- torso -- R upperarm
# L forearm       |      R forearm
#                 |
#    L thigh -- pelvis -- R thigh
#    L calf               R calf
#    L foot               R foot
# ------------------------------------------

if __name__ == '__main__':
    # unpackPackages(GAME_DIR)
    # unpackPackage(joinPath(GAME_DIR, 'limbo_boot.pkg'))
    # unpackPackage(joinPath(GAME_DIR, 'limbo_runtime.pkg'))
    # parseLocFile(r"G:\Steam\steamapps\common\Limbo\limbo_boot.pkg_unpacked\unknown\1\00F84590_169F3875.decomp.bin")
    # parseSprite(r"G:\Steam\steamapps\common\Limbo\limbo_boot.pkg_unpacked\sprites\00855541_C7D16BF8.decomp.bin")
    # parseSprite(r"G:\Steam\steamapps\common\Limbo\limbo_boot.pkg_unpacked\unknown\9\00F88F83_DAA7985E.decomp.bin")
    # checkSprites()
    # checkScripts()
    # readScript(joinPath(GAME_DIR, 'limbo_runtime.pkg_unpacked', 'scripts', '0000BBA1_1F4ED919.decomp.bin'))
    # createScriptTemplate(joinPath(GAME_DIR, 'limbo_boot.pkg_unpacked', 'scripts', '003213FA_3B8B0A5A.decomp.bin'))
    createScriptTemplate(joinPath(GAME_DIR, 'limbo_boot.pkg_unpacked', 'scripts', '00124A9D_5F5C1AAD.decomp.bin'))
    