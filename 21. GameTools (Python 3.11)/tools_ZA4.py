# Zombie Army 4 Tools

import sys
import regex

sys.path.insert(0, r'C:\Projects\PythonLib\python\v001')

from bfw.utils import *
from bfw.reader import *
from bfw.native.limits import *
from bfw.types.enums import Enum2



GAME_DIR = r'G:\Steam\steamapps\common\ZombieArmy4'
PACKAGES_JSON_NAME = 'packages.json'



class Signature (Enum2):
    Plain      = b'Asura   '
    Compressed = b'AsuraZbb'


class SectionType (Enum2):
    AALG = b'AALG'  #       1  14.9MB
    AAUT = b'AAUT'  #       1  51.4KB
    ADSP = b'ADSP'  #       1   1.0KB
    AFSO = b'AFSO'  #       1     12B
    AIRE = b'aire'  #       1  13.9KB
    AMRO = b'AMRO'  #       1     20B
    APFO = b'APFO'  #       1     20B
    AREA = b'area'  #   13578  21.9MB
    ARNM = b'ARNM'  #      31  63.4MB
    ASSD = b'ASSD'  #       1     12B
    ASTS = b'ASTS'  #     129   4.5GB  # Audio Stream Sounds
    ATRT = b'ATRT'  #     318   8.6MB
    AUDA = b'AUDA'  #     319  15.2MB
    AXBB = b'AXBB'  #       1     16B
    AXBT = b'AXBT'  #       1   2.6KB
    BLUE = b'BLUE'  #     161   4.9MB
    CONA = b'CONA'  #  149048  15.8MB
    CPAN = b'CPAN'  #     427  63.2KB
    CRNA = b'CRNA'  #      31 206.7KB
    CTAC = b'CTAC'  #   62592  10.5MB
    CTAT = b'CTAT'  #   91068   9.5MB
    CTEV = b'CTEV'  #  234833  24.7MB
    CTTR = b'CTTR'  #   64438  10.5MB
    CUTS = b'CUTS'  #    3698  14.7MB
    DCAL = b'DCAL'  #       1  97.6KB
    DFG2 = b'DFG2'  #       1     16B
    DLCG = b'DLCG'  #      12   6.8KB
    DLCR = b'DLCR'  #      13    208B
    DLET = b'DLET'  #    1120 122.4KB
    DLEV = b'DLEV'  #  185346  22.5MB
    DLLN = b'DLLN'  #  233380  39.5MB
    DLLT = b'DLLT'  #     168   7.2KB
    DYIN = b'DYIN'  #      34 206.6KB
    DYMC = b'DYMC'  #       1 134.4KB
    EMOD = b'EMOD'  #      33    740B
    ENTI = b'ENTI'  # 1845591 547.7MB
    FAAN = b'FAAN'  #  236108 604.3MB
    FACE = b'FACE'  #     236   1.0MB
    FNFO = b'FNFO'  #     529   8.3KB
    FNTK = b'FNTK'  #      10   4.7KB
    FOG  = b'FOG '  #      24   4.3KB
    FONT = b'FONT'  #      16   1.5MB
    FSX2 = b'FSX2'  #      91  21.5KB
    FXET = b'FXET'  #    9248   5.2MB
    FXPT = b'FXPT'  #   38614  42.6MB
    FXST = b'FXST'  #   38614  14.5MB
    FXTT = b'FXTT'  #    2065   1.8MB
    GISN = b'GISN'  #      33   5.6MB
    HCAN = b'HCAN'  #   18607 560.5MB
    HMPT = b'HMPT'  #    5412   3.1MB
    HRTF = b'HRTF'  #       1  96.5KB
    HSBB = b'HSBB'  #   21529   6.7MB
    HSKE = b'HSKE'  #   21529 252.3KB
    HSKL = b'HSKL'  #   19374   1.2MB
    HSKN = b'HSKN'  #   21529   1.0GB
    HSND = b'HSND'  #    1299   2.0MB
    HTPR = b'HTPR'  #       6    184B
    HTXT = b'HTXT'  #      99  12.9MB
    IKTM = b'IKTM'  #       4   2.2KB
    INST = b'INST'  #      33   1.6GB
    IPTP = b'IPTP'  #       1     30B
    IRTX = b'IRTX'  #      33   3.1KB
    MARE = b'MARE'  #      57  18.6MB
    META = b'META'  #       1     20B
    NAV1 = b'NAV1'  #     319   9.0KB
    OCMH = b'OCMH'  #      24   2.7MB
    PBRV = b'PBRV'  #      33 684.1MB
    PHEN = b'PHEN'  #      33   2.0GB
    PLUT = b'PLUT'  #      24  69.0KB
    PSKY = b'PSKY'  #      24  14.1KB
    RAGD = b'RAGD'  #      57 219.9KB
    REND = b'REND'  #      24    288B
    RSCF = b'RSCF'  #  199769  76.8GB  +
    RSFL = b'RSFL'  #     379   2.5MB
    RVBP = b'RVBP'  #      24  12.2KB
    SDDC = b'SDDC'  #      33   1.1MB
    SDEV = b'SDEV'  #   13709   3.6MB
    SDGS = b'SDGS'  #       1     12B
    SDMX = b'SDMX'  #       1 417.1KB
    SDPH = b'SDPH'  #     319  35.2MB
    SDSM = b'SDSM'  #   36035   6.1MB
    SMSG = b'SMSG'  #     318  87.2MB
    SPWN = b'spwn'  #     319 646.7KB
    SUBT = b'SUBT'  #       1   1.7KB
    TEXT = b'TEXT'  #     348 124.7KB
    TTXT = b'TTXT'  #     387 182.6KB
    TXAN = b'TXAN'  #     372  35.9KB
    TXST = b'TXST'  #      34   2.7MB
    UIAN = b'UIAN'  #       7   5.4MB
    UIAU = b'UIAU'  #       1     60B
    UIMP = b'UIMP'  #     245  13.5MB
    UITP = b'UITP'  #      12    320B
    VTEX = b'VTEX'  #      33   1.2MB
    WOFX = b'WOFX'  #      57   1.1KB
    WPSG = b'WPSG'  #     319  14.3KB


_cnt = 0
_cnt2 = 0
_map = {}

class RSCFFlag:
    Unk0  = 1 << 0
    Unk1  = 1 << 1
    Unk3  = 1 << 3
    Unk5  = 1 << 5
    Unk7  = 1 << 7
    Unk13 = 1 << 13
    Unk25 = 1 << 25

# contains only one resource
def readRSCF (f, offset, size):
    unk1  = f.u32()
    unk2  = f.u32()
    unk3  = f.u32()
    flags = f.u32()  # see RSCFFlag

    assert unk1 in [ 0, 1, 5, 7, 10 ], unk1
    assert unk2 in [ 0, 1, 2 ], unk2
    assert unk3 in [ 0, 2, 3, 6 ], unk3

    size = f.u32()
    path = f.alignedString(4)
    # data = f.read(size)

    f.skip(size)

    # path extensions:
    # <no_ext>
    # .5m
    # ._holy_lrg
    # ._holy_med
    # ._holy_sml
    # ._with_dress_pose_1
    # ._with_dress_pose_2
    # .bmp
    # .dds
    # .debug
    # .jpg
    # .pc
    # .png
    # .tga
    # .wav

def readASTS (f, offset, size):
    pass

def readPlainPackage (f):
    sinature = f.read(8)

    if sinature != Signature.Plain:
        raise Exception(f'Unexpected signature: { sinature }')

    while f.remaining() >= 4:
        sectionStart = f.tell()
        sectionType  = f.read(4)

        if sectionType == b'\x00\x00\x00\x00':
            break

        assert SectionType.hasValue(sectionType)

        sectionSize  = f.u32()          # size with sectionType and sectionSize
        contentSize  = sectionSize - 8  # size without sectionType and sectionSize
        contentStart = f.tell()
        sectionEnd   = contentStart + contentSize

        if sectionType == SectionType.RSCF:
            readRSCF(f, contentStart, contentSize)
        elif sectionType == SectionType.ASTS:
            readASTS(f, contentStart, contentSize)
        elif sectionType not in []:
            if f.getFilePath() and contentSize > 20:
                assert 0, (sectionType, f.getFilePath(), contentStart)            

        f.seek(sectionEnd)

def unpackPackage (pkgPath, unpackDir):    
    pkgPath = getAbsPath(pkgPath)

    if not isFile(pkgPath):
        raise Exception(f'File is not found: { pkgPath }')

    with openFile(pkgPath, readerType=ReaderType.FS) as f:
        sinature = f.read(8)

        if not Signature.hasValue(sinature):
            raise Exception('Unknown file signature')

        if sinature == Signature.Compressed:
            print('Decompressing...')

            pkgCompSize   = f.u32()
            pkgDecompSize = f.u32()

            pkgBuf = bytearray(pkgDecompSize)
            pkgEnd = f.tell() + pkgCompSize
            cursor  = 0

            while f.tell() < pkgEnd:
                blockCompSize   = f.u32()
                blockDecompSize = f.u32()

                block = f.read(blockCompSize)
                block = decompressData(block)

                assert len(block) == blockDecompSize

                pkgBuf[cursor:cursor + blockDecompSize] = block

                cursor += blockDecompSize

            assert f.tell() == pkgEnd

            pkgBuf = bytes(pkgBuf)

            readPlainPackage(MemReader(pkgBuf))            
        else:
            f.seek(0)

            readPlainPackage(f)

    # exit()

def unpackAll (gameDir, unpackDir):
    dbPath = joinPath(gameDir, PACKAGES_JSON_NAME)

    if not isFile(dbPath):
        collectPackages(gameDir)

    pkgPaths = readJson(dbPath)

    for pkgPath in pkgPaths:
        pkgPath = joinPath(gameDir, pkgPath)

        print(pkgPath)

        unpackPackage(pkgPath, unpackDir)

        print(' ')

def collectPackages (gameDir):
    print('Collecting packages...')

    packages = {}

    for filePath in iterFiles(gameDir, True):
        with openFile(filePath, readerType=ReaderType.FS) as f:
            data = f.read(8)

            if data.startswith(b'Asura'):
                print(filePath)

                packages[getRelPath(filePath, gameDir)] = True 

    dbPath = joinPath(gameDir, PACKAGES_JSON_NAME)

    writeJson(dbPath, list(packages.keys()))

def main ():
    # collectPackages(GAME_DIR)
    unpackAll(GAME_DIR, joinPath(GAME_DIR, '.unpacked'))
    # unpack(joinPath(GAME_DIR, 'Global.bix'), joinPath(GAME_DIR, '.unpacked'))
    # print(toJson(sorted(list(_map.keys()))))
    # print(formatSize(_cnt2), _cnt2)
    # print(formatSize(_cnt), _cnt)


if __name__ == '__main__':
    main()

'''
b'ENTI'    1845591    547.7MB
b'FAAN'     236108    604.3MB
b'CTEV'     234833     24.7MB
b'DLLN'     233380     39.5MB
b'RSCF'     199769     76.8GB
b'DLEV'     185346     22.5MB
b'CONA'     149048     15.8MB
b'CTAT'      91068      9.5MB
b'CTTR'      64438     10.5MB
b'CTAC'      62592     10.5MB
b'FXPT'      38614     42.6MB
b'FXST'      38614     14.5MB
b'SDSM'      36035      6.1MB
b'HSKN'      21529      1.0GB
b'HSBB'      21529      6.7MB
b'HSKE'      21529    252.3KB
b'HSKL'      19374      1.2MB
b'HCAN'      18607    560.5MB
b'SDEV'      13709      3.6MB
b'area'      13578     21.9MB
b'FXET'       9248      5.2MB
b'HMPT'       5412      3.1MB
b'CUTS'       3698     14.7MB
b'FXTT'       2065      1.8MB
b'HSND'       1299      2.0MB
b'DLET'       1120    122.4KB
b'FNFO'        529      8.3KB
b'CPAN'        427     63.2KB
b'TTXT'        387    182.6KB
b'RSFL'        379      2.5MB
b'TXAN'        372     35.9KB
b'TEXT'        348    124.7KB
b'SDPH'        319     35.2MB
b'AUDA'        319     15.2MB
b'NAV1'        319      9.0KB
b'WPSG'        319     14.3KB
b'spwn'        319    646.7KB
b'SMSG'        318     87.2MB
b'ATRT'        318      8.6MB
b'UIMP'        245     13.5MB
b'FACE'        236      1.0MB
b'DLLT'        168      7.2KB
b'BLUE'        161      4.9MB
b'ASTS'        129      4.5GB
b'HTXT'         99     12.9MB
b'FSX2'         91     21.5KB
b'MARE'         57     18.6MB
b'WOFX'         57      1.1KB
b'RAGD'         57    219.9KB
b'DYIN'         34    206.6KB
b'TXST'         34      2.7MB
b'PBRV'         33    684.1MB
b'IRTX'         33      3.1KB
b'VTEX'         33      1.2MB
b'INST'         33      1.6GB
b'SDDC'         33      1.1MB
b'PHEN'         33      2.0GB
b'EMOD'         33       740B
b'GISN'         33      5.6MB
b'CRNA'         31    206.7KB
b'ARNM'         31     63.4MB
b'RVBP'         24     12.2KB
b'PLUT'         24     69.0KB
b'REND'         24       288B
b'PSKY'         24     14.1KB
b'FOG '         24      4.3KB
b'OCMH'         24      2.7MB
b'FONT'         16      1.5MB
b'DLCR'         13       208B
b'DLCG'         12      6.8KB
b'UITP'         12       320B
b'FNTK'         10      4.7KB
b'UIAN'          7      5.4MB
b'HTPR'          6       184B
b'IKTM'          4      2.2KB
b'UIAU'          1        60B
b'META'          1        20B
b'AXBT'          1      2.6KB
b'AXBB'          1        16B
b'AMRO'          1        20B
b'APFO'          1        20B
b'AFSO'          1        12B
b'DCAL'          1     97.6KB
b'SUBT'          1      1.7KB
b'IPTP'          1        30B
b'ASSD'          1        12B
b'DFG2'          1        16B
b'AALG'          1     14.9MB
b'aire'          1     13.9KB
b'SDMX'          1    417.1KB
b'AAUT'          1     51.4KB
b'HRTF'          1     96.5KB
b'DYMC'          1    134.4KB
b'SDGS'          1        12B
b'ADSP'          1      1.0KB
'''