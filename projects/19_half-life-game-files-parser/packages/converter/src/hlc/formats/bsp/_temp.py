from ...common import bfw
from ...maths import *
from ...fs import openAnyFile
from ..wad import getWADs

from bfw.utils import isBitSet, setBit, getExt, dropExt
from bfw.reader import Reader, MemReader



BLOCK_SIZE_DEFAULT = 128    # for keep backward compatibility
BLOCK_SIZE_MAX     = 1024
BLOCK_SIZE         = BLOCK_SIZE_DEFAULT	  # light map block size

VERTEX_SIZE     = 7
ABM_SOUND_COUNT = 4  # NUM_AMBIENTS




class RGBData:
    def __init__ (self):
        self.width     = 0	   # image width
        self.height    = 0     # image height
        self.depth     = 0     # image depth
        self.type_     = 0     # compression type
        self.flags     = 0     # misc image flags
        self.encode    = 0     # DXT may have custom encoder, that will be decoded in GLSL-side
        self.numMips   = 0     # mipmap count
        self.palette   = None  # palette if present
        self.buffer    = None  # image buffer
        self.fogParams = [ 0, 0, 0, 0 ]  # some water textures in hl1 has info about fog color and alpha
        self.size      = 0     # for bounds checking


# texture_t
class Texture:
    def __init__ (self):
        self.name      : str | None     = None     # char name[16]
        self.width     : int            = 0        # unsigned int
        self.height    : int            = 0        # unsigned int
        self.data      : RGBData | None = None     # int gl_texturenum TODO: loaded GL texture
        self.animTotal : int            = 0        # int anim_total -- total tenths in sequence ( 0 = no)
        self.animMin   : int            = 0        # int anim_min -- time for this frame min <= time < max
        self.animMax   : int            = 0        # int anim_max -- time for this frame min <= time < max
        self.animNext  : Texture | None = None     # struct texture_s *anim_next -- in the animation sequence
        self.animAlt   : Texture | None = None     # struct texture_s *alternate_anims -- bmodels in frame 1 use these
        # struct msurface_s *texturechain -- for gl_texsort drawing
        # unsigned short fb_texturenum -- auto-luma texturenum
        # unsigned short dt_texturenum -- detail-texture binding


# color24 - const.h
class RGB:
    def __init__ (self, r : int = 0, g : int = 0, b : int = 0):
        self.r : int = r
        self.g : int = g
        self.b : int = b


# ----------------------------------------------------------------------------------------------------------------------
# ------------------------------------------ M O D E L   C O M M O N ---------------------------------------------------
# ----------------------------------------------------------------------------------------------------------------------


# glpoly_t - com_model.h
class ModelPoly:
    def __init__ (self):
        self.next      : ModelPoly | None  = None    # struct glpoly_s *next
        self.chain     : ModelPoly | None  = None    # struct glpoly_s *chain
        self.vertCount : int               = 0       # int numverts
        self.flags     : int               = 0       # int flags -- for SURF_UNDERWATER
        self.vertices  : list[list[float]] = []      # float verts[vertCount][VERTEXSIZE] -- (x, y, z, s1, t1, s2, t2)


# mleaf_t - com_model.h
class ModelLeaf:
    def __init__ (self):
        TParent = ModelNode | None

        # common with node
        self.contents           : int       = ContentsType.Empty  # int contents
        # int visframe -- node needs to be traversed if current
        self.mins               : Vec3      = [ 0, 0, 0 ]  # float minmaxs[6] -- for bounding box culling
        self.maxs               : Vec3      = [ 0, 0, 0 ]  # ^^^
        self.parent             : TParent   = None         # struct mnode_s *parent

        # leaf specific
        self.compVisOffset      : int       = -1  # byte *compressed_vis
        # struct efrag_s *efrags
        self.firstMarkFaceIndex : int       = 0  # msurface_t **firstmarksurface
        self.markFaceCount      : int       = 0  # int nummarksurfaces
        self.cluster            : int       = 0  # int cluster -- helper to access to uncompressed visdata
        self.ambSoundLevels     : list[int] = [ 0 ] * ABM_SOUND_COUNT  # byte ambient_sound_level[NUM_AMBIENTS]


# mnode_t - com_model.h
class ModelNode:
    def __init__ (self):
        TChildren = list[ ModelNode | ModelLeaf | None ]
        TParent   = ModelNode | None
        TPlane    = ModelPlane | None

        # common with leaf
        self.contents       : int        = 0               # int contents -- 0, to differentiate from leafs
        # int visframe -- node needs to be traversed if current
        self.mins           : Vec3       = [ 0, 0, 0 ]     # float minmaxs[6] -- for bounding box culling
        self.maxs           : Vec3       = [ 0, 0, 0 ]     # ^^^
        self.parent         : TParent    = None            # struct mnode_s *parent

        # node specific
        self.plane          : TPlane     = None            # mplane_t *plane
        self.children       : TChildren  = [ None, None ]  # struct mnode_s *children[2]
        self.firstFaceIndex : int        = -1              # unsigned short firstsurface
        self.faceCount      : int        = 0               # unsigned short numsurfaces


# mplane_t - com_model.h
class ModelPlane:
    def __init__ (self):
        self.normal   : Vec3  = [ 0, 0, 0 ]        # vec3_t normal
        self.dist     : float = 0                  # float dist
        self.type_    : int   = PlaneType.Unknown  # byte type -- for fast side tests
        self.signBits : int   = 0                  # byte signbits


# medge_t - com_model.h
class ModelEdge:
    def __init__ (self):
        self.v                : list[int, int] = [ 0, 0 ]  # unsigned short v[2]
        self.cachedEdgeOffset : int            = -1        # unsigned int cachededgeoffset


# mtexinfo_t - com_model.h
class ModelTextureInfo:
    def __init__ (self):
        # [s/t] unit vectors in world space.
        # [i][3] is the s/t offset relative to the origin.
        # s or t = dot( 3Dpoint, vecs[i] ) + vecs[i][3]
        self.vectors : list[Vec4, Vec4] = [  # float vecs[2][4]
            [ 0, 0, 0, 0 ],
            [ 0, 0, 0, 0 ]
        ]
        self.texture  : Texture | None = None
        self.flags    : int            = 0     # int flags -- sky or slime, no lightmap or 256 subdivision
        self.faceInfo : None           = None  # [UNUSED] mfaceinfo_t *faceinfo -- pointer to landscape info and lightmap resolution (maybe NULL) TODO: check is used in engine/common/mod_bmodel.c:2117


# msurface_t - com_model.h
class ModelFace:
    def __init__ (self):
        # int visframe -- should be drawn when node is crossed
        self.plane          : ModelPlane | None = None         # mplane_t *plane -- pointer to shared plane TODO: BSPPlane
        self.flags          : int               = 0            # int flags -- see SURF_ #defines
        self.firstEdgeIndex : int               = 0            # int firstedge -- look up in model->surfedges[], negative numbers
        self.edgeCount      : int               = 0            # int numedges -- are backwards edges
        self.textureMins    : list[int]         = [ 0, 0 ]     # short texturemins[2]
        self.extents        : list[int]         = [ 0, 0 ]     # short extents[2]
        self.lightS         : int               = 0            # int light_s -- gl lightmap coordinates
        self.lightT         : int               = 0            # int light_t
        self.polys          : ModelPoly | None  = None         # glpoly_t *polys -- multiple if warped
        # msurface_s *texturechain
        self.textureInfo    : ModelTextureInfo | None = None   # mtexinfo_t *texinfo

        # lighting info
        # int dlightframe -- last frame the surface was checked by an animated light
        # int dlightbits -- dynamically generated. Indicates if the surface illumination is modified by an animated light.
        # int lightmaptexturenum
        self.styles : list[int] = [ 0, 0, 0, 0 ]    # byte styles[MAXLIGHTMAPS]
        # int cached_light[MAXLIGHTMAPS] -- values currently used in lightmap
        self.info : ModelFaceInfo = ModelFaceInfo(self)    # mextrasurf_t *info -- pointer to surface extradata (was cached_dlight)
        # TODO: IS THIS IS SINGLE ELEMENT [offset] OR SLICE [offset:]???
        self.samples : list[RGB] | None = None    # color24 *samples -- note: this is the actual lightmap data for this surface
        # decal_t *pdecals
        self.lightMapOffset : int = 0  # dface_t->lightofs -- RAW offset (in bytes)


# mextrasurf_t - com_model.h
class ModelFaceInfo:
    def __init__ (self, face : ModelFace | None = None):
        TLMV  = list[Vec4, Vec4]
        TFace = ModelFace | None

        self.mins   : Vec3  = [ 0, 0, 0 ]   # vec3_t mins
        self.maxs   : Vec3  = [ 0, 0, 0 ]   # vec3_t maxs
        self.origin : Vec3  = [ 0, 0, 0 ]   # vec3_t origin -- surface origin
        self.face   : TFace = face          # msurface_s *surf -- upcast to surface

        # extended light info
        # int dlight_s -- gl lightmap coordinates for dynamic lightmaps
        # int dlight_t
        self.lightMapMins    : list[int, int] = [ 0, 0 ]   # short lightmapmins[2] -- lightmatrix
        self.lightMapExtents : list[int, int] = [ 0, 0 ]   # short lightextents[2]
        self.lightMapVecs    : TLMV           = [          # float lmvecs[2][4]
            [ 0, 0, 0, 0 ],
            [ 0, 0, 0, 0 ]
        ]
        # color24 *deluxemap -- note: this is the actual deluxemap data for this surface
        # byte *shadowmap -- note: occlusion map for this surface

        # begin userdata
        # msurface_s *lightmapchain -- lightmapped polys
        # mextrasurf_s *detailchain -- for detail textures drawing
        # mextrasurf_s *mirrorchain -- for gl_texsort drawing
        # mextrasurf_s *lumachain -- draw fullbrights
        # cl_entity_s *parent -- upcast to owner entity
        # int mirrortexturenum -- gl texnum
        # float mirrormatrix[4][4]
        # grasshdr_s *grass -- grass that linked by this surface
        # unsigned short grasscount -- number of bushes per polygon (used to determine total VBO size)
        # unsigned short numverts -- world->vertexes[]
        # int firstvertex -- fisrt look up in tr.tbn_vectors[], then acess to world->vertexes[]
        # int reserved[32] -- just for future expansions or mod-makers


# ----------------------------------------------------------------------------------------------------------------------
# ----------------------------------------------------------------------------------------------------------------------
# ----------------------------------------------------------------------------------------------------------------------


# texFlags_t - render_api.h
class TextureFlags:
    ColorMap      = 0 << 0     # TF_COLORMAP      -- just for tabulate source
    Nearest       = 1 << 0     # TF_NEAREST       -- disable texfilter
    KeepSource    = 1 << 1     # TF_KEEP_SOURCE   -- some images keep source
    NoFlipTGA     = 1 << 2     # TF_NOFLIP_TGA    -- Steam background completely ignore tga attribute 0x20
    ExpandSource  = 1 << 3     # TF_EXPAND_SOURCE -- Don't keep source as 8-bit expand to RGBA
    AllowEmboss   = 1 << 4     # TF_ALLOW_EMBOSS  -- Allow emboss-mapping for this image
    Rectangle     = 1 << 5     # TF_RECTANGLE     -- this is GL_TEXTURE_RECTANGLE
    CubeMap       = 1 << 6     # TF_CUBEMAP       -- it's cubemap texture
    DepthMap      = 1 << 7     # TF_DEPTHMAP      -- custom texture filter used
    QuakePal      = 1 << 8     # TF_QUAKEPAL      -- image has an quake1 palette
    Luminance     = 1 << 9     # TF_LUMINANCE     -- force image to grayscale
    SkySide       = 1 << 10    # TF_SKYSIDE       -- this is a part of skybox
    Clamp         = 1 << 11    # TF_CLAMP         -- clamp texcoords to [0..1] range
    NoMipMap      = 1 << 12    # TF_NOMIPMAP      -- don't build mips for this image
    HasLuma       = 1 << 13    # TF_HAS_LUMA      -- sets by GL_UploadTexture
    MakeLuma      = 1 << 14    # TF_MAKELUMA      -- create luma from quake texture (only q1 textures contain luma-pixels)
    NormalMap     = 1 << 15    # TF_NORMALMAP     -- is a normalmap
    HasAlpha      = 1 << 16    # TF_HAS_ALPHA     -- image has alpha (used only for GL_CreateTexture)
    ForceColor    = 1 << 17    # TF_FORCE_COLOR   -- force upload monochrome textures as RGB (detail textures)
    Border        = 1 << 19    # TF_BORDER        -- zero clamp for projected textures
    Texture3D     = 1 << 20    # TF_TEXTURE_3D    -- this is GL_TEXTURE_3D
    AtlasPage     = 1 << 21    # TF_ATLAS_PAGE    -- bit who indicate lightmap page or deluxemap page
    AlphaContrast = 1 << 22    # TF_ALPHACONTRAST -- special texture mode for A2C
    ImgUploaded   = 1 << 25    # TF_IMG_UPLOADED  -- this is set for first time when called glTexImage, otherwise it will be call glTexSubImage
    ArbFloat      = 1 << 26    # TF_ARB_FLOAT     -- float textures
    NoCompare     = 1 << 27    # TF_NOCOMPARE     -- disable comparing for depth textures
    Arb16Bit      = 1 << 28    # TF_ARB_16BIT     -- keep image as 16-bit (not 24)


# MODEL_* - mod_local.h
# model flags (stored in model_t->flags)
class ModelFlags:
    Conveyor        = 1 << 0  # MODEL_CONVEYOR
    HasOrigin       = 1 << 1  # MODEL_HAS_ORIGIN
    Liquid          = 1 << 2  # MODEL_LIQUID           -- model has only point hull
    Transparent     = 1 << 3  # MODEL_TRANSPARENT      -- have transparent surfaces
    ColoredLighting = 1 << 4  # MODEL_COLORED_LIGHTING -- light maps stored as RGB


# FWORLD_* - mod_local.h
class WorldFlags:
    SkySphere    = 1 << 0  # FWORLD_SKYSPHERE
    CustomSkybox = 1 << 1  # FWORLD_CUSTOM_SKYBOX
    WaterAlpha   = 1 << 2  # FWORLD_WATERALPHA
    HasDeluxeMap = 1 << 3  # FWORLD_HAS_DELUXEMAP


# CONTENTS_* - const.h
class ContentsType:
    Empty           = -1   # CONTENTS_EMPTY
    Solid           = -2   # CONTENTS_SOLID
    Water           = -3   # CONTENTS_WATER
    Slime           = -4   # CONTENTS_SLIME
    Lava            = -5   # CONTENTS_LAVA
    Sky             = -6   # CONTENTS_SKY
    # These additional contents constants are defined in bspfile.h
    Origin          = -7   # CONTENTS_ORIGIN -- removed at csg time
    Clip            = -8   # CONTENTS_CLIP -- changed to contents_solid
    Current0        = -9   # CONTENTS_CURRENT_0
    Current90       = -10  # CONTENTS_CURRENT_90
    Current180      = -11  # CONTENTS_CURRENT_180
    Current270      = -12  # CONTENTS_CURRENT_270
    CurrentUp       = -13  # CONTENTS_CURRENT_UP
    CurrentDown     = -14  # CONTENTS_CURRENT_DOWN
    Translucent     = -15  # CONTENTS_TRANSLUCENT
    Ladder          = -16  # CONTENTS_LADDER
    FlyField        = -17  # CONTENT_FLYFIELD
    GravityFlyField = -18  # CONTENT_GRAVITY_FLYFIELD
    Fog             = -19  # CONTENT_FOG


# PLANE_* - mathlib.h
class PlaneType:
    Unknown = -1
    # Plane is perpendicular to given axis
    X       = 0  # PLANE_X
    Y       = 1  # PLANE_Y
    Z       = 2  # PLANE_Z
    # Non-axial plane is snapped to the nearest
    AnyX    = 3  # PLANE_NONAXIAL
    AnyY    = 4
    AnyZ    = 5



# ----------------------------------------------------------------------------------------------------------------------
# ----------------------------------------------------------------------------------------------------------------------
# ----------------------------------------------------------------------------------------------------------------------


class StudioModelFlags:
    FlatShade  = 1 << 0   # STUDIO_NF_FLATSHADE
    Chrome     = 1 << 1   # STUDIO_NF_CHROME
    FullBright = 1 << 2   # STUDIO_NF_FULLBRIGHT
    NoMips     = 1 << 3   # STUDIO_NF_NOMIPS     -- ignore mip-maps
    Additive   = 1 << 5   # STUDIO_NF_ADDITIVE   -- rendering with additive mode
    Masked     = 1 << 6   # STUDIO_NF_MASKED     -- use texture with alpha channel
    NormalMap  = 1 << 7   # STUDIO_NF_NORMALMAP  -- indexed normalmap
    ColorMap   = 1 << 30  # STUDIO_NF_COLORMAP   -- internal system flag
    UVCoords   = 1 << 31  # STUDIO_NF_UV_COORDS  -- using half-float coords instead of ST


class Mip:
    def __init__ (self, name, width, height, offsets):
        self.name    = name
        self.width   = width
        self.height  = height
        self.offsets = offsets


# ilFlags_t - common.h
class ILFlags:
    UseLerping     = 1 << 0    # IL_USE_LERPING     -- lerping images during resample
    Keep8Bit       = 1 << 1    # IL_KEEP_8BIT       -- don't expand paletted images
    AllowOverwrite = 1 << 2    # IL_ALLOW_OVERWRITE -- allow to overwrite stored images
    DontFlipTGA    = 1 << 3    # IL_DONTFLIP_TGA    -- Steam background completely ignore tga attribute 0x20 (stupid lammers!)
    DDSHardware    = 1 << 4    # IL_DDS_HARDWARE    -- DXT compression is support
    LoadDecal      = 1 << 5    # IL_LOAD_DECAL      -- special mode for load gradient decals
    Overview       = 1 << 6    # IL_OVERVIEW        -- overview required some unque operations

# imgFlags_t - common.h
class ImageFlags:
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

# engine/common/imagelib/imagelib.h:259
class ImageLumpType:
    Normal   = 0  # no alpha
    Masked   = 1  # 1-bit alpha channel masked texture
    Gradient = 2  # gradient image (decals)
    Extended = 3  # bmp images have extened palette with alpha-channel
    HalfLife = 4  # get predefined half-life palette
    Quake1   = 5  # get predefined quake palette

class ImagePalette:
    Invalid  = -1
    Custom   = 0
    Quake1   = 1
    HalfLife = 2

class ILHint:
    No = 0
    Q1 = 1  # palette choosing
    HL = 2

class DXTEncode:
    Default            = 0         # don't use custom encoders
    ColorYCoCg         = 0x1A01    # make sure that value doesn't collide with anything
    Alpha1Bit          = 0x1A02    # normal 1-bit alpha
    Alpha8Bit          = 0x1A03    # normal 8-bit alpha
    AlphaSDF           = 0x1A04    # signed distance field
    NormalAGOrtho      = 0x1A05    # orthographic projection
    NormalAGStereo     = 0x1A06    # stereographic projection
    NormalAGParaboloid = 0x1A07    # paraboloid projection
    NormalAGQuadratic  = 0x1A08    # newton method
    NormalAGAzimuthal  = 0x1A09    # Lambert Azimuthal Equal-Area

class PixFormat:
    Unknown    = 0
    Indexed24  = 1    # inflated palette (768 bytes)
    Indexed32  = 2    # deflated palette (1024 bytes)
    RGBA32     = 3    # normal rgba buffer
    BGRA32     = 4    # big endian RGBA (MacOS)
    RGB24      = 5    # uncompressed dds or another 24-bit image
    BGR24      = 6    # big-endian RGB (MacOS)
    DXT1       = 7    # s3tc DXT1 format
    DXT3       = 8    # s3tc DXT3 format
    DXT5       = 9    # s3tc DXT5 format
    ATI2       = 10   # latc ATI2N format
    TotalCount = 11   # must be last

class Image:
    def __init__ (self):
        self.forceFlags   = 0
        self.cmdFlags     = 0
        self.hint         = ILHint.No
        self.width        = 0
        self.height       = 0
        self.depth        = 0
        self.sourceWidth  = 0
        self.sourceHeight = 0
        self.sourceType   = 0
        self.numMips      = 0
        self.numSides     = 0
        self.flags        = 0
        self.encode       = DXTEncode.Default
        self.type_        = PixFormat.Unknown
        self.fogParams    = [ 0, 0, 0, 0 ]  # rgba_t
        self.dRenderMode  = 0
        self.dCurrentPal  = None
        self.hasCustomPalette = False

        # pointers will be saved with prevoius picture struct
        # don't care about it
        self.palette = None
        self.cubeMap = None
        self.rgba    = []
        self.ptr     = 0
        self.size    = 0


def Image_LoadMDL (reader) -> bool:
    global image

    assert image.hint == ILHint.HL

    name   = reader.string(64)    # char     name[64]
    flags  = reader.u32()         # uint32_t flags
    width  = reader.i32()         # int      width
    height = reader.i32()         # int      height
    index  = reader.i32()         # int      index

    assert not isBitSet(flags, StudioModelFlags.Masked)

    image.width  = width
    image.height = height

    resolution = width * height

    indices = reader.read(resolution)

    assert reader.remaining() == MIP_PALETTE_SIZE

    palette = reader.read(MIP_PALETTE_SIZE)

    Image_GetPaletteLMP(palette, ImageLumpType.Normal)

    image.type_ = PixFormat.Indexed32    # 32-bit palette
    image.depth = 1

    return Image_AddIndexedImageToPack(indices, image.width, image.height)


def Image_LoadDDS (reader) -> bool:
    raise NotImplementedError()

def Image_LoadTGA (reader) -> bool:
    raise NotImplementedError()

def Image_LoadBMP (reader) -> bool:
    raise NotImplementedError()

def Image_LoadSPR (reader) -> bool:
    raise NotImplementedError()

def Image_LoadLMP (reader) -> bool:
    raise NotImplementedError()

def Image_LoadFNT (reader) -> bool:
    raise NotImplementedError()

def Image_LoadPAL (reader) -> bool:
    raise NotImplementedError()


ANIM_CYCLE = 2

MIP_HEADER_SIZE        = 40
MIP_PALETTE_COLORS     = 256
MIP_PALETTE_CHANNELS   = 3
MIP_PALETTE_SIZE       = MIP_PALETTE_CHANNELS * MIP_PALETTE_COLORS  # 768
MIP_PALETTE_BLOCK_SIZE = 2 + MIP_PALETTE_SIZE                       # 2 bytes is a colorCount (== MIP_PALETTE_COLORS)


def Image_LoadMIP (reader : Reader) -> bool:
    global image

    fileSize = reader.getSize()

    if fileSize < MIP_HEADER_SIZE:
        return False

    isHLTexture  = False
    reflectivity = [ 0, 0, 0 ]
    renderMode   = ImageLumpType.Normal

    name    = reader.string(16)
    width   = reader.u32()
    height  = reader.u32()
    offsets = reader.u32(4)

    assert 0 < width <= 8192 and 0 < height <= 8192

    mip = Mip(
        name    = name,
        width   = width,
        height  = height,
        offsets = offsets
    )

    image.width  = mip.width
    image.height = mip.height

    resolution = image.width * image.height  # pixels

    mipsSize = (resolution * 85) >> 6
    baseSize = MIP_HEADER_SIZE + mipsSize  # == paletteStart

    mipsStart    = mip.offsets[0]
    paletteStart = mipsStart + mipsSize

    palette = None

    # header     - 40
    # mips       - (resolution * 85) >> 6
    # colorCount - 2
    # palette    - 768

    # print(name)

    if image.hint != ILHint.Q1 and fileSize >= (baseSize + MIP_PALETTE_BLOCK_SIZE):
        isHLTexture = True
        # fin = reader.seek(mipsStart)
        # pal = reader.seek(paletteStart)
        reader.seek(paletteStart)

        colorCount = reader.i16()

        if colorCount == MIP_PALETTE_COLORS:
            palette = reader.read(MIP_PALETTE_SIZE)
        else:
            palette = None

        if '{' in name:
            # TODO: add Image.cmdFlags!!!
            if not Image_CheckFlag(ILFlags.LoadDecal) or (palette[765] == palette[766] == 0 and palette[767] == 255):
                image.flags = setBit(image.flags, ImageFlags.Alpha1Bit)
                renderMode = ImageLumpType.Normal
            else:
                # classic gradient decals
                image.flags = setBit(image.flags, ImageFlags.ColorIndex)
                renderMode = ImageLumpType.Gradient

            image.flags = setBit(image.flags, ImageFlags.HasAlpha)
        else:
            paletteType = Image_ComparePalette(palette)

            if mip.name[0] not in '*!' and paletteType == PALETTE_Q1:
                assert False, 'engine/common/imagelib/img_wad.c:397'

            if paletteType == PALETTE_Q1:
                image.flags = setBit(image.flags, ImageFlags.QuakePal)

            renderMode = ImageLumpType.Normal

        Image_GetPaletteLMP(palette, renderMode)
        image.dCurrentPal[255][3] = 0  # image.d_currentpal[255] &= 0xFFFFFF;

    elif image.hint != ILHint.HL and fileSize >= baseSize:
        isHLTexture = False
        palette = None
        renderMode = ImageLumpType.Normal

        reader.seek(mipsStart)

        indices = reader.read(resolution)

        if not image.hasCustomPalette:
            for index in indices:
                if 224 < index < 255:
                    if mip.name[0] not in '*!':
                        image.flags |= ImageFlags.HasLuma

                    break

        if '{' in name:
            for index in indices:
                if index == 255:
                    image.flags |= ImageFlags.HasAlpha
                    break

        image.flags = setBit(image.flags, ImageFlags.QuakePal)
        Image_GetPaletteQ1()

    else:
        return False

    if mip.name.lower().startswith('sky') and image.width == (image.height * 2):
        image.flags |= ImageFlags.QuakeSky

    if isHLTexture and (mip.name[0] == '!' or mip.name.lower().startswith('water')):
        # grab the fog color
        image.fogParams[0] = palette[3 * 3 + 0]
        image.fogParams[1] = palette[3 * 3 + 1]
        image.fogParams[2] = palette[3 * 3 + 2]

        # grab the fog density
        image.fogParams[3] = palette[4 * 3 + 0]

    elif isHLTexture and renderMode == ImageLumpType.Gradient:
        # grab the decal color
        image.fogParams[0] = palette[255 * 3 + 0]
        image.fogParams[1] = palette[255 * 3 + 1]
        image.fogParams[2] = palette[255 * 3 + 2]

        # calc the decal reflectivity
        image.fogParams[3] = int(avgVec3(image.fogParams))

    elif palette:
        for i in range(256):
            reflectivity[0] += palette[i * 3 + 0]
            reflectivity[1] += palette[i * 3 + 1]
            reflectivity[2] += palette[i * 3 + 2]

        vec = [ 0, 0, 0 ]

        divVec3(reflectivity, 256, vec)

        image.fogParams[0] = int(vec[0])
        image.fogParams[1] = int(vec[1])
        image.fogParams[2] = int(vec[2])

    image.type_ = PixFormat.Indexed32
    image.depth = 1

    reader.seek(mipsStart)

    indices = reader.read(resolution)

    return Image_AddIndexedImageToPack(indices, image.width, image.height)


def Image_AddIndexedImageToPack (indices : bytes, width : int, height : int) -> bool:
    global image

    resolution = width * height
    expandToRGBA = True

    if Image_CheckFlag(ILFlags.Keep8Bit) or isBitSet(image.flags, ImageFlags.HasLuma | ImageFlags.QuakeSky):
        expandToRGBA = False

    image.size = resolution

    if expandToRGBA:
        image.size *= 4
    else:
        Image_CopyPalette32bit()

    if not expandToRGBA:
        image.rgba = indices
    elif not Image_Copy8bitRGBA(indices, image.rgba, resolution):
        return False

    return True

def Image_CopyPalette32bit ():
    global image

    if image.palette:
        return

    image.palette = image.dCurrentPal

def Image_Copy8bitRGBA (indices : bytes, dest : list, resolution) -> bool:
    global image

    assert isinstance(indices, bytes) or isinstance(indices, list)
    assert isinstance(dest, list)
    assert resolution > 0

    if not indices or not image.dCurrentPal:
        return False

    indices = list(indices)

    if isBitSet(image.flags, ImageFlags.HasLuma):
        for i in range(resolution):
            if indices[i] >= 224:
                indices[i] = 0

    for r, g, b, a in image.dCurrentPal:
        if r != g or g != b:
            setBit(image.flags, ImageFlags.HasColor)
            break

    for index in indices:
        rgba = image.dCurrentPal[index]

        assert isinstance(rgba, list) and len(rgba) == 4

        dest.append(rgba)


    image.type = PixFormat.RGBA32

    return True


PALETTE_Q1 = b'\x00\x00\x00\x0f\x0f\x0f\x1f\x1f\x1f\x2f\x2f\x2f\x3f\x3f\x3f\x4b\x4b\x4b\x5b\x5b\x5b\x6b\x6b\x6b\x7b\x7b\x7b\x8b\x8b\x8b\x9b\x9b\x9b\xab\xab\xab\xbb\xbb\xbb\xcb\xcb\xcb\xdb\xdb\xdb\xeb\xeb\xeb\x0f\x0b\x07\x17\x0f\x0b\x1f\x17\x0b\x27\x1b\x0f\x2f\x23\x13\x37\x2b\x17\x3f\x2f\x17\x4b\x37\x1b\x53\x3b\x1b\x5b\x43\x1f\x63\x4b\x1f\x6b\x53\x1f\x73\x57\x1f\x7b\x5f\x23\x83\x67\x23\x8f\x6f\x23\x0b\x0b\x0f\x13\x13\x1b\x1b\x1b\x27\x27\x27\x33\x2f\x2f\x3f\x37\x37\x4b\x3f\x3f\x57\x47\x47\x67\x4f\x4f\x73\x5b\x5b\x7f\x63\x63\x8b\x6b\x6b\x97\x73\x73\xa3\x7b\x7b\xaf\x83\x83\xbb\x8b\x8b\xcb\x00\x00\x00\x07\x07\x00\x0b\x0b\x00\x13\x13\x00\x1b\x1b\x00\x23\x23\x00\x2b\x2b\x07\x2f\x2f\x07\x37\x37\x07\x3f\x3f\x07\x47\x47\x07\x4b\x4b\x0b\x53\x53\x0b\x5b\x5b\x0b\x63\x63\x0b\x6b\x6b\x0f\x07\x00\x00\x0f\x00\x00\x17\x00\x00\x1f\x00\x00\x27\x00\x00\x2f\x00\x00\x37\x00\x00\x3f\x00\x00\x47\x00\x00\x4f\x00\x00\x57\x00\x00\x5f\x00\x00\x67\x00\x00\x6f\x00\x00\x77\x00\x00\x7f\x00\x00\x13\x13\x00\x1b\x1b\x00\x23\x23\x00\x2f\x2b\x00\x37\x2f\x00\x43\x37\x00\x4b\x3b\x07\x57\x43\x07\x5f\x47\x07\x6b\x4b\x0b\x77\x53\x0f\x83\x57\x13\x8b\x5b\x13\x97\x5f\x1b\xa3\x63\x1f\xaf\x67\x23\x23\x13\x07\x2f\x17\x0b\x3b\x1f\x0f\x4b\x23\x13\x57\x2b\x17\x63\x2f\x1f\x73\x37\x23\x7f\x3b\x2b\x8f\x43\x33\x9f\x4f\x33\xaf\x63\x2f\xbf\x77\x2f\xcf\x8f\x2b\xdf\xab\x27\xef\xcb\x1f\xff\xf3\x1b\x0b\x07\x00\x1b\x13\x00\x2b\x23\x0f\x37\x2b\x13\x47\x33\x1b\x53\x37\x23\x63\x3f\x2b\x6f\x47\x33\x7f\x53\x3f\x8b\x5f\x47\x9b\x6b\x53\xa7\x7b\x5f\xb7\x87\x6b\xc3\x93\x7b\xd3\xa3\x8b\xe3\xb3\x97\xab\x8b\xa3\x9f\x7f\x97\x93\x73\x87\x8b\x67\x7b\x7f\x5b\x6f\x77\x53\x63\x6b\x4b\x57\x5f\x3f\x4b\x57\x37\x43\x4b\x2f\x37\x43\x27\x2f\x37\x1f\x23\x2b\x17\x1b\x23\x13\x13\x17\x0b\x0b\x0f\x07\x07\xbb\x73\x9f\xaf\x6b\x8f\xa3\x5f\x83\x97\x57\x77\x8b\x4f\x6b\x7f\x4b\x5f\x73\x43\x53\x6b\x3b\x4b\x5f\x33\x3f\x53\x2b\x37\x47\x23\x2b\x3b\x1f\x23\x2f\x17\x1b\x23\x13\x13\x17\x0b\x0b\x0f\x07\x07\xdb\xc3\xbb\xcb\xb3\xa7\xbf\xa3\x9b\xaf\x97\x8b\xa3\x87\x7b\x97\x7b\x6f\x87\x6f\x5f\x7b\x63\x53\x6b\x57\x47\x5f\x4b\x3b\x53\x3f\x33\x43\x33\x27\x37\x2b\x1f\x27\x1f\x17\x1b\x13\x0f\x0f\x0b\x07\x6f\x83\x7b\x67\x7b\x6f\x5f\x73\x67\x57\x6b\x5f\x4f\x63\x57\x47\x5b\x4f\x3f\x53\x47\x37\x4b\x3f\x2f\x43\x37\x2b\x3b\x2f\x23\x33\x27\x1f\x2b\x1f\x17\x23\x17\x0f\x1b\x13\x0b\x13\x0b\x07\x0b\x07\xff\xf3\x1b\xef\xdf\x17\xdb\xcb\x13\xcb\xb7\x0f\xbb\xa7\x0f\xab\x97\x0b\x9b\x83\x07\x8b\x73\x07\x7b\x63\x07\x6b\x53\x00\x5b\x47\x00\x4b\x37\x00\x3b\x2b\x00\x2b\x1f\x00\x1b\x0f\x00\x0b\x07\x00\x00\x00\xff\x0b\x0b\xef\x13\x13\xdf\x1b\x1b\xcf\x23\x23\xbf\x2b\x2b\xaf\x2f\x2f\x9f\x2f\x2f\x8f\x2f\x2f\x7f\x2f\x2f\x6f\x2f\x2f\x5f\x2b\x2b\x4f\x23\x23\x3f\x1b\x1b\x2f\x13\x13\x1f\x0b\x0b\x0f\x2b\x00\x00\x3b\x00\x00\x4b\x07\x00\x5f\x07\x00\x6f\x0f\x00\x7f\x17\x07\x93\x1f\x07\xa3\x27\x0b\xb7\x33\x0f\xc3\x4b\x1b\xcf\x63\x2b\xdb\x7f\x3b\xe3\x97\x4f\xe7\xab\x5f\xef\xbf\x77\xf7\xd3\x8b\xa7\x7b\x3b\xb7\x9b\x37\xc7\xc3\x37\xe7\xe3\x57\x7f\xbf\xff\xab\xe7\xff\xd7\xff\xff\x67\x00\x00\x8b\x00\x00\xb3\x00\x00\xd7\x00\x00\xff\x00\x00\xff\xf3\x93\xff\xf7\xc7\xff\xff\xff\x9f\x5b\x53'
PALETTE_HL = b'\x00\x00\x00\x0f\x0f\x0f\x1f\x1f\x1f\x2f\x2f\x2f\x3f\x3f\x3f\x4b\x4b\x4b\x5b\x5b\x5b\x6b\x6b\x6b\x7b\x7b\x7b\x8b\x8b\x8b\x9b\x9b\x9b\xab\xab\xab\xbb\xbb\xbb\xcb\xcb\xcb\xdb\xdb\xdb\xeb\xeb\xeb\x0f\x0b\x07\x17\x0f\x0b\x1f\x17\x0b\x27\x1b\x0f\x2f\x23\x13\x37\x2b\x17\x3f\x2f\x17\x4b\x37\x1b\x53\x3b\x1b\x5b\x43\x1f\x63\x4b\x1f\x6b\x53\x1f\x73\x57\x1f\x7b\x5f\x23\x83\x67\x23\x8f\x6f\x23\x0b\x0b\x0f\x13\x13\x1b\x1b\x1b\x27\x27\x27\x33\x2f\x2f\x3f\x37\x37\x4b\x3f\x3f\x57\x47\x47\x67\x4f\x4f\x73\x5b\x5b\x7f\x63\x63\x8b\x6b\x6b\x97\x73\x73\xa3\x7b\x7b\xaf\x83\x83\xbb\x8b\x8b\xcb\x00\x00\x00\x07\x07\x00\x0b\x0b\x00\x13\x13\x00\x1b\x1b\x00\x23\x23\x00\x2b\x2b\x07\x2f\x2f\x07\x37\x37\x07\x3f\x3f\x07\x47\x47\x07\x4b\x4b\x0b\x53\x53\x0b\x5b\x5b\x0b\x63\x63\x0b\x6b\x6b\x0f\x07\x00\x00\x0f\x00\x00\x17\x00\x00\x1f\x00\x00\x27\x00\x00\x2f\x00\x00\x37\x00\x00\x3f\x00\x00\x47\x00\x00\x4f\x00\x00\x57\x00\x00\x5f\x00\x00\x67\x00\x00\x6f\x00\x00\x77\x00\x00\x7f\x00\x00\x13\x13\x00\x1b\x1b\x00\x23\x23\x00\x2f\x2b\x00\x37\x2f\x00\x43\x37\x00\x4b\x3b\x07\x57\x43\x07\x5f\x47\x07\x6b\x4b\x0b\x77\x53\x0f\x83\x57\x13\x8b\x5b\x13\x97\x5f\x1b\xa3\x63\x1f\xaf\x67\x23\x23\x13\x07\x2f\x17\x0b\x3b\x1f\x0f\x4b\x23\x13\x57\x2b\x17\x63\x2f\x1f\x73\x37\x23\x7f\x3b\x2b\x8f\x43\x33\x9f\x4f\x33\xaf\x63\x2f\xbf\x77\x2f\xcf\x8f\x2b\xdf\xab\x27\xef\xcb\x1f\xff\xf3\x1b\x0b\x07\x00\x1b\x13\x00\x2b\x23\x0f\x37\x2b\x13\x47\x33\x1b\x53\x37\x23\x63\x3f\x2b\x6f\x47\x33\x7f\x53\x3f\x8b\x5f\x47\x9b\x6b\x53\xa7\x7b\x5f\xb7\x87\x6b\xc3\x93\x7b\xd3\xa3\x8b\xe3\xb3\x97\xab\x8b\xa3\x9f\x7f\x97\x93\x73\x87\x8b\x67\x7b\x7f\x5b\x6f\x77\x53\x63\x6b\x4b\x57\x5f\x3f\x4b\x57\x37\x43\x4b\x2f\x37\x43\x27\x2f\x37\x1f\x23\x2b\x17\x1b\x23\x13\x13\x17\x0b\x0b\x0f\x07\x07\xbb\x73\x9f\xaf\x6b\x8f\xa3\x5f\x83\x97\x57\x77\x8b\x4f\x6b\x7f\x4b\x5f\x73\x43\x53\x6b\x3b\x4b\x5f\x33\x3f\x53\x2b\x37\x47\x23\x2b\x3b\x1f\x23\x2f\x17\x1b\x23\x13\x13\x17\x0b\x0b\x0f\x07\x07\xdb\xc3\xbb\xcb\xb3\xa7\xbf\xa3\x9b\xaf\x97\x8b\xa3\x87\x7b\x97\x7b\x6f\x87\x6f\x5f\x7b\x63\x53\x6b\x57\x47\x5f\x4b\x3b\x53\x3f\x33\x43\x33\x27\x37\x2b\x1f\x27\x1f\x17\x1b\x13\x0f\x0f\x0b\x07\x6f\x83\x7b\x67\x7b\x6f\x5f\x73\x67\x57\x6b\x5f\x4f\x63\x57\x47\x5b\x4f\x3f\x53\x47\x37\x4b\x3f\x2f\x43\x37\x2b\x3b\x2f\x23\x33\x27\x1f\x2b\x1f\x17\x23\x17\x0f\x1b\x13\x0b\x13\x0b\x07\x0b\x07\xff\xf3\x1b\xef\xdf\x17\xdb\xcb\x13\xcb\xb7\x0f\xbb\xa7\x0f\xab\x97\x0b\x9b\x83\x07\x8b\x73\x07\x7b\x63\x07\x6b\x53\x00\x5b\x47\x00\x4b\x37\x00\x3b\x2b\x00\x2b\x1f\x00\x1b\x0f\x00\x0b\x07\x00\x00\x00\xff\x0b\x0b\xef\x13\x13\xdf\x1b\x1b\xcf\x23\x23\xbf\x2b\x2b\xaf\x2f\x2f\x9f\x2f\x2f\x8f\x2f\x2f\x7f\x2f\x2f\x6f\x2f\x2f\x5f\x2b\x2b\x4f\x23\x23\x3f\x1b\x1b\x2f\x13\x13\x1f\x0b\x0b\x0f\x2b\x00\x00\x3b\x00\x00\x4b\x07\x00\x5f\x07\x00\x6f\x0f\x00\x7f\x17\x07\x93\x1f\x07\xa3\x27\x0b\xb7\x33\x0f\xc3\x4b\x1b\xcf\x63\x2b\xdb\x7f\x3b\xe3\x97\x4f\xe7\xab\x5f\xef\xbf\x77\xf7\xd3\x8b\xa7\x7b\x3b\xb7\x9b\x37\xc7\xc3\x37\xe7\xe3\x57\x00\xff\x00\xab\xe7\xff\xd7\xff\xff\x67\x00\x00\x8b\x00\x00\xb3\x00\x00\xd7\x00\x00\xff\x00\x00\xff\xf3\x93\xff\xf7\xc7\xff\xff\xff\x9f\x5b\x53'

d_8to24table = [ [ 0, 0, 0, 0 ] for _ in range(256) ]
d_8toQ1table = [ [ 0, 0, 0, 0 ] for _ in range(256) ]
d_8toHLtable = [ [ 0, 0, 0, 0 ] for _ in range(256) ]

isQ1PaletteInit = False
isHLPaletteInit = False


def Image_ComparePalette (palette):
    if not palette:
        return ImagePalette.Invalid
    elif palette[:765] == PALETTE_Q1[:765]:
        return ImagePalette.Quake1
    elif palette[:765] == PALETTE_HL[:765]:
        return ImagePalette.HalfLife

    return ImagePalette.Custom

def Image_GetPaletteLMP (palette, renderMode):
    global image, d_8to24table

    image.dRenderMode = renderMode

    if palette:
        table = d_8to24table.copy()
        Image_SetPalette(palette, table)
        image.dCurrentPal = table
    else:
        match renderMode:
            case ImageLumpType.Quake1:
                Image_GetPaletteQ1()
            case ImageLumpType.HalfLife:
                Image_GetPaletteHL()
            case _:
                Image_GetPaletteHL()

def Image_SetPalette (palette, table):
    global image

    match image.dRenderMode:
        case ImageLumpType.Normal:
            for i in range(256):
                table[i] = [
                    palette[i * 3 + 0],
                    palette[i * 3 + 1],
                    palette[i * 3 + 2],
                    0xFF
                ]
        case ImageLumpType.Gradient:
            for i in range(256):
                table[i] = [
                    palette[765],
                    palette[766],
                    palette[767],
                    i
                ]
        case ImageLumpType.Masked:
            for i in range(255):
                table[i] = [
                    palette[i * 3 + 0],
                    palette[i * 3 + 1],
                    palette[i * 3 + 2],
                    0xFF
                ]

                table[255] = [ 0, 0, 0, 0 ]
        case ImageLumpType.Extended:
            for i in range(256):
                table[i] = [
                    palette[i * 4 + 0],
                    palette[i * 4 + 1],
                    palette[i * 4 + 2],
                    palette[i * 4 + 3],
                ]

def Image_GetPaletteQ1 ():
    global image, d_8toQ1table, isQ1PaletteInit

    if not isQ1PaletteInit:
        image.dRenderMode = ImageLumpType.Normal
        Image_SetPalette(PALETTE_Q1, d_8toQ1table)
        d_8toQ1table[255] = [ 0, 0, 0, 0 ]
        isQ1PaletteInit = True

    image.dRenderMode = ImageLumpType.Quake1
    image.dCurrentPal = d_8toQ1table.copy()

def Image_GetPaletteHL ():
    global image, d_8toHLtable, isHLPaletteInit

    if not isHLPaletteInit:
        image.dRenderMode = ImageLumpType.Normal
        Image_SetPalette(PALETTE_HL, d_8toHLtable)
        isHLPaletteInit = True

    image.dRenderMode = ImageLumpType.HalfLife
    image.dCurrentPal = d_8toHLtable.copy()

LOAD_FUNCS = [
    ('dds', Image_LoadDDS, ILHint.No),    # dds for world and studio models
    ('tga', Image_LoadTGA, ILHint.No),    # hl vgui menus
    ('bmp', Image_LoadBMP, ILHint.No),    # WON menu images
    ('mip', Image_LoadMIP, ILHint.No),    # hl textures from wad or buffer
    ('mdl', Image_LoadMDL, ILHint.HL),    # hl studio model skins
    ('spr', Image_LoadSPR, ILHint.HL),    # hl sprite frames
    ('lmp', Image_LoadLMP, ILHint.No),    # hl menu images (cached.wad etc)
    ('fnt', Image_LoadFNT, ILHint.HL),    # hl console font (fonts.wad etc)
    ('pal', Image_LoadPAL, ILHint.No),    # install studio\sprite palette
]

# WAD_TYPES = [
#     ('pal', WADLumpType.Palette),  # palette
#     ('dds', WADLumpType.DDS),      # DDS image
#     ('lmp', WADLumpType.GFX),      # quake1, hl pic
#     ('fnt', WADLumpType.QFont),    # hl qfonts
#     ('mip', WADLumpType.Mip),      # hl/q1 mip
#     ('txt', WADLumpType.Script),   # scripts
# ]

image = Image()

def Image_SetForceFlags (flags):
    global image
    image.forceFlags = setBit(image.forceFlags, flags)

def Image_CheckFlag (flags):
    global image

    if isBitSet(image.forceFlags, flags):
        return True

    if isBitSet(image.cmdFlags, flags):
        return True

    return False

def Image_AddCmdFlags (flags):
    global image
    image.cmdFlags = setBit(image.cmdFlags, flags)

def Image_Reset ():
    global image
    # reset global variables
    image.width        = 0
    image.height       = 0
    image.depth        = 0
    image.sourceWidth  = 0
    image.sourceHeight = 0
    image.sourceType   = 0
    image.numMips      = 0
    image.numSides     = 0
    image.flags        = 0
    image.encode       = DXTEncode.Default
    image.type_        = PixFormat.Unknown
    image.fogParams    = [ 0, 0, 0, 0 ]  # rgba_t

    # pointers will be saved with prevoius picture struct
    # don't care about it
    image.palette = None
    image.cubeMap = None
    image.rgba    = []
    image.ptr     = 0
    image.size    = 0


def GL_LoadTexture (name, buf, size, flags):
    # TODO: is it right?
    Image_AddCmdFlags(ILFlags.UseLerping)
    Image_AddCmdFlags(ILFlags.AllowOverwrite)
    Image_AddCmdFlags(ILFlags.DDSHardware)

    picFlags = 0

    if isBitSet(flags, TextureFlags.NoFlipTGA):
        picFlags = setBit(picFlags, ILFlags.DontFlipTGA)

    if isBitSet(flags, TextureFlags.KeepSource) and not isBitSet(flags, TextureFlags.ExpandSource):
        picFlags = setBit(picFlags, ILFlags.Keep8Bit)

    Image_SetForceFlags(picFlags)

    # TODO: Convert image to texture
    return FS_LoadImage(name, buf, size)


def FS_LoadImage (filename, buffer, size) -> RGBData | None:
    ext = getExt(filename, True)
    anyFormat = True
    loadName = filename

    Image_Reset()

    if ext:
        for loadExt, *_ in LOAD_FUNCS:
            if loadExt.lower() == ext:
                loadName = dropExt(loadName)
                anyFormat = False
                break

    # assert filename[0] != '#'  # btns_0.bmp
    # "#maps/c0a0.bsp:origin"
    if filename[0] == '#' and buffer and size:
        f = MemReader(buffer, filename)

        for loadExt, loadFn, loadHint in LOAD_FUNCS:
            if anyFormat or loadExt.lower() == ext:
                image.hint = loadHint

                if loadFn(f):
                    return ImagePack()
    else:
        for loadExt, loadFn, loadHint in LOAD_FUNCS:
            if anyFormat or loadExt.lower() == ext:
                path = loadName + '.' + loadExt
                image.hint = loadHint
                f = openAnyFile(path)

                if f and f.getSize():
                    if loadFn(f):
                        return ImagePack()

    image.forceFlags = 0

    return None

    # assert False, 'engine/common/imagelib/img_main.c:265'


def ImagePack () -> RGBData:
    global image

    pack = RGBData()

    image.forceFlags = 0

    if image.cubeMap:
        image.flags |= ImageFlags.CubeMap
        pack.buffer = image.cubeMap
        pack.width  = image.sourceWidth
        pack.height = image.sourceHeight
        pack.type_  = image.sourceType
        pack.size   = image.size * image.numSides
    else:
        pack.buffer = image.rgba
        pack.width  = image.width
        pack.height = image.height
        pack.depth  = image.depth
        pack.type_  = image.type_
        pack.size   = image.size

    pack.fogParams[0] = image.fogParams[0]
    pack.fogParams[1] = image.fogParams[1]
    pack.fogParams[2] = image.fogParams[2]
    pack.fogParams[3] = image.fogParams[3]

    pack.flags   = image.flags
    pack.numMips = image.numMips
    pack.palette = image.palette
    pack.encode  = image.encode

    return pack

# ----------------------------------------------------------------------------------------------------------------------
# ----------------------------------------------------------------------------------------------------------------------
# ----------------------------------------------------------------------------------------------------------------------

def __test__ ():
    from bfw.utils import toJson

    types = {}

    mapping = {}

    keys = sorted(list(set(types.keys())))

    fields = {}

    for k in keys:
        type_ = types[k]
        fields[k] = {
            'type': mapping.get(type_, 'BSPEntityFiledType.Unknown')
        }

    print(toJson(fields).replace('"', "'"))



if __name__ == '__main__':
    __test__()