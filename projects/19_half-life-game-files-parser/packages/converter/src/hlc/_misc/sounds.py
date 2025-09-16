import re
import os
import sys

sys.path.insert(0, r'C:\Projects\PythonLib\python\v001')

from bfw.utils import *

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from hlat.core.consts import *
from hlat.core.fns import *



MATERIALS_PATH = joinPath(SOUNDS_DIR, 'materials.txt')

class Attenuation:
    No     = 0.0   # ATTN_NONE
    Normal = 0.8   # ATTN_NORM
    Idle   = 2.0   # ATTN_IDLE
    Static = 1.25  # ATTN_STATIC

class MatType:
    Concrete = 1
    Metal    = 2
    Glass    = 3
    Dirt     = 4
    Slosh    = 5
    Tile     = 6
    Grate    = 7
    Wood     = 8
    Flesh    = 9
    Vent     = 10
    Computer = 11

MAT_CODE_TO_TYPE = {
    'C': MatType.Concrete,
    'M': MatType.Metal,
    'Y': MatType.Glass,
    'D': MatType.Dirt,
    'S': MatType.Slosh,
    'T': MatType.Tile,
    'G': MatType.Grate,
    'W': MatType.Wood,
    'F': MatType.Flesh,
    'V': MatType.Vent,
    'P': MatType.Computer
}

_GLASS_COMP_SOUNDS = {
    'volume': 0.8,
    'crowbarVolume': 0.2,
    'attenuation': Attenuation.Normal,
    'sounds': [
        'debris/glass1.wav',
        'debris/glass2.wav',
        'debris/glass3.wav'
    ]
}

MAT_STRIKE_SOUNDS = {
    MatType.Concrete: {
        'volume': 0.9,
        'crowbarVolume': 0.6,
        'attenuation': Attenuation.Normal,
        'sounds': [
            'player/pl_step1.wav',
            'player/pl_step2.wav'
        ]
    },
    MatType.Metal: {
        'volume': 0.9,
        'crowbarVolume': 0.3,
        'attenuation': Attenuation.Normal,
        'sounds': [
            'player/pl_metal1.wav',
            'player/pl_metal2.wav'
        ]
    },
    MatType.Dirt: {
        'volume': 0.9,
        'crowbarVolume': 0.1,
        'attenuation': Attenuation.Normal,
        'sounds': [
            'player/pl_dirt1.wav',
            'player/pl_dirt2.wav',
            'player/pl_dirt3.wav'
        ]
    },
    MatType.Vent: {
        'volume': 0.5,
        'crowbarVolume': 0.3,
        'attenuation': Attenuation.Normal,
        'sounds': [
            'player/pl_duct1.wav'
        ]
    },
    MatType.Grate: {
        'volume': 0.9,
        'crowbarVolume': 0.5,
        'attenuation': Attenuation.Normal,
        'sounds': [
            'player/pl_grate1.wav',
            'player/pl_grate4.wav'
        ]
    },
    MatType.Tile: {
        'volume': 0.8,
        'crowbarVolume': 0.2,
        'attenuation': Attenuation.Normal,
        'sounds': [
            'player/pl_tile1.wav',
            'player/pl_tile2.wav',
            'player/pl_tile3.wav',
            'player/pl_tile4.wav'
        ]
    },
    MatType.Slosh: {
        'volume': 0.9,
        'crowbarVolume': 0.0,
        'attenuation': Attenuation.Normal,
        'sounds': [
            'player/pl_slosh1.wav',
            'player/pl_slosh3.wav',
            'player/pl_slosh2.wav',
            'player/pl_slosh4.wav'
        ]
    },
    MatType.Wood: {
        'volume': 0.9,
        'crowbarVolume': 0.2,
        'attenuation': Attenuation.Normal,
        'sounds': [
            'debris/wood1.wav',
            'debris/wood2.wav',
            'debris/wood3.wav'
        ]
    },
    MatType.Glass: _GLASS_COMP_SOUNDS,
    MatType.Computer: _GLASS_COMP_SOUNDS,
    MatType.Flesh: {
        'volume': 1.0,
        'crowbarVolume': 0.2,
        'attenuation': 1.0,
        'sounds': [
            'weapons/bullet_hit1.wav',
            'weapons/bullet_hit2.wav'
        ]
    }
}

ALL_MAT_SOUNDS = list(set([
    normResPath(f'sound/{ sound }')
    for params in MAT_STRIKE_SOUNDS.values()
    for sound in params['sounds']
]))

def parseMatTypes (matPath=MATERIALS_PATH):
    mats  = {}
    lines = readText(matPath, HL_TEXT_ENCODING).split('\n')

    for line in lines:
        line = line.split('//', 1)[0].strip()

        if not line:
            continue

        line = re.split(r'\s+', line)

        assert line

        code = line[0].upper()
        name = line[1].lower()

        assert code in MAT_CODE_TO_TYPE

        matType  = MAT_CODE_TO_TYPE[code]
        prevType = mats.get(name, {}).get('type')

        if prevType is not None and matType != prevType:
            print(f'[parseMatTypes] Material "{ name }" type has been redefined from { prevType } to { matType }')

        mats[name] = {
            'type': matType,
            'sounds': MAT_STRIKE_SOUNDS[matType]
        }

    return mats



def _test_ ():
    print(toJson(parseMatTypes()))

    for soundPath in ALL_MAT_SOUNDS:
        assert isFile(joinPath(GAME_DIR, soundPath)), soundPath



__all__ = [
    'MATERIALS_PATH',
    'Attenuation',
    'MatType',
    'MAT_CODE_TO_TYPE',
    'MAT_STRIKE_SOUNDS',
    'ALL_MAT_SOUNDS',
    'parseMatTypes',
]



if __name__ == '__main__':
    _test_()