import os
import sys

from io import BytesIO

# pip install Pillow
from PIL import Image as PILImage

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../..')))

from bfw.utils import *



class RawImage:
    def __init__ (self):
        self.filePath   : str | None   = None
        self.channels   : int          = -1
        self.pxFormat   : str | None   = None
        self.width      : int          = -1
        self.height     : int          = -1
        self.resolution : int          = -1
        self.rawData    : bytes | None = None
        self.rawSize    : int          = -1
        self.hasAlpha   : bool         = False

        self._colors     : list[bytes] | None = None
        self._colorCount : int                = -1

    @classmethod
    def fromFile (cls, filePath : str) -> 'RawImage':
        if not isFile(filePath):
            raise OSError(f'File does not exist: { filePath }')

        image = PILImage.open(filePath)

        return cls._createImage(filePath, image)

    @classmethod
    def fromBuffer (cls, data : bytes) -> 'RawImage':
        image = PILImage.open(BytesIO(data))

        return cls._createImage(None, image)

    # @classmethod
    # def fromPixelData (cls, pxFormat : str, width : int, height : int, data : bytes) -> 'RawImage':
    #     image = PILImage.frombytes(pxFormat, (width, height), data) 

    #     return cls._createImage(None, image)

    @classmethod
    def _createImage (cls, filePath : str | None, image : PILImage) -> 'RawImage':
        resolution = image.width * image.height

        # print(image.mode)

        pxFormat = 'RGBA'
        image = image.convert(pxFormat)
        channels = 4

        extrema = image.getextrema()

        if extrema[3] == (255, 255):
            pxFormat = 'RGB'
            image = image.convert(pxFormat)
            channels = 3

        rawData = image.tobytes()
        rawSize = resolution * channels

        assert len(rawData) == rawSize

        rawImage = cls()

        rawImage.filePath   = filePath
        rawImage.channels   = channels
        rawImage.pxFormat   = pxFormat
        rawImage.width      = image.width
        rawImage.height     = image.height
        rawImage.resolution = resolution
        rawImage.rawData    = rawData
        rawImage.rawSize    = rawSize
        rawImage.hasAlpha   = channels == 4

        return rawImage

    def _collectColors (self):
        if self._colors is not None:
            return

        colors = {}

        rawData  = self.rawData
        channels = self.channels

        for i in range(0, self.rawSize, channels):
            color = rawData[i:i + channels]
            colors[color] = True

        self._colors = list(colors.keys())
        self._colorCount = len(self._colors)

    @property
    def colorCount (self) -> int:
        self._collectColors()

        return self._colorCount

    @property
    def colors (self) -> list[bytes] | None:
        self._collectColors()

        return self._colors

    def save (self, filePath):
        image = PILImage.frombytes(self.pxFormat, (self.width, self.height), self.rawData)

        image.save(filePath)



# noinspection PyUnusedLocal
def _test_ ():
    testDir1 = r'C:\Projects\_Data_Samples'

    for filePath in iterFiles(testDir1, includeExts=[ '.tga', '.bmp' ]):
        print(filePath)

        try:
            image   = RawImage.fromFile(filePath)
            rawData = readBin(filePath)
            image   = RawImage.fromBuffer(rawData)

            print(f'{ image.width }x{ image.height }:{ image.channels * 8 }, { image.colorCount } colors')

        except Exception as e:
            print(f'ERROR: { e }')

        print(' ')

        sys.exit()



__all__ = [
    'PILImage',
    'RawImage'
]



if __name__ == '__main__':
    _test_()
