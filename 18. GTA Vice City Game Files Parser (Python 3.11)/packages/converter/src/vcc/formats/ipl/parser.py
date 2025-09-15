from math import acos

from ...common import bfw
from ...common.types import *
from ...common.consts import *
from ...common.game_data import *
from ...common.fns import splitSeps, isEmptyString, toFloats, toInts
from ...maths import radToDeg

from ..handling import VehicleHandlingData
from ..ped_stats.types import TPedStats, PedStats

from .consts import *
from .types import *

from bfw.utils import *
from bfw.types.enums import Enum
from bfw.native.limits import MAX_U16



class IPLSectionType (Enum):
    No        : int = 0  # NONE
    Instance  : int = 1  # INST
    Zone      : int = 2  # ZONE
    Cull      : int = 3  # CULL
    Occlusion : int = 4  # OCCL
    Pick      : int = 5  # PICK
    Path      : int = 6  # PATH


# eZoneType
class ZoneType (Enum):
    Default : int = 0  # ZONE_DEFAULT
    Nav     : int = 1  # ZONE_NAVIG
    Info    : int = 2  # ZONE_INFO
    Map     : int = 3  # ZONE_MAPZONE


# eLevelName
class LevelName (Enum):
    Ignore   : int = -1  # LEVEL_IGNORE
    Generic  : int = 0   # LEVEL_GENERIC
    Beach    : int = 1   # LEVEL_BEACH
    Mainland : int = 2   # LEVEL_MAINLAND


class Zone:
    def __init__ (self):
        self.type          : TInt  = None  # eZoneType type (see ZoneType)
        self.name          : TStr  = None  # char name[8]
        self.min           : TVec3 = None  # float minx, miny, minz
        self.max           : TVec3 = None  # float maxx, maxy, maxz
        self.level         : TInt  = None  # eLevelName level (see LevelName)
        self.zoneInfoDay   : TInt  = None  # int16 zoneinfoDay
        self.zoneInfoNight : TInt  = None  # int16 zoneinfoNight


# TODO: see CTheZones::Init()
class Zones:
    InfoZoneCount : int = 1  # game/src/core/Zones.cpp:85

    @classmethod
    def advanceInfoZoneCount (cls) -> int:
        count = cls.InfoZoneCount

        cls.InfoZoneCount += 1

        return count

    def __init__ (self):
        self.mapZones  : List[Zone] = []
        self.navZones  : List[Zone] = []
        self.infoZones : List[Zone] = []

    def addZone (self, zone : Zone) -> Zone:
        match zone.type:
            case ZoneType.Default | ZoneType.Nav:
                self.navZones.append(zone)
            case ZoneType.Info:
                self.infoZones.append(zone)
            case ZoneType.Map:
                self.mapZones.append(zone)
            case _:
                raise Exception(f'Unknown zone type: { zone.type }')

        return zone


class Occluder:
    def __init__ (self):
        # TODO: all of them are ints in original
        self.pos    : TVec3  = None  # int16 x, y, z
        self.width  : TFloat = None  # int16 width
        self.length : TFloat = None  # int16 length
        self.height : TFloat = None  # int16 height
        self.angle  : TFloat = None  # uint16 angle


class Occlusion:
    def __init__ (self):
        self.occluders : List[Occluder] = []

    def addOccluder (self, occluder : Occluder) -> Occluder:
        self.occluders.append(occluder)

        return occluder


class CullZone:
    def __init__ (self):
        self.min         : TVec3 = None  # int16 minx, miny, minz
        self.max         : TVec3 = None  # int16 maxx, maxy, maxz
        self.attributes  : TInt  = None  # int16 flag
        self.wantedLevel : TInt  = None  # int16 wantedLevel


class CullZones:
    def __init__ (self):
        self.zones : List[CullZone] = []

    def addZone (self, zone : CullZone) -> CullZone:
        self.zones.append(zone)

        return zone


class PathNodeType (Enum):
    External = 1  # NodeTypeExtern
    Internal = 2  # NodeTypeIntern


class PathData:
    def __init__ (self):
        self.type           : TInt   = None  # int8 type
        self.next           : TInt   = None  # int8 next
        self.isCrossing     : TBool  = None  # uint8 crossing : 1
        self.pos            : TVec3  = None  # float x, y, z
        self.width          : TFloat = None  # uint8 width
        self.leftLaneCount  : TInt   = None  # int8 numLeftLanes
        self.rightLaneCount : TInt   = None  # int8 numRightLanes
        self.speedLimit     : TInt   = None  # int8 speedLimit
        self.spawnRate      : TFloat = None  # uint8 spawnRate : 4
        self.isDisabled     : TBool  = None  # uint8 disabled : 1
        self.roadBlock      : TBool  = None  # uint8 roadBlock : 1
        self.betweenLevels  : TBool  = None  # uint8 betweenLevels : 1
        self.isWaterPath    : TBool  = None  # uint8 waterPath : 1
        self.smallBoatsOnly : TBool  = None  # uint8 onlySmallBoats : 1

    # CPathInfoForObject::SwapConnectionsToBeRightWayRound
    def swapConnections (self, paths : List['PathData']):
        startIndex = paths.index(self)

        for i in range(startIndex, startIndex + 12):
            if paths[i].type == PathNodeType.External and paths[i].next < 0:
                for j in range(startIndex, startIndex + 12):
                    if paths[j].type == PathNodeType.Internal and paths[j].next == (i - startIndex):
                        paths[i].next = j - startIndex
                        paths[j].next = -1
                        paths[i].isCrossing, paths[j].isCrossing = paths[j].isCrossing, paths[i].isCrossing


class PathFind:
    def __init__ (self):
        self.pedPaths : List[PathData] = []
        self.carPaths : List[PathData] = []

    # StoreDetachedNodeInfoPed
    def addPedPath (self, pathInfo : PathData) -> PathData:
        self.pedPaths.append(pathInfo)

        return pathInfo

    # CPathFind::StoreDetachedNodeInfoCar
    def addCarPath (self, pathInfo : PathData) -> PathData:
        self.carPaths.append(pathInfo)

        return pathInfo

    def getPathsByType (self, pathType : int):
        if pathType == 0:
            return self.pedPaths

        if pathType in [ 1, 2 ]:
            return self.carPaths

        raise Exception(f'Unexpected path type: { pathType }')


class ObjectInstance:
    def __init__ (self):
        self.objId : TInt   = None  # id to ctx.modelInfos (for IsSimpleObject only)
        self.name  : TStr   = None
        self.area  : TFloat = None
        self.trans : TVec3  = None
        self.scale : TVec3  = None
        self.axis  : TVec3  = None
        self.angle : TFloat = None


class ObjectInstances:
    def __init__ (self):
        self.objects : List[ObjectInstance] = []

    def addObj (self, obj : ObjectInstance) -> ObjectInstance:
        self.objects.append(obj)

        return obj


class Placements:
    def __init__ (self):
        self.zones     : Zones           = Zones()
        self.occlusion : Occlusion       = Occlusion()
        self.cullZones : CullZones       = CullZones()
        self.paths     : PathFind        = PathFind()
        self.objects   : ObjectInstances = ObjectInstances()


# https://gta.fandom.com/wiki/Item_Placement
# https://gtamods.com/wiki/Item_Placement
class IPLReader:
    @classmethod
    def fromFile (cls, filePath : str, ctx : Opt[Any] = None) -> Placements:
        if not isFile(filePath):
            raise OSError(f'File does not exist: { filePath }')

        text = readText(filePath, encoding='utf-8')

        return cls(ctx).read(text)

    def __init__ (self, ctx : Opt[Any] = None):
        self.ctx : Opt[Any] = ctx

    # CFileLoader::LoadScene
    def read (self, text : str) -> Placements:
        if self.ctx:
            if self.ctx.placements is None:
                self.ctx.placements = Placements()

            placements = self.ctx.placements
        else:
            placements = Placements()

        lines = text.split('\n')

        sectionType    = None
        pathIndex      = -1
        pathType       = None
        firstGroupPath = None  # first item in a group of 12 consecutive paths

        for line in lines:
            line = line.strip()

            if isEmptyString(line) or line[0] in '#\x00':
                continue

            if not sectionType:
                match line:
                    case 'inst':
                        sectionType = IPLSectionType.Instance
                    case 'zone':
                        sectionType = IPLSectionType.Zone
                    case 'cull':
                        sectionType = IPLSectionType.Cull
                    case 'occl':
                        sectionType = IPLSectionType.Occlusion
                    case 'path':
                        sectionType = IPLSectionType.Path
                    case 'pick':
                        sectionType = IPLSectionType.Pick
                    case _:
                        raise Exception(f'Expected section, but unexpected token given: { line }')

                continue

            if line == 'end':
                sectionType = None
                continue

            values = splitSeps(line)

            match sectionType:
                case IPLSectionType.Instance:
                    placements.objects.addObj(self.readObjectInstance(values))

                case IPLSectionType.Zone:
                    placements.zones.addZone(self.readZone(values))

                case IPLSectionType.Cull:
                    placements.cullZones.addZone(self.readCullZone(values))

                case IPLSectionType.Occlusion:
                    placements.occlusion.addOccluder(self.readOccluder(values))

                case IPLSectionType.Path:
                    if pathIndex == -1:
                        pathIndex = 0
                        pathType  = self.readPathHeader(values)
                    else:
                        match pathType:
                            case 0:
                                path = placements.paths.addPedPath(self.readPedPathNode(values))
                            case 1:
                                path = placements.paths.addCarPath(self.readCarPathNode(values, False))
                            case 2:
                                path = placements.paths.addCarPath(self.readCarPathNode(values, True))
                            case _:
                                raise Exception(f'Unexpected path type: { pathType }')

                        pathIndex += 1

                        if pathIndex == 1:
                            firstGroupPath = path

                        if pathIndex == 12:
                            pathIndex = -1

                            firstGroupPath.swapConnections(placements.paths.getPathsByType(pathType))

                case IPLSectionType.Pick:
                    raise Exception('"pick" section of .ipl file is not used in VC')

        return placements

    def readObjectInstance (self, values : List[str]) -> ObjectInstance:
        assert len(values) == 13

        obj = ObjectInstance()

        obj.objId = int(values[0])
        obj.name  = values[1].lower()
        obj.area  = float(values[2])
        obj.trans = toFloats(values[3:6])
        obj.scale = toFloats(values[6:9])
        obj.axis  = toFloats(values[9:12])
        obj.angle = -radToDeg(2 * acos(float(values[12])))

        # TODO: a lot of work game/src/core/FileLoader.cpp:1201

        return obj

    def readZone (self, values : List[str]) -> Zone:
        zone = Zone()

        zone.name  = values[0].upper()
        zone.type  = int(values[1])  # ZoneType
        zone.min   = toFloats(values[2:5])
        zone.max   = toFloats(values[5:8])
        zone.level = int(values[8])  # LevelName

        if zone.type == ZoneType.Info:
            zone.zoneInfoDay   = Zones.advanceInfoZoneCount()
            zone.zoneInfoNight = Zones.advanceInfoZoneCount()

        return zone

    def readCullZone (self, values : List[str]) -> CullZone:
        zone = CullZone()

        _pos             = toFloats(values[0:3])  # ignored
        zone.min         = toFloats(values[3:6])
        zone.max         = toFloats(values[6:9])
        zone.attributes  = int(values[9])
        zone.wantedLevel = int(values[10])

        assert zone.wantedLevel == 0

        return zone

    def readOccluder (self, values : List[str]) -> Occluder:
        occluder = Occluder()

        occluder.pos    = toFloats(values[0:3])
        occluder.width  = float(values[3])
        occluder.length = float(values[4])
        occluder.height = float(values[5])
        occluder.angle  = float(values[6])

        occluder.pos[2] += occluder.height / 2

        while occluder.angle < 0:
            occluder.angle += 360

        while occluder.angle > 360:
            occluder.angle -= 360

        occluder.angle = occluder.angle / 360 * MAX_U16

        return occluder

    def readPathHeader (self, values : List[str]):
        assert len(values) == 2

        pathType = int(values[0])
        _pathId  = int(values[1])  # used only in CFileLoader::ReloadPaths()

        return pathType

    # TODO: merge with readCarPathNode?
    def readPedPathNode (self, values : List[str]) -> PathData:
        assert len(values) == 12

        pathInfo = PathData()

        pathInfo.type           = int(values[0])
        pathInfo.next           = int(values[1])
        pathInfo.isCrossing     = bool(int(values[2]))
        pathInfo.pos            = [ n / 16 for n in toFloats(values[3:6]) ]
        pathInfo.width          = min(float(values[6]), 31) * 8
        _leftLaneCount          = int(values[7])
        pathInfo.leftLaneCount  = 0
        _rightLaneCount         = int(values[8])
        pathInfo.rightLaneCount = 0
        _speedLimit             = int(values[9])
        pathInfo.speedLimit     = 0
        flags                   = int(values[10])
        pathInfo.spawnRate      = min(float(values[11]) * 15, 15)
        pathInfo.isDisabled     = bool(flags & 1)
        _roadBlock              = bool(flags & 2)
        pathInfo.roadBlock      = False
        pathInfo.betweenLevels  = bool(flags & 4)
        pathInfo.isWaterPath    = False
        pathInfo.smallBoatsOnly = False

        return pathInfo

    def readCarPathNode (self, values : List[str], isWaterPath : bool) -> PathData:
        assert len(values) == 12

        pathInfo = PathData()

        pathInfo.type           = int(values[0])
        pathInfo.next           = int(values[1])
        _isCrossing             = bool(int(values[2]))
        pathInfo.isCrossing     = False
        pathInfo.pos            = [ n / 16 for n in toFloats(values[3:6]) ]
        pathInfo.width          = min(float(values[6]), 15) * 8
        pathInfo.leftLaneCount  = int(values[7])
        pathInfo.rightLaneCount = int(values[8])
        pathInfo.speedLimit     = int(values[9])
        flags                   = int(values[10])
        pathInfo.spawnRate      = min(float(values[11]) * 15, 15)
        pathInfo.isDisabled     = bool(flags & 1)
        pathInfo.roadBlock      = bool(flags & 2)
        pathInfo.betweenLevels  = bool(flags & 4)
        pathInfo.isWaterPath    = isWaterPath
        pathInfo.smallBoatsOnly = False

        return pathInfo



def _test_ ():
    for filePath in iterFiles(GAME_DIR, True, [ IPL_EXT, ZON_EXT ]):
        print(filePath)
        _ide = IPLReader.fromFile(filePath)
        print(' ')



__all__ = [
    'IPLReader',
    'Placements',

    '_test_',
]



if __name__ == '__main__':
    _test_()
