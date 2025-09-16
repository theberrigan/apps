import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../..')))

from bfw.types.enums import Enum2
from bfw.utils import *
from bfw.reader import *



MAX_U8 = 255
MASK_5 = 31
MASK_6 = 63
RATIO_8_TO_5 = MAX_U8 / MASK_5
RATIO_8_TO_6 = MAX_U8 / MASK_6



def convertRGB565ToRGB8 (num):
    return [
        round(((num >> 11) & MASK_5) * RATIO_8_TO_5),
        round(((num >> 5) & MASK_6) * RATIO_8_TO_6),
        round((num & MASK_5) * RATIO_8_TO_5)
    ]

def lerp (a, b, r):
    return a * (1 - r) + b * r

def interpColors (color1, color2, isDXT1):
    isLTE = isDXT1 and color1 <= color2

    color1 = convertRGB565ToRGB8(color1)
    color2 = convertRGB565ToRGB8(color2)
    colors = [ *color1, 255, *color2, 255, 0, 0, 0, 0, 0, 0, 0, 0 ]

    if isLTE:
        colors[8]  = round((color1[0] + color2[0]) / 2)
        colors[9]  = round((color1[1] + color2[1]) / 2)
        colors[10] = round((color1[2] + color2[2]) / 2)
        colors[11] = 255
    else:
        colors[8]  = round(lerp(color1[0], color2[0], 1 / 3))
        colors[9]  = round(lerp(color1[1], color2[1], 1 / 3))
        colors[10] = round(lerp(color1[2], color2[2], 1 / 3))
        colors[11] = 255
        colors[12] = round(lerp(color1[0], color2[0], 2 / 3))
        colors[13] = round(lerp(color1[1], color2[1], 2 / 3))
        colors[14] = round(lerp(color1[2], color2[2], 2 / 3))
        colors[15] = 255

    return colors

# C:\Projects\DataCoding\2\DXT\dds-dxt.js
# BC1
class DXT1:
    def __init__ (self):
        pass

    @classmethod
    def toRGBA (cls, data, width, height):
        with MemReader(data) as f:
            return cls._read(f, width, height)

    @classmethod
    def _read (cls, f, width, height):
        channels = 4
        rgbaSize = width * height * channels
        rgba     = bytearray(rgbaSize)
        wQuart   = width // 4
        hQuart   = height // 4

        for h in range(hQuart):
            for w in range(wQuart):
                color1  = f.u16()
                color2  = f.u16()
                indices = f.u32()
                colors  = interpColors(color1, color2, True)

                for y in range(4):
                    for x in range(4):
                        pxIndex    = (3 - x) + (y * 4)
                        rgbaIndex  = (h * 4 + 3 - y) * width * 4 + (w * 4 + x) * 4
                        colorIndex = (indices >> (2 * (15 - pxIndex))) & 3

                        rgba[rgbaIndex + 0] = colors[colorIndex * 4 + 0]
                        rgba[rgbaIndex + 1] = colors[colorIndex * 4 + 1]
                        rgba[rgbaIndex + 2] = colors[colorIndex * 4 + 2]
                        rgba[rgbaIndex + 3] = colors[colorIndex * 4 + 3]

        return rgba



def _test_ ():
    pass



__all__ = [
    'DXT1'
]



if __name__ == '__main__':
    _test_()
