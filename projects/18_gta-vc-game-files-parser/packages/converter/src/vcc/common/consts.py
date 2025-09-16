from .bfw_ import bfw

from bfw.utils import *



ROOT_DIR = r'G:\Steam\steamapps\common\Grand Theft Auto Vice City\.dev\converter'
GAME_DIR = joinPath(ROOT_DIR, 'original')
OUTPUT_DIR = joinPath(ROOT_DIR, 'converted')





def _test_ ():
    assert isDir(GAME_DIR)



__all__ = [
    'ROOT_DIR',
    'GAME_DIR',
    'OUTPUT_DIR',
]



if __name__ == '__main__':
    _test_()
