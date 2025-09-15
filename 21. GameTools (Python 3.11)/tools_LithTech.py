# LithTech Engine Tools
# Developer: Monolith Productions
# Games: FEAR, Condemned, etc.
# https://en.wikipedia.org/wiki/Monolith_Productions
# https://en.wikipedia.org/wiki/LithTech

import re
import sys

from operator import attrgetter

sys.path.insert(0, r'C:\Projects\PythonLib\python\v001')

from bfw.utils import *
from bfw.reader import *
from bfw.types.enums import Enum2



CCO_GAME_DIR   = r'G:\Steam\steamapps\common\Condemned Criminal Origins'
FEAR_GAME_DIR  = r'G:\Steam\steamapps\common\FEAR Ultimate Shooter Edition'
FEAR2_GAME_DIR = r'G:\Games\F.E.A.R. 2 - Project Origin'
W2_GAME_DIR    = r'G:\Games\Wolfschanze2'
C2_GAME_DIR    = r'G:\Games\Condemned2'  # Big endian
BS_GAME_DIR    = r'G:\Games\Battlestrike'
COH3_GAME_DIR  = r'G:\Games\COH3'  # Code of Honor 3

GAME_DIRS = [
    CCO_GAME_DIR,
    FEAR_GAME_DIR,
    FEAR2_GAME_DIR,
    W2_GAME_DIR,
    C2_GAME_DIR,
    BS_GAME_DIR,
    COH3_GAME_DIR,
]

ARCH_EXTS = [
    '.Arch00',  # FEAR, CCO  - 2005      - Arch00 +
    '.Arch01',  # FEAR2, GCI - 2009-2012 - Arch01
    '.Arch02',  # C2BS       - 2008      - Arch02 (same as Arch00 but BE) + 
    '.Arch03',  # ???
    '.Arch04',  # GoME       - 2012      - Arch04
    '.Arch05',  # MESoM      - 2014      - Arch05
    '.Arch06',  # MESoW      - 2017      - Arch06
    '.Arch07',
    '.Arch08',
    '.Arch09',
]

ARCH_SIGNATURE_LE = b'LTAR'
ARCH_SIGNATURE_BE = b'RATL'  # See Condemned 2 PS3

ARCH_CRC_REGEX = re.compile(r'^crc[\\/]+[\da-f]{32}\.crc$', flags=re.I)



class ArchV3Header:
    def __init__ (self):
        self.version     = None
        self.namesSize   = None
        self.dirCount    = None
        self.fileCount   = None
        self.unk5        = None
        self.unk6        = None
        self.unk7        = None
        self.crc1        = None
        self.crc2        = None
        # ---------------------
        self.namesOffset = None


class ArchV3Entry:
    def __init__ (self):
        self.path         = None
        self.offset       = None
        self.compSize     = None
        self.decompSize   = None
        self.compLevel    = None
        # ----------------------
        self.crc          = None
        self.isPresent    = None
        self.isCompressed = None
        self.isCRC        = None


class ArchV3:
    @classmethod
    def fromFile (cls, filePath):
        filePath = getAbsPath(filePath)

        if not isFile(filePath):
            raise Exception(f'File does not exist: { filePath }')

        return cls(filePath).read()

    def __init__ (self, filePath):
        self.filePath = filePath
        self.header   = None
        self.entries  = None

    def read (self):
        with openFile(self.filePath) as f:
            self.header  = self.readHeader(f)
            self.entries = self.readEntries(f, self.header)

        return self

    def readHeader (self, f):
        header = ArchV3Header()

        signature = f.read(4)

        if signature == ARCH_SIGNATURE_BE:
            f.setByteOrder(ByteOrder.Big)
        elif signature != ARCH_SIGNATURE_LE:
            raise Exception(f'Unknown signature: { signature }')

        header.version = f.u32()

        assert header.version == 3

        header.namesSize = f.u32()
        header.dirCount  = f.u32()  # dir count
        header.fileCount = f.u32()  # file count
        header.unk5      = f.u32()  # 0 or 1
        header.unk6      = f.u32()  # 0
        header.unk7      = f.u32()  # 0 or 1

        assert header.unk5 in [ 0, 1 ], header.unk5
        assert header.unk6 in [ 0    ], header.unk6
        assert header.unk7 in [ 0, 1 ], header.unk7

        header.crc1 = f.read(8).hex()
        header.crc2 = f.read(8).hex()  # == second part of "<hex>.crc" file name

        header.namesOffset = f.tell()

        return header

    def readNames (self, f, header):
        namesEnd = header.namesOffset + header.namesSize
        names    = {}

        while f.tell() < namesEnd:
            offset = f.tell() - header.namesOffset
            name   = f.alignedString(4, encoding='cp1252')

            names[offset] = name

        assert namesEnd == f.tell()

        return names

    def readFiles (self, f, header, names):
        entries = [ ArchV3Entry() for _ in range(header.fileCount) ]

        for entry in entries:
            nameOffset         = f.u32()
            entry.path         = names[nameOffset]
            entry.offset       = f.u64()
            entry.compSize     = f.u64()  # or 0
            entry.decompSize   = f.u64()  # or very big number
            entry.compLevel    = f.u32()  # flags or compression type; 0 - not compressed, 9 (0b1001) - compressed
            entry.isPresent    = bool(entry.offset and entry.compSize)
            entry.isCompressed = entry.compLevel > 0
            entry.isCRC        = False

            assert 0 <= entry.compLevel <= 9, entry.compLevel

        return entries

    def readDirs (self, f, header, names, entries):
        entryCursor = 0

        for i in range(header.dirCount):
            dirNameOffset  = f.u32()
            _dirStartIndex = f.u32()  # or 0xFFFFFFFF
            _dirEndIndex   = f.u32()  # or 0xFFFFFFFF
            dirFileCount   = f.u32()

            dirName = names[dirNameOffset]

            for j in range(dirFileCount):
                entry = entries[entryCursor]

                entry.path  = joinPath(dirName, entry.path)
                entry.isCRC = bool(re.match(ARCH_CRC_REGEX, entry.path))

                # 2fc2466d cb9348e4 bc2d72ca c8e6d163 .crc
                # 6d46c22f 93cbe448 bc2d72ca c8e6d163
                # pji(header)
                # pji(entry)

                entryCursor += 1

        entries = sorted(entries, key=attrgetter('offset'))

        return entries

    def readEntryData (self, f, entry):
        if not entry.isPresent:
            return b''

        f.seek(entry.offset)

        if not entry.isCompressed:
            data = f.read(entry.compSize)

            assert len(data) == entry.decompSize

            return data

        assetEnd = entry.offset + entry.compSize

        data = bytearray(entry.decompSize)
        dataCursor = 0

        while dataCursor < entry.decompSize:
            blockCompSize     = f.u32()
            blockDecompSize   = f.u32()
            isBlockCompressed = blockCompSize != blockDecompSize

            blockData = f.read(align(blockCompSize, 4))
            blockData = blockData[:blockCompSize]

            if isBlockCompressed:
                try:
                    blockData = decompressData(blockData)
                except Exception as e:
                    blockData = None

                if blockData is None:
                    raise Exception('Failed to decompress data block')

            assert len(blockData) == blockDecompSize, (f.tell() - blockCompSize)

            data[dataCursor:dataCursor + blockDecompSize] = blockData
            dataCursor += blockDecompSize

        data = bytes(data)

        assert dataCursor == entry.decompSize, (dataCursor, entry.decompSize)
        assert f.tell() == assetEnd, (f.tell(), assetEnd)

        return data

    def getCRCEntry (self, entries):
        for entry in entries:
            if entry.isCRC:
                return entry

        return None

    def pathToKey (self, entryPath):
        assert entryPath

        entryPath = entryPath.lower()
        entryPath = re.sub(r'[\\/]+', '/', entryPath)
        entryPath = entryPath.lstrip('/')

        return entryPath

    def readCRCs (self, f, entries):
        crcEntry = self.getCRCEntry(entries)

        if crcEntry is None:
            return entries

        entryMap = { self.pathToKey(e.path): e for e in entries }

        crcData = self.readEntryData(f, crcEntry)

        with MemReader(crcData, byteOrder=f.byteOrder) as f:
            crcCount = f.u32()
            _unk1    = f.u32()  # smth similar to crcEntry.decompSize

            for i in range(crcCount):
                pathSize = f.u16()
                filePath = f.string(pathSize, encoding='cp1252')
                filePath = self.pathToKey(filePath)

                entryMap[filePath].crc = f.u32()

        return entries

    def readEntries (self, f, header):
        names   = self.readNames(f, header)
        entries = self.readFiles(f, header, names)
        entries = self.readDirs(f, header, names, entries)
        entries = self.readCRCs(f, entries)

        for e in entries:
            pjp(e)

        return entries






# TODO:
# - CRCs
# - Check integrity of decompressed assets
def unpack (filePath, unpackDir):    
    filePath = getAbsPath(filePath)

    if not isFile(filePath):
        raise Exception(f'File is not found: { filePath }')

    archName = getBaseName(filePath)
    destDir  = joinPath(unpackDir, archName)

    with openFile(filePath) as f:
        signature = f.read(4)

        if signature == ARCH_SIGNATURE_BE:
            f.setByteOrder(ByteOrder.Big)
        elif signature != ARCH_SIGNATURE_LE:
            raise Exception(f'Incorrect signature: { signature }')

        version = f.u32()

        assert version == 3

        namesSize = f.u32()
        dirCount  = f.u32()  # dir count
        fileCount = f.u32()  # file count
        unk5      = f.u32()  # 0 or 1
        unk6      = f.u32()  # 0
        unk7      = f.u32()  # 0 or 1

        assert unk5 in [ 0, 1 ], unk5
        assert unk6 in [ 0    ], unk6
        assert unk7 in [ 0, 1 ], unk7

        crc1 = f.read(8)
        crc2 = f.read(8)  # == second part of "<hex>.crc" file name

        namesOffset = f.tell()
        namesEnd    = namesOffset + namesSize
        names       = {}

        while f.tell() < namesEnd:
            nameOffset = f.tell() - namesOffset
            name       = f.alignedString(4, encoding='cp1252')

            names[nameOffset] = name

        assert namesEnd == f.tell()

        assets = [ None ] * fileCount

        for i in range(fileCount):
            nameOffset = f.u32()
            offset     = f.u64()
            compSize   = f.u64()  # or 0
            decompSize = f.u64()  # or very big number
            compType   = f.u32()  # flags or compression type; 0 - not compressed, 9 (0b1001) - compressed

            assets[i] = {
                'path':       names[nameOffset],
                'offset':     offset,
                'compSize':   compSize,
                'decompSize': decompSize,
                'compType':   compType
            }

            assert compType in [ 0, 9 ], compType

        assetCursor = 0

        for i in range(dirCount):
            dirNameOffset = f.u32()
            dirStartIndex = f.u32()  # or 0xFFFFFFFF
            dirEndIndex   = f.u32()  # or 0xFFFFFFFF
            dirFileCount  = f.u32()

            dirName = names[dirNameOffset]

            for j in range(dirFileCount):
                asset = assets[assetCursor]

                asset['path'] = joinPath(dirName, asset['path'])

                assetCursor += 1

        assets = sorted(assets, key=lambda item: item['offset'])

        for asset in assets:
            path         = asset['path']
            offset       = asset['offset']
            compSize     = asset['compSize']
            decompSize   = asset['decompSize']
            compType     = asset['compType']
            isPresent    = bool(offset and compSize)
            isCompressed = compType == 9  # TODO: check compType instead

            data = b''

            if isPresent:
                f.seek(offset)

                if isCompressed:
                    assetEnd = offset + compSize

                    data = bytearray(decompSize)
                    dataCursor = 0

                    while dataCursor < decompSize:
                        blockCompSize     = f.u32()
                        blockDecompSize   = f.u32()
                        isBlockCompressed = blockCompSize != blockDecompSize

                        blockData = f.read(align(blockCompSize, 4))
                        blockData = blockData[:blockCompSize]

                        if isBlockCompressed:
                            try:
                                blockData = decompressData(blockData)
                            except Exception as e:
                                blockData = None

                            if blockData is None:
                                raise Exception('Failed to decompress data block with ZLIB')

                        assert len(blockData) == blockDecompSize, (f.tell() - blockCompSize)

                        data[dataCursor:dataCursor + blockDecompSize] = blockData
                        dataCursor += blockDecompSize

                    data = bytes(data)

                    assert dataCursor == decompSize, (dataCursor, decompSize)
                    assert f.tell() == assetEnd, (f.tell(), assetEnd)
                else:
                    data = f.read(compSize)

                assert len(data) == decompSize

            destPath = joinPath(destDir, path)

            # print('-->', destPath)

            if 0:
                assert len(data) == compSize

                createFileDirs(destPath)

                writeBin(destPath, data)

        # print(toJson(assets))

    # sys.exit()

def unpackAll (gameDir, unpackDir):
    if not isDir(gameDir):
        print(f'Game directory does not exist: { gameDir }')

    for filePath in iterFiles(gameDir, True, ARCH_EXTS):
        print(filePath)

        try:
            # unpack(filePath, unpackDir)
            ArchV3.fromFile(filePath)
        except Exception as e:
            print('ERROR:', e)

        print(' ')

def main ():
    # for gameDir in GAME_DIRS:
    for gameDir in [ FEAR_GAME_DIR ]:
    # for gameDir in [ FEAR2_GAME_DIR ]:
    # for gameDir in [ C2_GAME_DIR ]:
        unpackAll(gameDir, joinPath(gameDir, '.unpacked'))

    # unpack(joinPath(CCO_GAME_DIR, 'Game', 'CondemnedA.Arch00'), joinPath(CCO_GAME_DIR, '.unpacked'))
    # unpack(joinPath(CCO_GAME_DIR, 'Game', 'CondemnedL.Arch00'), joinPath(CCO_GAME_DIR, '.unpacked'))


if __name__ == '__main__':
    main()

r'''
G:\Steam\steamapps\common\FEAR Ultimate Shooter Edition\FEAR.Arch00
{"version":3,"namesSize":216136,"dirCount":247,"fileCount":10571,"unk5":1,"unk6":0,"unk7":1,"crc1":"2daf797d03c5d34f","crc2":"a20fb7382f053fa1","namesOffset":48}
{"path":"CRC\\7d79af2dc5034fd3a20fb7382f053fa1.crc","offset":3846517938,"compSize":442727,"decompSize":442727,"compLevel":0,"isPresent":true,"isCompressed":false,"isCRC":true}
 
G:\Steam\steamapps\common\FEAR Ultimate Shooter Edition\FEARA.Arch00
{"version":3,"namesSize":20648,"dirCount":12,"fileCount":1044,"unk5":1,"unk6":0,"unk7":1,"crc1":"252da553bf234b4f","crc2":"a95af64c2998ca78","namesOffset":48}
{"path":"CRC\\53a52d2523bf4f4ba95af64c2998ca78.crc","offset":945217216,"compSize":35485,"decompSize":35485,"compLevel":0,"isPresent":true,"isCompressed":false,"isCRC":true}
 
G:\Steam\steamapps\common\FEAR Ultimate Shooter Edition\FEARA_1.Arch00
{"version":3,"namesSize":48,"dirCount":2,"fileCount":1,"unk5":1,"unk6":0,"unk7":1,"crc1":"92e3701616a80647","crc2":"8312ca160d3b3978","namesOffset":48}
{"path":"CRC\\1670e392a81647068312ca160d3b3978.crc","offset":160,"compSize":54,"decompSize":54,"compLevel":0,"isPresent":true,"isCompressed":false,"isCRC":true}
 
G:\Steam\steamapps\common\FEAR Ultimate Shooter Edition\FEARA_2.Arch00
{"version":3,"namesSize":460,"dirCount":4,"fileCount":20,"unk5":0,"unk6":0,"unk7":1,"crc1":"50c3ab9a40cd674b","crc2":"aec5bc1ac968bab9","namesOffset":48}
{"path":"CRC\\9aabc350cd404b67aec5bc1ac968bab9.crc","offset":18955998,"compSize":673,"decompSize":673,"compLevel":0,"isPresent":true,"isCompressed":false,"isCRC":true}
 
G:\Steam\steamapps\common\FEAR Ultimate Shooter Edition\FEARA_3.Arch00
{"version":3,"namesSize":232,"dirCount":4,"fileCount":12,"unk5":1,"unk6":0,"unk7":1,"crc1":"db0d56e561839940","crc2":"a1fa69131cbfc567","namesOffset":48}
{"path":"CRC\\e5560ddb83614099a1fa69131cbfc567.crc","offset":14145212,"compSize":366,"decompSize":366,"compLevel":0,"isPresent":true,"isCompressed":false,"isCRC":true}
 
G:\Steam\steamapps\common\FEAR Ultimate Shooter Edition\FEARA_4.Arch00
{"version":3,"namesSize":48,"dirCount":2,"fileCount":1,"unk5":1,"unk6":0,"unk7":1,"crc1":"57af812db53d0b4b","crc2":"aae1af8cd6dedc75","namesOffset":48}
{"path":"CRC\\2d81af573db54b0baae1af8cd6dedc75.crc","offset":160,"compSize":54,"decompSize":54,"compLevel":0,"isPresent":true,"isCompressed":false,"isCRC":true}
 
G:\Steam\steamapps\common\FEAR Ultimate Shooter Edition\FEARA_5.Arch00
{"version":3,"namesSize":48,"dirCount":2,"fileCount":1,"unk5":1,"unk6":0,"unk7":1,"crc1":"29365fb38e2f1e4a","crc2":"891fcd608ef82563","namesOffset":48}
{"path":"CRC\\b35f36292f8e4a1e891fcd608ef82563.crc","offset":160,"compSize":54,"decompSize":54,"compLevel":0,"isPresent":true,"isCompressed":false,"isCRC":true}
 
G:\Steam\steamapps\common\FEAR Ultimate Shooter Edition\FEARA_6.Arch00
{"version":3,"namesSize":48,"dirCount":2,"fileCount":1,"unk5":1,"unk6":0,"unk7":1,"crc1":"05bb8b9a9cd3a746","crc2":"a03593ee8599a053","namesOffset":48}
{"path":"CRC\\9a8bbb05d39c46a7a03593ee8599a053.crc","offset":160,"compSize":54,"decompSize":54,"compLevel":0,"isPresent":true,"isCompressed":false,"isCRC":true}
 
G:\Steam\steamapps\common\FEAR Ultimate Shooter Edition\FEARA_7.Arch00
{"version":3,"namesSize":76,"dirCount":4,"fileCount":2,"unk5":1,"unk6":0,"unk7":1,"crc1":"5faab6719f825c42","crc2":"b590bcb1bc14b28a","namesOffset":48}
{"path":"CRC\\71b6aa5f829f425cb590bcb1bc14b28a.crc","offset":1245750,"compSize":83,"decompSize":83,"compLevel":0,"isPresent":true,"isCompressed":false,"isCRC":true}
 
G:\Steam\steamapps\common\FEAR Ultimate Shooter Edition\FEARA_8.Arch00
{"version":3,"namesSize":80,"dirCount":4,"fileCount":2,"unk5":1,"unk6":0,"unk7":1,"crc1":"18dd675555d2c949","crc2":"b63e570fc0e6150c","namesOffset":48}
{"path":"CRC\\5567dd18d25549c9b63e570fc0e6150c.crc","offset":7983388,"compSize":85,"decompSize":85,"compLevel":0,"isPresent":true,"isCompressed":false,"isCRC":true}
 
G:\Steam\steamapps\common\FEAR Ultimate Shooter Edition\FEARE.Arch00
 
G:\Steam\steamapps\common\FEAR Ultimate Shooter Edition\FEARE_1.Arch00
{"version":3,"namesSize":96,"dirCount":2,"fileCount":4,"unk5":1,"unk6":0,"unk7":0,"crc1":"a7c40435dd2c2c40","crc2":"97fdeff2c1c2b342","namesOffset":48}
{"path":"CRC\\3504c4a72cdd402c97fdeff2c1c2b342.crc","offset":4354352,"compSize":112,"decompSize":112,"compLevel":0,"isPresent":true,"isCompressed":false,"isCRC":true}
 
G:\Steam\steamapps\common\FEAR Ultimate Shooter Edition\FEARE_2.Arch00
{"version":3,"namesSize":96,"dirCount":2,"fileCount":4,"unk5":0,"unk6":0,"unk7":0,"crc1":"76a2332440d40d44","crc2":"8e55905688d64d23","namesOffset":48}
{"path":"CRC\\2433a276d440440d8e55905688d64d23.crc","offset":4354352,"compSize":112,"decompSize":112,"compLevel":0,"isPresent":true,"isCompressed":false,"isCRC":true}
 
G:\Steam\steamapps\common\FEAR Ultimate Shooter Edition\FEARE_3.Arch00
{"version":3,"namesSize":96,"dirCount":2,"fileCount":4,"unk5":1,"unk6":0,"unk7":0,"crc1":"fae441dd569ad342","crc2":"ac94d09a0aee3303","namesOffset":48}
{"path":"CRC\\dd41e4fa9a5642d3ac94d09a0aee3303.crc","offset":4436272,"compSize":112,"decompSize":112,"compLevel":0,"isPresent":true,"isCompressed":false,"isCRC":true}
 
G:\Steam\steamapps\common\FEAR Ultimate Shooter Edition\FEARE_4.Arch00
{"version":3,"namesSize":96,"dirCount":2,"fileCount":4,"unk5":1,"unk6":0,"unk7":0,"crc1":"38921853469e104e","crc2":"951403f5f65872e9","namesOffset":48}
{"path":"CRC\\531892389e464e10951403f5f65872e9.crc","offset":4428080,"compSize":112,"decompSize":112,"compLevel":0,"isPresent":true,"isCompressed":false,"isCRC":true}
 
G:\Steam\steamapps\common\FEAR Ultimate Shooter Edition\FEARE_5.Arch00
{"version":3,"namesSize":96,"dirCount":2,"fileCount":4,"unk5":1,"unk6":0,"unk7":0,"crc1":"6e2d89eb5dff2d4b","crc2":"b7a1469e489be7c1","namesOffset":48}
{"path":"CRC\\eb892d6eff5d4b2db7a1469e489be7c1.crc","offset":4518192,"compSize":112,"decompSize":112,"compLevel":0,"isPresent":true,"isCompressed":false,"isCRC":true}
 
G:\Steam\steamapps\common\FEAR Ultimate Shooter Edition\FEARE_6.Arch00
{"version":3,"namesSize":96,"dirCount":2,"fileCount":4,"unk5":1,"unk6":0,"unk7":0,"crc1":"a97ffd0405987248","crc2":"b037c6d95d7578af","namesOffset":48}
{"path":"CRC\\04fd7fa998054872b037c6d95d7578af.crc","offset":4514096,"compSize":112,"decompSize":112,"compLevel":0,"isPresent":true,"isCompressed":false,"isCRC":true}
 
G:\Steam\steamapps\common\FEAR Ultimate Shooter Edition\FEARE_7.Arch00
{"version":3,"namesSize":96,"dirCount":2,"fileCount":4,"unk5":1,"unk6":0,"unk7":0,"crc1":"2adc1ac536541942","crc2":"9029a489b16d74b7","namesOffset":48}
{"path":"CRC\\c51adc2a543642199029a489b16d74b7.crc","offset":4575536,"compSize":112,"decompSize":112,"compLevel":0,"isPresent":true,"isCompressed":false,"isCRC":true}
 
G:\Steam\steamapps\common\FEAR Ultimate Shooter Edition\FEARE_8.Arch00
{"version":3,"namesSize":96,"dirCount":2,"fileCount":4,"unk5":1,"unk6":0,"unk7":0,"crc1":"31cffbefa8749d45","crc2":"b43bc436980a5393","namesOffset":48}
{"path":"CRC\\effbcf3174a8459db43bc436980a5393.crc","offset":4579632,"compSize":112,"decompSize":112,"compLevel":0,"isPresent":true,"isCompressed":false,"isCRC":true}
 
G:\Steam\steamapps\common\FEAR Ultimate Shooter Edition\FEARL.Arch00
 
G:\Steam\steamapps\common\FEAR Ultimate Shooter Edition\FEARL_1.Arch00
{"version":3,"namesSize":48,"dirCount":2,"fileCount":1,"unk5":1,"unk6":0,"unk7":0,"crc1":"3532f1e3820a0241","crc2":"be3c6adb997a9c5c","namesOffset":48}
{"path":"CRC\\e3f132350a824102be3c6adb997a9c5c.crc","offset":160,"compSize":54,"decompSize":54,"compLevel":0,"isPresent":true,"isCompressed":false,"isCRC":true}
 
G:\Steam\steamapps\common\FEAR Ultimate Shooter Edition\FEARL_2.Arch00
{"version":3,"namesSize":48,"dirCount":2,"fileCount":1,"unk5":0,"unk6":0,"unk7":0,"crc1":"ee6539fb1c002041","crc2":"a840c8213fbab88e","namesOffset":48}
{"path":"CRC\\fb3965ee001c4120a840c8213fbab88e.crc","offset":160,"compSize":54,"decompSize":54,"compLevel":0,"isPresent":true,"isCompressed":false,"isCRC":true}
 
G:\Steam\steamapps\common\FEAR Ultimate Shooter Edition\FEARL_3.Arch00
{"version":3,"namesSize":220,"dirCount":7,"fileCount":8,"unk5":1,"unk6":0,"unk7":0,"crc1":"786ca5b900110b47","crc2":"a57dcb2c8a2fc64b","namesOffset":48}
{"path":"CRC\\b9a56c781100470ba57dcb2c8a2fc64b.crc","offset":6051965,"compSize":304,"decompSize":304,"compLevel":0,"isPresent":true,"isCompressed":false,"isCRC":true}
 
G:\Steam\steamapps\common\FEAR Ultimate Shooter Edition\FEARL_4.Arch00
{"version":3,"namesSize":48,"dirCount":2,"fileCount":1,"unk5":1,"unk6":0,"unk7":0,"crc1":"8c800926c5f9de4a","crc2":"8387da48a064e978","namesOffset":48}
{"path":"CRC\\2609808cf9c54ade8387da48a064e978.crc","offset":160,"compSize":54,"decompSize":54,"compLevel":0,"isPresent":true,"isCompressed":false,"isCRC":true}
 
G:\Steam\steamapps\common\FEAR Ultimate Shooter Edition\FEARL_5.Arch00
{"version":3,"namesSize":2244,"dirCount":6,"fileCount":178,"unk5":1,"unk6":0,"unk7":0,"crc1":"00cf2fc1bcfe2b4f","crc2":"9974aae1bfa93c39","namesOffset":48}
{"path":"CRC\\c12fcf00febc4f2b9974aae1bfa93c39.crc","offset":10852239,"compSize":3953,"decompSize":3953,"compLevel":0,"isPresent":true,"isCompressed":false,"isCRC":true}
 
G:\Steam\steamapps\common\FEAR Ultimate Shooter Edition\FEARL_6.Arch00
{"version":3,"namesSize":48,"dirCount":2,"fileCount":1,"unk5":1,"unk6":0,"unk7":0,"crc1":"e0d368768b52ec43","crc2":"b9fb1d94973d8c85","namesOffset":48}
{"path":"CRC\\7668d3e0528b43ecb9fb1d94973d8c85.crc","offset":160,"compSize":54,"decompSize":54,"compLevel":0,"isPresent":true,"isCompressed":false,"isCRC":true}
 
G:\Steam\steamapps\common\FEAR Ultimate Shooter Edition\FEARL_7.Arch00
{"version":3,"namesSize":324,"dirCount":6,"fileCount":18,"unk5":1,"unk6":0,"unk7":0,"crc1":"e41a390139a21248","crc2":"a6e34168f0ddecb7","namesOffset":48}
{"path":"CRC\\01391ae4a2394812a6e34168f0ddecb7.crc","offset":1407824,"compSize":514,"decompSize":514,"compLevel":0,"isPresent":true,"isCompressed":false,"isCRC":true}
 
G:\Steam\steamapps\common\FEAR Ultimate Shooter Edition\FEARL_8.Arch00
{"version":3,"namesSize":184,"dirCount":5,"fileCount":7,"unk5":1,"unk6":0,"unk7":0,"crc1":"f2eb1ad8f0a13242","crc2":"b4f1ebf63e5f9cde","namesOffset":48}
{"path":"CRC\\d81aebf2a1f04232b4f1ebf63e5f9cde.crc","offset":856497,"compSize":271,"decompSize":271,"compLevel":0,"isPresent":true,"isCompressed":false,"isCRC":true}
 
G:\Steam\steamapps\common\FEAR Ultimate Shooter Edition\FEAR_1.Arch00
{"version":3,"namesSize":2132,"dirCount":22,"fileCount":107,"unk5":1,"unk6":0,"unk7":1,"crc1":"51bbcaf040849948","crc2":"bc0adccc24516f02","namesOffset":48}
{"path":"CRC\\f0cabb5184404899bc0adccc24516f02.crc","offset":42242791,"compSize":4680,"decompSize":4680,"compLevel":0,"isPresent":true,"isCompressed":false,"isCRC":true}
 
G:\Steam\steamapps\common\FEAR Ultimate Shooter Edition\FEAR_2.Arch00
{"version":3,"namesSize":7264,"dirCount":26,"fileCount":326,"unk5":0,"unk6":0,"unk7":1,"crc1":"396b8e2dbbb6e047","crc2":"a8ffb90de9559d88","namesOffset":48}
{"path":"CRC\\2d8e6b39b6bb47e0a8ffb90de9559d88.crc","offset":159105978,"compSize":13498,"decompSize":13498,"compLevel":0,"isPresent":true,"isCompressed":false,"isCRC":true}
 
G:\Steam\steamapps\common\FEAR Ultimate Shooter Edition\FEAR_3.Arch00
{"version":3,"namesSize":5660,"dirCount":53,"fileCount":225,"unk5":1,"unk6":0,"unk7":1,"crc1":"f92a0b702f700945","crc2":"8df517caa14ab6db","namesOffset":48}
{"path":"CRC\\700b2af9702f45098df517caa14ab6db.crc","offset":120314133,"compSize":9919,"decompSize":9919,"compLevel":0,"isPresent":true,"isCompressed":false,"isCRC":true}
 
G:\Steam\steamapps\common\FEAR Ultimate Shooter Edition\FEAR_4.Arch00
{"version":3,"namesSize":48,"dirCount":2,"fileCount":1,"unk5":1,"unk6":0,"unk7":1,"crc1":"de082718d5d6674a","crc2":"a6ce948ee4179c31","namesOffset":48}
{"path":"CRC\\182708ded6d54a67a6ce948ee4179c31.crc","offset":160,"compSize":54,"decompSize":54,"compLevel":0,"isPresent":true,"isCompressed":false,"isCRC":true}
 
G:\Steam\steamapps\common\FEAR Ultimate Shooter Edition\FEAR_5.Arch00
{"version":3,"namesSize":10728,"dirCount":61,"fileCount":379,"unk5":1,"unk6":0,"unk7":1,"crc1":"f08aecd04c172140","crc2":"a8898b3e41e3df92","namesOffset":48}
{"path":"CRC\\d0ec8af0174c4021a8898b3e41e3df92.crc","offset":144125163,"compSize":18824,"decompSize":18824,"compLevel":0,"isPresent":true,"isCompressed":false,"isCRC":true}
 
G:\Steam\steamapps\common\FEAR Ultimate Shooter Edition\FEAR_6.Arch00
{"version":3,"namesSize":480,"dirCount":4,"fileCount":19,"unk5":1,"unk6":0,"unk7":1,"crc1":"84606162f777534f","crc2":"84d793ea9a81e678","namesOffset":48}
{"path":"CRC\\6261608477f74f5384d793ea9a81e678.crc","offset":1220116,"compSize":1003,"decompSize":1003,"compLevel":0,"isPresent":true,"isCompressed":false,"isCRC":true}
 
G:\Steam\steamapps\common\FEAR Ultimate Shooter Edition\FEAR_7.Arch00
{"version":3,"namesSize":2276,"dirCount":32,"fileCount":110,"unk5":1,"unk6":0,"unk7":1,"crc1":"7f2d6f037dc7be48","crc2":"817106e31847424b","namesOffset":48}
{"path":"CRC\\036f2d7fc77d48be817106e31847424b.crc","offset":67311374,"compSize":4501,"decompSize":4501,"compLevel":0,"isPresent":true,"isCompressed":false,"isCRC":true}
 
G:\Steam\steamapps\common\FEAR Ultimate Shooter Edition\FEAR_8.Arch00
{"version":3,"namesSize":780,"dirCount":11,"fileCount":29,"unk5":1,"unk6":0,"unk7":1,"crc1":"35bd82695f287041","crc2":"ad2af750b4b7891a","namesOffset":48}
{"path":"CRC\\6982bd35285f4170ad2af750b4b7891a.crc","offset":7365649,"compSize":1375,"decompSize":1375,"compLevel":0,"isPresent":true,"isCompressed":false,"isCRC":true}
 
G:\Steam\steamapps\common\FEAR Ultimate Shooter Edition\FEARXP\FEARA_XP.Arch00
{"version":3,"namesSize":8168,"dirCount":7,"fileCount":351,"unk5":0,"unk6":0,"unk7":1,"crc1":"db0d56e561839940","crc2":"a1fa69131cbfc567","namesOffset":48}
{"path":"CRC\\e5560ddb83614099a1fa69131cbfc567.crc","offset":173746308,"compSize":13287,"decompSize":13287,"compLevel":0,"isPresent":true,"isCompressed":false,"isCRC":true}
 
G:\Steam\steamapps\common\FEAR Ultimate Shooter Edition\FEARXP\FEARE_XP.Arch00
{"version":3,"namesSize":96,"dirCount":2,"fileCount":4,"unk5":0,"unk6":0,"unk7":0,"crc1":"fae441dd569ad342","crc2":"ac94d09a0aee3303","namesOffset":48}
{"path":"CRC\\dd41e4fa9a5642d3ac94d09a0aee3303.crc","offset":5972272,"compSize":112,"decompSize":112,"compLevel":0,"isPresent":true,"isCompressed":false,"isCRC":true}
 
G:\Steam\steamapps\common\FEAR Ultimate Shooter Edition\FEARXP\FEARL_XP.Arch00
{"version":3,"namesSize":9668,"dirCount":11,"fileCount":599,"unk5":0,"unk6":0,"unk7":0,"crc1":"786ca5b900110b47","crc2":"a57dcb2c8a2fc64b","namesOffset":48}
{"path":"CRC\\b9a56c781100470ba57dcb2c8a2fc64b.crc","offset":22131053,"compSize":16861,"decompSize":16861,"compLevel":0,"isPresent":true,"isCompressed":false,"isCRC":true}
 
G:\Steam\steamapps\common\FEAR Ultimate Shooter Edition\FEARXP\FEAR_XP.Arch00
{"version":3,"namesSize":57380,"dirCount":117,"fileCount":2712,"unk5":0,"unk6":0,"unk7":1,"crc1":"f92a0b702f700945","crc2":"8df517caa14ab6db","namesOffset":48}
{"path":"CRC\\700b2af9702f45098df517caa14ab6db.crc","offset":1656734253,"compSize":115085,"decompSize":115085,"compLevel":0,"isPresent":true,"isCompressed":false,"isCRC":true}
 
G:\Steam\steamapps\common\FEAR Ultimate Shooter Edition\FEARXP2\FEARA_XP.Arch00
{"version":3,"namesSize":29604,"dirCount":22,"fileCount":1442,"unk5":1,"unk6":0,"unk7":1,"crc1":"01bc330241531645","crc2":"8a7eaa319034e17a","namesOffset":48}
{"path":"CRC\\0233bc01534145168a7eaa319034e17a.crc","offset":1382888109,"compSize":51038,"decompSize":51038,"compLevel":0,"isPresent":true,"isCompressed":false,"isCRC":true}
 
G:\Steam\steamapps\common\FEAR Ultimate Shooter Edition\FEARXP2\FEARE_XP.Arch00
{"version":3,"namesSize":96,"dirCount":2,"fileCount":4,"unk5":1,"unk6":0,"unk7":0,"crc1":"f72ea44e200c9142","crc2":"95c66f3f50c68616","namesOffset":48}
{"path":"CRC\\4ea42ef70c20429195c66f3f50c68616.crc","offset":6320432,"compSize":112,"decompSize":112,"compLevel":0,"isPresent":true,"isCompressed":false,"isCRC":true}
 
G:\Steam\steamapps\common\FEAR Ultimate Shooter Edition\FEARXP2\FEARL_XP.Arch00
{"version":3,"namesSize":59992,"dirCount":14,"fileCount":3953,"unk5":1,"unk6":0,"unk7":0,"crc1":"49c15e1575d58648","crc2":"9945bda8124918b9","namesOffset":48}
{"path":"CRC\\155ec149d57548869945bda8124918b9.crc","offset":157499143,"compSize":106882,"decompSize":106882,"compLevel":0,"isPresent":true,"isCompressed":false,"isCRC":true}
 
G:\Steam\steamapps\common\FEAR Ultimate Shooter Edition\FEARXP2\FEARM_XP.arch00
{"version":3,"namesSize":296584,"dirCount":283,"fileCount":14386,"unk5":1,"unk6":0,"unk7":1,"crc1":"605738732edaaa4f","crc2":"924b18df2bbc4efe","namesOffset":48}
{"path":"CRC\\73385760da2e4faa924b18df2bbc4efe.crc","offset":4085695234,"compSize":611635,"decompSize":611635,"compLevel":0,"isPresent":true,"isCompressed":false,"isCRC":true}
 
G:\Steam\steamapps\common\FEAR Ultimate Shooter Edition\FEARXP2\FEAR_XP.Arch00
{"version":3,"namesSize":59760,"dirCount":375,"fileCount":2936,"unk5":1,"unk6":0,"unk7":1,"crc1":"6d46c22f93cbe448","crc2":"bc2d72cac8e6d163","namesOffset":48}
{"path":"CRC\\2fc2466dcb9348e4bc2d72cac8e6d163.crc","offset":2164599848,"compSize":127846,"decompSize":127846,"compLevel":0,"isPresent":true,"isCompressed":false,"isCRC":true}
'''