from ...common import bfw

from bfw.types.enums import Enum



class GXTControlCommand (Enum):
    CameraChangeViewAllSituations = 1   # Change Camera
    GoBack                        = 2   # Backwards
    GoForward                     = 3   # Forward
    GoLeft                        = 4   # Left
    GoRight                       = 5   # Right
    Ped1rstPersonLookDown         = 6   # Look Down
    Ped1rstPersonLookLeft         = 7   # Look Left
    Ped1rstPersonLookRight        = 8   # Look Right
    Ped1rstPersonLookUp           = 9   # Look Up
    PedAnswerPhone                = 10  # Action
    PedCenterCameraBehindPlayer   = 11  # Center Camera
    PedCycleTargetLeft            = 12  # Next Target
    PedCycleTargetRight           = 13  # Previous Target
    PedCycleWeaponLeft            = 14  # Previous Weapon / Target
    PedCycleWeaponRight           = 15  # Next Weapon / Target
    PedDuck                       = 16  # Crouch
    PedFireWeapon                 = 17  # Fire
    PedJumping                    = 18  # Jump
    PedLockTarget                 = 19  # Target / Aim Weapon
    PedLookBehind                 = 20  # Look Behind
    PedSniperZoomIn               = 21  # Zoom In
    PedSniperZoomOut              = 22  # Zoom Out
    PedSprint                     = 23  # Sprint
    ToggleSubmissions             = 24  # Sub-mission
    VehicleAccelerate             = 25  # Accelerate
    VehicleBrake                  = 26  # Brake / Reverse
    VehicleChangeRadioStation     = 27  # Change Radio Station
    VehicleEnterExit              = 28  # Enter+Exit
    VehicleFireWeapon             = 29  # Fire
    VehicleHandbrake              = 30  # Handbrake
    VehicleHorn                   = 31  # Horn
    VehicleLookbehind             = 32  # Look Behind
    VehicleLookLeft               = 33  # Look Left
    VehicleLookRight              = 34  # Look Right
    VehicleSteerDown              = 35  # Steer Forward / Down
    VehicleSteerLeft              = 36  # Left
    VehicleSteerRight             = 37  # Right
    VehicleSteerUp                = 38  # Steer Back / Up
    VehicleTurretDown             = 39  # Turret Down / Special Ctrl Down
    VehicleTurretLeft             = 40  # Turret Left / Special Ctrl Left
    VehicleTurretRight            = 41  # Turret Right / Special Ctrl Right
    VehicleTurretUp               = 42  # Turret Up / Special Ctrl Up


class GXTAction (Enum):
    Button         = 1
    Flashing       = 2
    Number         = 3
    String         = 4
    ToggleBold     = 5
    DefaultStyle   = 6
    ColorBlue      = 7
    ColorPink      = 8
    ColorHotPink   = 9
    ColorWhite     = 10
    ColorPurple    = 11
    ColorPlum      = 12
    ColorGreen     = 13
    ColorGrey      = 14
    ColorLightBlue = 15
    ColorYellow    = 16



__all__ = [
    'GXTControlCommand',
    'GXTAction',
]
