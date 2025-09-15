from ...common import bfw

from bfw.types.enums import Enum



class MatType (Enum):
    Concrete = 1
    Metal    = 2
    Glass    = 3
    Dirt     = 4
    Slosh    = 5
    Tile     = 6
    Grate    = 7
    Wood     = 8
    Flesh    = 9
    Vent     = 10
    Computer = 11



__all__ = [
    'MatType'
]