from ...common import bfw
from ...common.consts import *

from .types import ParticleType

from bfw.utils import joinPath



PARTICLES_FILE_PATH = joinPath(GAME_DIR, 'data', 'particle.cfg')
PARTICLE_TYPE_COUNT = ParticleType.getSize()

PARTICLE_TYPES_TO_FRAMES = [
    {
        'types': [
            ParticleType.SPARK,
            ParticleType.SPARK_SMALL,
            ParticleType.RAINDROP_SMALL,
            ParticleType.HELI_ATTACK
        ],
        'frames': [
            'rainsmall'
        ]
    },
    {
        'types': [
            ParticleType.WATER_SPARK
        ],
        'frames': [
            'spark'
        ]
    },
    {
        'types': [
            ParticleType.WHEEL_DIRT,
            ParticleType.SAND,
            ParticleType.STEAM2,
            ParticleType.STEAM_NY,
            ParticleType.STEAM_NY_SLOWMOTION,
            ParticleType.GROUND_STEAM,
            ParticleType.ENGINE_STEAM,
            ParticleType.PEDFOOT_DUST,
            ParticleType.CAR_DUST,
            ParticleType.EXHAUST_FUMES
        ],
        'frames': [
            'smokeii_3'
        ]
    },
    {
        'types': [
            ParticleType.WHEEL_WATER,
            ParticleType.WATER,
            ParticleType.SMOKE,
            ParticleType.SMOKE_SLOWMOTION,
            ParticleType.DRY_ICE,
            ParticleType.GARAGEPAINT_SPRAY,
            ParticleType.STEAM,
            ParticleType.WATER_CANNON,
            ParticleType.EXTINGUISH_STEAM,
            ParticleType.HELI_DUST,
            ParticleType.PAINT_SMOKE,
            ParticleType.BULLETHIT_SMOKE
        ],
        'frames': [
            'smoke1',
            'smoke2',
            'smoke3',
            'smoke4',
            'smoke5'
        ]
    },
    {
        'types': [
            ParticleType.BLOOD
        ],
        'frames': [
            'blood'
        ]
    },
    {
        'types': [
            ParticleType.BLOOD_SMALL,
            ParticleType.BLOOD_SPURT
        ],
        'frames': [
            'bloodsplat2'
        ]
    },
    {
        'types': [
            ParticleType.DEBRIS,
            ParticleType.TREE_LEAVES
        ],
        'frames': [
            'gameleaf01_64',
            'letter'
        ]
    },
    {
        'types': [
            ParticleType.DEBRIS2
        ],
        'frames': [
            'gunge'
        ]
    },
    {
        'types': [
            ParticleType.FLYERS
        ],
        'frames': [
            'newspaper02_64'
        ]
    },
    {
        'types': [
            ParticleType.FLAME,
            ParticleType.CARFLAME
        ],
        'frames': [
            'flame1'
        ]
    },
    {
        'types': [
            ParticleType.FIREBALL
        ],
        'frames': [
            'flame1'
        ]
    },
    {
        'types': [
            ParticleType.GUNFLASH,
            ParticleType.GUNFLASH_NOANIM
        ],
        'frames': [
            'gunflash1',
            'gunflash2',
            'gunflash3',
            'gunflash4'
        ]
    },
    {
        'types': [
            ParticleType.GUNSMOKE,
            ParticleType.WATERDROP,
            ParticleType.BLOODDROP,
            ParticleType.HEATHAZE,
            ParticleType.HEATHAZE_IN_DIST
        ],
        'frames': []
    },
    {
        'types': [
            ParticleType.GUNSMOKE2,
            ParticleType.BOAT_THRUSTJET,
            ParticleType.RUBBER_SMOKE
        ],
        'frames': [
            'rubber1',
            'rubber2',
            'rubber3',
            'rubber4',
            'rubber5'
        ]
    },
    {
        'types': [
            ParticleType.CIGARETTE_SMOKE
        ],
        'frames': [
            'gunsmoke3'
        ]
    },
    {
        'types': [
            ParticleType.TEARGAS
        ],
        'frames': [
            'heathaze'
        ]
    },
    {
        'types': [
            ParticleType.SHARD,
            ParticleType.RAINDROP,
            ParticleType.RAINDROP_2D
        ],
        'frames': [
            'raindrop4'
        ]
    },
    {
        'types': [
            ParticleType.SPLASH,
            ParticleType.CAR_SPLASH,
            ParticleType.WATER_HYDRANT,
            ParticleType.PED_SPLASH
        ],
        'frames': [
            'carsplash_01',
            'carsplash_02',
            'carsplash_03',
            'carsplash_04'
        ]
    },
    {
        'types': [
            ParticleType.RAIN_SPLASH,
            ParticleType.RAIN_SPLASH_BIGGROW
        ],
        'frames': [
            'splash1',
            'splash2',
            'splash3',
            'splash4',
            'splash5'
        ]
    },
    {
        'types': [
            ParticleType.RAIN_SPLASHUP
        ],
        'frames': [
            'splash_up1',
            'splash_up2'
        ]
    },
    {
        'types': [
            ParticleType.WATERSPRAY
        ],
        'frames': [
            'waterspray1',
            'waterspray2',
            'waterspray3'
        ]
    },
    {
        'types': [
            ParticleType.EXPLOSION_MEDIUM,
            ParticleType.EXPLOSION_LARGE,
            ParticleType.EXPLOSION_MFAST,
            ParticleType.EXPLOSION_LFAST
        ],
        'frames': [
            'explo01',
            'explo02',
            'explo03',
            'explo04',
            'explo05',
            'explo06'
        ]
    },
    {
        'types': [
            ParticleType.BOAT_SPLASH
        ],
        'frames': [
            'boatwake2'
        ]
    },
    {
        'types': [
            ParticleType.ENGINE_SMOKE,
            ParticleType.ENGINE_SMOKE2,
            ParticleType.CARFLAME_SMOKE,
            ParticleType.FIREBALL_SMOKE,
            ParticleType.ROCKET_SMOKE,
            ParticleType.TEST
        ],
        'frames': [
            'cloudmasked'
        ]
    },
    {
        'types': [
            ParticleType.CARCOLLISION_DUST,
            ParticleType.BURNINGRUBBER_SMOKE
        ],
        'frames': [
            'collisionsmoke'
        ]
    },
    {
        'types': [
            ParticleType.CAR_DEBRIS,
            ParticleType.BIRD_DEBRIS,
            ParticleType.HELI_DEBRIS
        ],
        'frames': [
            'cardebris_01',
            'cardebris_02',
            'cardebris_03',
            'cardebris_04'
        ]
    },
    {
        'types': [
            ParticleType.GUNSHELL_FIRST,
            ParticleType.GUNSHELL,
            ParticleType.GUNSHELL_BUMP1,
            ParticleType.GUNSHELL_BUMP2
        ],
        'frames': [
            'gunshell'
        ]
    },
    {
        'types': [
            ParticleType.BIRD_FRONT
        ],
        'frames': [
            'birdf_01',
            'birdf_02',
            'birdf_03',
            'birdf_04'
        ]
    },
    {
        'types': [
            ParticleType.SHIP_SIDE
        ],
        'frames': [
            'boats_01',
            'boats_02',
            'boats_03',
            'boats_04',
            'boats_05',
            'boats_06',
            'boats_07',
            'boats_08'
        ]
    },
    {
        'types': [
            ParticleType.BEASTIE
        ],
        'frames': [
            'beastie'
        ]
    }
]



__all__ = [
    'PARTICLES_FILE_PATH',
    'PARTICLE_TYPE_COUNT',
    'PARTICLE_TYPES_TO_FRAMES'
]