import sys

sys.path.insert(0, r'C:\Projects\PythonLib\python')

from bfw.utils import *



SCRIPT_DIR = getDirPath(getAbsPath(__file__))
DATA_DIR   = joinPath(SCRIPT_DIR, 'data')

GAME_DIR   = r'G:\Steam\steamapps\common\Ion Fury\files'
SOUNDS_DIR = joinPath(GAME_DIR, 'sounds')



__all__ = [
    'SCRIPT_DIR',
    'DATA_DIR',
    'GAME_DIR',
    'SOUNDS_DIR',
]