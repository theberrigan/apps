from ...common import bfw

from bfw.types.enums import Enum



class ParticleType (Enum):
    SPARK               = 0
    SPARK_SMALL         = 1
    WATER_SPARK         = 2
    WHEEL_DIRT          = 3
    SAND                = 4
    WHEEL_WATER         = 5
    BLOOD               = 6
    BLOOD_SMALL         = 7
    BLOOD_SPURT         = 8
    DEBRIS              = 9
    DEBRIS2             = 10
    FLYERS              = 11
    WATER               = 12
    FLAME               = 13
    FIREBALL            = 14
    GUNFLASH            = 15
    GUNFLASH_NOANIM     = 16
    GUNSMOKE            = 17
    GUNSMOKE2           = 18
    CIGARETTE_SMOKE     = 19
    SMOKE               = 20
    SMOKE_SLOWMOTION    = 21
    DRY_ICE             = 22
    TEARGAS             = 23
    GARAGEPAINT_SPRAY   = 24
    SHARD               = 25
    SPLASH              = 26
    CARFLAME            = 27
    STEAM               = 28
    STEAM2              = 29
    STEAM_NY            = 30
    STEAM_NY_SLOWMOTION = 31
    GROUND_STEAM        = 32
    ENGINE_STEAM        = 33
    RAINDROP            = 34
    RAINDROP_SMALL      = 35
    RAIN_SPLASH         = 36
    RAIN_SPLASH_BIGGROW = 37
    RAIN_SPLASHUP       = 38
    WATERSPRAY          = 39
    WATERDROP           = 40
    BLOODDROP           = 41
    EXPLOSION_MEDIUM    = 42
    EXPLOSION_LARGE     = 43
    EXPLOSION_MFAST     = 44
    EXPLOSION_LFAST     = 45
    CAR_SPLASH          = 46
    BOAT_SPLASH         = 47
    BOAT_THRUSTJET      = 48
    WATER_HYDRANT       = 49
    WATER_CANNON        = 50
    EXTINGUISH_STEAM    = 51
    PED_SPLASH          = 52
    PEDFOOT_DUST        = 53
    CAR_DUST            = 54
    HELI_DUST           = 55
    HELI_ATTACK         = 56
    ENGINE_SMOKE        = 57
    ENGINE_SMOKE2       = 58
    CARFLAME_SMOKE      = 59
    FIREBALL_SMOKE      = 60
    PAINT_SMOKE         = 61
    TREE_LEAVES         = 62
    CARCOLLISION_DUST   = 63
    CAR_DEBRIS          = 64
    BIRD_DEBRIS         = 65
    HELI_DEBRIS         = 66
    EXHAUST_FUMES       = 67
    RUBBER_SMOKE        = 68
    BURNINGRUBBER_SMOKE = 69
    BULLETHIT_SMOKE     = 70
    GUNSHELL_FIRST      = 71
    GUNSHELL            = 72
    GUNSHELL_BUMP1      = 73
    GUNSHELL_BUMP2      = 74
    ROCKET_SMOKE        = 75
    TEST                = 76
    BIRD_FRONT          = 77
    SHIP_SIDE           = 78
    BEASTIE             = 79
    RAINDROP_2D         = 80
    HEATHAZE            = 81
    HEATHAZE_IN_DIST    = 82



__all__ = [
    'ParticleType',
]