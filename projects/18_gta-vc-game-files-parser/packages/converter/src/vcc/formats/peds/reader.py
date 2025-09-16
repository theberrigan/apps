from ...common import bfw
from ...common.types import *
from ...common.consts import *
from ...common.fns import splitSeps

from .consts import *
from .types import *

from bfw.utils import *
from bfw.types.enums import Enum



# DO NOT RENAME ITEMS!
class PedFlag (Enum):
    PLAYER1    = 1 << 0   # PED_FLAG_PLAYER1
    PLAYER2    = 1 << 1   # PED_FLAG_PLAYER2
    PLAYER3    = 1 << 2   # PED_FLAG_PLAYER3
    PLAYER4    = 1 << 3   # PED_FLAG_PLAYER4
    CIVMALE    = 1 << 4   # PED_FLAG_CIVMALE
    CIVFEMALE  = 1 << 5   # PED_FLAG_CIVFEMALE
    COP        = 1 << 6   # PED_FLAG_COP
    GANG1      = 1 << 7   # PED_FLAG_GANG1
    GANG2      = 1 << 8   # PED_FLAG_GANG2
    GANG3      = 1 << 9   # PED_FLAG_GANG3
    GANG4      = 1 << 10  # PED_FLAG_GANG4
    GANG5      = 1 << 11  # PED_FLAG_GANG5
    GANG6      = 1 << 12  # PED_FLAG_GANG6
    GANG7      = 1 << 13  # PED_FLAG_GANG7
    GANG8      = 1 << 14  # PED_FLAG_GANG8
    GANG9      = 1 << 15  # PED_FLAG_GANG9
    EMERGENCY  = 1 << 16  # PED_FLAG_EMERGENCY
    PROSTITUTE = 1 << 17  # PED_FLAG_PROSTITUTE
    CRIMINAL   = 1 << 18  # PED_FLAG_CRIMINAL
    SPECIAL    = 1 << 19  # PED_FLAG_SPECIAL
    GUN        = 1 << 20  # PED_FLAG_GUN
    COP_CAR    = 1 << 21  # PED_FLAG_COP_CAR
    FAST_CAR   = 1 << 22  # PED_FLAG_FAST_CAR
    EXPLOSION  = 1 << 23  # PED_FLAG_EXPLOSION
    FIREMAN    = 1 << 24  # PED_FLAG_FIREMAN
    DEADPEDS   = 1 << 25  # PED_FLAG_DEADPEDS


# ePedType
# DO NOT RENAME ITEMS!
class PedType (Enum):
    PLAYER1    = 0   # PEDTYPE_PLAYER1
    PLAYER2    = 1   # PEDTYPE_PLAYER2
    PLAYER3    = 2   # PEDTYPE_PLAYER3
    PLAYER4    = 3   # PEDTYPE_PLAYER4
    CIVMALE    = 4   # PEDTYPE_CIVMALE
    CIVFEMALE  = 5   # PEDTYPE_CIVFEMALE
    COP        = 6   # PEDTYPE_COP
    GANG1      = 7   # PEDTYPE_GANG1
    GANG2      = 8   # PEDTYPE_GANG2
    GANG3      = 9   # PEDTYPE_GANG3
    GANG4      = 10  # PEDTYPE_GANG4
    GANG5      = 11  # PEDTYPE_GANG5 -- Security - hardcoded
    GANG6      = 12  # PEDTYPE_GANG6
    GANG7      = 13  # PEDTYPE_GANG7 -- Vercetti gang - hardcoded
    GANG8      = 14  # PEDTYPE_GANG8
    GANG9      = 15  # PEDTYPE_GANG9
    EMERGENCY  = 16  # PEDTYPE_EMERGENCY
    FIREMAN    = 17  # PEDTYPE_FIREMAN
    CRIMINAL   = 18  # PEDTYPE_CRIMINAL
    UNUSED1    = 19  # PEDTYPE_UNUSED1
    PROSTITUTE = 20  # PEDTYPE_PROSTITUTE
    SPECIAL    = 21  # PEDTYPE_SPECIAL
    UNUSED2    = 22  # PEDTYPE_UNUSED2


PED_TYPE_COUNT = 23


# CPedType
class PedData:
    def __init__ (self):
        self.flags   : TInt   = None  # uint32 m_flag
        self.unk1    : TFloat = None  # float unk1
        self.unk2    : TFloat = None  # float unk2
        self.unk3    : TFloat = None  # float unk3
        self.unk4    : TFloat = None  # float unk4
        self.unk5    : TFloat = None  # float unk5
        self.threats : TInt   = None  # uint32 m_threats
        self.avoid   : TInt   = None  # uint32 m_avoid



class PedReader:
    @classmethod
    def fromFile (cls, filePath : str, ctx : Opt[Any] = None):
        if not isFile(filePath):
            raise OSError(f'File does not exist: { filePath }')

        text = readText(filePath, encoding='utf-8')

        return cls().read(text, ctx)

    def read (self, text : str, ctx : Opt[Any] = None):
        peds = Array(PED_TYPE_COUNT, PedData)

        for ped in peds:
            ped.flags   = PedFlag.PLAYER1
            ped.unk1    = 0
            ped.unk2    = 0
            # unk3 not initialized
            ped.unk4    = 0
            ped.unk5    = 0
            ped.threats = 0
            ped.avoid   = 0

        if ctx is not None:
            ctx.peds = peds

        # ----------------------------------------------

        lines = text.split('\n')

        pedType = None

        for line in lines:
            line = line.split('#')[0].strip()

            if not line:
                continue

            values = splitSeps(line)

            key    = values[0]
            values = values[1:]

            if key == 'Threat':
                ped = peds[pedType]

                ped.threats = 0

                for value in values:
                    assert PedFlag.hasKey(value)

                    ped.threats |= PedFlag.getValue(value)

            elif key == 'Avoid':
                ped = peds[pedType]

                ped.avoid = 0

                for value in values:
                    assert PedFlag.hasKey(value)

                    ped.avoid |= PedFlag.getValue(value)
            else:
                pedName = key.upper()

                assert PedType.hasKey(pedName), pedName
                assert PedFlag.hasKey(pedName)

                pedType = PedType.getValue(pedName)

                ped = peds[pedType]

                ped.flags |= PedFlag.getValue(pedName)
                ped.unk1   = float(values[0]) / 50
                ped.unk2   = float(values[1]) / 50
                ped.unk3   = float(values[2]) / 50
                ped.unk4   = float(values[3])
                ped.unk5   = float(values[4])

        return peds



def _test_ ():
    print(toJson(PedReader.fromFile(joinPath(GAME_DIR, 'data/ped.dat'))))



__all__ = [
    'PedReader',
    'PedData',

    '_test_',
]



if __name__ == '__main__':
    _test_()
