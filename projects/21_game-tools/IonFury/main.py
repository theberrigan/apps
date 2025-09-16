import re
import sys
import subprocess

sys.path.insert(0, r'C:\Projects\PythonLib\python')

from bfw.utils import *
from bfw.reader import *

from _consts import *
from _voxels import VOXELS
from _palettes import PALETTES



ART_SIGNATURE = b'BUILDART'



'''
app_main():
    G_ScanGroups()
    G_LoadGroups()
    G_Startup():
        G_CompileScripts()  // load .con files
        engineInit():
            enginePreInit():
                ...
            engineLoadTables()  // init math tables (div, triangs....)
            paletteLoadFromDisk():
                paletteInitClosestColorScale(30, 59, 11)  // init rdist, gdist, bdist
                paletteInitClosestColorGrid()             // init colscan, coldist
                <init glblend>
        artLoadFiles()  // load "tiles000.art"
    Anim_Init()
    loaddefinitionsfile()  // load .def files and deps (including /palettes/*)
    cacheAllSounds()
    enginePostInit()
    G_PostLoadPalette()
    engineLoadClipMaps():
        engineLoadBoard()  // load "_clipshape0.map"
    videoSetGameMode():    // change rendmode from CLASSIC (0) to POLYMOST (3)
        PolymostProcessVoxels():  // load .kvx files; Generating 3D meshes from voxel model data
            voxload():
                loadkvx()
    ---
    G_NewGame_EnterLevel():
        G_EnterLevel():
            engineLoadBoard()  // load .map file
    ---
'''

# Globals:
# - tilesiz - { x, y }, abs indexing
# - picanm - picanm_t, abs indexing

# basepalette_ - 768kb each, no diffs
# palookup_000 - 256 * 32 kb, base shades table, must be loaded first

# https://developer.mozilla.org/en-US/docs/Web/API/WebGLRenderingContext/blendFunc

# closest color formula sqrt(pow(rgb1[0] - rgb2[0], 2) + pow(rgb1[1] - rgb2[1], 2) + pow(rgb1[2] - rgb2[2], 2))

# Ion Fury designed for Polymost
# Polymer is not playable
# https://steamcommunity.com/app/562860/discussions/0/1643169167153772980/ 

# OpenGL (Polymost/Polymer) vs Classic (Software)
# int32_t glrendmode = REND_POLYMOST;  // OpenGL == Polymost



# artLoadFiles
def loadArtFile (filePath):
    if not isFile(filePath):
        print('File doesn\'t exist:', filePath)
        return

    print('Unpacking', filePath)

    tiles = []

    with openFile(filePath) as f:
        signature = f.read(8)

        if signature != ART_SIGNATURE:
            print('Unknown signature:', formatByteString(signature))
            return

        version = f.u32()

        if version != 1:
            print('Unknown version:', version)
            return

        tileCount = f.u32()  # counted below
        tileStart = f.u32()
        tileEnd   = f.u32()

        tileCount = tileEnd - tileStart + 1

        # <artReadManifest>
        sizesX = f.i16(tileCount)
        sizesY = f.i16(tileCount)

        for i in range(tileCount):
            resolution = sizesX[i] * sizesY[i] 

            picanmdisk = f.u32()

            if not resolution:
                continue

            # <tileConvertAnimFormat>
            # global picanm : picanm_t
            picanm = {
                'num':  picanmdisk & 63,
                'xofs': (picanmdisk >> 8) & 255,
                'yofs': (picanmdisk >> 16) & 255,
                'sf':   ((picanmdisk >> 24) & 15) | (picanmdisk & 192)
            }
            # </tileConvertAnimFormat>

            tiles.append({
                'id': i,
                'width': sizesX[i],
                'height': sizesY[i],
                'anim': picanm,
                'indexCount': resolution,
                'indices': None
            })
        # </artReadManifest>

        # <artPreloadFile>
        for tile in tiles:
            tile['indices'] = f.read(tile['indexCount'])
        # </artPreloadFile>

    return tiles

# glblenddef_
glblenddef_t = {
    'alpha': 0.0,
    'src': 0,
    'dst': 0,
    'flags': 0
}

# glblend_t
def createGLBlend ():
    return {
        'def': [            
            deepCopy(glblenddef_t),
            deepCopy(glblenddef_t)
        ]
    }

def defaultGLBlend (blend):
    blend['def'][0]['alpha'] = 2.0 / 3.0
    blend['def'][0]['src']   = BLENDFACTOR_SRC_ALPHA
    blend['def'][0]['dst']   = BLENDFACTOR_ONE_MINUS_SRC_ALPHA
    blend['def'][0]['flags'] = 0

    blend['def'][1]['alpha'] = 1.0 / 3.0
    blend['def'][1]['src']   = BLENDFACTOR_SRC_ALPHA
    blend['def'][1]['dst']   = BLENDFACTOR_ONE_MINUS_SRC_ALPHA
    blend['def'][1]['flags'] = 0

    return blend

def nullGLBlend (blend):
    blend['def'][0]['alpha'] = 1.0
    blend['def'][0]['src']   = BLENDFACTOR_ONE
    blend['def'][0]['dst']   = BLENDFACTOR_ZERO
    blend['def'][0]['flags'] = 0

    blend['def'][1]['alpha'] = 1.0
    blend['def'][1]['src']   = BLENDFACTOR_ONE
    blend['def'][1]['dst']   = BLENDFACTOR_ZERO
    blend['def'][1]['flags'] = 0

    return blend

# palette_t
def createPalette ():
    return {
        'r': 0,
        'g': 0,
        'b': 0,
        'f': 0
    }

MAXBASEPALS  = 256
MAXPALOOKUPS = 256
MAXBLENDTABS = 256

PALETTE_MAIN        = 1 << 0
PALETTE_SHADE       = 1 << 1
PALETTE_TRANSLUCENT = 1 << 2

BLENDFACTOR_ZERO                = 0
BLENDFACTOR_ONE                 = 1
BLENDFACTOR_SRC_COLOR           = 2
BLENDFACTOR_ONE_MINUS_SRC_COLOR = 3
BLENDFACTOR_SRC_ALPHA           = 4
BLENDFACTOR_ONE_MINUS_SRC_ALPHA = 5 
BLENDFACTOR_DST_ALPHA           = 6 
BLENDFACTOR_ONE_MINUS_DST_ALPHA = 7 
BLENDFACTOR_DST_COLOR           = 8
BLENDFACTOR_ONE_MINUS_DST_COLOR = 9

BLEND_FACTOR_MAP = {
    'ZERO':                BLENDFACTOR_ZERO,
    'ONE':                 BLENDFACTOR_ONE,
    'SRC_COLOR':           BLENDFACTOR_SRC_COLOR,
    'ONE_MINUS_SRC_COLOR': BLENDFACTOR_ONE_MINUS_SRC_COLOR,
    'SRC_ALPHA':           BLENDFACTOR_SRC_ALPHA,
    'ONE_MINUS_SRC_ALPHA': BLENDFACTOR_ONE_MINUS_SRC_ALPHA,
    'DST_ALPHA':           BLENDFACTOR_DST_ALPHA,
    'ONE_MINUS_DST_ALPHA': BLENDFACTOR_ONE_MINUS_DST_ALPHA,
    'DST_COLOR':           BLENDFACTOR_DST_COLOR,
    'ONE_MINUS_DST_COLOR': BLENDFACTOR_ONE_MINUS_DST_COLOR
}

g_noFloorPal = [ False ] * MAXPALOOKUPS
g_palette = bytearray(768)  # global palette
basepaltable = [ g_palette ] + ([ None ] * (MAXBASEPALS - 1))  # global basepaltable [MAXBASEPALS] 256
paletteloaded = 0
colmatch_palette = None
numshades = 0
palookup = [ None ] * MAXPALOOKUPS
palookupfog = [ createPalette() for i in range(MAXPALOOKUPS) ]
blendtable = [ None ] * MAXBLENDTABS
glblend = [ createGLBlend() for i in range(MAXBLENDTABS) ]


# The palookup array is an array of pointers that point to the
# first byte of each 8K palette lookup table.  All 256 pointers
# are initialized to NULL by initengine() except for palookup[0]
# which is the default 8K palette.  This will allow you to modify
# the palette lookup table directly for non-snowy fading effects,
# etc.  Each palette lookup table has 32 shades.  Each shade has
# 256 bytes.  Shade 0 is closest (actual palette brightness) and
# shade 31 is farthest (dark usually).  (256*32 = 8192 or 8K)

def loadPalettes ():
    global g_noFloorPal, basepaltable, paletteloaded, colmatch_palette, numshades, palookup, blendtable, g_palette

    paletteLoadFromDisk()

    for item in PALETTES:
        didLoadPal = False
        didLoadShade = False
        didLoadTransluc = False

        print(toJson(item, False))

        if item['type'] == 'nofloorpalrange':
            a, b = item['values']

            for i in range(a, b + 1):
                g_noFloorPal[i] = True

        elif item['type'] == 'basepalette':
            palPath = getAbsPath(joinPath(GAME_DIR, item['path']))
            palette = bytearray(readBin(palPath))

            assert len(palette) == 768

            paletteSetColorTable(item['id'], palette)
            didLoadPal = True

        elif item['type'] == 'palookup':
            if 'path' in item:
                plPath = getAbsPath(joinPath(GAME_DIR, item['path']))
                lookup = bytearray(readBin(plPath))

                if len(lookup) > 256 * 32:
                    print('WARNING: palookup file is bigger than 8192 bytes')
                    lookup = lookup[:256 * 32]

                if len(lookup) == 256 * 32:
                    didLoadShade = True
                    numshades = 32
                    paletteSetLookupTable(item['id'], lookup)
                else:
                    paletteMakeLookupTable(item['id'], lookup, 0, 0, 0, g_noFloorPal[item['id']])

            elif 'copy' in item:
                sourcepal = palookup[item['copy']]
                paletteSetLookupTable(item['id'], sourcepal)
                didLoadShade = True

            if item.get('floorpal', False):
                g_noFloorPal[item['id']] = False

        elif item['type'] == 'makepalookup':
            pal = item['pal']
            r, g, b = item['color']

            r = clamp(r, 0, 63)
            g = clamp(g, 0, 63)
            b = clamp(b, 0, 63)

            assert item['remapself']

            remappal = pal

            assert remappal > 0

            # NOTE: all palookups are initialized, i.e. non-NULL!
            # NOTE2: aliasing (pal==remappal) is OK
            paletteMakeLookupTable(pal, palookup[remappal], r << 2, g << 2, b << 2, g_noFloorPal[remappal])

        elif item['type'] == 'blendtable':
            btPath = getAbsPath(joinPath(GAME_DIR, item['path']))
            table = bytearray(readBin(btPath))

            paletteSetBlendTable(item['id'], table)
            didLoadTransluc = True

            if 'blend' in item:
                glb = nullGLBlend(glblend[item['id']])

                glb['def'][0]['src'] = glb['def'][1]['src'] = BLEND_FACTOR_MAP[item['blend'][0]]
                glb['def'][0]['dst'] = glb['def'][1]['dst'] = BLEND_FACTOR_MAP[item['blend'][1]]

        elif item['type'] == 'numalphatables':
            value = item['value']
            value2 = value * 2 + (value & 1)

            for i in range(1, value + 1):
                finv2value = 1.0 / value2

                glb = defaultGLBlend(glblend[i])

                glb['def'][0]['alpha'] = (value2 - i) * finv2value
                glb['def'][1]['alpha'] = i * finv2value

        elif item['type'] == 'fogpal':
            p = item['id']
            r, g, b = item['color']

            r = clamp(r, 0, 63)
            g = clamp(g, 0, 63)
            b = clamp(b, 0, 63)

            paletteMakeLookupTable(p, None, r << 2, g << 2, b << 2, 1)

        if didLoadPal and item['id'] == 0:
            paletteInitClosestColorMap(g_palette)
            paletteloaded |= PALETTE_MAIN

        if didLoadShade and item['id'] == 0:
            paletteloaded |= PALETTE_SHADE

        if didLoadTransluc and item['id'] == 0:
            paletteloaded |= PALETTE_TRANSLUCENT

def paletteSetColorTable (paletteId, table):
    if not basepaltable[paletteId]:
        basepaltable[paletteId] = bytearray(768)

    dst = basepaltable[paletteId]

    assert len(table) == len(dst)

    for i in range(768):
        dst[i] = table[i]

def paletteSetBlendTable (blend, table):
    if not blendtable[blend]:
        blendtable[blend] = bytearray(256 * 256)

    dst = blendtable[blend]

    assert len(table) == len(dst)

    for i in range(256 * 256):
        dst[i] = table[i]

def clamp (num, numMin, numMax):
    return min(max(num, numMin), numMax)

def paletteSetLookupTable (palnum, shtab):
    if shtab:
        maybe_alloc_palookup(palnum)
        palookup[palnum] = shtab[:256 * numshades]

def paletteMakeLookupTable (palnum, remapbuf, r, g, b, noFloorPal):
    global palookup, paletteloaded

    assert paletteloaded != 0
    assert palnum < MAXPALOOKUPS

    g_noFloorPal[palnum] = noFloorPal

    isBlackFog = (r | g | b) == 0

    if not remapbuf:
        if isBlackFog:
            palookup[palnum] = palookup[0]  # alias to base shade table
            return

        remapbuf = bytearray(range(256))  # instead of idmap

    maybe_alloc_palookup(palnum)

    # "black fog"/visibility case -- only remap color indices
    if isBlackFog:
        for i in range(numshades):
            for j in range(256):
                src = palookup[0]
                dst = palookup[palnum]

                assert src and dst

                dst[256 * i + j] = src[256 * i + remapbuf[j]]
    else:
        ptr2 = palookup[palnum]

        assert ptr2
        assert g_palette

        for i in range(numshades):
            palscale = divscale16(i, numshades - 1)

            for j in range(256):
                rgb = g_palette[remapbuf[j] * 3:remapbuf[j] * 3 + 3]

                assert (rgb[0] + mulscale16(r - rgb[0], palscale)) >= 0 and (rgb[1] + mulscale16(g - rgb[1], palscale)) >= 0 and (rgb[2] + mulscale16(b - rgb[2], palscale)) >= 0

                ptr2[256 * i + j] = paletteGetClosestColor(
                    rgb[0] + mulscale16(r - rgb[0], palscale),
                    rgb[1] + mulscale16(g - rgb[1], palscale),
                    rgb[2] + mulscale16(b - rgb[2], palscale)
                )

                # print(ptr2[256 * i + j])

    palookupfog[palnum]['r'] = r
    palookupfog[palnum]['g'] = g
    palookupfog[palnum]['b'] = b

def palookup_isdefault (palnum):
    return not palookup[palnum] or (palnum and palookup[palnum] == palookup[0])

def maybe_alloc_palookup (palnum):
    if palookup_isdefault(palnum):
        alloc_palookup(palnum)

def alloc_palookup (palnum):
    # The asm functions vlineasm1, mvlineasm1 (maybe others?) access the next
    # palookup[...] shade entry for tilesizy==512 tiles.
    # See DEBUG_TILESIZY_512 and the comment in a.nasm: vlineasm1.
    assert numshades
    palookup[palnum] = bytearray((numshades + 1) * 256)

def divscale16 (a, b):
    return divscale(a, b, 16)

def divscale (a, b, scale):
    def qw (x): 
        return x & 0xFFFFFFFFFFFFFFFF

    def dw (x): 
        return x & 0xFFFFFFFF

    def wo (x): 
        return x & 0xFFFF

    def by (x): 
        return x & 0xFF

    def tabledivide64 (n, d):
        return n // d  # TODO

    return dw(tabledivide64(qw(a << by(scale)), b))

def mulscale16 (a, b):
    return mulscale(a, b, 16)

def mulscale (a, b, scale):
    return (a * b) >> scale


COLRESULTSIZ       = 4096

FASTPALCOLDEPTH    = 256
FASTPALRIGHTSHIFT  = 3
FASTPALGRIDSIZ     = FASTPALCOLDEPTH >> FASTPALRIGHTSHIFT  # 32
FASTPALRGBDIST     = FASTPALCOLDEPTH * 2 + 1               # 513
FASTPALCOLDIST     = 1 << FASTPALRIGHTSHIFT                # 8
FASTPALCOLDISTMASK = FASTPALCOLDIST - 1                    # 0b111

colhere = [ False ] * ((FASTPALGRIDSIZ + 2) ** 3)          # bit_field[39304]
colhead = [ 0 ] * ((FASTPALGRIDSIZ + 2) ** 3)              # char[39304];  keeps [0-255]; keeps colors-entry-points 
colnext = [ 0 ] * 256                                      # int32_t[256]; keeps [0-255]; colnext[i] == j -- next color "j" for color "i"; -1 -- no next color

rdist = [ 0 ] * FASTPALRGBDIST                             # int32_t[513]
gdist = [ 0 ] * FASTPALRGBDIST                             # int32_t[513]
bdist = [ 0 ] * FASTPALRGBDIST                             # int32_t[513]

coldist = [ 0 ] * FASTPALCOLDIST                           # uint8_t[8]  { 0, 1, 2, 3, 4, 3, 2, 1 }
colscan = [ 0 ] * 27                                       # int32_t[27] { -1057, -1056, -1055, -1025, -1024, -1023, -993, -992, -991, -33, -32, -31, -1, 1057, 1, 31, 32, 33, 991, 992, 993, 1023, 1024, 1025, 1055, 1056, 0 }

colmatchresults    = [ 0 ] * COLRESULTSIZ                  # uint32_t[4096]
numcolmatchresults = 0


def paletteFlushClosestColor ():
    global colmatchresults, numcolmatchresults

    colmatchresults = [ 0 ] * COLRESULTSIZ
    numcolmatchresults = 0

def paletteGetClosestColor (r, g, b):
    return paletteGetClosestColorUpToIndex(r, g, b, 255)

def paletteGetClosestColorUpToIndex (r, g, b, lastokcol):
    return paletteGetClosestColorWithBlacklist(r, g, b, lastokcol, None)

# Finds a color index in [0 .. lastokcol] closest to (r, g, b).
# <lastokcol> must be in [0 .. 255].
# blacklist - list of bools or None
def paletteGetClosestColorWithBlacklist (r, g, b, lastokcol, blacklist):
    global colmatchresults, numcolmatchresults

    col = r | (g << 8) | (b << 16)

    mindist = -1

    k = min(COLRESULTSIZ, numcolmatchresults)

    # uint32 colmatchresults[i] -- i8r8g8b8 (i - index)

    if numcolmatchresults:
        # check last color
        # (numcolmatchresults - 1) & (COLRESULTSIZ - 1) -- makes index into colmatchresults less than COLRESULTSIZ
        if col == (colmatchresults[(numcolmatchresults - 1) & (COLRESULTSIZ - 1)] & 0x00ffffff):
            return colmatchresults[(numcolmatchresults - 1) & (COLRESULTSIZ - 1)] >> 24

        for i in range(k):
            if col == (colmatchresults[i] & 0x00ffffff):
                mindist = i
                break

        if mindist != -1:
            idx = colmatchresults[mindist] >> 24

            if idx <= lastokcol and (not blacklist or not blacklist[idx]):
                return idx

    i = paletteGetClosestColorWithBlacklistNoCache(r, g, b, lastokcol, blacklist)

    colmatchresults[numcolmatchresults & (COLRESULTSIZ - 1)] = col | (i << 24)

    numcolmatchresults += 1

    return i

def paletteGetClosestColorWithBlacklistNoCache (r, g, b, lastokcol, blacklist):
    # just like in the paletteInitClosestColorMap
    j = (
        (r >> FASTPALRIGHTSHIFT) * FASTPALGRIDSIZ * FASTPALGRIDSIZ +
        (g >> FASTPALRIGHTSHIFT) * FASTPALGRIDSIZ + 
        (b >> FASTPALRIGHTSHIFT) +
        FASTPALGRIDSIZ * FASTPALGRIDSIZ + FASTPALGRIDSIZ + 1
    )

    # TODO: call paletteInitClosestColorGrid before
    # paletteInitClosestColorGrid()
    # paletteLoadFromDisk()
    # engineInit()
    # G_Startup()

    minrdist = rdist[coldist[r & FASTPALCOLDISTMASK] + FASTPALCOLDEPTH]
    mingdist = gdist[coldist[g & FASTPALCOLDISTMASK] + FASTPALCOLDEPTH]
    minbdist = bdist[coldist[b & FASTPALCOLDISTMASK] + FASTPALCOLDEPTH]

    mindist = min(minrdist, mingdist, minbdist) + 1

    r = FASTPALCOLDEPTH - r
    g = FASTPALCOLDEPTH - g
    b = FASTPALCOLDEPTH - b

    retcol = -1

    for k in range(26, -1, -1):
        i = colscan[k] + j

        if not colhere[i]:
            continue

        i = colhead[i]

        while True:
            pal1 = colmatch_palette[i * 3:i * 3 + 3]
            dist = gdist[pal1[1] + g]

            if dist >= mindist or i > lastokcol or (blacklist and blacklist[i]):
                i = colnext[i]

                if i < 0:
                    break

                continue

            dist += rdist[pal1[0] + r]

            if dist >= mindist:
                i = colnext[i]

                if i < 0:
                    break

                continue

            dist += bdist[pal1[2] + b]

            if dist >= mindist:
                i = colnext[i]

                if i < 0:
                    break

                continue

            mindist = dist
            retcol = i

            i = colnext[i]

            if i < 0:
                break

    if retcol >= 0:
        return retcol

    mindist = 2 ** 31 - 1  # INT32_MAX

    for i in range(lastokcol + 1):
        if blacklist and blacklist[i]:
            continue

        pal1 = colmatch_palette[i * 3:i * 3 + 3]

        dist = gdist[pal1[1] + g]

        if dist >= mindist:
            continue

        dist += rdist[pal1[0] + r]

        if dist >= mindist:
            continue

        dist += bdist[pal1[2] + b]

        if dist >= mindist:
            continue

        mindist = dist
        retcol = i

    return retcol

def paletteInitClosestColorMap (palette):
    global colmatch_palette, colhere, colhead

    colhere = [ False ] * len(colhere)
    colhead = [ 0 ] * len(colhead)

    colmatch_palette = palette

    for i in range(255, -1, -1):
        j = (                                                                              # rgb = (255, 128, 16)
            (palette[i * 3 + 0] >> FASTPALRIGHTSHIFT) * FASTPALGRIDSIZ * FASTPALGRIDSIZ +  # 255 >> 3 << 5 << 5 |
            (palette[i * 3 + 1] >> FASTPALRIGHTSHIFT) * FASTPALGRIDSIZ +                   # 128 >> 3 << 5 |
            (palette[i * 3 + 2] >> FASTPALRIGHTSHIFT) +                                    # 16  >> 3 |
            FASTPALGRIDSIZ * FASTPALGRIDSIZ + FASTPALGRIDSIZ + 1                           # 0b10000100001
        )

        if colhere[j]:
            colnext[i] = colhead[j]
        else:
            colnext[i] = -1

        colhead[j] = i
        colhere[j] = True

    paletteFlushClosestColor()

def paletteLoadFromDisk ():
    paletteInitClosestColorScale(30, 59, 11)
    paletteInitClosestColorGrid()

    for glb in glblend:
        defaultGLBlend(glb)

def paletteInitClosestColorScale (rscale, gscale, bscale):
    j = 0

    for i in range(256, -1, -1):
        rdist[i] = rdist[FASTPALCOLDEPTH * 2 - i] = j * rscale
        gdist[i] = gdist[FASTPALCOLDEPTH * 2 - i] = j * gscale
        bdist[i] = bdist[FASTPALCOLDEPTH * 2 - i] = j * bscale

        j += FASTPALRGBDIST - i * 2  # 513 - [ 512, 510, ..., 4, 2, 0 ]

def paletteInitClosestColorGrid ():
    i = 0

    deltaX = FASTPALGRIDSIZ * FASTPALGRIDSIZ  # 32 * 32 = 1024
    deltaY = FASTPALGRIDSIZ                   # 32
    deltaZ = 1                                # 1

    for x in range(-deltaX, deltaX + 1, deltaX):
        for y in range(-deltaY, deltaY + 1, deltaY):
            for z in range(-deltaZ, deltaZ + 1, deltaZ):
                colscan[i] = x + y + z
                i += 1

    i           = colscan[13]  # 0
    colscan[13] = colscan[26]  # 1057
    colscan[26] = i            # 0

    for i in range(FASTPALCOLDIST):
        if i < (FASTPALCOLDIST // 2):
            coldist[i] = i
        else:
            coldist[i] = FASTPALCOLDIST - i

def convertMusic (srcDir, dstDir):
    filesCount = 0
    totalSrcSize = 0
    totalDstSize = 0

    for srcPath in iterFiles(srcDir, True, [ '.xm' ]):
        print(f'Input file path:', srcPath)

        proc = subprocess.run([ 'ffprobe', '-v', 'quiet', '-show_format', '-show_streams', '-select_streams', 'a:0', '-print_format', 'json', srcPath ], stdout=subprocess.PIPE, stderr=subprocess.PIPE)

        if proc.returncode != 0:
            raise Exception('ffprobe error #1')

        info = parseJsonSafe(proc.stdout)

        if not info:
            raise Exception('ffprobe error #2')

        streamData = info['streams'][0]

        channelCount  = streamData['channels']
        channelLayout = streamData['channel_layout']

        print(f'Channels: { channelCount } ({ channelLayout })')

        formatData = info['format']

        bitRate = int(formatData['bit_rate'], 10) // 1000

        print(f'Bitrate: { bitRate }k')

        for key, value in formatData['tags'].items():
            value = re.sub(r'[\r\n\t]*\n+[\r\n\t]*', ' -- ', value.strip())

            print(f'> { key }: { value }')

        # -------------------------------------

        dstPath = joinPath(dstDir, getRelPath(srcPath, srcDir))
        dstPath = replaceExt(dstPath, '.ogg')

        # nearest greater or equal multiple of 16
        bitRate = ((bitRate - 1) | 15) + 1
        bitRate = max(48, bitRate)

        createDirs(getDirPath(dstPath))

        print(f'Target bitrate: { bitRate }k')
        print(f'Output file path:', dstPath)

        proc = subprocess.run([ 'ffmpeg', '-hide_banner', '-v', 'warning', '-y', '-i', srcPath, '-c:a', 'libvorbis', '-ar', '44100', '-b:a', f'{ bitRate }k', dstPath ], stdout=sys.stdout, stderr=sys.stderr)

        if proc.returncode != 0:
            message = proc.stderr.decode('utf-8')
            raise Exception(f'ffmpeg error #1: { message }')

        totalSrcSize += getFileSize(srcPath)
        totalDstSize += getFileSize(dstPath)
        filesCount += 1

        print(' ')

        # break

    ratio = (totalDstSize / totalSrcSize * 100) - 100

    print('-' * 50)
    print(' ')
    print('Total audio files:', filesCount)
    print('Total source size:', formatSize(totalSrcSize))
    print('Total target size:', formatSize(totalDstSize))
    print(f'Size increase: {ratio:+.1f}%')
    print(' ')

    # sys.exit()

def filterUnusedSounds ():
    defSounds = []

    for name, sound in collectDefinedSounds().items():
        if not sound['path']:
            print(f'Sound { name } doesn\'t have path')
            continue

        sndPath = joinPath(GAME_DIR, sound['path'])
        sndPath = getAbsPath(sndPath).lower()

        assert isFile(sndPath)

        defSounds.append(sndPath)

    count = 0
    size = 0

    for sndPath in iterFiles(SOUNDS_DIR, True, [ '.ogg' ]):
        if getAbsPath(sndPath).lower() in defSounds:
            continue

        sndRelPath = getRelPath(sndPath, SOUNDS_DIR)

        if sndRelPath.lower().startswith('music'):
            continue

        sndSize = getFileSize(sndPath)

        count += 1
        size  += sndSize

        print(sndRelPath, formatSize(sndSize))

    print(count)
    print(formatSize(size))

def collectDefinedSounds ():
    soundMap = {}

    lines = readText(joinPath(GAME_DIR, 'scripts', 'sounds.con'))
    lines = lines.split('\n')

    for line in lines:
        line = line.strip()

        if not line:
            continue

        line = re.split(r'\s+', line)

        match line[0]:
            case 'define':
                sndName = line[1]
                sndId = int(line[2], 10)

                assert sndName not in soundMap

                soundMap[sndName] = {
                    'id': sndId,
                    'path': None,
                    'params': None
                }
            case 'definesound':
                sndName = line[1]
                sndPath = line[2]

                assert sndName in soundMap

                # TODO: src/sounds.cpp:599
                soundMap[sndName]['path'] = sndPath
                soundMap[sndName]['params'] = {
                    'minPitch': int(line[3], 10),  # int
                    'maxPitch': int(line[4], 10),  # int
                    'priority': int(line[5], 10),  # int
                    'type':     int(line[6], 10),  # int
                    'distance': int(line[7], 10),  # int
                    'volume':   1.0,               # float
                }
            case _:
                continue

    print(toJson(soundMap))

    return soundMap



if __name__ == '__main__':
    # loadArtFile(joinPath(GAME_DIR, 'tiles000.art'))
    # loadPalettes()
    # convertMusic(joinPath(GAME_DIR, 'sounds', 'music'), joinPath(GAME_DIR, 'sounds', 'music_converted'))
    collectDefinedSounds()
    # filterUnusedSounds()

