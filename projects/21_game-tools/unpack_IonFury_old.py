# Ion Fury Extractor

from deps.utils import *
from deps.reader import *



SCRIPT_DIR = getDirPath(getAbsPath(__file__))
GAME_DIR = r'G:\Steam\steamapps\common\Ion Fury\files'

SIGNATURE_ART = b'BUILDART'

MAXTILES = 30720

rottile = []  # rottile_t rottile[MAXTILES]
picanm  = []  # picanm_t picanm[MAXTILES]
gotpic  = [ 0 ] * MAXTILES
tilesiz = []
picsiz  = [ 0 ] * MAXTILES
faketiledata = [ None ] * MAXTILES
faketilesize = [ 0 ] * MAXTILES

pow2long = [
    1, 2, 4, 8,
    16, 32, 64, 128,
    256, 512, 1024, 2048,
    4096, 8192, 16384, 32768,
    65536, 131072, 262144, 524288,
    1048576, 2097152, 4194304, 8388608,
    16777216, 33554432, 67108864, 134217728,
    268435456, 536870912, 1073741824, 2147483647
]


# artLoadFiles
def loadArts (filePath):
    print('Reading', filePath)

    for i in range(MAXTILES):
        rottile.append({
            'newtile': -1,
            'owner':   -1
        })

        picanm.append({
            'num':       0,
            'xofs':      0,
            'yofs':      0,
            'sf':        0,
            'tileflags': 0,
        })

        tilesiz.append({
            'x': 0,
            'y': 0
        })

    with openFile(filePath) as f:
        # artReadHeader (artheader_t)
        # ---------------------------

        signature = f.read(8)

        assert signature == SIGNATURE_ART

        version, tileCount, tileStart, tileEnd = f.struct('<4I')

        assert version == 1

        tileCount = tileEnd - tileStart + 1

        # print(version, tileCount, tileStart, tileEnd)

        # artReadManifest
        # ---------------------------

        resX = f.i16(tileCount)
        resY = f.i16(tileCount)

        # local->tileread is a bitmap[tileCount]
        # if bit local->tileread[localIndex] is set - tile is loaded 
        # global tilesiz contains sizes
        # global picanm contains anims info
        # global picsiz contains greater power of 2 of tile size (see tileUpdatePicSiz)
        for i in range(tileStart, tileEnd + 1):
            localIndex = i - tileStart
            size = resX[i] * resY[i]

            picanmdisk = f.u32()

            if size == 0:
                continue

            tilesiz[i]['x'] = resX[i]
            tilesiz[i]['y'] = resY[i]

            # tileConvertAnimFormat
            # ---------------------------

            picanm[i]['num']  = picanmdisk & 63
            picanm[i]['xofs'] = (picanmdisk >> 8) & 255
            picanm[i]['yofs'] = (picanmdisk >> 16) & 255
            picanm[i]['sf']   = ((picanmdisk >> 24) & 15) | (picanmdisk & 192)

            # print(localIndex, size, thispicanm)

        # artPreloadFile
        # ---------------------------

        for i in range(tileStart, tileEnd + 1):
            localIndex = i - tileStart
            size = resX[i] * resY[i]

            if size == 0:
                # tileDelete(i)
                continue

            data = f.read(size)

            faketiledata[i] = data
            faketilesize[i] = size

            # store LZ4-compressed data in memory
            # saveMipAsPNG(joinPath(r'C:\Users\Berrigan\Desktop\IFTiles', f'{i:09d}.png'), data, resX[i], resY[i])
            # break

        # artUpdateManifest
        # tileUpdatePicSiz
        # ---------------------------

        for i in range(MAXTILES):
            j = 15

            while ((j > 1) and (pow2long[j] > tilesiz[i]['x'])):
                j -= 1

            picsiz[i] = j

            k = 15

            while ((k > 1) and (pow2long[k] > tilesiz[i]['y'])):
                k -= 1

            picsiz[i] |= k << 4


MAXPALOOKUPS = 256
MAXBASEPALS  = 256
g_noFloorPal = [ 0 ] * MAXPALOOKUPS

palette = b'\x00' * 768
basepaltable = [ palette ] + [ None ] * (MAXBASEPALS - 1)
paletteloaded = 0

PALETTE_MAIN     = 1 << 0
PALETTE_SHADE    = 1 << 1
PALETTE_TRANSLUC = 1 << 2

FASTPALCOLDEPTH = 256
FASTPALRIGHTSHIFT = 3
FASTPALRGBDIST = FASTPALCOLDEPTH * 2 + 1
rdist = [ 0 ] * FASTPALRGBDIST
gdist = [ 0 ] * FASTPALRGBDIST
bdist = [ 0 ] * FASTPALRGBDIST
FASTPALGRIDSIZ = FASTPALCOLDEPTH >> FASTPALRIGHTSHIFT  # 256 >> 3 = 32
colhere = [ 0 ] * ((FASTPALGRIDSIZ + 2) * (FASTPALGRIDSIZ + 2) * (FASTPALGRIDSIZ + 2))  # bitmap
colhead = [ 0 ] * ((FASTPALGRIDSIZ + 2) * (FASTPALGRIDSIZ + 2) * (FASTPALGRIDSIZ + 2))  # char[...]
colnext = [ 0 ] * 256  # int32_t[256]
FASTPALCOLDIST = 1 << FASTPALRIGHTSHIFT
FASTPALCOLDISTMASK = FASTPALCOLDIST - 1
coldist = [ 0 ] * FASTPALCOLDIST  # uint8_t[FASTPALCOLDIST]
colscan = [ 0 ] * 27  # int32_t[27]
colmatch_palette = None

COLRESULTSIZ = 4096
colmatchresults = [ 0 ] * COLRESULTSIZ  # uint32_t[COLRESULTSIZ]
numcolmatchresults = None  # int32_t


def paletteSetColorTable (rawId, table):
    global palette

    if rawId == 0:
        palette = table

    basepaltable[rawId] = table


def paletteFlushClosestColor ():
    global colmatchresults, numcolmatchresults

    colmatchresults = [ 0 ] * COLRESULTSIZ
    numcolmatchresults = 0


def paletteInitClosestColorMap (pal):
    global colmatch_palette

    colmatch_palette = pal

    pal1 = 768 - 3

    for i in range(255, -1, -1):
        # 15-bit color?        
        # 111101111011110
        #     10000100001
        j = (
            (pal[pal1 + 0] >> FASTPALRIGHTSHIFT) * FASTPALGRIDSIZ * FASTPALGRIDSIZ +  # X >> 5 << 5 << 5 + 
            (pal[pal1 + 1] >> FASTPALRIGHTSHIFT) * FASTPALGRIDSIZ +                   # X >> 5 << 5 + 
            (pal[pal1 + 2] >> FASTPALRIGHTSHIFT) +                                    # X >> 5 +
            FASTPALGRIDSIZ * FASTPALGRIDSIZ + FASTPALGRIDSIZ + 1                      # 0b10000100001
        )

        print(j)

        # colhere[4913] - bitmap of 39304 bits
        # char colhead[39304]

        if colhere[j]:
            colnext[i] = colhead[j]
        else:
            colnext[i] = -1

        colhead[j] = i
        colhere[j] = 1

        pal1 -= 3

    paletteFlushClosestColor()

    print('-' * 100)
    for c in colnext:
        print(c)



def loadPalettes ():
    global paletteloaded
    print('Loading palettes...')

    # nofloorpalrange 1 255
    # ---------------------------

    b = 1
    e = 255

    for i in range(b, e + 1):
        g_noFloorPal[i] = 1

    # basepalette 0 { raw { file "/palette/basepalette_000.raw" } }
    # ---------------------------

    rawId = 0
    rawPath = joinPath(GAME_DIR, 'palette', 'basepalette_000.raw')

    with open(rawPath, 'rb') as f:
        palbuf = f.read()

    paletteSetColorTable(rawId, palbuf)

    if rawId == 0:
        paletteInitClosestColorMap(palette)
        paletteloaded |= PALETTE_MAIN


'''
def paletteInitClosestColorScale ():
    FASTPALCOLDEPTH = 256
    FASTPALRGBDIST = FASTPALCOLDEPTH * 2 + 1
    # int32_t

    rdist = [ 0 ] * FASTPALRGBDIST
    gdist = [ 0 ] * FASTPALRGBDIST
    bdist = [ 0 ] * FASTPALRGBDIST

    rscale = 30
    gscale = 59
    bscale = 11

    j = 0

    for i in range(256, -1, -1):
        rdist[i] = rdist[FASTPALCOLDEPTH * 2 - i] = j * rscale
        gdist[i] = gdist[FASTPALCOLDEPTH * 2 - i] = j * gscale
        bdist[i] = bdist[FASTPALCOLDEPTH * 2 - i] = j * bscale

        j += FASTPALRGBDIST - (i << 1)

        print(j, FASTPALRGBDIST - (i << 1), j * rscale, j * gscale, j * bscale)


FASTPALCOLDEPTH   = 256
FASTPALRIGHTSHIFT = 3
FASTPALRGBDIST    = FASTPALCOLDEPTH * 2 + 1
FASTPALGRIDSIZ    = FASTPALCOLDEPTH >> FASTPALRIGHTSHIFT
colheadSize = (FASTPALGRIDSIZ + 2) * (FASTPALGRIDSIZ + 2) * (FASTPALGRIDSIZ + 2)
colhereSize = (colheadSize + 7) >> 3
'''





def main ():
    paletteInitClosestColorMap(r"G:\Steam\steamapps\common\Ion Fury\files\palette\basepalette_000.raw")

'''
- nofloorpalrange 1 255 - делает g_noFloorPal[i] = 1 для всех i из [1; 255]
- basepalette <id>0 { raw { file "..." } } - [id == 0] делает paletteSetColorTable и paletteInitClosestColorMap
  basepaltable[id] = data
- 

'''


'''
import struct
from PIL import Image

def saveMipAsPNG (imagePath, indices, width, height):
    palette = []

    resolution = width * height

    with openFile(r"G:\Steam\steamapps\common\Ion Fury\files\palette\basepalette_000.raw") as f:
        for i in range(256):
            palette.append(list(f.u8(3)) + [ 255 ])

    pixels = [ palette[i] for i in indices ]
    pixels = sum(pixels, [])

    data = struct.pack(f'<{ (resolution * 4) }B', *pixels)

    image = Image.frombytes('RGBA', (width, height), data)

    image.save(getAbsPath(imagePath))
'''

'''
nofloorpalrange <b>1 <e>255
    b = max(b, 1)
    e = min(e, 255)

    for (i = b; i <= e; i++)
        g_noFloorPal[i] = 1;

-------------------------------------

basepalette <id>0 { raw { file "/palette/basepalette_000.raw" } }

basepaltable[id] = readFile("/palette/basepalette_000.raw")

if didLoadPal && id == 0:
    paletteInitClosestColorMap(palette);  // fill in colhere and colhead
    paletteloaded |= PALETTE_MAIN;

-------------------------------------

palookup <id>0 { raw { file "/palette/palookup_000.raw" } }

data = readFile("/palette/basepalette_000.raw", 256 * 32)

if len(data) == 256 * 32:  // shade table
    didLoadShade = 1
    paletteSetLookupTable(id, data):
        palookup[id] = data
else:
    ...

if (didLoadShade && id == 0):
    paletteloaded |= PALETTE_SHADE;

-------------------------------------

blendtable <id>0 { raw { file "/palette/blendtable_000.raw" } }

data = readFile("/palette/blendtable_000.raw", 256 * 256)

paletteSetBlendTable(id, data):
    blendtable[id] = data

didLoadTransluc = 1;

if (didLoadTransluc && id == 0):
    paletteloaded |= PALETTE_TRANSLUC;

'''

if __name__ == '__main__':
    loadArts(joinPath(GAME_DIR, 'tiles000.art'))
    loadPalettes()
    # main()