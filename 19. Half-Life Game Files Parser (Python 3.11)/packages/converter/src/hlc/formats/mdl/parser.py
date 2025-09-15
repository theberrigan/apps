from typing import Union

from ...common import bfw
from ...common.consts import *
from ...maths import *
from ...utils import boundVertex
from ..bsp._temp import Texture, StudioModelFlags, TextureFlags, GL_LoadTexture
from .consts import *
from .types import *

from bfw.utils import *
from bfw.reader import *



# ----------------------------------------------------------------------------------------------------------------------


# remapping info
SUIT_HUE_START  = 192
SUIT_HUE_END    = 223
PLATE_HUE_START = 160
PLATE_HUE_END   = 191



class ModelWrongSignatureException (Exception):
    pass


class ModelWrongVersionException (Exception):
    pass


class ModelHeader:
    def __init__ (self):
        self.name              = None  # char   name[64]
        self.fileSize          = None  # int    length
        self.eyePos            = None  # vec3_t eyeposition         -- ideal eye position
        self.mins              = None  # vec3_t min                 -- ideal movement hull size
        self.maxs              = None  # vec3_t max
        self.bbMins            = None  # vec3_t bbmin               -- clipping bounding box
        self.bbMaxs            = None  # vec3_t bbmax
        self.flags             = None  # int    flags
        self.boneCount         = None  # int    numbones            -- bones
        self.boneOffset        = None  # int    boneindex
        self.boneCtrlCount     = None  # int    numbonecontrollers  -- bone controllers
        self.boneCtrlOffset    = None  # int    bonecontrollerindex
        self.hitBoxCount       = None  # int    numhitboxes         -- complex bounding boxes
        self.hitBoxOffset      = None  # int    hitboxindex
        self.animSeqCount      = None  # int    numseq              -- animation sequences
        self.animSeqOffset     = None  # int    seqindex
        self.seqGroupCount     = None  # int    numseqgroups        -- demand loaded sequences
        self.seqGroupOffset    = None  # int    seqgroupindex
        self.textureCount      = None  # int    numtextures         -- raw textures
        self.textureOffset     = None  # int    textureindex
        self.textureDataOffset = None  # int    texturedataindex    -- offset of the first texture data, used in _T.mdl to quickly find image data
        self.skinRefCount      = None  # int    numskinref          -- replaceable textures
        self.skinFamilyCount   = None  # int    numskinfamilies
        self.skinIndex         = None  # int    skinindex
        self.bodyPartCount     = None  # int    numbodyparts
        self.bodyPartOffset    = None  # int    bodypartindex
        self.attachmentCount   = None  # int    numattachments      -- queryable attachable points
        self.attachmentIndex   = None  # int    attachmentindex
        self.header2Index      = None  # int    studiohdr2index
        self.soundIndex        = None  # int    soundindex (unused)
        self.soundGroupCount   = None  # int    soundgroups (unused)
        self.soundGroupIndex   = None  # int    soundgroupindex (unused)
        self.transitionCount   = None  # int    numtransitions      -- animation node to animation node transition graph
        self.transitionOffset  = None  # int    transitionindex


# mstudiobodyparts_t
class ModelBodyPart:
    def __init__ (self):
        self.name       : str | None = None    # char name[64]
        self.modelCount : int | None = None    # int  nummodels
        self.base       : int | None = None    # int  base
        self.modelIndex : int | None = None    # int  modelindex -- index into models array


# mstudiobone_t
class ModelBone:
    def __init__ (self):
        self.name          : str | None  = None                        # char  name[32]           -- bone name for symbolic links
        self.parentIndex   : int | None  = None                        # int   parent             -- parent bone
        self.flags         : int | None  = None                        # int   flags
        self.boneCtrlIndex : list[int]   = [ -1, -1, -1, -1, -1, -1 ]  # int   bonecontroller[6]  -- bone controller index, -1 == none
        self.value         : list[float] = [ 0, 0, 0, 0, 0, 0 ]        # float value[6]           -- default DoF values
        self.scale         : list[float] = [ 0, 0, 0, 0, 0, 0 ]        # float scale[6]           -- scale for delta DoF values


# mstudiobonecontroller_t
class ModelBoneController:
    def __init__ (self):
        self.boneIndex : int | None   = None    # int   bone  -- -1 == 0
        self.type_     : int | None   = None    # int   type  -- X, Y, Z, XR, YR, ZR, M
        self.start     : float | None = None    # float start
        self.end       : float | None = None    # float end
        self.restIndex : int | None   = None    # int   rest  -- byte index value at rest
        self.index     : int | None   = None    # int   index -- 0-3 user set controller, 4 mouth


# mstudioseqdesc_t
class ModelAnimSeqDesc:
    def __init__ (self):
        self.label              : str | None   = None           # char   label[32]          -- sequence label
        self.fps                : float | None = None           # float  fps                -- frames per second
        self.flags              : int | None   = None           # int    flags              -- looping/non-looping flags
        self.activity           : int | None   = None           # int    activity
        self.actWeight          : int | None   = None           # int    actweight
        self.eventCount         : int | None   = None           # int    numevents
        self.eventOffset        : int | None   = None           # int    eventindex
        self.frameCount         : int | None   = None           # int    numframes          -- number of frames per sequence
        self.pivotCount         : int | None   = None           # int    numpivots          -- number of foot pivots
        self.pivotOffset        : int | None   = None           # int    pivotindex
        self.motionType         : int | None   = None           # int    motiontype
        self.motionBone         : int | None   = None           # int    motionbone
        self.linearMovement     : Vec3         = [ 0, 0, 0 ]    # vec3_t linearmovement
        self.autoMovePosIndex   : int | None   = None           # int    automoveposindex
        self.autoMoveAngleIndex : int | None   = None           # int    automoveangleindex
        self.bbMins             : Vec3         = [ 0, 0, 0 ]    # vec3_t bbmin              -- per sequence bounding box
        self.bbMaxs             : Vec3         = [ 0, 0, 0 ]    # vec3_t bbmax
        self.blendCount         : int | None   = None           # int    numblends
        self.animIndex          : int | None   = None           # int    animindex          -- mstudioanim_t pointer relative to start of sequence group data, [blend][bone][X, Y, Z, XR, YR, ZR]
        self.blendType          : list[int]    = [ 0, 0 ]       # int    blendtype[2]       -- X, Y, Z, XR, YR, ZR
        self.blendStart         : list[int]    = [ 0, 0 ]       # float  blendstart[2]      -- starting value
        self.blendEnd           : list[int]    = [ 0, 0 ]       # float  blendend[2]        -- ending value
        self.blendParent        : int | None   = None           # int    blendparent
        self.seqGroupIndex      : int | None   = None           # int    seqgroup           -- sequence group for demand loading
        self.entryNode          : int | None   = None           # int    entrynode          -- transition node at entry
        self.exitNode           : int | None   = None           # int    exitnode           -- transition node at exit
        self.nodeFlags          : int | None   = None           # int    nodeflags          -- transition rules
        self.nextSeq            : int | None   = None           # int    nextseq            -- auto advancing sequences


# mstudioseqgroup_t
class ModelAnimSeqGroup:
    def __init__ (self):
        self.label    : str | None = None    # char         label[32] -- textual name
        self.fileName : str | None = None    # char         name[64]  -- file name
        self.cache    : None       = None    # cache_user_t cache     -- cache index pointer
        self.nextSeq  : int | None = None    # int          data      -- hack for group 0


# mstudiobbox_t
class ModelBBox:
    def __init__ (self):
        self.boneIndex : int | None = None           # int    bone
        self.group     : int | None = None           # int    group -- intersection group
        self.bbMin     : Vec3       = [ 0, 0, 0 ]    # vec3_t bbmin -- bounding box
        self.bbMax     : Vec3       = [ 0, 0, 0 ]    # vec3_t bbmax


class ModelBody:
    def __init__ (self):
        self.name                  = None    # char  name[64]
        self.type_                 = None    # int   type
        self.boundRadius           = None    # float boundingradius
        self.meshCount             = None    # int   nummesh
        self.meshOffset            = None    # int   meshindex
        self.vertexCount           = None    # int   numverts           -- number of unique vertices
        self.vertexInfoOffset      = None    # int   vertinfoindex      -- vertex bone info
        self.vertexOffset          = None    # int   vertindex          -- vertex vec3_t
        self.normalCount           = None    # int   numnorms           -- number of unique surface normals
        self.normalInfoOffset      = None    # int   norminfoindex      -- normal bone info
        self.normalOffset          = None    # int   normindex          -- normal vec3_t
        self.blendVertexInfoOffset = None    # int   blendvertinfoindex -- boneweighted vertex info
        self.blendNormInfoOffset   = None    # int   blendnorminfoindex -- boneweighted normal info
        self.vertices              = []

MDL_SIGNATURE = b'IDST'
MDL_VERSION   = 10  # STUDIO_VERSION


# model_t
class MDL:
    def __init__ (self):
        self.filePath    : str | None                = None
        self.header      : ModelHeader | None        = None
        self.bones       : list[ModelBone]           = []
        self.boneCtrls   : list[ModelBoneController] = []
        self.hitBoxes    : list[ModelBBox]           = []
        self.seqDescs    : list[ModelAnimSeqDesc]    = []
        self.seqGroups   : list[ModelAnimSeqGroup]   = []
        self.textures    : list[Texture]             = []
        self.bodyParts   : list[ModelBodyPart]       = []
        self.bodies      : list[ModelBody]           = []
        self.transitions : list[int]                 = []

        self.mins      : Vec3                      = [ 0, 0, 0 ]
        self.maxs      : Vec3                      = [ 0, 0, 0 ]

        '''
        char		name[64];		// model name
        qboolean		needload;		// bmodels and sprites don't cache normally
    
        // shared modelinfo
        modtype_t		type;		// model type
        int		numframes;	// sprite's framecount
        byte		*mempool;		// private mempool (was synctype)
        int		flags;		// hl compatibility
    
    //
    // volume occupied by the model
    //
        vec3_t		mins, maxs;	// bounding box at angles '0 0 0'
        float		radius;
        
        // brush model
        int		firstmodelsurface;
        int		nummodelsurfaces;
    
        int		numsubmodels;
        dmodel_t		*submodels;	// or studio animations
    
        int		numplanes;
        mplane_t		*planes;
    
        int		numleafs;		// number of visible leafs, not counting 0
        mleaf_t		*leafs;
    
        int		numvertexes;
        mvertex_t		*vertexes;
    
        int		numedges;
        medge_t		*edges;
    
        int		numnodes;
        mnode_t		*nodes;
    
        int		numtexinfo;
        mtexinfo_t	*texinfo;
    
        int		numsurfaces;
        msurface_t	*surfaces;
    
        int		numsurfedges;
        int		*surfedges;
    
        int		numclipnodes;
        mclipnode_t	*clipnodes;
    
        int		nummarksurfaces;
        msurface_t	**marksurfaces;
    
        hull_t		hulls[MAX_MAP_HULLS];
    
        int		numtextures;
        texture_t		**textures;
    
        byte		*visdata;
    
        color24		*lightdata;
        char		*entities;
    //
    // additional model data
    //
        cache_user_t	cache;		// only access through Mod_Extradata
        '''

    @classmethod
    def fromFile (cls, filePath : str, isSubModel : bool = False) -> 'MDL':
        if not isFile(filePath):
            raise OSError(f'File does not exist: { filePath }')

        rawData = readBin(filePath)
        reader  = MemReader(rawData, filePath)

        return cls._read(reader, isSubModel)

    @classmethod
    def fromBuffer (cls, rawData : bytes, filePath : str | None = None, isSubModel : bool = False) -> 'MDL':
        reader = MemReader(rawData, filePath)

        return cls._read(reader, isSubModel)

    # Mod_LoadStudioModel | engine\common\mod_studio.c
    @classmethod
    def _read (cls, reader : MemReader, isSubModel : bool) -> 'MDL':
        model = cls()

        model.filePath = reader.getFilePath()

        cls._readHeader(reader, model)
        cls._readBones(reader, model)
        cls._readBoneControllers(reader, model)
        cls._readHitBoxes(reader, model)
        cls._readAnimSeqDescs(reader, model)
        cls._readAnimSeqGroups(reader, model)
        cls._readTextures(reader, model, isSubModel)
        cls._readBodyParts(reader, model)
        cls._readTransitions(reader, model)
        # TODO: read numskinfamilies, numskinref, skinindex (exist in ...T.mdl)

        if not areEqVec3(VEC3_ORIGIN, model.header.bbMins):
            copyVec3(model.header.bbMins, model.mins)
            copyVec3(model.header.bbMaxs, model.maxs)
        elif not areEqVec3(VEC3_ORIGIN, model.header.mins):
            copyVec3(model.header.mins, model.mins)
            copyVec3(model.header.maxs, model.maxs)
        else:
            pass  # TODO

        # assert not reader.remaining()

        return model

    @classmethod
    def _readHeader (cls, reader : MemReader, model : 'MDL') -> None:
        signature = reader.read(4)                  # int    ident

        if signature != MDL_SIGNATURE:
            raise ModelWrongSignatureException(f'Wrong signature: { formatByteString(signature) }')

        version = reader.i32()                      # int    version

        if version != MDL_VERSION:
            raise ModelWrongVersionException(f'Wrong version: { version }')

        model.header = header = ModelHeader()

        header.name              = reader.string(64)  # char   name[64]
        header.fileSize          = reader.i32()       # int    length
        header.eyePos            = reader.vec3()      # vec3_t eyeposition         -- ideal eye position
        header.mins              = reader.vec3()      # vec3_t min                 -- ideal movement hull size
        header.maxs              = reader.vec3()      # vec3_t max
        header.bbMins            = reader.vec3()      # vec3_t bbmin               -- clipping bounding box
        header.bbMaxs            = reader.vec3()      # vec3_t bbmax
        header.flags             = reader.u32()       # int    flags
        header.boneCount         = reader.i32()       # int    numbones            -- bones
        header.boneOffset        = reader.i32()       # int    boneindex
        header.boneCtrlCount     = reader.i32()       # int    numbonecontrollers  -- bone controllers
        header.boneCtrlOffset    = reader.i32()       # int    bonecontrollerindex
        header.hitBoxCount       = reader.i32()       # int    numhitboxes         -- complex bounding boxes
        header.hitBoxOffset      = reader.i32()       # int    hitboxindex
        header.animSeqCount      = reader.i32()       # int    numseq              -- animation sequences
        header.animSeqOffset     = reader.i32()       # int    seqindex
        header.seqGroupCount     = reader.i32()       # int    numseqgroups        -- demand loaded sequences
        header.seqGroupOffset    = reader.i32()       # int    seqgroupindex
        header.textureCount      = reader.i32()       # int    numtextures         -- raw textures
        header.textureOffset     = reader.i32()       # int    textureindex
        header.textureDataOffset = reader.i32()       # int    texturedataindex    -- offset of the first texture data, used in _T.mdl to quickly find image data
        header.skinRefCount      = reader.i32()       # int    numskinref          -- replaceable textures
        header.skinFamilyCount   = reader.i32()       # int    numskinfamilies
        header.skinIndex         = reader.i32()       # int    skinindex
        header.bodyPartCount     = reader.i32()       # int    numbodyparts
        header.bodyPartOffset    = reader.i32()       # int    bodypartindex
        header.attachmentCount   = reader.i32()       # int    numattachments      -- queryable attachable points
        header.attachmentIndex   = reader.i32()       # int    attachmentindex
        header.header2Index      = reader.i32()       # int    studiohdr2index
        header.soundIndex        = reader.i32()       # int    soundindex (unused)
        header.soundGroupCount   = reader.i32()       # int    soundgroups (unused)
        header.soundGroupIndex   = reader.i32()       # int    soundgroupindex (unused)
        header.transitionCount   = reader.i32()       # int    numtransitions      -- animation node to animation node transition graph
        header.transitionOffset  = reader.i32()       # int    transitionindex

        assert header.fileSize == reader.getSize()
        assert not header.header2Index
        assert not header.soundIndex
        assert not header.soundGroupIndex
        assert not header.soundGroupCount

    @classmethod
    def _readBones (cls, reader : MemReader, model : 'MDL') -> None:
        reader.seek(model.header.boneOffset)

        model.bones = bones = [ ModelBone() for _ in range(model.header.boneCount) ]

        for bone in bones:
            # mstudiobone_t
            bone.name          = reader.string(32)    # char  name[32]           -- bone name for symbolic links
            bone.parentIndex   = reader.i32()         # int   parent             -- parent bone
            bone.flags         = reader.i32()         # int   flags
            bone.boneCtrlIndex = reader.i32(6)        # int   bonecontroller[6]  -- bone controller index, -1 == none
            bone.value         = reader.f32(6)        # float value[6]           -- default DoF values
            bone.scale         = reader.f32(6)        # float scale[6]           -- scale for delta DoF values

    @classmethod
    def _readBoneControllers (cls, reader : MemReader, model : 'MDL') -> None:
        reader.seek(model.header.boneCtrlOffset)

        model.boneControllers = controllers = [ ModelBoneController() for _ in range(model.header.boneCtrlCount) ]

        for ctrl in controllers:
            # read mstudiobonecontroller_t
            ctrl.boneIndex = reader.i32()    # int   bone  -- -1 == 0
            ctrl.type_     = reader.i32()    # int   type  -- X, Y, Z, XR, YR, ZR, M
            ctrl.start     = reader.f32()    # float start
            ctrl.end       = reader.f32()    # float end
            ctrl.restIndex = reader.i32()    # int   rest  -- byte index value at rest
            ctrl.index     = reader.i32()    # int   index -- 0-3 user set controller, 4 mouth

    @classmethod
    def _readHitBoxes (cls, reader : MemReader, model : 'MDL') -> None:
        reader.seek(model.header.hitBoxOffset)

        model.hitBoxes = hitBoxes = [ ModelBBox() for _ in range(model.header.hitBoxCount) ]

        for hitBox in hitBoxes:
            # read mstudiobbox_t
            hitBox.boneIndex = reader.i32()     # int    bone
            hitBox.group     = reader.i32()     # int    group -- intersection group
            hitBox.bbMin     = reader.vec3()    # vec3_t bbmin -- bounding box
            hitBox.bbMax     = reader.vec3()    # vec3_t bbmax

    @classmethod
    def _readAnimSeqDescs (cls, reader : MemReader, model : 'MDL') -> None:
        reader.seek(model.header.animSeqOffset)

        model.seqDescs = seqDescs = [ ModelAnimSeqDesc() for _ in range(model.header.animSeqCount) ]

        for desc in seqDescs:
            # read mstudioseqdesc_t
            desc.label              = reader.string(32)    # char   label[32]          -- sequence label
            desc.fps                = reader.f32()         # float  fps                -- frames per second
            desc.flags              = reader.i32()         # int    flags              -- looping/non-looping flags
            desc.activity           = reader.i32()         # int    activity
            desc.actWeight          = reader.i32()         # int    actweight
            desc.eventCount         = reader.i32()         # int    numevents
            desc.eventOffset        = reader.i32()         # int    eventindex
            desc.frameCount         = reader.i32()         # int    numframes          -- number of frames per sequence
            desc.pivotCount         = reader.i32()         # int    numpivots          -- number of foot pivots
            desc.pivotOffset        = reader.i32()         # int    pivotindex
            desc.motionType         = reader.i32()         # int    motiontype
            desc.motionBone         = reader.i32()         # int    motionbone
            desc.linearMovement     = reader.vec3()        # vec3_t linearmovement
            desc.autoMovePosIndex   = reader.i32()         # int    automoveposindex
            desc.autoMoveAngleIndex = reader.i32()         # int    automoveangleindex
            desc.bbMins             = reader.vec3()        # vec3_t bbmin              -- per sequence bounding box
            desc.bbMaxs             = reader.vec3()        # vec3_t bbmax
            desc.blendCount         = reader.i32()         # int    numblends
            desc.animIndex          = reader.i32()         # int    animindex          -- mstudioanim_t pointer relative to start of sequence group data, [blend][bone][X, Y, Z, XR, YR, ZR]
            desc.blendType          = reader.i32(2)        # int    blendtype[2]       -- X, Y, Z, XR, YR, ZR
            desc.blendStart         = reader.f32(2)        # float  blendstart[2]      -- starting value
            desc.blendEnd           = reader.f32(2)        # float  blendend[2]        -- ending value
            desc.blendParent        = reader.i32()         # int    blendparent
            desc.seqGroupIndex      = reader.i32()         # int    seqgroup           -- sequence group for demand loading
            desc.entryNode          = reader.i32()         # int    entrynode          -- transition node at entry
            desc.exitNode           = reader.i32()         # int    exitnode           -- transition node at exit
            desc.nodeFlags          = reader.i32()         # int    nodeflags          -- transition rules
            desc.nextSeq            = reader.i32()         # int    nextseq            -- auto advancing sequences

    @classmethod
    def _readAnimSeqGroups (cls, reader : MemReader, model : 'MDL') -> None:
        reader.seek(model.header.seqGroupOffset)

        model.seqGroups = seqGroups = [ ModelAnimSeqGroup() for _ in range(model.header.seqGroupCount) ]

        for group in seqGroups:
            group.label    = reader.string(32)    # char         label[32] -- textual name
            group.fileName = reader.string(64)    # char         name[64]  -- file name
            group.cache    = reader.skip(4)       # cache_user_t cache     -- cache index pointer
            group.nextSeq  = reader.i32()         # int          data      -- hack for group 0

        # TODO: load anim sub-files (gl_studio.c: R_StudioGetAnim)

    # TODO: complete (skin)
    @classmethod
    def _readTextures (cls, reader : MemReader, model : 'MDL', isSubModel : bool) -> None:
        header = model.header

        assert header.textureCount or not isSubModel, 'Textures not found in either main or submodel'

        # Mod_StudioLoadTextures - load textures from current model if there are
        if header.textureCount > 0:
            assert header.textureOffset

            model.textures = textures = []

            for i in range(header.textureCount):
                headerOffset = header.textureOffset + (80 * i)

                reader.seek(headerOffset)

                # mstudiotexture_t (ptexture[i])
                name   = reader.string(64)    # char     name[64]
                flags  = reader.u32()         # uint32_t flags
                width  = reader.i32()         # int      width
                height = reader.i32()         # int      height
                offset = reader.i32()         # int      index

                assert getExt(name) == '.bmp'
                assert not name.lower().startswith('remap')

                # R_StudioLoadTexture

                flags2 = 0

                # <UNREACHABLE>
                if isBitSet(flags, StudioModelFlags.NormalMap):
                    flags2 |= TextureFlags.NormalMap
                # </UNREACHABLE>

                if name.lower().startswith('dm_base'):
                    size = width * height + 768

                    texture = Texture()

                    texture.name      = 'DM_Base'
                    texture.animMin   = PLATE_HUE_START
                    texture.animMax   = PLATE_HUE_END
                    texture.animTotal = SUIT_HUE_END

                    texture.width  = width
                    texture.height = height

                    flags  |= StudioModelFlags.ColorMap
                    flags2 |= TextureFlags.ForceColor

                if isBitSet(flags, StudioModelFlags.NoMips):
                    flags2 |= TextureFlags.NoMipMap

                mdlBasePath  = dropExt(getRelPath(model.filePath, GAME_DIR).replace('\\', '/'))
                texBaseName  = dropExt(name)
                internalPath = f'#{ mdlBasePath }/{ texBaseName }.mdl'

                reader.seek(headerOffset)
                headerBytes = reader.read(80)

                reader.seek(offset)
                dataBytes = reader.read(size)

                textureBuffer = headerBytes + dataBytes

                # print(name, width, height, index, header.textureIndex, model.filePath, internalPath)

                rgbData = GL_LoadTexture(internalPath, textureBuffer, len(textureBuffer), flags2)

                assert rgbData is not None

                texture = Texture()

                texture.name   = name
                texture.data   = rgbData
                texture.width  = rgbData.width
                texture.height = rgbData.height

                textures.append(texture)

        # Load textures from external "<base_model_name>t.mdl" file
        elif not isSubModel:
            assert model.filePath

            subModel = cls._loadSubModel(model.filePath)

            assert subModel

            # thdr->numskinfamilies * thdr->numskinref * sizeof(short);
            model.textures               = subModel.textures
            model.header.textureCount    = subModel.header.textureCount
            model.header.skinFamilyCount = subModel.header.skinFamilyCount
            model.header.skinRefCount    = subModel.header.skinRefCount

            # TODO: read skinFamilies and skinRefs, it is in engine\client\gl_studio.c:2307

    # TODO: complete
    @classmethod
    def _readBodyParts (cls, reader : MemReader, model : 'MDL') -> None:
        reader.seek(model.header.bodyPartOffset)

        model.bodyParts = bodyParts = [ ModelBodyPart() for _ in range(model.header.bodyPartCount) ]

        bodyCount = 0

        for bodyPart in bodyParts:
            # read mstudiobodyparts_t
            bodyPart.name       = reader.string(64)    # char name[64]
            bodyPart.modelCount = reader.i32()         # int  nummodels
            bodyPart.base       = reader.i32()         # int  base
            bodyPart.modelIndex = reader.i32()         # int  modelindex -- index into models array

            bodyCount += bodyPart.modelCount

        model.bodies = bodies = [ ModelBody() for _ in range(bodyCount) ]

        for body in bodies:
            # read mstudiomodel_t
            body.name                  = reader.string(64)    # char  name[64]
            body.type_                 = reader.i32()         # int   type
            body.boundRadius           = reader.f32()         # float boundingradius
            body.meshCount             = reader.i32()         # int   nummesh
            body.meshOffset            = reader.i32()         # int   meshindex
            body.vertexCount           = reader.i32()         # int   numverts           -- number of unique vertices
            body.vertexInfoOffset      = reader.i32()         # int   vertinfoindex      -- vertex bone info
            body.vertexOffset          = reader.i32()         # int   vertindex          -- vertex vec3_t
            body.normalCount           = reader.i32()         # int   numnorms           -- number of unique surface normals
            body.normalInfoOffset      = reader.i32()         # int   norminfoindex      -- normal bone info
            body.normalOffset          = reader.i32()         # int   normindex          -- normal vec3_t
            body.blendVertexInfoOffset = reader.i32()         # int   blendvertinfoindex -- boneweighted vertex info
            body.blendNormInfoOffset   = reader.i32()         # int   blendnorminfoindex -- boneweighted normal info

        boneMins : Vec3 = [ 0, 0, 0 ]
        boneMaxs : Vec3 = [ 0, 0, 0 ]
        vertexCount = 0

        for body in bodies:
            reader.seek(body.vertexOffset)

            body.vertices = []

            for i in range(body.vertexCount):
                vertex = reader.vec3()

                body.vertices.append(vertex)

                vertexCount = boundVertex(boneMins, boneMaxs, vertexCount, vertex)

    # TODO: is it correct?
    @classmethod
    def _readTransitions (cls, reader : MemReader, model : 'MDL') -> None:
        reader.seek(model.header.transitionOffset)

        print(model.header.transitionCount)
        model.transitions = reader.u8(model.header.transitionCount)

    @classmethod
    def _loadSubModel (cls, baseModelPath) -> Union['MDL', None]:
        path = splitExt(baseModelPath)
        path = path[0] + 't' + path[1]

        return cls.fromFile(path, True)

        # TODO: wrap with:
        # try:
        #     return Model.fromFile(path, True)
        # except:
        #     return None

def Mod_StudioComputeBounds (header : ModelHeader, mins : Vec3, maxs : Vec3, ignoreSeqs : bool):
    pass



def _test_ ():
    for filePath in iterFiles(MODELS_DIR, True, [ MODEL_EXT ]):
        print(filePath)
        MDL.fromFile(filePath)
        print(' ')



__all__ = [
    'MDL',

    '_test_',
]



if __name__ == '__main__':
    _test_()