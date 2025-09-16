from io import BytesIO

# pip install Pillow
from PIL import Image as PILImage

from ...common import bfw

from bfw.utils import *



class RAWImage:
    def __init__ (self):
        self.filePath   : str | None   = None
        self.channels   : int          = -1
        self.width      : int          = -1
        self.height     : int          = -1
        self.resolution : int          = -1
        self.rawData    : bytes | None = None
        self.rawSize    : int          = -1
        self.hasAlpha   : bool         = False

        self._colors     : list[bytes] | None = None
        self._colorCount : int                = -1

    @classmethod
    def fromFile (cls, filePath : str) -> 'RAWImage':
        if not isFile(filePath):
            raise OSError(f'File does not exist: { filePath }')

        image = PILImage.open(filePath)

        return cls._convertImage(filePath, image)

    @classmethod
    def fromBuffer (cls, rawData : bytes) -> 'RAWImage':
        image = PILImage.open(BytesIO(rawData))

        return cls._convertImage(None, image)

    @staticmethod
    def _convertImage (filePath : str | None, image : PILImage) -> 'RAWImage':
        resolution = image.width * image.height

        image = image.convert('RGBA')
        channels = 4

        extrema = image.getextrema()

        if extrema[3] == (255, 255):
            image = image.convert('RGB')
            channels = 3

        rawData = image.tobytes()
        rawSize = resolution * channels

        assert len(rawData) == rawSize

        rawImage = RAWImage()

        rawImage.filePath   = filePath
        rawImage.channels   = channels
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



# noinspection PyUnusedLocal
def _test_ ():
    from hlc.common.consts import GAME_DIR

    testDir1 = r'C:\Projects\_Data_Samples'
    testDir2 = GAME_DIR

    for filePath in iterFiles(testDir2, includeExts=[ '.tga', '.bmp' ]):
        print(filePath)

        try:
            image   = RAWImage.fromFile(filePath)
            rawData = readBin(filePath)
            image   = RAWImage.fromBuffer(rawData)

            print(f'{ image.width }x{ image.height }:{ image.channels * 8 }, { image.colorCount } colors')

        except Exception as e:
            print(f'ERROR: { e }')

        print(' ')



__all__ = [
    'RAWImage',

    '_test_',
]



if __name__ == '__main__':
    _test_()
