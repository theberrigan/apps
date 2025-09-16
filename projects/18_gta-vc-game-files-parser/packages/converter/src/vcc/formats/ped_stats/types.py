from typing import Dict, Optional

from ...common import bfw
from ...common.types import *

from bfw.types.enums import Enum



class PedStatsType (Enum):
    Player       = 0
    Cop          = 1
    Medic        = 2
    Fireman      = 3
    Gang1        = 4
    Gang2        = 5
    Gang3        = 6
    Gang4        = 7
    Gang5        = 8
    Gang6        = 9
    Gang7        = 10
    StreetGuy    = 11
    SuitGuy      = 12
    SensibleGuy  = 13
    GeekGuy      = 14
    OldGuy       = 15
    ToughGuy     = 16
    StreetGirl   = 17
    SuitGirl     = 18
    SensibleGirl = 19
    GeekGirl     = 20
    OldGirl      = 21
    ToughGirl    = 22
    TrampMale    = 23
    TrampFemale  = 24
    Tourist      = 25
    Prostitute   = 26
    Criminal     = 27
    Busker       = 28
    TaxiDriver   = 29
    Psycho       = 30
    Steward      = 31
    SportsFan    = 32
    Shopper      = 33
    OldShopper   = 34
    BeachGuy     = 35
    BeachGirl    = 36
    Skater       = 37
    StdMission   = 38
    Coward       = 39


class PedStatsFlag (Enum):
    PunchOnly       = 1 << 0
    CanKneeHead     = 1 << 1
    CanKick         = 1 << 2
    CanRoundHse     = 1 << 3
    NoDive          = 1 << 4
    OneHitKnockdown = 1 << 5
    ShoppingBags    = 1 << 6
    GunPanic        = 1 << 7


# name                - ignored: MUST be in correct order
# fleeDistance        - float
# headingChangeRate   - float in degrees
# fear                - 0-100 (100 - Scared of everything)
# temper              - 0-100 (100 - Bad Tempered)
# lawfulness          - 0-100 (100 - Boy Scout)
# sexiness            - 0-100
# attackStrength      - float multiplier to attack damages
# defendWeakness      - float multiplier to received damages
# flags               - see PedStatFlag
class PedStatsData:
    def __init__ (self):
        self.type              : TInt   = None  # ePedStats m_type (PedStatType)
        self.name              : TStr   = None  # char m_name[24]
        self.fleeDistance      : TFloat = None  # float m_fleeDistance
        self.headingChangeRate : TFloat = None  # float m_headingChangeRate
        self.fear              : TInt   = None  # int8 m_fear
        self.temper            : TInt   = None  # int8 m_temper
        self.lawfulness        : TInt   = None  # int8 m_lawfulness
        self.sexiness          : TInt   = None  # int8 m_sexiness
        self.attackStrength    : TFloat = None  # float m_attackStrength
        self.defendWeakness    : TFloat = None  # float m_defendWeakness
        self.flags             : TInt   = None  # int16 m_flags (PedStatFlag)


class PedStats:
    def __init__ (self):
        self.items : Dict[str, PedStatsData] = {}

    def add (self, data : PedStatsData) -> PedStatsData:
        self.items[data.name] = data

        return data

    def getByName (self, name : str) -> Optional[PedStatsData]:
        return self.items.get(name)

TPedStats = Optional[PedStats]



__all__ = [
    'PedStatsType',
    'PedStatsFlag',
    'PedStatsData',
    'PedStats',
    'TPedStats',
]
