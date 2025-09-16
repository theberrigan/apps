from ...common import bfw
from ...common.consts import SPRITES_DIR, HL_TEXT_ENCODING
from ..ssv import SSV
from .consts import *
from .types import *

from bfw.utils import *




class SpriteRect:
    def __init__ (self):
        self.name       = None
        self.resolution = None
        self.sprName    = None
        self.x          = None
        self.y          = None
        self.width      = None
        self.height     = None


def parse (text):
    lines = SSV.fromText(text)

    sprites : list[SpriteRect] = []

    for i, values in enumerate(lines):
        if i == 0:
            assert len(values) == 1
            continue

        assert len(values) == 7

        rect = SpriteRect()

        rect.sprName    = values[2].lower() + SPRITE_EXT
        rect.name       = values[0].lower()
        rect.resolution = int(values[1], 10)
        rect.x          = int(values[3], 10)
        rect.y          = int(values[4], 10)
        rect.width      = int(values[5], 10)
        rect.height     = int(values[6], 10)

        sprites.append(rect)

    return sprites


class SpriteList:
    @classmethod
    def fromFile (cls, filePath, encoding=HL_TEXT_ENCODING):
        if not isFile(filePath):
            raise Exception(f'File does not exist: { filePath }')

        return parse(readText(filePath, encoding))

    @classmethod
    def fromText (cls, text):
        if not isinstance(text, str):
            raise Exception(f'Expected str, given { type(text).__name__ }')

        return parse(text)



def _test_ ():
    for filePath in iterFiles(SPRITES_DIR, False, [ '.txt' ]):
        print(toJson(SpriteList.fromFile(filePath)))
        print(toJson(SpriteList.fromText(readText(filePath, HL_TEXT_ENCODING))))



__all__ = [
    'SpriteList',
    'SpriteRect',

    '_test_',
]



if __name__ == '__main__':
    _test_()
