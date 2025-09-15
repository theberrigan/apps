# https://gibberlings3.github.io/iesdp/file_formats/ie_formats/bmp.htm
# http://www.ue.eti.pg.gda.pl/fpgalab/zadania.spartan3/zad_vga_struktura_pliku_bmp_en.html
# https://en.wikipedia.org/wiki/BMP_file_format
# https://docs.fileformat.com/image/bmp/
# https://www.ece.ualberta.ca/~elliott/ee552/studentAppNotes/2003_w/misc/bmp_file_format/bmp_file_format.htm
# https://learn.microsoft.com/en-us/windows/win32/api/wingdi/ns-wingdi-bitmapinfoheader
# https://www.fileformat.info/format/bmp/egff.htm
# https://learn.microsoft.com/en-us/windows/win32/gdi/bitmap-storage

import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../..'))) 

from bfw.utils import *
from bfw.reader import *

from bfw.fs.scan.collecting import GLOBAL_SAMPLES_DIR, collectSamplesInFile, iterSamplesInFile



BMP_SAMPLES_DIR  = joinPath(GLOBAL_SAMPLES_DIR, 'bmp')
BMP_SAMPLES_PATH = joinPath(GLOBAL_SAMPLES_DIR, 'bmp.bin')
BMP_EXT = '.bmp'
BMP_SIGNATURE = b'BM'



class BMPCompressionType:
    RGB  = 0  # Uncompressed RGB
    RLE8 = 1
    RLE4 = 2
    BF   = 3  # Uncompressed RGB with color masks. Valid for 16-bpp and 32-bpp bitmaps.

    @classmethod
    def isSupported (cls, compType):
        return compType in [
            cls.RGB,
            cls.RLE8,
            cls.RLE4,
            cls.BF
        ]



# BITMAPFILEHEADER
# https://learn.microsoft.com/en-us/windows/win32/api/wingdi/ns-wingdi-bitmapfileheader
def readHeader (f, bmp):
    signature = f.read(2)

    if signature != BMP_SIGNATURE:
        raise Exception('Unknown file signature')

    bmp.fileSize = f.u32()

    f.skip(4)  # Reserved

    bmp.bitmapOffset = f.u32()    


# WIN2XBITMAPHEADER (v2 | 12 bytes InfoHeader | Windows 2.x)
# https://www.fileformat.info/format/bmp/egff.htm
def readInfoHeaderV2 (f, bmp):
    bmp.width      = f.i32()  # SHORT Width  - Image width in pixels
    bmp.height     = f.i32()  # SHORT Height - Image height in pixels
    bmp.planeCount = f.u16()  # WORD  Planes - Number of color planes
    bmp.bitDepth   = f.u16()  # WORD BitsPerPixel - Number of bits per pixel

    bmp.version = 2


# BITMAPINFOHEADER (v3 | 40 bytes InfoHeader | Windows 3.x/NT)
# https://learn.microsoft.com/en-us/windows/win32/api/wingdi/ns-wingdi-bitmapinfoheader
def readInfoHeaderV3 (f, bmp):
    readInfoHeaderV2(f, bmp)  # must be first

    bmp.compType = f.u32()  # DWORD Compression - Compression methods used

    bmp.bitmapSize    = f.u32()  # DWORD SizeOfBitmap    - Size of bitmap in bytes
    bmp.ppmResX       = f.i32()  # LONG  HorzResolution  - Horizontal resolution in pixels per meter
    bmp.ppmResY       = f.i32()  # LONG  VertResolution  - Vertical resolution in pixels per meter
    bmp.colorCount    = f.u32()  # DWORD ColorsUsed      - Number of colors in the image
    bmp.minColorCount = f.u32()  # DWORD ColorsImportant - Minimum number of important colors

    bmp.version = 3  # must be after readInfoHeaderV2


# BITMAPV4HEADER (v4 | 108 bytes InfoHeader | Windows 95)
# https://learn.microsoft.com/en-us/windows/win32/api/wingdi/ns-wingdi-bitmapv4header
def readInfoHeaderV4 (f, bmp):
    readInfoHeaderV3(f, bmp)  # must be first

    bmp.maskR  = f.u32()  # DWORD RedMask    - Mask identifying bits of red component
    bmp.maskG  = f.u32()  # DWORD GreenMask  - Mask identifying bits of green component
    bmp.maskB  = f.u32()  # DWORD BlueMask   - Mask identifying bits of blue component
    bmp.maskA  = f.u32()  # DWORD AlphaMask  - Mask identifying bits of alpha component
    bmp.csType = f.u32()  # DWORD CSType     - Color space type
    bmp.rX     = f.i32()  # LONG  RedX       - X coordinate of red endpoint
    bmp.rY     = f.i32()  # LONG  RedY       - Y coordinate of red endpoint
    bmp.rZ     = f.i32()  # LONG  RedZ       - Z coordinate of red endpoint
    bmp.gX     = f.i32()  # LONG  GreenX     - X coordinate of green endpoint
    bmp.gY     = f.i32()  # LONG  GreenY     - Y coordinate of green endpoint
    bmp.gZ     = f.i32()  # LONG  GreenZ     - Z coordinate of green endpoint
    bmp.bX     = f.i32()  # LONG  BlueX      - X coordinate of blue endpoint
    bmp.bY     = f.i32()  # LONG  BlueY      - Y coordinate of blue endpoint
    bmp.bZ     = f.i32()  # LONG  BlueZ      - Z coordinate of blue endpoint
    bmp.gammaR = f.u32()  # DWORD GammaRed   - Gamma red coordinate scale value
    bmp.gammaG = f.u32()  # DWORD GammaGreen - Gamma green coordinate scale value
    bmp.gammaB = f.u32()  # DWORD GammaBlue  - Gamma blue coordinate scale value

    bmp.version = 4  # must be after readInfoHeaderV3


# BITMAPV5HEADER (v5 | 124 bytes InfoHeader | Windows 98)
# https://learn.microsoft.com/en-us/windows/win32/api/wingdi/ns-wingdi-bitmapv5header
def readInfoHeaderV5 (f, bmp):
    readInfoHeaderV4(f, bmp)  # must be first

    bmp.intent        = f.u32()  # DWORD Intent      - Rendering intent for bitmap
    bmp.profileOffset = f.u32()  # DWORD ProfileData - Offset from the beginning of the BITMAPV5HEADER structure to the start of the profile data
    bmp.profileSize   = f.u32()  # DWORD ProfileSize - Size of embedded profile data

    f.skip(4)  # DWORD Reserved

    bmp.version = 5  # must be after readInfoHeaderV4

def readInfoHeader (f, bmp):
    infoSize = f.u32()

    match infoSize:
        case 12:
            readInfoHeaderV2(f, bmp)
        case 40:
            readInfoHeaderV3(f, bmp)
        case 108:
            readInfoHeaderV4(f, bmp)
        case 124:
            readInfoHeaderV5(f, bmp)
        case _:
            raise Exception(f'Unknown size of InfoHeader: { infoSize }')

class BMP:
    def __init__ (self):
        # from header
        self.fileSize      = None  # equals getFileSize()
        self.bitmapOffset  = None

        # from info header
        self.version       = None  # according to size of info header
        # since v2
        self.width         = None
        self.height        = None
        self.planeCount    = None
        self.bitDepth      = None
        # since v3
        self.compType      = None
        self.bitmapSize    = None
        self.ppmResX       = None
        self.ppmResY       = None
        self.colorCount    = None
        self.minColorCount = None
        # since v4
        self.maskR         = None
        self.maskG         = None
        self.maskB         = None
        self.maskA         = None
        self.csType        = None
        self.rX            = None
        self.rY            = None
        self.rZ            = None
        self.gX            = None
        self.gY            = None
        self.gZ            = None
        self.bX            = None
        self.bY            = None
        self.bZ            = None
        self.gammaR        = None
        self.gammaG        = None
        self.gammaB        = None
        # since v5
        self.intent        = None
        self.profileOffset = None
        self.profileSize   = None

    @classmethod
    def fromFile (cls, bmpPath):
        if not isFile(bmpPath):
            raise Exception(f'File does not exist: { bmpPath }')

        with openFile(bmpPath) as f:
            cls._read(f)

    @classmethod
    def fromBuffer (cls, data):
        with MemReader(data) as f:
            cls._read(f)

    # https://learn.microsoft.com/en-us/windows/win32/gdi/bitmap-storage
    @classmethod
    def _read (cls, f):
        bmp = BMP()

        readHeader(f, bmp)
        readInfoHeader(f, bmp)

        print(bmp.version)

        if bmp.planeCount != 1:
            raise Exception(f'InfoHeader.planeCount must be 1, but { planeCount } in the file')

        assert BMPCompressionType.isSupported(bmp.compType)



################################################
####               AUXILIARY                ####
################################################

_BLACKLISTED = [
    filePath.lower() for filePath in [
        r'C:\Program Files (x86)\Microsoft DirectX SDK\Samples\C++\Misc\InstallOnDemand\Loading.bmp',
        r'C:\Projects\_Shared\Qt\6.2.2\Src\qtbase\tests\auto\gui\image\qimagereader\images\corrupt_clut.bmp',
        r'C:\Projects\_Shared\Qt\6.2.2\Src\qtwebengine\src\3rdparty\chromium\third_party\blink\renderer\platform\testing\data\gracehopper.bmp',
        r'C:\Projects\_Shared\Qt\6.2.2\Src\qtwebengine\src\3rdparty\chromium\third_party\skia\resources\invalid_images\b33651913.bmp',
        r'C:\Projects\_Shared\Qt\6.2.2\Src\qtwebengine\src\3rdparty\chromium\third_party\skia\resources\invalid_images\osfuzz6288.bmp',
        r'C:\Projects\_Sources\Chromium\third_party\blink\web_tests\images\resources\crbug752898.bmp',
        r'C:\Projects\_Sources\GameEngines\SourceEngine2013_5\Content\hl2\resource\game-icon.bmp',  # WINDOWS OPENS, BUT IH SIZE IS 56!!!
        r'G:\Steam\steamapps\common\Counter-Strike Source\cstrike\resource\game-icon.bmp',          # WINDOWS OPENS, BUT IH SIZE IS 56!!!
    ]
]

def _collectSamples ():
    def check (filePath, fileSize, fileCRC):
        print(filePath, fileSize, fileCRC)

    collectSamplesInFile(
        rootDirs     = getDrives(True),
        destPath     = BMP_SAMPLES_PATH,
        exts         = [ BMP_EXT ], 
        isRecursive  = True, 
        minSize      = 1, 
        maxSize      = None,
        noDups       = True,
        checkFn      = check
    )

def _checkBMP (filePath):
    if filePath.lower() in _BLACKLISTED:
        return False

    return readBin(filePath, len(BMP_SIGNATURE)) == BMP_SIGNATURE

def _parseSamplesFromFile (filePath=BMP_SAMPLES_PATH):
    for bmpPath in iterSamplesInFile(filePath):
        if _checkBMP(bmpPath):
            print(bmpPath)        
            BMP.fromFile(bmpPath)
            print(' ')

def _parseSamplesFromDir (rootDir=BMP_SAMPLES_DIR):
    for bmpPath in iterFiles(rootDir, True, [ BMP_EXT ]):
        if _checkBMP(bmpPath):
            print(bmpPath)
            BMP.fromFile(bmpPath)
            print(' ')


################################################
####                TESTING                 ####
################################################

def _test_ ():
    pass


################################################
####                 EXPORT                 ####
################################################

__all__ = [
    'BMP'
]



if __name__ == '__main__':
    # _test_()
    # _collectSamples()
    _parseSamplesFromFile()
    # _parseSamplesFromDir()

'''
BRK_ - broken
UNK_ - unknown
AMN_ - animated
STG_ - smth strange

.ico
.cur
.png
.bmp
.jpg
.jpeg
.gif
.webp
.tiff
.tga
.dds

'''