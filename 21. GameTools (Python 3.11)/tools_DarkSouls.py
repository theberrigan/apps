# Dark Souls Prepare to Die Edition Tools

import sys

sys.path.insert(0, r'C:\Projects\PythonLib\python\v001')

from bfw.utils import *
from bfw.reader import *
from bfw.types.enums import Enum



GAME_DIR = r'G:\Steam\steamapps\common\Dark Souls Prepare to Die Edition'

BHD_SIGNATURE = b'BHD5'



class BDTGroup:
    def __init__ (self):
        self.count  = None
        self.offset = None
        self.items  = None


class BDTItem:
    def __init__ (self):
        self.id     = None
        self.size   = None
        self.offset = None
        self.zeros1 = None


class BNDItem:
    def __init__ (self):
        self.unk1       = None
        self.size       = None
        self.offset     = None
        self.unk2       = None
        self.pathOffset = None
        self.size2      = None
        self.path       = None


class TPFItem:
    def __init__ (self):
            self.offset     = None
            self.size       = None
            self.unk2       = None
            self.nameOffset = None
            self.zeros1     = None
            self.name       = None


class PackageType (Enum):
    Raw = 0
    BDT = 1
    BDF = 2
    BND = 3
    DCX = 4


def isShiftJISString (data):
    try:
        data.decode('shift_jis')
        return True
    except:
        return False


def detectExtByData (data):
    data3 = data[:3]
    data4 = data[:4]
    data5 = data[:5]

    if data3 == b'BND':         # +
        return '.anibnd'

    if data3 == b'BHF':         # +
        return '.chrtpfbhd'
    
    if data3 == b'BDF':         # - (size: +)
        return '._bdf'
    
    if data3 == b'DRB':         # -
        return '._drb'
    
    if data4 == b'BJBO':        # - (size: +)
        return '._bjbo'
    
    if data4 == b'CFOM':        # - (size: +)
        return '._cfom'
    
    if data4 == b'MFOM':        # - (size: +)
        return '._mfom'
    
    if data4 == b'RFOM':        # - (size: +)
        return '._rfom'
    
    if data4 == b'DCX\x00':     # - (size: +)
        return '._dcx'
    
    if data4 == b'TPF\x00':     # +
        return '.tpf'
    
    if data4 == b'TAE ':        # +
        return '.tae'
    
    if data4 == b'\x89PNG':     # +
        return '.png'
    
    if data4 == b'FSB4':        # +
        return '.fsb'
    
    if data4 == b'FEV1':        # + 
        return '.fev'
    
    if data4 == b'\x1bLua':     # +
        return '.lua'
    
    if data4 == b'W\xe0\xe0W':  # +
        return '.hkx'
    
    if data4 == b'F2TR':        # +
        return '.flver2tri'
    
    if data4 == b'fSSL':        # +
        return '.esd'
    
    if data4 == b'LUAI':        # +
        return '.luainfo'
    
    if data4 == b'FXR\x00':     # + (size: ?)
        return '.ffx'
    
    if data4 == b'DFPN':        # - (size: +)
        return '.dfpn'
    
    if data5 == b'FRTRI':       # +
        return '.tri'
    
    if data5 == b'FRCTL':       # +
        return '.ctl'
    
    if data5 == b'FLVER':       # +
        return '.flver'
    
    if data5 == b'FREGM':       # +
        return '.egm'
    
    if data5 == b'FREGT':       # +
        return '.egt'
    
    if data[:2] == b'BM' and len(data) >= 6 and int.from_bytes(data[2:6], 'little') == len(data):  # +
        return '.bmp'

    if isShiftJISString(data):
        return '.txt'

    return '.bin'


def detectPackageTypeByData (data):
    if data[:3] == b'BDF':
        return PackageType.BDF

    if data[:3] == b'BND':
        return PackageType.BND

    if data[:4] == b'DCX\x00':
        return PackageType.DCX

    return PackageType.Raw


def unpackSubPackage (data, unpackDir, itemName):
    packageType = detectPackageTypeByData(data)

    if packageType == PackageType.BDF:
        unpackBDF(MemReader(data), unpackDir, itemName)
        return True

    if packageType == PackageType.DCX:
        unpackDCX(MemReader(data), unpackDir, itemName)
        return True

    if packageType == PackageType.BND:
        unpackBND(MemReader(data), unpackDir, itemName)
        return True

    return False


def unpackBDT (filePath, unpackDir=None):
    filePath = getAbsPath(filePath)

    if not isFile(filePath):
        raise Exception(f'File is not found: { filePath }')

    if not unpackDir:
        unpackDir = joinPath(getDirPath(filePath), '.unpacked')

    bhdPath = replaceExt(filePath, '.bhd5')
    bdtPath = replaceExt(filePath, '.bdt')

    with openFile(bhdPath) as f:
        signature = f.read(4)

        assert signature == BHD_SIGNATURE

        unk1       = f.u32()
        unk2       = f.u32()
        fileSize   = f.u32()
        groupCount = f.u32()
        unk5       = f.u32()

        assert unk1 == 255
        assert unk2 == 1
        assert unk5 == 24

        groups = [ BDTGroup() for _ in range(groupCount) ]

        for group in groups:
            group.count  = f.u32()
            group.offset = f.u32()

        for group in groups:
            f.seek(group.offset)

            group.items = [ BDTItem() for _ in range(group.count) ]

            for item in group.items:
                item.id     = f.u32()
                item.size   = f.u32()
                item.offset = f.u32()
                item.zeros1 = f.u32()

    with openFile(bdtPath) as f:
        for group in groups:
            for item in group.items:
                f.seek(item.offset)

                data = f.read(item.size)

                itemName = f'{item.id:08X}'

                if not unpackSubPackage(data, unpackDir, itemName):
                    ext = detectExtByData(data)

                    itemPath = joinPath(unpackDir, '__unnamed', f'{itemName}{ext}')

                    createFileDirs(itemPath)

                    writeBin(itemPath, data)

                '''
                ++ b'\x89PNG' - PNG
                ++ b'FSB4'    - FMOD Sound Bank
                ++ b'FEV1'    - FMOD Events
                ++ b'BDF3'    - DCX with extra 16-byte header (contains compressed hkx and tpf files)
                ++ b'DCX\x00' - different binary data
                + b'BJBO'     - patternless binary file
                + b'MFOM'     - 1 small file with string "frpg_mixer/mixer/frpg_rev"
                + b'RFOM'     - 1 small binary file with floats
                + b'TPF\x00'  - DDS(s)
                + b'BND3'     - 2 files with meta items with abs paths
                + b'CFOM'     - 1 small file with some ints
                + b'BHF3'     - only meta items with file names
                + b'DRB\x00'  - 3 files with some UTF-16 string and sections (DRB, STR, TEXI, SHPR, CTPR, ANIP, INTP, SCDP, SHAP, CTRL, ANIK, ANIO, ANIM, SCDK, SCDO, SCDL, DLGO, DLG, END)
                + b'DFPN'     - 2 binary files with a lot of \x00 
                + b'TAE '     - 1 binary file with couple of UTF-16 strings
                + b'EDF\x00'  - binary file
                + b'ELD\x00'  - binary file
                + b'EVD\x00'  - binary files with a lot of \x00 
                + b'fSSL'     - 2 binary files
                b'map:'
                b'\x00\x00\x00\x88'
                b'\x00\x00H`'
                b'\x00\x00\x11\xb8'
                b'\x00\x00\x018'
                b'\x00\x00\x1bX'
                b'\x00\x00<\xdc'
                b'\x00\x00?p'
                b'\x00\x01\x11 '
                b'\x00\x00\x00\\'
                b'\x01\x00\x00\x00'
                b'\x00\x00\x01d'
                b'\x00\x00\x00\x00'
                b'\x00\x00\x03t'
                b'\x00\x00\x00\xb4'
                b'\x00\x00\x03H'
                b'\x00\x00\x02\xc4'
                b'\x00\x00\x02\xf0'
                b'\x00\x00N\x0c'
                b'\x00\x00\x00\xe0'
                b'\x00\x00\x03\xa0'
                b'\r\n##'
                b'\x00\x00\x01\xe8'
                b'\x00\x00\x01\xbc'
                b'\x00\x00\x01\x90'
                b'#\x83C\x83'
                b'\x00\x00\x02\x14'
                b'\x00\x005 '
                b'\x02\x00\x00\x00'
                b'\x00\x00\x1c`'
                b'\x00\x00\x01\x0c'
                b'\x00\x00!0'
                '''


def unpackBDF (f, unpackDir, itemName):
    f.setByteOrder(ByteOrder.Big)

    signature = f.read(16)

    assert signature == b'BDF307D7R6\x00\x00\x00\x00\x00\x00'

    unpackDCX(f, unpackDir, itemName)


def unpackDCX (f, unpackDir, itemName):
    f.setByteOrder(ByteOrder.Big)

    signature = f.read(4)

    assert signature == b'DCX\x00'

    unk1 = f.u32()
    unk2 = f.u32()
    unk3 = f.u32()
    unk4 = f.u32()
    unk5 = f.u32()

    assert unk1 == 65536, unk1
    assert unk2 == 24, unk2
    assert unk3 == 36, unk3
    assert unk4 == 36, unk4
    assert unk5 == 44, unk5

    signature = f.read(4)

    assert signature == b'DCS\x00'

    decompSize = f.u32()
    compSize   = f.u32()

    signature = f.read(4)

    assert signature == b'DCP\x00'

    signature = f.read(4)

    assert signature == b'DFLT'

    unk6  = f.u32()
    unk7  = f.u32()
    unk8  = f.u32()
    unk9  = f.u32()
    unk10 = f.u32()
    unk11 = f.u32()

    assert unk6 == 32, unk6
    assert unk7 == 150994944, unk7
    assert unk8 == 0, unk8
    assert unk9 == 0, unk9
    assert unk10 == 0, unk10
    assert unk11 == 65792, unk11

    signature = f.read(4)

    assert signature == b'DCA\x00'

    unk12 = f.u32()

    assert unk12 == 8, unk12

    data = f.read(compSize)
    data = decompressData(data)

    assert len(data) == decompSize

    if not unpackSubPackage(data, unpackDir, itemName):
        ext = detectExtByData(data)

        itemPath = joinPath(unpackDir, '__unnamed', f'{itemName}{ext}')

        createFileDirs(itemPath)

        writeBin(itemPath, data)


def unpackBND (f, unpackDir, itemName):
    f.setByteOrder(ByteOrder.Little)

    signature = f.read(12)

    assert signature in [
        b'BND307C15R17',
        b'BND307D7R6\x00\x00',
        b'BND307F31W13',
        b'BND307J12L31',
        b'BND307K31N36',
        b'BND307M13L29',
        b'BND308C1N50\x00',
        b'BND308J17V46',
        b'BND309E22N26',
        b'BND309E22N27',
        b'BND309G17X51',
        b'BND310B20L16',
        b'BND310I2N48\x00',
        # ----------------
        b'BND308D25L29',
        b'BND309G16Q26',
        b'BND307D27U31',
        b'BND307D2Q19\x00',
    ], signature

    flags     = f.u32()  # 0b1110100
    itemCount = f.u32()
    metaSize  = f.u32()
    unk2      = f.u32()
    unk3      = f.u32()
    hasSize2  = bool(flags & (1 << 2))

    assert flags in [ 84, 112, 116 ], flags
    assert unk2 == 0, unk2
    assert unk3 == 0, unk3

    items = [ BNDItem() for _ in range(itemCount) ]

    for item in items:
        item.unk1       = f.u32()
        item.size       = f.u32()
        item.offset     = f.u32()
        item.unk2       = f.u32()
        item.pathOffset = f.u32()

        assert item.unk1 == 64

        if hasSize2:
            item.size2 = f.u32()

            assert item.size == item.size2, (item.size, item.size2)

    for item in items:
        f.seek(item.pathOffset)

        item.path = f.string(encoding='shift_jis')

        # print(f'> { item.path }')

    for item in items:
        f.seek(item.offset)

        data = f.read(item.size)

        if not unpackSubPackage(data, unpackDir, itemName):
            item.path = item.path.lstrip('\\/')

            if isAbsPath(item.path):
                item.path = getRelPath(item.path, r'N:\FRPG')

            ext = detectExtByData(data)

            itemPath = joinPath(unpackDir, item.path)

            createFileDirs(itemPath)

            writeBin(itemPath, data)


# Texture Pack File?
def unpackTPF (filePath, unpackDir=None):
    filePath = getAbsPath(filePath)

    if not isFile(filePath):
        raise Exception(f'File is not found: { filePath }')

    if not unpackDir:
        unpackDir = joinPath(getDirPath(filePath), '.unpacked')

    with openFile(filePath) as f:
        signature = f.read(4)

        assert signature == b'TPF\x00'

        dataSize  = f.u32()
        itemCount = f.u32()
        unk1      = f.u32()

        assert unk1 == 131840, unk1

        items = [ TPFItem() for _ in range(itemCount) ]

        for item in items:
            item.offset     = f.u32()
            item.size       = f.u32()
            item.unk2       = f.u32()  # flags?
            item.nameOffset = f.u32()
            item.zeros1     = f.u32()

            assert item.zeros1 == 0

        for item in items:
            f.seek(item.nameOffset)

            item.name = f.string()

        # --- 16 * itemCount bytes of zeros here ---

        for item in items:
            f.seek(item.offset)

            data = f.read(item.size)


# bdt -> bnd
# bdt -> bdf -> dcx
# bdt -> dcx
# bdt -> dcx -> bnd
# bdt -> dcx -> bnd -> bnd
def unpackBDTs ():
    for filePath in iterFiles(GAME_DIR, True, [ '.bdt' ]):
        print(filePath)

        unpackBDT(filePath)

        print(' ')


def unpackTPFs ():
    for filePath in iterFiles(GAME_DIR, True, [ '.tpf' ]):
        print(filePath)

        unpackTPF(filePath)

        print(' ')


def main ():
    # unpackBDTs()
    # unpackTPFs()
    # unpackTPF(r'G:\Steam\steamapps\common\Dark Souls Prepare to Die Edition\DATA\.unpacked\__unnamed\A20205C7.tpf')



if __name__ == '__main__':
    main()


'''
b'\x02\x00\x00\x00' 18
b'\x01\x00\x00\x00' 18
b'\x00\x00\x00\x00' 18
b'\x00\x00\x00\\' 208
b'\x00\x00\x00\x88' 13
b'\x00\x00\x01\x90' 6
b'\x00\x00\x01\x0c' 7
b'\x00\x01\x11 ' 1
b'\x00\x00\x01\xbc' 1
b'\x00\x00N\x0c' 1
b'\x00\x00\x1bX' 1
b'\x00\x00\x00\xb4' 11
b'\x00\x00\x01d' 7
b'\x00\x00\x03t' 1
b'\x00\x00\x02\x14' 2
b'\x00\x00\x02\xc4' 2
b'\x00\x00\x03H' 1
b'\x00\x00H`' 1
b'\x00\x00\x018' 4
b'\x00\x00\x02\xf0' 1
b'\x00\x00\x1c`' 1
b'\x00\x00<\xdc' 1
b'\x00\x00\x03\xa0' 1
b'\x00\x00\x00\xe0' 3
b'\x00\x00?p' 1
b'\x00\x00\x11\xb8' 1
b'\x00\x005 ' 1
b'\x00\x00\x01\xe8' 1
b'\x00\x00!0' 1
'''
'''
+ b'FXR\x00__.ffx'
+ b'FRTR__.tri'
+ b'BHF3__.chrtpfbhd'
+ b'LUAI__.luainfo'
+ b'FREG__.egt'
+ b'FRCT__.ctl'
+ b'fSSL__.esd'
+ b'FREG__.egm'
+ b'TAE __.tae'
+ b'BM8\xc0__.bmp'
+ b'TPF\x00__.tpf'
+ b'W\xe0\xe0W__.hkx'
+ b'FLVE__.flver'
+ b'BND3__.anibnd'
+ b'\x1bLua__.lua'
+ b'F2TR__.flver2tri'
b'<\x06\x00\x00__.luagnl'
b'\xb0\x02\x00\x00__.luagnl'
b'\xe0,\x00\x00__.paramdef'
b'\x00\x03\x00\x00__.luagnl'
b'T\x03\x00\x00__.luagnl'
b'\x80!\x00\x00__.paramdef'
b'0h\x00\x00__.param'
b'@\x06\x00\x00__.paramdef'
b'0\x0e\x00\x00__.param'
b'\x80\x16\x00\x00__.paramdef'
b'\x10V\x00\x00__.paramdef'
b'\x00\x10\x00\x00__.paramdef'
b'\xb0\x07\x00\x00__.paramdef'
b'0\x0b\x00\x00__.param'
b'\x00\x03\xfe\xff__.vpo'
b'`\x06\x00\x00__.paramdef'
b'\xe0\x08\x00\x00__.param'
b'0\n\x00\x00__.param'
b'P\x03\x00\x00__.paramdef'
b'\xd0\x07\x00\x00__.paramdef'
b'@\x10\x00\x00__.paramdef'
b'__.txt'
b'`7\x00\x00__.paramdef'
b'0\x16\x00\x00__.paramdef'
b' \x15\x00\x00__.paramdef'
b'\x80\xe9\x04\x00__.param'
b'@\x05\x00\x00__.param'
b'\x83L\x83\x83__.dmy'
b'\x10\xc6\x00\x00__.param'
b'0\x03\x00\x00__.paramdef'
b'0\x1a\x00\x00__.param'
b'\x82\xb1\x82\xcc__.txt'
b"\xd0'\x00\x00__.param"
b'\xf0\x05\x00\x00__.paramdef'
b'\x00\x87\x00\x00__.paramdef'
b'\xec\x07\x00\x00__.luagnl'
b'\xc0\xe6\x00\x00__.param'
b'\x10,\x00\x00__.paramdef'
b'\x005\x01\x00__.param'
b'p\x04\x00\x00__.luagnl'
b'\x00\x11\x00\x00__.paramdef'
b'\x00\xf4\x02\x00__.param'
b'0\x93\x00\x00__.paramdef'
b'\xb0\xb8\x03\x00__.param'
b'\xb0\x02\x00\x00__.param'
b'\x10E\x00\x00__.param'
b'0\r\x00\x00__.param'
b'pC\x00\x00__.param'
b'\xa0\x0b\x00\x00__.paramdef'
b'\xe0\x01\x00\x00__.param'
b'\x90\x08\x00\x00__.param'
b'\xf08\x00\x00__.paramdef'
b'`\x0c\x00\x00__.param'
b'\xa0\x08\x00\x00__.param'
b'\xa0\xfb\x02\x00__.param'
b'\xb06\x00\x00__.paramdef'
b' :\x00\x00__.param'
b'\x01\x00\x00\x00__.sibcam'
b'\xf8\x02\x00\x00__.luagnl'
b'h\x03\x00\x00__.luagnl'
b'\x1c\x06\x00\x00__.luagnl'
b'\xb8\x01\x00\x00__.luagnl'
b'\x10\x1b\x00\x00__.paramdef'
b'\x08P\x00\x00__.param'
b'P\r\x00\x00__.paramdef'
b'`\x03\x00\x00__.param'
b'`e\x05\x00__.param'
b'\xc0\x01\x00\x00__.luagnl'
b'0\x08\x00\x00__.param'
b'\xa0/\x00\x00__.param'
b'0\x16\x00\x00__.param'
b'P3\x01\x00__.param'
b'\xf8\x06\x00\x00__.luagnl'
b'\x90J\x00\x00__.paramdef'
b'p\x05\x00\x00__.paramdef'
b'(\x04\x00\x00__.luagnl'
b'\xd0\x0c\x00\x00__.paramdef'
b'\xe0\n\x00\x00__.paramdef'
b'\xd0<\x00\x00__.paramdef'
b'\xec\x03\x00\x00__.luagnl'
b'`b\x00\x00__.paramdef'
b'p\x06\x00\x00__.paramdef'
b'\x80\x04\x00\x00__.paramdef'
b'0\x04\x00\x00__.param'
b'\xd0\x01\x00\x00__.param'
b'\xb0\x1f\x02\x00__.param'
b'\x90g\x00\x00__.paramdef'
b'\xd8\x06\x00\x00__.luagnl'
b'\x90\x1b\x00\x00__.paramdef'
b'\xa0\x03\x00\x00__.luagnl'
b'p\x9c\x02\x00__.param'
b'`\x0c\x00\x00__.paramdef'
b'\x80\x01\x00\x00__.param'
b'\xa0\x16\x00\x00__.paramdef'
b'\xd0g\x00\x00__.param'
b'D\x08\x00\x00__.param'
b'@!\x00\x00__.param'
b'0\xa8\x01\x00__.param'
b'\xe8\x15\x00\x00__.luagnl'
b'\x01\x00\x00\x00__.hkxpwv'
b'\x01\x00\x00\x00__.nvm'
b'\x00\x00\x01\x00__.fmg'
b'\x00\x00\x00\x00__.mtd'
b'\x00\x01\x00\x00__.rmb'
b'\x90\t\x00\x00__.param'
b'\xb0\x9c\x01\x00__.param'
b'\x80\x0e\x00\x00__.paramdef'
b'\xdc\x04\x00\x00__.luagnl'
b'\x80\x06\x00\x00__.paramdef'
b'\x00\x03\xff\xff__.fpo'
b'@\x05\x00\x00__.paramdef'
b'\xc0\x06\x00\x00__.param'
b'0\x07\x00\x00__.param'
b'\x00\x07\x00\x00__.paramdef'
b'\x80\x15\x00\x00__.paramdef'
b'\xa0\x9f\x04\x00__.param'
b'`#\x00\x00__.paramdef'
b'\x00\x00\x00\x00__.txt'
b'\x80\x0b\x00\x00__.paramdef'
b'\x01\x00\x00\x00__.bsipwv'
b'\xf0G\x00\x00__.paramdef'
b'\xc0\x0b\x00\x00__.paramdef'
b'P\n\x00\x00__.paramdef'
b'\x14\x04\x00\x00__.luagnl'
'''