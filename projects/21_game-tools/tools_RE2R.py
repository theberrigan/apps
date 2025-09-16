# Resident Evil 2 Remake Tools
# Engine: RE Engine

import sys

sys.path.insert(0, r'C:\Projects\PythonLib\python\v001')

from zstd import ZSTD_uncompress

from bfw.utils import *
from bfw.reader import *
from bfw.types.enums import Enum



GAME_DIR = r'G:\Steam\steamapps\common\RESIDENT EVIL 2  BIOHAZARD RE2'

PAK_EXT       = '.pak'
PAK_SIGNATURE = b'KPKA'



class EntryFlag:
    Unk1       = 1 << 0  # encrypted???
    Compressed = 1 << 1  # compressed
    Unk2       = 1 << 8  # non-compressed
    Unk3       = 1 << 10 # common
    Unk4       = 1 << 11 # common
    Unk5       = 1 << 12 # common


class Entry:
    def __init__ (self):
        self.unk1       = None
        self.offset     = None
        self.compSize   = None
        self.decompSize = None
        self.flags      = None
        self.unk3       = None


def unpack (filePath):
    filePath = getAbsPath(filePath)

    if not isFile(filePath):
        raise Exception(f'File does not exist: { filePath }')

    if not getFileSize(filePath):
        return

    with openFile(filePath) as f:
        signature = f.read(4)

        if signature != PAK_SIGNATURE:
            raise Exception(f'Unknown signature: { filePath }')

        version = f.u32()  # ???

        assert version == 4, version

        entryCount = f.u32()
        unk2       = f.u32()

        print(unk2)

        entries = [ Entry() for _ in range(entryCount) ]

        for entry in entries:
            entry.unk1       = f.u64()  # id?
            entry.offset     = f.u64()
            entry.compSize   = f.u64()
            entry.decompSize = f.u64()
            entry.flags      = f.u64()
            entry.unk3       = f.u64()

            pji(entry)

        return

        for entry in entries:
            f.seek(entry.offset)

            data = f.read(entry.compSize)

            if data.startswith(bytes.fromhex('28 B5 2F FD')):
                pass 
                # [2, 1026, 2050, 3074, 4098, 5122, 6146]
                # print(entry.flags)
                # data = ZSTD_uncompress(data)
                # assert len(data) == entry.decompSize
            else:
                if entry.compSize != entry.decompSize:
                    assert (entry.flags & 1)
                else:
                    print(formatHex(data[:4]), entry.flags)
                    assert not (entry.flags & 1)
                # assert entry.compSize == entry.decompSize, (entry.flags, entry.offset, entry.compSize, entry.decompSize)
                # [0, 1, 256, 1024, 1025, 1280, 2048, 2049, 3072, 3073, 4096, 4097, 5121, 6145]
                # _s.add(entry.flags)



    

def unpackAll (gameDir):
    if not isDir(gameDir):
        raise Exception(f'Game directory does not exist: { gameDir }')

    for filePath in iterFiles(gameDir, True, [ PAK_EXT ]):
        print(filePath)

        unpack(filePath)

        print(' ')


def main ():
    unpackAll(GAME_DIR)



if __name__ == '__main__':
    main()
