import struct
import os


GAME_DIR = r'G:\Steam\steamapps\common\Ion Fury\files'
SIGNATURE_ART = b'BUILDART'
MAX_TILES = 30720
MAX_USER_TILES = MAX_TILES - 256

#define 
#define MAXUSERTILES (MAXTILES-256)


def readStruct (structFormat, file):
    structSize = struct.calcsize(structFormat)
    dataChunk = file.read(structSize)
    items = struct.unpack(structFormat, dataChunk)

    return items[0] if len(items) == 1 else items


class picanm_t:
    def __init__ (self):
        self.num  = 0       # uint8_t - animate number
        self.xofs = 0       # int8_t
        self.yofs = 0       # int8_t
        self.sf   = 0       # uint8_t - anim. speed and flags
        self.tileflags = 0  # uint8_t - tile-specific flags, such as true non-power-of-2 drawing.


class rottile_t:
    def __init__ (self):
        self.newtile = 0  # int16_t
        self.owner   = 0  # int16_t


class artheader_t:
    def __init__ (self):
        self.tileStart = 0  # int32_t
        self.tileEnd   = 0  # int32_t
        self.tileCount = 0  # int32_t
        self.tileRead  = 0  # uint8_t*


def unpackArt (filePath):
    # <artLoadFiles>
    # --------------------------------------

    if not os.path.isfile(filePath):
        print('File does not exist:', filePath)
        return

    with open(filePath, 'rb') as f:
        signature = f.read(8)

        if signature != SIGNATURE_ART:
            print('Wrong signature:', signature)
            return

        # tilesiz : vec2_16_t[MAXTILES]
        # picanm[MAXTILES] - animations? 8 * 4 bytes
        # rottile[MAXTILES] - 16 * 2 bytes
        # tilesXXX: XXX < 200 - indexed tiles; XXX >= 200 - per-map tiles 

        version = readStruct('<i', f)

        if version != 1:
            print('Unknown version:', version)
            return

        # --------------------------------

        rottile = []

        for i in range(MAXTILES):
            rt = rottile_t()

            rt.newtile = -1
            rt.owner   = -1

            rottile.append(rt)

        # <artReadIndexedFile>
        # <artReadHeader>

        # Do not use tileCount read from the file
        tileCount, tileStart, tileEnd = readStruct('<3i', f)

        if tileStart >= MAX_USER_TILES or tileEnd >= MAX_USER_TILES or tileStart > tileEnd:
            print('Unable to load:', filePath)
            return

        tileCount = tileEnd - tileStart + 1

        header = artheader_t()

        header.tileStart = tileStart
        header.tileEnd   = tileEnd
        header.tileCount = tileCount

        # </artReadHeader>

        # TODO: read per-map tiles here

        # <artReadManifest>

        valueCount = tileCount * 2
        values = readStruct(f'<{ valueCount }h', f)

        assert len(values) == valueCount

        tileSizes = [
            (
                values[i],
                values[tileCount + i]
            ) for i in range(tileCount)
        ]

        picanms = []

        for tileSizeX, tileSizeY in tileSizes:
            tileSize = tileSizeX * tileSizeY

            picanmdisk = readStruct('<I', f)

            if tileSize == 0:
                continue

            # <tileConvertAnimFormat>

            picanm = picanm_t()

            picanm.num  = picanmdisk & 63;
            picanm.xofs = (picanmdisk >> 8) & 255;
            picanm.yofs = (picanmdisk >> 16) & 255;
            picanm.sf   = ((picanmdisk >> 24) & 15) | (picanmdisk & 192);

            picanms.append(picanm)

            # </tileConvertAnimFormat>

            print(picanm.num, picanm.xofs, picanm.yofs, picanm.sf)

        print(f.tell())




'''
int32_t       mip1leng
vec3<int32_t> voxsiz (BE?)
vec3<float>   voxpiv
seek((voxsiz.x + 1) << 2, fromCurPos)
'''

if __name__ == '__main__':
    unpackArt(os.path.join(GAME_DIR, 'tiles000.art'))