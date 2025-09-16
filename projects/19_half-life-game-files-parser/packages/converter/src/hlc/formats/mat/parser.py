from ...common import bfw
from ...common.consts import MATERIALS_PATH, HL_TEXT_ENCODING
from ..ssv import SSV
from .consts import *
from .types import *

from bfw.utils import *



def parse (text):
    mats = {}

    for values in SSV.fromText(text):
        assert len(values) == 2

        code = values[0].upper()
        name = values[1].lower()

        assert code in MAT_CODE_TO_TYPE

        matType  = MAT_CODE_TO_TYPE[code]
        prevType = mats.get(name)

        if prevType is not None and matType != prevType:
            print(f'WARNING! Material "{ name }" type has been redefined from { prevType } to { matType }')

        mats[name] = matType

    return mats


class Mat:
    @classmethod
    def fromFile (cls, filePath, encoding=HL_TEXT_ENCODING):
        if not isFile(filePath):
            raise OSError(f'File does not exist: { filePath }')

        return parse(readText(filePath, encoding))

    @classmethod
    def fromText (cls, text):
        if not isinstance(text, str):
            raise Exception(f'Expected str, given { type(text).__name__ }')

        return parse(text)



def _test_ ():
    print(toJson(Mat.fromFile(MATERIALS_PATH)))
    print(toJson(Mat.fromText(readText(MATERIALS_PATH, HL_TEXT_ENCODING))))



__all__ = [
    'Mat',

    '_test_',
]



if __name__ == '__main__':
    _test_()
