# COD2 Font Extractor

from io import BytesIO
from sys import exit
from struct import unpack

from deps.utils import *
from deps.reader import *
from deps.writer import *

from PIL import Image as PILImage


# https://wiki.zeroy.com/index.php?title=Call_of_Duty_2:_Technical_Reference
# https://wiki.zeroy.com/index.php?title=Call_of_Duty:_Font_System



SCRIPT_DIR = getDirPath(getAbsPath(__file__))
GAME_DIR   = r'G:\Games\Call Of Duty 2'
RAW_DIR    = joinPath(GAME_DIR, 'raw')
FONTS_DIR  = joinPath(RAW_DIR, 'fonts')



class TGAColorMapType:
    Absent  = 0  # Color map is absent
    Present = 1  # Color map is present


class TGAImageType:
    NoData            = 0   # 0 no image data is present
    UncompColorMapped = 1   # 1 uncompressed color-mapped image
    UncompTrueColor   = 2   # 2 uncompressed true-color image
    UncompGrayscale   = 3   # 3 uncompressed black-and-white (grayscale) image
    RLEColorMapped    = 9   # 9 run-length encoded color-mapped image
    RLETrueColor      = 10  # 10 run-length encoded true-color image
    RLEGrayscale      = 11  # 11 run-length encoded black-and-white (grayscale) image



def tgaToRgba (filePath):
    print(filePath)

    with openFile(filePath) as f, BytesIO() as buff:
        # Header
        imageIdSize  = f.u8()  # 0-255 (after Image Specification)
        colorMapType = f.u8()  # see TGAColorMapType (after Image ID)
        imageType    = f.u8()  # see TGAImageType (after Color Map)

        assert imageIdSize == 0
        assert colorMapType == TGAColorMapType.Absent
        assert imageType == TGAImageType.RLETrueColor

        # Color map specification
        cmFirstIndex = f.u16()
        cmSize       = f.u16()
        cmEntrySize  = f.u8()

        assert cmFirstIndex == 0
        assert cmSize == 0
        assert cmEntrySize == 0

        # Image specification
        originX = f.u16()  # absolute coordinate of lower-left corner for displays where origin is at the lower left
        originY = f.u16()  # as for X-origin
        width   = f.u16()  # width in pixels
        height  = f.u16()  # height in pixels
        depth   = f.u8()   # bits per pixel
        bits    = f.u8()   # bits 3-0 give the alpha channel depth, bits 5-4 give pixel ordering

        alphaBits = bits & 0xF  # depends; "attribute bit count" in common
        pxOrder   = (bits >> 4) & 0x3

        print(alphaBits, pxOrder, bits)

        assert originX == originY == 0
        assert width and height
        assert depth % 8 == 0

        channelCount = depth // 8
        rawByteCount = width * height * channelCount

        # See "TGA 2.0", p.24
        while buff.getbuffer().nbytes < rawByteCount:
            byte = f.u8()

            isRLP    = bool(byte >> 7)    # True - Run-length packet; False - Raw Packet
            repCount = (byte & 0x7F) + 1  # When repCount == 1, isRLP == False

            if isRLP:
                pxValue = f.read(channelCount)
                assert len(pxValue) == channelCount
                buff.write(pxValue * repCount)
            else:
                pxValue = f.read(channelCount * repCount)
                assert len(pxValue) == (channelCount * repCount)
                buff.write(pxValue)

        assert buff.getbuffer().nbytes == rawByteCount
        assert f.tell() == f.getSize()

        return PILImage.frombuffer('RGBA', (width, height), buff.getvalue(), 'raw')


def rgbaToTga (image):
    width   = image.width
    height  = image.height
    pixels  = image.tobytes()
    pxCount = width * height

    assert len(pixels) % pxCount == 0

    channels = len(pixels) // pxCount
    depth    = channels * 8

    with BinWriter() as f:        
        # Header
        f.u8(0)
        f.u8(TGAColorMapType.Absent)
        f.u8(TGAImageType.RLETrueColor)

        # Color map specification
        f.u16(0)
        f.u16(0)
        f.u8(0)

        # Image specification
        f.u16(0)       # absolute coordinate of lower-left corner for displays where origin is at the lower left
        f.u16(0)       # as for X-origin
        f.u16(width)   # width in pixels
        f.u16(height)  # height in pixels
        f.u8(depth)    # bits per pixel
        f.u8(32)       # bits 3-0 give the alpha channel depth, bits 5-4 give pixel ordering

        for i in range(height):
            line = pixels[width * channels * i:width * channels * (i + 1)]

            start  = None
            prevPx = None
            reps   = [] 

            assert len(line) / width == channels

            for j in range(width):
                px = line[channels * j:channels * (j + 1)]
                isLastPx = j == (width - 1)

                if prevPx == px and start is None:
                    start = j - 1

                if isLastPx and prevPx == px and start is not None:
                    reps.append((start, j + 1))

                if prevPx and prevPx != px and start is not None:
                    reps.append((start, j))
                    start = None

                prevPx = px

            print(reps)
            # exit(0)

        # f.save(joinPath(FONTS_DIR, '_tmp.bin'))

        print(f.getSize())



def parseFont (filePath):
    print(filePath)

    with openFile(filePath) as f:
        fontPathOffset    = f.i32()
        fontSize          = f.i32()
        recordCount       = f.i32()
        fontMatPathOffset = f.i32()

        for i in range(recordCount):
            charCode    = f.u16()
            charSpacing = f.u8(3)
            charSize    = f.u8(2)
            _zero       = f.u8()
            charRect    = f.f32(4)

            assert _zero == 0

        f.seek(fontPathOffset)

        fontPath = f.string()

        f.seek(fontMatPathOffset)

        fontMatPath = f.string()
        fontMatPath = getAbsPath(joinPath(RAW_DIR, fontMatPath + '.tga'))

        image = tgaToRgba(fontMatPath)

        rgbaToTga(image)

        # image.save(getAbsPath(joinPath(RAW_DIR, replaceExt(fontMatPath, '.png'))))



def scanFonts ():
    for filePath in iterFiles(FONTS_DIR, False, includeExts=[ '' ]):
        parseFont(filePath)
        print(' ')



if __name__ == '__main__':
    scanFonts()