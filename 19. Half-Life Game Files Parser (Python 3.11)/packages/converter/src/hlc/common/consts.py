from .bfw_ import bfw

from bfw.utils import *



GAME_DIR       = r'C:\Projects\_Sources\GameEngines\Goldsrc\Xash3D_3\game\valve'
SOUNDS_DIR     = joinPath(GAME_DIR, 'sound')
MAPS_DIR       = joinPath(GAME_DIR, 'maps')
GRAPHS_DIR     = joinPath(MAPS_DIR, 'graphs')
SPRITES_DIR    = joinPath(GAME_DIR, 'sprites')
MATERIALS_PATH = joinPath(SOUNDS_DIR, 'materials.txt')

HL_TEXT_ENCODING = 'cp1252'
HL_PALETTE_SIZE  = 768



def _test_ ():
    assert isDir(GAME_DIR)
    assert isDir(SOUNDS_DIR)
    assert isDir(MAPS_DIR)
    assert isDir(GRAPHS_DIR)
    assert isDir(SPRITES_DIR)
    assert isFile(MATERIALS_PATH)



__all__ = [
    'GAME_DIR',
    'SOUNDS_DIR',
    'MAPS_DIR',
    'GRAPHS_DIR',
    'SPRITES_DIR',
    'MATERIALS_PATH',
    'HL_TEXT_ENCODING',
    'HL_PALETTE_SIZE',
]



if __name__ == '__main__':
    _test_()
