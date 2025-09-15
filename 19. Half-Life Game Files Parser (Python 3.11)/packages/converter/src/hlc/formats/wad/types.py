from ...common import bfw

from bfw.types.enums import Enum



class WADLumpType (Enum):
    Any       = -1  # TYP_ANY       - any type can be accepted
    Null      = 0   # TYP_NONE      - unknown lump type
    Label     = 1   # TYP_LABEL     - legacy from Doom1. Empty lump - label (like P_START, P_END etc.)
    Palette   = 64  # TYP_PALETTE   - quake or half-life palette (768 bytes)
    DDS       = 65  # TYP_DDSTEX    - contain DDS texture
    GFX       = 66  # TYP_GFXPIC    - menu or hud image (not contain mip-levels)
    Mip       = 67  # TYP_MIPTEX    - quake1 and half-life in-game textures with four miplevels
    Script    = 68  # TYP_SCRIPT    - contain script files
    Colormap2 = 69  # TYP_COLORMAP2 - old stuff. build palette from LBM file (not used)
    QFont     = 70  # TYP_QFONT     - half-life font (qfont_t)



__all__ = [
    'WADLumpType',
]