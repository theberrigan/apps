import math

from typing import Dict, Optional

from ...common import bfw
from ...common.types import *
from ...common.consts import *
from ...common.game_data import *
from ...common.fns import splitSpaces
from ...maths import degToRad

from .consts import *
from .types import *

from bfw.utils import *
from bfw.types.enums import Enum



class HandlingReader:
    @classmethod
    def parseDefault (cls, convert : bool = True, encoding : str = 'utf-8') -> Handling:
        return cls.fromFile(HANDLING_FILE_PATH, convert, encoding)

    @classmethod
    def fromFile (cls, filePath : str, convert : bool = True, encoding : str = 'utf-8') -> Handling:
        if not isFile(filePath):
            raise OSError(f'File does not exist: { filePath }')

        text = readText(filePath, encoding=encoding)

        return cls().read(text, convert)

    @classmethod
    def fromBuffer (cls, text : str, convert : bool = True) -> Handling:
        return cls().read(text, convert)

    def read (self, text : str, convert : bool = True) -> Handling:
        handling = Handling()

        lines = text.split('\n')

        for line in lines:
            line = line.strip()

            if line == ';the end':
                break

            if not line or line.startswith(';'):
                continue

            firstChar = line[0]

            if firstChar in '%!$':
                line = line[1:].lstrip()

            values = splitSpaces(line)

            vehicleName = values[0].upper()
            vehicleId   = VehicleType.getValue(vehicleName)

            values = values[1:]

            match firstChar:
                case '%':  # Boats
                    vehicle = BoatHandlingData()

                    vehicle.id                    = vehicleId                         # tVehicleType nIdentifier
                    vehicle.name                  = vehicleName
                    vehicle.thrustY               = float(values[0])                 # float fThrustY
                    vehicle.thrustZ               = float(values[1])                 # float fThrustZ
                    vehicle.thrustAppZ            = float(values[2])                 # float fThrustAppZ
                    vehicle.aqPlaneForce          = float(values[3])                 # float fAqPlaneForce
                    vehicle.aqPlaneLimit          = float(values[4])                 # float fAqPlaneLimit
                    vehicle.aqPlaneOffset         = float(values[5])                 # float fAqPlaneOffset
                    vehicle.waveAudioMult         = float(values[6])                 # float fWaveAudioMult
                    vehicle.moveRes               = self.parseVector(values[7:10])   # CVector vecMoveRes
                    vehicle.turnRes               = self.parseVector(values[10:13])  # CVector vecTurnRes
                    vehicle.lookLRBehindCamHeight = float(values[13])                # float fLook_L_R_BehindCamHeight

                    handling.add(vehicle)

                case '!':  # Bikes
                    vehicle = BikeHandlingData()

                    vehicle.id              = vehicleId          # tVehicleType nIdentifier
                    vehicle.name            = vehicleName
                    vehicle.leanFwdCOM      = float(values[0])   # float fLeanFwdCOM
                    vehicle.leanFwdForce    = float(values[1])   # float fLeanFwdForce
                    vehicle.leanBakCOM      = float(values[2])   # float fLeanBakCOM
                    vehicle.leanBackForce   = float(values[3])   # float fLeanBackForce
                    vehicle.maxLean         = float(values[4])   # float fMaxLean
                    vehicle.fullAnimLean    = float(values[5])   # float fFullAnimLean
                    vehicle.desLean         = float(values[6])   # float fDesLean
                    vehicle.speedSteer      = float(values[7])   # float fSpeedSteer
                    vehicle.slipSteer       = float(values[8])   # float fSlipSteer
                    vehicle.noPlayerCOMz    = float(values[9])   # float fNoPlayerCOMz
                    vehicle.wheelieAng      = float(values[10])  # float fWheelieAng
                    vehicle.stoppieAng      = float(values[11])  # float fStoppieAng
                    vehicle.wheelieSteer    = float(values[12])  # float fWheelieSteer
                    vehicle.wheelieStabMult = float(values[13])  # float fWheelieStabMult
                    vehicle.stoppieStabMult = float(values[14])  # float fStoppieStabMult

                    if convert:
                        self.convertBike(vehicle)

                    handling.add(vehicle)

                case '$':  # Heli and planes
                    vehicle = FlyingHandlingData()

                    vehicle.id            = vehicleId                         # tVehicleType nIdentifier
                    vehicle.name          = vehicleName
                    vehicle.thrust        = float(values[0])                 # float fThrust
                    vehicle.thrustFallOff = float(values[1])                 # float fThrustFallOff
                    vehicle.yaw           = float(values[2])                 # float fYaw
                    vehicle.yawStab       = float(values[3])                 # float fYawStab
                    vehicle.sideSlip      = float(values[4])                 # float fSideSlip
                    vehicle.roll          = float(values[5])                 # float fRoll
                    vehicle.rollStab      = float(values[6])                 # float fRollStab
                    vehicle.pitch         = float(values[7])                 # float fPitch
                    vehicle.pitchStab     = float(values[8])                 # float fPitchStab
                    vehicle.formLift      = float(values[9])                 # float fFormLift
                    vehicle.attackLift    = float(values[10])                # float fAttackLift
                    vehicle.moveRes       = float(values[11])                # float fMoveRes
                    vehicle.turnRes       = self.parseVector(values[12:15])  # CVector vecTurnRes
                    vehicle.speedRes      = self.parseVector(values[15:18])  # CVector vecSpeedRes

                    handling.add(vehicle)

                case _:  # Other vehicles
                    vehicle = RegularHandlingData()

                    vehicle.id                              = vehicleId                      # tVehicleType nIdentifier
                    vehicle.name                            = vehicleName
                    vehicle.mass                            = float(values[0])               # float fMass
                    vehicle.turnMass                        = None                           # float fTurnMass
                    vehicle.invMass                         = None                           # float fInvMass
                    vehicle.buoyancy                        = None                           # float fBuoyancy
                    vehicle.dimension                       = self.parseVector(values[1:4])  # CVector Dimension
                    vehicle.centreOfMass                    = self.parseVector(values[4:7])  # CVector CentreOfMass
                    vehicle.percentSubmerged                = int(values[7])                 # int8 nPercentSubmerged
                    vehicle.tractionMultiplier              = float(values[8])               # float fTractionMultiplier
                    vehicle.tractionLoss                    = float(values[9])               # float fTractionLoss
                    vehicle.tractionBias                    = float(values[10])              # float fTractionBias
                    vehicle.transmission                    = HandlingTransmission()
                    vehicle.transmission.numberOfGears      = int(values[11])                # int8 nNumberOfGears
                    vehicle.transmission.maxVelocity        = float(values[12])              # float fMaxVelocity
                    vehicle.transmission.maxCruiseVelocity  = None                           # float fMaxCruiseVelocity
                    vehicle.transmission.maxReverseVelocity = None                           # float fMaxReverseVelocity
                    vehicle.transmission.engineAcceleration = float(values[13]) * 0.4        # float fEngineAcceleration
                    vehicle.transmission.driveType          = values[14].upper()             # char nDriveType
                    vehicle.transmission.engineType         = values[15].upper()             # char nEngineType
                    vehicle.transmission.flags              = int(values[29], 16)            # uint8 Flags
                    vehicle.transmission.gears              = [ HandlingGear() for _ in range(6)]   # tGear Gears[6]
                    vehicle.brakeDeceleration               = float(values[16])              # float fBrakeDeceleration
                    vehicle.brakeBias                       = float(values[17])              # float fBrakeBias
                    vehicle.hasABS                          = bool(int(values[18]))          # int8 bABS
                    vehicle.steeringLock                    = float(values[19])              # float fSteeringLock
                    vehicle.suspensionForceLevel            = float(values[20])              # float fSuspensionForceLevel
                    vehicle.suspensionDampingLevel          = float(values[21])              # float fSuspensionDampingLevel
                    vehicle.seatOffsetDistance              = float(values[22])              # float fSeatOffsetDistance
                    vehicle.collisionDamageMultiplier       = float(values[23])              # float fCollisionDamageMultiplier
                    vehicle.monetaryValue                   = int(values[24])                # int32 nMonetaryValue
                    vehicle.suspensionUpperLimit            = float(values[25])              # float fSuspensionUpperLimit
                    vehicle.suspensionLowerLimit            = float(values[26])              # float fSuspensionLowerLimit
                    vehicle.suspensionBias                  = float(values[27])              # float fSuspensionBias
                    vehicle.suspensionAntiDiveMultiplier    = float(values[28])              # float fSuspensionAntidiveMultiplier
                    vehicle.frontLights                     = int(values[30])                # int8 FrontLights
                    vehicle.rearLights                      = int(values[31])                # int8 RearLights
                    # UNUSED:
                    # float fUnused
                    # uint32 Flags
                    # float Transmission.fCurVelocity

                    if convert:
                        self.convertRegular(vehicle)

                    handling.add(vehicle)

        return handling

    def parseVector (self, values : list[str]) -> list[float]:
        return [ float(v) for v in values ]

    def convertBike (self, vehicle : BikeHandlingData) -> BikeHandlingData:
        vehicle.maxLean      = math.sin(degToRad(vehicle.maxLean))
        vehicle.fullAnimLean = degToRad(vehicle.fullAnimLean)
        vehicle.wheelieAng   = math.sin(degToRad(vehicle.wheelieAng))
        vehicle.stoppieAng   = math.sin(degToRad(vehicle.stoppieAng))

        return vehicle

    def convertRegular (self, vehicle : RegularHandlingData) -> RegularHandlingData:
        vehicle.transmission.engineAcceleration *= 1 / (50 * 50)
        vehicle.transmission.maxVelocity *= 1000 / (60 * 60 * 50)
        vehicle.brakeDeceleration *= 1 / (50 * 50)
        vehicle.turnMass = (vehicle.dimension[0] ** 2 + vehicle.dimension[1] ** 2) * vehicle.mass / 12

        if vehicle.turnMass < 10:
            vehicle.turnMass *= 5

        vehicle.invMass = 1 / vehicle.mass
        vehicle.collisionDamageMultiplier *= 2000 / vehicle.mass
        vehicle.buoyancy = 100 / vehicle.percentSubmerged * GRAVITY * vehicle.mass

        a = 0
        b = 100

        velocity = vehicle.transmission.maxVelocity

        while a < b and velocity > 0:
            velocity -= 0.01
            a = vehicle.transmission.engineAcceleration / 6
            c = 0.5 * (velocity ** 2) * vehicle.dimension[0] * vehicle.dimension[2] / vehicle.mass
            b = -velocity * (1 / (c + 1) - 1)

        if vehicle.id == VehicleType.RCBANDIT:
            vehicle.transmission.maxCruiseVelocity  = vehicle.transmission.maxVelocity
            vehicle.transmission.maxReverseVelocity = vehicle.transmission.maxVelocity
        elif VehicleType.BIKE <= vehicle.id <= VehicleType.FREEWAY:
            vehicle.transmission.maxCruiseVelocity  = velocity
            vehicle.transmission.maxVelocity        = velocity * 1.2
            vehicle.transmission.maxReverseVelocity = -0.05
        else:
            vehicle.transmission.maxCruiseVelocity  = velocity
            vehicle.transmission.maxVelocity        = velocity * 1.2
            vehicle.transmission.maxReverseVelocity = -0.2

        if vehicle.transmission.driveType == '4':
            vehicle.transmission.engineAcceleration /= 4
        else:
            vehicle.transmission.engineAcceleration /= 2

        self.initGearRatios(vehicle)

        return vehicle

    def initGearRatios (self, vehicle : RegularHandlingData) -> RegularHandlingData:
        gears       = vehicle.transmission.gears
        gearCount   = vehicle.transmission.numberOfGears
        maxVelocity = vehicle.transmission.maxVelocity

        for gear in gears:
            gear.maxVelocity       = 0
            gear.shiftUpVelocity   = 0
            gear.shiftDownVelocity = 0

        for i in range(1, gearCount + 1):
            pGearRatio0 = gears[i - 1]
            pGearRatio1 = gears[i]

            pGearRatio1.maxVelocity = i / gearCount * maxVelocity

            velocityDiff = pGearRatio1.maxVelocity - pGearRatio0.maxVelocity

            if i >= gearCount:
                pGearRatio1.shiftUpVelocity = maxVelocity
            else:
                gears[i + 1].shiftDownVelocity = velocityDiff * 0.42 + pGearRatio0.maxVelocity
                pGearRatio1.shiftUpVelocity    = velocityDiff * 0.6667 + pGearRatio0.maxVelocity

        # Reverse gear
        gears[0].maxVelocity       = vehicle.transmission.maxReverseVelocity
        gears[0].shiftUpVelocity   = -0.01
        gears[0].shiftDownVelocity = vehicle.transmission.maxReverseVelocity
        gears[1].shiftDownVelocity = -0.01

        return vehicle



def _test_ ():
    print(toJson(HandlingReader.parseDefault(convert=True)))



__all__ = [
    'HandlingReader',
    'VehicleHandlingData',
    'BoatHandlingData',
    'BikeHandlingData',
    'FlyingHandlingData',
    'RegularHandlingData',
    'HandlingTransmission',
    'HandlingGear',
    'Handling',

    '_test_',
]



if __name__ == '__main__':
    _test_()
