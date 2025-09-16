from typing import Optional, List, Callable, Dict, Any

from ...common import bfw
from ...common.types import *

from bfw.reader import Reader
from bfw.types.enums import Enum



def _enumValue (vendor, index):
    return ((vendor & 0xFFFFFF) << 8) | (index & 0xFF)


class Platform (Enum):
    Null      = 0           # PLATFORM_NULL
    GL        = 2           # PLATFORM_GL
    PS2       = 4           # PLATFORM_PS2
    Xbox      = 5           # PLATFORM_XBOX
    D3D8      = 8           # PLATFORM_D3D8
    D3D9      = 9           # PLATFORM_D3D9
    WDGL      = 11          # PLATFORM_WDGL -- WarDrum OpenGL
    GL3       = 12          # PLATFORM_GL3  -- my GL3 implementation
    FourCCPS2 = 0x00325350  # FOURCC_PS2    -- 'PS2\0'


class VendorId (Enum):
    Core           = 0        # VEND_CORE
    CriterionTK    = 1        # VEND_CRITERIONTK (toolkits)
    CriterionINT   = 4        # VEND_CRITERIONINT
    CriterionWorld = 5        # VEND_CRITERIONWORLD
    Raster         = 10       # VEND_RASTER
    Driver         = 11       # VEND_DRIVER
    Rockstar       = 0x253F2  # rwVENDORID_ROCKSTAR


class CoreModuleId (Enum):
    NA      = _enumValue(VendorId.CriterionINT, 0x00)  # 0x400 | ID_NAMODULE
    Frame   = _enumValue(VendorId.CriterionINT, 0x03)  # 0x403 | ID_FRAMEMODULE
    Image   = _enumValue(VendorId.CriterionINT, 0x06)  # 0x406 | ID_IMAGEMODULE
    Raster  = _enumValue(VendorId.CriterionINT, 0x07)  # 0x407 | ID_RASTERMODULE
    Texture = _enumValue(VendorId.CriterionINT, 0x08)  # 0x408 | ID_TEXTUREMODULE


class PluginId (Enum):
    NA               = _enumValue(VendorId.Core, 0x00)             # 0x00      | ID_NAOBJECT
    Struct           = _enumValue(VendorId.Core, 0x01)             # 0x01      | ID_STRUCT
    String           = _enumValue(VendorId.Core, 0x02)             # 0x02      | ID_STRING
    Extension        = _enumValue(VendorId.Core, 0x03)             # 0x03      | ID_EXTENSION
    Camera           = _enumValue(VendorId.Core, 0x05)             # 0x05      | ID_CAMERA
    Texture          = _enumValue(VendorId.Core, 0x06)             # 0x06      | ID_TEXTURE
    Material         = _enumValue(VendorId.Core, 0x07)             # 0x07      | ID_MATERIAL
    MaterialList     = _enumValue(VendorId.Core, 0x08)             # 0x08      | ID_MATLIST
    AtomicSect       = _enumValue(VendorId.Core, 0x09)             # 0x09      | ID_ATOMICSECT
    PlaneSect        = _enumValue(VendorId.Core, 0x0A)             # 0x0A      | ID_PLANESECT
    World            = _enumValue(VendorId.Core, 0x0B)             # 0x0B      | ID_WORLD
    Spline           = _enumValue(VendorId.Core, 0x0C)             # 0x0C      | ID_SPLINE
    Matrix           = _enumValue(VendorId.Core, 0x0D)             # 0x0D      | ID_MATRIX
    FrameList        = _enumValue(VendorId.Core, 0x0E)             # 0x0E      | ID_FRAMELIST
    Geometry         = _enumValue(VendorId.Core, 0x0F)             # 0x0F      | ID_GEOMETRY
    Clump            = _enumValue(VendorId.Core, 0x10)             # 0x10      | ID_CLUMP
    Light            = _enumValue(VendorId.Core, 0x12)             # 0x12      | ID_LIGHT
    UnicodeString    = _enumValue(VendorId.Core, 0x13)             # 0x13      | ID_UNICODESTRING
    Atomic           = _enumValue(VendorId.Core, 0x14)             # 0x14      | ID_ATOMIC
    TextureNative    = _enumValue(VendorId.Core, 0x15)             # 0x15      | ID_TEXTURENATIVE
    TextureDict      = _enumValue(VendorId.Core, 0x16)             # 0x16      | ID_TEXDICTIONARY
    AnimDatabase     = _enumValue(VendorId.Core, 0x17)             # 0x17      | ID_ANIMDATABASE
    Image            = _enumValue(VendorId.Core, 0x18)             # 0x18      | ID_IMAGE
    SkinAnimation    = _enumValue(VendorId.Core, 0x19)             # 0x19      | ID_SKINANIMATION
    GeometryList     = _enumValue(VendorId.Core, 0x1A)             # 0x1A      | ID_GEOMETRYLIST
    AnimAnimation    = _enumValue(VendorId.Core, 0x1B)             # 0x1B      | ID_ANIMANIMATION
    Team             = _enumValue(VendorId.Core, 0x1C)             # 0x1C      | ID_TEAM
    Crowd            = _enumValue(VendorId.Core, 0x1D)             # 0x1D      | ID_CROWD
    DMorphAnimation  = _enumValue(VendorId.Core, 0x1E)             # 0x1E      | ID_DMORPHANIMATION
    RightToRender    = _enumValue(VendorId.Core, 0x1F)             # 0x1F      | ID_RIGHTTORENDER
    MTEffectNative   = _enumValue(VendorId.Core, 0x20)             # 0x20      | ID_MTEFFECTNATIVE
    MTEffectDict     = _enumValue(VendorId.Core, 0x21)             # 0x21      | ID_MTEFFECTDICT
    TeamDict         = _enumValue(VendorId.Core, 0x22)             # 0x22      | ID_TEAMDICTIONARY
    PITextureDict    = _enumValue(VendorId.Core, 0x23)             # 0x23      | ID_PITEXDICTIONARY
    TOC              = _enumValue(VendorId.Core, 0x24)             # 0x24      | ID_TOC
    GlobalData       = _enumValue(VendorId.Core, 0x25)             # 0x25      | ID_PRTSTDGLOBALDATA
    CorePluginIdMax  = _enumValue(VendorId.Core, 0x26)             # 0x26      | ID_COREPLUGINIDMAX
    UVAnimDict       = _enumValue(VendorId.Core, 0x2B)             # 0x2B      | ID_UVANIMDICT
    Morph            = _enumValue(VendorId.CriterionTK, 0x05)      # 0x105     | ID_MORPHPLUGIN
    SkyMipMap        = _enumValue(VendorId.CriterionTK, 0x10)      # 0x110     | ID_SKYMIPMAP
    Skin             = _enumValue(VendorId.CriterionTK, 0x16)      # 0x116     | ID_SKIN
    Particles        = _enumValue(VendorId.CriterionTK, 0x18)      # 0x118     | ID_PARTICLESPLUGIN
    HAnim            = _enumValue(VendorId.CriterionTK, 0x1E)      # 0x11E     | ID_HANIM
    UserData         = _enumValue(VendorId.CriterionTK, 0x1F)      # 0x11F     | ID_USERDATA
    MatFX            = _enumValue(VendorId.CriterionTK, 0x20)      # 0x120     | ID_MATFX
    Anisotropy       = _enumValue(VendorId.CriterionTK, 0x27)      # 0x127     | ID_ANISOT
    PDS              = _enumValue(VendorId.CriterionTK, 0x31)      # 0x131     | ID_PDS
    ADC              = _enumValue(VendorId.CriterionTK, 0x34)      # 0x134     | ID_ADC
    UVAnimation      = _enumValue(VendorId.CriterionTK, 0x35)      # 0x135     | ID_UVANIMATION
    Mesh             = _enumValue(VendorId.CriterionWorld, 0x0E)   # 0x50E     | ID_MESH
    NativeData       = _enumValue(VendorId.CriterionWorld, 0x10)   # 0x510     | ID_NATIVEDATA
    VertexFMT        = _enumValue(VendorId.CriterionWorld, 0x11)   # 0x511     | ID_VERTEXFMT
    RasterGL         = _enumValue(VendorId.Raster, Platform.GL)    # 0xA02     | ID_RASTERGL
    RasterPS2        = _enumValue(VendorId.Raster, Platform.PS2)   # 0xA04     | ID_RASTERPS2
    RasterXbox       = _enumValue(VendorId.Raster, Platform.Xbox)  # 0xA05     | ID_RASTERXBOX
    RasterD3D8       = _enumValue(VendorId.Raster, Platform.D3D8)  # 0xA08     | ID_RASTERD3D8
    RasterD3D9       = _enumValue(VendorId.Raster, Platform.D3D9)  # 0xA09     | ID_RASTERD3D9
    RasterWDGL       = _enumValue(VendorId.Raster, Platform.WDGL)  # 0xA0B     | ID_RASTERWDGL
    RasterGL3        = _enumValue(VendorId.Raster, Platform.GL3)   # 0xA0C     | ID_RASTERGL3
    Driver           = _enumValue(VendorId.Driver, 0)              # 0xB00     | ID_DRIVER
    VisibilityAtomic = _enumValue(VendorId.Rockstar, 0x00)         # 0x253F200 | ID_VISIBILITYATOMIC
    VisibilityClump  = _enumValue(VendorId.Rockstar, 0x01)         # 0x253F201 | ID_VISIBILITYCLUMP
    VisibilityFrame  = _enumValue(VendorId.Rockstar, 0x02)         # 0x253F202 | ID_VISIBILITYFRAME
    CustomMatOffset  = _enumValue(VendorId.Rockstar, 0x80)         # 0x253F280 | ID_CUSTOM_MAT_OFFSET
    RPAnimBlend      = _enumValue(VendorId.Rockstar, 0xFD)         # 0x253F2FD | ID_RPANIMBLEND
    NodeName         = _enumValue(VendorId.Rockstar, 0xFE)         # 0x253F2FE | ID_NODENAME


# ChunkHeaderInfo
class RWStreamHeader:
    def __init__ (self):
        self.kind      : TInt = None  # uint32 type
        self.dataSize  : TInt = None  # uint32 length
        self.version   : TInt = None  # uint32 version
        self.build     : TInt = None  # uint32 build
        self.dataStart : TInt = None
        self.dataEnd   : TInt = None


# see Camera View Matrix White Paper
class RWMatrix:
    def __init__ (self):
        self.right : TVec3 = [ 0, 0, 0 ]
        self.up    : TVec3 = [ 0, 0, 0 ]
        self.at    : TVec3 = [ 0, 0, 0 ]
        self.pos   : TVec3 = [ 0, 0, 0 ]



__all__ = [
    'Platform',
    'VendorId',
    'CoreModuleId',
    'PluginId',
    'RWStreamHeader',
    'RWMatrix',
]


'''
ID_METRICSPLUGIN          = _enumValue(VendorId.CriterionTK, 0x01)
ID_SPLINEPLUGIN           = _enumValue(VendorId.CriterionTK, 0x02)
ID_STEREOPLUGIN           = _enumValue(VendorId.CriterionTK, 0x03)
ID_VRMLPLUGIN             = _enumValue(VendorId.CriterionTK, 0x04)
ID_MORPHPLUGIN            = _enumValue(VendorId.CriterionTK, 0x05)
ID_PVSPLUGIN              = _enumValue(VendorId.CriterionTK, 0x06)
ID_MEMLEAKPLUGIN          = _enumValue(VendorId.CriterionTK, 0x07)
ID_ANIMPLUGIN             = _enumValue(VendorId.CriterionTK, 0x08)
ID_GLOSSPLUGIN            = _enumValue(VendorId.CriterionTK, 0x09)
ID_LOGOPLUGIN             = _enumValue(VendorId.CriterionTK, 0x0a)
ID_MEMINFOPLUGIN          = _enumValue(VendorId.CriterionTK, 0x0b)
ID_RANDOMPLUGIN           = _enumValue(VendorId.CriterionTK, 0x0c)
ID_PNGIMAGEPLUGIN         = _enumValue(VendorId.CriterionTK, 0x0d)
ID_BONEPLUGIN             = _enumValue(VendorId.CriterionTK, 0x0e)
ID_VRMLANIMPLUGIN         = _enumValue(VendorId.CriterionTK, 0x0f)
ID_SKYMIPMAPVAL           = _enumValue(VendorId.CriterionTK, 0x10)
ID_MRMPLUGIN              = _enumValue(VendorId.CriterionTK, 0x11)
ID_LODATMPLUGIN           = _enumValue(VendorId.CriterionTK, 0x12)
ID_MEPLUGIN               = _enumValue(VendorId.CriterionTK, 0x13)
ID_LTMAPPLUGIN            = _enumValue(VendorId.CriterionTK, 0x14)
ID_REFINEPLUGIN           = _enumValue(VendorId.CriterionTK, 0x15)
ID_SKINPLUGIN             = _enumValue(VendorId.CriterionTK, 0x16)
ID_LABELPLUGIN            = _enumValue(VendorId.CriterionTK, 0x17)
ID_PARTICLESPLUGIN        = _enumValue(VendorId.CriterionTK, 0x18)
ID_GEOMTXPLUGIN           = _enumValue(VendorId.CriterionTK, 0x19)
ID_SYNTHCOREPLUGIN        = _enumValue(VendorId.CriterionTK, 0x1a)
ID_STQPPPLUGIN            = _enumValue(VendorId.CriterionTK, 0x1b)
ID_PARTPPPLUGIN           = _enumValue(VendorId.CriterionTK, 0x1c)
ID_COLLISPLUGIN           = _enumValue(VendorId.CriterionTK, 0x1d)
ID_HANIMPLUGIN            = _enumValue(VendorId.CriterionTK, 0x1e)
ID_USERDATAPLUGIN         = _enumValue(VendorId.CriterionTK, 0x1f)
ID_MATERIALEFFECTSPLUGIN  = _enumValue(VendorId.CriterionTK, 0x20)
ID_PARTICLESYSTEMPLUGIN   = _enumValue(VendorId.CriterionTK, 0x21)
ID_DMORPHPLUGIN           = _enumValue(VendorId.CriterionTK, 0x22)
ID_PATCHPLUGIN            = _enumValue(VendorId.CriterionTK, 0x23)
ID_TEAMPLUGIN             = _enumValue(VendorId.CriterionTK, 0x24)
ID_CROWDPPPLUGIN          = _enumValue(VendorId.CriterionTK, 0x25)
ID_MIPSPLITPLUGIN         = _enumValue(VendorId.CriterionTK, 0x26)
ID_ANISOTPLUGIN           = _enumValue(VendorId.CriterionTK, 0x27)
ID_GCNMATPLUGIN           = _enumValue(VendorId.CriterionTK, 0x29)
ID_GPVSPLUGIN             = _enumValue(VendorId.CriterionTK, 0x2a)
ID_XBOXMATPLUGIN          = _enumValue(VendorId.CriterionTK, 0x2b)
ID_MULTITEXPLUGIN         = _enumValue(VendorId.CriterionTK, 0x2c)
ID_CHAINPLUGIN            = _enumValue(VendorId.CriterionTK, 0x2d)
ID_TOONPLUGIN             = _enumValue(VendorId.CriterionTK, 0x2e)
ID_PTANKPLUGIN            = _enumValue(VendorId.CriterionTK, 0x2f)
ID_PRTSTDPLUGIN           = _enumValue(VendorId.CriterionTK, 0x30)
ID_PDSPLUGIN              = _enumValue(VendorId.CriterionTK, 0x31)
ID_PRTADVPLUGIN           = _enumValue(VendorId.CriterionTK, 0x32)
ID_NORMMAPPLUGIN          = _enumValue(VendorId.CriterionTK, 0x33)
ID_ADCPLUGIN              = _enumValue(VendorId.CriterionTK, 0x34)
ID_UVANIMPLUGIN           = _enumValue(VendorId.CriterionTK, 0x35)
ID_ENVIRONMENTPLUGIN      = _enumValue(VendorId.CriterionTK, 0x36)
ID_CHARSEPLUGIN           = _enumValue(VendorId.CriterionTK, 0x80)
ID_NOHSWORLDPLUGIN        = _enumValue(VendorId.CriterionTK, 0x81)
ID_IMPUTILPLUGIN          = _enumValue(VendorId.CriterionTK, 0x82)
ID_SLERPPLUGIN            = _enumValue(VendorId.CriterionTK, 0x83)
ID_OPTIMPLUGIN            = _enumValue(VendorId.CriterionTK, 0x84)
ID_TLWORLDPLUGIN          = _enumValue(VendorId.CriterionTK, 0x85)
ID_DATABASEPLUGIN         = _enumValue(VendorId.CriterionTK, 0x86)
ID_RAYTRACEPLUGIN         = _enumValue(VendorId.CriterionTK, 0x87)
ID_RAYPLUGIN              = _enumValue(VendorId.CriterionTK, 0x88)
ID_LIBRARYPLUGIN          = _enumValue(VendorId.CriterionTK, 0x89)
ID_2DPLUGIN               = _enumValue(VendorId.CriterionTK, 0x90)
ID_TILERENDPLUGIN         = _enumValue(VendorId.CriterionTK, 0x91)
ID_JPEGIMAGEPLUGIN        = _enumValue(VendorId.CriterionTK, 0x92)
ID_TGAIMAGEPLUGIN         = _enumValue(VendorId.CriterionTK, 0x93)
ID_GIFIMAGEPLUGIN         = _enumValue(VendorId.CriterionTK, 0x94)
ID_QUATPLUGIN             = _enumValue(VendorId.CriterionTK, 0x95)
ID_SPLINEPVSPLUGIN        = _enumValue(VendorId.CriterionTK, 0x96)
ID_MIPMAPPLUGIN           = _enumValue(VendorId.CriterionTK, 0x97)
ID_MIPMAPKPLUGIN          = _enumValue(VendorId.CriterionTK, 0x98)
ID_2DFONT                 = _enumValue(VendorId.CriterionTK, 0x99)
ID_INTSECPLUGIN           = _enumValue(VendorId.CriterionTK, 0x9a)
ID_TIFFIMAGEPLUGIN        = _enumValue(VendorId.CriterionTK, 0x9b)
ID_PICKPLUGIN             = _enumValue(VendorId.CriterionTK, 0x9c)
ID_BMPIMAGEPLUGIN         = _enumValue(VendorId.CriterionTK, 0x9d)
ID_RASIMAGEPLUGIN         = _enumValue(VendorId.CriterionTK, 0x9e)
ID_SKINFXPLUGIN           = _enumValue(VendorId.CriterionTK, 0x9f)
ID_VCATPLUGIN             = _enumValue(VendorId.CriterionTK, 0xa0)
ID_2DPATH                 = _enumValue(VendorId.CriterionTK, 0xa1)
ID_2DBRUSH                = _enumValue(VendorId.CriterionTK, 0xa2)
ID_2DOBJECT               = _enumValue(VendorId.CriterionTK, 0xa3)
ID_2DSHAPE                = _enumValue(VendorId.CriterionTK, 0xa4)
ID_2DSCENE                = _enumValue(VendorId.CriterionTK, 0xa5)
ID_2DPICKREGION           = _enumValue(VendorId.CriterionTK, 0xa6)
ID_2DOBJECTSTRING         = _enumValue(VendorId.CriterionTK, 0xa7)
ID_2DANIMPLUGIN           = _enumValue(VendorId.CriterionTK, 0xa8)
ID_2DANIM                 = _enumValue(VendorId.CriterionTK, 0xa9)
ID_2DKEYFRAME             = _enumValue(VendorId.CriterionTK, 0xb0)
ID_2DMAESTRO              = _enumValue(VendorId.CriterionTK, 0xb1)
ID_BARYCENTRIC            = _enumValue(VendorId.CriterionTK, 0xb2)
ID_PITEXDICTIONARYTK      = _enumValue(VendorId.CriterionTK, 0xb3)
ID_TOCTOOLKIT             = _enumValue(VendorId.CriterionTK, 0xb4)
ID_TPLTOOLKIT             = _enumValue(VendorId.CriterionTK, 0xb5)
ID_ALTPIPETOOLKIT         = _enumValue(VendorId.CriterionTK, 0xb6)
ID_ANIMTOOLKIT            = _enumValue(VendorId.CriterionTK, 0xb7)
ID_SKINSPLITTOOKIT        = _enumValue(VendorId.CriterionTK, 0xb8)
ID_CMPKEYTOOLKIT          = _enumValue(VendorId.CriterionTK, 0xb9)
ID_GEOMCONDPLUGIN         = _enumValue(VendorId.CriterionTK, 0xba)
ID_WINGPLUGIN             = _enumValue(VendorId.CriterionTK, 0xbb)
ID_GENCPIPETOOLKIT        = _enumValue(VendorId.CriterionTK, 0xbc)
ID_LTMAPCNVTOOLKIT        = _enumValue(VendorId.CriterionTK, 0xbd)
ID_FILESYSTEMPLUGIN       = _enumValue(VendorId.CriterionTK, 0xbe)
ID_DICTTOOLKIT            = _enumValue(VendorId.CriterionTK, 0xbf)
ID_UVANIMLINEAR           = _enumValue(VendorId.CriterionTK, 0xc0)
ID_UVANIMPARAM            = _enumValue(VendorId.CriterionTK, 0xc1)
'''
