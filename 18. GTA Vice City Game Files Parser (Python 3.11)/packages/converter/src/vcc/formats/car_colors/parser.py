from math import acos

from ...common import bfw
from ...common.types import *
from ...common.consts import *
from ...common.game_data import *
from ...common.fns import splitSeps, isEmptyString, toFloats, toInts
from ...maths import radToDeg

from ..handling import VehicleHandlingData
from ..ped_stats.types import TPedStats, PedStats

from .consts import *
from .types import *

from bfw.utils import *
from bfw.types.enums import Enum



class CCSectionType (Enum):
    Colors = 1
    Cars   = 2


class CarColorCombo:
    def __init__ (self, color1 : int, color2 : int):
        self.color1 : int = color1
        self.color2 : int = color2


class CarColors:
    def __init__ (self):
        self.colors : List[TRGB]                     = []
        self.cars   : Dict[str, List[CarColorCombo]] = {}

    def addColor (self, color : TRGB) -> TRGB:
        self.colors.append(color)

        return color

    def addCombo (self, vehicleName : str, combo : CarColorCombo) -> CarColorCombo:
        if vehicleName not in self.cars:
            self.cars[vehicleName] = []

        self.cars[vehicleName].append(combo)

        return combo


class CarColorReader:
    @classmethod
    def fromFile (cls, filePath : str, ctx : Opt[Any] = None) -> CarColors:
        if not isFile(filePath):
            raise OSError(f'File does not exist: { filePath }')

        text = readText(filePath, encoding='utf-8')

        return cls(ctx).read(text)

    def __init__ (self, ctx : Opt[Any] = None):
        self.ctx : Opt[Any] = ctx

    # CFileLoader::LoadScene
    def read (self, text : str) -> CarColors:
        if self.ctx:
            if self.ctx.carColors is None:
                self.ctx.carColors = CarColors()

            carColors = self.ctx.carColors
        else:
            carColors = CarColors()

        lines = text.split('\n')

        sectionType = None

        for line in lines:
            line = line.split('#')[0].strip().strip(',')

            if isEmptyString(line):
                continue

            if not sectionType:
                match line:
                    case 'col':
                        sectionType = CCSectionType.Colors
                    case 'car':
                        sectionType = CCSectionType.Cars
                    case _:
                        raise Exception(f'Expected section, but unexpected token given: { line }')

                continue

            if line == 'end':
                sectionType = None
                continue

            values = splitSeps(line)

            match sectionType:
                case CCSectionType.Colors:
                    assert len(values) == 3

                    carColors.addColor(toInts(values))

                case CCSectionType.Cars:
                    vehicleName : str       = values[0].lower()  # same as ctx.modelInfos.vehicles[i].modelName
                    combos      : List[int] = toInts(values[1:])

                    assert len(combos) % 2 == 0

                    for i in range(len(combos) // 2):
                        carColors.addCombo(vehicleName, CarColorCombo(combos[i * 2], combos[i * 2 + 1]))

        return carColors



def _test_ ():
    _colors = CarColorReader.fromFile(joinPath(GAME_DIR, 'data/carcols.dat'))



__all__ = [
    'CarColorReader',
    'CarColors',

    '_test_',
]



if __name__ == '__main__':
    _test_()
