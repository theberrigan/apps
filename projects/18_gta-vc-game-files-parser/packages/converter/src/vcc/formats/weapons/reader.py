from ...common import bfw
from ...common.types import *
from ...common.consts import *
from ...common.fns import splitSeps, toFloats
from ...common.game_data import AnimAssocGroupId, ModelId

from .consts import *
from .types import *

from bfw.utils import *
from bfw.types.enums import Enum



# eWeaponType
class WeaponType (Enum):
    UNARMED           = 0   # WEAPONTYPE_UNARMED
    BRASSKNUCKLE      = 1   # WEAPONTYPE_BRASSKNUCKLE
    SCREWDRIVER       = 2   # WEAPONTYPE_SCREWDRIVER
    GOLFCLUB          = 3   # WEAPONTYPE_GOLFCLUB
    NIGHTSTICK        = 4   # WEAPONTYPE_NIGHTSTICK
    KNIFE             = 5   # WEAPONTYPE_KNIFE
    BASEBALLBAT       = 6   # WEAPONTYPE_BASEBALLBAT
    HAMMER            = 7   # WEAPONTYPE_HAMMER
    CLEAVER           = 8   # WEAPONTYPE_CLEAVER
    MACHETE           = 9   # WEAPONTYPE_MACHETE
    KATANA            = 10  # WEAPONTYPE_KATANA
    CHAINSAW          = 11  # WEAPONTYPE_CHAINSAW
    GRENADE           = 12  # WEAPONTYPE_GRENADE
    DETONATOR_GRENADE = 13  # WEAPONTYPE_DETONATOR_GRENADE
    TEARGAS           = 14  # WEAPONTYPE_TEARGAS
    MOLOTOV           = 15  # WEAPONTYPE_MOLOTOV
    ROCKET            = 16  # WEAPONTYPE_ROCKET
    COLT45            = 17  # WEAPONTYPE_COLT45
    PYTHON            = 18  # WEAPONTYPE_PYTHON
    SHOTGUN           = 19  # WEAPONTYPE_SHOTGUN
    SPAS12_SHOTGUN    = 20  # WEAPONTYPE_SPAS12_SHOTGUN
    STUBBY_SHOTGUN    = 21  # WEAPONTYPE_STUBBY_SHOTGUN
    TEC9              = 22  # WEAPONTYPE_TEC9
    UZI               = 23  # WEAPONTYPE_UZI
    SILENCED_INGRAM   = 24  # WEAPONTYPE_SILENCED_INGRAM
    MP5               = 25  # WEAPONTYPE_MP5
    M4                = 26  # WEAPONTYPE_M4
    RUGER             = 27  # WEAPONTYPE_RUGER
    SNIPERRIFLE       = 28  # WEAPONTYPE_SNIPERRIFLE
    LASERSCOPE        = 29  # WEAPONTYPE_LASERSCOPE
    ROCKETLAUNCHER    = 30  # WEAPONTYPE_ROCKETLAUNCHER
    FLAMETHROWER      = 31  # WEAPONTYPE_FLAMETHROWER
    M60               = 32  # WEAPONTYPE_M60
    MINIGUN           = 33  # WEAPONTYPE_MINIGUN
    DETONATOR         = 34  # WEAPONTYPE_DETONATOR
    HELICANNON        = 35  # WEAPONTYPE_HELICANNON
    CAMERA            = 36  # WEAPONTYPE_CAMERA
    # -------------------------------------------------
    HEALTH            = 37  # WEAPONTYPE_HEALTH = 37
    ARMOUR            = 38  # WEAPONTYPE_ARMOUR
    RAMMEDBYCAR       = 39  # WEAPONTYPE_RAMMEDBYCAR
    RUNOVERBYCAR      = 40  # WEAPONTYPE_RUNOVERBYCAR
    EXPLOSION         = 41  # WEAPONTYPE_EXPLOSION
    UZI_DRIVEBY       = 42  # WEAPONTYPE_UZI_DRIVEBY
    DROWNING          = 43  # WEAPONTYPE_DROWNING
    FALL              = 44  # WEAPONTYPE_FALL
    UNIDENTIFIED      = 45  # WEAPONTYPE_UNIDENTIFIED
    ANYMELEE          = 46  # WEAPONTYPE_ANYMELEE
    ANYWEAPON         = 47  # WEAPONTYPE_ANYWEAPON


WEAPON_COUNT = 37  # WEAPONTYPE_TOTALWEAPONS

WEAPON_NAME_TO_TYPE = {
    'unarmed':         WeaponType.UNARMED,
    'brassknuckle':    WeaponType.BRASSKNUCKLE,
    'screwdriver':     WeaponType.SCREWDRIVER,
    'golfclub':        WeaponType.GOLFCLUB,
    'nightstick':      WeaponType.NIGHTSTICK,
    'knife':           WeaponType.KNIFE,
    'baseballbat':     WeaponType.BASEBALLBAT,
    'hammer':          WeaponType.HAMMER,
    'cleaver':         WeaponType.CLEAVER,
    'machete':         WeaponType.MACHETE,
    'katana':          WeaponType.KATANA,
    'chainsaw':        WeaponType.CHAINSAW,
    'grenade':         WeaponType.GRENADE,
    'detonategrenade': WeaponType.DETONATOR_GRENADE,
    'teargas':         WeaponType.TEARGAS,
    'molotov':         WeaponType.MOLOTOV,
    'rocket':          WeaponType.ROCKET,
    'colt45':          WeaponType.COLT45,
    'python':          WeaponType.PYTHON,
    'shotgun':         WeaponType.SHOTGUN,
    'spas12shotgun':   WeaponType.SPAS12_SHOTGUN,
    'stubbyshotgun':   WeaponType.STUBBY_SHOTGUN,
    'tec9':            WeaponType.TEC9,
    'uzi':             WeaponType.UZI,
    'silencedingram':  WeaponType.SILENCED_INGRAM,
    'mp5':             WeaponType.MP5,
    'm4':              WeaponType.M4,
    'ruger':           WeaponType.RUGER,
    'sniperrifle':     WeaponType.SNIPERRIFLE,
    'laserscope':      WeaponType.LASERSCOPE,
    'rocketlauncher':  WeaponType.ROCKETLAUNCHER,
    'flamethrower':    WeaponType.FLAMETHROWER,
    'm60':             WeaponType.M60,
    'minigun':         WeaponType.MINIGUN,
    'detonator':       WeaponType.DETONATOR,
    'helicannon':      WeaponType.HELICANNON,
    'camera':          WeaponType.CAMERA,
}


# eWeaponFire
# DO NOT RENAME ITEMS!
class WeaponAmmoType (Enum):
    MELEE       = 0  # WEAPON_FIRE_MELEE
    INSTANT_HIT = 1  # WEAPON_FIRE_INSTANT_HIT
    PROJECTILE  = 2  # WEAPON_FIRE_PROJECTILE
    AREA_EFFECT = 3  # WEAPON_FIRE_AREA_EFFECT
    CAMERA      = 4  # WEAPON_FIRE_CAMERA


class WeaponFlag (Enum):
    USE_GRAVITY       = 1 << 0   # WEAPONFLAG_USE_GRAVITY
    SLOWS_DOWN        = 1 << 1   # WEAPONFLAG_SLOWS_DOWN
    DISSIPATES        = 1 << 2   # WEAPONFLAG_DISSIPATES
    RAND_SPEED        = 1 << 3   # WEAPONFLAG_RAND_SPEED
    EXPANDS           = 1 << 4   # WEAPONFLAG_EXPANDS
    EXPLODES          = 1 << 5   # WEAPONFLAG_EXPLODES
    CANAIM            = 1 << 6   # WEAPONFLAG_CANAIM
    CANAIM_WITHARM    = 1 << 7   # WEAPONFLAG_CANAIM_WITHARM
    FIRST_PERSON      = 1 << 8   # WEAPONFLAG_1ST_PERSON
    HEAVY             = 1 << 9   # WEAPONFLAG_HEAVY
    THROW             = 1 << 10  # WEAPONFLAG_THROW
    RELOAD_LOOP2START = 1 << 11  # WEAPONFLAG_RELOAD_LOOP2START
    USE_2ND           = 1 << 12  # WEAPONFLAG_USE_2ND
    GROUND_2ND        = 1 << 13  # WEAPONFLAG_GROUND_2ND
    FINISH_3RD        = 1 << 14  # WEAPONFLAG_FINISH_3RD
    RELOAD            = 1 << 15  # WEAPONFLAG_RELOAD
    FIGHTMODE         = 1 << 16  # WEAPONFLAG_FIGHTMODE
    CROUCHFIRE        = 1 << 17  # WEAPONFLAG_CROUCHFIRE
    COP3_RD           = 1 << 18  # WEAPONFLAG_COP3_RD
    GROUND_3RD        = 1 << 19  # WEAPONFLAG_GROUND_3RD
    PARTIALATTACK     = 1 << 20  # WEAPONFLAG_PARTIALATTACK
    ANIMDETONATE      = 1 << 21  # WEAPONFLAG_ANIMDETONATE


class WeaponSlot (Enum):
    UNARMED       = 0  # WEAPONSLOT_UNARMED = 0
    MELEE         = 1  # WEAPONSLOT_MELEE
    PROJECTILE    = 2  # WEAPONSLOT_PROJECTILE
    HANDGUN       = 3  # WEAPONSLOT_HANDGUN
    SHOTGUN       = 4  # WEAPONSLOT_SHOTGUN
    SUBMACHINEGUN = 5  # WEAPONSLOT_SUBMACHINEGUN
    RIFLE         = 6  # WEAPONSLOT_RIFLE
    HEAVY         = 7  # WEAPONSLOT_HEAVY
    SNIPER        = 8  # WEAPONSLOT_SNIPER
    OTHER         = 9  # WEAPONSLOT_OTHER


# CWeaponInfo
class WeaponInfo:
    def __init__ (self):
        self.name           : TStr   = None
        self.type           : TInt   = None  # see WeaponType
        self.ammoType       : TInt   = None  # eWeaponFire m_eWeaponFire (see WeaponAmmoType)
        self.range          : TFloat = None  # float m_fRange
        self.fireRate       : TInt   = None  # uint32 m_nFiringRate
        self.reload         : TInt   = None  # uint32 m_nReload
        self.ammoAmount     : TInt   = None  # int32 m_nAmountofAmmunition
        self.damage         : TInt   = None  # uint32 m_nDamage
        self.speed          : TFloat = None  # float m_fSpeed
        self.radius         : TFloat = None  # float m_fRadius
        self.lifespan       : TFloat = None  # float m_fLifespan
        self.spread         : TFloat = None  # float m_fSpread
        self.fireOffset     : TVec3  = None  # CVector m_vecFireOffset
        self.animToPlayName : TStr   = None
        self.animToPlay     : TInt   = None  # AssocGroupId m_AnimToPlay (see AnimAssocGroupId)
        self.animLoopStart  : TFloat = None  # float m_fAnimLoopStart
        self.animLoopEnd    : TFloat = None  # float m_fAnimLoopEnd
        self.animFrameFire  : TFloat = None  # float m_fAnimFrameFire
        self.anim2LoopStart : TFloat = None  # float m_fAnim2LoopStart
        self.anim2LoopEnd   : TFloat = None  # float m_fAnim2LoopEnd
        self.anim2FrameFire : TFloat = None  # float m_fAnim2FrameFire
        self.animBreakout   : TFloat = None  # float m_fAnimBreakout
        self.modelId        : TInt   = None  # int32 m_nModelId (or -1)
        self.modelId2       : TInt   = None  # int32 m_nModel2Id (or -1)
        self.flags          : TInt   = None  # uint32 m_Flags (see WeaponFlag)
        self.weaponSlot     : TInt   = None  # uint32 m_nWeaponSlot (see WeaponSlot)


def isShotgun (weaponType : int) -> bool:
    return weaponType in [ WeaponType.SHOTGUN, WeaponType.SPAS12_SHOTGUN, WeaponType.STUBBY_SHOTGUN ]


class WeaponReader:
    @classmethod
    def fromFile (cls, filePath : str, ctx : Opt[Any] = None) -> List[WeaponInfo]:
        if not isFile(filePath):
            raise OSError(f'File does not exist: { filePath }')

        text = readText(filePath, encoding='utf-8')

        return cls().read(text, ctx)

    def read (self, text : str, ctx : Opt[Any] = None) -> List[WeaponInfo]:
        weapons = Array(WEAPON_COUNT, WeaponInfo)

        for i, weapon in enumerate(weapons):
            weapon.name           = None  # will be set later
            weapon.type           = i
            weapon.ammoType       = WeaponAmmoType.INSTANT_HIT  # WEAPON_FIRE_INSTANT_HIT
            weapon.range          = 0
            weapon.fireRate       = 0
            weapon.reload         = 0
            weapon.ammoAmount     = 0
            weapon.damage         = 0
            weapon.speed          = 0
            weapon.radius         = 0
            weapon.lifespan       = 0
            weapon.spread         = 0
            weapon.fireOffset     = [ 0, 0, 0 ]
            weapon.animToPlayName = None
            weapon.animToPlay     = AnimAssocGroupId.UNARMED  # ASSOCGRP_UNARMED
            weapon.animLoopStart  = 0
            weapon.animLoopEnd    = 0
            weapon.animFrameFire  = 0
            weapon.anim2LoopStart = 0
            weapon.anim2LoopEnd   = 0
            weapon.anim2FrameFire = 0
            weapon.animBreakout   = 0
            weapon.modelId        = -1
            weapon.modelId2       = -1
            weapon.flags          = WeaponFlag.USE_GRAVITY | WeaponFlag.SLOWS_DOWN | WeaponFlag.RAND_SPEED | WeaponFlag.EXPANDS | WeaponFlag.EXPLODES
            weapon.weaponSlot     = WeaponSlot.UNARMED

        if ctx is not None:
            ctx.weapons = weapons

        lines = text.split('\n')

        for line in lines:
            line = line.split('#')[0].strip()

            if not line:
                continue

            if line == 'ENDWEAPONDATA':
                break

            values = splitSeps(line)

            # ----------------------------------------------------------------------------------------------------------

            weaponName = values[0].lower()
            weaponType = WEAPON_NAME_TO_TYPE.get(weaponName)

            assert weaponType is not None

            weapon = weapons[weaponType]

            assert weapon.type == weaponType

            weapon.name           = weaponName
            weapon.ammoType       = WeaponAmmoType.getValue(values[1].upper())
            weapon.range          = float(values[2])
            weapon.fireRate       = int(values[3])
            weapon.reload         = int(values[4])
            weapon.ammoAmount     = int(values[5])
            weapon.damage         = int(values[6])
            weapon.speed          = float(values[7])
            weapon.radius         = float(values[8])
            weapon.lifespan       = float(values[9])
            weapon.spread         = float(values[10])
            weapon.fireOffset     = toFloats(values[11:14])
            weapon.animToPlayName = values[14].lower()
            weapon.animLoopStart  = float(values[15]) / 30
            weapon.animLoopEnd    = float(values[16]) / 30
            weapon.animFrameFire  = float(values[17]) / 30
            weapon.anim2LoopStart = float(values[18]) / 30
            weapon.anim2LoopEnd   = float(values[19]) / 30
            weapon.anim2FrameFire = float(values[20]) / 30
            weapon.animBreakout   = float(values[21]) / 30
            weapon.modelId        = int(values[22])
            weapon.modelId2       = int(values[23])
            weapon.flags          = int(values[24], 16)
            weapon.weaponSlot     = int(values[25])

            if weapon.animLoopEnd and weapon.type != WeaponType.FLAMETHROWER and not isShotgun(weapon.type):
                weapon.fireRate = (weapon.animLoopEnd - weapon.animLoopStart) * 900

            if weapon.type in [ WeaponType.DETONATOR, WeaponType.HELICANNON ]:
                weapon.modelId = -1
            elif weapon.type == WeaponType.DETONATOR_GRENADE:
                weapon.modelId = ModelId.BOMB

            if weapon.modelId != -1 and ctx:
                ctx.modelInfos.getById(weapon.modelId).setWeaponId(weapon.type)

            # TODO: after anim assocs are ready
            # for (int i = 0; i < NUM_ANIM_ASSOC_GROUPS; i++) {
            #   if (!strcmp(weapon.animToPlayName, CAnimManager::GetAnimGroupName((AssocGroupId)i))) {
            #     weapon.animToPlay = i
            #     break;

        return weapons



def _test_ ():
    print(toJson(WeaponReader.fromFile(joinPath(GAME_DIR, 'data/weapon.dat'))))



__all__ = [
    'WeaponReader',
    'WeaponInfo',

    '_test_',
]



if __name__ == '__main__':
    _test_()
