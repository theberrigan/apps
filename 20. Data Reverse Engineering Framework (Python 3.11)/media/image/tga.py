import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../..')))

from bfw.types.enums import Enum2
from bfw.utils import *
from bfw.reader import *


'''
- .tga, .tpic, .vda, .icb, .vst
- TGA 2.0 is a wrapper around TGA 1.0 with backward compat.
- Targa 16, 24, 32; VBA, ICB, Targa M8
- All numbers are little-endian
- Byte  = u8
- Short = u16
- Long  = u32

Terms:
- Pseudo-Color - single index into color map: i => CM[i] => (R, G, B)
- True-Color   - non-indexed color:           (R, G, B) => (R, G, B)
- Direct-Color - one index per one channel:   (ir, ig, ib) => (CM[ir], CM[ig], CM[ib]) => (R, G, B)

TGA v1:
- Header containing information on the image data and palette
- Optional image identification field
- Optional color map
- Bitmap data

TGA v2 appends some data at the end of v1:
- Optional developer directory, which may contain a variable number of tags pointing to pieces of information stored in the TGA file
- Optional developer area
- Optional extension area, which contains information typically found in the header of a bitmap file
- Optional color-correction table
- Optional postage-stamp image
- Optional scan-line table
- Footer, which points to the developer and extension areas and identifies the TGA file as a new TGA format file

- Colormapped images (pseudocolor) use a palette. 
- Truecolor images do not use a palette and store their pixel data directly in the image data,
  although truecolor TGA image files may contain a palette that is used to store the color information from a paint program. 

Areas:
+---+----+----+---------------------+
| # | V1 | V2 | Name                |
+---+----+----+---------------------+
| 1 | +  | +  | TGA File Header     |
| 2 | +  | +  | Image/ColorMap Data |
| 3 | -  | ~  | Developer Area      |
| 4 | -  | ~  | Extension Area      |
| 5 | -  | ~  | TGA File Footer     |
+---+----+----+---------------------+

TGA FILE HEADER --------------------------------------------------------------------------------------------------------
Field 1   | ID Length               | 1  | size of Field 6 (0 - absent)
Field 2   | Color Map Type          | 1  | see TGAColorMapType; [0-128) - reserved, [128-255] - free for devs; [1]
Field 3   | Image Type              | 1  | see TGAImageType; [0-128) - reserved, [128-255] - free for devs
Field 4   | Color Map Specification | 5  | (Color Map Type == 0) => (00 00 00 00 00)
Field 4.1 | First Entry Index       | 2  | index of the first color map entry
Field 4.2 | Color Map Length        | 2  | total number of color map entries included
Field 4.3 | Color Map Entry Size    | 1  | establishes the number of bits per entry
Field 5   | Image Specification     | 10 | describes the image screen location, size and pixel depth
Field 5.1 | X-origin of Image       | 2  | lower-left img corner X-offset relative to lower-left display corner
Field 5.2 | Y-origin of Image       | 2  | lower-left img corner Y-offset relative to lower-left display corner
Field 5.3 | Image Width             | 2  |
Field 5.4 | Image Height            | 2  |
Field 5.5 | Pixel Depth             | 1  | BPP, includes Attribute or Alpha channel bits (8, 16, 24, 32 or any value)
Field 5.6 | Image Descriptor        | 1  | bits 3-0 number of attr bits per pixel (see Field 24); bits 5-4 pixel order 
IMAGE/COLOR MAP DATA ---------------------------------------------------------------------------------------------------
Field 6~  | Image ID                | F1 | identifying information about the image
Field 7~  | Color Map Data          | >> | color map data (LUT data); if F2 == 0, no this data; size: F4.3 * F4.2       ???
Field 8~  | Image Data              | >> | pixel data, size depends on type - Pseudo-Color, True-Color or Direct-Color  ???
DEVELOPER AREA ---------------------------------------------------------------------------------------------------------
---
[1] - For True-Color image just skip Color Map data even if Color Map Type != 0

'''


class TGACMapType (Enum2):
    Absent  = 0  # Color map is absent
    Present = 1  # Color map is present


class TGAImageType (Enum2):  # Description                                          | Palette | Encoding
    NoData            = 0    # no image data is present                             | -       | -
    UncompColorMapped = 1    # uncompressed color-mapped (with palette) image       | +       | -
    UncompTrueColor   = 2    # uncompressed true-color image                        | -       | -
    UncompGrayscale   = 3    # uncompressed black-and-white (grayscale) image       | -       | -
    RLEColorMapped    = 9    # run-length encoded color-mapped (with palette) image | +       | RLE
    RLETrueColor      = 10   # run-length encoded true-color image                  | -       | RLE
    RLEGrayscale      = 11   # run-length encoded black-and-white (grayscale) image | -       | RLE


class TGA:
    def __init__ (self):
        # Header
        self.imageIdSize  : int | None = None  # size of Image ID (after header (Image Specification)) (0-255, 0 - absent)
        self.cmType       : int | None = None  # see TGACMapType (after Image ID) (0-127 - reserved, 128-255 - for devs)
        self.imageType    : int | None = None  # see TGAImageType (after Color Map) (0-127 - reserved, 128-255 - for devs)

        # Color map specification
        # If cmType == TGACMapType.Absent, then next 3 fields are zeros
        self.cmFirstIndex : int | None = None  # offset of first entry in CM
        self.cmEntryCount : int | None = None  # number of CM entries
        self.cmEntrySize  : int | None = None  # size of entry of CM (!= image data px depth) (typically 15, 16, 24, 32)

        # Image specification
        self.originX      : int | None = None  # absolute coordinate of lower-left corner for displays where origin is at the lower left
        self.originY      : int | None = None  # as for X-origin
        self.width        : int | None = None  # width in pixels
        self.height       : int | None = None  # height in pixels
        self.depth        : int | None = None  # bits per pixel, including attribute bits, if any (typically 8, 16, 24, 32)
        self.alphaBits    : int | None = None  # depends; "attribute bit count" in common; only in pixels for the 16/32-bit flavors; called alpha channel, overlay, or interrupt bits
        self.pxOrder      : int | None = None  # origin corner (0 - lower-left); originX and originY are relative to it

        # -------------------------------

        # Image/CM data
        self.imageId : str | None  = None  # see self.imageIdSize (NT-string or absent)
        self.cm      : list | None = None  # present only if self.cmType == TGACMapType.Present

    @classmethod
    def fromFile (cls, filePath):
        if not isFile(filePath):
            raise OSError(f'File does not exist: { filePath }')

        with openFile(filePath) as f:
            return cls._read(f)

    @classmethod
    def fromBuffer (cls, data, filePath=None):
        with MemReader(data, filePath=filePath) as f:
            return cls._read(f)

    @classmethod
    def _read (cls, f):
        image = cls()

        cls._readHeader(f, image)
        cls._readData(f, image)

        return image

    @classmethod
    def _readHeader (cls, f, image):
        image.imageIdSize  = f.u8()
        image.cmType       = f.u8()
        image.imageType    = f.u8()
        image.cmFirstIndex = f.u16()
        image.cmEntryCount = f.u16()
        image.cmEntrySize  = f.u8()
        image.originX      = f.u16()
        image.originY      = f.u16()
        image.width        = f.u16()
        image.height       = f.u16()
        image.depth        = f.u8()
        bits               = f.u8()
        image.alphaBits    = bits & 15
        image.pxOrder      = (bits >> 4) & 3

        return image

    @classmethod
    def _readData (cls, f, image):
        if image.imageIdSize:
            image.imageId = f.string(size=image.imageIdSize)
        else:
            image.imageId = None

        if image.cmType == TGACMapType.Present:
            image.cm = f.read(image.cmEntrySize * image.cmEntryCount)
            print('HAS CM', image.cmEntrySize, image.cmEntryCount)
        else:
            image.cm = None

        return image





# noinspection PyUnusedLocal
def _test_ ():
    testDir1 = r'C:\Projects\_Data_Samples'
    testDir2 = r"G:\Games\Call Of Duty Collector's Edition\Main\.raw\gfx\reticle"

    for filePath in iterFiles(testDir2, includeExts=[ '.tga' ]):
        print(filePath)

        try:
            image = TGA.fromFile(filePath)
            image = TGA.fromBuffer(readBin(filePath))

            print(toJson(image))

            # print(f'{ image.width }x{ image.height }:{ image.channels * 8 }, { image.colorCount } colors')

        except Exception as e:
            print(f'ERROR: { e }')

        print(' ')

        # sys.exit()



__all__ = [
    'TGA'
]



if __name__ == '__main__':
    _test_()
