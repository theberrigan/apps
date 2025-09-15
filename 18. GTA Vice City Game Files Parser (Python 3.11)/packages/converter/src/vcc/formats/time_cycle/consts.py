from ...common import bfw
from ...common.consts import *

from bfw.utils import joinPath



TIME_CYCLE_FILE_PATH = joinPath(GAME_DIR, 'data', 'timecyc.dat')

TC_WEATHER_COUNT = 7
TC_HOUR_COUNT    = 24

TC_WEATHER_NAMES = [
    'Sunny',
    'Cloudy',
    'Rainy',
    'Foggy',
    'Extra Sunny',
    'Rainy',
    'Extra Colours',
]



__all__ = [
    'TIME_CYCLE_FILE_PATH',
    'TC_WEATHER_COUNT',
    'TC_HOUR_COUNT',
    'TC_WEATHER_NAMES',
]