import os
import sys

from math import isnan as isNaN
from struct import pack, unpack

sys.path.insert(0, r'C:\Projects\PythonLib\python\v001')

from bfw.utils import *
from bfw.reader import *

# from formats.wad import getWADs


def testFloat ():
    for filePath in iterFiles(r'C:\Projects\_Sources\GameEngines\Goldsrc\Xash3D_3', True, excludeExts=[ '.opensdf' ]):
        with openFile(filePath) as f:
            while f.remaining() >= 4:
                a = f.read(4)
                b = unpack('<f', a)[0]

                if not isNaN(b):
                    c = pack('<f', b)

                    assert a == c, (a, b, c)



class Enum:
    _enum_kvm_ = None
    _enum_vkm_ = None

    @classmethod
    def _createCache (cls):
        if cls._enum_vkm_ is None:
            cls._enum_kvm_ = {
                k: v
                for k, v in cls.__dict__.items()
                if k[0] != '_'
            }

            cls._enum_vkm_ = { v: k for k, v in cls._enum_kvm_.items() }

    @classmethod
    def hasKey (cls, key):
        cls._createCache()
        return key in cls._enum_kvm_

    @classmethod
    def hasValue (cls, value):
        cls._createCache()
        return value in cls._enum_vkm_

    @classmethod
    def getKey (cls, value):
        cls._createCache()
        return cls._enum_vkm_.get(value)

    @classmethod
    def items (cls):
        cls._createCache()
        return cls._enum_kvm_.items()


# flags
class ImageFlags (Enum):
    CubeMap    = 1 << 0                 # IMAGE_CUBEMAP      -- it's 6-sides cubemap buffer
    HasAlpha   = 1 << 1                 # IMAGE_HAS_ALPHA    -- image contain alpha-channel
    HasColor   = 1 << 2                 # IMAGE_HAS_COLOR    -- image contain RGB-channel
    ColorIndex = 1 << 3                 # IMAGE_COLORINDEX   -- all colors in palette is gradients of last color (decals)
    HasLuma    = 1 << 4                 # IMAGE_HAS_LUMA     -- image has luma pixels (q1-style maps)
    Skybox     = 1 << 5                 # IMAGE_SKYBOX       -- only used by FS_SaveImage - for write right suffixes
    QuakeSky   = 1 << 6                 # IMAGE_QUAKESKY     -- it's a quake sky double layered clouds (so keep it as 8 bit)
    DDSFormat  = 1 << 7                 # IMAGE_DDS_FORMAT   -- a hint for GL loader
    MultiLayer = 1 << 8                 # IMAGE_MULTILAYER   -- to differentiate from 3D texture
    Alpha1Bit  = 1 << 9                 # IMAGE_ONEBIT_ALPHA -- binary alpha
    QuakePal   = 1 << 10                # IMAGE_QUAKEPAL     -- image has quake1 palette
    FlipX      = 1 << 16                # IMAGE_FLIP_X       -- flip the image by width
    FlipY      = 1 << 17                # IMAGE_FLIP_Y       -- flip the image by height
    Rot90      = 1 << 18                # IMAGE_ROT_90       -- flip from upper left corner to down right corner
    Rot180     = FlipX | FlipY          # IMAGE_ROT180       --
    Rot270     = FlipX | FlipY | Rot90  # IMAGE_ROT270       --
    Emboss     = 1 << 19                # IMAGE_EMBOSS       -- apply emboss mapping
    Resample   = 1 << 20                # IMAGE_RESAMPLE     -- resample image to specified dims
    ForceRGBA  = 1 << 23                # IMAGE_FORCE_RGBA   -- force image to RGBA buffer
    MakeLuma   = 1 << 24                # IMAGE_MAKE_LUMA    -- create luma texture from indexed
    Quantize   = 1 << 25                # IMAGE_QUANTIZE     -- make indexed image from 24 or 32- bit image
    LightGamma = 1 << 26                # IMAGE_LIGHTGAMMA   -- apply gamma for image
    Remap      = 1 << 27                # IMAGE_REMAP        -- interpret width and height as top and bottom color

# print(ImageFlags.getKey(1 << 16)); sys.exit()

# print(ImageFlags.__dict__); sys.exit()

# cmdFlags and forceFlags
class ILFlags (Enum):
    UseLerping     = 1 << 0    # IL_USE_LERPING     -- lerping images during resample
    Keep8Bit       = 1 << 1    # IL_KEEP_8BIT       -- don't expand paletted images
    AllowOverwrite = 1 << 2    # IL_ALLOW_OVERWRITE -- allow to overwrite stored images
    DontFlipTGA    = 1 << 3    # IL_DONTFLIP_TGA    -- Steam background completely ignore tga attribute 0x20 (stupid lammers!)
    DDSHardware    = 1 << 4    # IL_DDS_HARDWARE    -- DXT compression is support
    LoadDecal      = 1 << 5    # IL_LOAD_DECAL      -- special mode for load gradient decals
    Overview       = 1 << 6    # IL_OVERVIEW        -- overview required some unque operations

# flags=()
# cmdFlags=(UseLerping | AllowOverwrite | DDSHardware)
# forceFlags=(DontFlipTGA | LoadDecal | Overview)

def collectImageFlags ():
    lines = readText(r'C:\Projects\HLW\packages\game\misc\logs\hl.log')
    
    lines = lines.split('\n')

    for line in lines:
        line = line.strip()

        if not line:
            continue

        line = line.split(':', 2)


# collectImageFlags()

# https://peps.python.org/pep-3115
# https://realpython.com/python-metaclasses/

# class EnumMeta:
#     def __new__ (cls, *args, **kwargs):
#         print('M.__call__', *args, **kwargs)
#
# class Enum (metaclass=EnumMeta):
#     pass
#
# class MyEnum (Enum):
#     XXX = 1
#     YYY = XXX + 1

# print(My())


