# Deus Ex Human Revolution Director's Cut Tools

import sys

sys.path.insert(0, r'C:\Projects\PythonLib\python\v001')

from bfw.utils import *
from bfw.reader import *
from bfw.types.enums import Enum



GAME_DIR = 'G:\\Steam\\steamapps\\common\\Deus Ex Human Revolution Director\'s Cut'



class PakItemMeta:
    def __init__ (self):
        self.size      = None
        self.absOffset = None
        self.unk1      = None
        self.zeros1    = None
        self.pakIndex  = None
        self.offset    = None


def isCP1252String (data):
    try:
        data.decode('cp1252')
        return True
    except:
        return False


def detectExtByData (data):
    data4 = data[:4]

    if data4 == b'CDRM':
        return '.cdrm'

    if data4 == b'FSB4':
        return '.fsb'

    if data4 == b'Mus!':
        return '.mus'

    if data4 == b'CRID':
        return '.crid'

    if data4 == b'<dx3':
        return '.xml'

    if data4 == b'PCD9':
        return '.pcd9'

    num = int.from_bytes(data4, 'little')
    
    if num in [ 22050, 32000, 44100, 48000 ]:
        return '.samples'

    if 0 <= num <= 6:
        return '.lng'

    if isCP1252String(data):
        return '.txt'

    return '.bin'


def unpackPackage (filePath, unpackDir=None):
    filePath = getAbsPath(filePath)

    if not isFile(filePath):
        raise Exception(f'File is not found: { filePath }')

    if not unpackDir:
        unpackDir = joinPath(getDirPath(filePath), '.unpacked')

    with openFile(filePath) as f:
        pakSize  = f.u32()
        platform = f.read(4)

        assert platform == b'pc-w'

        unk3 = f.read(60)

        assert unk3 == (b'\x00' * 60)

        itemCount = f.u32()

        unks1 = [ f.u32() for _ in range(itemCount) ]

        items = [ PakItemMeta() for _ in range(itemCount) ]

        pakCount = 0

        for item in items:
            item.size      = f.u32()
            item.absOffset = f.u32() * 2048
            item.unk1      = f.u32()
            item.zeros1    = f.u32()

            item.pakIndex = item.absOffset // pakSize
            item.offset   = item.absOffset % pakSize

            assert item.zeros1 == 0, item.zeros1

            pakCount = max(pakCount, item.pakIndex + 1)

        items.sort(key=lambda item: item.offset)

        paks = [ [] for _ in range(pakCount) ]

        for item in items:
            paks[item.pakIndex].append(item)

    createDirs(unpackDir)

    for i, items in enumerate(paks):
        pakPath = replaceExt(filePath, f'.{i:03}')

        with openFile(pakPath) as f:
            for item in items:
                f.seek(item.offset)

                data = f.read(item.size)

                ext = detectExtByData(data)

                itemPath = joinPath(unpackDir, f'{item.absOffset:012}{ext}')

                writeBin(itemPath, data)

    '''
    .cdrm    = 6.8GB
    .samples = 5.6GB
    .crid    = 5.1GB
    .lng     = 17.4MB
    .txt     = 2.7MB
    .mus     = 1.6MB
    .fsb     = 314.0KB
    .bin     = 174.5KB
    .pcd9    = 9.0KB
    .xml     = 811B

    ---------------------------------------------------------------

    samples:
    b'D\xac\x00\x00' 87401
    b'"V\x00\x00' 11
    b'\x80\xbb\x00\x00' 10
    b'\x00}\x00\x00' 1

    sign as ext:
    + b'CDRM' 15552
    + b'FSB4' 157
    + b'Mus!' 157
    + b'CRID' 63

    unk (bin):
    b'\x1f\x00\x00\x00' 1
    b'\xeb\x02\x00\x00' 1

    lng:
    b'\x00\x00\x00\x00' 1
    b'\x01\x00\x00\x00' 1
    b'\x02\x00\x00\x00' 1
    b'\x03\x00\x00\x00' 1
    b'\x04\x00\x00\x00' 1
    b'\x05\x00\x00\x00' 1
    b'\x06\x00\x00\x00' 1

    pcd9:
    + b'PCD9' 1

    xml:
    + b'<dx3' 1

    txt:
    + b'4101' 1
    + b'746\r' 1
    + b'1,45' 1
    + b'6,26' 1
    + b'1,17' 1
    + b'6,58' 1
    + b'1,91' 1
    + b'4,49' 1
    + b'3,18' 1
    '''


def unpackCDRM (filePath, unpackDir=None):
    filePath = getAbsPath(filePath)

    if not isFile(filePath):
        raise Exception(f'File is not found: { filePath }')

    if not unpackDir:
        unpackDir = joinPath(getDirPath(filePath), '.unpacked')

    with openFile(filePath) as f:
        signature = f.read(4)

        assert signature == b'CDRM'

        unk1 = f.u32()
        unk2 = f.u32()
        unk3 = f.u32()

        assert unk1 == 2, unk1
        assert unk3 in [ 0, 8 ], unk3

        for i in range(unk2):
            unk4 = f.u32()
            unk5 = f.u32()

            print(unk4, unk5)

        print(f.tell())


def unpackCDRMs (gameDir, unpackDir=None):
    for filePath in iterFiles(gameDir, True, [ '.cdrm' ]):
        print(filePath)

        unpackCDRM(filePath, unpackDir)

        print(' ')


def unpackAll (gameDir, unpackDir=None):
    for filePath in iterFiles(gameDir, True, [ '.000', '.001', '.002', '.003' ]):
        print(filePath)

        unpack(filePath, unpackDir)

        print(' ')


def main ():
    # unpackAll(GAME_DIR, joinPath(GAME_DIR, '.unpacked'))
    # unpackPackage(joinPath(GAME_DIR, 'BIGFILE.000'))
    # unpackCDRM('G:\\Steam\\steamapps\\common\\Deus Ex Human Revolution Director\'s Cut\\.unpacked\\009742764032.cdrm')
    unpackCDRM('G:\\Steam\\steamapps\\common\\Deus Ex Human Revolution Director\'s Cut\\.unpacked\\000521209856.cdrm')
    # unpackCDRMs(joinPath(GAME_DIR, '.unpacked'))
    # 'G:\\Steam\\steamapps\\common\\Deus Ex Human Revolution Director\'s Cut\\__tmp.bin'

    # with openFile('G:\\Steam\\steamapps\\common\\Deus Ex Human Revolution Director\'s Cut\\.unpacked\\009742764032.cdrm') as f:
    #     f.seek(3344)
    #     print(len(decompressData(f.read(1899))))
    #     # 3344 1899 (4657)



if __name__ == '__main__':
    main()
