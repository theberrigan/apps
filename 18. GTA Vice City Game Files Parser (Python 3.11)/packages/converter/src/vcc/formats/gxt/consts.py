import re

from .types import *



GXT_EXT = '.gxt'

GXT_TABLE_ENTRY_SIZE = 8 + 4  # 8 - name, 4 - offset
GXT_TKEY_ENTRY_SIZE  = 4 + 8  # 4 - offset, 8 - name

GXT_COMMAND_NAME_TO_ID = {
    'CAMERA_CHANGE_VIEW_ALL_SITUATIONS': GXTControlCommand.CameraChangeViewAllSituations,
    'GO_BACK':                           GXTControlCommand.GoBack,
    'GO_FORWARD':                        GXTControlCommand.GoForward,
    'GO_LEFT':                           GXTControlCommand.GoLeft,
    'GO_RIGHT':                          GXTControlCommand.GoRight,
    'PED_1RST_PERSON_LOOK_DOWN':         GXTControlCommand.Ped1rstPersonLookDown,
    'PED_1RST_PERSON_LOOK_LEFT':         GXTControlCommand.Ped1rstPersonLookLeft,
    'PED_1RST_PERSON_LOOK_RIGHT':        GXTControlCommand.Ped1rstPersonLookRight,
    'PED_1RST_PERSON_LOOK_UP':           GXTControlCommand.Ped1rstPersonLookUp,
    'PED_ANSWER_PHONE':                  GXTControlCommand.PedAnswerPhone,
    'PED_CENTER_CAMERA_BEHIND_PLAYER':   GXTControlCommand.PedCenterCameraBehindPlayer,
    'PED_CYCLE_TARGET_LEFT':             GXTControlCommand.PedCycleTargetLeft,
    'PED_CYCLE_TARGET_RIGHT':            GXTControlCommand.PedCycleTargetRight,
    'PED_CYCLE_WEAPON_LEFT':             GXTControlCommand.PedCycleWeaponLeft,
    'PED_CYCLE_WEAPON_RIGHT':            GXTControlCommand.PedCycleWeaponRight,
    'PED_DUCK':                          GXTControlCommand.PedDuck,
    'PED_FIREWEAPON':                    GXTControlCommand.PedFireWeapon,
    'PED_JUMPING':                       GXTControlCommand.PedJumping,
    'PED_LOCK_TARGET':                   GXTControlCommand.PedLockTarget,
    'PED_LOOKBEHIND':                    GXTControlCommand.PedLookBehind,
    'PED_SNIPER_ZOOM_IN':                GXTControlCommand.PedSniperZoomIn,
    'PED_SNIPER_ZOOM_OUT':               GXTControlCommand.PedSniperZoomOut,
    'PED_SPRINT':                        GXTControlCommand.PedSprint,
    'TOGGLE_SUBMISSIONS':                GXTControlCommand.ToggleSubmissions,
    'VEHICLE_ACCELERATE':                GXTControlCommand.VehicleAccelerate,
    'VEHICLE_BRAKE':                     GXTControlCommand.VehicleBrake,
    'VEHICLE_CHANGE_RADIO_STATION':      GXTControlCommand.VehicleChangeRadioStation,
    'VEHICLE_ENTER_EXIT':                GXTControlCommand.VehicleEnterExit,
    'VEHICLE_FIREWEAPON':                GXTControlCommand.VehicleFireWeapon,
    'VEHICLE_HANDBRAKE':                 GXTControlCommand.VehicleHandbrake,
    'VEHICLE_HORN':                      GXTControlCommand.VehicleHorn,
    'VEHICLE_LOOKBEHIND':                GXTControlCommand.VehicleLookbehind,
    'VEHICLE_LOOKLEFT':                  GXTControlCommand.VehicleLookLeft,
    'VEHICLE_LOOKRIGHT':                 GXTControlCommand.VehicleLookRight,
    'VEHICLE_STEERDOWN':                 GXTControlCommand.VehicleSteerDown,
    'VEHICLE_STEERLEFT':                 GXTControlCommand.VehicleSteerLeft,
    'VEHICLE_STEERRIGHT':                GXTControlCommand.VehicleSteerRight,
    'VEHICLE_STEERUP':                   GXTControlCommand.VehicleSteerUp,
    'VEHICLE_TURRETDOWN':                GXTControlCommand.VehicleTurretDown,
    'VEHICLE_TURRETLEFT':                GXTControlCommand.VehicleTurretLeft,
    'VEHICLE_TURRETRIGHT':               GXTControlCommand.VehicleTurretRight,
    'VEHICLE_TURRETUP':                  GXTControlCommand.VehicleTurretUp,
}

GXT_TOKENS = {
    '1': GXTAction.Number,          # ~1~ - substitute number
    'a': GXTAction.String,          # ~a~ - substitute string
    'k': GXTAction.Button,          # ~k~~BUTTON~ - substitute localized name of control BUTTON
    'b': GXTAction.ColorBlue,       # ~b~ - blue
    'o': GXTAction.ColorPink,       # ~o~ - pink
    'g': GXTAction.ColorHotPink,    # ~g~ - hot pink
    'h': GXTAction.ColorWhite,      # ~h~ - white
    'p': GXTAction.ColorPurple,     # ~p~ - purple
    'q': GXTAction.ColorPlum,       # ~q~ - plum
    't': GXTAction.ColorGreen,      # ~t~ - green
    'w': GXTAction.ColorGrey,       # ~w~ - grey
    'x': GXTAction.ColorLightBlue,  # ~x~ - light blue
    'y': GXTAction.ColorYellow,     # ~y~ - yellow
    'l': GXTAction.DefaultStyle,    # [UNUSED] ~l~ - reset style and disable text styling
    'B': GXTAction.ToggleBold,      # [UNUSED] ~B~TEXT~B~ - bold/unbold TEXT
    'f': GXTAction.Flashing         # [UNUSED] ~f~ - flashing text
}

GXT_TOKEN_REGEX = '|'.join((GXT_TOKENS | GXT_COMMAND_NAME_TO_ID).keys())
GXT_TOKEN_REGEX = re.compile(rf'(~(?:{ GXT_TOKEN_REGEX })~)')



__all__ = [
    'GXT_EXT',
    'GXT_TABLE_ENTRY_SIZE',
    'GXT_TKEY_ENTRY_SIZE',
    'GXT_COMMAND_NAME_TO_ID',
    'GXT_TOKENS',
    'GXT_TOKEN_REGEX',
]
