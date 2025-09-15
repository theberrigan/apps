from typing import Type

from ...common import bfw
from ...common.types import *
from ...common.consts import *
from ...common.fns import splitSpaces

from .consts import *
from .types import *

from bfw.utils import *
from bfw.types.enums import Enum



class TCHour:
    def __init__ (self):
        self.ambient                  : TInt = None  # uint8 m_nAmbient<Red/Green/Blue>
        self.ambientObj               : TInt = None  # uint8 m_nAmbient<Red/Green/Blue>_Obj
        self.ambientBl                : TInt = None  # uint8 m_nAmbient<Red/Green/Blue>_Bl
        self.ambientObjBl             : TInt = None  # uint8 m_nAmbient<Red/Green/Blue>_Obj_Bl
        self.directional              : TInt = None  # uint8 m_nDirectional<Red/Green/Blue>
        self.skyTop                   : TInt = None  # uint8 m_nSkyTop<Red/Green/Blue>
        self.skyBottom                : TInt = None  # uint8 m_nSkyBottom<Red/Green/Blue>
        self.sunCore                  : TInt = None  # uint8 m_nSunCore<Red/Green/Blue>
        self.sunCorona                : TInt = None  # uint8 m_nSunCorona<Red/Green/Blue>
        self.sunSize                  : TInt = None  # int8 m_fSunSize
        self.spriteSize               : TInt = None  # int8 m_fSpriteSize
        self.spriteBrightness         : TInt = None  # int8 m_fSpriteBrightness
        self.shadowStrength           : TInt = None  # uint8 m_nShadowStrength
        self.lightShadowStrength      : TInt = None  # uint8 m_nLightShadowStrength
        self.poleShadowStrength       : TInt = None  # uint8 m_nPoleShadowStrength
        self.farClip                  : TInt = None  # int16 m_fFarClip
        self.fogStart                 : TInt = None  # int16 m_fFogStart
        self.lightsOnGroundBrightness : TInt = None  # uint8 m_fLightsOnGroundBrightness
        self.lowClouds                : TInt = None  # uint8 m_nLowClouds<Red/Green/Blue>
        self.fluffyCloudsTop          : TInt = None  # uint8 m_nFluffyCloudsTopRed<Red/Green/Blue>
        self.fluffyCloudsBottom       : TInt = None  # uint8 m_nFluffyCloudsBottom<Red/Green/Blue>
        self.blur                     : TInt = None  # uint8 m_fBlur<Red/Green/Blue>
        self.water                    : TInt = None  # uint8 m_fWater<Red/Green/Blue/Alpha>


class TCWeather:
    def __init__ (self):
        THours = list[TCHour] | None

        self.name  : TStr   = None
        self.type  : TInt   = None  # see TCWeatherType
        self.hours : THours = None


class TimeCycleReader:
    @classmethod
    def parseDefault (cls, encoding : str = 'utf-8') -> list[TCWeather]:
        return cls.fromFile(TIME_CYCLE_FILE_PATH, encoding)

    @classmethod
    def fromFile (cls, filePath : str, encoding : str = 'utf-8') -> list[TCWeather]:
        if not isFile(filePath):
            raise OSError(f'File does not exist: { filePath }')

        text = readText(filePath, encoding=encoding)

        return cls().read(text)

    @classmethod
    def fromBuffer (cls, text : str) -> list[TCWeather]:
        return cls().read(text)

    def read (self, text : str) -> list[TCWeather]:
        result = []

        weatherType = 0
        hourIndex   = 0

        lines = text.split('\n')

        weather : TCWeather | None = None

        for line in lines:
            line = line.strip()

            if not line or line.startswith('//'):
                continue

            values = splitSpaces(line)

            if hourIndex == 0:
                weather = TCWeather()

                weather.name  = TC_WEATHER_NAMES[weatherType]
                weather.type  = weatherType
                weather.hours = []

                result.append(weather)

            hour = TCHour()

            hour.ambient                  = self.toInts(values[0:3])      # uint8 m_nAmbient<Red/Green/Blue>
            hour.ambientObj               = self.toInts(values[3:6])      # uint8 m_nAmbient<Red/Green/Blue>_Obj
            hour.ambientBl                = self.toInts(values[6:9])      # uint8 m_nAmbient<Red/Green/Blue>_Bl
            hour.ambientObjBl             = self.toInts(values[9:12])     # uint8 m_nAmbient<Red/Green/Blue>_Obj_Bl
            hour.directional              = self.toInts(values[12:15])    # uint8 m_nDirectional<Red/Green/Blue>
            hour.skyTop                   = self.toInts(values[15:18])    # uint8 m_nSkyTop<Red/Green/Blue>
            hour.skyBottom                = self.toInts(values[18:21])    # uint8 m_nSkyBottom<Red/Green/Blue>
            hour.sunCore                  = self.toInts(values[21:24])    # uint8 m_nSunCore<Red/Green/Blue>
            hour.sunCorona                = self.toInts(values[24:27])    # uint8 m_nSunCorona<Red/Green/Blue>
            hour.sunSize                  = int(float(values[27]) * 10)   # int8 m_fSunSize
            hour.spriteSize               = int(float(values[28]) * 10)   # int8 m_fSpriteSize
            hour.spriteBrightness         = int(float(values[29]) * 10)   # int8 m_fSpriteBrightness
            hour.shadowStrength           = int(values[30])               # uint8 m_nShadowStrength
            hour.lightShadowStrength      = int(values[31])               # uint8 m_nLightShadowStrength
            hour.poleShadowStrength       = int(values[32])               # uint8 m_nPoleShadowStrength
            hour.farClip                  = int(float(values[33]))        # int16 m_fFarClip
            hour.fogStart                 = int(float(values[34]))        # int16 m_fFogStart
            hour.lightsOnGroundBrightness = int(float(values[35]) * 10)   # uint8 m_fLightsOnGroundBrightness
            hour.lowClouds                = self.toInts(values[36:39])    # uint8 m_nLowClouds<Red/Green/Blue>
            hour.fluffyCloudsTop          = self.toInts(values[39:42])    # uint8 m_nFluffyCloudsTopRed<Red/Green/Blue>
            hour.fluffyCloudsBottom       = self.toInts(values[42:45])    # uint8 m_nFluffyCloudsBottom<Red/Green/Blue>
            hour.blur                     = self.toInts(values[45:48])    # uint8 m_fBlur<Red/Green/Blue>
            hour.water                    = self.toInts(values[48:52])    # uint8 m_fWater<Red/Green/Blue/Alpha>

            weather.hours.append(hour)

            if (hourIndex + 1) == TC_HOUR_COUNT:
                weatherType += 1
                hourIndex = 0
            else:
                hourIndex += 1

        assert weatherType == TC_WEATHER_COUNT and hourIndex == 0

        return result

    def toFloats (self, values : list[str]) -> list[float]:
        return [ float(v) for v in values ]

    def toInts (self, values : list[str]) -> list[int]:
        return [ int(v, 10) for v in values ]


def _test_ ():
    print(toJson(TimeCycleReader.parseDefault()))



__all__ = [
    'TimeCycleReader',
    'TCWeather',
    'TCHour',

    '_test_',
]



if __name__ == '__main__':
    _test_()
