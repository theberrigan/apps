from ...common import bfw

from bfw.types.enums import Enum



class TCWeatherType (Enum):
    Sunny        = 1
    Cloudy       = 2
    Rainy1       = 3
    Foggy        = 4
    ExtraSunny   = 5
    Rainy2       = 6
    ExtraColours = 7



__all__ = [
    'TCWeatherType',
]
