from typing import Optional

from ...common import bfw
from ...common.types import *
from ...common.consts import *
from ...common.game_data import *
from ...common.fns import splitSeps, isEmptyString, toFloats, toInts

from ..dff import RWAtomic, RWClump, RWGeometryFlag, HAnimFlag
from ..txd import Texture
from ..col import ColModel, TempCollisions

from ..handling import VehicleHandlingData
from ..ped_stats.types import TPedStats, PedStats

from .consts import *
from .types import *

from bfw.utils import *
from bfw.types.enums import Enum



# TODO: load all modelNames
# TODO: load all txdNames
# TODO: load animFileName for VehicleObject and PedObject
# TODO: check inheritance
# TODO: check how different objects keep their atomics/clumps
# NOTE: weapon object keeps it's modelId in m_atomics[2]



class GameObjectType (Enum):
    Object     : int = 1  # MITYPE_SIMPLE
    TimeObject : int = 2  # MITYPE_TIME
    Weapon     : int = 3  # MITYPE_WEAPON
    Clump      : int = 4  # MITYPE_CLUMP
    Vehicle    : int = 5  # MITYPE_VEHICLE
    Ped        : int = 6  # MITYPE_PED
    FX2D       : int = 7
    Path       : int = 8  # unused in VC
    Generic    : int = 9  # category for models from initModelInfos


class GameObjects:
    def __init__ (self):
        # obj.id -> obj
        self.generics : Dict[int, SimpleObject]  = {}  # category for models from initModelInfos
        self.objs     : Dict[int, SimpleObject]  = {}
        self.timeObjs : Dict[int, TimeObject]    = {}
        self.weapons  : Dict[int, WeaponObject]  = {}
        self.clumps   : Dict[int, ClumpObject]   = {}
        self.vehicles : Dict[int, VehicleObject] = {}
        self.peds     : Dict[int, PedObject]     = {}
        self.fx2d     : Dict[int, FX2DObject]    = {}

    def getById (self, objId : int):
        for objs in [
            self.generics,
            self.objs,
            self.timeObjs,
            self.weapons,
            self.clumps,
            self.vehicles,
            self.peds,
        ]:
            obj = objs.get(objId)

            if obj is not None:
                return obj

    def getByName (self, name : str):
        name = name.lower()

        for obj in self.iter():
            if obj.modelName == name:
                return obj

        return None

    def iter (self):
        for objs in [
            self.generics,
            self.objs,
            self.timeObjs,
            self.weapons,
            self.clumps,
            self.vehicles,
            self.peds,
            # self.fx2d,
        ]:
            for obj in objs.values():
                yield obj

    def iterStatics (self) -> Iterator['SimpleObject']:
        for objGroup in [
            self.objs.values(),
            self.timeObjs.values(),
        ]:
            for obj in objGroup:
                yield obj


class VehicleType (Enum):
    Car   : int = 0
    Boat  : int = 1
    Train : int = 2
    Heli  : int = 3
    Plane : int = 4
    Bike  : int = 5


class VehicleClass (Enum):
    Ignore             : int = -1
    Normal             : int = 0
    Poor               : int = 1
    Rich               : int = 2
    Exec               : int = 3
    Worker             : int = 4
    Big                : int = 5
    Taxi               : int = 6
    Moped              : int = 7
    Motorbike          : int = 8
    LeisureBoat        : int = 9
    WorkerBoat         : int = 10
    Cops               : int = 11
    Cuban              : int = 12
    Haitian            : int = 13
    Street             : int = 14
    Diaz               : int = 15
    Biker              : int = 16
    Security           : int = 17
    Player             : int = 18
    Golfers            : int = 19
    Gang9              : int = 20
    CopsBoat           : int = 21
    FirstCarRating     : int = Normal
    FirstBoatRating    : int = LeisureBoat
    FirstGangCarRating : int = Cuban
    NumCarClasses      : int = Motorbike - FirstCarRating + 1
    NumBoatClasses     : int = WorkerBoat - FirstBoatRating + 1
    NumGangCarClasses  : int = Gang9 - FirstGangCarRating + 1
    TotalCustomClasses : int = NumCarClasses + NumBoatClasses


VEHICLE_CLASS_NAME_TO_ID = {
    'normal'      : VehicleClass.Normal,
    'poorfamily'  : VehicleClass.Poor,
    'richfamily'  : VehicleClass.Rich,
    'executive'   : VehicleClass.Exec,
    'worker'      : VehicleClass.Worker,
    'big'         : VehicleClass.Big,
    'taxi'        : VehicleClass.Taxi,
    'moped'       : VehicleClass.Moped,
    'motorbike'   : VehicleClass.Motorbike,
    'leisureboat' : VehicleClass.LeisureBoat,
    'workerboat'  : VehicleClass.WorkerBoat,
    'ignore'      : VehicleClass.Ignore,
}


# ePedType
class PedType (Enum):
    Player1    = 0
    Player2    = 1
    Player3    = 2
    Player4    = 3
    CivMale    = 4
    CivFemale  = 5
    Cop        = 6
    Gang1      = 7
    Gang2      = 8
    Gang3      = 9
    Gang4      = 10
    Gang5      = 11
    Gang6      = 12
    Gang7      = 13
    Gang8      = 14
    Gang9      = 15
    Emergency  = 16
    Fireman    = 17
    Criminal   = 18
    Unused1    = 19
    Prostitute = 20
    Special    = 21
    Unused2    = 22


PED_TYPE_NAME_TO_ID = {
    'PLAYER1'    : PedType.Player1,
    'PLAYER2'    : PedType.Player2,
    'PLAYER3'    : PedType.Player3,
    'PLAYER4'    : PedType.Player4,
    'CIVMALE'    : PedType.CivMale,
    'CIVFEMALE'  : PedType.CivFemale,
    'COP'        : PedType.Cop,
    'GANG1'      : PedType.Gang1,
    'GANG2'      : PedType.Gang2,
    'GANG3'      : PedType.Gang3,
    'GANG4'      : PedType.Gang4,
    'GANG5'      : PedType.Gang5,
    'GANG6'      : PedType.Gang6,
    'GANG7'      : PedType.Gang7,
    'GANG8'      : PedType.Gang8,
    'GANG9'      : PedType.Gang9,
    'EMERGENCY'  : PedType.Emergency,
    'FIREMAN'    : PedType.Fireman,
    'CRIMINAL'   : PedType.Criminal,
    'UNUSED1'    : PedType.Unused1,
    'PROSTITUTE' : PedType.Prostitute,
    'SPECIAL'    : PedType.Special,
    'UNUSED2'    : PedType.Unused2,
}


class FX2DType (Enum):
    Light        : int = 0  # EFFECT_LIGHT
    Particle     : int = 1  # EFFECT_PARTICLE
    Attractor    : int = 2  # EFFECT_ATTRACTOR
    PedAttractor : int = 3  # EFFECT_PED_ATTRACTOR
    SunGlare     : int = 4  # EFFECT_SUNGLARE


class ObjectLOD:
    @classmethod
    def create (cls, distance : TFloat = 0, isDamaged : TBool = False) -> Self:
        lod = cls()

        lod.distance  = distance
        lod.isDamaged = isDamaged

        return lod

    def __init__ (self):
        self.distance  : TFloat = None  # LOD distance
        self.isDamaged : TBool  = None

TLODs = Opt[List[ObjectLOD]]


class GameObject:
    def __init__ (self):
        self.type        : TInt                     = None  # see GameObjectType
        self.id          : TInt                     = None
        self.atomics     : Opt[Dict[int, RWAtomic]] = None
        self.atomicCount : TInt                     = None
        self.colModel    : Opt[ColModel]            = None
        self.objectId    : int                      = -1    # set by object.dat parser

    def setObjectId (self, objectId : int):
        self.objectId = objectId

    def isBuilding (self) -> bool:
        return self.type in [
            GameObjectType.Object,
            GameObjectType.TimeObject,
        ]

    def isSimple (self) -> bool:
        return self.type in [
            GameObjectType.Object,
            GameObjectType.TimeObject,
            GameObjectType.Weapon,
        ]

    def isClump (self) -> bool:
        return self.type in [
            GameObjectType.Clump,
            GameObjectType.Ped,
            GameObjectType.Vehicle,
        ]

# BaseModelInfo:
# - atomics[2] is often a pointer to the non-LOD modelinfo
# - m_lodDistances[2] holds the near distance for LODs
# SimpleModelInfo (BaseModelInfo):
# - keeps RwObject in m_atomics[0] (GetRwObject())
# - keeps RpAtomic in m_atomics[2] (GetRelatedModel(), SetRelatedModel())
# - has SetAtomic()
# -- obj.atomicCount = objCount
# TimeModelInfo (SimpleModelInfo)
# - m_otherTimeModelID keeps linked tobj id
# WeaponModelInfo (SimpleModelInfo)
# - keeps eWeaponType weaponId in m_atomics[2] (SetWeaponInfo())
# -- obj.atomicCount = 1
# ClumpModelInfo:
# - keeps anim file name in m_animFileName (SetAnimFile())


# CSimpleModelInfo
class SimpleObject (GameObject):
    def __init__ (self):
        super().__init__()

        self.modelName         : TStr  = None
        self.txdName           : TStr  = None
        self.lods              : TLODs = None

        self.wetRoadReflection : TBool = None
        self.noFade            : TBool = None
        self.drawLast          : TBool = None
        self.additive          : TBool = None
        self.isSubway          : TBool = None
        self.ignoreLight       : TBool = None
        self.noZWrite          : TBool = None
        self.noShadows         : TBool = None
        self.ignoreDrawDist    : TBool = None
        self.isCodeGlass       : TBool = None
        self.isArtistGlass     : TBool = None

        # 0 - no damage model
        # 1 - 1 and 2 are damage models
        # 2 - 2 is damage model
        # self.firstDamaged = 0  // index of first damaged model in self.lods

        #  uint16  m_isBigBuilding : 1;  // is obj.lods[0].distance > LOD_DISTANCE
        #  RpAtomic *m_atomics[3];  // stores atomics from DFF clump
        #  uint8  m_numAtomics;
        #  uint8  m_alpha;  // used to fade in/out loaded/unloaded props
        #  uint16 m_isDamaged : 1; // is model is damaged is game, and we need to draw damaged model instead of main one?

    def setAtomic (self, lodIndex : int, atomic : RWAtomic):
        if self.atomics is None:
            self.atomics = {}

        self.atomics[lodIndex] = atomic
        self.atomicCount = len(self.atomics)

        geo = atomic.getGeometry()

        if self.ignoreLight:
            geo.flags = clearBit(geo.flags, RWGeometryFlag.LIGHT)

        atomic._pipeline += ',worldPipe from game/src/extras/custompipes.cpp:380'


class TimeObject (SimpleObject):
    def __init__ (self):
        super().__init__()

        self.timeStart  : TInt            = None
        self.timeEnd    : TInt            = None
        self.otherModel : Opt[TimeObject] = None


# NOTE: originally inherited from SimpleObject
class WeaponObject (SimpleObject):
    def __init__ (self):
        super().__init__()

        # self.modelName    : TStr  = None
        # self.txdName      : TStr  = None
        # self.lods         : TLODs = None
        self.animFileName : TStr  = None
        self.weaponId     : TInt  = None  # in original saved to m_atomics[2] using CWeaponModelInfo::SetWeaponInfo()

    def setWeaponId (self, weaponId : int):
        self.weaponId = weaponId


class ClumpObject (GameObject):
    def __init__ (self):
        super().__init__()

        self.clump        : Opt[RWClump] = None
        self.modelName    : TStr         = None
        self.txdName      : TStr         = None
        self.animFileName : TStr         = None

    def setClump (self, clump : RWClump):
        self.clump = clump

        if clump.isSkinned():
            hierarchy = clump.getAnimHierarchy()

            assert hierarchy

            for atomic in clump.atomics:
                atomic.hierarchy = hierarchy

            skinAtomic = clump.getFirstAtomic()

            geometry    = skinAtomic.getGeometry()
            vertexCount = geometry.vertexCount
            skin        = geometry.getSkin()
            weights     = skin.weights

            assert len(skin.weights) == (vertexCount * 4)

            for i in range(vertexCount):
                sum_ = sum(weights[i * 4:i * 4 + 4])

                weights[i * 4 + 0] /= sum_
                weights[i * 4 + 1] /= sum_
                weights[i * 4 + 2] /= sum_
                weights[i * 4 + 3] /= sum_

            hierarchy.flags = HAnimFlag.HANIMHIERARCHYUPDATEMODELLINGMATRICES | HAnimFlag.HANIMHIERARCHYUPDATELTMS


class VehicleObject (ClumpObject):
    def __init__ (self):
        super().__init__()

        THandling = VehicleHandlingData | None

        self.vehicleType      : TInt      = None
        self.gameName         : TStr      = None
        self.vehicleClassName : TStr      = None
        self.vehicleClass     : TInt      = None
        self.frequency        : TInt      = None
        self.level            : TInt      = None
        self.compRules        : TInt      = None
        self.handlingName     : TStr      = None
        self.handling         : THandling = None


class CarObject (VehicleObject):
    def __init__ (self):
        super().__init__()

        self.wheelId    : TInt   = None
        self.wheelScale : TFloat = None


class BoatObject (VehicleObject):
    def __init__ (self):
        super().__init__()


class TrainObject (VehicleObject):
    def __init__ (self):
        super().__init__()


class HelicopterObject (VehicleObject):
    def __init__ (self):
        super().__init__()


class PlaneObject (VehicleObject):
    def __init__ (self):
        super().__init__()

        self.lodId      : TInt   = None
        self.wheelScale : TFloat = None


class BikeObject (VehicleObject):
    def __init__ (self):
        super().__init__()

        self.steerAngle : TInt   = None
        self.wheelScale : TFloat = None


class PedObject (ClumpObject):
    def __init__ (self):
        super().__init__()

        self.pedTypeName   : TStr                     = None
        self.pedType       : TInt                     = None  # see PedType
        self.pedStatsName  : TStr                     = None
        self.pedStats      : TPedStats                = None
        self.animGroupName : TStr                     = None
        self.animGroupId   : TInt                     = None
        self.animGroup     : Opt[AnimAssocDefinition] = None
        self.canDriveCars  : TInt                     = None
        self.radio1        : TInt                     = None
        self.radio2        : TInt                     = None


class FX2DObject (GameObject):
    NextFXId : int = 1

    @classmethod
    def genId (cls) -> int:
        fxId = cls.NextFXId

        cls.NextFXId += 1

        return fxId

    def __init__ (self):
        super().__init__()

        self.id       : TInt  = None
        self.ownerId  : TInt  = None
        self.position : TVec3 = None
        self.color    : TRGBA = None


class FX2DLightObject (FX2DObject):
    def __init__ (self):
        super().__init__()

        self.coronaName      : TStr         = None  # in particles.txd
        self.shadowName      : TStr         = None  # in particles.txd
        self.coronaTexture   : Opt[Texture] = None
        self.shadowTexture   : Opt[Texture] = None
        self.distance        : TFloat       = None
        self.range           : TFloat       = None
        self.size            : TFloat       = None
        self.shadowSize      : TFloat       = None
        self.shadowIntensity : TInt         = None
        self.lightType       : TInt         = None
        self.roadReflection  : TInt         = None
        self.flareType       : TInt         = None
        self.flags           : TInt         = None


class FX2DParticleObject (FX2DObject):
    def __init__ (self):
        super().__init__()

        self.fxType    : TInt   = None
        self.direction : TVec3  = None
        self.scale     : TFloat = None


class FX2DAttractorObject (FX2DObject):
    def __init__ (self):
        super().__init__()

        self.fxType      : TInt  = None
        self.direction   : TVec3 = None
        self.probability : TInt  = None


class FX2DPedAttractorObject (FX2DObject):
    def __init__ (self):
        super().__init__()

        self.fxType         : TInt  = None
        self.queueDirection : TVec3 = None
        self.useDirection   : TVec3 = None


class FX2DLightFlag (Enum):
    LosCheck   = 1                      # LIGHTFLAG_LOSCHECK    -- same order as CPointLights flags, must start at 2
    FogNormal  = 2                      # LIGHTFLAG_FOG_NORMAL  -- can have light and fog
    FogAlways  = 4                      # LIGHTFLAG_FOG_ALWAYS  -- fog only
    HideObject = 8                      # LIGHTFLAG_HIDE_OBJECT -- hide the object instead of rendering light (???)
    LongDist   = 16                     # LIGHTFLAG_LONG_DIST
    Fog        = FogNormal | FogAlways


# CModelInfo::Initialise()
def initModelInfos (ctx):
    assert ctx.tempColModels

    ctx.modelInfos = GameObjects()

    for modelId, colModel in [
        (ModelId.CAR_DOOR,   ctx.tempColModels.ModelDoor1),
        (ModelId.CAR_BUMPER, ctx.tempColModels.ModelBumper1),
        (ModelId.CAR_PANEL,  ctx.tempColModels.ModelPanel1),
        (ModelId.CAR_BONNET, ctx.tempColModels.ModelBonnet1),
        (ModelId.CAR_BOOT,   ctx.tempColModels.ModelBoot1),
        (ModelId.CAR_WHEEL,  ctx.tempColModels.ModelWheel1),
        (ModelId.BODYPARTA,  ctx.tempColModels.ModelBodyPart1),
        (ModelId.BODYPARTB,  ctx.tempColModels.ModelBodyPart2),
    ]:
        assert colModel

        model = SimpleObject()

        model.id          = modelId
        model.colModel    = colModel
        model.txdName     = 'generic'
        model.atomicCount = 1
        model.lods        = [ ObjectLOD.create(80, False) ]

        ctx.modelInfos.generics[model.id] = model


# https://gta.fandom.com/wiki/IDE
class IDEReader:
    @classmethod
    def fromFile (cls, filePath : str, ctx : Opt[Any] = None) -> GameObjects:
        if not isFile(filePath):
            raise OSError(f'File does not exist: { filePath }')

        text = readText(filePath, encoding='utf-8')

        return cls(ctx).read(text)

    def __init__ (self, ctx : Opt[Any] = None):
        self.ctx : Opt[Any] = ctx

        if self.ctx:
            self.objs : GameObjects = self.ctx.modelInfos
        else:
            self.objs : GameObjects = GameObjects()

    # CFileLoader::LoadObjectTypes
    def read (self, text : str) -> GameObjects:
        lines = text.split('\n')

        objType = None

        for line in lines:
            line = line.strip()

            if isEmptyString(line) or line[0] in '#\x00':
                continue

            if not objType:
                match line:
                    case 'objs':
                        objType = GameObjectType.Object
                    case 'tobj':
                        objType = GameObjectType.TimeObject
                    case 'weap':
                        objType = GameObjectType.Weapon
                    case 'hier':
                        objType = GameObjectType.Clump
                    case 'cars':
                        objType = GameObjectType.Vehicle
                    case 'peds':
                        objType = GameObjectType.Ped
                    case 'path':
                        objType = GameObjectType.Path
                    case '2dfx':
                        objType = GameObjectType.FX2D
                    case _:
                        raise Exception(f'Expected section, but unexpected token given: { line }')

                continue

            if line == 'end':
                objType = None
                continue

            values = splitSeps(line)

            match objType:
                case GameObjectType.Object:
                    self.addObject(values, False)

                case GameObjectType.TimeObject:
                    self.addObject(values, True)

                case GameObjectType.Weapon:
                    self.addWeapon(values)

                case GameObjectType.Clump:
                    self.addClump(values)

                case GameObjectType.Vehicle:
                    self.addVehicle(values)

                case GameObjectType.Ped:
                    self.addPed(values)

                case GameObjectType.FX2D:
                    self.addFX2D(values)

                case GameObjectType.Path:
                    raise Exception('"path" section of .ide file is not used in VC')

        # TODO: link lod models
        # quasi-lod (any model with obj.lods[0].distance > LOD_DISTANCE):
        # - atomic[2] = mainModel
        # - lods[0] - the only not-damaged lod
        # - lods[0].distance - far distance (draw obj until distance to it <= this value)
        # - lods[2].distance - near distance (draw obj until distance to it > this value)
        #   if !mainModel: lods[2].distance = 0, else: lods[2].distance = mainModel[indexOfFirstNotDamagedLOD].distance
        # - draw this lod while: lods[2].distance <= distance_to_this_lod < lods[0].distance

        # "lod..." always contains 1 not-damaged lod with distance > 300
        # non-lod:
        # - if 3: 3rd always damaged
        # - if 2: 2nd sometimes damaged
        # - if 1: no damaged
        # both linked models have only 1 lod
        '''
        for obj in self.objs.iterStatics():
            # if obj.lods[0].distance > LOD_DISTANCE:
            #     print(obj.modelName, ' '.join([ str(l.distance) for l in obj.lods ]))

            prefix = obj.modelName[:3]
            suffix = obj.modelName[3:]

            # if prefix != 'lod' and len(obj.lods) == 1:
            #     print(obj.modelName, ' '.join([ str(l.distance) + str(l.isDamaged) for l in obj.lods ]))
            #     assert not obj.lods[0].isDamaged
            #
            # continue

            if prefix == 'lod':
                continue

            lodModel = self.getStaticByName('lod' + suffix)

            if lodModel:
                print(obj.modelName, ' '.join([ str(l.distance) + str(l.isDamaged) for l in obj.lods ]), lodModel.modelName, ' '.join([ str(l.distance) + str(l.isDamaged) for l in lodModel.lods ]))
                assert len(obj.lods) == len(lodModel.lods) == 1, (len(obj.lods), len(lodModel.lods))

            # self.findModelLOD(obj)
        '''
        '''
        for obj in self.objs.iterStatics():
            _obj_relatedModel = None

            if obj.lods[0].distance > LOD_DISTANCE and not _obj_relatedModel:
                _obj_isBigBuilding = True
                _obj_relatedModel = None

                for obj2 in self.objs.iterStatics():
                    if obj2 != obj and obj2.modelName[3:] == obj.modelName[3:]:
                        print(obj2.modelName, len(obj2.lods), obj.modelName, len(obj.lods))
                        _obj_relatedModel = obj2
                        break

                relatedModel = _obj_relatedModel

                if relatedModel:
                    print(obj.modelName, obj2.modelName)
                    # related->GetLargestLodDistance()
                    # 0: no damage model; 1: 1 and 2 are damage models; 2: 2 is damage model
                    m_firstDamaged = False
                    m_isDamaged = False

                    for lod in obj.lods:
                        if lod.isDamaged:
                            m_firstDamaged = True
                            break

                    if m_firstDamaged is False or m_isDamaged:
                        d = obj.lods[obj.atomicCount - 1].distance
                    else:
                        d = obj.lods[m_firstDamaged - 1].distance
                    # /related->GetLargestLodDistance()

                    obj.lods[2].distance = d

                    if obj.drawLast:
                        obj.drawLast = False
                else:
                    assert obj.modelName == 'airtrain_vlo', obj.modelName
                    # obj.lods[2].distance = 0  # NEAR_DRAW_DIST
        '''

        return self.objs

    # find low LOD for the model
    def getStaticByName (self, name : str) -> Opt[SimpleObject]:
        for obj in self.objs.iterStatics():
            if obj.modelName == name:
                return obj

        return None

    def filterString (self, value : str) -> Optional[str]:
        if value.lower() == 'null':
            return None

        return value

    def parseLCString (self, name : str) -> TStr:
        return self.filterString(name.lower())

    def createLODs (self, lodDistances : list[float]) -> list[ObjectLOD]:
        lods = [ ObjectLOD.create(d, False) for d in lodDistances ]

        match len(lods):
            case 2:
                if lods[0].distance >= lods[1].distance:
                    lods[1].isDamaged = True
            case 3:
                if lods[0].distance < lods[1].distance:
                    if lods[1].distance >= lods[2].distance:
                        lods[2].isDamaged = True
                else:
                    lods[1].isDamaged = True
                    lods[2].isDamaged = True

        return lods

    def linkTimeObjects (self, obj : TimeObject):
        baseName = obj.modelName[:-3]
        suffix   = obj.modelName[-3:]

        if suffix == '_nt':
            suffix = '_dy'
        elif suffix == '_dy':
            suffix = '_nt'
        else:
            return

        otherModelName = baseName + suffix

        obj2 : TimeObject

        for obj2 in self.objs.timeObjs.values():
            if obj2.modelName == otherModelName:
                assert not obj2.otherModel

                obj.otherModel  = obj2
                obj2.otherModel = obj

                break

    def addObject (self, values : list[str], isTimeObj : bool):
        if isTimeObj:
            obj = TimeObject()
            obj.type = GameObjectType.TimeObject
        else:
            obj = SimpleObject()
            obj.type = GameObjectType.Object

        obj.id        = int(values[0])
        obj.modelName = self.parseLCString(values[1])
        obj.txdName   = self.parseLCString(values[2])
        objCount      = int(values[3])
        obj.lods      = self.createLODs(toFloats(values[4:4 + objCount]))
        flags         = int(values[4 + objCount])

        if isTimeObj:
            obj.timeStart = int(values[4 + objCount + 1])
            obj.timeEnd   = int(values[4 + objCount + 2])

        obj.wetRoadReflection = bool(flags & 1)
        obj.noFade            = bool(flags & 2)
        obj.drawLast          = bool(flags & (4 | 8))
        obj.additive          = bool(flags & 8)
        obj.isSubway          = bool(flags & 0x10)
        obj.ignoreLight       = bool(flags & 0x20)
        obj.noZWrite          = bool(flags & 0x40)
        obj.noShadows         = bool(flags & 0x80)
        obj.ignoreDrawDist    = bool(flags & 0x100)
        obj.isCodeGlass       = bool(flags & 0x200)
        obj.isArtistGlass     = bool(flags & 0x400)

        # TODO: check
        # obj.atomicCount = objCount
        # obj.atomics     = []

        ModelId.setModelId(obj.modelName, obj.id)

        if isTimeObj:
            self.linkTimeObjects(obj)
            self.objs.timeObjs[obj.id] = obj
        else:
            self.objs.objs[obj.id] = obj

    def addWeapon (self, values : list[str]):
        obj = WeaponObject()

        obj.type         = GameObjectType.Weapon
        obj.id           = int(values[0])
        obj.modelName    = self.parseLCString(values[1])
        obj.txdName      = self.parseLCString(values[2])
        obj.animFileName = self.parseLCString(values[3])
        objCount         = int(values[4])
        obj.lods         = self.createLODs(toFloats(values[5:5 + objCount]))

        # Weapon stores weaponId in obj.atomics[2]
        # TODO: check
        # obj.atomicCount = 1
        # obj.atomics     = []

        if self.ctx:
            obj.colModel = self.ctx.tempColModels.ModelWeapon
            assert obj.colModel

        ModelId.setModelId(obj.modelName, obj.id)

        self.objs.weapons[obj.id] = obj

    def addClump (self, values : list[str]):
        obj = ClumpObject()

        assert len(values) == 3

        obj.type      = GameObjectType.Clump
        obj.id        = int(values[0])
        obj.modelName = self.parseLCString(values[1])
        obj.txdName   = self.parseLCString(values[2])
        obj.clump     = None

        if self.ctx:
            obj.colModel = self.ctx.tempColModels.ModelBBox

        self.objs.clumps[obj.id] = obj

    def addVehicle (self, values : list[str]):
        objType = values[3].lower()

        match objType:
            case 'car':
                obj = CarObject()

                obj.vehicleType = VehicleType.Car
                obj.wheelId     = int(values[11])
                obj.wheelScale  = float(values[12])

            case 'boat':
                obj = BoatObject()

                obj.vehicleType = VehicleType.Boat

            case 'train':
                obj = TrainObject()

                obj.vehicleType = VehicleType.Train

            case 'heli':
                obj = HelicopterObject()

                obj.vehicleType = VehicleType.Heli

            case 'plane':
                obj = PlaneObject()

                obj.vehicleType = VehicleType.Plane
                obj.lodId       = int(values[11])
                obj.wheelScale  = 1.0

            case 'bike':
                obj = BikeObject()

                obj.vehicleType = VehicleType.Bike
                obj.steerAngle  = int(values[11])
                obj.wheelScale  = float(values[12])

            case _:
                raise Exception(f'Unexpected object type: { objType }')

        obj.type             = GameObjectType.Vehicle
        obj.id               = int(values[0])
        obj.modelName        = self.parseLCString(values[1])
        obj.txdName          = self.parseLCString(values[2])
        obj.handlingName     = values[4].upper()
        obj.handling         = None
        obj.gameName         = values[5].upper()
        obj.animFileName     = self.parseLCString(values[6])
        obj.vehicleClassName = values[7].lower()
        obj.vehicleClass     = VEHICLE_CLASS_NAME_TO_ID.get(obj.vehicleClassName)
        obj.frequency        = int(values[8])
        obj.level            = int(values[9])
        obj.compRules        = int(values[10], 16)
        obj.clump            = None

        if self.ctx:
            obj.handling = self.ctx.handling.getByName(obj.handlingName)
            assert obj.handling, obj.handlingName

        assert obj.vehicleClass is not None, obj.vehicleClassName

        self.objs.vehicles[obj.id] = obj

    def addPed (self, values : list[str]):
        obj = PedObject()

        obj.type          = GameObjectType.Ped
        obj.id            = int(values[0])
        obj.modelName     = self.parseLCString(values[1])
        obj.txdName       = self.parseLCString(values[2])
        obj.pedTypeName   = values[3].upper()
        obj.pedType       = PED_TYPE_NAME_TO_ID.get(obj.pedTypeName)
        obj.pedStatsName  = values[4].upper()
        obj.pedStats      = None
        obj.animGroupName = values[5].lower()
        obj.animGroupId   = ANIM_NAME_TO_ASSOC[obj.animGroupName]
        obj.animGroup     = ANIM_ASSOC_DEFINITIONS[obj.animGroupId]
        obj.canDriveCars  = int(values[6], 16)
        obj.animFileName  = self.parseLCString(values[7])
        obj.radio1        = int(values[8])
        obj.radio2        = int(values[9])
        obj.clump         = None

        assert obj.pedType is not None, obj.pedTypeName

        if self.ctx:
            obj.pedStats = self.ctx.pedStats.getByName(obj.pedStatsName)
            assert obj.pedStats, obj.pedStatsName

            obj.colModel = self.ctx.tempColModels.ModelPed1
            assert obj.colModel

        self.objs.peds[obj.id] = obj

    def addFX2D (self, values : list[str]):
        objType = int(values[8])  # see FX2DType

        match objType:
            case FX2DType.Light:
                obj = FX2DLightObject()

                obj.coronaName      = self.parseLCString(values[9].strip('"'))
                obj.shadowName      = self.parseLCString(values[10].strip('"'))
                obj.distance        = float(values[11])
                obj.range           = float(values[12])
                obj.size            = float(values[13])
                obj.shadowSize      = float(values[14])
                obj.shadowIntensity = int(values[15])
                obj.lightType       = int(values[16])
                obj.roadReflection  = int(values[17])
                obj.flareType       = int(values[18])
                obj.flags           = int(values[19])

                if obj.flags & FX2DLightFlag.FogAlways:
                    obj.flags = clearBit(obj.flags, FX2DLightFlag.FogNormal)

                if self.ctx:
                    obj.coronaTexture = self.ctx.txd.particles.getTexture(obj.coronaName)
                    obj.shadowTexture = self.ctx.txd.particles.getTexture(obj.shadowName)
                else:
                    obj.coronaTexture = None
                    obj.shadowTexture = None

            case FX2DType.Particle:
                obj = FX2DParticleObject()

                obj.fxType    = int(values[9])
                obj.direction = toFloats(values[10:13])
                obj.scale     = float(values[13])

            case FX2DType.Attractor:
                obj = FX2DAttractorObject()

                obj.fxType      = int(values[9])
                obj.direction   = toFloats(values[10:13])
                obj.probability = clamp(int(values[13]), 0, 255)

            case FX2DType.PedAttractor:
                obj = FX2DPedAttractorObject()

                obj.fxType         = int(values[9])
                obj.queueDirection = toFloats(values[10:13])
                obj.useDirection   = toFloats(values[13:16])

            case FX2DType.SunGlare:
                obj = FX2DObject()  # no specific fields

            case _:
                raise Exception(f'Unexpected FX type: { objType }')

        obj.id       = FX2DObject.genId()
        obj.ownerId  = int(values[0])  # id of the model the effect linked to
        obj.type     = GameObjectType.FX2D
        obj.position = toFloats(values[1:4])
        obj.color    = toInts(values[4:8])

        assert self.objs.getById(obj.ownerId)

        self.objs.fx2d[obj.id] = obj

        # add this effect to it's owner
        # ownerId  = int(values[0])
        # ownerObj = self.objs.getById(ownerId)
        # assert ownerObj
        # ownerObj.effects.append(obj)



def _test_ ():
    for filePath in iterFiles(GAME_DIR, True, [ IDE_EXT ]):
        print(filePath)
        _ide = IDEReader.fromFile(filePath)
        print(' ')



__all__ = [
    'IDEReader',
    'SimpleObject',
    'initModelInfos',
    'GameObjects',
    'PedObject',
    'GameObjectType',

    '_test_',
]



if __name__ == '__main__':
    _test_()
