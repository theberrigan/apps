from ...common import bfw
from ...common.consts import *

from ..anims.types import AnimationId

from .types import *

from bfw.utils import joinPath



FIGHT_FILE_PATH = joinPath(GAME_DIR, 'data', 'fistfite.dat')

# order important
FIGHT_DEFAULT_ANIMS = [
    AnimationId.STD_NUM,
    AnimationId.STD_PUNCH,
    AnimationId.STD_FIGHT_IDLE,
    AnimationId.STD_FIGHT_SHUFFLE_F,
    AnimationId.STD_FIGHT_KNEE,
    AnimationId.STD_FIGHT_LHOOK,
    AnimationId.STD_FIGHT_JAB,
    AnimationId.STD_FIGHT_PUNCH,
    AnimationId.STD_FIGHT_LONGKICK,
    AnimationId.STD_FIGHT_ROUNDHOUSE,
    AnimationId.STD_FIGHT_KICK,
    AnimationId.STD_FIGHT_HEAD,
    AnimationId.STD_FIGHT_BKICK_L,
    AnimationId.STD_FIGHT_BKICK_L,
    AnimationId.STD_FIGHT_ELBOW_L,
    AnimationId.STD_FIGHT_BKICK_R,
    AnimationId.STD_FIGHT_ELBOW_R,
    AnimationId.STD_KICKGROUND,
    AnimationId.STD_HIT_FRONT,
    AnimationId.STD_HIT_BACK,
    AnimationId.STD_HIT_RIGHT,
    AnimationId.STD_HIT_LEFT,
    AnimationId.STD_HIT_BODYBLOW,
    AnimationId.STD_HIT_CHEST,
    AnimationId.STD_HIT_HEAD,
    AnimationId.STD_HIT_WALK,
    AnimationId.STD_HIT_FLOOR,
    AnimationId.STD_HIT_BEHIND,
    AnimationId.ATTACK_1,
    AnimationId.ATTACK_2,
    AnimationId.ATTACK_3,
    AnimationId.STD_FIGHT_2IDLE,
]

FIGHT_HIT_LEVEL_MAP = {
    'G': FightMoveHitLevel.GROUND,
    'H': FightMoveHitLevel.HIGH,
    'L': FightMoveHitLevel.LOW,
    'M': FightMoveHitLevel.MEDIUM,
    'N': FightMoveHitLevel.NULL,
}



__all__ = [
    'FIGHT_FILE_PATH',
    'FIGHT_DEFAULT_ANIMS',
    'FIGHT_HIT_LEVEL_MAP',
]