from ...common import bfw
from ...common.types import *
from ...common.consts import *
from ...common.fns import splitSpaces

from .consts import *
from .types import *

from bfw.utils import *



class PedStatsReader:
    @classmethod
    def fromFile (cls, filePath : str, ctx : Opt[Any] = None) -> PedStats:
        if not isFile(filePath):
            raise OSError(f'File does not exist: { filePath }')

        text = readText(filePath, encoding='utf-8')

        return cls().read(text, ctx)

    def read (self, text : str, ctx : Opt[Any] = None) -> PedStats:
        stats = PedStats()

        if ctx is not None:
            ctx.pedStats = stats

        lines = text.split('\n')

        statsType = 0

        for line in lines:
            line = line.strip()

            if not line or line.startswith('#'):
                continue

            values = splitSpaces(line)

            data = PedStatsData()

            data.type              = statsType  # see PedStatsType
            data.name              = values[0].upper()
            data.fleeDistance      = float(values[1])
            data.headingChangeRate = float(values[2])
            data.fear              = int(values[3])
            data.temper            = int(values[4])
            data.lawfulness        = int(values[5])
            data.sexiness          = int(values[6])
            data.attackStrength    = float(values[7])
            data.defendWeakness    = float(values[8])
            data.flags             = int(values[9])

            stats.add(data)

            statsType += 1

        return stats



def _test_ ():
    print(toJson(PedStatsReader.fromFile(joinPath(GAME_DIR, 'data/pedstats.dat'))))



__all__ = [
    'PedStatsReader',

    '_test_',
]



if __name__ == '__main__':
    _test_()
