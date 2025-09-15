from math import floor
from typing import Callable, Optional

from ...common import bfw
from ...common.consts import *

from .consts import *
from .types import *

from bfw.utils import *
from bfw.reader import *
from bfw.types.enums import Enum



class Color:
    def __init__ (self, r : int = None, g : int = None, b : int = None):
        self.r = r
        self.g = g
        self.b = b


# TODO: implement compression
# TODO: implement DDS
# https://github.com/LordVonAdel/dxtn
class DXT:
    _alphaLookupBuffer = bytearray(8)

    @classmethod
    def _decompress (cls, data : bytes | bytearray, width : int, height : int, blockSize : int, method : Callable) -> bytearray:
        if width % DXT_BLOCK_WIDTH != 0:
            raise Exception(f'Texture width must be divisible by { DXT_BLOCK_WIDTH }')

        if height % DXT_BLOCK_HEIGHT != 0:
            raise Exception(f'Texture height must be divisible by { DXT_BLOCK_HEIGHT }')

        if width < DXT_BLOCK_WIDTH or height < DXT_BLOCK_HEIGHT:
            raise Exception('Texture size is too small')

        w = width // DXT_BLOCK_WIDTH
        h = height // DXT_BLOCK_HEIGHT
        blockNumber = w * h

        if blockNumber * blockSize != len(data):
            raise Exception('Data size is not equal to dimension')

        out = bytearray(width * height * 4)
        blockBuffer = bytearray(DXT_RGBA_BLOCK_SIZE)

        for i in range(blockNumber):
            decompressed = method(data[i * blockSize:(i + 1) * blockSize], blockBuffer)
            pixelX = (i % w) * 4
            pixelY = floor(i / w) * 4

            j = 0

            for y in range(4):
                for x in range(4):
                    px = x + pixelX
                    py = y + pixelY

                    out[px * 4 + py * 4 * width + 0] = decompressed[j + 0]
                    out[px * 4 + py * 4 * width + 1] = decompressed[j + 1]
                    out[px * 4 + py * 4 * width + 2] = decompressed[j + 2]
                    out[px * 4 + py * 4 * width + 3] = decompressed[j + 3]

                    j += 4

        return out

    @classmethod
    def decompressDXT1 (cls, data : bytes | bytearray, width : int, height : int) -> bytearray:
        return cls._decompress(data, width, height, DXT1_BLOCK_SIZE, cls._decompressDXT1Block)

    @classmethod
    def decompressDXT3 (cls, data : bytes | bytearray, width : int, height : int) -> bytearray:
        return cls._decompress(data, width, height, DXT3_BLOCK_SIZE, cls._decompressDXT3Block)

    @classmethod
    def decompressDXT5 (cls, data : bytes | bytearray, width : int, height : int) -> bytearray:
        return cls._decompress(data, width, height, DXT5_BLOCK_SIZE, cls._decompressDXT5Block)

    @classmethod
    def _decompressDXT1Block (cls, data : bytes | bytearray, out : Optional[bytearray]) -> bytearray:
        if len(data) != DXT1_BLOCK_SIZE:
            raise Exception('Data size is not equal to block size')

        cVal0 = (data[1] << 8) | data[0]
        cVal1 = (data[3] << 8) | data[2]

        lookup = cls._generateDXT1Lookup(cVal0, cVal1)

        if out is None:
            out = bytearray(DXT_RGBA_BLOCK_SIZE)

        for i in range(16):
            bitOffset = i * 2
            byte = 4 + floor(bitOffset / 8)
            bits = (data[byte] >> bitOffset % 8) & 3

            out[i * 4 + 0] = lookup[bits * 4 + 0]
            out[i * 4 + 1] = lookup[bits * 4 + 1]
            out[i * 4 + 2] = lookup[bits * 4 + 2]
            out[i * 4 + 3] = lookup[bits * 4 + 3]

        return out

    @classmethod
    def _generateDXT1Lookup (cls, colorValue0, colorValue1, out : Optional[bytearray] = None) -> bytearray:
        color0 : Color = cls._decomposeRGB565(colorValue0)
        color1 : Color = cls._decomposeRGB565(colorValue1)

        if out is None:
            out = bytearray(16)

        # Non-transparent mode
        if colorValue0 > colorValue1:
            out[0] = floor(color0.r * 255)
            out[1] = floor(color0.g * 255)
            out[2] = floor(color0.b * 255)
            out[3] = 255

            out[4] = floor(color1.r * 255)
            out[5] = floor(color1.g * 255)
            out[6] = floor(color1.b * 255)
            out[7] = 255

            out[8]  = floor((color0.r * 2 / 3 + color1.r * 1 / 3) * 255)
            out[9]  = floor((color0.g * 2 / 3 + color1.g * 1 / 3) * 255)
            out[10] = floor((color0.b * 2 / 3 + color1.b * 1 / 3) * 255)
            out[11] = 255

            out[12] = floor((color0.r * 1 / 3 + color1.r * 2 / 3) * 255)
            out[13] = floor((color0.g * 1 / 3 + color1.g * 2 / 3) * 255)
            out[14] = floor((color0.b * 1 / 3 + color1.b * 2 / 3) * 255)
            out[15] = 255

        # Transparent mode
        else:
            out[0] = floor(color0.r * 255)
            out[1] = floor(color0.g * 255)
            out[2] = floor(color0.b * 255)
            out[3] = 255

            out[4] = floor((color0.r * 1 / 2 + color1.r * 1 / 2) * 255)
            out[5] = floor((color0.g * 1 / 2 + color1.g * 1 / 2) * 255)
            out[6] = floor((color0.b * 1 / 2 + color1.b * 1 / 2) * 255)
            out[7] = 255

            out[8]  = floor(color1.r * 255)
            out[9]  = floor(color1.g * 255)
            out[10] = floor(color1.b * 255)
            out[11] = 255

            out[12] = 0
            out[13] = 0
            out[14] = 0
            out[15] = 0

        return out

    @classmethod
    def _decompressDXT3Block (cls, data : bytes | bytearray, out : Optional[bytearray]) -> bytearray:
        if out is None:
            out = bytearray(DXT_RGBA_BLOCK_SIZE)

        cls._decompressDXT1Block(data[8:16], out)

        for i in range(8):
            out[i * 8 + 3] = (data[i] & 0x0F) << 4
            out[i * 8 + 7] = (data[i] & 0xF0)

        return out

    @classmethod
    def _decompressDXT5Block (cls, data : bytes | bytearray, out : Optional[bytearray]) -> bytearray:
        if out is None:
            out = bytearray(DXT_RGBA_BLOCK_SIZE)

        cls._decompressDXT1Block(data[8:16], out)

        alpha0 = data[0]
        alpha1 = data[1]

        alphaLookup = cls._generateDXT5AlphaLookup(alpha0, alpha1, cls._alphaLookupBuffer)

        out[31] = alphaLookup[(data[4] & 0b11100000) >> 5]
        out[27] = alphaLookup[(data[4] & 0b00011100) >> 2]
        out[23] = alphaLookup[((data[4] & 0b00000011) << 1) + ((data[3] & 0b10000000) >> 7)]
        out[19] = alphaLookup[(data[3] & 0b01110000) >> 4]
        out[15] = alphaLookup[(data[3] & 0b00001110) >> 1]
        out[11] = alphaLookup[((data[3] & 0b00000001) << 2) + ((data[2] & 0b11000000) >> 6)]
        out[7]  = alphaLookup[(data[2] & 0b00111000) >> 3]
        out[3]  = alphaLookup[(data[2] & 0b00000111) >> 0]

        out[63] = alphaLookup[(data[7] & 0b11100000) >> 5]
        out[59] = alphaLookup[(data[7] & 0b00011100) >> 2]
        out[55] = alphaLookup[((data[7] & 0b00000011) << 1) + ((data[6] & 0b10000000) >> 7)]
        out[51] = alphaLookup[(data[6] & 0b01110000) >> 4]
        out[47] = alphaLookup[(data[6] & 0b00001110) >> 1]
        out[43] = alphaLookup[((data[6] & 0b00000001) << 2) + ((data[5] & 0b11000000) >> 6)]
        out[39] = alphaLookup[(data[5] & 0b00111000) >> 3]
        out[35] = alphaLookup[(data[5] & 0b00000111) >> 0]

        return out

    @classmethod
    def _generateDXT5AlphaLookup (cls, alpha0 : int, alpha1 : int, out : Optional[bytearray]) -> bytearray:
        if out is None:
            out = bytearray(8)

        out[0] = alpha0
        out[1] = alpha1

        if alpha0 > alpha1:
            out[2] = round((6 * alpha0 + 1 * alpha1) / 7)
            out[3] = round((5 * alpha0 + 2 * alpha1) / 7)
            out[4] = round((4 * alpha0 + 3 * alpha1) / 7)
            out[5] = round((3 * alpha0 + 4 * alpha1) / 7)
            out[6] = round((2 * alpha0 + 5 * alpha1) / 7)
            out[7] = round((1 * alpha0 + 6 * alpha1) / 7)
        else:
            out[2] = round((4 * alpha0 + 1 * alpha1) / 5)
            out[3] = round((3 * alpha0 + 2 * alpha1) / 5)
            out[4] = round((2 * alpha0 + 3 * alpha1) / 5)
            out[5] = round((1 * alpha0 + 4 * alpha1) / 5)
            out[6] = 0
            out[7] = 255

        return out

    @classmethod
    def _decomposeRGB565 (cls, color : int) -> Color:
        out = Color()

        out.r = ((color & 0b11111000_00000000) >> 8) / 0xFF
        out.g = ((color & 0b00000111_11100000) >> 3) / 0xFF
        out.b = ((color & 0b00000000_00011111) << 3) / 0xFF

        return out



def _test_ ():
    pass



__all__ = [
    'DXT',

    '_test_',
]



if __name__ == '__main__':
    _test_()
