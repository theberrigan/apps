from ...common import bfw

from bfw.types.enums import Enum



class VDFTokenType (Enum):
    BraceLeft  = 1
    BraceRight = 2
    String     = 3
    Comment    = 4



__all__ = [
    'VDFTokenType',
]