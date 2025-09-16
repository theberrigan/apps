import struct, os, json
from typing import Any, List, Set, Dict, Tuple, Optional


class GeometryFlag:
    TRISTRIP = 0x0001
    POSITIONS = 0x0002
    TEXTURED = 0x0004
    PRELIT = 0x0008
    NORMALS = 0x0010
    LIGHT = 0x0020
    MODULATEMATERIALCOLOR = 0x0040
    TEXTURED2 = 0x0080
    NATIVE = 0x01000000


class MaterialEffect:
    NULL            = 0    # No Effect
    BUMPMAP         = 1    # Bump Map
    ENVMAP          = 2    # Environment Map (Reflections)
    BUMPENVMAP      = 3    # Bump Map/Environment Map
    DUAL            = 4    # Dual Textures
    UVTRANSFORM     = 5    # UV-Tranformation
    DUALUVTRANSFORM = 6    # Dual Textures/UV-Transformation


class UVAnimationTypeId:
    UVANIMATION = 0x1C1


class HAnimationFlag:
    SUBHIERARCHY            = 0x0001    # hierarchy inherits from another hierarchy
    NOMATRICES              = 0x0002    # hierarchy doesn't use local matrices for bones
    UPDATEMODELLINGMATRICES = 0x1000    # update local matrices for bones
    UPDATELTMS              = 0x2000    # recalculate global matrices for bones
    LOCALSPACEMATRICES      = 0x4000    # hierarchy computes matrices in the local space


class HAnimationBoneFlag:
    POPPARENTMATRIX  = 1    # this flag must be set for bones which don't have child bones
    PUSHPARENTMATRIX = 2    # this flag must be set for all bones, except those which are the latest in a particular hierarchical level
    UNK              = 8    # ?

class PipelineSet:
    REFLECTIVE          = 0x53F20098
    VEHICLES            = 0x53F2009A
    NIGHT_VERTEX_COLORS = 0x53F2009C


# https://gtamods.com/wiki/Category:RW_Sections
class SectionType:
    # Generic
    ANY  = -1

    # RenderWare
    NAOBJECT        = 0x00
    STRUCT          = 0x01
    STRING          = 0x02
    EXTENSION       = 0x03
    CAMERA          = 0x05
    TEXTURE         = 0x06
    MATERIAL        = 0x07
    MATERIALLIST    = 0x08
    FRAMELIST       = 0x0E
    GEOMETRY        = 0x0F
    CLUMP           = 0x10
    LIGHT           = 0x12
    ATOMIC          = 0x14
    GEOMETRYLIST    = 0x1A
    ANIMANIMATION   = 0x1B    # https://gtamods.com/wiki/Anim_Animation_(RW_Section)
    RIGHT_TO_RENDER = 0x1F    # https://gtamods.com/wiki/Right_To_Render_(RW_Section)
    UVANIMDICT      = 0x2B    # https://gtamods.com/wiki/UV_Animation_Dictionary_(RW_Section)

    # ?
    MORPH_PLG            = 0x105  # https://gtamods.com/wiki/Morph_PLG_(RW_Section)
    SKY_MIPMAP_VAL       = 0x110  # https://gtamods.com/wiki/Sky_Mipmap_Val_(RW_Section)
    SKIN_PLG             = 0x116  # https://gtamods.com/wiki/Skin_PLG_(RW_Section)
    PARTICLES_PLG        = 0x118  # https://gtamods.com/wiki/Particles_PLG_(RW_Section)
    HANIM_PLG            = 0x11E  # https://gtamods.com/wiki/HAnim_PLG_(RW_Section)
    USER_DATA_PLG        = 0x11F  # https://gtamods.com/wiki/User_Data_PLG_(RW_Section)
    MATERIAL_EFFECTS_PLG = 0x120  # https://gtamods.com/wiki/Material_Effects_PLG_(RW_Section)
    ANISOTROPY_PLG       = 0x127  # https://gtamods.com/wiki/Anisotropy_PLG_(RW_Section)
    ADC_PLG              = 0x134  # Address Control flag, see RW reference vol.1 page 23
    UV_ANIMATION_PLG     = 0x135  # https://gtamods.com/wiki/UV_Animation_PLG_(RW_Section)
    BIN_MESH_PLG         = 0x50E  # https://gtamods.com/wiki/Bin_Mesh_PLG_(RW_Section)
    NATIVE_DATA_PLG      = 0x510  # https://gtamods.com/wiki/Native_Data_PLG_(RW_Section)

    # Rockstar
    PIPELINE            = 0x253F2F3   # https://gtamods.com/wiki/Pipeline_Set_(RW_Section)
    SPECULAR_MATERIAL   = 0x253F2F6   # https://gtamods.com/wiki/Specular_Material_(RW_Section)   Clump > Geometry List > Geometry > Material List > Material > Extension > Specular Material.
    EFFECT2D            = 0x253F2F8   # https://gtamods.com/wiki/2d_Effect_(RW_Section)           Clump > Geometry List > Geometry > Extension > 2d Effect
    NIGHT_VERTEX_COLOR  = 0x253F2F9   # https://gtamods.com/wiki/Extra_Vert_Colour_(RW_Section)   Clump > Geometry List > Geometry > Extension > Extra Vert Colour
    COLLISION_MODEL     = 0x253F2FA   # https://gtamods.com/wiki/Collision_Model_(RW_Section)     Clump > Extension > Collision Model
    REFLECTION_MATERIAL = 0x253F2FC   # https://gtamods.com/wiki/Reflection_Material_(RW_Section) Clump > Geometry List > Geometry > Material List > Material > Extension > Reflection Material
    BREAKABLE           = 0x253F2FD
    NODE_NAME           = 0x253F2FE

    _map = None

    @staticmethod
    def getName (value):
        if SectionType._map is None:
            SectionType._map = { getattr(SectionType, key): key for key in dir(SectionType) if key.isupper() }

        return SectionType._map[value] if value in SectionType._map else '0x{:X}'.format(value)


# def bytesToString (rawBytes : bytes):
#     leftBound = rawBytes.index(b'\x00') if b'\x00' in rawBytes else len(rawBytes)
#     return rawBytes[:leftBound].decode('ascii').strip()


class Reader:
    def __init__ (self, filePath):
        self.filePath = filePath
        self.descriptor = None
        self.open()

    def __del__ (self):
        self.close()

    def __enter__ (self):
        return self

    def __exit__ (self, *args, **kwargs):
        self.close()

    def open (self):
        if self.descriptor is None:
            self.descriptor = open(self.filePath, 'rb')

    def close (self):
        if self.descriptor:
            self.descriptor.close()
            self.descriptor = None

    def read (self, size=None):
        return self.descriptor.read(size)

    def readStruct (self, structFormat):
        return struct.unpack(structFormat, self.descriptor.read(struct.calcsize(structFormat)))

    def tell (self):
        return self.descriptor.tell()

    def seek (self, pos):
        return self.descriptor.seek(pos)


class VirtualReader:
    def __init__ (self, filePath):
        self.filePath = filePath
        self.cursor = 0
        self.size = 0
        self.buffer = None
        self.open()

    def __del__ (self):
        self.close()

    def __enter__ (self):
        return self

    def __exit__ (self, *args, **kwargs):
        self.close()

    def open (self):
        with open(self.filePath, 'rb') as f:
            self.buffer = f.read()
            self.cursor = 0
            self.size = len(self.buffer)

    def close (self):
        self.buffer = None
        self.cursor = 0
        self.size = 0

    def read (self, sizeToRead = None):
        sizeLeft = max(0, self.size - self.cursor)

        if sizeToRead is None or sizeToRead < 0 or sizeToRead >= sizeLeft:
            sizeToRead = sizeLeft

        if sizeToRead == 0:
            return b''

        chunk = self.buffer[self.cursor:self.cursor + sizeToRead]
        self.cursor += sizeToRead

        return chunk

    def tell (self):
        return self.cursor

    def seek (self, offset):
        if type(offset) != int or offset < 0:
            raise OSError('Invalid argument')

        self.cursor = offset

        return self.cursor

    def readString (self, stringLength):
        rawBytes = self.read(stringLength)
        leftBound = rawBytes.index(b'\x00') if b'\x00' in rawBytes else len(rawBytes)
        return rawBytes[:leftBound].decode('ascii').strip()

    def readStruct (self, structFormat):
        return struct.unpack(structFormat, self.read(struct.calcsize(structFormat)))

    # for debug purposes
    def readHex (self, sizeToRead):
        return ' '.join([ '{:02X}'.format(b) for b in list(self.read(sizeToRead)) ])


class SectionHeader:
    def __init__ (self, reader):
        self.reader = reader
        header = self.reader.readStruct('III')
        self.sectionType = header[0]
        self.contentSize = header[1]
        self.rwVersion = self.decodeVersion(header[2])
        self.headerEnd = self.reader.tell()
        self.contentEnd = self.headerEnd + self.contentSize

    @staticmethod
    def decodeVersion (version):
        if (version & 0xFFFF0000) == 0:
            return version << 8
        else:
            p1 = ((version >> 14) & 0x3FF00) + 0x30000
            p2 = (version >> 16) & 0x3F
            
            return p1 | p2

    def __str__ (self):
        return '{}(sectionType={}, contentSize={}, rwVersion=0x{:X})'.format(
            self.__class__.__name__,
            SectionType.getName(self.sectionType),
            self.contentSize, 
            self.rwVersion
        )


class Section:
    sectionType = SectionType.ANY
    parent = None
    isExtension = False

    def __init__ (self, dff, header=None, parent=None):
        self.dff = dff
        self.reader = dff.reader
        self.header = header
        self.parent = parent

        if not self.header:
            self.readHeader()

        if self.sectionType != SectionType.ANY and self.sectionType != self.header.sectionType:
            raise Exception('Expected section {}, but {} given ({})'.format(
                SectionType.getName(self.sectionType), 
                SectionType.getName(self.header.sectionType),
                self.reader.filePath
            ))

        self.readContent()

        assert self.isSectionEnd(), 'OOB'

    def readHeader (self):
        self.header = SectionHeader(self.reader)

    def readContent (self):
        raise NotImplementedError()

    def skipContent (self):
        self.reader.seek(self.header.contentEnd)

    def isSectionEnd (self):
        return self.reader.tell() == self.header.contentEnd


# Right To Render is a extension to an Atomic or Material
# It records which pipeline was attached to the Atomic or Material when
# it was being written so that it can be attached again when the file is read.
# https://gtamods.com/wiki/Right_To_Render_(RW_Section)
class RightToRenderSection (Section):
    sectionType = SectionType.RIGHT_TO_RENDER
    isExtension = True
    pluginId = 0
    extraData = 0

    def readContent (self):
        self.pluginId, self.extraData = self.reader.readStruct('<II')


# For example if the data is 0x53F2009A a specular material can be added to a non-vehicle object.
# Primarily this is used for vehicle upgrade parts and some cutscene objects.
# Vehicles are using this rendering pipeline by default and do not need a pipeline set.
# It is not possible to add specular or reflective materials to a player, pedestrian or other 'skinned' models.
# https://gtamods.com/wiki/Pipeline_Set_(RW_Section)
class PipelineSection (Section):
    sectionType = SectionType.PIPELINE
    isExtension = True
    pipelineSet = 0

    def readContent (self):
        self.pipelineSet = self.reader.readStruct('<I')[0]


# Clump > Geometry List > Geometry > Material List > Material > Extension > Specular Material
# It is used to store material information for specular lighting.
# On the PC and Xbox versions of the game a specular texture is not used.
# https://gtamods.com/wiki/Specular_Material_(RW_Section)
class SpecularMaterialSection (Section):
    sectionType = SectionType.SPECULAR_MATERIAL
    isExtension = True
    specularFactor = 0.0
    textureName = None

    def readContent (self):
        self.specularFactor = self.reader.readStruct('<f')[0]
        self.textureName = self.reader.readString(24)


class Effect2DType:
    ANY           = -1
    LIGHT         = 0
    PARTICLE      = 1
    PED_ATTRACTOR = 3
    SUN_GLARE     = 4
    ENTER_EXIT    = 6
    STREET_SIGN   = 7
    TRIGGER_POINT = 8
    COVER_POINT   = 9
    ESCALATOR     = 10


class Effect2DLightDataSize:
    NO_LOOK_AT  = 76
    HAS_LOOK_AT = 80


class Effect2DLightFlag1:
    CORONA_CHECK_OBSTACLES       = 0x1
    FOG_TYPE                     = 0x2  # |
    FOG_TYPE2                    = 0x4  # | TODO: why two fog type?
    WITHOUT_CORONA               = 0x8
    CORONA_ONLY_AT_LONG_DISTANCE = 0x10
    AT_DAY                       = 0x20
    AT_NIGHT                     = 0x40
    BLINKING1                    = 0x80


class Effect2DLightFlag2:
    CORONA_ONLY_FROM_BELOW     = 0x1
    BLINKING2                  = 0x2
    UPDATE_HEIGHT_ABOVE_GROUND = 0x4
    CHECK_DIRECTION            = 0x8
    BLINKING3                  = 0x10


class Effect2DLightCoronaShowMode:
    DEFAULT                               = 0
    RANDOM_FLASHING                       = 1
    RANDOM_FLASHING_ALWAYS_AT_WET_WEATHER = 2
    LIGHTS_ANIM_SPEED_4X                  = 3
    LIGHTS_ANIM_SPEED_2X                  = 4
    LIGHTS_ANIM_SPEED_1X                  = 5
    UNK1                                  = 6
    TRAFFIC_LIGHT                         = 7
    TRAIN_CROSS_LIGHT                     = 8
    UNK2                                  = 9
    AT_RAIN_ONLY                          = 10
    UNK3                                  = 11
    UNK4                                  = 12
    UNK5                                  = 13


class Effect2DPedAttractorType:
   ATM            = 0    # Ped uses ATM (at day time only)
   SEAT           = 1    # Ped sits (at day time only)
   STOP           = 2    # Ped stands (at day time only)
   PIZZA          = 3    # Ped stands for few seconds
   SHELTER        = 4    # Ped goes away after spawning, but stands if weather is rainy
   TRIGGER_SCRIPT = 5    # Launches an external script
   LOOK_AT        = 6    # Ped looks at object, then goes away
   SCRIPTED       = 7    # This type is not valid
   PARK           = 8    # Ped lays (at day time only, ped goes away after 6 PM)
   STEP           = 9    # Ped sits on steps


class Effect2DEnterExitFlag1:
    UNKNOWN_INTERIOR      = 0x1
    UNKNOWN_PAIRING       = 0x2
    CREATE_LINKED_PAIRING = 0x4
    REWARD_INTERIOR       = 0x8
    USED_REWARD_INTRANCE  = 0x10
    CARS_AND_AIRCRAFT     = 0x20
    BIKES_AND_MOTORCYCLES = 0x40
    DISABLE_ON_FOOT       = 0x80


class Effect2DEnterExitFlag2:
    ACCEPT_NPC_GROUP     = 0x1
    FOOD_DATE_FLAG       = 0x2
    UNKNOWN_BURGLARY     = 0x4
    DISABLE_EXIT         = 0x8
    BURGLARY_ACCESS      = 0x10
    ENTERED_WITHOUT_EXIT = 0x20
    ENABLE_ACCESS        = 0x40
    DELETE_ENEX          = 0x80


class Effect2D:
    effectType = Effect2DType.ANY

    def __init__ (self, reader, position, dataSize):
        self.reader = reader
        self.position = position
        self.dataSize = dataSize
        self.readEffect()

    def readEffect (self):
        raise NotImplementedError()


class Effect2DLight (Effect2D):
    effectType = Effect2DType.LIGHT
    color = (0.0, 0.0, 0.0, 0.0)
    coronaFarClip = 0.0
    pointLightRange = 0.0
    coronaSize = 0.0
    shadowSize = 0.0
    coronaShowMode = 0          # Effect2DLightCoronaShowMode
    coronaEnableReflection = 0
    coronaFlareType = 0
    shadowColorMultiplier = 0
    flags1 = 0                  # Effect2DLightFlag1
    coronaTextureName = ''
    shadowTextureName = ''
    shadowZDistance = 0
    flags2 = 0
    lookAt = (0.0, 0.0, 0.0, 0.0)

    def readEffect (self):
        self.color = self.reader.readStruct('<4B')

        (
            self.coronaFarClip,
            self.pointLightRange,
            self.coronaSize,
            self.shadowSize,
            self.coronaShowMode,
            self.coronaEnableReflection,
            self.coronaFlareType,
            self.shadowColorMultiplier,
            self.flags1
        ) = self.reader.readStruct('<4f5B')

        self.coronaTextureName = self.reader.readString(24)
        self.shadowTextureName = self.reader.readString(24)

        self.shadowZDistance, self.flags2 = self.reader.readStruct('<BB')

        if self.dataSize == Effect2DLightDataSize.HAS_LOOK_AT:
            self.lookAt = self.reader.readStruct('<3Bx')

        self.reader.read(1)  # skip padding


class Effect2DParticle (Effect2D):
    effectType = Effect2DType.PARTICLE
    particleEffectName = ''

    def readEffect (self):
        # The particle effect name is an entry in effects.fxp.
        self.particleEffectName = self.reader.readString(24)


class Effect2DPedAttractor (Effect2D):
    effectType = Effect2DType.PED_ATTRACTOR
    attractorType = 0   # Effect2DPedAttractorType
    rotation = (0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0)
    scriptName = ''     # If the PED just stands/sits/lays, this field is set to 'none'
    pedProbability = 0
    unk1 = 0
    notUsed1 = 0
    unk2 = 0
    notUsed2 = 0

    def readEffect (self):
        self.attractorType = self.reader.readStruct('<I')[0]
        self.rotation = self.reader.readStruct('<9f')
        self.scriptName = self.reader.readString(8)

        (
            self.pedProbability,
            self.unk1,
            self.notUsed1,
            self.unk2,
            self.notUsed2
        ) = self.reader.readStruct('<I4B')


class Effect2DSunGlare (Effect2D):
    effectType = Effect2DType.SUN_GLARE
    effectData = None

    def readEffect (self):
        # SUN_GLARE effect doesn't have payload data
        # But we read 0-sized data just in case
        self.effectData = self.reader.read(self.dataSize) or None


class Effect2DEnterExit (Effect2D):
    effectType = Effect2DType.ENTER_EXIT
    enterMarkerRotationAngle = 0.0
    markerRadiusX = 0.0
    markerRadiusY = 0.0
    markerPosition = (0.0, 0.0, 0.0)
    exitMarkerRotationAngle = 0.0
    interiorId = 0
    flags1 = 0    # Effect2DEnterExitFlag1
    skyColor = 0
    interiorName = ''
    timeOn = 0
    timeOff = 0
    flags2 = 0    # Effect2DEnterExitFlag2

    def readEffect (self):
        (
            self.enterMarkerRotationAngle,
            self.markerRadiusX,
            self.markerRadiusY
        ) = self.reader.readStruct('<3f')

        self.markerPosition = self.reader.readStruct('<3f')

        (
            self.exitMarkerRotationAngle,
            self.interiorId,
            self.flags1,
            self.skyColor
        ) = self.reader.readStruct('<fHBB')

        self.interiorName = self.reader.readString(8)

        (
            self.timeOn,
            self.timeOff,
            self.flags2
        ) = self.reader.readStruct('<3Bx')


class Effect2DStreetSign (Effect2D):
    effectType = Effect2DType.STREET_SIGN
    scale = (0.0, 0.0)
    rotation = (0.0, 0.0, 0.0)
    lineCount = 0
    symbolsInLine = 0
    textColor = 0
    lines = []

    def readEffect (self):
        self.scale = self.reader.readStruct('<ff')
        self.rotation = self.reader.readStruct('<3f')

        info = self.reader.readStruct('<H')[0]

        self.lineCount     = info & 3
        self.symbolsInLine = info & (3 << 2)
        self.textColor     = info & (3 << 4)

        self.lines = [ self.reader.readString(16) for i in range(4) ]

        self.reader.read(2)  # skip padding


class Effect2DTriggerPoint (Effect2D):
    effectType = Effect2DType.TRIGGER_POINT
    pointId = 0

    def readEffect (self):
        self.pointId = self.reader.readStruct('<I')[0]


class Effect2DCoverPoint (Effect2D):
    effectType = Effect2DType.COVER_POINT
    direction = (0.0, 0.0)
    coverType = 0

    def readEffect (self):
        self.direction = self.reader.readStruct('<ff')
        self.coverType = self.reader.readStruct('<I')[0]


class Effect2DEscalator (Effect2D):
    effectType = Effect2DType.ESCALATOR
    bottom = (0.0, 0.0, 0.0)
    top = (0.0, 0.0, 0.0)
    end = (0.0, 0.0, 0.0)
    direction = 0

    def readEffect (self):
        self.bottom = self.reader.readStruct('<3f')
        self.top = self.reader.readStruct('<3f')
        self.end = self.reader.readStruct('<3f')
        self.direction = self.reader.readStruct('<I')[0]


# Clump > Geometry List > Geometry > Extension > 2d Effect
# It is used to store 2D effects, which were located in ide files in previous versions.
# There can be multiple effects per section, their types are defined by an ID.
# https://gtamods.com/wiki/2d_Effect_(RW_Section)
class Effect2DSection (Section):
    sectionType = SectionType.EFFECT2D
    isExtension = True
    effectsMap = None
    effects = []

    def readContent (self):
        if not Effect2DSection.effectsMap:
            Effect2DSection.effectsMap = {
                item.effectType: item
                for item in globals().values()
                if isinstance(item, type) and issubclass(item, Effect2D)
            }

        effectsCount = self.reader.readStruct('<I')[0]

        for i in range(effectsCount):
            position = self.reader.readStruct('<3f')
            effectType, dataSize = self.reader.readStruct('<II')  # dataSize == 76 or 80

            if effectType not in Effect2DSection.effectsMap:
                raise Exception('Unknown 2D effect {} ({})'.format(effectType, self.reader.filePath))

            self.effects.append(Effect2DSection.effectsMap[effectType](self.reader, position, dataSize))


# Clump > Geometry List > Geometry > Extension > Extra Vert Colour
# In GTA San Andreas it is used to store alternative vertex colors displayed at night time.
# https://gtamods.com/wiki/Extra_Vert_Colour_(RW_Section)
class NightVertexColorSection (Section):
    sectionType = SectionType.NIGHT_VERTEX_COLOR
    isExtension = True
    nightVertexColors = []

    def readContent (self):
        isUsed = self.reader.readStruct('<I')[0]

        if not isUsed:
            return

        self.nightVertexColors = [ self.reader.readStruct('<4B') for i in range(self.parent.struct.vertexCount) ]


# Clump > Extension > Collision Model
# In GTA San Andreas it is used to store collision models for vehicles,
# complete with header, but only one model per section/file
# https://gtamods.com/wiki/Collision_Model_(RW_Section)
# https://gtamods.com/wiki/Collision_File ???
class CollisionModelSection (Section):
    sectionType = SectionType.COLLISION_MODEL
    isExtension = True
    collisionModel = None

    def readContent (self):
        self.collisionModel = self.reader.read(self.header.contentSize)  # TODO: whats format of the model?


# In GTA San Andreas it is used to override vehicle reflection maps
# Clump > Geometry List > Geometry > Material List > Material > Extension > Reflection Material
class ReflectionMaterialSection (Section):
    sectionType = SectionType.REFLECTION_MATERIAL
    isExtension = True
    envMapScale = (0.0, 0.0)
    envMapOffset = (0.0, 0.0)
    shininess = 0.0
    texturePtr = 0

    def readContent (self):
        self.envMapScale = self.reader.readStruct('<ff')
        self.envMapOffset = self.reader.readStruct('<ff')
        self.shininess = self.reader.readStruct('<f')[0]
        self.texturePtr = self.reader.readStruct('<I')[0]


# TODO: finish
# Clump > Geometry List > Geometry > Extension > Breakable
# It contains information on how to split breakable objects when they are hit.
# An object including this section has to be defined in object.dat.
# https://gtamods.com/wiki/Breakable_(RW_Section)
class BreakableSection (Section):
    sectionType = SectionType.BREAKABLE
    isExtension = True
    posRule = 0
    vertexCount = 0
    unk1 = 0
    vertexOffset = 0
    textureCoordOffset = 0
    preLitLumOffset = 0
    triangleCount = 0
    unk2 = 0
    vertexIndicesOffset = 0
    materialIndicesOffset = 0
    materialCount = 0
    unk3 = 0
    texturesOffset = 0
    textureNamesOffset = 0
    textureMasksOffset = 0
    ambientColorsOffset = 0
    vertices = []
    textureCoord = []
    preLitLum = []
    vertexIndices = []
    materialIndices = []
    textureNames = []
    textureMasks = []
    ambientColors = []

    def readContent (self):
        isUsed = self.reader.readStruct('<I')[0]

        if not isUsed:
            return

        (
            self.posRule,
            self.vertexCount,
            self.unk1,
            self.vertexOffset,
            self.textureCoordOffset,
            self.preLitLumOffset,
            self.triangleCount,
            self.unk2,
            self.vertexIndicesOffset,
            self.materialIndicesOffset,
            self.materialCount,
            self.unk3,
            self.texturesOffset,
            self.textureNamesOffset,
            self.textureMasksOffset,
            self.ambientColorsOffset
        ) = self.reader.readStruct('<IHHIIIHHIIHHIIII')

        self.vertices     = [ self.reader.readStruct('<3f') for i in range(self.vertexCount) ]
        self.textureCoord = [ self.reader.readStruct('<ff') for i in range(self.vertexCount) ]
        self.preLitLum    = [ self.reader.readStruct('<4B') for i in range(self.vertexCount) ]

        self.vertexIndices   = [ self.reader.readStruct('<3H') for i in range(self.triangleCount) ]
        self.materialIndices = [ self.reader.readStruct('<H')[0] for i in range(self.triangleCount) ]

        self.textureNames  = [ self.reader.readString(32) for i in range(self.materialCount) ]
        self.textureMasks  = [ self.reader.readString(32) for i in range(self.materialCount) ]
        self.ambientColors = [ self.reader.readStruct('<3f') for i in range(self.materialCount) ]


# FrameListSection.frameCount extensions per FrameListSection
# https://gtamods.com/wiki/Node_Name_(RW_Section)
class NodeNameSection (Section):
    sectionType = SectionType.NODE_NAME
    isExtension = True
    nodeName = ''

    def readContent (self):
        self.nodeName = self.reader.read(self.header.contentSize).decode('ascii').strip()


# One extension per GeometrySection
# Rarely used in the GTA, since it is not utilizing morphing
# https://gtamods.com/wiki/Morph_PLG_(RW_Section)
class MorphPGLSection (Section):
    sectionType = SectionType.MORPH_PLG
    isExtension = True

    def readContent (self):
        self.skipContent()
        print('Morph PGL section found but skipped ({})'.format(self.reader.filePath))


# One extension per Texture and TextureNative
# Not used in GTA SA PC version
# https://gtamods.com/wiki/Sky_Mipmap_Val_(RW_Section)
class SkyMipMapValueSection (Section):
    sectionType = SectionType.SKY_MIPMAP_VAL
    isExtension = True
    K = 0
    L = 0

    def readContent (self):
        chunk = self.reader.readStruct('<I')[0]

        self.K = chunk & (0xFFFFFFFF >> 18) - 2048  # [0, 4095] -> [-2048, 2047]
        self.L = chunk & (3 << 14)


# TODO: finish
# One extension per GeometrySection
# It is used to hold information about skinned model.
# https://gtamods.com/wiki/Skin_PLG_(RW_Section)
class SkinPLGSection (Section):
    sectionType = SectionType.SKIN_PLG
    isExtension = True
    boneCount = 0
    usedBoneCount = 0
    maxWeightsPerVertex = 0
    usedBones = tuple()
    vertexBoneIndices = []
    vertexBoneWeights = []
    skinToBoneMatrices = []
    boneLimit = 0
    meshCount = 0
    RLECount = 0
    meshBoneRemapIndices = tuple()
    meshBoneRLECount = tuple()
    meshBoneRLE = tuple()

    def readContent (self):
        self.boneCount, usedBoneCount, maxWeightsPerVertex = self.reader.readStruct('<BBBx')
        self.usedBones = self.reader.readStruct('<{}B'.format(usedBoneCount))
        self.vertexBoneIndices = [ self.reader.readStruct('<4B') for i in range(self.parent.struct.vertexCount) ]
        self.vertexBoneWeights = [ self.reader.readStruct('<4f') for i in range(self.parent.struct.vertexCount) ]

        for i in range(self.boneCount):
            if self.header.rwVersion < 0x37000 and maxWeightsPerVertex == 0:
                self.reader.readStruct('<I')  # skip unused

            self.skinToBoneMatrices.append([ self.reader.readStruct('<4f') for i in range(4) ])

        # The rest bytes don't occur in GTA SA PC-version DFFs, thus code is not tested
        # -----------------------------------------------------------------------------

        self.boneLimit, self.meshCount, self.RLECount = self.reader.readStruct('<III')

        if self.meshCount > 0:
            self.meshBoneRemapIndices = self.reader.readStruct('<{}B'.format(self.boneCount))
            self.meshBoneRLECount = self.reader.readStruct('<{}H'.format(self.meshCount))
            self.meshBoneRLE = self.reader.readStruct('<{}H'.format(self.RLECount))


class ParticlesPLGSection (Section):
    sectionType = SectionType.PARTICLES_PLG
    isExtension = True

    def readContent (self):
        self.skipContent()  # skip
        print('Particles PGL section found but skipped ({})'.format(self.reader.filePath))


# TODO: finish
# Frame List -> Extension
# It defines information for bones which can be used inside animations (*.ifp) to animate the object.
class HAnimPLGSection (Section):
    sectionType = SectionType.HANIM_PLG
    isExtension = True
    HAnimVersion = 0
    nodeId = 0
    nodeCount = 0
    flags = 0
    keyFrameSize = 0
    nodes = []

    def readContent (self):
        HAnimVersion, nodeId, nodeCount = self.reader.readStruct('<III')

        if nodeCount > 0:
            self.flags, self.keyFrameSize = self.reader.readStruct('<II')

        for i in range(nodeCount):
            nodeId, nodeIndex, flags = self.reader.readStruct('<III')
            self.nodes.append((nodeId, nodeIndex, flags))


class UserDataPLGSection (Section):
    sectionType = SectionType.USER_DATA_PLG
    isExtension = True

    def readContent (self):
        self.skipContent()  # skip
        print('User Data PGL section found but skipped ({})'.format(self.reader.filePath))


# Material Extension used to attach certain effects to material, such as bump mapping,
# reflections and UV-Animations. If a material defines material effects, the Atomic
# that draws the material's parent geometry also contains a material effects extension.
class MaterialEffectPLGSection (Section):
    sectionType = SectionType.MATERIAL_EFFECTS_PLG
    isExtension = True
    materialEffect = MaterialEffect.NULL

    def readContent (self):
        # print('after matfx header', self.reader.tell(), self.header.contentSize)
        materialEffect = self.reader.readStruct('<i')[0]

        # if materialEffect != MaterialEffect.NULL and self.header.contentSize == 4:
        #     print(self.parent)

        if materialEffect == MaterialEffect.NULL:
            return

        for i in range(2):
            effectType = self.reader.readStruct('<I')[0]
            # print(effectType)
            break

        self.skipContent()
        '''
        # print('---' * 30)
        _hdrend = self.reader.tell()
        _end = _hdrend + self.header.contentSize

        self.materialEffect = self.reader.readStruct('<I')[0]
        # print(_hdrend, self.header.contentSize, self.materialEffect)

        # if (_hdrend + self.header.contentSize) == self.reader.tell() and self.materialEffect != MaterialEffect.NULL:
        #     print('smth wrong')
        
        # if self.materialEffect == MaterialEffect.NULL:
        #     return  # TODO: is it correct?

        # print(self.materialEffect)
        for i in range(2):
            effectType = self.reader.readStruct('<I')[0]
            # print(self.reader.tell(), effectType)

            if effectType == MaterialEffect.NULL:
                break
            elif effectType == MaterialEffect.BUMPMAP:
                intensity, hasBumpMap = self.reader.readStruct('<fI')

                if hasBumpMap:
                    # print(self.header.contentSize)
                    # print('hasBumpMap', i, hasBumpMap, effectType, self.materialEffect)
                    bumpTexture = TextureSection(self.dff)

                hasHeightMap = self.reader.readStruct('<I')[0]

                if hasHeightMap:
                    heightTexture = TextureSection(self.dff)
            elif effectType == MaterialEffect.ENVMAP:
                reflection, useFrameBufferAlpha, hasEnvMap = self.reader.readStruct('<fII')

                if hasEnvMap:
                    envTexture = TextureSection(self.dff)
            else:
                print(_end, self.reader.tell(), effectType, self.materialEffect, self.header)

            # elif effectType == MaterialEffect.BUMPENVMAP:
            #     print('BUMPENVMAP', i, self.reader.filePath, self.reader.tell())
            #     envTexture = TextureSection(self.dff)
            #     print(envTexture.textureName)
            # else:
            #     self.reader.seek(_hdrend + self.header.contentSize)
            #     return
        self.reader.seek(_end)
        # print(self.reader.tell())
        '''


# Seems like not used in GTA SA on PC
class AnisotropyPLGSection (Section):
    sectionType = SectionType.ANISOTROPY_PLG
    isExtension = True
    anisotropyLevel : int = 1

    def readContent (self):
        self.anisotropyLevel = self.reader.readStruct('<I')[0]


# TODO: unknown section structure
# rccam.dff, bloodrb.dff
class ADCPLGSection (Section):
    sectionType = SectionType.ADC_PLG
    isExtension = True

    def readContent (self):
        self.reader.read(self.header.contentSize)


class UVAnimationPLGStructSection (Section):
    sectionType = SectionType.STRUCT
    animationCount = 0
    animationNames = []

    def readContent (self):
        mask = self.reader.readStruct('<I')[0]

        for i in range(8):
            self.animationCount += mask & (1 << i)

        self.animationNames = [ self.reader.readString(32) for i in range(self.animationCount) ]


# visagesign04.dff
class UVAnimationPLGSection (Section):
    sectionType = SectionType.UV_ANIMATION_PLG
    isExtension = True
    struct = None

    def readContent (self):
        self.struct = UVAnimationPLGStructSection(self.dff)

'''
Optimized representation of the model topology.
Triangles are grouped together into Meshes by their Material and stored as triangle strips 
when the rpGEOMETRYTRISTRIP flag is set in the Geometry, otherwise as triangle lists.
In pre-instanced (with native geometry data) files, the chunk looks different according to platform.
'''
class BinMeshPLGSection (Section):
    sectionType = SectionType.BIN_MESH_PLG
    isExtension = True
    flags = 0
    meshCount = 0
    totalIndexCount = 0
    meshes : List[Tuple[int, List[int]]] = []

    def readContent (self):
        self.flags, self.meshCount, self.totalIndexCount = self.reader.readStruct('<III')

        for i in range(self.meshCount):
            meshIndexCount, materialIndex = self.reader.readStruct('<II')
            # Don't check pre-instances & graphics API, because GTA SA on PC doesn't use it
            self.meshes.append((
                materialIndex,
                [ self.reader.readStruct('<i')[0] for j in range(meshIndexCount) ]
            ))


# Native geometry data is not used in GTA SA on PC
class NativeDataPLGSection (Section):
    sectionType = SectionType.NATIVE_DATA_PLG
    isExtension = True

    def readContent (self):
        self.skipContent()  # skip
        print('Native Data PGL section found but skipped ({})'.format(self.reader.filePath))


class ExtensionSection (Section):
    sectionType = SectionType.EXTENSION
    extMap = None
    sections = []

    def readContent (self):
        if not ExtensionSection.extMap:
            ExtensionSection.extMap = {
                item.sectionType: item
                for item in globals().values()
                if isinstance(item, type) and issubclass(item, Section) and item.isExtension
            }

        extEnd = self.reader.tell() + self.header.contentSize

        while self.reader.tell() < extEnd:
            extHeader = SectionHeader(self.reader)

            if extHeader.sectionType not in ExtensionSection.extMap:
                raise Exception('Extension section {} is not supported ({})'.format(
                    SectionType.getName(extHeader.sectionType),
                    self.reader.filePath
                ))

            self.sections.append(ExtensionSection.extMap[extHeader.sectionType](self.dff, extHeader, self.parent))


class StringSection (Section):
    sectionType = SectionType.STRING
    data = ''

    def readContent (self):
        self.data = self.reader.readString(self.header.contentSize)

    def __str__ (self):
        return self.data


class ClumpSection (Section):
    sectionType = SectionType.CLUMP
    struct = None
    frameList = None
    geometryList = None
    atomics = []
    extension = None

    def readContent (self):
        self.struct = ClumpStructSection(self.dff)
        self.frameList = FrameListSection(self.dff)
        self.geometryList = GeometryListSection(self.dff)
        self.atomics = [ AtomicSection(self.dff) for i in range(self.struct.atomicCount) ]

        # TODO:
        # - img/bonaventura_LAn.dff: has extra STRUCT/LIGHT sections
        # - img/sfw_waterfall.dff: UVANIMDICT instead of CLUMP    imported successfully by view_space3D_dff
        # - img/vgsN_scrollsgn01.dff UVANIMDICT instead of CLUMP  BUT!!! no plugin capable import it into blender

        # TODO: parse Light https://gtamods.com/wiki/Light_(RW_Section)
        for i in range(self.struct.lightCount):
            # Struct contains a 4 byte index into the Frame List for the Frame the Light should be attached to
            header = SectionHeader(self.reader)  # Struct
            self.reader.read(header.contentSize)
            header = SectionHeader(self.reader)  # Light
            self.reader.read(header.contentSize)

        # Skip Camera section since it is unused in GTA SA
        for i in range(self.struct.cameraCount):
            # Struct contains a 4 byte index into the Frame List for the Frame the Camera should be attached to
            self.reader.read(SectionHeader(self.reader).contentSize)  # Skip Struct
            self.reader.read(SectionHeader(self.reader).contentSize)  # Skip Camera

        self.extension = ExtensionSection(self.dff, None, self)


class ClumpStructSection (Section):
    sectionType = SectionType.STRUCT
    atomicCount = 0
    lightCount = 0
    cameraCount = 0

    def readContent (self):
        self.atomicCount = self.reader.readStruct('I')[0]

        if self.header.rwVersion > 0x33000:
            self.lightCount, self.cameraCount = self.reader.readStruct('II')

    def __str__ (self):
        return '{} {{\n\tatomicCount = {}\n\tlightCount = {}\n\tcameraCount = {}\n}}'.format(
            SectionType.getName(self.sectionType),
            self.atomicCount,
            self.lightCount,
            self.cameraCount
        )


class FrameListSection (Section):
    sectionType = SectionType.FRAMELIST
    struct = None
    extensions = []

    def readContent (self):
        self.struct = FrameListStructSection(self.dff)
        self.extensions = [ ExtensionSection(self.dff, parent=self) for i in range(self.struct.frameCount) ]


class FrameListStructSection (Section):
    sectionType : int = SectionType.STRUCT
    frameCount : int = 0
    frames : List[Tuple[Any, Any, int, int]] = []

    def readContent (self):
        self.frameCount = self.reader.readStruct('i')[0]

        for i in range(self.frameCount):
            rotation = self.reader.readStruct('9f')
            position = self.reader.readStruct('3f')
            parent, flags = self.reader.readStruct('II')
            # TODO: wrap to Frame class
            self.frames.append((rotation, position, parent, flags))

    def __str__ (self):
        return '{} {{\n\tframeCount = {}\n\tframes = [\n{},\n\t\t...\n\t]\n}}'.format(
            SectionType.getName(self.sectionType),
            self.frameCount,
            ',\n'.join(map(lambda x: '\t\t' + str(x), self.frames[:3]))
        )


class GeometryListSection (Section):
    sectionType = SectionType.GEOMETRYLIST
    struct = None
    geometry = []

    def readContent (self):
        self.struct = GeometryListStructSection(self.dff)
        self.geometry = [ GeometrySection(self.dff) for i in range(self.struct.geometryCount) ]


class GeometryListStructSection (Section):
    sectionType = SectionType.STRUCT
    geometryCount = 0

    def readContent (self):
        self.geometryCount = self.reader.readStruct('i')[0]


class GeometrySection (Section):
    sectionType = SectionType.GEOMETRY
    struct = None
    materialList = None
    extension = None

    def readContent (self):
        self.struct = GeometryStructSection(self.dff)
        self.materialList = MaterialListSection(self.dff)
        self.extension = ExtensionSection(self.dff, parent=self)


class GeometryStructSection (Section):
    sectionType = SectionType.STRUCT
    format = 0         # [ 1 byte flags1 | 1 byte tex count | 2 bytes flags2 ]
    triangleCount = 0
    vertexCount = 0
    morphCount = 0
    surfAmbient = 0.0
    surfSpecular = 0.0
    surfDiffuse = 0.0
    vertexColors = []
    textureUVs = []    # [0] - primary texture, [1] - environment map, [2:] - extra textures
    triangles = []
    morphs = []

    def readContent (self):
        (
            self.format,
            self.triangleCount,
            self.vertexCount,
            self.morphCount
        ) = self.reader.readStruct('Iiii')

        if self.header.rwVersion < 0x34001:
            self.surfAmbient, self.surfSpecular, self.surfDiffuse = self.reader.readStruct('fff')

        # Geometry must be instanced. Since instancing takes time, instanced geometry can be directly
        # written to a DFF, so the step can be skipped and the loading of the file will be optimized.
        # This means however that a pre-instanced DFF can only be used by the same platform that wrote the file.
        # When an instanced Geometry is streamed out, the Geometry chunk will contain no geometry 
        # data and the rpNATIVE flag will be set.
        # Pre-instanced DFFs are used in Vice City and San Andreas for PS2, Xbox and mobile devices.
        # Supported only non-instanced data.
        if (self.format & GeometryFlag.NATIVE) == 0:
            if self.format & GeometryFlag.PRELIT:
                # TODO: normalize [0-255] -> [0.0, 1.0]
                self.vertexColors = [ self.reader.readStruct('BBBB') for i in range(self.vertexCount) ]

            if self.format & (GeometryFlag.TEXTURED | GeometryFlag.TEXTURED2):
                textureCount = (self.format & 0x00FF0000) >> 16
                for i in range(textureCount):
                    # TODO: reverse second uv component
                    self.textureUVs.append([ self.reader.readStruct('ff') for j in range(self.vertexCount) ])

            for i in range(self.triangleCount):
                v2, v3, materialId, v1 = self.reader.readStruct('HHHH')

                if max(v1, v2, v3) >= self.vertexCount:
                    raise Exception('Vertex indices out of range for triangle.')

                self.triangles.append((v1, v2, v3, materialId))

        if self.morphCount != 1:
            # TODO: why?
            print('WARNING! Multiple frames not supported')

        for i in range(self.morphCount):
            bx, by, bz, br, hasVertices, hasNormals = self.reader.readStruct('ffffii')  # RwSphere boundingSphere(x, y, z, radius)
            vertices = [ self.reader.readStruct('fff') for i in range(self.vertexCount) ] if hasVertices else []
            normals = [ self.reader.readStruct('fff') for i in range(self.vertexCount) ] if hasNormals else []

            self.morphs.append(( bx, by, bz, br, vertices, normals ))


class MaterialListSection (Section):
    sectionType = SectionType.MATERIALLIST
    struct = None
    materials = []

    def readContent (self):
        self.struct = MaterialListStructSection(self.dff)
        self.materials = [ MaterialSection(self.dff) for i in range(self.struct.materialCount) ]


class MaterialListStructSection (Section):
    sectionType = SectionType.STRUCT
    materialCount = 0
    unks = []  # TODO: what is it?

    def readContent (self):
        self.materialCount = self.reader.readStruct('i')[0]
        self.unks = [ self.reader.readStruct('i')[0] for i in range(self.materialCount) ]


class MaterialSection (Section):
    sectionType = SectionType.MATERIAL
    struct = None
    texture = None
    extension = None

    def readContent (self):
        # print('after mat header', self.reader.tell())
        self.struct = MaterialStructSection(self.dff)
        self.texture = TextureSection(self.dff) if self.struct.isTextured > 0 else None
        self.extension = ExtensionSection(self.dff, parent=self)


class MaterialStructSection (Section):
    sectionType = SectionType.STRUCT
    flags = 0
    col = (0, 0, 0, 0)
    unk = 0
    isTextured = 0
    ambient = 0.0
    specular = 0.0
    diffuse = 0.0

    def readContent (self):
        self.flags = self.reader.readStruct('I')[0]
        self.col = self.reader.readStruct('BBBB')  # TODO: what is it?

        (
            self.unk,
            self.isTextured,
            self.ambient,
            self.specular,
            self.diffuse
        ) = self.reader.readStruct('iifff')


class TextureSection (Section):
    sectionType = SectionType.TEXTURE
    struct = None
    textureName = None
    alphaName = None
    extension = None

    def readContent (self):
        self.struct = TextureStructSection(self.dff)
        self.textureName = StringSection(self.dff)
        self.alphaName = StringSection(self.dff)
        self.extension = ExtensionSection(self.dff, parent=self)


class TextureStructSection (Section):
    sectionType = SectionType.STRUCT
    flags = 0
    unk = 0  # TODO: unk?

    def readContent (self):
        self.flags, self.unk = self.reader.readStruct('HH')


class AtomicSection (Section):
    sectionType = SectionType.ATOMIC
    struct = None
    extension = None

    def readContent (self):
        self.struct = AtomicStructSection(self.dff)
        self.extension = ExtensionSection(self.dff, parent=self)


class AtomicStructSection (Section):
    sectionType = SectionType.STRUCT
    frameIndex = 0
    geometryIndex = 0
    flags = 0
    unused = 0
    # internalGeometry is not used in GTA SA, so skip it

    def readContent (self):
        (
            self.frameIndex,
            self.geometryIndex,
            self.flags,
            self.unused
        ) = self.reader.readStruct('iiIi')


class UVAnimDictSection (Section):
    sectionType = SectionType.UVANIMDICT
    struct = None
    animations = []

    def readContent (self):
        self.struct = UVAnimDictStructSection(self.dff)
        self.animations = [ UVAnimAnimationSection(self.dff) for i in range(self.struct.animationCount) ]


class UVAnimDictStructSection (Section):
    sectionType = SectionType.STRUCT
    animationCount : int = 0

    def readContent (self):
        self.animationCount = self.reader.readStruct('I')[0]


class UVAnimAnimation:
    def __init__ (self, dff, frameCount):
        self.dff = dff
        self.reader = dff.reader
        self.animationName = self.reader.readStruct('<4x32s')[0].decode('ascii').strip('\0')
        self.nodeUVChannel = self.reader.readStruct('<8f')
        self.frames = []

        for i in range(frameCount):
            time = self.reader.readStruct('f')[0]
            scale = self.reader.readStruct('fff')
            position = self.reader.readStruct('fff')
            prevFrameIndex = self.reader.readStruct('i')[0]
            self.frames.append(( time, scale, position, prevFrameIndex ))


class UVAnimAnimationSection (Section):
    sectionType = SectionType.ANIMANIMATION
    version : int = 0
    typeId : int = 0
    frameCount : int = 0
    flags : int = 0
    duration : float = 0.0
    animation : UVAnimAnimation = None

    def readContent (self):
        (
            self.version,
            self.typeId,
            self.frameCount,
            self.flags,
            self.duration
        ) = self.reader.readStruct('4If')

        if self.typeId == UVAnimationTypeId.UVANIMATION:
            self.animation = UVAnimAnimation(self.dff, self.frameCount)
        else:
            raise Exception('Unexpected UV animation type id {:0X} ({})'.format(
                self.typeId,
                self.reader.filePath
            ))


# TODO: support multiple clumps, see /player.img/*
class DFF:
    def __init__ (self, filePath):
        self.filePath = filePath
        self.reader = VirtualReader(filePath)
        self.root = None

        header = SectionHeader(self.reader)

        if header.sectionType == SectionType.CLUMP:
            self.root = ClumpSection(self, header)
        elif header.sectionType == SectionType.UVANIMDICT:
            self.root = UVAnimDictSection(self, header)
        else:
            raise Exception('Unexpected root section {} ({})'.format(
                SectionType.getName(header.sectionType),
                self.filePath
            ))


# ------------------------------------------

def parseDFFs (dirName, errors = 0):
    for item in os.listdir(dirName):
        itemPath = os.path.join(dirName, item)

        if os.path.isdir(itemPath):
            errors = parseDFFs(itemPath, errors)
        elif os.path.isfile(itemPath) and item.lower().endswith('.dff'):
            try:
                model = DFF(itemPath)
            except Exception as e:
                errors += 1
                print(itemPath)
                print(str(e))

    return errors

if __name__ == '__main__':
    # for filePath in [
    #     'img/sfw_waterfall.dff',      # has 2DEFFECT instead of CLUMP
    #     'img/vgsN_scrollsgn01.dff',   # has 2DEFFECT instead of CLUMP
    #     'img/vegaswaterfall02.dff' ,  # has 2DEFFECT instead of CLUMP
    #     # 'img/bonaventura_LAn.dff',      # has (STRUCT + LIGHT) before extension
    #     # 'img/slamvan.dff',              # vehicle
    #     # 'img/zero.dff'                  # character (has skinning?)
    # ]:
    #     print(filePath)
    #     model = DFF(filePath)
    #     print('-' * 100)
    # ---------------------------------------------------
    # print('Errors:', parseDFFs('./GTA_SA_files/models/'))
    DFF('C:/RW/Graphics/bin/some.dff')
    
    # ---------------------------------------------------
    # model = DFF('./GTA_SA_files/models/gta3.img/androm.dff')  # bump map
    # model = DFF('./GTA_SA_files/models/cutscene.img/csbravura.dff')   # bumpenv map
    # model = DFF('./GTA_SA_files/models/gta3.img/visagesign04.dff')   # bumpenv map
    # model = DFF('./GTA_SA_files/models/gta3.img/bravura.dff')   # bumpenv map


'''
Clump - иерархия Frame'ов, к которой прикреплены Atomics, Lights и Cameras
Atomic ассоциирует Frame и Geometry

CLUMP
    STRUCT
    FRAMELIST
    GEOMETRYLIST
    ATOMIC *
    STRUCT + LIGHT   (if rwVersion > 0x33000)  STRUCT содержит UINT-индекс Frame во Frame List, к которому примязан этот Light
    STRUCT + CAMERA  (if rwVersion > 0x33000)  STRUCT содержит UINT-индекс Frame во Frame List, к которому примязана эта Camera
'''