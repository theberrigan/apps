from ...common import bfw

from bfw.types.enums import Enum



class LoadResourceType (Enum):
    TextureDict     : int = 1
    Collision       : int = 2
    Model           : int = 3
    ItemDefinitions : int = 4
    ItemPlacements  : int = 5
    Splash          : int = 6



__all__ = [
    'LoadResourceType',
]
