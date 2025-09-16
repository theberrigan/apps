# Visceral Engine Tools

import re
import sys

sys.path.insert(0, r'C:\Projects\PythonLib\python\v001')

from bfw.utils import *
from bfw.reader import *
from bfw.types.enums import Enum2



GAMES_DIR = r'D:\.dev\VisceralGames'

JB_DIR  = joinPath(GAMES_DIR, '1. James Bond 007 From Russia with Love (PS2)')  # v1 | pack only
G1_DIR  = joinPath(GAMES_DIR, '2. The Godfather The Game (PS2)')                # v2 | pack only
SG_DIR  = joinPath(GAMES_DIR, '3. The Simpsons Game (PS3)')                     # -- | files only, no toc, audio with ".mus" extension
DS1_DIR = joinPath(GAMES_DIR, '4. Dead Space')                                  # -- | files only, some tocs (28 7B BA 9C), audio with ".exa.snu" (03...)
G2_DIR  = joinPath(GAMES_DIR, '5. The Godfather II')                            # v1 | packs with audio only, some tocs (28 7B BA 9C), audio with ".exa.snu" (03...) 
DI_DIR  = joinPath(GAMES_DIR, '6. Dante\'s Inferno (PS3)')                      # v3 | pack only
DS2_DIR = joinPath(GAMES_DIR, '7. Dead Space 2')                                # v3 | pack only
DS3_DIR = joinPath(GAMES_DIR, '8. Dead Space 3')                                # v3 | pack only



class HeaderV1:
    def __init__ (self):
        self.fileSize    = None
        self.entryCount  = None
        self.metaSize    = None
        self.isHashNames = None


class EntryV1:
    def __init__ (self):
        self.offset = None
        self.size   = None
        self.path   = None


def isCRCString (name):
    return bool(re.match(r'^[\da-f]{8}$', name, flags=re.I))


def unpackV1 (filePath):    
    filePath = getAbsPath(filePath)

    if not isFile(filePath):
        raise Exception(f'File is not found: { filePath }')

    with openFile(filePath) as f:
        signature = f.read(4)

        if signature != b'BIGF':
            raise Exception('Unknown signature')

        header = HeaderV1()

        f.setByteOrder(ByteOrder.Little)

        header.fileSize = f.u32()  # total file size

        assert f.getSize() == header.fileSize

        f.setByteOrder(ByteOrder.Big)

        header.entryCount = f.u32()
        header.metaSize   = f.u32()  # from start of the file

        entries = [ EntryV1() for _ in range(header.entryCount) ]

        isHashNames = True

        for entry in entries:
            entry.offset = f.u32()
            entry.size   = f.u32()
            entry.path   = f.string()

            if isHashNames and not isCRCString(entry.path):
                isHashNames = False

        header.isHashNames = isHashNames

        for entry in entries:
            f.seek(entry.offset)

            signature = f.read(4)

            if signature == b'coTS':
                f.setByteOrder(ByteOrder.Little)

                unk1 = f.u32()  # hash count?
                unk2 = f.u32()
                unk3 = f.u32()  # total hash size?
                unk4 = f.u32()

                assert unk1 in [ 5 ], unk1
                assert unk2 in [ 0, 1, 2, 3, 4 ], unk2
                assert unk3 in [ 20 ], unk3

                print(entry.offset, entry.size, unk2, unk4)

                for i in range(unk1):
                    unk5 = f.u32()

                    print(f'\t{unk5:08X}')

                unk6 = f.u32()
                unk7 = f.u32()

                print(unk6, unk7)

                unk8  = f.u32()
                unk9  = f.u32()
                unk10 = f.u32()

                assert unk9 in [ 0, 1 ]

                assert unk8 == 0xFFFFFFFF, f'{unk8:08X}'

                print(unk9, unk10)

                for i in range(5):
                    unk11 = f.u32()

                    print(f'\t{unk11:08X}')

                unk12 = f.u32()
                unk13 = f.u32()

                print(unk12, unk13)

                print('-' * 50)



class HeaderV2:
    def __init__ (self):
        self.fileSize   = None
        self.entryCount = None
        self.metaSize   = None


class EntryV2:
    def __init__ (self):
        self.offset = None
        self.size   = None
        self.id     = None


def unpackV2 (filePath):    
    filePath = getAbsPath(filePath)

    if not isFile(filePath):
        raise Exception(f'File is not found: { filePath }')

    with openFile(filePath) as f:
        signature = f.read(4)

        if signature != b'\xc2IGH':
            raise Exception('Unknown signature')

        header = HeaderV2()

        f.setByteOrder(ByteOrder.Little)

        header.fileSize   = f.u32()  # total file size
        header.entryCount = f.u32()
        header.metaSize   = f.u32()  # from start of the file

        assert f.getSize() == header.fileSize

        entries = [ EntryV2() for _ in range(header.entryCount) ]

        for entry in entries:
            entry.offset = f.u32()
            entry.size   = f.u32()
            entry.id     = f.u32()


class HeaderV3:
    def __init__ (self):
        self.fileSize   = None
        self.entryCount = None
        self.metaSize   = None
        self.unkOffset  = None
        self.unkSize    = None


class EntryV3:
    def __init__ (self):
        self.id     = None
        self.offset = None
        self.size   = None


# Index and payloads are aligned by 2048
def unpackV3 (filePath):    
    filePath = getAbsPath(filePath)

    if not isFile(filePath):
        raise Exception(f'File is not found: { filePath }')

    with openFile(filePath) as f:
        signature = f.read(4)

        if signature != b'BIGH':
            raise Exception('Unknown signature')

        header = HeaderV3()

        f.setByteOrder(ByteOrder.Little)

        header.fileSize = f.u32()  # total file size

        assert f.getSize() == header.fileSize

        f.setByteOrder(ByteOrder.Big)

        header.entryCount = f.u32() - 1  # ignore last entry (entry.offset == 0x4C323833 and entry.size == 0x15050000)
        header.metaSize   = f.u32()      # from start of the file
        header.unkOffset  = f.u32()      # some special entry offset
        header.unkSize    = f.u32()      # some special entry size

        assert header.entryCount >= 0

        entries = [ EntryV3() for _ in range(header.entryCount) ]

        for entry in entries:
            entry.id     = f.u32()
            entry.offset = f.u32()
            entry.size   = f.u32()


def unpackAll (gameDir):
    for filePath in iterFiles(gameDir, True):  # [ '.rus', '.viv', '.dat' ]
        match readBin(filePath, 4):
            case b'BIGF':
                # continue
                print(filePath)
                unpackV1(filePath)
                print(' ')
            case b'\xc2IGH':
                continue
                print(filePath)
                unpackV2(filePath)
                print(' ')
            case b'BIGH':
                continue
                print(filePath)
                unpackV3(filePath)
                print(' ')


def main ():
    for gameDir in [
        # GAMES_DIR,
        JB_DIR,
        # G1_DIR,
        # SG_DIR,
        # DS1_DIR,
        # G2_DIR,
        # DI_DIR,
        # DS2_DIR,
        # DS3_DIR,
    ]:
        unpackAll(gameDir)



if __name__ == '__main__':
    main()

r'''
1. James Bond 007 From Russia with Love (PS2) | v1 | BIGF    | PS2 | coTS (.str) | ???               | SCHl | MPCh |      | 
2. The Godfather The Game (PS2)               | v2 | \xc2IGH | PS2 | coTS (.str) | ???               | SCHl | MPCh |      | 
3. The Simpsons Game (PS3)                    | -- | ----    | PS3 | SToc (.str) | ???               |      |      |      | 
4. Dead Space                                 | -- | ----    | PC  | 3slo (.str) | ({\xba\x9c (.toc) |      |      |      | 
5. The Godfather II                           | v1 | BIGF    | PC  | 3slo (.str) | ({\xba\x9c (.toc) |      |      |      | 
6. Dante's Inferno (PS3)                      | v3 | BIGH    | PS3 | ols3 (.str) | \x9c\xba{( (.toc) | SCHl |      | MVhd | 
7. Dead Space 2                               | v3 | BIGH    | PC  | 3slo (.str) | ({\xba\x9c (.toc) |      |      |      | 
8. Dead Space 3                               | v3 | BIGH    | PC  | 3slo (.str) | ({\xba\x9c (.toc) | SCHl |      | MVhd | 

1. James Bond 007 From Russia with Love (PS2) (v1)

    packs:
    b'SCHl' 4303
    b'coTS' 1392
    b'MPCh' 7
    b'\x00\x00\x01\x00' 6
    b'\x10\x00\x00\x00' 4
    b'-mai' 2
    b'fron' 2
    b'\x15\x11\x91\t' 2
    b"\x00't\xb5" 2
    b'\xde\xab4\x11' 2
    b'\x95p0:' 2
    b'\xe2\x89\xf5b' 2
    b'\xf8\xc3N\xbc' 2
    b'3\xcc(\xbd' 2
    b't\xc5o#' 2
    b':@\xf8\xbb' 2
    b'\x08[\x8c\xf3' 2
    b'.\xea\xe9e' 2
    b'\xf1\xba\xba\x82' 2
    b'\xd5\xb8r!' 2
    b'\xe8\xd6\x85/' 2
    b'1\nen' 2

2. The Godfather The Game (PS2) (v2)

    packs:
    b'SCHl' 6375
    b'coTS' 4514
    b'FMVS' 30
    b'MPCh' 4
    b'\x00\x00\x01\x00' 3
    b'FORM' 1
    b'\x8f\x97\xacG' 1
    b'2\nBA' 1

3. The Simpsons Game (PS3) (--)

    files:
    {'.mus', '.str', '.snu'}
    b'\x01\x00\x00\x00' 6326 ['.snu']
    b'\x01\x0c\x00\x00' 1083 ['.snu']
    b'\x01\x04\x00\x00' 3 ['.snu']
    b'\x01\x08\x00\x00' 1 ['.snu']
    b'SToc' 490 ['.str']
    b'\xe5\x92X\xac' 1 ['.mus']
    b'c\xa9:"' 1 ['.mus']
    b'\x97\xe5\xab2' 1 ['.mus']
    b'\x01m!\xff' 1 ['.mus']
    b'\x17\r\xcd\xc9' 1 ['.mus']
    b'M|\x95\\' 1 ['.mus']
    b'\xd2A\xc2\r' 1 ['.mus']
    b'\x8eQ6&' 1 ['.mus']
    b"d\xa1'\x95" 1 ['.mus']
    b'\x8f\x94Xa' 1 ['.mus']
    b'\xcb\x80\xf3k' 1 ['.mus']
    b'\x95\n4\x97' 1 ['.mus']
    b'}R\xaf\x90' 1 ['.mus']
    b'\xc5K\xdeO' 1 ['.mus']
    b'AM&]' 1 ['.mus']
    b'\xe6\xac&Q' 1 ['.mus']
    b'\x92\xf2\x9d\xbe' 1 ['.mus']

4. Dead Space (--)

    files:
    {'.snu', '.toc', '.str'}
    b'\x03\x00\x00\x01' 1315 ['.snu']
    b'\x03\x00\x00\x02' 1036 ['.snu']
    b'3slo' 787 ['.str']
    b'\x03\x00\x00\x04' 457 ['.snu']
    b'\x01\x00\x00\x00' 98 ['.snu']
    b'({\xba\x9c' 51 ['.toc']
    b'\x03\x00\x00\x08' 36 ['.snu']
    b'\x02\x00\x00\x02' 7 ['.snu']
    b'\x02\x00\x00\x04' 6 ['.snu']
    b'\x02\x00\x00\x08' 2 ['.snu']
    b'\x03\x00\x00\x06' 1 ['.snu']

5. The Godfather II (v1)

    files:
    {'.str', '.toc'}
    b'3slo' 2304 ['.str']
    b'({\xba\x9c' 25 ['.toc']

    packs:
    {'.snu'}
    b'\x03\x00\x00\x01' 19459 ['.snu']
    b'\x03\x0c\x00\x01' 1586 ['.snu']
    b'\x03\x04\x00\x01' 1578 ['.snu']
    b'\x03\x08\x00\x01' 1573 ['.snu']
    b'\x03\x00\x00\x02' 199 ['.snu']
    b'\x03\x00\x00\x04' 155 ['.snu']
    b'\x03\x08\x00\x04' 114 ['.snu']
    b'\x03\x04\x00\x04' 100 ['.snu']
    b'\x03\x0c\x00\x04' 92 ['.snu']
    b'\x03\x00\x00\x06' 30 ['.snu']
    b'\x03\x04\x00\x06' 12 ['.snu']
    b'\x03\x04\x00\x02' 4 ['.snu']
    b'\x03\x08\x00\x02' 3 ['.snu']
    b'\x03\x08\x00\x06' 3 ['.snu']
    b'\x01\x00\x00\x00' 2 ['.snu']
    b'\x03\x0c\x00\x02' 2 ['.snu']
    b'\x03\x0c\x00\x06' 1 ['.snu']

6. Dante's Inferno (PS3) (v3)

    packs:
    b'\x03\x00\x00\x01' 1865
    b'\x03\x0c\x00\x01' 1714
    b'ols3' 1181
    b'\x03\x0c\x00\x02' 419
    b'\x03\x00\x00\x02' 329
    b'\x03\x00\x00\x06' 107
    b'\x03\x00\x00\x04' 101
    b'\x03\x0c\x00\x04' 61
    b'MVhd' 58
    b'\x03\x04\x00\x04' 15
    b'\x9c\xba{(' 13
    b'\x03\x08\x00\x04' 13
    b'--Ab' 2
    b'SCHl' 1
    b'\r\nfu' 1
    b'\r\n--' 1
    b'func' 1
    b'10\nB' 1
    b'-- D' 1
    b'\x01\x00\x00\x00' 1

7. Dead Space 2 (v3)

    packs:
    b'3slo' 1311
    b'\x03\x00\x00\x04' 647
    b'\x03\x00\x00\x02' 474
    b'\x03\x00\x00\x01' 200
    b'({\xba\x9c' 175
    b'\x01\x00\x00\x00' 71
    b'\x03\x00\x00\x06' 52
    b'\x03\x00\x00\x08' 49
    b'\x03\x04\x00\x04' 14
    b'\x03\x0c\x00\x04' 8
    b'\x03\x08\x00\x04' 7
    b'-- P' 3
    b'-- (' 3
    b'ch01' 3
    b'\x02\x00\x00\x02' 2
    b'\x03\x0c\x00\x01' 1
    b'11\nE' 1
    b'\x02\x00\x00\x08' 1
    b'\x02\x00\x00\x04' 1

8. Dead Space 3 (v3)

    packs:
    b'\x03\x00\x00\x01' 2139
    b'3slo' 1983
    b'\x03\x00\x00\x02' 784
    b'\x03\x00\x00\x04' 366
    b'\x03\x00\x00\x06' 152
    b'({\xba\x9c' 114
    b'\x03\x00\x00\x08' 55
    b'MVhd' 25
    b'\x03\x08\x00\x04' 5
    b'\x03\n\x00\x04' 5
    b'\x03\x0c\x00\x04' 3
    b'\x03\x02\x00\x04' 3
    b'\x03\x06\x00\x04' 3
    b'\x03\x0e\x00\x04' 3
    b'SCHl' 2
    b'\x01\x00\x00\x00' 1
    b'\x03\x08\x00\x01' 1
    b'\x03\x04\x00\x04' 1
    b'/MAP' 1
    b'12\nn' 1
    b'map_' 1
    b'2\ngl' 1
    b'2 //' 1
    b'1\t//' 1
    b'LCH2' 1
    b'1 //' 1
'''