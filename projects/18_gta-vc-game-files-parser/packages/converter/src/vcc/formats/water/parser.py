from ...common import bfw
from ...common.types import *
from ...common.consts import *

from ..txd import Texture

from .consts import *
from .types import *

from bfw.utils import *
from bfw.reader import *



MAX_LARGE_SECTORS = 64
MAX_SMALL_SECTORS = 128



class Rect:
    def __init__ (self, left : TFloat = None, bottom : TFloat = None, right : TFloat = None, top : TFloat = None):
        self.left   : TFloat = left    # float left   -- x min
        self.bottom : TFloat = bottom  # float bottom -- y max
        self.right  : TFloat = right   # float right  -- x max
        self.top    : TFloat = top     # float top    -- y min


class WaterParams:
    def __init__ (self):
        self.levelCount    : Opt[int]               = None  # int32 CWaterLevel::ms_nNoOfWaterLevels
        self.z             : Opt[List[float]]       = None  # float CWaterLevel::ms_aWaterZs[48]
        self.rects         : Opt[List[Rect]]        = None  # CRect CWaterLevel::ms_aWaterRects[48]
        self.blockList     : Opt[List[List[float]]] = None  # int8 CWaterLevel::aWaterBlockList[MAX_LARGE_SECTORS][MAX_LARGE_SECTORS]
        self.fineBlockList : Opt[List[List[float]]] = None  # int8 CWaterLevel::aWaterFineBlockList[MAX_SMALL_SECTORS][MAX_SMALL_SECTORS]


class Water:
    def __init__ (self):
        self.params   : WaterParams        = WaterParams()
        self.textures : Dict[str, Texture] = {}


class WaterReader:
    @classmethod
    def fromFile (cls, filePath : str, ctx : Opt[Any] = None) -> Water:
        if not isFile(filePath):
            raise OSError(f'File does not exist: { filePath }')

        rawData = readBin(filePath)
        reader  = MemReader(rawData, filePath)

        return cls().read(reader, ctx)

    def read (self, f : Reader, ctx : Opt[Any] = None) -> Water:
        water = Water()

        if ctx:
            ctx.water = water

        water.levelCount = f.i32()
        water.z          = f.f32(48)
        water.rects      = [ Rect(*f.vec4()) for _ in range(48) ]  # TODO: are l/b/r/t correct?

        water.blockList = [
            [ f.i8() for _j in range(MAX_LARGE_SECTORS) ]
            for _i in range(MAX_LARGE_SECTORS)
        ]

        water.fineBlockList = [
            [ f.i8() for _j in range(MAX_SMALL_SECTORS) ]
            for _i in range(MAX_SMALL_SECTORS)
        ]

        # ----------------------------------

        if ctx:
            water.textures = {
                'water':        ctx.txd.particles.getTexture('waterclear256'),
                'waterEnv':     ctx.txd.particles.getTexture('waterreflection2'),
                'waterEnvBase': ctx.txd.particles.getTexture('sandywater'),
                'waterWake':    ctx.txd.particles.getTexture('waterwake'),
            }

            assert all(water.textures.values())

        # TODO: create water meshes here? CWaterLevel::CreateWavyAtomic()

        return water



def _test_ ():
    WaterReader.fromFile(joinPath(GAME_DIR, 'data/waterpro.dat'))



__all__ = [
    'WaterReader',
    'Water',

    '_test_',
]



if __name__ == '__main__':
    _test_()
