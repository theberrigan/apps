from ...common import bfw

from bfw.types.enums import Enum



# Compression type
class TextureCompType (Enum):
    No   = 0
    DXT1 = 1
    DXT3 = 3
    DXT5 = 5  # unused in VC


class TexturePxFormat (Enum):
    Default = 0
    C1555   = 0x100  # in DXT1
    C565    = 0x200  # in DXT1
    C4444   = 0x300  # in DXT3
    C8888   = 0x500  # in PAL8
    C888    = 0x600  # in PAL8 and raw BGRA


class TextureFilterType (Enum):
    Nearest          = 1
    Linear           = 2
    MipNearest       = 3  # one mipmap
    MipLinear        = 4
    LinearMipNearest = 5  # mipmap interpolated
    LinearMipLinear  = 6


class TextureAddressingType (Enum):
    Wrap   = 1
    Mirror = 2
    Clamp  = 3
    Border = 4



__all__ = [
    'TextureCompType',
    'TexturePxFormat',
    'TextureFilterType',
    'TextureAddressingType',
]