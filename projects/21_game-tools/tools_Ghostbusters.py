# Ghostbusters The Video Game Remastered Tools
# Engine: Infernal Engine
# Games on the engine: https://vk.cc/cKTRi7

import sys

sys.path.insert(0, r'C:\Projects\PythonLib\python\v001')

from bfw.utils import *
from bfw.reader import *
from bfw.types.enums import Enum
from bfw.media.ffmpeg.ffprobe import FFProbe



GAME_DIR       = r'G:\Steam\steamapps\common\Ghostbusters The Video Game Remastered'
POD_EXT        = '.pod'
POD_SIGNATURE  = b'POD6'
POD_ENTRY_SIZE = 24


class PODFlag (Enum):
    Compressed = 1 << 3


class PODHeader:
    def __init__ (self):
        self.itemCount   = None
        self._unk1       = None
        self.indexOffset = None
        self.namesSize   = None
        self.nextName    = None
        self.namesOffset = None


class PODItem:
    def __init__ (self):
        self.name         = None
        self.nameOffset   = None
        self.compSize     = None
        self.offset       = None
        self.decompSize   = None
        self.flags        = None
        self._unk1_0      = None
        self.isCompressed = None
        self.isEmpty      = None


# TODO: unpack "patch.pod" last
def unpack (filePath, unpackDir=None):
    filePath = getAbsPath(filePath)

    if not isFile(filePath):
        raise Exception(f'File does not exist: { filePath }')

    if not unpackDir:
        unpackDir = filePath + '.unpacked'

    with openFile(filePath) as f:
        signature = f.read(4)

        if signature != POD_SIGNATURE:
            raise Exception(f'Not a POD file: { filePath }')

        header = PODHeader()

        header.itemCount   = f.u32()
        header._unk1       = f.u32()  # flags?
        header.indexOffset = f.u32()
        header.namesSize   = f.u32()
        header.nextName    = f.string(size=108)
        header.namesOffset = header.indexOffset + POD_ENTRY_SIZE * header.itemCount

        assert header._unk1 in [ 992, 1000 ], header._unk1

        pji(header)

        f.seek(header.indexOffset)

        items = [ PODItem() for _ in range(header.itemCount) ]

        for item in items:
            item.nameOffset   = f.u32()
            item.compSize     = f.u32()
            item.offset       = f.u32()
            item.decompSize   = f.u32()
            item.flags        = f.u32()
            item._unk1_0      = f.u32()
            item.isCompressed = bool(item.flags & PODFlag.Compressed)
            item.isEmpty      = item.compSize == 0

            assert item._unk1_0 in [ 0 ], _unk1_0

        for item in items:
            f.seek(header.namesOffset + item.nameOffset)

            item.name = f.string()

        for item in items:
            if item.isEmpty:
                data = b''
            else:
                f.seek(item.offset)

                data = f.read(item.compSize)

                if item.isCompressed:
                    data = decompressData(data)

                    decompSize = len(data)

                    if decompSize != item.decompSize:
                        raise Exception(f'Decompressed data size ({ decompSize }) does not match expected value ({ item.decompSize })')

            assetPath = getAbsPath(joinPath(unpackDir, item.name))

            print(assetPath)

            createFileDirs(assetPath)
            writeBin(assetPath, data)
    

def unpackAll (gameDir, unpackDir=None):
    if not isDir(gameDir):
        raise Exception(f'Game directory does not exist: { gameDir }')

    for filePath in iterFiles(gameDir, True, [ POD_EXT ]):
        print(filePath)

        unpack(filePath, unpackDir)

        print(' ')


def unpackSMP (smpPath):
    smpPath = getAbsPath(smpPath)

    if not isFile(smpPath):
        raise Exception(f'File does not exist: { smpPath }')

    with openFile(smpPath) as f:
        version = f.u32()

        assert version in [ 6 ], version

        guid             = f.read(16)
        _unk1_0          = f.u32()
        timeBaseDuration = f.u32()
        dataOffset       = f.u32()
        dataSize         = f.u32()
        _unk3_9          = f.u32()
        channelCount     = f.u32()
        bitDepth         = f.u32()
        sampleRate       = f.u32()

        assert _unk1_0 in [ 0 ], _unk1_0
        assert _unk3_9 in [ 9 ], _unk3_9


def unpackSMPs (gameDir):
    if not isDir(gameDir):
        raise Exception(f'Game directory does not exist: { gameDir }')

    for filePath in iterFiles(gameDir, True, [ '.smp' ]):
        print(filePath)

        unpackSMP(filePath)

        print(' ')

from math import log2

def unpackTexture (texPath):
    texPath = getAbsPath(texPath)

    if not isFile(texPath):
        raise Exception(f'File does not exist: { texPath }')

    # all textures are PoT
    with openFile(texPath) as f:
        version = f.u32()

        assert version in [ 7 ], version

        guid     = f.read(16)
        _unk1_0  = f.u32()
        unk2     = f.u32()
        res1     = f.u32()
        res2     = f.u32()
        unk3     = f.u32()
        mipCount = f.u32()
        _unk5_0  = f.u32()

        if mipCount and unk2 == 3:
            _s1 = res1
            _s2 = res2

            pxCount = 0

            for i in range(mipCount):
                pxCount += _s1 * _s2

                _s1 //= 2
                _s2 //= 2

            # unk2 == 3:  4.0
            # unk2 == 24: 24.0
            # unk2 == 43: ~0.5
            # unk2 == 47: 2.0
            # unk2 == 50: 1.0

            print(f.remaining() - (pxCount * 4), unk2, unk3, mipCount)

        assert _unk1_0 in [ 0 ], _unk1_0
        assert _unk5_0 in [ 0 ], _unk5_0
        assert unk2 in [ 3, 24, 43, 47, 50 ], unk2
        assert unk3 in [ 0, 1, 8 ], unk3



def unpackTextures (gameDir):
    if not isDir(gameDir):
        raise Exception(f'Game directory does not exist: { gameDir }')

    for filePath in iterFiles(gameDir, True, [ '.tex' ]):
        print(filePath)

        unpackTexture(filePath)

        print(' ')


def decryptSaveFile (filePath):
    data = bytearray(readBin(filePath))

    key = bytes.fromhex((
        '00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00' +
        '00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00' +
        '00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00' +
        '00 44_58_73 00 97_4D_A9 00 85_3B_60 00 84_E5_47' + 
        '00 17_88_14 00 00 00 00 00 00 00 00 00 00 00 00' + 
        '00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00' +
        '00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00' +
        '00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00' +
        '00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00' +
        '00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00' +
        '00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00' +
        '00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00' +
        '00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00' +
        '00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00' +
        '00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00' +
        '00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00'
    ).replace('_', ''))

    assert len(key) == 256

    # key = readBin(r"G:\Steam\steamapps\common\Ghostbusters The Video Game Remastered\ghost_w32.fpt")

    data = xorBuffer(data, key)

    writeBin(filePath + '.dec', data)




def main ():
    unpackAll(GAME_DIR, joinPath(GAME_DIR, '.unpacked'))
    # unpackSMPs(GAME_DIR)
    # unpackTextures(GAME_DIR)
    # decryptSaveFile(r'C:\Users\Berrigan\Documents\GHOSTBUSTERS\PROFILE.SAV')

    # pjp(FFProbe.getMeta(
    #     r"G:\Steam\steamapps\common\Ghostbusters The Video Game Remastered\.unpacked\1.ogg",
    #     # includeData      = True,   # -show_data
    #     # includeDataHash  = True,   # -show_data_hash
    #     includeFormat    = True,   # -show_format
    #     # includePackets   = True,   # -show_packets
    #     # includeFrames    = True,   # -show_frames
    #     # includeLog       = True,   # -show_log
    #     includeStreams   = True,   # -show_streams
    #     # includePrograms  = True,   # -show_programs
    #     # includeChapters  = True,   # -show_chapters
    #     # countFrames      = True,   # -count_frames
    #     # countPackets     = True,   # -count_packets
    #     # includeProgVer   = True,   # -show_program_version
    #     # includeLibVer    = True,   # -show_library_versions
    #     # includePixFormat = True,   # -show_pixel_formats
    # ))



if __name__ == '__main__':
    main()


'''
.ani     3, 5, 6, 7
.bfm     20
.bst     127
.cib     14
.cinemat 10
.fxa     b'FACE'
.fxe     b'FACE'
.hbb     10
.mtb     414
.phys2b  6
.skb     30
.smb     19
.smp     6   ~
.snb     13
.subb    3
.tex     7
.tfb     9
.ui      768
'''