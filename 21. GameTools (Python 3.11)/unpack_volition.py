# Volition Game Engine VPP Extractor

import os, struct, json, ctypes, zlib
from collections import namedtuple

GAME_DIR = r'G:\Steam\steamapps\common\Saints Row IV'

VPP_SIGNATURE = b'\xCE\x0A\x89\x51'
VPP_HEADER_SIZE = 40
SUPPORTED_ENGINE_VERSIONS = [ 10 ]

UINT32_MAX = 0xFFFFFFFF

def formatBytes (byteSeq):
    return ' '.join([ '{:02X}'.format(b) for b in byteSeq ])

def readStruct (structFormat, descriptor):
    items = struct.unpack(structFormat, descriptor.read(struct.calcsize(structFormat)))
    return items[0] if len(items) == 1 else items

def readNullString (descriptor):
    buff = b''

    while True:
        byte = descriptor.read(1)

        if byte == b'\x00':
            break

        buff += byte

    return buff.decode('utf-8')


VPPHeader = namedtuple('VPPHeader', ('engineVersion', 'unk1', 'fileSize', 'flags', 'entryCount', 'indexSize', 'namesSize', 'decompSize', 'compSize'))
ItemHeader = namedtuple('ItemHeader', ('nameRelOffset', 'zero1', 'contentRelOffset', 'decompSize', 'compSize', 'flags', 'name'))

def decompressData (data):
    decompress = zlib.decompressobj()
    data = decompress.decompress(data)
    data += decompress.flush()

    return data


_tmp = {}


class Unpacker:
    def __init__ (self, vppFilePath):
        self.vppFilePath = vppFilePath
        self.vppHeader = None
        self.items = None
        self.f = None

    def __del__ (self):
        pass

    def unpack (self):
        print('Unpacking {}'.format(self.vppFilePath))

        if not self.vppFilePath or not os.path.isfile(self.vppFilePath):
            raise FileNotFoundError('VPP doesn\'t exist: {}'.format(self.vppFilePath))

        fileSize = os.path.getsize(self.vppFilePath)

        if fileSize < VPP_HEADER_SIZE:
            raise Exception('VPP file is too small to be valid')

        with open(self.vppFilePath, 'rb') as self.f:
            vppHeader = self.readHeader()

            isContentOrItemsCompressed = vppHeader.flags & 1            
            isContentCompressed = vppHeader.flags == 18435  # TODO: replace with flag checking
            # isContentCompressed = isContentOrItemsCompressed and bool(vppHeader.flags & 2)
            contentSizeInFile = vppHeader.compSize if isContentOrItemsCompressed else vppHeader.decompSize
            expectedFileSize = VPP_HEADER_SIZE + vppHeader.indexSize + vppHeader.namesSize + contentSizeInFile

            if expectedFileSize != fileSize:
                raise Exception('VPP file is corrupted: {}'.format(self.vppFilePath))

            namesBaseOffset = VPP_HEADER_SIZE + vppHeader.indexSize
            contentBaseOffset = namesBaseOffset + vppHeader.namesSize

            items = self.readIndex(namesBaseOffset)

            self.readContent(isContentCompressed, contentBaseOffset)

        self.f = None


    def readHeader (self):
        signature = self.f.read(4)

        if signature != VPP_SIGNATURE:
            raise Exception('VPP signature check failed')

        # unk1 - always large number, seems like CRC32

        # 4 possible flags:
        # - 1: 1       - file has compressed entire content OR some compressed items
        # - 2: 1 << 1  - ? in combination with flag 1 means entire content compression, but this flag can be set alone - I dunno what it does in this case
        # - 3: 1 << 11 - ? always set with flags 1 and 4
        # - 4: 1 << 14 - ? always set with flags 1 and 3            
        # Possible combinations:
        # - 0             (0)     - no compression at all
        # - 2             (2)     - effect unknown
        # - 1 & 3 & 4     (18433) - file has compressed entire content or items (effect of 3 & 4 is unknown)
        # - 1 & 2 & 3 & 4 (18435) - file has compressed entire content (not sure, maybe just a coincidence) (effect of 3 & 4 is unknown)
        # Assumptions:
        # - Level of compression
        # - Compression method

        vppHeader = VPPHeader(*readStruct('<9I', self.f))

        print(vppHeader)

        if vppHeader.engineVersion not in SUPPORTED_ENGINE_VERSIONS:
            raise Exception('Unsupported game engine version: {}'.format(engineVersion))

        self.vppHeader = vppHeader

        return vppHeader

    def readIndex (self, namesBaseOffset):
        items = []

        for i in range(self.vppHeader.entryCount):
            # 3 possible flags:
            # - 1: 1       - item compressed
            # - 2: 1 << 16 - ? set for comp & non-comp
            # - 3: 1 << 20 - ? set for comp & non-comp
            # Possible combinations:
            # - 2     (65536)   - ?
            # - 2 & 1 (65537)   - item compressed (effect of flag 2 is unknown)
            # - 3     (1048576) - ?
            # - 3 & 1 (1048577) - item compressed (effect of flag 3 is unknown)
            nameRelOffset, zero1, contentRelOffset, decompSize, compSize, flags = readStruct('<6I', self.f)
            items.append([ nameRelOffset, zero1, contentRelOffset, decompSize, compSize, flags ])

        for i, item in enumerate(items):
            offset = namesBaseOffset + item[0]
            self.f.seek(offset)
            name = readNullString(self.f)
            item.append(name)
            items[i] = ItemHeader(*item)

        self.items = items

        return items

    def readContent (self, isContentCompressed, contentBaseOffset):
        data = None

        if isContentCompressed:
            self.f.seek(contentBaseOffset)
            data = decompressData(self.f.read(self.vppHeader.compSize))

            assert len(data) == self.vppHeader.decompSize, 'Decompressed content size check failed'
            # print('Entire content decompressed')
        else:
            for item in self.items:
                offset = contentBaseOffset + item.contentRelOffset
                self.f.seek(offset)
                isCompressed = bool(item.flags & 1)

                if isCompressed:
                    data = decompressData(self.f.read(item.compSize))

                    assert len(data) == item.decompSize, 'Decompressed item size check failed'
                    # print('Item content decompressed')
                else:
                    data = self.f.read(item.decompSize)

                    assert data != b'\x78\xDA', 'Item should not be compressed'
                    # print('Item content read')

        # if self.vppHeader _tmp


def unpackAll (gameDir):
    vppDir = os.path.join(gameDir, 'packfiles', 'pc', 'cache')

    for item in os.listdir(vppDir):
        # if item in [ 'cutscene_tables.vpp_pc', 'da_tables.vpp_pc', 'misc.vpp_pc', 'misc_tables.vpp_pc', 'patch_compressed.vpp_pc', 'shaders.vpp_pc', 'sound_turbo.vpp_pc', 'startup.vpp_pc', 'vehicles_preload.vpp_pc' ]:
        #     continue
        itemPath = os.path.join(vppDir, item)

        if not item.lower().endswith('.vpp_pc') or not os.path.isfile(itemPath):
            continue

        unpacker = Unpacker(itemPath)
        unpacker.unpack()

        # break


def unpack (vppFilePath):
    unpacker = Unpacker(vppFilePath)
    unpacker.unpack()


if __name__ == '__main__':
    unpackAll(GAME_DIR)
    # unpack(os.path.join(GAME_DIR, 'packfiles', 'pc', 'cache', 'cutscene_tables.vpp_pc'))
    # unpack(os.path.join(GAME_DIR, 'packfiles', 'pc', 'cache', 'soundboot.vpp_pc'))
    # unpack(os.path.join(GAME_DIR, 'packfiles', 'pc', 'cache', 'customize_item.vpp_pc'))
    # unpack(os.path.join(GAME_DIR, 'packfiles', 'pc', 'cache', 'shaders.vpp_pc'))

    # for item in _tmp:
    #     print(item)

    # print(len(_tmp))

    # print(bin(_tmpFlags))
    # print(len(_tmp))

    # print(_tmpCounter / 1024 / 1024 / 1024)
    print('Done')

'''

0C 3C F0 3A
81 06 10 15
                         compFlags  entContComp
characters.vpp_pc         | 0     | -           | # cont. compr == UINT32_MAX; no compression at all 
customize_item.vpp_pc     | 0     | -           | # cont. compr == UINT32_MAX; no compression at all
customize_player.vpp_pc   | 0     | -           | 
cutscenes.vpp_pc          | 0     | -           | 
cutscene_sounds.vpp_pc    | 0     | -           | 
decals.vpp_pc             | 0     | -           | 
dlc1.vpp_pc               | 0     | -           | 
dlc2.vpp_pc               | 0     | -           | 
dlc3.vpp_pc               | 0     | -           | 
dlc4.vpp_pc               | 0     | -           | 
dlc5.vpp_pc               | 0     | -           | 
dlc6.vpp_pc               | 0     | -           | 
effects.vpp_pc            | 0     | -           | 
high_mips.vpp_pc          | 0     | -           | 
interface.vpp_pc          | 0     | -           | 
interface_startup.vpp_pc  | 0     | -           | 
items.vpp_pc              | 0     | -           | 
patch_uncompressed.vpp_pc | 0     | -           | 
player_morph.vpp_pc       | 0     | -           | 
player_taunts.vpp_pc      | 0     | -           | 
preload_effects.vpp_pc    | 0     | -           | 
preload_items.vpp_pc      | 0     | -           | 
skybox.vpp_pc             | 0     | -           | 
sounds.vpp_pc             | 0     | -           | 
sounds_common.vpp_pc      | 0     | -           | 
sr3_city_0.vpp_pc         | 0     | -           | 
sr3_city_1.vpp_pc         | 0     | -           | 
sr3_city_missions.vpp_pc  | 0     | -           | 
superpowers.vpp_pc        | 0     | -           | 
vehicles.vpp_pc           | 0     | -           | 
voices.vpp_pc             | 0     | -           | # cont. compr == UINT32_MAX; no compression at all 
                          |       |             | 
cutscene_tables.vpp_pc    | 18433 | -           | # cont. compr != UINT32_MAX; per item compr
da_tables.vpp_pc          | 18433 | -           | # cont. compr != UINT32_MAX; per item compr
misc.vpp_pc               | 18433 | -           | 
misc_tables.vpp_pc        | 18433 | -           | 
patch_compressed.vpp_pc   | 18433 | -           | 
shaders.vpp_pc            | 18433 | -           | 
sound_turbo.vpp_pc        | 18433 | -           | 
startup.vpp_pc            | 18433 | -           | 
vehicles_preload.vpp_pc   | 18433 | -           | 
                          |       |             | 
preload_anim.vpp_pc       | 2     | -           | # cont. compr == UINT32_MAX; no compression at all
preload_rigs.vpp_pc       | 2     | -           | # cont. compr == UINT32_MAX; no compression at all
                          |       |             | 
soundboot.vpp_pc          | 18435 | +           | # cont. compr != UINT32_MAX; entire content compressed

'''