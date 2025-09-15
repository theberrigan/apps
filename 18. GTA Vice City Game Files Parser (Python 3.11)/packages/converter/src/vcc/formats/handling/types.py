import math

from typing import Dict, Optional

from ...common import bfw
from ...common.types import *

from bfw.types.enums import Enum



# noinspection SpellCheckingInspection
class VehicleType (Enum):
    LANDSTAL = 0
    IDAHO    = 1
    STINGER  = 2
    LINERUN  = 3
    PEREN    = 4
    SENTINEL = 5
    PATRIOT  = 6
    FIRETRUK = 7
    TRASH    = 8
    STRETCH  = 9
    MANANA   = 10
    INFERNUS = 11
    PONY     = 12
    MULE     = 13
    CHEETAH  = 14
    AMBULAN  = 15
    FBICAR   = 16
    MOONBEAM = 17
    ESPERANT = 18
    TAXI     = 19
    KURUMA   = 20
    BOBCAT   = 21
    MRWHOOP  = 22
    BFINJECT = 23
    POLICE   = 24
    ENFORCER = 25
    SECURICA = 26
    BANSHEE  = 27
    BUS      = 28
    RHINO    = 29
    BARRACKS = 30
    TRAIN    = 31
    HELI     = 32
    DODO     = 33
    COACH    = 34
    CABBIE   = 35
    STALLION = 36
    RUMPO    = 37
    RCBANDIT = 38
    MAFIA    = 39
    AIRTRAIN = 40
    DEADDODO = 41
    FLATBED  = 42
    YANKEE   = 43
    GOLFCART = 44
    VOODOO   = 45
    WASHING  = 46
    CUBAN    = 47
    ROMERO   = 48
    PACKER   = 49
    ADMIRAL  = 50
    GANGBUR  = 51
    ZEBRA    = 52
    TOPFUN   = 53
    GLENDALE = 54
    OCEANIC  = 55
    HERMES   = 56
    SABRE1   = 57
    SABRETUR = 58
    PHEONIX  = 59
    WALTON   = 60
    REGINA   = 61
    COMET    = 62
    DELUXO   = 63
    BURRITO  = 64
    SPAND    = 65
    BAGGAGE  = 66
    KAUFMAN  = 67
    RANCHER  = 68
    FBIRANCH = 69
    VIRGO    = 70
    GREENWOO = 71
    HOTRING  = 72
    SANDKING = 73
    BLISTAC  = 74
    BOXVILLE = 75
    BENSON   = 76
    DESPERAD = 77
    LOVEFIST = 78
    BLOODRA  = 79
    BLOODRB  = 80
    BIKE     = 81
    MOPED    = 82
    DIRTBIKE = 83
    ANGEL    = 84
    FREEWAY  = 85
    PREDATOR = 86
    SPEEDER  = 87
    REEFER   = 88
    RIO      = 89
    SQUALO   = 90
    TROPIC   = 91
    COASTGRD = 92
    DINGHY   = 93
    MARQUIS  = 94
    CUPBOAT  = 95
    SEAPLANE = 96
    SPARROW  = 97
    SEASPAR  = 98
    MAVERICK = 99
    COASTMAV = 100
    POLMAV   = 101
    HUNTER   = 102
    RCBARON  = 103
    RCGOBLIN = 104
    RCCOPTER = 105



class Handling:
    def __init__ (self):
        self.items : Dict[str, VehicleHandlingData] = {}

    def add (self, data : 'VehicleHandlingData') -> 'VehicleHandlingData':
        self.items[data.name] = data

        return data

    def getByName (self, name : str) -> Optional['VehicleHandlingData']:
        return self.items.get(name)


class VehicleHandlingData:
    def __init__ (self):
        self.id   : TInt = None  # tVehicleType nIdentifier
        self.name : TStr = None


class BoatHandlingData (VehicleHandlingData):
    def __init__ (self):
        super().__init__()

        self.thrustY               : TFloat = None  # float fThrustY
        self.thrustZ               : TFloat = None  # float fThrustZ
        self.thrustAppZ            : TFloat = None  # float fThrustAppZ
        self.aqPlaneForce          : TFloat = None  # float fAqPlaneForce
        self.aqPlaneLimit          : TFloat = None  # float fAqPlaneLimit
        self.aqPlaneOffset         : TFloat = None  # float fAqPlaneOffset
        self.waveAudioMult         : TFloat = None  # float fWaveAudioMult
        self.moveRes               : TVec   = None  # CVector vecMoveRes
        self.turnRes               : TVec   = None  # CVector vecTurnRes
        self.lookLRBehindCamHeight : TFloat = None  # float fLook_L_R_BehindCamHeight


class BikeHandlingData (VehicleHandlingData):
    def __init__ (self):
        super().__init__()

        self.leanFwdCOM      : TFloat = None  # float fLeanFwdCOM
        self.leanFwdForce    : TFloat = None  # float fLeanFwdForce
        self.leanBakCOM      : TFloat = None  # float fLeanBakCOM
        self.leanBackForce   : TFloat = None  # float fLeanBackForce
        self.maxLean         : TFloat = None  # float fMaxLean
        self.fullAnimLean    : TFloat = None  # float fFullAnimLean
        self.desLean         : TFloat = None  # float fDesLean
        self.speedSteer      : TFloat = None  # float fSpeedSteer
        self.slipSteer       : TFloat = None  # float fSlipSteer
        self.noPlayerCOMz    : TFloat = None  # float fNoPlayerCOMz
        self.wheelieAng      : TFloat = None  # float fWheelieAng
        self.stoppieAng      : TFloat = None  # float fStoppieAng
        self.wheelieSteer    : TFloat = None  # float fWheelieSteer
        self.wheelieStabMult : TFloat = None  # float fWheelieStabMult
        self.stoppieStabMult : TFloat = None  # float fStoppieStabMult


class FlyingHandlingData (VehicleHandlingData):
    def __init__ (self):
        super().__init__()

        self.thrust        : TFloat = None  # float fThrust
        self.thrustFallOff : TFloat = None  # float fThrustFallOff
        self.yaw           : TFloat = None  # float fYaw
        self.yawStab       : TFloat = None  # float fYawStab
        self.sideSlip      : TFloat = None  # float fSideSlip
        self.roll          : TFloat = None  # float fRoll
        self.rollStab      : TFloat = None  # float fRollStab
        self.pitch         : TFloat = None  # float fPitch
        self.pitchStab     : TFloat = None  # float fPitchStab
        self.formLift      : TFloat = None  # float fFormLift
        self.attackLift    : TFloat = None  # float fAttackLift
        self.moveRes       : TFloat = None  # float fMoveRes
        self.turnRes       : TVec   = None  # CVector vecTurnRes
        self.speedRes      : TVec   = None  # CVector vecSpeedRes


class RegularHandlingData (VehicleHandlingData):
    def __init__ (self):
        super().__init__()

        TTransmission = HandlingTransmission | None

        self.mass                          : TFloat        = None  # float fMass
        self.turnMass                      : TFloat        = None  # float fTurnMass
        self.invMass                       : TFloat        = None  # float fInvMass
        self.buoyancy                      : TFloat        = None  # float fBuoyancy
        self.dimension                     : TVec          = None  # CVector Dimension
        self.centreOfMass                  : TVec          = None  # CVector CentreOfMass
        self.percentSubmerged              : TInt          = None  # int8 nPercentSubmerged
        self.tractionMultiplier            : TFloat        = None  # float fTractionMultiplier
        self.tractionLoss                  : TFloat        = None  # float fTractionLoss
        self.tractionBias                  : TFloat        = None  # float fTractionBias
        self.transmission                  : TTransmission = None
        self.brakeDeceleration             : TFloat        = None  # float fBrakeDeceleration
        self.brakeBias                     : TFloat        = None  # float fBrakeBias
        self.hasABS                        : TBool         = None  # int8 bABS
        self.steeringLock                  : TFloat        = None  # float fSteeringLock
        self.suspensionForceLevel          : TFloat        = None  # float fSuspensionForceLevel
        self.suspensionDampingLevel        : TFloat        = None  # float fSuspensionDampingLevel
        self.seatOffsetDistance            : TFloat        = None  # float fSeatOffsetDistance
        self.collisionDamageMultiplier     : TFloat        = None  # float fCollisionDamageMultiplier
        self.monetaryValue                 : TInt          = None  # int32 nMonetaryValue
        self.suspensionUpperLimit          : TFloat        = None  # float fSuspensionUpperLimit
        self.suspensionLowerLimit          : TFloat        = None  # float fSuspensionLowerLimit
        self.suspensionBias                : TFloat        = None  # float fSuspensionBias
        self.suspensionAntiDiveMultiplier  : TFloat        = None  # float fSuspensionAntidiveMultiplier
        self.frontLights                   : TInt          = None  # int8 FrontLights
        self.rearLights                    : TInt          = None  # int8 RearLights


class HandlingTransmission:
    def __init__ (self):
        TGear = list[HandlingGear] | None

        self.numberOfGears       : TInt   = None  # int8 nNumberOfGears
        self.maxVelocity         : TFloat = None  # float fMaxVelocity
        self.maxCruiseVelocity   : TFloat = None  # float fMaxCruiseVelocity
        self.maxReverseVelocity  : TFloat = None  # float fMaxReverseVelocity
        self.engineAcceleration  : TFloat = None  # float fEngineAcceleration
        self.driveType           : TStr   = None  # char nDriveType
        self.engineType          : TStr   = None  # char nEngineType
        self.flags               : TInt   = None  # uint8 Flags
        self.gears               : TGear  = None  # tGear Gears[6]


class HandlingGear:
    def __init__ (self):
        self.maxVelocity       : TFloat = None  # float fMaxVelocity
        self.shiftUpVelocity   : TFloat = None  # float fShiftUpVelocity
        self.shiftDownVelocity : TFloat = None  # float fShiftDownVelocity



__all__ = [
    'VehicleType',
    'Handling',
    'VehicleHandlingData',
    'BoatHandlingData',
    'BikeHandlingData',
    'FlyingHandlingData',
    'RegularHandlingData',
    'HandlingTransmission',
    'HandlingGear',
]
