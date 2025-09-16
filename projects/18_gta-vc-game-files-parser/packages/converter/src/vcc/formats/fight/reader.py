from ...common import bfw
from ...common.types import *
from ...common.game_data import *
from ...common.fns import splitSpaces, toInts, toFloats

from .consts import *
from .types import *

from bfw.utils import *



class FightMove:
    def __init__ (self):
        self.animId            : TInt   = None  # AnimationId animId;
        self.moveName          : TStr   = None
        self.startFireTime     : TFloat = None  # float startFireTime;
        self.endFireTime       : TFloat = None  # float endFireTime;
        self.comboFollowOnTime : TFloat = None  # float comboFollowOnTime;
        self.strikeRadius      : TFloat = None  # float strikeRadius;
        self.extendReachMult   : TFloat = None  # float extendReachMultiplier;
        self.hitLevel          : TInt   = None  # uint8 hitLevel; // FightMoveHitLevel
        self.animName          : TStr   = None
        self.damage            : TInt   = None  # uint8 damage;
        self.flags             : TInt   = None  # uint8 flags;


class FightReader:
    @classmethod
    def parseDefault (cls):
        return cls.fromFile(FIGHT_FILE_PATH)

    @classmethod
    def fromFile (cls, filePath : str):
        if not isFile(filePath):
            raise OSError(f'File does not exist: { filePath }')

        text = readText(filePath, encoding='utf-8')

        return cls().read(text)

    def read (self, text : str):
        lines = text.split('\n')

        moves  = []
        moveIndex = 0

        for line in lines:
            line = line.strip()

            if line == 'ENDWEAPONDATA':
                break

            if not line or line[0] == '#':
                continue

            values = splitSpaces(line)

            item = FightMove()

            item.animId            = FIGHT_DEFAULT_ANIMS[moveIndex]
            item.moveName          = values[0].lower()
            item.startFireTime     = float(values[1]) / 30
            item.endFireTime       = float(values[2]) / 30
            item.comboFollowOnTime = float(values[3]) / 30
            item.strikeRadius      = float(values[4])
            item.extendReachMult   = float(values[5])
            item.hitLevel          = FIGHT_HIT_LEVEL_MAP[values[6].upper()]
            item.animName          = values[7].lower()
            item.damage            = int(values[8])
            item.flags             = int(values[9])

            if item.animName != 'default':
                if item.animName != 'null':
                    raise Exception('NOT IMPLEMENTED')   # TODO: complete after ped.ifp loading (game\src\peds\PedFight.cpp:2388)
                else:
                    item.animId = AnimationId.STD_WALK

            moveIndex += 1

        return moves



def _test_ ():
    print(toJson(FightReader.parseDefault()))



__all__ = [
    'FightReader',

    '_test_',
]



if __name__ == '__main__':
    _test_()
