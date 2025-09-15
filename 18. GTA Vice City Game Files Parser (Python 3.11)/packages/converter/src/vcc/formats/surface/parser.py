from ...common import bfw
from ...common.types import *
from ...common.consts import *
from ...common.fns import splitSpaces

from .consts import *
from .types import *

from bfw.utils import *



class SurfaceCombo:
    def __init__ (self):
        self.surface1     : TStr   = None
        self.surface2     : TStr   = None
        self.adhesiveness : TFloat = None


class SurfaceReader:
    @classmethod
    def parseDefault (cls, encoding : str = 'utf-8') -> list[SurfaceCombo]:
        return cls.fromFile(SURFACE_FILE_PATH, encoding)

    @classmethod
    def fromFile (cls, filePath : str, encoding : str = 'utf-8') -> list[SurfaceCombo]:
        if not isFile(filePath):
            raise OSError(f'File does not exist: { filePath }')

        text = readText(filePath, encoding=encoding)

        return cls().read(text)

    @classmethod
    def fromBuffer (cls, text : str) -> list[SurfaceCombo]:
        return cls().read(text)

    def read (self, text : str) -> list[SurfaceCombo]:
        result = []

        lines = text.split('\n')

        surfaces = []

        for i, line in enumerate(lines):
            line = line.strip()

            if not line or line.startswith(';'):
                continue

            values = splitSpaces(line)

            surface = values[0].lower()

            surfaces.append(surface)

            values = values[1:]

            for j, value in enumerate(values):
                combo = SurfaceCombo()

                combo.surface1     = surface
                combo.surface2     = surfaces[j]
                # noinspection PyTypeChecker
                combo.adhesiveness = max(0, float(value))

                result.append(combo)

        return result



def _test_ ():
    print(toJson(SurfaceReader.parseDefault()))



__all__ = [
    'SurfaceReader',
    'SurfaceCombo',

    '_test_',
]



if __name__ == '__main__':
    _test_()
