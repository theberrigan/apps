from ...common import bfw

from bfw.types.enums import Enum



# angletype_t
class SpriteAngleType (Enum):
    FwdParallelUpright  = 0
    FacingUpright       = 1
    FwdParallel         = 2
    Oriented            = 3
    FwdParallelOriented = 4


# drawtype_t
class SpriteDrawType (Enum):
    Normal     = 0
    Additive   = 1
    IndexAlpha = 2
    AlphaTest  = 3


# facetype_t
class SpriteFaceType (Enum):
    Front = 0  # oriented sprite will be draw with one face
    No    = 1  # oriented sprite will be draw back face too


# synctype_t
class SpriteSyncType (Enum):
    Sync = 0
    Rand = 1


# frametype_t
class SpriteFrameType (Enum):
    Single = 0
    Group  = 1
    Angled = 2  # Xash3D ext



__all__ = [
    'SpriteAngleType',
    'SpriteDrawType',
    'SpriteFaceType',
    'SpriteSyncType',
    'SpriteFrameType',
]
