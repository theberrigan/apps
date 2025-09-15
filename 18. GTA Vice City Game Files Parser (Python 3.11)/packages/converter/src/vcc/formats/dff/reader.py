import re

from ...common import bfw
from ...common.types import *
from ...common.consts import *

from ..rw import RWStream, PluginId, RWMatrix
from ..txd import TextureFilterType, Texture

from .consts import *
from .types import *

from bfw.utils import *
from bfw.types.enums import Enum
from bfw.reader import *



# FRAMES
# ----------------------------------------------------------------------------------------------------------------------

class RWFrame:
    def __init__ (self):
        self.matrix      : RWMatrix      = RWMatrix()
        self.parentIndex : TInt          = None
        self.children    : List[RWFrame] = []

        # by FrameNodeNamePlugin
        self._fullName : TStr = None
        self._baseName : TStr = None
        self._lodIndex : TInt = None

        # by FrameHAnimPlugin
        self.anim : Opt['HAnimData'] = None

    def addChild (self, child : 'RWFrame'):
        self.children.insert(0, child)

    # GetAnimHierarchyFromClumpCB
    # HAnimData::get(RwFrame)->hierarchy
    def getAnimHierarchy (self) -> Opt['HAnimHierarchy']:
        if self.anim and self.anim.hierarchy:
            return self.anim.hierarchy

        return None

    def getFullName (self) -> TStr:
        return self._fullName

    def setName (self, name : str):
        name = (name or '').strip().lower()

        self._fullName = name
        self._baseName, \
        self._lodIndex = self.parseName(name)

    def getBaseName (self) -> TStr:
        return self._baseName

    def getLODIndex (self) -> TInt:
        return self._lodIndex

    def parseName (self, name : str) -> Tuple[TStr, TInt]:
        lodIndex = None
        baseName = None

        if name:
            # wheel_alloy_l0
            match = re.search(r'_l(\d)', name, flags=re.I)

            if match:
                lodIndex = int(match.group(1))
                baseName = name[:match.start()]
            else:
                lodIndex = 0
                baseName = name

        return baseName, lodIndex

        # TODO: some names have strange format
        # stonebench1_l0- colmesh
        # vendmach_l0
        # washer_l0
        # washer_l0- colsph02
        # washer_l0- colsph03
        # washer_l01- colsph05
        # washer_l01- colsph06
        # wastebin_l0
        # wheel_alloy_l0
        # wheel_alloy_l1


TFrameList = List[RWFrame]


# HIERARCHY ANIMATION
# ----------------------------------------------------------------------------------------------------------------------

# RpHAnimHierarchyFlag
class HAnimFlag (Enum):
    HANIMHIERARCHYSUBHIERARCHY            = 1       # rpHANIMHIERARCHYSUBHIERARCHY            = HAnimHierarchy::Flags::SUBHIERARCHY
    HANIMHIERARCHYNOMATRICES              = 2       # rpHANIMHIERARCHYNOMATRICES              = HAnimHierarchy::Flags::NOMATRICES
    HANIMHIERARCHYUPDATEMODELLINGMATRICES = 0x1000  # rpHANIMHIERARCHYUPDATEMODELLINGMATRICES = HAnimHierarchy::Flags::UPDATEMODELLINGMATRICES
    HANIMHIERARCHYUPDATELTMS              = 0x2000  # rpHANIMHIERARCHYUPDATELTMS              = HAnimHierarchy::Flags::UPDATELTMS
    HANIMHIERARCHYLOCALSPACEMATRICES      = 0x4000  # rpHANIMHIERARCHYLOCALSPACEMATRICES      = HAnimHierarchy::Flags::LOCALSPACEMATRICES


# HAnimNodeInfo
class HAnimNode:
    def __init__ (self):
        self.id    : TInt = None  # int32 id
        self.index : TInt = None  # int32 index
        self.flags : TInt = None  # int32 flags
        # self.frame : Opt[RWFrame] = None  # Frame *frame


class HAnimHierarchy:
    def __init__ (self, nodeCount : int, nodeFlags : List[int], nodeIds : List[int], flags : int, maxKeySize : int):
        # NOTE: self.interpolator = AnimInterpolator::create(numNodes, maxKeySize);
        self.maxKeySize : TInt            = maxKeySize  # used to create interpolator
        self.flags      : TInt            = flags       # int32 flags
        self.nodeCount  : TInt            = nodeCount   # int32 numNodes
        self.nodeInfo   : List[HAnimNode] = [ HAnimNode() for _ in range(nodeCount) ]

        for i in range(self.nodeCount):
            info = self.nodeInfo[i]

            info.id    = nodeIds[i]
            info.index = i
            info.flags = nodeFlags[i]


class HAnimData:
    def __init__ (self):
        self.id        : TInt                = None
        self.hierarchy : Opt[HAnimHierarchy] = None


# GEOMETRY
# ----------------------------------------------------------------------------------------------------------------------

class RWGeometryFlag (Enum):
    TRISTRIP  = 0x01
    POSITIONS = 0x02
    TEXTURED  = 0x04
    PRELIT    = 0x08
    NORMALS   = 0x10
    LIGHT     = 0x20
    MODULATE  = 0x40
    TEXTURED2 = 0x80
    # When this flag is set the geometry has
    # native geometry. When streamed out this geometry
    # is written out instead of the platform independent data.
    # When streamed in with this flag, the geometry is mostly empty.
    NATIVE = 0x01000000
    # Just for documentation: RW sets this flag
    # to prevent rendering when executing a pipeline,
    # so only instancing will occur.
    # librw's pipelines are different, so it's unused here.
    NATIVEINSTANCE = 0x02000000


class RWGeometry:
    @classmethod
    def create (cls, vertexCount : int, triangleCount : int, flags : int) -> Self:
        geo = cls()

        geo.flags = flags & 0xFF00FFFF  # RWGeometryFlag (Geometry::Flags)

        hasNativeData = bool(geo.flags & RWGeometryFlag.NATIVE)
        _hasNormals   = bool(geo.flags & RWGeometryFlag.NORMALS)
        has1stTexture = bool(geo.flags & RWGeometryFlag.TEXTURED)
        has2ndTexture = bool(geo.flags & RWGeometryFlag.TEXTURED2)

        texCoordSetCount = (flags & 0xFF0000) >> 16

        assert texCoordSetCount in [ 0, 1 ], texCoordSetCount
        assert not hasNativeData
        assert not has2ndTexture
        assert vertexCount > 0

        geo.hasTextures   = bool(texCoordSetCount or has1stTexture)
        geo.vertexCount   = vertexCount
        geo.triangleCount = triangleCount
        geo.triangles     = [ Triangle() for _ in range(geo.triangleCount) ]

        for triangle in geo.triangles:
            triangle.matId = 0xFFFF  # set U16_MAX

        geo.morphTarget = MorphTarget()
        geo.materials   = None

        return geo

    # no native data
    # 0 or 1 tex coord sets
    # no second texture
    def __init__ (self):
        self.flags         : TInt                = None  # RWGeometryFlag (Geometry::Flags)
        self.hasTextures   : TBool               = None
        self.vertexCount   : TInt                = None
        self.triangleCount : TInt                = None
        self.colors        : Opt[List[TRGBA]]    = None  # RGBA[vertexCount]
        self.triangles     : Opt[List[Triangle]] = None
        self.texCoords     : Opt[List[TUV]]      = None  # UV[vertexCount] (def. 8)
        self.morphTarget   : Opt[MorphTarget]    = None
        self.materials     : Opt[TMaterialList]  = None

        # by GeometryMeshPlugin
        self.meshData : Opt[MeshData] = None

        # by GeometrySkinPlugin
        self.skin : Opt[Skin] = None

    def getSkin (self) -> Opt['Skin']:
        return self.skin


class MorphTarget:
    def __init__ (self):
        self.boundingSphere : Opt[Sphere]            = None  # Sphere boundingSphere
        self.vertices       : Opt[List[List[float]]] = None  # V3d *vertices
        self.normals        : Opt[List[List[float]]] = None  # V3d *normals


class Triangle:
    def __init__ (self):
        self.v     : Opt[List[int]] = None
        self.matId : TInt           = None


class Mesh:
    def __init__ (self):
        self.materialIndex : Opt[int]       = None  # index to geometry.materials
        self.material      : Opt[Material]  = None  # Material *material (from geometry.materials)
        self.indexCount    : Opt[int]       = None  # uint32 numIndices
        self.indices       : Opt[List[int]] = None  # uint16 *indices


class MeshData:
    def __init__ (self):
        self.flags           : TInt            = None  # uint32 flags
        self.meshCount       : TInt            = None  # uint16 meshCount
        self.totalIndexCount : TInt            = None  # uint32 totalIndices
        self.meshes          : Opt[List[Mesh]] = None


# GEOMETRY: SKINNING
# ----------------------------------------------------------------------------------------------------------------------

class RLECount:
    def __init__ (self):
        self.start : TInt = None  # uint8 start
        self.size  : TInt = None  # uint8 size


class RLE:
    def __init__ (self):
        self.startBone : TInt = None  # uint8 rleStartBone -- into remapIndices
        self.n         : TInt = None  # uint8 rleN


class Skin:
    @classmethod
    def create (cls, boneCount : int, usedBoneCount : int, weightCount : int) -> Self:
        skin = cls()

        skin.boneCount     = boneCount
        skin.usedBoneCount = usedBoneCount
        skin.weightCount   = weightCount
        skin.usedBones     = None
        skin.invMatrices   = []
        skin.indices       = None
        skin.weights       = None

        skin.boneLimit    = 0
        skin.meshCount    = 0
        skin.rleSize      = 0
        skin.remapIndices = None
        skin.rleCount     = None
        skin.rle          = None
        # skin.platformData = None
        # skin.legacyType   = 0

        return skin

    def __init__ (self):
        self.boneCount     : TInt             = None  # int32 numBones
        self.usedBoneCount : TInt             = None  # int32 numUsedBones
        self.weightCount   : TInt             = None  # int32 numWeights
        self.usedBones     : Opt[List[int]]   = None  # uint8 *usedBones
        self.invMatrices   : Opt[List[float]] = None  # float *inverseMatrices
        self.indices       : Opt[List[int]]   = None  # uint8 *indices
        self.weights       : Opt[List[float]] = None  # float *weights

        # skin split data related stuff
        self.boneLimit    : TInt                = None  # int32 boneLimit
        self.meshCount    : TInt                = None  # int32 numMeshes
        self.rleSize      : TInt                = None  # int32 rleSize
        self.remapIndices : Opt[List[int]]      = None  # int8 *remapIndices
        self.rleCount     : Opt[List[RLECount]] = None  # RLEcount *rleCount -- points into rle for each mesh
        self.rle          : Opt[List[RLE]]      = None  # RLE *rle -- run length encoded used bones

    def findNumWeights (self, vertexCount : int):
        self.weightCount = 1
        w = 0

        while vertexCount:
            vertexCount -= 1

            while self.weights[self.weightCount + w] != 0.0:
                self.weightCount += 1

                if self.weightCount == 4:
                    return

            w += 4

    # p.345 Bone Vertex Indices
    def findUsedBones (self, vertexCount : int):
        usedTab = [ 0 ] * 256  # 256 - max bones in skeleton
        indices = 0
        weights = 0

        while vertexCount:
            vertexCount -= 1

            for i in range(self.weightCount):
                if self.weights[weights + i] == 0.0:
                    continue

                if usedTab[self.indices[indices + i]] == 0:
                    usedTab[self.indices[indices + i]] += 1

            indices += 4
            weights += 4

        self.usedBones = []

        for i in range(256):
            if usedTab[i]:
                self.usedBones.append(i)

        self.usedBoneCount = len(self.usedBones)


# MATERIALS AND TEXTURES
# ----------------------------------------------------------------------------------------------------------------------

class MaterialTexture:
    def __init__ (self):
        self.name       : TStr         = None
        self.maskName   : TStr         = None
        self.filterType : TInt         = None  # info1 & 0xFF  # see TextureFilterType
        self.addrU      : TInt         = None  # (info1 >> 8) & 0xF  # see TextureAddressingType
        self.addrV      : TInt         = None  # (info1 >> 12) & 0xF  # see TextureAddressingType
        self.useMipMaps : TBool        = None
        self.texture    : Opt[Texture] = None  # TODO <LINK>: link real texture with this prop in main loader


class Material:
    def __init__ (self):
        self.color        : TRGBA                = None
        self.surfaceProps : Opt[SurfaceProps]    = None
        self.texture      : Opt[MaterialTexture] = None

        # by MaterialMatFXPlugin plugin
        self.matFX        : Opt[MatFX] = None


TMaterialList = List[Material]


class SurfaceProps:
    @classmethod
    def getDefault (cls):
        return cls(1, 1, 1)

    def __init__(self, ambient : float = 1, specular : float = 1, diffuse : float = 1):
        self.ambient  = ambient
        self.specular = specular
        self.diffuse  = diffuse

    def clone (self):
        sp = SurfaceProps()

        sp.ambient  = self.ambient
        sp.specular = self.specular
        sp.diffuse  = self.diffuse

        return sp


# MATERIALS AND TEXTURES: MATFX
# ----------------------------------------------------------------------------------------------------------------------

class MatFXType (Enum):
    NOTHING         = 0
    BUMPMAP         = 1  # unused
    ENVMAP          = 2
    BUMPENVMAP      = 3  # unused
    DUAL            = 4  # unused
    UVTRANSFORM     = 5  # unused
    DUALUVTRANSFORM = 6  # unused


class MatFXEffect:
    def __init__(self):
        self.type : Opt[TInt]     = None  # see MatFXType
        self.env  : Opt[MatFXEnv] = None


class MatFXEnv:
    def __init__ (self):
        self.frame       : Opt[RWFrame]         = None  # Frame   *frame
        self.texture     : Opt[MaterialTexture] = None  # Texture *tex  TODO <LINK>: link real texture with this prop in main loader
        self.coefficient : TFloat               = None  # float    coefficient
        self.alpha       : TInt                 = None  # int32    fbAlpha (int32 bool)


class MatFX:
    def __init__ (self):
        self.type : TInt              = MatFXType.NOTHING  # see MatFXType
        self.fx   : List[MatFXEffect] = [ MatFXEffect() for _ in range(2) ]


# ATOMICS
# ----------------------------------------------------------------------------------------------------------------------

class RWAtomic:
    Rights = [
        0,  # atomic->pipeline->pluginID;
        0   # atomic->pipeline->pluginData;
    ]

    def __init__ (self):
        self.frameIndex     : TInt            = None  # index to frames
        self.frame          : Opt[RWFrame]    = None
        self.geometryIndex  : TInt            = None  # index to geometries
        self.geometry       : Opt[RWGeometry] = None
        self.flags          : TInt            = None  # atomic->object.object.flags (atomic.ObjectWithFrame.RWObject)
        self.boundingSphere : Opt[Sphere]     = None  # ref to self.geometry.morphTarget.boundingSphere

        self.hierarchy : Opt[HAnimHierarchy] = None

        # by AtomicMatFXPlugin
        # TODO: is enabled by default?
        self.areEffectsEnabled : bool = False

        # by AtomicMatFXPlugin
        # by AtomicRightsPlugin
        self._pipeline : Any = ''  # matfx pipeline

    def getSkin (self) -> Opt[Skin]:
        if not self.geometry:
            return None

        return self.geometry.skin

    def setFrame (self, frameIndex : int, frame : RWFrame):
        self.frameIndex = frameIndex
        self.frame      = frame
        # NOTE: self.obj.object.privateFlags |= WORLDBOUNDDIRTY;

    def getFrame (self) -> Opt[RWFrame]:
        return self.frame

    def setGeometry (self, geometryIndex : int, geometry : 'RWGeometry'):
        if geometry:
            self.geometryIndex  = geometryIndex
            self.geometry       = geometry
            self.boundingSphere = geometry.morphTarget.boundingSphere
            # NOTE: if(this->getFrame()) this->getFrame()->updateObjects();

    def getGeometry (self) -> Opt['RWGeometry']:
        return self.geometry

    def enableEffects (self):
        self.areEffectsEnabled = True
        self._pipeline = 'matFXGlobals.pipelines[PLATFORM_GL3] from librw/src/gl/gl3matfx.cpp:199'  # TODO


# LIGHTS
# ----------------------------------------------------------------------------------------------------------------------

class RWLightFlag (Enum):
    LIGHTATOMICS = 1
    LIGHTWORLD   = 2


class RWLight:
    @classmethod
    def create (cls) -> Self:
        light = cls()

        light.radius        = 0
        light.minusCosAngle = 1
        light.color         = [ 1, 1, 1, 1 ]
        light.typeFlags     = RWLightFlag.LIGHTATOMICS | RWLightFlag.LIGHTWORLD
        light.privateFlags  = 1
        light.frameIndex    = None
        light.frame         = None

        return light

    def __init__ (self):
        self.radius        : TFloat           = None
        self.minusCosAngle : TFloat           = None
        self.color         : Opt[List[float]] = None  # Vec4
        self.typeFlags     : TInt             = None  # self.ObjectWithFrame_Object_flags | light->object.object.init(typeFlags >> 16)  # type
        self.privateFlags  : TInt             = None  # self.ObjectWithFrame_Object_privateFlags | x & 1 == isGrayScale?
        self.frameIndex    : TInt             = None  # index to clump.frames
        self.frame         : Opt[RWFrame]     = None

    def setColor (self, color : TVec3):
        self.color[0] = color[0]
        self.color[1] = color[1]
        self.color[2] = color[2]
        self.privateFlags = int(color[0] == color[1] == color[2])

    def setFrame (self, frameIndex : int, frame : RWFrame):
        # NOTE: self.object.setFrame(f)
        self.frameIndex = frameIndex
        self.frame      = frame


# CLUMP
# ----------------------------------------------------------------------------------------------------------------------

class RWClump:
    def __init__ (self):
        self.frame      : Opt[RWFrame]          = None  # self.frame (== self.frames[0]) is RwFrame.object.parent -- root frame
        self.frames     : Opt[List[RWFrame]]    = None
        self.geometries : Opt[List[RWGeometry]] = None
        self.atomics    : Opt[List[RWAtomic]]   = None
        self.lights     : Opt[List[RWLight]]    = None

    def getFirstAtomic (self) -> Opt[RWAtomic]:
        if self.atomics:
            # TODO: is this correct?
            return self.atomics[0]

        return None

    def isSkinned (self) -> bool:
        atomic = self.getFirstAtomic()

        if atomic:
            return bool(atomic.getGeometry().getSkin())

        return False

    def getFrame (self) -> Opt[RWFrame]:
        return self.frame

    def getAnimHierarchy (self) -> Opt[HAnimHierarchy]:
        if self.frames:
            for frame in self.frames:
                hierarchy = frame.getAnimHierarchy()

                if hierarchy:
                    return hierarchy

        return None



# STREAM PLUGINS
# ----------------------------------------------------------------------------------------------------------------------

class FrameNodeNamePlugin:
    Id = PluginId.NodeName

    @classmethod
    def read (cls, f : RWStream, size : int, frame : RWFrame) -> bool:
        assert isinstance(frame, RWFrame), frame

        frame.setName(f.string(size))

        return True


class FrameHAnimPlugin:
    Id = PluginId.HAnim

    @classmethod
    def read (cls, f : RWStream, _size : int, frame : RWFrame) -> bool:
        assert isinstance(frame, RWFrame), frame

        anim = frame.anim = HAnimData()

        version = f.i32()

        assert version == 0x100, version

        anim.id   = f.i32()
        nodeCount = f.i32()

        if nodeCount != 0:
            flags      = f.i32()
            maxKeySize = f.i32()

            nodeIds   = [ 0 ] * nodeCount
            nodeFlags = [ 0 ] * nodeCount

            for i in range(nodeCount):
                nodeIds[i]   = f.i32()
                _index       = f.i32()  # unused
                nodeFlags[i] = f.i32()

            anim.hierarchy = HAnimHierarchy(nodeCount, nodeFlags, nodeIds, flags, maxKeySize)

        return True


class GeometryMeshPlugin:
    Id = PluginId.Mesh

    @classmethod
    def read (cls, f : RWStream, _size : int, geometry : 'RWGeometry') -> bool:
        assert isinstance(geometry, RWGeometry), geometry

        assert not (geometry.flags & RWGeometryFlag.NATIVE)
        assert not geometry.meshData

        meshData = geometry.meshData = MeshData()

        meshData.flags           = f.u32()  # uint32 flags
        meshData.meshCount       = f.u32()  # uint32 numMeshes
        meshData.totalIndexCount = f.u32()  # uint32 totalIndices
        meshData.meshes          = [ Mesh for _ in range(meshData.meshCount) ]

        for mesh in meshData.meshes:
            mesh.indexCount    = f.u32()  # uint32 numIndices
            mesh.materialIndex = f.i32()  # int32 matIndex
            mesh.material      = geometry.materials[mesh.materialIndex]
            mesh.indices       = f.i32(mesh.indexCount, asArray=True)

        return True


# TODO: decompress RLE
class GeometrySkinPlugin:
    Id = PluginId.Skin

    @classmethod
    def read (cls, f : RWStream, _size : int, geometry : 'RWGeometry') -> bool:
        assert isinstance(geometry, RWGeometry), geometry
        assert geometry.vertexCount

        boneCount     = f.u8()
        usedBoneCount = f.u8()
        weightCount   = f.u8()
        _unused       = f.u8()

        # numUsedBones and numWeights appear in/after 34003
        # but not in/before 33002 (probably rw::version >= 0x34000)
        # Use numBones for numUsedBones to allocate data,
        # find out the correct value later
        isOldFormat = usedBoneCount == 0

        if isOldFormat:
            usedBoneCount = boneCount

        skin = geometry.skin = Skin.create(boneCount, usedBoneCount, weightCount)

        if not isOldFormat:
            skin.usedBones = f.u8(skin.usedBoneCount, asArray=True)

        skin.indices = f.u8(geometry.vertexCount * 4, asArray=True)
        skin.weights = f.f32(geometry.vertexCount * 4, asArray=True)

        for i in range(skin.boneCount):
            if isOldFormat:
                _unused = f.u32()
                assert _unused == 0xDEADDEAD, hex(_unused)

            skin.invMatrices.append(f.f32(16))

        if isOldFormat:
            skin.findNumWeights(geometry.vertexCount)
            skin.findUsedBones(geometry.vertexCount)
        else:
            cls.readSkinSplitData(f, skin)

        return True

    @classmethod
    def readSkinSplitData (cls, f : RWStream, skin : 'Skin'):
        skin.boneLimit = f.i32()
        skin.meshCount = f.i32()
        skin.rleSize   = f.i32()

        if skin.meshCount:
            skin.remapIndices = f.u8(skin.boneCount, asArray=True)
            skin.rleCount     = []

            for i in range(skin.meshCount):
                rleCount = RLECount()

                rleCount.start = f.u8()
                rleCount.size  = f.u8()

                skin.rleCount.append(rleCount)

            skin.rle = []

            for i in range(skin.rleSize):
                rle = RLE()

                rle.startBone = f.u8()
                rle.n         = f.u8()

                skin.rle.append(rle)


# Not used in VC, this is the stub
class GeometryMorphPlugin:
    Id = PluginId.Morph

    @classmethod
    def read (cls, f : RWStream, size : int, geometry : 'RWGeometry') -> bool:
        assert isinstance(geometry, RWGeometry), geometry
        assert size == 4, size

        _unk = f.u32()

        assert _unk == 0, _unk

        return True


class MaterialMatFXPlugin:
    Id = PluginId.MatFX

    # only ENVMAP effect supported
    @classmethod
    def read (cls, f : RWStream, _size : int, material : 'Material') -> bool:
        assert isinstance(material, Material), material

        fxType = f.u32()

        assert fxType == MatFXType.ENVMAP

        matFX = material.matFX

        if not matFX or matFX.type not in [ MatFXType.NOTHING, fxType ]:
            matFX = material.matFX = MatFX()

        matFX.type       = MatFXType.ENVMAP
        matFX.fx[0].type = MatFXType.ENVMAP
        matFX.fx[1].type = MatFXType.NOTHING

        # 1ND EFFECT

        fxType = f.u32()

        assert matFX.fx[0].type == fxType == MatFXType.ENVMAP

        env = matFX.fx[0].env = MatFXEnv()

        env.coefficient = f.f32()
        env.alpha       = f.i32()
        env.texture     = None

        hasTexture = bool(f.i32())

        if hasTexture:
            if not f.findChunk(PluginId.Texture):
                raise Exception('MatFX texture is not found')

            env.texture = f.consumer.readTexture(f)

        # 2ND EFFECT

        fxType = f.u32()

        assert matFX.fx[1].type == fxType == MatFXType.NOTHING

        return True


class TextureSkyMipMapPlugin:
    Id = PluginId.SkyMipMap

    @classmethod
    def read (cls, f : RWStream, size : int, texture : 'MaterialTexture') -> bool:
        assert isinstance(texture, MaterialTexture), texture
        assert size == 4, size

        # some param for PS2 raster (Ps2Raster::kl)
        _kl = f.i32()

        return True


class AtomicParticlesPlugin:
    Id = PluginId.Particles

    @classmethod
    def read (cls, f : RWStream, size : int, atomic : 'RWAtomic') -> bool:
        assert isinstance(atomic, RWAtomic), atomic
        assert size == 4, size

        _unk = f.u32()

        assert _unk == 0, _unk

        return True


class AtomicMatFXPlugin:
    Id = PluginId.MatFX

    @classmethod
    def read (cls, f : RWStream, size : int, atomic : 'RWAtomic') -> bool:
        assert isinstance(atomic, RWAtomic), atomic
        assert size == 4, size

        areEffectsEnabled = bool(f.i32())

        if areEffectsEnabled:
            atomic.enableEffects()

        return True


class AtomicRightsPlugin:
    Id = PluginId.RightToRender

    @classmethod
    def read (cls, f : RWStream, size : int, atomic : 'RWAtomic') -> bool:
        assert isinstance(atomic, RWAtomic), atomic
        assert size == 8, size

        RWAtomic.Rights = f.u32(2)

        return True

    @classmethod
    def alwaysCallback (cls, _f : RWStream, atomic : 'RWAtomic') -> bool:
        if atomic.getSkin():
            atomic._pipeline = 'skinGlobals.pipelines[PLATFORM_GL3] from librw/src/gl/gl3skin.cpp:297'  # TODO

        return True


# READER
# ----------------------------------------------------------------------------------------------------------------------

class DFF:
    def __init__ (self):
        self.filePath : TStr         = None
        self.clump    : Opt[RWClump] = None


class DFFReader:
    Plugins = [
        (RWFrame,         FrameNodeNamePlugin),
        (RWFrame,         FrameHAnimPlugin),
        (RWGeometry,      GeometryMeshPlugin),
        (RWGeometry,      GeometrySkinPlugin),
        (RWGeometry,      GeometryMorphPlugin),
        (Material,        MaterialMatFXPlugin),
        (MaterialTexture, TextureSkyMipMapPlugin),
        (RWAtomic,        AtomicParticlesPlugin),
        (RWAtomic,        AtomicMatFXPlugin),
        (RWAtomic,        AtomicRightsPlugin),
    ]

    @classmethod
    def fromFile (cls, filePath : str, ctx : Opt[Any] = None) -> DFF:
        if not isFile(filePath):
            raise OSError(f'File does not exist: { filePath }')

        rawData   = readBin(filePath)
        reader    = MemReader(rawData, filePath)
        dffReader = cls(ctx)
        stream    = RWStream(reader, dffReader, cls.Plugins)

        return dffReader.read(stream, filePath)

    def __init__ (self, ctx : Opt[Any] = None):
        self.ctx : Opt[Any] = ctx

    # CFileLoader::LoadModelFile
    def read (self, f : RWStream, filePath : str) -> DFF:
        header = f.findChunk(PluginId.Clump)

        assert header

        dff = DFF()

        dff.filePath = filePath
        dff.clump    = self.readClump(f)

        return dff

    # RpClumpStreamRead
    def readClump (self, f : RWStream) -> RWClump:
        clump = RWClump()

        header = f.findChunk(PluginId.Struct)

        if not header:
            raise Exception('Clump struct is not found')

        atomicCount = f.i32()
        lightCount  = 0
        cameraCount = 0

        if header.version > 0x33000:
            lightCount  = f.i32()
            cameraCount = f.i32()

        assert cameraCount == 0

        if not f.findChunk(PluginId.FrameList):
            raise Exception('Frame list is not found')

        frames = clump.frames = self.readFrames(f)

        # set first frame as a parent of the clump
        clump.frame = frames[0]

        geometries = clump.geometries = []

        assert header.version >= 0x30400, hex(header.version)

        if not f.findChunk(PluginId.GeometryList):
            raise Exception('Geometry list is not found')

        if not f.findChunk(PluginId.Struct):
            raise Exception('Geometry list struct is not found')

        geometryCount = f.i32()

        for i in range(geometryCount):
            if not f.findChunk(PluginId.Geometry):
                raise Exception('Geometry is not found')

            geometry = self.readGeometry(f)

            if not geometry:
                raise Exception('Failed to read geometry')

            geometries.append(geometry)

        atomics = clump.atomics = []

        for i in range(atomicCount):
            if not f.findChunk(PluginId.Atomic):
                raise Exception('Atomic is not found')

            atomic = self.readAtomic(f, frames, geometries)

            if not atomic:
                raise Exception('Atomic is not found')

            atomics.append(atomic)

        lights = clump.lights = []

        for i in range(lightCount):
            if not f.findChunk(PluginId.Struct):
                raise Exception('Struct is not found')

            frameIndex = f.i32()

            if not f.findChunk(PluginId.Light):
                raise Exception('Light is not found')

            light = self.readLight(f)

            if not light:
                raise Exception('Failed to read light')

            light.setFrame(frameIndex, frames[frameIndex])

            lights.append(light)

        assert cameraCount == 0, 'Need to read cameras'

        # NO EXTENSIONS
        if not f.readExtension(clump):
            raise Exception('Failed to read clump extension')

        '''
        clump
            frameList
                frame1
                ...
                frameN
            geometryList
                geometry1
                ...
                geometryN
                    materialList
                        material1
                        ...
                        materialN
                            texture?
            atomic1
            ...
            atomicN
        '''

        return clump

    # FrameList_::streamRead
    def readFrames (self, f : RWStream) -> TFrameList:
        if not f.findChunk(PluginId.Struct):
            raise Exception('Frame list struct is not found')

        frameCount = f.i32()

        frames : TFrameList = [ RWFrame() for _ in range(frameCount) ]

        for frame in frames:
            # FrameStreamData
            frame.matrix.right = f.vec3()  # V3d right
            frame.matrix.up    = f.vec3()  # V3d up
            frame.matrix.at    = f.vec3()  # V3d at
            frame.matrix.pos   = f.vec3()  # V3d pos
            frame.parentIndex  = f.i32()   # int32 parent
            _matFlag           = f.i32()   # int32 matflag; values: 0, 3, 131075; unused

            # TODO:
            # f->matrix.optimize();
            # f->matrix.flags &= ~Matrix::IDENTITY;
            # if parentIndex >= 0:
            #     frameList.frames[parentIndex].addChild(frame, append)

        for frame in frames:
            f.readExtension(frame)

        for frame in frames:
            if frame.parentIndex >= 0:
                frames[frame.parentIndex].addChild(frame)

        return frames

    def readGeometry (self, f : RWStream) -> 'RWGeometry':
        header = f.findChunk(PluginId.Struct)

        if not header:
            raise Exception('Geometry struct is not found')

        flags             = f.u32()  # uint32 flags
        triangleCount     = f.i32()  # int32 numTriangles
        vertexCount       = f.i32()  # int32 numVertices
        _morphTargetCount = f.i32()  # int32 numMorphTargets

        assert _morphTargetCount == 1

        geo = RWGeometry.create(vertexCount, triangleCount, flags)

        surfProps = SurfaceProps.getDefault()

        if header.version < 0x34000:
            surfProps.ambient  = f.f32()  # float32 ambient
            surfProps.specular = f.f32()  # float32 specular
            surfProps.diffuse  = f.f32()  # float32 diffuse

        # native data is NOT used
        assert not (geo.flags & RWGeometryFlag.NATIVE), 'has native data'

        if geo.flags & RWGeometryFlag.PRELIT:
            geo.colors = [ f.u8(4) for _ in range(geo.vertexCount) ]  # RGBA

        if geo.hasTextures:
            geo.texCoords = [ f.f32(2) for _ in range(geo.vertexCount) ]  # texCoords[vertex] = UV

        # don't use f.u16() due to endianness
        for i in range(geo.triangleCount):
            a = f.u32()
            b = f.u32()
            geo.triangles[i].v     = [ (a >> 16), (a & 0xFFFF), (b >> 16) ]
            geo.triangles[i].matId = b & 0xFFFF

        # ----------------------------------------------------------------

        mt = geo.morphTarget

        mt.boundingSphere        = Sphere()
        mt.boundingSphere.center = f.f32(3)
        mt.boundingSphere.radius = f.f32()

        hasVertices = bool(f.i32())
        hasNormals  = bool(f.i32())

        if hasVertices:
            mt.vertices = [ f.f32(3) for _ in range(geo.vertexCount) ]

        if hasNormals:
            mt.normals = [ f.f32(3) for _ in range(geo.vertexCount) ]

        # ----------------------------------------------------------------

        if not f.findChunk(PluginId.MaterialList):
            raise Exception('Material list is not found')

        geo.materials = self.readMaterials(f, surfProps)

        f.readExtension(geo)

        return geo

    def readMaterials (self, f : RWStream, surfProps : 'SurfaceProps') -> 'TMaterialList':
        materials : TMaterialList = []

        if not f.findChunk(PluginId.Struct):
            raise Exception('Material list struct is not found')

        materialCount = f.i32()

        if materialCount <= 0:
            return materials

        # indices of materials to increment refCounter using addRef() (or -1)
        _indices = f.i32(materialCount, asArray=True)

        assert all([ i < 0 for i in _indices ])

        for i in range(materialCount):
            if not f.findChunk(PluginId.Material):
                raise Exception('Material is not found')

            material = self.readMaterial(f, surfProps.clone())

            materials.append(material)

        return materials

    def readMaterial (self, f : RWStream, surfProps : 'SurfaceProps') -> Opt['Material']:
        header = f.findChunk(PluginId.Struct)

        if not header:
            raise Exception('Material struct is not found')

        mat = Material()

        _flags     = f.i32()        # int32 flags -- unused according to RW
        mat.color  = f.u8(4)        # RGBA color
        _unused    = f.i32()        # int32 unused
        hasTexture = bool(f.i32())  # int32 textured

        if header.version >= 0x30400:
            surfProps.ambient  = f.f32()
            surfProps.specular = f.f32()
            surfProps.diffuse  = f.f32()

        mat.surfaceProps = surfProps

        if hasTexture:
            if not f.findChunk(PluginId.Texture):
                raise Exception('Material texture is not found')

            mat.texture = self.readTexture(f)

            if mat.texture is None:
                raise Exception('Material texture is not loaded')

        # https://gtamods.com/wiki/Right_To_Render_(RW_Section)
        if not f.readExtension(mat):
            raise Exception('Failed to read material extension')

        return mat

    def readTexture (self, f : RWStream) -> Opt['MaterialTexture']:
        if not f.findChunk(PluginId.Struct):
            raise Exception('Texture struct is not found')

        tex = MaterialTexture()

        filterAddressing = f.u32()

        # if V addressing is 0, copy U
        if filterAddressing & 0xF000 == 0:
            filterAddressing |= (filterAddressing & 0xF00) << 4

        tex.filterType = filterAddressing & 0xFF          # see TextureFilterType
        tex.addrU      = (filterAddressing >> 8) & 0xF    # see TextureAddressingType
        tex.addrV      = (filterAddressing >> 12) & 0xF   # see TextureAddressingType
        tex.useMipMaps = TextureFilterType.MipNearest <= tex.filterType <= TextureFilterType.LinearMipLinear

        # if using mipmap filter mode, set automipmapping,
        # if 0x10000 is set, set mipmapping
        header = f.findChunk(PluginId.String)

        if not header:
            raise Exception('Failed to read texture name')

        tex.name = f.string(header.dataSize).lower()

        header = f.findChunk(PluginId.String)

        if not header:
            raise Exception('Failed to read texture mask name')

        tex.maskName = f.string(header.dataSize).lower() or None

        # TODO: WTF -- if (tex->refCount == 1) tex->filterAddressing = filterAddressing & 0xFFFF;

        if not f.readExtension(tex):
            raise Exception('Failed to read geometry material texture')

        return tex

    def readAtomic (self, f : RWStream, frames : TFrameList, geometries : List['RWGeometry']) -> Opt['RWAtomic']:
        header = f.findChunk(PluginId.Struct)

        if not header:
            raise Exception('Atomic struct is not found')

        assert header.version >= 0x30400

        atomic = RWAtomic()

        frameIndex    = f.i32()
        geometryIndex = f.i32()
        atomic.flags  = f.i32()  # always 5
        _unused       = f.i32()

        atomic.setFrame(frameIndex, frames[frameIndex])
        atomic.setGeometry(geometryIndex, geometries[geometryIndex])

        RWAtomic.Rights[0] = 0

        if not f.readExtension(atomic):
            raise Exception('Failed to read atomic extension')

        if RWAtomic.Rights[0]:
            atomic._pipeline = 'skinGlobals.pipelines[PLATFORM_GL3] from librw/src/gl/gl3skin.cpp:297'  # TODO

        return atomic

    def readLight (self, f : RWStream) -> 'RWLight':
        header = f.findChunk(PluginId.Struct)

        assert header
        assert header.version >= 0x30300

        light = RWLight.create()

        light.radius        = f.f32()   # float32 radius;
        light.setColor(f.f32(3))        # float32 red, green, blue;
        light.minusCosAngle = f.f32()   # float32 minusCosAngle;
        light.typeFlags     = f.u32()   # uint32 type_flags;

        # NO EXTENSIONS
        if not f.readExtension(light):
            raise Exception('Failed to read light extension')

        return light



def _test_ ():
    for filePath in iterFiles(GAME_DIR, True, [ DFF_EXT ]):
        print(filePath)
        _dff = DFFReader.fromFile(filePath)
        print(' ')



__all__ = [
    'DFF',
    'DFFReader',
    'RWAtomic',
    'RWClump',
    'RWGeometryFlag',
    'HAnimFlag',

    '_test_',
]



if __name__ == '__main__':
    _test_()
