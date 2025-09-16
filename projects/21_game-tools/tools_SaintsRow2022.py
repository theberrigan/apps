# Saints Row 2022 Tools

import sys

sys.path.insert(0, r'C:\Projects\PythonLib\python\v001')

from bfw.utils import *
from bfw.reader import *
from bfw.types.enums import Enum

import lz4.frame



GAME_DIR = r'G:\Steam\steamapps\common\Saints Row'

VPP_SIGNATURE = b'\xCE\x0A\x89\x51'


class VPPEntry:
    def __init__ (self):
        self.nameOffset   = None
        self._unk4        = None
        self.dataOffset   = None
        self.decompSize   = None
        self.compSize     = None
        self.flags        = None
        self.alignment    = None
        self._unk8        = None
        # ----------------------
        self.isCompressed = None
        self.path         = None




def unpackVPP (filePath, unpackDir=None):    
    filePath = getAbsPath(filePath)

    if not isFile(filePath):
        raise Exception(f'File is not found: { filePath }')

    if not unpackDir:
        unpackDir = filePath + '.unpacked'

    with openFile(filePath) as f:
        signature = f.read(4)

        if signature != VPP_SIGNATURE:
            raise Exception('Unknown signature')

        version = f.u32()

        if version != 17:
            raise Exception('Unsupported VPP version')

        headerHash = f.u32()  # Volition's custom CRC32

        # header is 108 bytes
        flags       = f.u32()
        entryCount  = f.u32()
        _unk1       = f.u32()
        entriesSize = f.u32()
        namesSize   = f.u32()
        fileSize    = f.u64()
        decompSize  = f.u64()
        compSize    = f.u64()
        timestamp   = f.u64()
        dataStart   = f.u32()

        assert fileSize == f.getSize()

        _pad = f.read(52)

        assert _pad == (b'\x00' * len(_pad))

        entriesStart = f.tell()
        namesStart   = entriesStart + entriesSize

        isCompressed = bool(flags & 1)
        isCondensed  = bool(flags & 2)
        compMethod   = (flags >> 11) & 15  # 10 is LZ4

        assert not isCompressed or compMethod == 10
        assert not isCondensed

        # print(_unk1, dataStart)

        # ----------------------

        f.seek(entriesStart)

        entries = [ VPPEntry() for _ in range(entryCount) ]

        for entry in entries:
            entry.nameOffset   = f.u64()
            entry._unk4        = f.u64()
            entry.dataOffset   = f.u64()
            entry.decompSize   = f.u64()
            entry.compSize     = f.u64()
            entry.flags        = f.u16()
            entry.alignment    = f.u16()
            entry._unk8        = f.u32()
            entry.isCompressed = bool(entry.flags & 1)

            # pji(entry)

        # ----------------------

        for entry in entries:
            f.seek(namesStart + entry.nameOffset)

            entry.path = f.string()

        # ----------------------

        for entry in entries:
            if entry.compSize in [  ]:
                continue

            if getExt(entry.path) not in [ '.wem', '.wem_pad', '.bnk_pad', '.bnk' ]:
                continue

            print(entry.path, entry.compSize, entry.decompSize)

            f.seek(dataStart + entry.dataOffset)

            if entry.isCompressed:
                data = f.read(entry.compSize)
                data = lz4.frame.decompress(data)

                assert len(data) == entry.decompSize
            else:
                data = f.read(entry.decompSize)


            destPath = getAbsPath(joinPath(r'D:\.dev\VolitionGames\_SR2022Unpacked', entry.path))

            print(destPath)
            print('')

            # createFileDirs(destPath)

            # writeBin(destPath, data)

            


        


def unpackVPPs ():
    for filePath in iterFiles(GAME_DIR, True, [ '.vpp_pc' ]):
        print(filePath)

        unpackVPP(filePath)

        print(' ')



def main ():    
    unpackVPPs()
    # unpackVPP(joinPath(GAME_DIR, 'sr5', 'data', 'sr_boot', 'sr_boot.vpp_pc'))



if __name__ == '__main__':
    main()
