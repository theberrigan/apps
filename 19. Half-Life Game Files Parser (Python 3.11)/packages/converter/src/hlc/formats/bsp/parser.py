from re import split

from ...common import bfw, GAME_DIR
from ...maths import *
from ...utils import clearBounds, addPointToBounds, boundVertex
from ._temp import *
from ..nod import Graph
from ..wad import getWADs, WADLumpType
from ..vdf import *
from .types import *
from .consts import *

from bfw.reader import *
from bfw.utils import *
from bfw.types.enums import Enum
from bfw.native.limits import MAX_U32



# SIMPLE CONSTS
# ----------------------------------------------------------------------------------------------------------------------

BSP_VERSION_HL  = 30  # HLBSP_VERSION
BSP_MAX_HULLS   = 4   # MAX_MAP_HULLS
BSP_LUMPS_COUNT = 15  # HEADER_LUMPS

LM_STYLE_COUNT       = 4   # LM_STYLES
LM_SAMPLE_SIZE       = 16  # LM_SAMPLE_SIZE
LM_SAMPLE_EXTRA_SIZE = 8   # LM_SAMPLE_EXTRASIZE
MAX_LIGHT_MAPS       = 4   # MAXLIGHTMAPS
SUBDIVIDE_SIZE       = 64  # SUBDIVIDE_SIZE



# ENUMS
# ----------------------------------------------------------------------------------------------------------------------

# LUMP_* - bspfile.h
class BSPLumpType (Enum):
    Entities     = 0   # LUMP_ENTITIES
    Planes       = 1   # LUMP_PLANES
    Textures     = 2   # LUMP_TEXTURES -- internal textures
    Vertices     = 3   # LUMP_VERTEXES
    Visibility   = 4   # LUMP_VISIBILITY
    Nodes        = 5   # LUMP_NODES
    TextureInfos = 6   # LUMP_TEXINFO
    Faces        = 7   # LUMP_FACES
    Lighting     = 8   # LUMP_LIGHTING
    ClipNodes    = 9   # LUMP_CLIPNODES
    Leaves       = 10  # LUMP_LEAFS
    MarkFaces    = 11  # LUMP_MARKSURFACES
    Edges        = 12  # LUMP_EDGES
    FaceEdges    = 13  # LUMP_SURFEDGES
    Models       = 14  # LUMP_MODELS -- internal submodels


# SURF_* - bspfile.h
class BSPFaceFlags (Enum):
    PlaneBack     = 1 << 1    # SURF_PLANEBACK      -- plane should be negated
    DrawSky       = 1 << 2    # SURF_DRAWSKY        -- sky surface
    DrawTurbQuads = 1 << 3    # SURF_DRAWTURB_QUADS -- all subidivided polygons are quads
    DrawTurb      = 1 << 4    # SURF_DRAWTURB       -- warp surface
    DrawTiled     = 1 << 5    # SURF_DRAWTILED      -- face without lighmap
    Conveyor      = 1 << 6    # SURF_CONVEYOR       -- scrolled texture (was SURF_DRAWBACKGROUND)
    Underwater    = 1 << 7    # SURF_UNDERWATER     -- caustics
    Transparent   = 1 << 8    # SURF_TRANSPARENT    -- it's a transparent texture (was SURF_DONTWARP)


# TEX_* - bspfile.h
class BSPTextureFlags (Enum):
    Special       = 1 << 0    # TEX_SPECIAL        -- sky or slime, no lightmap or 256 subdivision
    WorldLuxels   = 1 << 1    # TEX_WORLD_LUXELS   -- alternative lightmap matrix will be used (luxels per world units instead of luxels per texels)
    AxialLuxels   = 1 << 2    # TEX_AXIAL_LUXELS   -- force world luxels to axial positive scales
    ExtraLightMap = 1 << 3    # TEX_EXTRA_LIGHTMAP -- bsp31 legacy - using 8 texels per luxel instead of 16 texels per luxel
    Scroll        = 1 << 6    # TEX_SCROLL         -- Doom special FX



# COMPOUND CONSTS
# ----------------------------------------------------------------------------------------------------------------------

BSP_LUMP_ENTRY_SIZES = {
    BSPLumpType.Entities:     1,
    BSPLumpType.Planes:       20,
    BSPLumpType.Textures:     1,
    BSPLumpType.Vertices:     12,
    BSPLumpType.Visibility:   1,
    BSPLumpType.Nodes:        24,
    BSPLumpType.TextureInfos: 40,
    BSPLumpType.Faces:        20,
    BSPLumpType.Lighting:     3,  # == bsp.lightMapSamples == 3
    BSPLumpType.ClipNodes:    8,
    BSPLumpType.Leaves:       28,
    BSPLumpType.MarkFaces:    2,
    BSPLumpType.Edges:        4,
    BSPLumpType.FaceEdges:    4,
    BSPLumpType.Models:       64,
}


# CLASSES
# ----------------------------------------------------------------------------------------------------------------------

# world_static_t
class World:
    def __init__ (self):
        self.isLoading : bool = False  # qboolean loading -- true if worldmodel is loading TODO: remove
        self.flags     : int  = 0      # int flags -- misc flags

        # mapstats info
        # char message[2048] -- just for debug
        # char compiler[256] -- map compiler
        # char generator[256] -- map editor

        # translucent sorted array
        # sortedface_t *draw_surfaces -- used for sorting translucent surfaces
        self.maxFaces  : int = 0   # int max_surfaces -- max surfaces per submodel (for all models)
        # hull_model_t *hull_models
        # int num_hull_models

        # visibility info
        self.visBytes  : int  = 0  # size_t visbytes -- cluster size
        self.fatBytes  : int  = 0  # size_t fatbytes -- fatpvs size

        # world bounds
        self.mins : Vec3 = [ 0, 0, 0 ]    # vec3_t mins -- real accuracy world bounds
        self.maxs : Vec3 = [ 0, 0, 0 ]    # vec3_t maxs
        self.size : Vec3 = [ 0, 0, 0 ]    # vec3_t size


class BSPHeader:
    def __init__ (self):
        self.version : int           = -1
        self.lumps   : list[BSPLump] = []


class BSPLump:
    def __init__ (self):
        self.offset : int = -1
        self.size   : int = 0
        self.count  : int = 0


# dmodel_t - bspfile.h
class BSPModel:
    def __init__ (self):
        self.mins           : Vec3      = [ 0, 0, 0 ]  # vec3_t mins
        self.maxs           : Vec3      = [ 0, 0, 0 ]  # vec3_t maxs
        self.origin         : Vec3      = [ 0, 0, 0 ]  # vec3_t origin -- for sounds or lights
        self.headNode       : list[int] = [ 0 ] * BSP_MAX_HULLS  # int headnode[MAX_MAP_HULLS]
        self.visLeaves      : int       = 0   # int visleafs -- not including the solid leaf 0
        self.firstFaceIndex : int       = -1  # int firstface
        self.faceCount      : int       = 0   # int numfaces


# dclipnode32_t - bspfile.h
class BSPClipNode:
    def __init__ (self):
        TChildren = list[int, int] | None

        self.planeIndex : int       = -1    # int planenum
        self.children   : TChildren = None  # int children[2] -- negative numbers are contents


class BSP:
    def __init__ (self):
        self.filePath : str | None       = None
        self.reader   : Reader | None    = None
        self.header   : BSPHeader | None = None
        self.world    : World | None     = None

        # TODO: move somewhere
        self.loadModelFlags  = 0

        self.wadNames        : list[str]              = []    # "halflife", "decals", ...
        self.entityList                               = []    # dict
        self.message         : str | None             = None  # "Unforeseen Consequences"
        self.planeCount      : int                    = 0
        self.planes          : list[ModelPlane]       = []
        self.subModelCount   : int                    = 0
        self.subModels       : list[BSPModel]         = []
        self.vertexCount     : int                    = 0
        self.vertices        : Vec3                   = []
        self.faceEdgeCount   : int                    = 0
        self.faceEdges       : list[int]              = []
        self.textures                                 = []  # TODO
        self.visDataSize     : int                    = 0
        self.visData         : bytes | None           = None
        self.texInfoCount    : int                    = 0
        self.texInfos        : list[ModelTextureInfo] = []
        self.faceCount       : int                    = 0
        self.faces           : list[ModelFace]        = []
        self.edgeCount       : int                    = 0
        self.edges           : list[ModelEdge]        = []
        self.lightMapSamples : int                    = 3   # how many channels (samples) in a light map pixel (by default 3: R, G and B)
        self.lightDataCount  : int                    = 0
        self.lightData       : list[RGB]              = []
        self.markFaceCount   : int                    = 0
        self.markFaces       : list[ModelFace]        = []
        self.leafCount       : int                    = 0
        self.leaves          : list[ModelLeaf]        = []
        self.nodeCount       : int                    = 0
        self.nodes           : list[ModelNode]        = []
        self.clipNodeCount   : int                    = 0
        self.clipNodes       : list[BSPClipNode]      = []

        self.nodeGraph       : Graph | None           = None

    @classmethod
    def fromFile (cls, filePath : str):
        bsp = cls()

        bsp.parseFile(filePath)

        return bsp

    def parseFile (self, filePath : str):
        self.filePath = filePath

        if not isFile(filePath):
            raise Exception(f'File does not exist: { filePath }')

        self.world = World()

        self.world.isLoading = True

        if self.world.isLoading:
            self.world.flags = 0
            # bmod->isworld = true

        # TODO: move somewhere else
        # engine/client/gl_vidnt.c:1819
        # engine/common/imagelib/img_utils.c:150
        Image_AddCmdFlags(ILFlags.DDSHardware)
        Image_AddCmdFlags(ILFlags.UseLerping | ILFlags.AllowOverwrite)

        self.reader = openFile(filePath, ReaderType.Mem)

        self.readHeader()

        #                        lumpIndex            entryType    rawDataPtr          entryCount
        self.readEntities()      # LUMP_ENTITIES      byte         srcmodel.entdata    srcmodel.entdatasize
        self.readPlanes()        # LUMP_PLANES        dplane_t     srcmodel.planes     srcmodel.numplanes
        self.readSubModels()     # LUMP_MODELS        dmodel_t     srcmodel.submodels  srcmodel.numsubmodels
        self.readVertices()      # LUMP_VERTEXES      dvertex_t    srcmodel.vertexes   srcmodel.numvertexes
        self.readEdges()         # LUMP_EDGES         dedge_t      srcmodel.edges      srcmodel.numedges
        self.readFaceEdges()     # LUMP_SURFEDGES     dsurfedge_t  srcmodel.surfedges  srcmodel.numsurfedges
        self.readTextures()      # LUMP_TEXTURES      byte         srcmodel.textures   srcmodel.texdatasize
        self.readVisibility()    # LUMP_VISIBILITY    byte         srcmodel.visdata    srcmodel.visdatasize
        self.readTextureInfos()  # LUMP_TEXINFO       dtexinfo_t   srcmodel.texinfo    srcmodel.numtexinfo
        self.readFaces()         # LUMP_FACES         dface_t      srcmodel.surfaces   srcmodel.numsurfaces
        self.readLighting()      # LUMP_LIGHTING      byte         srcmodel.lightdata  srcmodel.lightdatasize
        self.readMarkFaces()     # LUMP_MARKSURFACES  dmarkface_t  srcmodel.markfaces  srcmodel.nummarkfaces
        self.readLeaves()        # LUMP_LEAFS         dleaf_t      srcmodel.leafs      srcmodel.numleafs
        self.readNodes()         # LUMP_NODES         dnode_t      srcmodel.nodes      srcmodel.numnodes
        self.readClipNodes()     # LUMP_CLIPNODES     dclipnode_t  srcmodel.clipnodes  srcmodel.numclipnodes

        self.loadEntities()
        self.loadNodeGraph()

    def readHeader (self):
        self.header = BSPHeader()

        self.header.version = version = self.reader.i32()
        self.header.lumps   = lumps   = [ BSPLump() for _ in range(BSP_LUMPS_COUNT) ]

        if version != BSP_VERSION_HL:
            raise Exception(f'Unsupported BSP version: { version }')

        for lumpIndex in range(BSP_LUMPS_COUNT):
            offset, size = self.reader.i32(2)

            assert offset > 0 and size > 0, 'Empty lump?'

            entrySize = BSP_LUMP_ENTRY_SIZES[lumpIndex]

            assert (size % entrySize) == 0

            lump = lumps[lumpIndex]

            lump.offset = offset
            lump.size   = size
            lump.count  = size // entrySize

    # Mod_LoadEntities
    def readEntities (self):
        lump = self.header.lumps[BSPLumpType.Entities]

        self.reader.seek(lump.offset)

        # read vdf file
        data = self.reader.read(lump.size)

        sections = VDF.fromBuffer(data)

        assert isinstance(sections, list)

        self.wadNames   = wadNames = []
        self.entityList = sections
        self.message    = sections[0].get('message')

        for section in sections:
            wadPaths = section.get('wad')  # \quiver\valve\liquids.wad

            if not wadPaths:
                continue

            for wadPath in wadPaths.split(';'):
                baseName = getFileName(wadPath.strip()).lower()

                if baseName not in self.wadNames:
                    wadNames.append(baseName)

        assert self.reader.tell() == (lump.offset + lump.size)

    # Mod_LoadPlanes
    def readPlanes (self):
        lump = self.header.lumps[BSPLumpType.Planes]

        self.reader.seek(lump.offset)

        self.planeCount = count  = lump.count
        self.planes     = planes = [ ModelPlane() for _ in range(count) ]

        for plane in planes:
            # read dplane_t
            normal   = self.reader.vec3()
            dist     = self.reader.f32()
            type_    = self.reader.i32()  # PlaneType
            signBits = 0

            for j, value in enumerate(normal):
                if value < 0:
                    signBits = signBits | (1 << j)

            assert PlaneType.X <= type_ <= PlaneType.AnyZ
            assert lenVec3(normal) >= 0.5, 'bad normal for plane'

            plane.normal   = normal
            plane.dist     = dist
            plane.type_    = type_
            plane.signBits = signBits

        assert self.reader.tell() == (lump.offset + lump.size)

    # Mod_LoadSubmodels
    def readSubModels (self):
        lump = self.header.lumps[BSPLumpType.Models]

        self.reader.seek(lump.offset)

        self.subModelCount = count  = lump.count
        self.subModels     = models = [ BSPModel() for _ in range(count) ]

        for i in range(count):
            # read dmodel_t
            mins           = self.reader.vec3()  # vec3_t mins
            maxs           = self.reader.vec3()  # vec3_t maxs
            origin         = self.reader.vec3()  # vec3_t origin -- for sounds or lights
            headNode       = self.reader.i32(BSP_MAX_HULLS)  # int headnode[MAX_MAP_HULLS]
            visLeaves      = self.reader.i32()   # int visleafs -- not including the solid leaf 0
            firstFaceIndex = self.reader.i32()   # int firstface
            faceCount      = self.reader.i32()   # int numfaces

            for j in range(3):
                if mins[j] == 999999:
                    mins[j] = 0

                if maxs[j] == -999999:
                    maxs[j] = 0

                mins[j] -= 1
                maxs[j] += 1

            model = models[i]

            model.mins           = mins
            model.maxs           = maxs
            model.origin         = origin
            model.headNode       = headNode
            model.visLeaves      = visLeaves
            model.firstFaceIndex = firstFaceIndex
            model.faceCount      = faceCount

            # skip the world to save mem
            if i == 0:
                continue

            self.world.maxFaces = max(self.world.maxFaces, faceCount)

        assert self.reader.tell() == (lump.offset + lump.size)

    # Mod_LoadVertexes
    def readVertices (self):
        lump = self.header.lumps[BSPLumpType.Vertices]

        self.reader.seek(lump.offset)

        clearBounds(self.world.mins, self.world.maxs)

        self.vertexCount = count    = lump.count
        self.vertices    = vertices = []

        world = self.world

        for _ in range(count):
            # read dvertex_t
            vertex = self.reader.vec3()

            addPointToBounds(vertex, world.mins, world.maxs)

            vertices.append(vertex)

        subVec3(world.maxs, world.mins, world.size)

        for i in range(3):
            world.mins[i] -= 1
            world.maxs[i] += 1

        assert self.reader.tell() == (lump.offset + lump.size)

    # Mod_LoadEdges
    def readEdges (self):
        lump = self.header.lumps[BSPLumpType.Edges]

        self.reader.seek(lump.offset)

        self.edgeCount = count = lump.count
        self.edges     = edges = [ ModelEdge() for _ in range(count) ]

        for edge in edges:
            # read dedge_t
            edge.v = self.reader.u16(2)

        assert self.reader.tell() == (lump.offset + lump.size)

    # Mod_LoadSurfEdges
    def readFaceEdges (self):
        lump = self.header.lumps[BSPLumpType.FaceEdges]

        self.reader.seek(lump.offset)

        self.faceEdgeCount = lump.count
        self.faceEdges     = self.reader.i32(lump.count)

        assert self.reader.tell() == (lump.offset + lump.size)

    # Mod_LoadTextures
    def readTextures (self):
        lump = self.header.lumps[BSPLumpType.Textures]

        self.reader.seek(lump.offset)

        texCount   = self.reader.i32()
        texOffsets = self.reader.i32(texCount)  # relative to lump.offset

        # print(texCount)
        # sys.exit(0)

        textures = []

        for i in range(texCount):
            texOffset = texOffsets[i]

            if texOffset == -1:
                # TODO: create empty texture "*default" 16x16
                print('Empty texture')
                continue

            self.reader.seek(lump.offset + texOffset)

            name       = self.reader.string(16)
            width      = self.reader.u32()
            height     = self.reader.u32()
            mipOffsets = self.reader.u32(4)  # (each == 0) or (each > 0); ([0] == 0) or ([0] == 40) (size of this struct)

            assert name

            name = (name or f'miptex_{ i }').lower()

            hasCustomPalette = False

            # Check custom palette
            if mipOffsets[0] > 0:
                # 40 + size of 4 mip levels in bytes
                # 40 - size of this struct; == mipOffsets[3] + (width // 8) * (height // 8)
                entrySize  = MIP_HEADER_SIZE + ((width * height * 85) >> 6)
                nextOffset = lump.size

                for j in range(i + 1, texCount):
                    if texOffsets[j] != -1:
                        nextOffset = texOffsets[j]
                        break

                remaining = nextOffset - (texOffset + entrySize)

                hasCustomPalette = remaining >= 770

            # First look for textures in the archive, and then embedded in the BSP

            rgbData = None

            # If there is no nested textures, load from wads
            if mipOffsets[0] <= 0:
                # print('->', name)
                mipName = f'{ name }.mip'

                for j in range(len(self.wadNames) - 1, -1, -1):
                    wadName = self.wadNames[j] + '.wad'

                    texPath = wadName + '/' + mipName

                    isTextureFound = getWADs().hasEntry(texPath, WADLumpType.Mip)

                    if isTextureFound:
                        rgbData = GL_LoadTexture(texPath, None, 0, TextureFlags.AllowEmboss)
                        break

            if mipOffsets[0] > 0 and not rgbData:
                size = MIP_HEADER_SIZE + ((width * height * 85) >> 6)

                if hasCustomPalette:
                    size += MIP_PALETTE_BLOCK_SIZE

                self.reader.seek(lump.offset + texOffset)

                data = self.reader.read(size)

                bspPath = getRelPath(self.filePath, GAME_DIR).replace('\\', '/')

                internalPath = f'#{ bspPath }:{ name }.mip'

                rgbData = GL_LoadTexture(internalPath, data, len(data), TextureFlags.AllowEmboss)

                # print('-->', texture)

            if not rgbData:
                assert 0

            texture = Texture()

            texture.name   = name
            texture.data   = rgbData
            texture.width  = rgbData.width
            texture.height = rgbData.height

            textures.append(texture)

        textureCount = len(textures)

        for i in range(textureCount):
            texture = textures[i]

            if not texture or texture.name[0] not in '+-':
                continue

            if texture.animNext:
                continue

            anims    : list[Texture | None] = [ None ] * 10
            altAnims : list[Texture | None] = [ None ] * 10

            maxIndex    = texture.name[1]
            maxAltIndex = 0

            if '0' <= maxIndex <= '9':
                maxIndex = ord(maxIndex) - ord('0')
                maxAltIndex = 0
                anims[maxIndex] = texture
                maxIndex += 1
            elif 'a' <= maxIndex <= 'j':
                maxAltIndex = ord(maxIndex) - ord('a')
                maxIndex = 0
                altAnims[maxAltIndex] = texture
                maxAltIndex += 1
            else:
                assert 0

            for j in range(i + 1, textureCount):
                texture2 = textures[j]

                if not texture2 or texture2.name[0] not in '+-':
                    continue

                if texture.name[2:] != texture2.name[2:]:
                    continue

                index = texture2.name[1]

                if '0' <= index <= '9':
                    index = ord(index) - ord('0')
                    anims[index] = texture2
                    maxIndex = max(maxIndex, index + 1)
                elif 'a' <= index <= 'j':
                    index = ord(index) - ord('a')
                    altAnims[index] = texture2
                    maxAltIndex = max(maxAltIndex, index + 1)
                else:
                    assert 0

            for j in range(maxIndex):
                texture2 = anims[j]

                assert texture2

                texture2.animTotal = maxIndex * ANIM_CYCLE
                texture2.animMin   = j * ANIM_CYCLE
                texture2.animMax   = (j + 1) * ANIM_CYCLE
                texture2.animNext  = anims[(j + 1) % maxIndex]

                if maxAltIndex:
                    texture2.animAlt = altAnims[0]

            for j in range(maxAltIndex):
                texture2 = altAnims[j]

                assert texture2

                texture2.animTotal = maxAltIndex * ANIM_CYCLE
                texture2.animMin   = j * ANIM_CYCLE
                texture2.animMax   = (j + 1) * ANIM_CYCLE
                texture2.animNext  = altAnims[(j + 1) % maxAltIndex]

                if maxIndex:
                    texture2.animAlt = anims[0]

        self.textures = textures
        # outPath = joinPath(PROJECT_ROOT_DIR, '_images', f'{ name }.png')
        #
        # if not isFile(outPath):
        #     saveMipAsPNG(texture, outPath)

        # assert self.reader.tell() == (lump.offset + lump.size)

    # Mod_LoadVisibility
    def readVisibility (self):
        lump = self.header.lumps[BSPLumpType.Visibility]

        self.visDataSize = lump.size

        if self.visDataSize:
            self.reader.seek(lump.offset)

            self.visData = self.reader.read(self.visDataSize)
        else:
            self.visData = None

        assert self.reader.tell() == (lump.offset + lump.size)

    # Mod_LoadTexInfo
    def readTextureInfos (self):
        lump = self.header.lumps[BSPLumpType.TextureInfos]

        self.reader.seek(lump.offset)

        self.texInfoCount = lump.count
        self.texInfos     = [ ModelTextureInfo() for _ in range(self.texInfoCount) ]

        for info in self.texInfos:
            # read dtexinfo_t
            vectors = [                   # float vecs[2][4] -- texmatrix [s/t][xyz offset]
                self.reader.f32(4),
                self.reader.f32(4)
            ]
            texIndex = self.reader.i32()  # int	miptex
            flags    = self.reader.i16()  # short flags
            faceInfo = self.reader.i16()  # short faceinfo -- -1 no face info otherwise dfaceinfo_t

            assert 0 <= texIndex < len(self.textures)  # TODO: replace with self.textureCount
            assert not faceInfo, 'See engine/common/mod_bmodel.c:2117'

            info.vectors = vectors
            info.texture = self.textures[texIndex]
            info.flags   = flags

        assert self.reader.tell() == (lump.offset + lump.size)

    # Mod_LoadSurfaces
    def readFaces (self):
        lump = self.header.lumps[BSPLumpType.Faces]

        self.reader.seek(lump.offset)

        assert self.lightMapSamples == 3

        self.faceCount = count = lump.count
        self.faces     = faces = [ ModelFace() for _ in range(count) ]

        testLightSize      = -1
        nextLightMapOffset = -1
        prevLightMapOffset = -1

        for face in faces:
            # read dface_t
            planeIndex     = self.reader.u16()   # Plane the face is parallel to (self.planes[planeIndex])
            side           = self.reader.i16()   # [bool] Set if normal vector of the surface is opposite to corresponding plane's one
            firstEdgeIndex = self.reader.i32()   # Index of the first edge in self.faceEdges[firstEdgeIndex]
            edgeCount      = self.reader.i16()   # Number of consecutive surfedges (surface surfedges = self.faceEdges[firstEdgeIndex:firstEdgeIndex + edgeCount])
            texInfoIndex   = self.reader.i16()   # self.texInfos[texInfoIndex]
            styles         = self.reader.u8(LM_STYLE_COUNT)  # ???
            lightMapOffset = self.reader.i32()   # Offsets into the raw lightmap data (LUMP_LIGHTING[lightMapOffset:])

            assert (firstEdgeIndex + edgeCount) <= self.faceEdgeCount

            maxLightMaps = min(LM_STYLE_COUNT, MAX_LIGHT_MAPS)

            face.firstEdgeIndex = firstEdgeIndex
            face.edgeCount      = edgeCount
            face.flags          = 0
            face.plane          = self.planes[planeIndex]
            face.textureInfo    = self.texInfos[texInfoIndex]
            face.styles         = styles[:maxLightMaps]
            face.lightMapOffset = lightMapOffset

            texInfoFlags = face.textureInfo.flags
            texName      = face.textureInfo.texture.name

            if side:
                face.flags |= BSPFaceFlags.PlaneBack

            if texName.startswith('sky'):
                face.flags |= BSPFaceFlags.DrawSky

            if texName[0] == '*' and texName != '*default' or texName[0] == '!':
                face.flags |= BSPFaceFlags.DrawTurb

            if texName.startswith('water') or texName.startswith('laser'):
                face.flags |= BSPFaceFlags.DrawTurb

            if texName.startswith('scroll'):
                face.flags |= BSPFaceFlags.Conveyor

            if isBitSet(texInfoFlags, BSPTextureFlags.Scroll):
                face.flags |= BSPFaceFlags.Conveyor

            if texName.startswith('{scroll'):
                face.flags |= BSPFaceFlags.Conveyor | BSPFaceFlags.Transparent

            if texName[0] == '{':
                face.flags |= BSPFaceFlags.Transparent

            if isBitSet(texInfoFlags, BSPTextureFlags.Special):
                face.flags |= BSPFaceFlags.DrawTiled

            self.calcFaceBounds(face)
            self.calcFaceExtents(face)

            # grab the second sample to detect colored lighting
            if testLightSize > 0 and lightMapOffset != -1:
                if prevLightMapOffset < lightMapOffset < nextLightMapOffset:
                    nextLightMapOffset = lightMapOffset

            # grab the first sample to determine lightmap size
            if lightMapOffset != -1 and testLightSize == -1:
                sampleSize = self.getSampleSizeForFace(face)
                sMax = int((face.info.lightMapExtents[0] / sampleSize) + 1)
                tMax = int((face.info.lightMapExtents[1] / sampleSize) + 1)
                lightStyles = 0

                testLightSize = sMax * tMax

                # count styles to right compute testLightSize
                for j in range(MAX_LIGHT_MAPS):
                    if face.styles[j] == 255:
                        break

                    lightStyles += 1

                testLightSize *= lightStyles
                prevLightMapOffset = lightMapOffset
                nextLightMapOffset = 99999999

            if isBitSet(face.flags, BSPFaceFlags.DrawTurb):
                self.subdivideFaces(face)

        # now we have enough data to try to determine sample count per light map pixel
        if testLightSize > 0 and prevLightMapOffset != -1 and nextLightMapOffset not in [ -1, 99999999 ]:
            samples = (nextLightMapOffset - prevLightMapOffset) / testLightSize

            if samples != int(samples):
                testLightSize = ceil(testLightSize / 4) * 4  # align datasize and try again
                # testLightSize = (testLightSize + 3) & (MAX_U32 ^ 3)  # align datasize and try again ((test_lightsize + 3) & ~3)
                samples = (nextLightMapOffset - prevLightMapOffset) / testLightSize

            # assert samples in [ 1, 3 ], f'lighting invalid sample count: { samples }'

            if samples in [ 1, 3 ]:
                self.lightMapSamples = max(int(samples), 1)  # avoid division by zero

            # TODO: seems like error never triggers in Xash, but in HLC it triggers for BSP c1a3c
            #       wtf? May be rounding errors?
            else:
                assert self.lightMapSamples == 3, self.lightMapSamples
                printW(f'Invalid lighting sample count { samples }, defaulted to { self.lightMapSamples }')

        assert self.reader.tell() == (lump.offset + lump.size)

    # Mod_LoadLighting
    def readLighting (self):
        self.lightData = []

        lump = self.header.lumps[BSPLumpType.Lighting]

        if not lump.size:
            return

        assert self.lightMapSamples == 3

        self.loadModelFlags |= ModelFlags.ColoredLighting

        self.reader.seek(lump.offset)

        self.lightDataCount = count     = lump.count
        self.lightData      = lightData = [ RGB() for _ in range(count) ]

        for rgb in lightData:
            r, g, b = self.reader.u8(3)

            rgb.r = r
            rgb.g = g
            rgb.b = b

        for face in self.faces:
            lightMapOffset = face.lightMapOffset

            if lightMapOffset < 0:
                continue

            assert lightMapOffset % self.lightMapSamples == 0

            offset = lightMapOffset // self.lightMapSamples

            assert offset < self.lightDataCount

            # TODO: IS THIS IS SINGLE ELEMENT [offset] OR SLICE [offset:]???
            face.samples = [ self.lightData[offset] ]

        assert self.reader.tell() == (lump.offset + lump.size)

    # Mod_LoadMarkSurfaces
    def readMarkFaces (self):
        lump = self.header.lumps[BSPLumpType.MarkFaces]

        self.reader.seek(lump.offset)

        self.markFaceCount = count     = lump.count
        self.markFaces     = markFaces = []

        # read dmarkface_t == unsigned short
        markFaceIndices = self.reader.u16(lump.count)

        for i in range(count):
            markFaceIndex = markFaceIndices[i]

            assert 0 <= markFaceIndex < self.faceCount

            markFaces.append(self.faces[markFaceIndex])

        assert self.reader.tell() == (lump.offset + lump.size)

    # Mod_LoadLeafs
    def readLeaves (self):
        lump = self.header.lumps[BSPLumpType.Leaves]

        # if bmod->isworld:
        visClusters = self.subModels[0].visLeaves
        self.world.visBytes = (visClusters + 7) >> 3
        self.world.fatBytes = (visClusters + 31) >> 3

        self.reader.seek(lump.offset)

        self.leafCount = count  = lump.count
        self.leaves    = leaves = [ ModelLeaf() for _ in range(count) ]

        for i in range(count):
            # read dleaf_t
            contents           = self.reader.i32()   # int contents -- contents enumeration
            visOffset          = self.reader.i32()   # int visofs -- offset into the visibility lump, -1 = no visibility info
            mins               = self.reader.i16(3)  # short mins[3] -- b-box mins, for frustum culling
            maxs               = self.reader.i16(3)  # short maxs[3] -- b-box maxs
            firstMarkFaceIndex = self.reader.u16()   # word firstmarksurface -- index into self.markFaces array
            markFaceCount      = self.reader.u16()   # word nummarksurfaces
            ambSoundLevels     = self.reader.u8(ABM_SOUND_COUNT)  # byte ambient_level[NUM_AMBIENTS] -- ambient sound level (0-255)

            leaf = leaves[i]

            leaf.contents           = contents
            leaf.mins               = mins
            leaf.maxs               = maxs
            leaf.firstMarkFaceIndex = firstMarkFaceIndex  # self.markFaces[leaf.firstMarkFaceIndex]
            leaf.markFaceCount      = markFaceCount
            leaf.ambSoundLevels     = ambSoundLevels

            leaf.cluster = i - 1

            if leaf.cluster >= visClusters:
                leaf.cluster = -1

            if visOffset == -1:
                leaf.compVisOffset = -1
            else:
                assert visOffset < self.visDataSize
                # assert leaf.cluster >= 0  # TODO: wtf engine/common/mod_bmodel.c:2410-2421 (conflict of branches)

                leaf.compVisOffset = visOffset

            # gl underwater warp
            if leaf.contents != ContentsType.Empty:
                for j in range(leaf.markFaceCount):
                    # mark underwater surfaces
                    self.markFaces[leaf.firstMarkFaceIndex + j].flags |= BSPFaceFlags.Underwater

        assert self.leaves[0].contents == ContentsType.Solid, 'map has leaf 0 is not CONTENTS_SOLID'

        #  do some final things for world
        if self.checkWaterAlphaSupport():
            self.world.flags |= WorldFlags.WaterAlpha

        assert self.reader.tell() == (lump.offset + lump.size)

    # Mod_LoadNodes
    def readNodes (self):
        lump = self.header.lumps[BSPLumpType.Nodes]

        self.reader.seek(lump.offset)

        self.nodeCount = count = lump.count
        self.nodes     = nodes = [ ModelNode() for _ in range(count) ]

        for node in nodes:
            # read dnode_t
            planeIndex     = self.reader.u32()   # int planenum -- index into planes lump
            children       = self.reader.i16(2)  # short children[2] -- if > 0, then indices into Nodes, otherwise bitwise inverse (-(leafs + 1)) indices into Leafs
            mins           = self.reader.i16(3)  # short mins[3] -- b-box mins, for sphere culling
            maxs           = self.reader.i16(3)  # short maxs[3] -- b-box maxs
            firstFaceIndex = self.reader.u16()   # word firstface -- index into Faces
            faceCount      = self.reader.u16()   # word numfaces -- faces count (counting both sides)

            node.contents       = 0
            node.mins           = mins
            node.maxs           = maxs
            node.plane          = self.planes[planeIndex]
            node.firstFaceIndex = firstFaceIndex
            node.faceCount      = faceCount

            for j in range(2):
                index = children[j]

                if index >= 0:
                    node.children[j] = nodes[index]
                else:
                    node.children[j] = self.leaves[~index]  # ~index == -1 - index

        self.setNodeParent(nodes[0], None)

        assert self.reader.tell() == (lump.offset + lump.size)

    # Mod_LoadClipnodes
    def readClipNodes (self):
        lump = self.header.lumps[BSPLumpType.ClipNodes]

        self.reader.seek(lump.offset)

        self.clipNodeCount = count = lump.count
        self.clipNodes     = nodes = [ BSPClipNode() for _ in range(count) ]

        for node in nodes:
            # read dclipnode_t
            planeIndex = self.reader.i32()   # int planenum
            children   = self.reader.i16(2)  # short children[2] -- negative numbers are contents

            assert 0 <= planeIndex < self.planeCount
            assert children[0] >= ContentsType.Fog
            assert children[1] >= ContentsType.Fog

            node.planeIndex = planeIndex
            node.children   = children

        assert self.reader.tell() == (lump.offset + lump.size)

    def setNodeParent (self, node : ModelNode | ModelLeaf, parent : ModelNode | ModelLeaf | None):
        node.parent = parent

        # is it leaf?
        if node.contents < 0:
            return

        self.setNodeParent(node.children[0], node)
        self.setNodeParent(node.children[1], node)

    def calcFaceBounds (self, face : ModelFace | None):
        clearBounds(face.info.mins, face.info.maxs)

        for i in range(face.edgeCount):
            edge = self.faceEdges[face.firstEdgeIndex + i]

            assert -self.edgeCount < edge < self.edgeCount

            if edge >= 0:
                v = self.vertices[self.edges[edge].v[0]]
            else:
                v = self.vertices[self.edges[-edge].v[1]]

            addPointToBounds(v, face.info.mins, face.info.maxs)

        averageVec3(face.info.mins, face.info.maxs, face.info.origin)

    def calcFaceExtents (self, face : ModelFace | None):
        sampleSize = self.getSampleSizeForFace(face)
        texInfo    = face.textureInfo
        info       = face.info

        self.calcLightMatrixFromTexMatrix(texInfo, info.lightMapVecs)

        mins   = [  999999,  999999 ]
        maxs   = [ -999999, -999999 ]
        lmMins = [  999999,  999999 ]
        lmMaxs = [ -999999, -999999 ]

        for i in range(face.edgeCount):
            edge = self.faceEdges[face.firstEdgeIndex + i]

            assert -self.edgeCount < edge < self.edgeCount

            if edge >= 0:
                v = self.vertices[self.edges[edge].v[0]]
            else:
                v = self.vertices[self.edges[-edge].v[1]]

            for j in range(2):
                value = dotVec3(v, texInfo.vectors[j]) + texInfo.vectors[j][3]
                mins[j] = min(value, mins[j])
                maxs[j] = max(value, maxs[j])

            for j in range(2):
                value = dotVec3(v, info.lightMapVecs[j]) + info.lightMapVecs[j][3]
                lmMins[j] = min(value, lmMins[j])
                lmMaxs[j] = max(value, lmMaxs[j])

        bMins = [ 0, 0 ]
        bMaxs = [ 0, 0 ]

        for i in range(2):
            bMins[i] = floor(mins[i] / sampleSize)
            bMaxs[i] = ceil(maxs[i] / sampleSize)

            face.textureMins[i] = bMins[i] * sampleSize
            face.extents[i] = (bMaxs[i] - bMins[i]) * sampleSize

            # <UNREACHABLE>
            if isBitSet(texInfo.flags, BSPTextureFlags.WorldLuxels):
                lmMins[i] = floor(lmMins[i])
                lmMaxs[i] = ceil(lmMaxs[i])

                info.lightMapMins[i] = lmMins[i]
                info.lightMapExtents[i] = lmMaxs[i] - lmMins[i]
            # </UNREACHABLE>
            else:
                info.lightMapMins[i] = face.textureMins[i]
                info.lightMapExtents[i] = face.extents[i]

    def calcLightMatrixFromTexMatrix (self, texInfo : ModelTextureInfo, lightMapVecs : list[Vec4, Vec4]):
        lightMapScale = LM_SAMPLE_SIZE

        if isBitSet(texInfo.flags, BSPTextureFlags.ExtraLightMap):
            lightMapScale = LM_SAMPLE_EXTRA_SIZE

        if texInfo.faceInfo:
            lightMapScale = texInfo.faceInfo.textureStep

        for i in range(2):
            for j in range(4):
                lightMapVecs[i][j] = texInfo.vectors[i][j]

        if not isBitSet(texInfo.flags, BSPTextureFlags.WorldLuxels):
            return

        # <UNREACHABLE>
        # engine/common/mod_bmodel.c:945
        normVec3(lightMapVecs[0])
        normVec3(lightMapVecs[1])

        if isBitSet(texInfo.flags, BSPTextureFlags.AxialLuxels):
            self.makeNormalAxial(lightMapVecs[0])
            self.makeNormalAxial(lightMapVecs[1])

        scaleVec3(lightMapVecs[0], 1 / lightMapScale, lightMapVecs[0])
        scaleVec3(lightMapVecs[1], -1 / lightMapScale, lightMapVecs[1])

        lightMapVecs[0][3] = lightMapScale * 0.5
        lightMapVecs[1][3] = -lightMapScale * 0.5
        # </UNREACHABLE>

    def makeNormalAxial (self, normal : Vec3):
        axis = None

        for i in range(3):
            if abs(normal[i]) > 0.9999:
                axis = i
                break

        if axis is None:
            return

        for i in range(3):
            if i == axis:
                normal[i] = 1
            else:
                normal[i] = 0

    def getSampleSizeForFace (self, face : ModelFace | None):
        # <UNREACHABLE>
        if not face or not face.textureInfo:
            return LM_SAMPLE_SIZE

        # world luxels has more priority
        if isBitSet(face.textureInfo.flags, BSPTextureFlags.WorldLuxels):
            return 1

        if isBitSet(face.textureInfo.flags, BSPTextureFlags.ExtraLightMap):
            return LM_SAMPLE_EXTRA_SIZE

        if face.textureInfo.faceInfo:
            return face.textureInfo.faceInfo.textureStep
        # </UNREACHABLE>

        return LM_SAMPLE_SIZE

    def subdivideFaces (self, face : ModelFace):
        vertices : list[Vec3] = [ [ 0, 0, 0 ] for _ in range(SUBDIVIDE_SIZE) ]
        vertCount = 0

        for i in range(face.edgeCount):
            edge = self.faceEdges[face.firstEdgeIndex + i]

            assert -self.edgeCount < edge < self.edgeCount

            # TODO: is this is a mistake??? It must be edge >= 0!??
            if edge > 0:
                v = self.vertices[self.edges[edge].v[0]]
            else:
                v = self.vertices[self.edges[-edge].v[1]]

            copyVec3(v, vertices[vertCount])

            vertCount += 1

        face.flags |= BSPFaceFlags.DrawTurbQuads

        self.subdividePolygonR(face, vertCount, vertices)

    def subdividePolygonR (self, face : ModelFace, vertCount : int, vertices : list[Vec3]):
        front : list[Vec3] = [ [ 0, 0, 0 ] for _ in range(SUBDIVIDE_SIZE) ]
        back : list[Vec3]  = [ [ 0, 0, 0 ] for _ in range(SUBDIVIDE_SIZE) ]
        dist : list[float] = [ 0 ] * SUBDIVIDE_SIZE
        mins : Vec3 = [ 0, 0, 0 ]
        maxs : Vec3 = [ 0, 0, 0 ]
        info = face.info

        assert vertCount <= (SUBDIVIDE_SIZE + 4), 'too many vertexes on face'

        sampleSize : int = self.getSampleSizeForFace(face)

        BoundPoly(vertCount, vertices, mins, maxs)

        for i in range(3):
            m : float = (mins[i] + maxs[i]) * 0.5  # calc center point of b-box for current axis
            m = SUBDIVIDE_SIZE * floor((m / SUBDIVIDE_SIZE) + 0.5)  # round to nearest SUBDIVIDE_SIZE unit (0, 64, 128, ...)

            # skip if polygon is too small???
            if (maxs[i] - m) < 8 or (m - mins[i]) < 8:
                continue

            # calc dists of current vertex and the center of b-box for current axis (can be negative)
            for j in range(vertCount):
                dist[j] = vertices[j][i] - m

            assert len(vertices) > vertCount

            # copy first dist to (last + 1) dist
            dist[vertCount] = dist[0]

            # copy first vertex coord to (last + 1) vertex coord
            copyVec3(vertices[0], vertices[vertCount])

            f = b = 0

            for j in range(vertCount):
                if dist[j] >= 0:
                    copyVec3(vertices[j], front[f])
                    f += 1

                if dist[j] <= 0:
                    copyVec3(vertices[j], back[b])
                    b += 1

                if dist[j] == 0 or dist[j + 1] == 0:
                    continue

                if (dist[j] > 0) != (dist[j + 1] > 0):
                    # clip point
                    frac = dist[j] / (dist[j] - dist[j + 1])

                    for k in range(3):
                        front[f][k] = back[b][k] = vertices[j][k] + frac * (vertices[j + 1][k] - vertices[j][k])

                    f += 1
                    b += 1

            self.subdividePolygonR(face, f, front)
            self.subdividePolygonR(face, b, back)

            return

        if vertCount != 4:
            face.flags = clearBit(face.flags, BSPFaceFlags.DrawTurbQuads)

        poly = ModelPoly()

        poly.next      = face.polys
        poly.flags     = face.flags
        poly.vertCount = vertCount
        poly.vertices  = [  # float[vertCount][VERTEXSIZE]
            ([ 0 ] * VERTEX_SIZE) for _ in range(vertCount)
        ]

        face.polys = poly

        texInfo = face.textureInfo

        for i in range(vertCount):
            vertex = vertices[i]

            copyVec3(vertex, poly.vertices[i])

            if isBitSet(face.flags, BSPFaceFlags.DrawTurb):
                s = dotVec3(vertex, texInfo.vectors[0])
                t = dotVec3(vertex, texInfo.vectors[1])
            else:
                s = dotVec3(vertex, texInfo.vectors[0]) + texInfo.vectors[0][3]
                t = dotVec3(vertex, texInfo.vectors[1]) + texInfo.vectors[1][3]
                s /= texInfo.texture.width
                t /= texInfo.texture.height

            poly.vertices[i][3] = s
            poly.vertices[i][4] = t

            # for speed reasons
            if not isBitSet(face.flags, BSPFaceFlags.DrawTurb):
                # light map texture coordinates
                s = dotVec3(vertex, info.lightMapVecs[0]) + info.lightMapVecs[0][3]
                s -= info.lightMapMins[0]
                s += face.lightS * sampleSize
                s += sampleSize * 0.5
                s /= BLOCK_SIZE * sampleSize  # fa->texinfo->texture->width;

                t = dotVec3(vertex, info.lightMapVecs[1]) + info.lightMapVecs[1][3]
                t -= info.lightMapMins[1]
                t += face.lightT * sampleSize
                t += sampleSize * 0.5
                t /= BLOCK_SIZE * sampleSize    # fa->texinfo->texture->width;

                poly.vertices[i][5] = s
                poly.vertices[i][6] = t

    def checkWaterAlphaSupport (self) -> bool:
        # False for all maps
        return False

    def loadEntities (self):
        for entityInfo in self.entityList:
            # Entity got by classname in function DispatchKeyValue
            # Also, in this fn some values set to entityInfo's values
            className = entityInfo.get('classname')

            assert className

            entityClassInfo = BSP_ENTITY_TYPES.get(className)

            if not entityClassInfo:
                printE(f'Spawn function for entity class name "{ className }" is not found')
                continue
                # print()

            yawAngle = entityInfo.get('angle')

            if yawAngle is not None:
                yawAngle = float(yawAngle)

                if yawAngle >= 0:
                    angles = f'0 { yawAngle } 0'
                elif yawAngle == -1:
                    angles = '-90 0 0'
                elif yawAngle == -2:
                    angles = '90 0 0'
                else:
                    angles = '0 0 0'

                del entityInfo['angle']

                entityInfo['angles'] = angles

            light = entityInfo.get('light')

            if light is not None:
                del entityInfo['light']

                entityInfo['light_level'] = light

            for key, value in entityInfo.items():
                match BSP_ENTITY_FIELDS.get(key, {}).get('type'):
                    case BSPEntityFieldType.ModelName | BSPEntityFieldType.SoundName | BSPEntityFieldType.String:
                        entityInfo[key] = str(value)

                    case BSPEntityFieldType.Time | BSPEntityFieldType.Float:
                        entityInfo[key] = float(value)

                    case BSPEntityFieldType.Integer:
                        entityInfo[key] = int(value)

                    case BSPEntityFieldType.PosVec | BSPEntityFieldType.Vec:
                        entityInfo[key] = parseVec3(value)

                        assert len(entityInfo[key]) == 3

        # CWorld->Precache():
        # - SENTENCEG_Init()           // load sound/sentences.txt
        # - TEXTURETYPE_Init()         // load sound/materials.txt
        # - W_Precache()               // a lot of items, weapons & sprites preloads
        # - ClientPrecache()           // a lot of sounds & models preloads
        # - load some sounds & models
        # - WorldGraph.FLoadGraph()    // load *.nod

    def loadNodeGraph (self):
        mapsDir = getDirPath(self.filePath)
        nodName = getFileName(self.filePath) + '.nod'
        nodPath = joinPath(mapsDir, 'graphs', nodName)

        if not isFile(nodPath):
            # TODO: replace with exception
            self.nodeGraph = None
            printW('Graph node file does not exist:', nodPath)
            return

        self.nodeGraph = Graph.fromFile(nodPath)


def parseVec3 (value : str) -> Vec3:
    vec  = [ 0, 0, 0 ]
    nums = split(r'[\s,]+', value.strip())

    for i, num in enumerate(nums):
        vec[i] = float(num)

    return vec


def BoundPoly (vertCount : int, vertices : list[Vec3], mins : Vec3, maxs : Vec3):
    clearBounds(mins, maxs)

    for i in range(vertCount):
        v = vertices[i]

        for j in range(3):
            if v[j] < mins[j]:
                mins[j] = v[j]

            if v[j] > maxs[j]:
                maxs[j] = v[j]



# noinspection PyUnreachableCode
def _test_ ():
    if 1:
        mapsDir = joinPath(GAME_DIR, 'maps')

        for bspPath in iterFiles(mapsDir, False, includeExts=[ '.bsp' ]):
            print(bspPath)
            bsp = BSP.fromFile(bspPath)
            print(' ')
            # break
    else:
        # bsp = BSP.fromFile(joinPath(GAME_DIR, 'maps', 'c0a0.bsp'))
        # bsp = BSP.fromFile(joinPath(GAME_DIR, 'maps', 'c0a0d.bsp'))  # has surfaces to subdivide
        # bsp = BSP.fromFile(joinPath(GAME_DIR, 'maps', 'c1a0e.bsp'))
        # bsp = BSP.fromFile(joinPath(GAME_DIR, 'maps', 'c0a0b.bsp'))
        # bsp = BSP.fromFile(joinPath(GAME_DIR, 'maps', 'c2a4f.bsp'))
        bsp = BSP.fromFile(joinPath(GAME_DIR, 'maps', 'c1a3c.bsp'))



__all__ = [
    'BSP',

    '_test_',
]



if __name__ == '__main__':
    _test_()
