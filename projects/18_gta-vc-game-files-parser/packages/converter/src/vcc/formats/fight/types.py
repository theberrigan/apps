from ...common import bfw

from bfw.types.enums import Enum



class FightMoveHitLevel (Enum):
    NULL   = 0
    GROUND = 1
    LOW    = 2
    MEDIUM = 3
    HIGH   = 4



__all__ = [
    'FightMoveHitLevel',
]