from ...common import bfw
from ...common.consts import *

from .types import PedStatsType

from bfw.utils import joinPath



PED_STATS_FILE_PATH = joinPath(GAME_DIR, 'data', 'pedstats.dat')



__all__ = [
    'PED_STATS_FILE_PATH',
]