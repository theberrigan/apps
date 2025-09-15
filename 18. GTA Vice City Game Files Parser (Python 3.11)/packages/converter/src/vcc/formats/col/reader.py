from typing import Optional, Dict

# from vcc.formats.dff.reader import Sphere
from ...common import bfw
from ...common.types import *
from ...common.consts import *
from ...common.fns import splitSeps, isEmptyString, toFloats, toInts

from ..handling import VehicleHandlingData
from ..ped_stats.types import TPedStats, PedStats

from .consts import *
from .types import *

from bfw.utils import *
from bfw.types.enums import Enum
from bfw.reader import *



class LevelName (Enum):
    IGNORE   = -1  # beware, this is only used in CPhysical's m_nZoneLevel
    GENERIC  = 0
    BEACH    = 1
    MAINLAND = 2


# eSurfaceType
class SurfaceType (Enum):
    DEFAULT           = 0   # SURFACE_DEFAULT
    TARMAC            = 1   # SURFACE_TARMAC
    GRASS             = 2   # SURFACE_GRASS
    GRAVEL            = 3   # SURFACE_GRAVEL
    MUD_DRY           = 4   # SURFACE_MUD_DRY
    PAVEMENT          = 5   # SURFACE_PAVEMENT
    CAR               = 6   # SURFACE_CAR
    GLASS             = 7   # SURFACE_GLASS
    TRANSPARENT_CLOTH = 8   # SURFACE_TRANSPARENT_CLOTH
    GARAGE_DOOR       = 9   # SURFACE_GARAGE_DOOR
    CAR_PANEL         = 10  # SURFACE_CAR_PANEL
    THICK_METAL_PLATE = 11  # SURFACE_THICK_METAL_PLATE
    SCAFFOLD_POLE     = 12  # SURFACE_SCAFFOLD_POLE
    LAMP_POST         = 13  # SURFACE_LAMP_POST
    FIRE_HYDRANT      = 14  # SURFACE_FIRE_HYDRANT
    GIRDER            = 15  # SURFACE_GIRDER
    METAL_CHAIN_FENCE = 16  # SURFACE_METAL_CHAIN_FENCE
    PED               = 17  # SURFACE_PED
    SAND              = 18  # SURFACE_SAND
    WATER             = 19  # SURFACE_WATER
    WOOD_CRATES       = 20  # SURFACE_WOOD_CRATES
    WOOD_BENCH        = 21  # SURFACE_WOOD_BENCH
    WOOD_SOLID        = 22  # SURFACE_WOOD_SOLID
    RUBBER            = 23  # SURFACE_RUBBER
    PLASTIC           = 24  # SURFACE_PLASTIC
    HEDGE             = 25  # SURFACE_HEDGE
    STEEP_CLIFF       = 26  # SURFACE_STEEP_CLIFF
    CONTAINER         = 27  # SURFACE_CONTAINER
    NEWS_VENDOR       = 28  # SURFACE_NEWS_VENDOR
    WHEELBASE         = 29  # SURFACE_WHEELBASE
    CARDBOARDBOX      = 30  # SURFACE_CARDBOARDBOX
    TRANSPARENT_STONE = 31  # SURFACE_TRANSPARENT_STONE
    METAL_GATE        = 32  # SURFACE_METAL_GATE
    SAND_BEACH        = 33  # SURFACE_SAND_BEACH
    CONCRETE_BEACH    = 34  # SURFACE_CONCRETE_BEACH


class ColSphere (Sphere):
    def __init__ (self):
        super().__init__()

        self.surface : int = SurfaceType.DEFAULT  # uint8 surface
        self.piece   : int = 0                    # uint8 piece

    # noinspection PyMethodOverriding
    def set (self, radius : float, center : List[float], surface : int, piece : int):
        super().set(radius, center)

        self.surface = surface
        self.piece   = piece


class ColBox (Box):
    def __init__ (self):
        super().__init__()

        self.surface : int = SurfaceType.DEFAULT  # uint8 surface
        self.piece   : int = 0                    # uint8 piece

    # noinspection PyMethodOverriding
    def set (self, boxMin : List[float], boxMax : List[float], surface : int, piece : int):
        super().set(boxMin, boxMax)

        self.surface = surface
        self.piece   = piece


class ColTriangle:
    def __init__ (self):
        self.a       : int = 0                    # uint16 a
        self.b       : int = 0                    # uint16 b
        self.c       : int = 0                    # uint16 c
        self.surface : int = SurfaceType.DEFAULT  # uint8 surface

    # noinspection PyMethodOverriding
    def set (self, a : int, b : int, c : int, surface : int):
        self.a       = a
        self.b       = b
        self.c       = c
        self.surface = surface


class ColModel:
    def __init__ (self):
        self.boundingSphere       : Sphere                 = Sphere()  # CSphere boundingSphere
        self.boundingBox          : Box                    = Box()     # CBox boundingBox
        self.level                : int                    = 0         # uint8 level -- colstore slot but probably still named level
        self.ownsCollisionVolumes : bool                   = False     # bool ownsCollisionVolumes
        self.sphereCount          : int                    = 0         # int16 numSpheres
        self.spheres              : Opt[List[ColSphere]]   = None      # CColSphere *spheres
        self.boxCount             : int                    = 0         # int16 numBoxes
        self.boxes                : Opt[List[ColBox]]      = None      # CColBox *boxes
        self.vertexCount          : int                    = 0         # int16 ?
        self.vertices             : Opt[List[List[float]]] = None      # CompressedVector* -- regular vec3 actually
        self.triangleCount        : int                    = 0         # int16 numTriangles
        self.triangles            : Opt[List[ColTriangle]] = None      # CColTriangle*
        # self.lineCount            : int                  = 0         # int8 numLines
        # self.lines                : Opt[List[Any]]       = None      # CColLine *lines

TCollisions = Dict[str, ColModel]


class CollisionReader:
    @classmethod
    def fromFile (cls, filePath : str) -> TCollisions:
        if not isFile(filePath):
            raise OSError(f'File does not exist: { filePath }')

        rawData = readBin(filePath)
        reader  = MemReader(rawData, filePath)

        return cls().read(reader)

    # CFileLoader::LoadCollisionFile
    # peds.col is corrupted and not used (?)
    def read (self, f : Reader) -> TCollisions:
        result = {}

        while f.remaining():
            signature = f.read(4)

            if signature != COL_SIGNATURE:
                # if remaining space < CD sector size
                if f.remaining() < 2048:
                    break

                raise Exception(f'Invalid signature: { signature }')

            colSize   = f.u32()
            colEnd    = f.tell() + colSize
            modelName = f.string(22).strip().lower()
            _modelId  = f.u16()  # don't use, identify by name instead

            # ----------------------------------------------

            model = ColModel()

            model.boundingSphere.radius = f.f32()
            model.boundingSphere.center = f.vec3()
            model.boundingBox.min       = f.vec3()
            model.boundingBox.max       = f.vec3()
            model.sphereCount           = f.u16()

            f.skip(2)

            # ----------------------------------------------

            model.spheres = []

            if model.sphereCount > 0:
                for _ in range(model.sphereCount):
                    sphere = ColSphere()

                    sphere.radius  = f.f32()
                    sphere.center  = f.vec3()
                    sphere.surface = f.u8()
                    sphere.piece   = f.u8()

                    f.skip(2)

                    model.spheres.append(sphere)

            # ----------------------------------------------

            lineCount = f.i16()

            f.skip(2)

            assert lineCount <= 0, lineCount

            if lineCount > 0:
                f.skip(24 * lineCount)

            # ----------------------------------------------

            model.boxCount = f.i16()

            f.skip(2)

            model.boxes = []

            if model.boxCount > 0:
                for _ in range(model.boxCount):
                    box = ColBox()

                    box.min     = f.vec3()
                    box.max     = f.vec3()
                    box.surface = f.u8()
                    box.piece   = f.u8()

                    f.skip(2)

                    model.boxes.append(box)

            # ----------------------------------------------

            model.vertexCount = f.i16()

            f.skip(2)

            model.vertices = []

            if model.vertexCount > 0:
                for _ in range(model.vertexCount):
                    model.vertices.append(f.vec3())

            # ----------------------------------------------

            model.triangleCount = f.i16()

            f.skip(2)

            model.triangles = []

            if model.triangleCount > 0:
                for _ in range(model.triangleCount):
                    triangle = ColTriangle()

                    triangle.a       = f.i32()
                    triangle.b       = f.i32()
                    triangle.c       = f.i32()
                    triangle.surface = f.u8()

                    f.skip(3)

                    model.triangles.append(triangle)

            assert f.tell() == colEnd, (f.tell(), colEnd)

            f.seek(colEnd)

            result[modelName] = model

        return result


class TempCollisions:
    ModelPed1         : ColModel       = ColModel()
    ModelPed2         : ColModel       = ColModel()
    ModelBBox         : ColModel       = ColModel()
    ModelBumper1      : ColModel       = ColModel()
    ModelWheel1       : ColModel       = ColModel()
    ModelPanel1       : ColModel       = ColModel()
    ModelBodyPart2    : ColModel       = ColModel()
    ModelBodyPart1    : ColModel       = ColModel()
    ModelCutObj       : List[ColModel] = [ ColModel() for _ in range(5) ]
    ModelPedGroundHit : ColModel       = ColModel()
    ModelBoot1        : ColModel       = ColModel()
    ModelDoor1        : ColModel       = ColModel()
    ModelBonnet1      : ColModel       = ColModel()
    ModelWeapon       : ColModel       = ColModel()

    # CTempColModels::Initialise()
    @classmethod
    def generate (cls) -> Type[Self]:
        pedSpheres       = [ ColSphere() for _ in range(3) ]
        ped2Spheres      = [ ColSphere() for _ in range(3) ]
        pedGSpheres      = [ ColSphere() for _ in range(4) ]
        doorSpheres      = [ ColSphere() for _ in range(3) ]
        bumperSpheres    = [ ColSphere() for _ in range(4) ]
        panelSpheres     = [ ColSphere() for _ in range(4) ]
        bonnetSpheres    = [ ColSphere() for _ in range(4) ]
        bootSpheres      = [ ColSphere() for _ in range(4) ]
        wheelSpheres     = [ ColSphere() for _ in range(2) ]
        bodyPartSpheres1 = [ ColSphere() for _ in range(2) ]
        bodyPartSpheres2 = [ ColSphere() for _ in range(2) ]

        # ---------------------------------------------------------------

        cls.ModelBBox.boundingSphere.set(2, [ 0, 0, 0 ])
        cls.ModelBBox.boundingBox.set([ -2, -2, -2 ], [ 2, 2, 2 ])
        cls.ModelBBox.level = LevelName.GENERIC

        for model in cls.ModelCutObj:
            model.boundingSphere.set(2, [ 0, 0, 0 ])
            model.boundingBox.set([ -2, -2, -2 ], [ 2, 2, 2 ])
            model.level = LevelName.GENERIC

        # Ped Spheres
        # ---------------------------------------------------------------

        for sphere in pedSpheres:
            sphere.radius = 0.35

        pedSpheres[0].center = [ 0, 0, -0.25 ]
        pedSpheres[1].center = [ 0, 0,  0.15 ]
        pedSpheres[2].center = [ 0, 0,  0.55 ]

        for sphere in pedSpheres:
            sphere.surface = SurfaceType.PED
            sphere.piece   = 0

        cls.ModelPed1.boundingSphere.set(1.25, [ 0, 0, 0 ])
        cls.ModelPed1.boundingBox.set([ -0.35, -0.35, -1 ], [ 0.35, 0.35, 0.9 ])

        cls.setModelSpheres(cls.ModelPed1, pedSpheres)

        # Ped 2 Spheres
        # ---------------------------------------------------------------

        ped2Spheres[0].radius = 0.3
        ped2Spheres[0].center = [ 0,  0.35, -0.9 ]

        ped2Spheres[1].radius = 0.4
        ped2Spheres[1].center = [ 0,  0, -0.9 ]

        ped2Spheres[2].radius = 0.3
        ped2Spheres[2].center = [ 0, -0.35, -0.9 ]

        for sphere in ped2Spheres:
            sphere.surface = SurfaceType.PED
            sphere.piece   = 0

        cls.ModelPed2.boundingSphere.set(2, [ 0, 0, 0 ])
        cls.ModelPed2.boundingBox.set([ -0.7, -0.7, -1.2 ], [ 0.7, 0.7, 0 ])

        cls.setModelSpheres(cls.ModelPed2, ped2Spheres)

        # Ped ground collision
        # ---------------------------------------------------------------

        pedGSpheres[0].radius  = 0.35
        pedGSpheres[0].center  = [ 0, -0.4, -0.9 ]
        pedGSpheres[0].surface = SurfaceType.PED
        pedGSpheres[0].piece   = 4

        pedGSpheres[1].radius  = 0.35
        pedGSpheres[1].center  = [ 0, -0.1, -0.9 ]
        pedGSpheres[1].surface = SurfaceType.PED
        pedGSpheres[1].piece   = 1

        pedGSpheres[2].radius  = 0.35
        pedGSpheres[2].center  = [ 0, 0.25, -0.9 ]
        pedGSpheres[2].surface = SurfaceType.PED
        pedGSpheres[2].piece   = 0

        pedGSpheres[3].radius  = 0.3
        pedGSpheres[3].center  = [ 0, 0.65, -0.9 ]
        pedGSpheres[3].surface = SurfaceType.PED
        pedGSpheres[3].piece   = 6

        cls.ModelPedGroundHit.boundingSphere.set(2, [ 0, 0, 0 ])
        cls.ModelPedGroundHit.boundingBox.set([ -0.4, -1.0, -1.25 ], [ 0.4, 1.2, -0.5 ])

        cls.setModelSpheres(cls.ModelPedGroundHit, pedGSpheres)

        # Door Spheres
        # ---------------------------------------------------------------

        doorSpheres[0].radius = 0.15
        doorSpheres[0].center = [ 0, -0.25, -0.35 ]

        doorSpheres[1].radius = 0.15
        doorSpheres[1].center = [ 0, -0.95, -0.35 ]

        doorSpheres[2].radius = 0.25
        doorSpheres[2].center = [ 0, -0.6, 0.25 ]

        for sphere in doorSpheres:
            sphere.surface = SurfaceType.CAR_PANEL
            sphere.piece   = 0

        cls.ModelDoor1.boundingSphere.set(1.5, [ 0, -0.6, 0 ])
        cls.ModelDoor1.boundingBox.set([ -0.3, 0, -0.6 ], [ 0.3, -1.2, 0.6 ])

        cls.setModelSpheres(cls.ModelDoor1, doorSpheres)

        # Bumper Spheres
        # ---------------------------------------------------------------

        for sphere in bumperSpheres:
            sphere.radius = 0.15

        bumperSpheres[0].center = [  0.85, -0.05, 0.0 ]
        bumperSpheres[1].center = [  0.4,   0.05, 0.0 ]
        bumperSpheres[2].center = [ -0.4,   0.05, 0.0 ]
        bumperSpheres[3].center = [ -0.85, -0.05, 0.0 ]

        for sphere in bumperSpheres:
            sphere.surface = SurfaceType.CAR_PANEL
            sphere.piece   = 0

        cls.ModelBumper1.boundingSphere.set(2.2, [ 0, -0.6, 0 ])
        cls.ModelBumper1.boundingBox.set([ -1.2, -0.3, -0.2 ], [ 1.2, 0.3, 0.2 ])

        cls.setModelSpheres(cls.ModelBumper1, bumperSpheres)

        # Panel Spheres
        # ---------------------------------------------------------------

        for sphere in panelSpheres:
            sphere.radius = 0.15

        panelSpheres[0].center = [  0.15,  0.45, 0 ]
        panelSpheres[1].center = [  0.15, -0.45, 0 ]
        panelSpheres[2].center = [ -0.15, -0.45, 0 ]
        panelSpheres[3].center = [ -0.15,  0.45, 0 ]

        for sphere in panelSpheres:
            sphere.surface = SurfaceType.CAR_PANEL
            sphere.piece   = 0

        cls.ModelPanel1.boundingSphere.set(1.4, [ 0, 0, 0 ])
        cls.ModelPanel1.boundingBox.set([ -0.3, -0.6, -0.15 ], [ 0.3, 0.6, 0.15 ])

        cls.setModelSpheres(cls.ModelPanel1, panelSpheres)

        # Bonnet Spheres
        # ---------------------------------------------------------------

        for sphere in bonnetSpheres:
            sphere.radius = 0.2

        bonnetSpheres[0].center = [ -0.4, 0.1, 0 ]
        bonnetSpheres[1].center = [ -0.4, 0.9, 0 ]
        bonnetSpheres[2].center = [  0.4, 0.1, 0 ]
        bonnetSpheres[3].center = [  0.4, 0.9, 0 ]

        for sphere in bonnetSpheres:
            sphere.surface = SurfaceType.CAR_PANEL
            sphere.piece   = 0

        cls.ModelBonnet1.boundingSphere.set(1.7, [ 0, 0.5, 0 ])
        cls.ModelBonnet1.boundingBox.set([ -0.7, -0.2, -0.3 ], [ 0.7, 1.2, 0.3 ])

        cls.setModelSpheres(cls.ModelBonnet1, bonnetSpheres)

        # Boot Spheres
        # ---------------------------------------------------------------

        for sphere in bootSpheres:
            sphere.radius = 0.2

        bootSpheres[0].center = [ -0.4, -0.1, 0 ]
        bootSpheres[1].center = [ -0.4, -0.6, 0 ]
        bootSpheres[2].center = [  0.4, -0.1, 0 ]
        bootSpheres[3].center = [  0.4, -0.6, 0 ]

        for sphere in bootSpheres:
            sphere.surface = SurfaceType.CAR_PANEL
            sphere.piece   = 0

        cls.ModelBoot1.boundingSphere.set(1.4, [ 0, -0.4, 0 ])
        cls.ModelBoot1.boundingBox.set([ -0.7, -0.9, -0.3 ], [ 0.7, 0.2, 0.3 ])

        cls.setModelSpheres(cls.ModelBoot1, bootSpheres)

        # Wheel Spheres
        # ---------------------------------------------------------------

        wheelSpheres[0].radius = 0.35
        wheelSpheres[0].center = [ -0.3, 0, 0 ]

        wheelSpheres[1].radius = 0.35
        wheelSpheres[1].center = [ 0.3, 0, 0 ]

        for sphere in wheelSpheres:
            sphere.surface = SurfaceType.WHEELBASE
            sphere.piece   = 0

        cls.ModelWheel1.boundingSphere.set(1.4, [ 0, 0, 0 ])
        cls.ModelWheel1.boundingBox.set([ -0.7, -0.4, -0.4 ], [ 0.7, 0.4, 0.4 ])

        cls.setModelSpheres(cls.ModelWheel1, wheelSpheres)

        # Body Part Spheres 1
        # ---------------------------------------------------------------

        bodyPartSpheres1[0].radius = 0.2
        bodyPartSpheres1[0].center = [ 0, 0, 0 ]

        bodyPartSpheres1[1].radius = 0.2
        bodyPartSpheres1[1].center = [ 0.8, 0, 0 ]

        for sphere in bodyPartSpheres1:
            sphere.surface = SurfaceType.PED
            sphere.piece   = 0

        cls.ModelBodyPart1.boundingSphere.set(0.7, [ 0.4, 0, 0 ])
        cls.ModelBodyPart1.boundingBox.set([ -0.3, -0.3, -0.3 ], [ 1.1, 0.3, 0.3 ])

        cls.setModelSpheres(cls.ModelBodyPart1, bodyPartSpheres1)

        # Body Part Spheres 2
        # ---------------------------------------------------------------

        bodyPartSpheres2[0].radius = 0.15
        bodyPartSpheres2[0].center = [ 0, 0, 0 ]

        bodyPartSpheres2[1].radius = 0.15
        bodyPartSpheres2[1].center = [ 0.5, 0, 0 ]

        for sphere in bodyPartSpheres2:
            sphere.surface = SurfaceType.PED
            sphere.piece   = 0

        cls.ModelBodyPart2.boundingSphere.set(0.5, [ 0.25, 0, 0 ])
        cls.ModelBodyPart2.boundingBox.set([ -0.2, -0.2, -0.2 ], [ 0.7, 0.2, 0.2 ])

        cls.setModelSpheres(cls.ModelBodyPart2, bodyPartSpheres2)

        # TODO: is this correct fix for sphere?
        # cls.ModelWeapon.boundingSphere.radius = 0.25
        cls.ModelWeapon.boundingSphere.set(0.25, [ 0, 0, 0 ])
        cls.ModelWeapon.boundingBox.set([ -0.25, -0.25, -0.25 ], [ 0.25, 0.25, 0.25 ])

        return cls

    @classmethod
    def setModelSpheres (cls, colModel : ColModel, spheres : List[ColSphere]):
        colModel.sphereCount          = len(spheres)
        colModel.spheres              = spheres
        colModel.level                = LevelName.GENERIC
        colModel.ownsCollisionVolumes = False


def _test_ ():
    # col = CollisionReader.fromFile(r'G:\Steam\steamapps\common\Grand Theft Auto Vice City\.converter\original\models\coll\vehicles.col')
    # return
    for filePath in iterFiles(GAME_DIR, True, [ COL_EXT ]):
        if filePath.lower().endswith('peds.col'):
            continue

        print(filePath)

        try:
            _col = CollisionReader.fromFile(filePath)
        except Exception as e:
            printE('Failed:', e)

        print(' ')



__all__ = [
    'CollisionReader',
    'ColModel',
    'TempCollisions',

    '_test_',
]



if __name__ == '__main__':
    _test_()
